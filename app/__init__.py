import logging
import logging.config
import os

from flask import Flask

from app.auth.blacklist import blacklist
from app.auth.jwt import jwt
from app.models import db, migrate
from config import config, get_mode_from_env, load_dotenv


logging.config.dictConfig(config['logger']['default'])
logger = logging.getLogger(__name__)

def init_db(app):
  db.init_app(app)
  migrate.init_app(app, db)


def register_blueprints(app):
  from app.views import index_blueprint
  app.register_blueprint(index_blueprint, url_prefix='/')
  from app.api import api_blueprint
  app.register_blueprint(api_blueprint, url_prefix='/api/')


def create_app():
  mode = get_mode_from_env(logger)
  load_dotenv(mode, logger)

  app = Flask(
      __name__, template_folder=os.environ['FLASK_TEMPLATE_DIR'],
      static_folder=os.environ['FLASK_STATIC_DIR'])

  app.config.update(config['app'][mode])
  blacklist.init_app(app)
  jwt.init_app(app)
  init_db(app)
  register_blueprints(app)

  return app

