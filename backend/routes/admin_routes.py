from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import (
    User, Station, Train, TrainSchedule, Coach, 
    CoachClass, Seat, Fare, Service, Reservation, Payment
)
from marshmallow import Schema, fields

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Schemas
class CoachClassSchema(Schema):
    class_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    capacity_per_coach = fields.Int(required=True)

class CoachSchema(Schema):
    coach_id = fields.Int(dump_only=True)
    train_id = fields.Int(required=True)
    class_id = fields.Int(required=True)
    coach_number = fields.Str(required=True)
    capacity = fields.Int(required=True)

class SeatSchema(Schema):
    seat_id = fields.Int(dump_only=True)
    coach_id = fields.Int(required=True)
    seat_number = fields.Str(required=True)
    berth_type = fields.Str()

class FareSchema(Schema):
    fare_id = fields.Int(dump_only=True)
    class_id = fields.Int(required=True)
    price = fields.Decimal(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

class ServiceSchema(Schema):
    service_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    class_id = fields.Int(required=True)
    valid_from = fields.Date(required=True)
    valid_to = fields.Date(required=True)

coach_class_schema = CoachClassSchema()
coach_classes_schema = CoachClassSchema(many=True)
coach_schema = CoachSchema()
coaches_schema = CoachSchema(many=True)
seat_schema = SeatSchema()
seats_schema = SeatSchema(many=True)
fare_schema = FareSchema()
fares_schema = FareSchema(many=True)
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

def admin_required(f):
    """Decorator to ensure admin access"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Coach Classes Management
@admin_bp.route('/coach-classes', methods=['GET'])
def get_coach_classes():
    try:
        classes = CoachClass.query.all()
        return jsonify(coach_classes_schema.dump(classes)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/coach-classes', methods=['POST'])
@admin_required
def create_coach_class():
    try:
        data = request.get_json()
        errors = coach_class_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        if CoachClass.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Coach class already exists'}), 409
        
        coach_class = CoachClass(
            name=data['name'],
            description=data.get('description'),
            capacity_per_coach=data['capacity_per_coach']
        )
        
        db.session.add(coach_class)
        db.session.commit()
        
        return jsonify({
            'message': 'Coach class created successfully',
            'coach_class': coach_class_schema.dump(coach_class)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Coaches Management
@admin_bp.route('/coaches', methods=['GET'])
def get_coaches():
    try:
        train_id = request.args.get('train_id')
        if train_id:
            coaches = Coach.query.filter_by(train_id=int(train_id)).all()
        else:
            coaches = Coach.query.all()
        return jsonify([c.to_dict() for c in coaches]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/coaches', methods=['POST'])
@admin_required
def create_coach():
    try:
        data = request.get_json()
        errors = coach_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        train = Train.query.get(data['train_id'])
        coach_class = CoachClass.query.get(data['class_id'])
        
        if not train or not coach_class:
            return jsonify({'error': 'Invalid train or class ID'}), 400
        
        coach = Coach(
            train_id=data['train_id'],
            class_id=data['class_id'],
            coach_number=data['coach_number'],
            capacity=data['capacity']
        )
        
        db.session.add(coach)
        db.session.commit()
        
        return jsonify({
            'message': 'Coach created successfully',
            'coach': coach.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Seats Management
@admin_bp.route('/seats', methods=['GET'])
def get_seats():
    try:
        coach_id = request.args.get('coach_id')
        if coach_id:
            seats = Seat.query.filter_by(coach_id=int(coach_id)).all()
        else:
            seats = Seat.query.all()
        return jsonify([s.to_dict() for s in seats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/seats', methods=['POST'])
@admin_required
def create_seat():
    try:
        data = request.get_json()
        errors = seat_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        coach = Coach.query.get(data['coach_id'])
        if not coach:
            return jsonify({'error': 'Coach not found'}), 404
        
        seat = Seat(
            coach_id=data['coach_id'],
            seat_number=data['seat_number'],
            berth_type=data.get('berth_type')
        )
        
        db.session.add(seat)
        db.session.commit()
        
        return jsonify({
            'message': 'Seat created successfully',
            'seat': seat.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Fares Management
@admin_bp.route('/fares', methods=['GET'])
def get_fares():
    try:
        class_id = request.args.get('class_id')
        if class_id:
            fares = Fare.query.filter_by(class_id=int(class_id)).all()
        else:
            fares = Fare.query.all()
        return jsonify([f.to_dict() for f in fares]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/fares', methods=['POST'])
@admin_required
def create_fare():
    try:
        data = request.get_json()
        errors = fare_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        coach_class = CoachClass.query.get(data['class_id'])
        if not coach_class:
            return jsonify({'error': 'Coach class not found'}), 404
        
        from datetime import datetime
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if isinstance(data['start_date'], str) else data['start_date']
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if isinstance(data['end_date'], str) else data['end_date']
        
        fare = Fare(
            class_id=data['class_id'],
            price=data['price'],
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(fare)
        db.session.commit()
        
        return jsonify({
            'message': 'Fare created successfully',
            'fare': fare.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Services Management
@admin_bp.route('/services', methods=['GET'])
def get_services():
    try:
        class_id = request.args.get('class_id')
        if class_id:
            services = Service.query.filter_by(class_id=int(class_id)).all()
        else:
            services = Service.query.all()
        return jsonify([s.to_dict() for s in services]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['POST'])
@admin_required
def create_service():
    try:
        data = request.get_json()
        errors = service_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        coach_class = CoachClass.query.get(data['class_id'])
        if not coach_class:
            return jsonify({'error': 'Coach class not found'}), 404
        
        from datetime import datetime
        valid_from = datetime.strptime(data['valid_from'], '%Y-%m-%d').date() if isinstance(data['valid_from'], str) else data['valid_from']
        valid_to = datetime.strptime(data['valid_to'], '%Y-%m-%d').date() if isinstance(data['valid_to'], str) else data['valid_to']
        
        service = Service(
            name=data['name'],
            description=data.get('description'),
            class_id=data['class_id'],
            valid_from=valid_from,
            valid_to=valid_to
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Reservations Management
@admin_bp.route('/reservations', methods=['GET'])
@admin_required
def get_all_reservations():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        reservations = Reservation.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'reservations': [r.to_dict() for r in reservations.items],
            'total': reservations.total,
            'pages': reservations.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@admin_required
def delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        db.session.delete(reservation)
        db.session.commit()
        
        return jsonify({'message': 'Reservation deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Users Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'users': [u.to_dict() for u in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['USER', 'ADMIN']:
            return jsonify({'error': 'Invalid role'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
