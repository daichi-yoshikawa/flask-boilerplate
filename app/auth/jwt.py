import redis
from flask import jsonify, make_response
from flask_jwt_extended import JWTManager
from http import HTTPStatus

from app.auth.blacklist import blacklist

jwt = JWTManager()


def normalize_message(msg):
  return msg.capitalize().rstrip('.') + '.'


@jwt.unauthorized_loader
def token_not_found(reason):
  ret = {'error': {'message': normalize_message(reason)}}
  status = HTTPStatus.UNAUTHORIZED
  return make_response(jsonify(ret), status)


@jwt.expired_token_loader
def token_is_expired(expired_token):
  ret = {'error': {'message': f"The {expired_token['type']} has expired."}}
  status = HTTPStatus.UNAUTHORIZED
  return make_response(jsonfiy(ret), status)


@jwt.invalid_token_loader
def invalid_token(reason):
  ret = {'error': {'message': normalize_message(reason)}}
  status = HTTPStatus.UNPROCESSABLE_ENTITY
  return make_response(jsonify(ret), status)


@jwt.revoked_token_loader
def token_is_revoked():
  ret = {'error': {'message': 'Token has been revoked.'}}
  status = HTTPStatus.UNAUTHORIZED
  return make_response(jsonify(ret), status)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
  jti = decrypted_token['jti']
  return blacklist.has_revoked(jti)
