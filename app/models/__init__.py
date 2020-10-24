"""
Modules defining db tables must be imported after instance of SQLAlchemy is created,
since they refer to the instance and circular import must be avoided.

1. app.models(__init__.py) creates an instance of SQLAlchemy.
2. app.models.*** uses the instance in it, ande define a model.
3. app.models.(__init__.py) imports the class defined in app.models.***.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

from .user import User
