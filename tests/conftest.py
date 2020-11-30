import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_APP'] = 'app'

import pytest

from app import create_app
from app.models import db
from app.models.role import Role


@pytest.fixture(scope='session')
def app():
  app = create_app()
  return app


@pytest.fixture(scope='session')
def client(app):
  assert app.config['ENV'] == 'testing'
  return app.test_client()


@pytest.fixture(scope='class')
def init_db(app):
  assert app.config['ENV'] == 'testing'
  assert 'test' in app.config['SQLALCHEMY_DATABASE_URI']

  from app.models import db

  with app.app_context():
    db.create_all()

    for role_name in ['admin', 'player']:
      row = Role(**{'name': role_name})
      db.session.add(row)
    db.session.commit()

    yield db

    db.drop_all()


@pytest.fixture(scope='session')
def base_url():
  return 'http://localhost'


@pytest.fixture(scope='session')
def headers():
  return {'Content-Type': 'application/json'}
