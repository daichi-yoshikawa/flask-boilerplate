import os


def join_url(base_url, tail_url):
  url = os.path.join(base_url, str(tail_url))
  return url.rstrip('/') + '/'


def bearer_token(token):
  return {'Authorization': f'Bearer {token}'}
