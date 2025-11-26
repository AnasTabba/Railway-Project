from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from marshmallow import Schema

db = SQLAlchemy()
jwt = JWTManager()
