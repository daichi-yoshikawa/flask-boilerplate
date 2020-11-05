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


class TokenAPI(Resource):
  @jwt_required
  def get(self):
    """Validate access token."""
    return make_response(jsonify(), HTTPStatus.OK)

  def post(self):
    """Signin/Login"""
    status = HTTPStatus.OK
    ret = {}
    error_msg = ''

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

      self.probate_access_token(token=access_token)
      self.probate_refresh_token(token=refresh_token)
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      error_msg = str(e)
      if status == HTTPStatus.OK:
        status = HTTPStatus.BAD_REQUEST
        error_msg = 'Bad request was sent.'
    finally:
      if error_msg != '':
        ret = {'error': {'message': error_msg}}
        logger.error(ret)

    return make_response(jsonify(ret), status)

  @jwt_refresh_token_required
  def put(self):
    """Refresh access token.
    TODO : Revoke old/expired access token.
    """
    status = HTTPStatus.OK
    ret = {}
    error_msg = ''

    try:
      identity = get_jwt_identity()
      access_token = create_access_token(identity=identity)
      ret = {'access_token': access_token}

      if request.json is not None and 'access_token' in request.json:
        if len(request.json['access_token']) == 0:
          msg = 'Given access token is empty.'
          raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)
        old_access_token = request.json['access_token']
        old_access_jti = get_jti(encoded_token=old_access_token)
        blacklist.revoke_access_token(old_access_jti)
      else:
        msg = 'Access token is not in body.'
        raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)

      self.probate_access_token(token=access_token)
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      status = HTTPStatus.INTERNAL_SERVER_ERROR
      error_msg = str(e)
    finally:
      if error_msg != '':
        ret = {'error': {'message': error_msg}}
        logger.error(ret)

    return make_response(jsonify(ret), status)

  @jwt_required
  def delete(self):
    status = HTTPStatus.OK
    ret = {}
    error_msg = ''

    try:
      access_jti = get_raw_jwt()['jti']

      refresh_jti = None
      if request.json is not None and 'refresh_token' in request.json:
        if len(request.json['refresh_token']) == 0:
          msg = 'Given refresh token is empty.'
          raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)
        refresh_token = request.json['refresh_token']
        refresh_jti = get_jti(encoded_token=refresh_token)
        blacklist.revoke_refresh_token(refresh_jti)
      else:
        msg = 'Refresh token is not in body.'
        raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)

      blacklist.revoke_access_token(access_jti)
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      status = HTTPStatus.INTERNAL_SERVER_ERROR
      error_msg = str(e)
    finally:
      if error_msg != '':
        if 'access_jti' in locals():
          blacklist.probate_access_token(access_jti)
        if 'refresh_jti' in locals() and refresh_jti is not None:
          blacklist.probate_refresh_token(refresh_jti)
        ret = {'error': {'message': error_msg}}
        logger.error(ret)

    return make_response(jsonify(ret), status)

  def probate_access_token(self, token):
    self.probate_token(token, token_type_hint='access_token')

  def probate_refresh_token(self, token):
    self.probate_token(token, token_type_hint='refresh_token')

  def probate_token(self, token, token_type_hint):
    jti = get_jti(encoded_token=token)
    if blacklist.has_as_key(jti):
      raise ApiException(
          f'Given {token_type_hint} is already in blacklist.',
          status=HTTPStatus.UNAUTHORIZED)

    if token_type_hint == 'access_token':
      blacklist.probate_access_token(jti)
    elif token_type_hint == 'refresh_token':
      blacklist.probate_refresh_token(jti)
    else:
      msg = f'Unknown token{token_type_hint} is given.'
      raise ValueError(msg)
