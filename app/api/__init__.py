"""
Note: Unlike app.views, there's no need to avoid circular import.
"""

from flask import Blueprint
from flask_restful import Api

from .v1_0.token import TokenApi
from .v1_0.users import UserApi, UserListApi


api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(TokenApi, '/v1_0/token/', endpoint='token')
api.add_resource(UserApi, '/v1_0/users/<int:id>/', endpoint='user')
api.add_resource(UserListApi, '/v1_0/users/', endpoint='users')
