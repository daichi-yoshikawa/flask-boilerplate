"""
Note: Unlike app.views, there's no need to avoid circular import.
"""

from flask import Blueprint
from flask_restful import Api

from .v1_0.users import UserListAPI


api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(UserListAPI, '/v1.0/users/', endpoint='users')
