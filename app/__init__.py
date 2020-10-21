import dotenv
import os

from flask import Flask

from app.auth import jwt
from app.models import db, migrate
from app.utils.redis import redis
from config import config

def configure_app(app, mode):
  app.config.update(config[mode]['app'])


def init_db(app):
  db.init_app(app)
  migrate.init_app(app, db)
  redis.init(host='localhost', port=6729, db=0)


def register_blueprints(app):
  from app.views import index_blueprint
  app.register_blueprint(index_blueprint, url_prefix='/')
  from app.api import api_blueprint
  app.register_blueprint(api_blueprint, url_prefix='/api/')


def create_app():
  try:
    mode = os.environ['FLASK_ENV']
  except KeyError:
    raise KeyError('FLASK_ENV must be set.')
  if not os.path.exists(f'dot.env.{mode}'):
    raise RuntimeError(f'dot.env.{mode} was not found.')
  dotenv.load_dotenv(f'dot.env.{mode}')

  app = Flask(
    __name__, template_folder=os.environ['FLASK_TEMPLATE_DIR'],
    static_folder=os.environ['FLASK_STATIC_DIR'])

  configure_app(app, mode)
  init_db(app)
  jwt.init_app(app)
  register_blueprints(app)

  return app
