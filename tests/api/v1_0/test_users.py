import json
import pytest
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User
from helpers.api.v1_0.users import users, users_to_signup, users_to_get
from helpers.utils import join_url


urls = dict(users='/api/v1_0/users/')
tokens = dict()


@pytest.mark.usefixtures("init_db")
class TestUsersAPI:
  @pytest.mark.parametrize('user', users_to_signup)
  def test_post(self, client, headers, user):
    n_users_start = db.session.query(User).count()
    data = user['request']
    ret = client.post(urls['users'], data=json.dumps(data), headers=headers)
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
    url = join_url(urls['users'], user['request'])
    ret = client.get(url)
    n_users_end = db.session.query(User).count()

    assert ret.json == dict(error={'message': 'Missing authorization header.'})
    assert ret.status_code == HTTPStatus.UNAUTHORIZED
    assert n_users_start == n_users_end

  @pytest.mark.parametrize('user', users_to_get)
  def test_get_with_token(self, client, user, headers):
    n_users_start = db.session.query(User).count()
    iam = {
      'name': 'test001',
      'email': 'test001@test',
      'password': 'testtest',
    }
    ret = client.post(
      '/api/v1_0/token/', data=json.dumps(iam), headers=headers)
    assert 'access_token' in ret.json
    assert 'refresh_token' in ret.json
    assert len(ret.json['access_token']) > 0
    assert len(ret.json['refresh_token']) > 0
    assert ret.json['access_token'] != ret.json['refresh_token']

    url = join_url(urls['users'], user['request'])
    ret = client.get(url, headers={'Authorization': f"Bearer {ret.json['access_token']}"})
    n_users_end = db.session.query(User).count()

    assert ret.json == user['expected']
    assert ret.status_code == user['status_code']
    assert n_users_start == n_users_end
