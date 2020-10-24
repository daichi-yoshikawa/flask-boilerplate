import os
import sys
sys.path.append('../')

import pytest

from app.models import db


@pytest.fixture()
def init_env():
  os.environ['FLASK_ENV'] = 'testing'
  os.environ['FLASK_APP'] = 'app'


@pytest.fixture()
def init_db():
  pass
