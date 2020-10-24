import os

from flask import request


def get_url(tail_url, base_url=None):
  base_url = request.base_url if base_url is None else base_url

  if isinstance(tail_url, list):
    tail_url = [str(v) for v in tail_url]

    """
    Remove duplicate delimiters.
    1. tail_url like ['users/', '/1/'] must be joined by delimiter '/'.
       -> 'users///1/'
    2. split by '/' again. -> ['users', '', '', '1']
    3. drop empty string. -> ['users', '1']
    """
    tail_url = [s for s in '/'.join(tail_url).split('/') if s != '']

    tail_url = '/'.join(tail_url)

  return os.path.join(base_url, str(tail_url)).rstrip('/') + '/'
