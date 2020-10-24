import os


def test_post_users(init_env, init_db):
  print(os.environ['FLASK_ENV'])
  print(os.environ['FLASK_APP'])
