import logging
import os

from flask import jsonify, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jti, get_jwt_identity, get_raw_jwt
from flask_jwt_extended import jwt_refresh_token_required, jwt_required
from flask_jwt_extended.config import config
from flask_restful import Resource
from http import HTTPStatus
from jwt.exceptions import ExpiredSignatureError
from marshmallow import ValidationError, Schema
from werkzeug.security import check_password_hash

from app.auth.blacklist import blacklist
from app.models.user import User, user_schema
from app.utils.exceptions import ApiException


logger = logging.getLogger(__name__)


def try_revoke_access_token(token):
  try:
    jti = get_jti(encoded_token=token)
    blacklist.revoke_access_token(jti)
  except ExpiredSignatureError as e:
    logger.warning(f'{str(type(e))}: {str(e)}')


def try_revoke_refresh_token(token):
  try:
    jti = get_jti(encoded_token=token)
    blacklist.revoke_refresh_token(jti)
  except ExpiredSignatureError as e:
    logger.warning(f'{str(type(e))}: {str(e)}')


class RequestSchema:
  class PostToken(Schema):
    email = type(user_schema.fields['email'])(
        required=True, validate=user_schema.fields['email'].validate)
    password = type(user_schema.fields['password'])(
        required=True, validate=user_schema.fields['password'].validate)


class TokenApi(Resource):
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
      if data is None:
        raise ApiException('Request is empty.', status=HTTPStatus.BAD_REQUEST)
      errors = RequestSchema.PostToken().validate(data)
      if errors:
        raise ValidationError(errors)

      query = User.query.filter_by(email=data['email'])
      user = query.first()

      if user is None:
        raise ApiException(
            f"User:({data['email']}) not found.",
            status=HTTPStatus.NOT_FOUND)
      elif not check_password_hash(user.password, data['password']):
        raise ApiException('Wrong password.', status=HTTPStatus.UNAUTHORIZED)

      access_token = create_access_token(identity=user.email)
      refresh_token = create_refresh_token(identity=user.email)
      access_expires_in = int(config.access_expires.total_seconds())
      refresh_expires_in = int(config.refresh_expires.total_seconds())

      ret = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_expires_in': access_expires_in,
        'refresh_expires_in': refresh_expires_in,
      }

      self.probate_access_token(token=access_token)
      self.probate_refresh_token(token=refresh_token)
    except ValidationError as e:
      status = HTTPStatus.BAD_REQUEST
      error_msg = e.normalized_messages()
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
        ret = { 'error': { 'message': error_msg } }
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
      access_expires_in = int(config.access_expires.total_seconds())
      ret = {
        'access_token': access_token,
        'access_expires_in': access_expires_in,
      }

      if request.json is not None and 'access_token' in request.json:
        if len(request.json['access_token']) == 0:
          msg = 'Given access token is empty.'
          raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)
        old_access_token = request.json['access_token']
        try_revoke_access_token(old_access_token)
      else:
        msg = 'Access token is not in body.'
        raise ApiException(msg, status=HTTPStatus.BAD_REQUEST)

      self.probate_access_token(token=access_token)
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      status = HTTPStatus.INTERNAL_SERVER_ERROR
      error_msg = f'{str(type(e))}: {str(e)}'
    finally:
      if error_msg != '':
        ret = { 'error': { 'message': error_msg } }
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
        try_revoke_refresh_token(refresh_token)
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
        ret = { 'error': { 'message': error_msg } }
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
          f'Given {token_type_hint}:{jti} is already in blacklist.',
          status=HTTPStatus.UNAUTHORIZED)

    if token_type_hint == 'access_token':
      blacklist.probate_access_token(jti)
    elif token_type_hint == 'refresh_token':
      blacklist.probate_refresh_token(jti)
    else:
      msg = f'Unknown token{token_type_hint} is given.'
      raise ValueError(msg)
