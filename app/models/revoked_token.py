from datetime import datetime

from marshmallow import Schema
from marshmallow import fields, validate
from sqlalchemy import func
from sqlalchemy.sql import expression

from app.models import db


class RevokedToken(db.Model):
  __tablename__ = 'revoked_tokens'
  id = db.Column(db.Integer, primary_key=True)
  jti = db.Column(db.Text, unique=True, nullable=False)
  revoked = db.Column(db.Boolean, nullable=False, server_default=expression.false())
  token_type_hint = db.Column(db.String(64), nullable=False)
  expires_in = db.Column(db.BigInteger, nullable=False)
  revoked_at = db.Column(db.DateTime, nullable=True)
  created_at = db.Column(db.DateTime, server_default=func.now())
  updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now())

  def __repr__(self):
    return f'RevokedToken(id={self.id}, jti={self.jti}, ' +\
           f'revoked={self.revoked}, token_type_hint={self.token_type_hint}, ' +\
           f'expires_in={self.expires_in}, revoked_at={self.revoked_at})'


class RevokedTokenSchema(Schema):
  id = fields.Integer(
    required=True,
    validate=[
      validate.Range(min=1, error='ID must be > 0.'),
    ])
  jti = fields.String(
    required=True,
    validate=[
      validate.Length(min=4, error='Token is too short.'),
    ])
  revoked = fields.Boolean(required=True)
  token_type_hint = fields.String(
    required=True,
    validate=[
      validate.OneOf(
          choices=['access_token', 'refresh_token'],
          error='Invalid value for token type.'),
    ])
  expires_in = fields.Integer(
    required=True,
    validate=[
      validate.Range(min=1, error='expires_in must be > 0.'),
    ])
  revoked_at = fields.DateTime()
