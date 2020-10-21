import redis as redis_


class Redis:
  def __init__(self):
    self._redis = None

  def init(self, host, port, db, **kwargs):
    self._redis = redis_.StrictRedis(host=host, port=port, db=db, **kwargs)

  @property
  def redis(self):
    if self._redis is None:
      raise RuntimeError('Redis is not initialized.')
    return self._redis


redis = Redis()
