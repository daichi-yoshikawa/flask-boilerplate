from flask import jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from http import HTTPStatus
from werkzeug.security import check_password_hash

from app.models.user import User


class TokenAPI(Resource):
  def post(self):
    """Sign-in/Login"""
    status = HTTPStatus.OK
    ret = {}

    try:
      data = request.get_json()
      query = User.query.filter_by(email=data['email'])
      user = query.first()

      if user is None:
        status = HTTPStatus.NOT_FOUND
        raise Exception('User not found.')
      elif not check_password_hash(user.password, data['password']):
        status = HTTPStatus.UNAUTHORIZED
        raise Exception('Password was wrong.')

      access_token = create_access_token(identity=user.email)
      refresh_token = create_access_token(identity=user.email)

      ret = {
        'access_token': access_token,
        'refresh_token': refresh_token,
      }
    except Exception as e:
      ret = { 'error': { 'msg': str(e) } }

      if status == HTTPStatus.OK:
        status = HTTPStatus.BAD_REQUEST
        ret['error']['msg'] = 'Bad request was sent.'

    return make_response(jsonify(ret), status)


