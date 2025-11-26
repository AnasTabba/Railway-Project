from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from extensions import db
from models import Train, Station
from datetime import datetime

train_bp = Blueprint('trains', __name__, url_prefix='/api')

class TrainSchema(Schema):
    train_id = fields.Int(dump_only=True)
    train_number = fields.Str(required=True)
    name = fields.Str(required=True)
    operator = fields.Str(required=True)
    source_station_id = fields.Int(required=True)
    destination_station_id = fields.Int(required=True)
    active = fields.Bool()

train_schema = TrainSchema()
trains_schema = TrainSchema(many=True)

@train_bp.route('/trains', methods=['GET'])
def get_trains():
    try:
        trains = Train.query.filter_by(active=True).all()
        return jsonify([t.to_dict() for t in trains]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@train_bp.route('/trains/<int:train_id>', methods=['GET'])
def get_train(train_id):
    try:
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        return jsonify(train.to_dict(include_schedule=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@train_bp.route('/admin/trains', methods=['POST'])
@jwt_required()
def create_train():
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        errors = train_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        if Train.query.filter_by(train_number=data['train_number']).first():
            return jsonify({'error': 'Train number already exists'}), 409
        
        source = Station.query.get(data['source_station_id'])
        destination = Station.query.get(data['destination_station_id'])
        
        if not source or not destination:
            return jsonify({'error': 'Invalid station ID'}), 400
        
        train = Train(
            train_number=data['train_number'],
            name=data['name'],
            operator=data['operator'],
            source_station_id=data['source_station_id'],
            destination_station_id=data['destination_station_id'],
            active=data.get('active', True)
        )
        
        db.session.add(train)
        db.session.commit()
        
        return jsonify({
            'message': 'Train created successfully',
            'train': train.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@train_bp.route('/admin/trains/<int:train_id>', methods=['PUT'])
@jwt_required()
def update_train(train_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        data = request.get_json()
        
        train.name = data.get('name', train.name)
        train.operator = data.get('operator', train.operator)
        train.active = data.get('active', train.active)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Train updated successfully',
            'train': train.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@train_bp.route('/admin/trains/<int:train_id>', methods=['DELETE'])
@jwt_required()
def delete_train(train_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        db.session.delete(train)
        db.session.commit()
        
        return jsonify({'message': 'Train deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
