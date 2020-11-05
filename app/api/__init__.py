"""
Note: Unlike app.views, there's no need to avoid circular import.
"""

from flask import Blueprint
from flask_restful import Api

from .v1_0.token import TokenAPI
from .v1_0.users import UserAPI, UserListAPI


api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(TokenAPI, '/v1_0/token/', endpoint='token')
api.add_resource(UserAPI, '/v1_0/users/<int:id>/', endpoint='user')
api.add_resource(UserListAPI, '/v1_0/users/', endpoint='users')
