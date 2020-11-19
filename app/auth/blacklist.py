import logging
import redis
from collections import namedtuple
from sqlalchemy import func

from app.models import db
from app.models.revoked_token import RevokedToken


logger = logging.getLogger(__name__)

__BlacklistStorage = namedtuple('BlacklistStorage', ['types'])
BlacklistStorage = __BlacklistStorage(['memory', 'redis', 'database'])


class Storage:
  def init_app(self, app):
    msg = self.get_error_msg('init_app')
    raise NotImplementedError(msg)

  def get(self, jti):
    """
    Return None if not exists in list.
    Return True if exists revoked, and False if exists but not revoked.
    """
    msg = self.get_error_msg('get')
    raise NotImplementedError(msg)

  def probate_access_token(self, jti):
    msg = self.get_error_msg('probate_access_token')
    raise NotImplementedError(msg)

  def probate_refresh_token(self, jti):
    msg = self.get_error_msg('probate_refresh_token')
    raise NotImplementedError(msg)

  def revoke_access_token(self, jti):
    msg = self.get_error_msg('revoke_access_token')
    raise NotImplementedError(msg)

  def revoke_refresh_token(self, jti):
    msg = self.get_error_msg('revoke_refresh_token')
    raise NotImplementedError(msg)

  def delete(self, jti):
    msg = self.get_error_msg('delete')
    raise NotImplementedError(msg)

  def flushall(self):
    msg = self.get_error_msg('flushall')
    raise NotImplementedError(msg)

  def get_error_msg(self, method):
    msg = f'{method} must be called from derived class of BlacklistImpl.'
    return msg


class MemoryStorage(Storage):
  def __init__(self):
    self.storage = dict()
    msg = """Blacklist to store revoked token is stored in memory with current config. Once the server is down, whole blacklist is gone. If you'd like to persist blacklist, use redis as storage."""
    logger.warning(msg)

  def init_app(self, app):
    pass

  def get(self, jti):
    if jti not in self.storage:
      return None
    else:
      return self.storage[jti]

  def probate_access_token(self, jti):
    self.storage[jti] = False

  def probate_refresh_token(self, jti):
    self.storage[jti] = False

  def revoke_access_token(self, jti):
    self.storage[jti] = True

  def revoke_refresh_token(self, jti):
    self.storage[jti] = True

  def delete(self, jti):
    self.storage.pop(jti)

  def flushall(self):
    self.storage = dict()


class RedisStorage(Storage):
  def __init__(self):
    self.storage = None

  def init_app(self, app):
    host = app.config['REDIS_HOST']
    password = app.config['REDIS_PASSWORD']
    port = app.config['REDIS_PORT']
    db = app.config['REDIS_DB_INDEX']

    self.storage = redis.StrictRedis(host=host, port=port, db=db, password=password)
    self.access_token_expires = int(app.config['JWT_ACCESS_TOKEN_EXPIRES']*1.2)
    self.refresh_token_expires = int(app.config['JWT_REFRESH_TOKEN_EXPIRES']*1.2)

  def get(self, jti):
    entry = self.storage.get(jti)
    ret = None if entry is None else entry == b'true'
    return ret

  def probate_access_token(self, jti):
    self.storage.set(jti, 'false', self.access_token_expires)

  def probate_refresh_token(self, jti):
    self.storage.set(jti, 'false', self.refresh_token_expires)

  def revoke_access_token(self, jti):
    self.storage.set(jti, 'true', self.access_token_expires)

  def revoke_refresh_token(self, jti):
    self.storage.set(jti, 'true', self.refresh_token_expires)

  def delete(self, jti):
    self.storage.delete(jti)

  def flushall(self):
    self.storage.flushdb()


class DatabaseStorage(Storage):
  def __init__(self):
    self.storage = None

  def init_app(self, app):
    self.token_expires = {
      'access_token': int(app.config['JWT_ACCESS_TOKEN_EXPIRES']),
      'refresh_token': int(app.config['JWT_REFRESH_TOKEN_EXPIRES']),
    }

  def get(self, jti):
    query = RevokedToken.query.filter_by(jti=jti)
    token = query.first()
    ret = None if token is None else token.revoked
    return ret

  def probate_access_token(self, jti):
    self.probate_token_impl(jti, token_type_hint='access_token')

  def probate_refresh_token(self, jti):
    self.probate_token_impl(jti, token_type_hint='refresh_token')

  def probate_token_impl(self, jti, token_type_hint):
    query = RevokedToken.query.filter_by(
        jti=jti, token_type_hint=token_type_hint)
    token = query.first()

    if token is None:
      revoked_token = RevokedToken(**{
        'jti': jti,
        'revoked': False,
        'token_type_hint': token_type_hint,
        'expires_in': self.token_expires[token_type_hint],
        'revoked_at': None,
      })
      db.session.add(revoked_token)
    else:
      token.revoked = False
    db.session.commit()

  def revoke_access_token(self, jti):
    self.revoke_token_impl(jti, token_type_hint='access_token')

  def revoke_refresh_token(self, jti):
    self.revoke_token_impl(jti, token_type_hint='refresh_token')

  def revoke_token_impl(self, jti, token_type_hint):
    query = RevokedToken.query.filter_by(
        jti=jti, token_type_hint=token_type_hint)
    token = query.first()

    if token is None:
      revoked_token = RevokedToken(**{
        'jti': jti,
        'revoked': True,
        'token_type_hint': token_type_hint,
        'expires_in': self.token_expires[token_type_hint],
        'revoked_at': func.now(),
      })
      db.session.add(revoked_token)
    else:
      token.revoked = True
      token.revoked_at = func.now()
    db.session.commit()

  def delete(self, jti):
    RevokedToken.query.filter_by(jti=jti).delete()
    db.session.commit()

  def flushall(self):
    db.session.query(RevokedToken).delete()
    db.session.commit()


class Blacklist:
  def __init__(self):
    self.storage = None

  def init_app(self, app):
    storage_type = app.config['BLACKLIST_STORAGE_TYPE']
    if storage_type not in BlacklistStorage.types:
      msg = f'Not supported storage type: {storage_type}.'
      raise ValueError(msg)

    if storage_type == 'memory':
      self.storage = MemoryStorage()
    elif storage_type == 'redis':
      self.storage = RedisStorage()
    elif storage_type == 'database':
      self.storage = DatabaseStorage()
    else:
      msg = f'Not supported storage type: {storage_type}.'
      raise ValueError(msg)

    self.storage.init_app(app)

  def has_as_key(self, jti):
    has = self.storage.get(jti)
    has = False if has is None else True
    return has

  def has_revoked(self, jti):
    revoked = self.storage.get(jti)
    revoked = False if revoked is None else revoked
    return revoked

  def probate_access_token(self, jti):
    self.storage.probate_access_token(jti)

  def probate_refresh_token(self, jti):
    self.storage.probate_refresh_token(jti)

  def revoke_access_token(self, jti):
    self.storage.revoke_access_token(jti)
    logger.debug(f'token: {jti} was revoked.')

  def revoke_refresh_token(self, jti):
    self.storage.revoke_refresh_token(jti)
    logger.debug(f'token: {jti} was revoked.')

  def delete(self, jti):
    self.storage.delete(jti)

  def flushall(self):
    self.storage.flushall()


blacklist = Blacklist()
