import json
import pytest
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User
from helpers.utils import bearer_token


url_token = '/api/v1_0/token/'

me = dict(name='test001', email='test001@test', password='testtest')
you = dict(name='test002', email='test002@test', password='testtest')

@pytest.fixture(scope='class')
def prepare_users(init_db):
  row = me.copy()
  row['password'] = generate_password_hash(row['password'])
  row = User(**row)
  db.session.add(row)
  row = you.copy()
  row['password'] = generate_password_hash(row['password'])
  row = User(**row)
  db.session.add(row)
  db.session.commit()


@pytest.fixture(scope='function')
def tokens(prepare_users, client, headers):
  data = me.copy()
  ret = client.post(url_token, data=json.dumps(data), headers=headers)

  assert ret.status_code == HTTPStatus.OK
  assert 'access_token' in ret.json
  assert 'refresh_token' in ret.json
  assert len(ret.json['access_token']) > 0
  assert len(ret.json['refresh_token']) > 0
  assert ret.json['access_token'] != ret.json['refresh_token']
  assert 'access_expires_in' in ret.json
  assert 'refresh_expires_in' in ret.json
  assert ret.json['access_expires_in'] > 0
  assert ret.json['refresh_expires_in'] > 0
  assert ret.json['refresh_expires_in'] > ret.json['access_expires_in']

  yield (ret.json['access_token'], ret.json['refresh_token'])


@pytest.mark.usefixtures("prepare_users")
class TestTokenAPI:
  @pytest.mark.parametrize(
    'param',
    [
      { # Normal
        'request': dict(name='test001', email='test001@test', password='testtest'),
        'expected': ['access_token', 'refresh_token'],
        'status_code': HTTPStatus.OK,
      },
      { # Wrong name
        'request': dict(name='test111', email='test001@test', password='testtest'),
        'expected': {'error': {'message': 'User:(test111, test001@test) not found.'}},
        'status_code': HTTPStatus.NOT_FOUND,
      },
      { # Wrong email
        'request': dict(name='test001', email='test111@test', password='testtest'),
        'expected': {'error': {'message': 'User:(test001, test111@test) not found.'}},
        'status_code': HTTPStatus.NOT_FOUND,
      },
      { # Wrong password
        'request': dict(name='test001', email='test001@test', password='test'),
        'expected': {'error': {'message': 'Wrong password.'}},
        'status_code': HTTPStatus.UNAUTHORIZED,
      },
      { # Wrong all info
        'request': dict(name='test111', email='test111@test', password='test'),
        'expected': {'error': {'message': 'User:(test111, test111@test) not found.'}},
        'status_code': HTTPStatus.NOT_FOUND,
      },
    ]
  )
  def test_post(self, client, headers, param):
    data = param['request']
    ret = client.post(url_token, data=json.dumps(data), headers=headers)

    assert ret.status_code == param['status_code']
    if ret.status_code == HTTPStatus.OK:
      assert 'access_token' in ret.json
      assert 'refresh_token' in ret.json
      assert len(ret.json['access_token']) > 0
      assert len(ret.json['refresh_token']) > 0
      assert ret.json['access_token'] != ret.json['refresh_token']
      assert 'access_expires_in' in ret.json
      assert 'refresh_expires_in' in ret.json
      assert ret.json['access_expires_in'] > 0
      assert ret.json['refresh_expires_in'] > 0
      assert ret.json['refresh_expires_in'] > ret.json['access_expires_in']
    else:
      assert ret.json == param['expected']

  def test_get(self, tokens, client, headers):
    access_token, refresh_token = tokens

    # Without token, fails.
    ret = client.get(url_token)
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Missing authorization header.'})

    # With access token, succeeds.
    ret = client.get(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.OK
    assert ret.json == dict({})

    # With refresh token, fails.
    ret = client.get(url_token, headers=bearer_token(refresh_token))
    assert ret.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert ret.json == dict(error={'message': 'Only access tokens are allowed.'})

  def test_put(self, tokens, client, headers):
    access_token, refresh_token = tokens

    # Check if GET with access token succeeds.
    ret = client.get(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.OK
    assert ret.json == dict({})

    # Without token, fails.
    ret = client.put(url_token)
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Missing authorization header.'})

    # With access token, fails.
    ret = client.put(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert ret.json == dict(error={'message': 'Only refresh tokens are allowed.'})

    # With refresh token, without access token in body, fails
    ret = client.put(url_token, headers=bearer_token(refresh_token))
    assert ret.status_code == HTTPStatus.BAD_REQUEST
    assert ret.json == dict(error={'message': 'Access token is not in body.'})

    # With refresh token in header and empty access token in body, fails.
    ret = client.put(
        url_token, data=json.dumps({'access_token': ''}),
        headers={**headers, **bearer_token(refresh_token)})
    assert ret.status_code == HTTPStatus.BAD_REQUEST
    assert ret.json == dict(error={'message': 'Given access token is empty.'})

    # With refresh token in header and valid access token in body, succeeds.
    ret = client.put(
        url_token, data=json.dumps({'access_token': access_token}),
        headers={**headers, **bearer_token(refresh_token)})
    assert ret.status_code == HTTPStatus.OK
    assert 'access_token' in ret.json
    assert len(ret.json['access_token']) > 0
    assert 'access_expires_in' in ret.json
    assert ret.json['access_expires_in'] > 0
    new_access_token = ret.json['access_token']

    # With old access token, GET fails.
    ret = client.get(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Token has been revoked.'})

    # With new access token, GET succeeds.
    ret = client.get(url_token, headers=bearer_token(new_access_token))
    assert ret.status_code == HTTPStatus.OK
    assert ret.json == dict({})

    # Refresh token can be succesfully done multiple times.
    ret = client.put(
        url_token, data=json.dumps({'access_token': new_access_token}),
        headers={**headers, **bearer_token(refresh_token)})
    assert ret.status_code == HTTPStatus.OK
    assert 'access_token' in ret.json
    assert len(ret.json['access_token']) > 0
    assert 'access_expires_in' in ret.json
    assert ret.json['access_expires_in'] > 0

  def test_delete(self, tokens, client, headers):
    access_token, refresh_token = tokens

    # Without token, fails.
    ret = client.delete(url_token)
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Missing authorization header.'})

    # With refresh token, fails.
    ret = client.delete(url_token, headers=bearer_token(refresh_token))
    assert ret.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert ret.json == dict(error={'message': 'Only access tokens are allowed.'})

    # With access token in header but empty body, fails.
    ret = client.delete(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.BAD_REQUEST
    assert ret.json == dict(error={'message': 'Refresh token is not in body.'})

    # With access token in header but empty refresh token in body, fails.
    ret = client.delete(
        url_token, data=json.dumps({'refresh_token': ''}),
        headers={**headers, **bearer_token(access_token)})
    assert ret.status_code == HTTPStatus.BAD_REQUEST
    assert ret.json == dict(error={'message': 'Given refresh token is empty.'})

    # With access token in header and valid refresh token in body, succeeds.
    ret = client.delete(
        url_token, data=json.dumps({'refresh_token': refresh_token}),
        headers={**headers, **bearer_token(access_token)})
    assert ret.status_code == HTTPStatus.OK
    assert ret.json == dict({})

    # GET fails because access token is not valid anymore.
    ret = client.get(url_token, headers=bearer_token(access_token))
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Token has been revoked.'})

    # PUT (refresh token) fails because refresh token is not valid anymore.
    ret = client.put(
        url_token, data=json.dumps({'access_token': access_token}),
        headers={**headers, **bearer_token(refresh_token)})
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert ret.json == dict(error={'message': 'Token has been revoked.'})
