import dotenv
import logging.config
import os

from flask import Flask
from flask_jwt_extended import JWTManager

from app.models import db, ma, migrate
from app.utils.exceptions import DotEnvNotFound, InvalidModeError, ModeNotSet
from app.utils.redis import redis
from config import config, MODES


logging.config.dictConfig(config['logger']['default'])
logger = logging.getLogger(__name__)

jwt = JWTManager()

def init_db(app):
  db.init_app(app)
  ma.init_app(app)
  migrate.init_app(app, db)
  redis.init(host='localhost', port=6729, db=0)


def register_blueprints(app):
  from app.views import index_blueprint
  app.register_blueprint(index_blueprint, url_prefix='/')
  from app.api import api_blueprint
  app.register_blueprint(api_blueprint, url_prefix='/api/')


def create_app():
  if 'FLASK_ENV' not in os.environ:
    msg = 'FLASK_ENV must be set.'
    logger.fatal(msg)
    raise ModeNotSet(msg)
  mode = os.environ['FLASK_ENV']
  if mode not in MODES:
    msg = f'Invalid FLASK_ENV is set. FLASK_ENV must be in {MODES}.'
    logger.fatal(msg)
    raise InvalidModeError(msg)

  if not os.path.exists(f'./.env.d/.env.{mode}'):
    msg = f'./.env.d/.env.{mode} was not found.'
    logger.fatal(msg)
    raise DotEnvNotFound(msg)

  dotenv.load_dotenv(f'./.env.d/.env.{mode}')
  app = Flask(
      __name__, template_folder=os.environ['FLASK_TEMPLATE_DIR'],
      static_folder=os.environ['FLASK_STATIC_DIR'])

  app.config.update(config['app'][mode])
  jwt.init_app(app)
  init_db(app)
  register_blueprints(app)

  return app

