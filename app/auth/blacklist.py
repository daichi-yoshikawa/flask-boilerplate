import logging
from collections import namedtuple

import redis


logger = logging.getLogger(__name__)

__BlacklistStorage = namedtuple('BlacklistStorage', ['types'])
BlacklistStorage = __BlacklistStorage(['redis', 'memory'])


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

  def add_candidate(self, jti):
    msg = self.get_error_msg('add_candidate')
    raise NotImplementedError(msg)

  def revoke(self, jti):
    msg = self.get_error_msg('revoke')
    raise NotImplementedError(msg)

  def delete(self, jti):
    msg = self.get_error_msg('delete')
    raise NotImplementedError()

  def get_error_msg(self, method):
    msg = f'{method} must be called from derived class of BlacklistImpl.'
    return msg


class MemoryStorage(Storage):
  def __init__(self):
    self.storage = dict()
    msg = """Blacklist to store revoked token is stored in memory with current config. Once the server is down, whole blacklist is gone. If you'd like to persist blacklist, use redis as storage."""
    logger.error(msg)

  def init_app(self, app):
    pass

  def get(self, jti):
    if jti not in self.storage:
      return None
    else:
      return self.storage[jti]

  def add_candidate(self, jti):
    self.storage[jti] = False

  def revoke(self, jti):
    self.storage[jti] = True

  def delete(self, jti):
    self.storage.pop(jti)


class RedisStorage(Storage):
  def __init__(self):
    self.storage = None

  def init_app(self, app):
    self.storage = redis.StrictRedis(host='localhost', port=6379, db=0)
    self.expire_sec = 100000

  def get(self, jti):
    entry = self.storage.get(jti)
    ret = None if entry is None else entry == 'true'
    return ret

  def add_candidate(self, jti):
    self.storage.set(jti, 'false', self.expire_sec)

  def revoke(self, jti):
    self.storage.set(jti, 'true', self.expire_sec)

  def delete(self, jti):
    self.storage.delete(jti)


class Blacklist:
  def __init__(self):
    self.storage = None

  def init_app(self, app):
    storage_type = 'memory'#app.config['BLACKLIST_STORAGE_TYPE']
    if storage_type not in BlacklistStorage.types:
      msg = f'Not supported storage type: {storage_type}.'
      raise ValueError(msg)

    if storage_type == 'memory':
      self.storage = MemoryStorage()
    elif storage_type == 'redis':
      self.storage = RedisStorage()
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

  def add_candidate(self, jti):
    self.storage.add_candidate(jti)

  def revoke(self, jti):
    self.storage.revoke(jti)
    logger.debug(f'token: {jti} was revoked.')

  def delete(self, jti):
    self.storage.delete(jti)


blacklist = Blacklist()
