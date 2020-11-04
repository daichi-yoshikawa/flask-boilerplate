import logging

from flask import jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jti, get_jwt_identity, get_raw_jwt
from flask_jwt_extended import jwt_refresh_token_required, jwt_required
from flask_restful import Resource
from http import HTTPStatus
from werkzeug.security import check_password_hash

from app.auth.blacklist import blacklist
from app.models.user import User
from app.utils.exceptions import ApiException


logger = logging.getLogger(__name__)


def delete_impl():
  status = HTTPStatus.OK
  ret = {}

  try:
    blacklist.revoke(get_raw_jwt()['jti'])
  except Exception as e:
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    ret = {'error': {'message': str(e)}}
    logger.error(ret)

  return make_response(jsonify(ret), status)


class TokenAPI(Resource):
  @jwt_required
  def get(self):
    """Validate access token."""
    return make_response(jsonify(), HTTPStatus.OK)

  def post(self):
    """Signin/Login"""
    status = HTTPStatus.OK
    ret = {}

    try:
      data = request.get_json()
      query = User.query.filter_by(name=data['name'], email=data['email'])
      user = query.first()

      if user is None:
        raise ApiException(
          f"User:({data['name']}, {data['email']}) not found.",
          status=HTTPStatus.NOT_FOUND)
      elif not check_password_hash(user.password, data['password']):
        raise ApiException('Wrong password.', status=HTTPStatus.UNAUTHORIZED)

      access_token = create_access_token(identity=user.email)
      refresh_token = create_refresh_token(identity=user.email)
      ret = {
        'access_token': access_token,
        'refresh_token': refresh_token,
      }

      self.add_token_to_blacklist_as_candidate(access_token, 'access token')
      self.add_token_to_blacklist_as_candidate(refresh_token, 'refresh token')
    except ApiException as e:
      status = e.status
      ret = {'error': {'message': str(e)}}
      logger.error(ret)
    except Exception as e:
      ret = {'error': {'message': str(e)}}
      if status == HTTPStatus.OK:
        status = HTTPStatus.BAD_REQUEST
        ret['error']['message'] = 'Bad request was sent.'
      logger.error(ret)

    return make_response(jsonify(ret), status)

  @jwt_refresh_token_required
  def put(self):
    """Refresh access token.
    TODO : Revoke old/expired access token.
    """
    status = HTTPStatus.OK
    ret = {}

    try:
      identity = get_jwt_identity()
      access_token = create_access_token(identity=identity)
      ret = {'access_token': access_token}
      self.add_token_to_blacklist_as_candidate(access_token, 'access token')

      """ May need to revoke old access token somehow.
      if request.json and request.json['access_token']:
         jti_old = get_jti(encoded_token=tokenrequest.json['access_token'])
      blacklist.revoke(jti_old)
      """
    except ApiException as e:
      status = e.status
      ret = {'error': {'message': str(e)}}
      logger.error(ret)
    except Exception as e:
      status = HTTPStatus.INTERNAL_SERVER_ERROR
      ret = {'error': {'message': str(e)}}
      logger.error(ret)

    return make_response(jsonify(ret), status)

  @jwt_required
  def delete(self):
    """Logout (to revoke access token)"""
    return delete_impl()

  def add_token_to_blacklist_as_candidate(self, token, xxx_token):
    jti = get_jti(encoded_token=token)
    if blacklist.has_as_key(jti):
      raise ApiException(
        f'Given {xxx_token} is already in blacklist.',
        status=HTTPStatus.UNAUTHORIZED)
    blacklist.add_candidate(jti=jti)


class RefreshTokenAPI(Resource):
  @jwt_refresh_token_required
  def delete(self):
    """Logout (to revoke refresh token)"""
    return delete_impl()
