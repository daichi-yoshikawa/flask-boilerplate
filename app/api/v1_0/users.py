import json
import logging

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from http import HTTPStatus
from marshmallow import ValidationError, Schema
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User, user_schema
from app.api.utils import get_url
from app.utils.exceptions import ApiException

logger = logging.getLogger(__name__)


class RequestSchema:
  class PostUsers(Schema):
    name = type(user_schema.fields['name'])(
        required=True, validate=user_schema.fields['name'].validate)
    email = type(user_schema.fields['email'])(
        required=True, validate=user_schema.fields['email'].validate)
    password = type(user_schema.fields['password'])(
        required=True, validate=user_schema.fields['password'].validate)
    role_id = type(user_schema.fields['role_id'])(
        required=True, validate=user_schema.fields['role_id'].validate)


class ResponseSchema:
  class GetUser(Schema):
    id = type(user_schema.fields['id'])(
        required=True, validate=user_schema.fields['name'].validate)
    name = type(user_schema.fields['name'])(
        required=True, validate=user_schema.fields['name'].validate)
    email = type(user_schema.fields['email'])(
        required=True, validate=user_schema.fields['email'].validate)


class UserListApi(Resource):
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
    error_msg = {}

    try:
      data = request.get_json()
      if data is None:
        raise ApiException('Request is empty.', status=HTTPStatus.BAD_REQUEST)
      errors = RequestSchema.PostUsers().validate(data)
      if errors:
        raise ValidationError(errors)
      data = RequestSchema.PostUsers().dump(data)

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

      ret['link'] = {'self': get_url(tail_url=user.id)}
    except ValidationError as e:
      status = HTTPStatus.BAD_REQUEST
      error_msg = e.normalized_messages()
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      error_msg = f'{type(e)} : {str(e)} '
      if status == HTTPStatus.CREATED:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        error_msg = f'Signup failed due to internal server error. ' + error_msg
    finally:
      if status != HTTPStatus.CREATED:
        db.session.rollback()
        ret = { 'error': { 'message': error_msg } }
        logger.error(ret)

    return make_response(jsonify(ret), status)


class UserApi(Resource):
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
    error_msg = ''

    try:
      query = User.query.filter_by(id=id)
      user = query.first()
      if not user:
        raise ApiException(
          f'User ID:{id} was not found.', status=HTTPStatus.NOT_FOUND)

      ret = ResponseSchema.GetUser().dump(user)
      ret['link'] = {'self': get_url(tail_url='')}
    except ApiException as e:
      status = e.status
      error_msg = str(e)
    except Exception as e:
      status.e = HTTPStatus.INTERNAL_SERVER_ERROR
      error_msg = str(e)
    finally:
      if error_msg != '':
        ret = { 'error': { 'message': error_msg } }
        logger.error(ret)

    return make_response(jsonify(ret), status)
