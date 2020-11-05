import pytest

from app.auth.blacklist import MemoryStorage, RedisStorage, Blacklist


@pytest.fixture(scope="class")
def blacklist(app):
  blacklist = Blacklist()
  blacklist.init_app(app)
  blacklist.flushall()

  yield blacklist

  blacklist.flushall()


def test_blacklist(blacklist):
  dummy_access_jti = 'abc'
  dummy_refresh_jti = 'xyz'

  assert blacklist.has_as_key(dummy_access_jti) == False
  assert blacklist.has_revoked(dummy_access_jti) == False
  assert blacklist.has_as_key(dummy_refresh_jti) == False
  assert blacklist.has_revoked(dummy_refresh_jti) == False

  blacklist.probate_access_token(dummy_access_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == False
  assert blacklist.has_as_key(dummy_refresh_jti) == False
  assert blacklist.has_revoked(dummy_refresh_jti) == False

  blacklist.probate_refresh_token(dummy_refresh_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == False
  assert blacklist.has_as_key(dummy_refresh_jti) == True
  assert blacklist.has_revoked(dummy_refresh_jti) == False

  blacklist.revoke_access_token(dummy_access_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == True
  assert blacklist.has_as_key(dummy_refresh_jti) == True
  assert blacklist.has_revoked(dummy_refresh_jti) == False

  blacklist.revoke_refresh_token(dummy_refresh_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == True
  assert blacklist.has_as_key(dummy_refresh_jti) == True
  assert blacklist.has_revoked(dummy_refresh_jti) == True

  blacklist.flushall()
  assert blacklist.has_as_key(dummy_access_jti) == False
  assert blacklist.has_revoked(dummy_access_jti) == False
  assert blacklist.has_as_key(dummy_refresh_jti) == False
  assert blacklist.has_revoked(dummy_refresh_jti) == False

  blacklist.revoke_access_token(dummy_access_jti)
  blacklist.revoke_refresh_token(dummy_refresh_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == True
  assert blacklist.has_as_key(dummy_refresh_jti) == True
  assert blacklist.has_revoked(dummy_refresh_jti) == True

  blacklist.probate_access_token(dummy_access_jti)
  blacklist.probate_refresh_token(dummy_refresh_jti)
  assert blacklist.has_as_key(dummy_access_jti) == True
  assert blacklist.has_revoked(dummy_access_jti) == False
  assert blacklist.has_as_key(dummy_refresh_jti) == True
  assert blacklist.has_revoked(dummy_refresh_jti) == False
