"""
index.py must be imported after instance of Blueprint is created,
since index.py refers to the instance and circular import must be avoided.

1. app.views(__init__.py) creates an instance of Blueprint.
2. app.views.index uses the instance in it, and define function.
3. app.views(__init__.py) imports the function defined in app.views.index.
4. app imports the instance of blueprint to register to Flask app.
"""

from flask import Blueprint

index_blueprint = Blueprint('index', __name__)

from . import index
