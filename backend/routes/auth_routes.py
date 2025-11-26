from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from extensions import db
from models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

class UserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=lambda x: len(x) >= 2)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=lambda x: len(x) >= 6)
    phone = fields.Str()
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        errors = user_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.user_id))
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=str(user.user_id))
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
