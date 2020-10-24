import logging

from flask import jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from werkzeug.security import check_password_hash

from app.models.user import User


logger = logging.getLogger(__name__)

class TokenAPI(Resource):
  def post(self):
    """Sign-in/Login"""
    status = HTTPStatus.OK
    ret = {}

    try:
      data = request.get_json()
      user = User.query.filter_by(email=data['email']).first()

      if user is None:
        status = HTTPStatus.NOT_FOUND
        raise Exception(f"User({data['email']}) is already registered.")
      elif not check_password(user.password, data['password']):
        status = HTTPStatus.UNAUTHORIZED
        raise Exception('Password was wrong.')

      identity = user.email
      access_token = create_access_token(identity=identity)
      refresh_token = create_refresh_token(identity=identity)

      ret = {
        'access_token': access_token,
        'refresh_token': refresh_token,
      }
    except Exception as e:
      logger.error(e)
      msg = str(e)
      if status == HTTPStatus.OK:
        status = HTTPStatus.BAD_REQUEST
        msg = 'Invalid request was sent.'
      ret = { 'error': { 'message': msg } }
      logger.error(ret)

    return make_response(jsonify(ret), status)
