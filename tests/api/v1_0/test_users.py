import json
import pytest
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User
from helpers.utils import join_url


users = [
  {
    'request': dict(name='test001', email='test001@test.com', password='testtest'),
    'expected': dict(link={'self': 'http://localhost/api/v1_0/users/1/'}),
    'status_code': HTTPStatus.CREATED,
  },
  {
    'request': dict(name='test002', email='test002@test.com', password='testtest'),
    'expected': dict(link={'self': 'http://localhost/api/v1_0/users/2/'}),
    'status_code': HTTPStatus.CREATED,
  },
  {
    'request': dict(name='test003', email='test003@test.com', password='testtest'),
    'expected': dict(link={'self': 'http://localhost/api/v1_0/users/3/'}),
    'status_code': HTTPStatus.CREATED,
  },
]

users_to_signup = list(users)
users_to_signup += [
  {
    'request': dict(name='test001', email='test004@test.com', password='testtest'),
    'expected': dict(error={'message': 'Username:test001 is already used.'}),
    'status_code': HTTPStatus.CONFLICT,
  },
  {
    'request': dict(name='test004', email='test001@test.com', password='testtest'),
    'expected': dict(error={'message': 'Email:test001@test.com is already used.'}),
    'status_code': HTTPStatus.CONFLICT,
  },
  {
    'request': dict(name='', email='test001@test.com', password='testtest'),
    'expected': dict(error={'message': {'name': ['Name length must be 4 - 64.']}}),
    'status_code': HTTPStatus.BAD_REQUEST,
  },
  {
    'request': dict(name='test001', email='test.com', password='testtest'),
    'expected': dict(error={'message': {'email': ['Not a valid email address.']}}),
    'status_code': HTTPStatus.BAD_REQUEST,
  },
  {
    'request': dict(name='test008', email='test008@test.com', password='t'),
    'expected': dict(error={'message': {'password': ['Password must be at least 8 characters.']}}),
    'status_code': HTTPStatus.BAD_REQUEST,
  }
]

users_to_get = [
  {
    'request': 1,
    'expected': dict(id=1, name='test001', email='test001@test.com', link={'self': 'http://localhost/api/v1_0/users/1/'}),
    'status_code': HTTPStatus.OK,
  },
  {
    'request': 3,
    'expected': dict(id=3, name='test003', email='test003@test.com', link={'self': 'http://localhost/api/v1_0/users/3/'}),
    'status_code': HTTPStatus.OK,
  },
  {
    'request': 100,
    'expected': dict(error={'message': 'User ID:100 was not found.'}),
    'status_code': HTTPStatus.NOT_FOUND,
  },
]

url_users = '/api/v1_0/users/'

@pytest.mark.usefixtures("init_db")
class TestUsersAPI:
  @pytest.mark.parametrize('user', users_to_signup)
  def test_post(self, client, headers, user):
    n_users_start = db.session.query(User).count()
    data = user['request']
    ret = client.post(url_users, data=json.dumps(data), headers=headers)
    n_users_end = db.session.query(User).count()

    assert ret.json == user['expected']
    assert ret.status_code == user['status_code']

    if ret.status_code == HTTPStatus.CREATED:
      assert n_users_end - n_users_start == 1
    else:
      assert n_users_end == n_users_start


@pytest.fixture(scope='class')
def prepare_users(init_db):
  for user in users:
    row = user['request'].copy()
    row['password'] = generate_password_hash(row['password'])
    row = User(**row)
    db.session.add(row)
  db.session.commit()


@pytest.mark.usefixtures("prepare_users")
class TestUserAPI:
  @pytest.mark.parametrize('user', users_to_get)
  def test_get_without_token(self, client, user):
    n_users_start = db.session.query(User).count()
    url = join_url(url_users, user['request'])
    ret = client.get(url)
    n_users_end = db.session.query(User).count()

    assert ret.json == dict(error={'message': 'Missing authorization header.'})
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert n_users_start == n_users_end

  @pytest.mark.parametrize('user', users_to_get)
  def test_get_with_token(self, client, user, headers):
    n_users_start = db.session.query(User).count()
    iam = {
      'email': 'test001@test.com',
      'password': 'testtest',
    }
    ret = client.post(
      '/api/v1_0/token/', data=json.dumps(iam), headers=headers)
    assert 'access_token' in ret.json
    assert 'refresh_token' in ret.json
    assert len(ret.json['access_token']) > 0
    assert len(ret.json['refresh_token']) > 0
    assert ret.json['access_token'] != ret.json['refresh_token']

    url = join_url(url_users, user['request'])
    ret = client.get(url, headers={'Authorization': f"Bearer {ret.json['access_token']}"})
    n_users_end = db.session.query(User).count()

    assert ret.json == user['expected']
    assert ret.status_code == user['status_code']
    assert n_users_start == n_users_end
