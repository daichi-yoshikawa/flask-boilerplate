import logging

from flask import jsonify, make_response, request
from flask_restful import Resource
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User, UserSchema
from app.api.utils import get_url

logger = logging.getLogger(__name__)


class UserListAPI(Resource):
  """
  GET: Return all users.
  POST: Create new user account.
  PUT: N/A
  DELETE: N/A
  """
  def post(self):
    """Sign up"""
    status = HTTPStatus.CREATED
    ret = {}

    try:
      data = request.get_json()
      if data is None:
        status = HTTPStatus.BAD_REQUEST
        raise Exception('Request is empty.')
      query = User.query.filter_by(email=data['email'])
      user = query.first()

      if user is None:
        data['password'] = generate_password_hash(data['password'])
        user = User(**data)
        db.session.add(user)
        db.session.commit()
      else:
        status = HTTPStatus.OK

      ret['url'] = get_url(tail_url=user.id)
    except Exception as e:
      logger.error(e)
      db.session.rollback()
      msg = str(e)
      if status == HTTPStatus.CREATED:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        msg = 'Signup failed due to internal server error.'
      ret = { 'error': { 'message': msg } }
      logger.error(ret)

    return make_response(jsonify(ret), status)

  def get(self):
    return {'user': 'list'}


class UserAPI(Resource):
  """
  GET: Return user.
  POST: N/A
  PUT: Update user data.
  DELETE: Delete user account.
  """
  def get(self, id):
    """Return user."""
    status = HTTPStatus.OK
    ret = {}

    try:
      query = User.query.filter_by(id=id)
      ret = UserSchema(many=False).dump(query.first())
      if not ret:
        status = HTTPStatus.NOT_FOUND
        raise Exception(f'User {id} was not found.')
      ret['url'] = get_url(tail_url='')
    except Exception as e:
      logger.error(e)
      ret = { 'error': { 'message': str(e) } }
      logger.error(ret)

    return make_response(jsonify(ret), status)
