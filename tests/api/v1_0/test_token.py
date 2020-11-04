import json
import pytest
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User


API_URL = '/api/v1_0/token/'


users = [
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


@pytest.fixture(scope='class')
def prepare_users(init_db):
  row = users[0]['request'].copy()
  row['password'] = generate_password_hash(row['password'])
  row = User(**row)
  db.session.add(row)
  db.session.commit()


@pytest.mark.usefixtures("prepare_users")
class TestTokenAPI:
  @pytest.mark.parametrize('user', users)
  def test_post(self, client, headers, user):
    data = user['request']
    ret = client.post(API_URL, data=json.dumps(data), headers=headers)

    assert ret.status_code == user['status_code']
    if ret.status_code == HTTPStatus.OK:
      assert 'access_token' in ret.json
      assert 'refresh_token' in ret.json
      assert len(ret.json['access_token']) > 0
      assert len(ret.json['refresh_token']) > 0
      assert ret.json['access_token'] != ret.json['refresh_token']
