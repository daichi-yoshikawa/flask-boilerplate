from datetime import datetime

from marshmallow import Schema
from marshmallow import fields, validate
from sqlalchemy import func

from app.models import db


class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), nullable=False)
  created_at = db.Column(db.DateTime, server_default=func.now())
  updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now())

  def __repr__(self):
    return f'Role(id={self.id}, name={self.name})'


class RoleSchema(Schema):
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
        min=1, max=64, error='Name length must be {min} - {max}.'),
    ])


role_schema = RoleSchema()
