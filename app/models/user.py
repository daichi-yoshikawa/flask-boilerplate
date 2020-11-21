from datetime import datetime

from marshmallow import Schema
from marshmallow import fields, validate
from sqlalchemy import func
from sqlalchemy.sql import expression

from app.models import db


class User(db.Model):
  name = 'users'
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), unique=True, nullable=False)
  email = db.Column(db.String(128), unique=True, nullable=False)
  password = db.Column(db.String(128), unique=False, nullable=False)
  created_at = db.Column(db.DateTime, server_default=func.now())
  updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now())

  def __repr__(self):
    return f'User(id={self.id}, name={self.name}, email={self.email})'


class UserSchema(Schema):
  """
  References
  ==========
  https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html
  """
  id = fields.Integer(
    required=True,
    validate=[
      validate.Range(min=1, error='ID must be > 0.'),
    ])
  name = fields.String(
    required=True,
    validate=[
      validate.Length(
          min=4, max=64, error='Name length must be {min} - {max}.'),
    ])
  email = fields.Email(required=True)
  password = fields.String(
    required=True,
    validate=[
      validate.Length(
          min=8, error='Password must be at least {min} characters.'),
    ])


user_schema = UserSchema()
