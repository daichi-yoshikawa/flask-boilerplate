import logging

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from http import HTTPStatus
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User, UserSchema
from app.api.utils import get_url
from app.utils.exceptions import ApiException

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
        raise ApiException('Request is empty.', status=HTTPStatus.BAD_REQUEST)

      if User.query.filter_by(name=data['name']).count() > 0:
        raise ApiException(
          f"Username:{data['name']} is already used.", status=HTTPStatus.CONFLICT)

      if User.query.filter_by(email=data['email']).count() > 0:
        raise ApiException(
          f"Email:{data['email']} is already used.", status=HTTPStatus.CONFLICT)

      data['password'] = generate_password_hash(data['password'])
      user = User(**data)
      db.session.add(user)
      db.session.commit()

      ret['url'] = get_url(tail_url=user.id)
    except ApiException as e:
      status = e.status
      ret = {'error': {'message': str(e)}}
      db.session.rollback()
      logger.error(ret)
    except Exception as e:
      db.session.rollback()
      msg = str(e)
      if status == HTTPStatus.CREATED:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        msg = 'Signup failed due to internal server error.'
      ret = { 'error': { 'message': msg } }
      logger.error(ret)

    return make_response(jsonify(ret), status)


class UserAPI(Resource):
  """
  GET: Return user.
  POST: N/A
  PUT: Update user data.
  DELETE: Delete user account.
  """
  @jwt_required
  def get(self, id):
    """Return user."""
    status = HTTPStatus.OK
    ret = {}

    try:
      query = User.query.filter_by(id=id)
      ret = UserSchema(many=False).dump(query.first())
      if not ret:
        raise ApiException(
          f'User ID:{id} was not found.', status=HTTPStatus.NOT_FOUND)
      ret['url'] = get_url(tail_url='')
    except ApiException as e:
      status = e.status
      ret = {'error': {'message': str(e)}}
      logger.error(ret)
    except Exception as e:
      ret = { 'error': { 'message': str(e) } }
      logger.error(ret)

    return make_response(jsonify(ret), status)
