from flask_restful import Resource

from app.models import db
from app.models.user import User


class UserListAPI(Resource):
  def get(self):
    return {'user': 'list'}
