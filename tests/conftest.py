import os

import pytest

from app import create_app


@pytest.fixture(scope="session")
def init_env():
  os.environ['FLASK_ENV'] = 'testing'
  os.environ['FLASK_APP'] = 'app'


@pytest.fixture(scope="session")
def app(init_env):
  app = create_app()
  return app


@pytest.fixture(scope="session")
def client(app):
  assert app.config['ENV'] == 'testing'
  return app.test_client()


@pytest.fixture(scope="session")
def db(app):
  assert app.config['ENV'] == 'testing'
  assert 'test' in app.config['SQLALCHEMY_DATABASE_URI']

  from app.models import db

  with app.app_context():
    db.create_all()
    yield db
    db.drop_all()


@pytest.fixture(scope="session")
def base_url():
  return 'http://localhost'


@pytest.fixture()
def headers():
  return {'Content-Type': 'application/json'}
