from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from extensions import db
from models import Station
from sqlalchemy import func

station_bp = Blueprint('stations', __name__, url_prefix='/api')

class StationSchema(Schema):
    station_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(required=True)
    country = fields.Str()
    platform_count = fields.Int()

station_schema = StationSchema()
stations_schema = StationSchema(many=True)

@station_bp.route('/stations', methods=['GET'])
def get_stations():
    try:
        stations = Station.query.all()
        return jsonify(stations_schema.dump(stations)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@station_bp.route('/stations/<int:station_id>', methods=['GET'])
def get_station(station_id):
    try:
        station = Station.query.get(station_id)
        if not station:
            return jsonify({'error': 'Station not found'}), 404
        return jsonify(station_schema.dump(station)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@station_bp.route('/admin/stations', methods=['POST'])
@jwt_required()
def create_station():
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        errors = station_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        if Station.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Station code already exists'}), 409
        
        station = Station(
            name=data['name'],
            code=data['code'],
            city=data['city'],
            province=data['province'],
            country=data.get('country', 'India'),
            platform_count=data.get('platform_count', 1)
        )
        
        db.session.add(station)
        db.session.commit()
        
        return jsonify({
            'message': 'Station created successfully',
            'station': station_schema.dump(station)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@station_bp.route('/admin/stations/<int:station_id>', methods=['PUT'])
@jwt_required()
def update_station(station_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        station = Station.query.get(station_id)
        if not station:
            return jsonify({'error': 'Station not found'}), 404
        
        data = request.get_json()
        
        station.name = data.get('name', station.name)
        station.city = data.get('city', station.city)
        station.province = data.get('province', station.province)
        station.country = data.get('country', station.country)
        station.platform_count = data.get('platform_count', station.platform_count)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Station updated successfully',
            'station': station_schema.dump(station)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@station_bp.route('/admin/stations/<int:station_id>', methods=['DELETE'])
@jwt_required()
def delete_station(station_id):
    try:
        user_id = int(get_jwt_identity())
        from models import User
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        station = Station.query.get(station_id)
        if not station:
            return jsonify({'error': 'Station not found'}), 404
        
        db.session.delete(station)
        db.session.commit()
        
        return jsonify({'message': 'Station deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
