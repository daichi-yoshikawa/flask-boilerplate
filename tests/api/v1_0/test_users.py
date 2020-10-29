import json
import os
import pytest
from http import HTTPStatus

from helpers.data import users_to_signup, users_to_get
from helpers.utils import join_url


urls = dict(users='/api/v1_0/users/')

@pytest.mark.usefixtures("db")
class TestUsersAPI:
  @pytest.mark.parametrize('user', users_to_signup)
  def test_post(self, client, headers, user):
    data = user['request']
    ret = client.post(urls['users'], data=json.dumps(data), headers=headers)

    assert ret.json == user['expected']
    assert ret.status_code == user['status_code']


@pytest.mark.usefixtures("db")
class TestUserAPI:
  @pytest.mark.parametrize('user', users_to_get)
  def test_get(self, client, user):
    url = join_url(urls['users'], user['request'])
    ret = client.get(url)

    assert ret.json == user['expected']
    assert ret.status_code == user['status_code']
