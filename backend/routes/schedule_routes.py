from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from extensions import db
from models import TrainSchedule, Train, Station
from datetime import datetime

schedule_bp = Blueprint('schedules', __name__, url_prefix='/api')

class TrainScheduleSchema(Schema):
    schedule_id = fields.Int(dump_only=True)
    train_id = fields.Int(required=True)
    station_id = fields.Int(required=True)
    arrival_time = fields.DateTime()
    departure_time = fields.DateTime()
    stop_order = fields.Int(required=True)
    platform_number = fields.Str()

schedule_schema = TrainScheduleSchema()
schedules_schema = TrainScheduleSchema(many=True)

@schedule_bp.route('/trains/<int:train_id>/schedule', methods=['GET'])
def get_train_schedule(train_id):
    try:
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        schedules = TrainSchedule.query.filter_by(train_id=train_id).order_by(TrainSchedule.stop_order).all()
        return jsonify([s.to_dict() for s in schedules]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/admin/schedule', methods=['POST'])
@jwt_required()
def create_schedule():
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        errors = schedule_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        train = Train.query.get(data['train_id'])
        station = Station.query.get(data['station_id'])
        
        if not train or not station:
            return jsonify({'error': 'Invalid train or station ID'}), 400
        
        schedule = TrainSchedule(
            train_id=data['train_id'],
            station_id=data['station_id'],
            arrival_time=datetime.fromisoformat(data['arrival_time']) if data.get('arrival_time') else None,
            departure_time=datetime.fromisoformat(data['departure_time']) if data.get('departure_time') else None,
            stop_order=data['stop_order'],
            platform_number=data.get('platform_number')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/admin/schedule/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        schedule = TrainSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        data = request.get_json()
        
        if 'arrival_time' in data:
            schedule.arrival_time = datetime.fromisoformat(data['arrival_time']) if data['arrival_time'] else None
        if 'departure_time' in data:
            schedule.departure_time = datetime.fromisoformat(data['departure_time']) if data['departure_time'] else None
        if 'platform_number' in data:
            schedule.platform_number = data['platform_number']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'schedule': schedule.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/admin/schedule/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        schedule = TrainSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'message': 'Schedule deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
