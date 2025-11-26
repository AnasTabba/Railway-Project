from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Reservation, Payment, Seat, Coach, Fare, Train, TrainSchedule, User
from datetime import datetime, timedelta
import uuid
from sqlalchemy import and_

booking_bp = Blueprint('bookings', __name__, url_prefix='/api')

def generate_pnr():
    """Generate unique PNR (Passenger Name Record)"""
    return f"PNR{uuid.uuid4().hex[:10].upper()}"

@booking_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    """
    Create a reservation (seat on HOLD)
    Body: {
        train_id: int,
        journey_date: YYYY-MM-DD,
        class_id: int,
        seat_id: int (optional - auto-assign if not provided)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json() or {}
        train_id = data.get('train_id')
        journey_date_str = data.get('journey_date')
        class_id = data.get('class_id')
        seat_id = data.get('seat_id')
        passenger_name = data.get('passenger_name')
        passenger_age = data.get('passenger_age')
        passenger_email = data.get('passenger_email')
        
        if not all([train_id, journey_date_str, class_id]):
            return jsonify({'error': 'train_id, journey_date, and class_id are required'}), 400
        
        try:
            journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        # Find coach of specified class for the train
        coach = Coach.query.filter_by(train_id=train_id, class_id=class_id).first()
        if not coach:
            return jsonify({'error': 'Coach class not available on this train'}), 404
        
        # Auto-assign seat if not provided
        if not seat_id:
            available_seat = Seat.query.filter(
                Seat.coach_id == coach.coach_id,
                ~Seat.reservations.any(
                    and_(
                        Reservation.journey_date == journey_date,
                        Reservation.status.in_(['BOOKED', 'HOLD'])
                    )
                )
            ).first()
            
            if not available_seat:
                return jsonify({'error': 'No available seats in this class'}), 409
            seat_id = available_seat.seat_id
        else:
            # Verify seat is available
            seat = Seat.query.get(seat_id)
            if not seat or seat.coach_id != coach.coach_id:
                return jsonify({'error': 'Invalid seat selection'}), 400
            
            existing_reservation = Reservation.query.filter_by(
                seat_id=seat_id,
                journey_date=journey_date,
                train_id=train_id
            ).filter(Reservation.status.in_(['BOOKED', 'HOLD'])).first()
            
            if existing_reservation:
                return jsonify({'error': 'Seat already reserved'}), 409
        
        # Create reservation with HOLD status
        pnr = generate_pnr()
        hold_expires_at = datetime.utcnow() + timedelta(seconds=600)  # 10 minutes hold
        
        reservation = Reservation(
            pnr=pnr,
            user_id=user_id,
            train_id=train_id,
            journey_date=journey_date,
            coach_id=coach.coach_id,
            seat_id=seat_id,
            status='HOLD',
            hold_expires_at=hold_expires_at,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            passenger_email=passenger_email
        )
        
        # Create payment record with PENDING status
        fare = Fare.query.filter(
            Fare.class_id == class_id,
            Fare.start_date <= journey_date,
            Fare.end_date >= journey_date
        ).first()
        
        if not fare:
            return jsonify({'error': 'No fare available for this journey date'}), 404
        
        payment = Payment(
            reservation=reservation,
            amount=fare.price,
            method='PENDING',
            status='PENDING'
        )
        
        db.session.add(reservation)
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation created (HOLD for 10 minutes)',
            'reservation': {
                'pnr': pnr,
                'train_id': train_id,
                'journey_date': journey_date_str,
                'seat': Seat.query.get(seat_id).to_dict() if seat_id else None,
                'status': 'HOLD',
                'hold_expires_at': hold_expires_at.isoformat(),
                'fare_amount': float(fare.price),
                'passenger_name': passenger_name,
                'passenger_age': passenger_age,
                'passenger_email': passenger_email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/reservations/<pnr>', methods=['GET'])
@jwt_required()
def get_reservation(pnr):
    """Get reservation details"""
    try:
        user_id = int(get_jwt_identity())
        reservation = Reservation.query.filter_by(pnr=pnr).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        # Check authorization
        if reservation.user_id != user_id:
            from models import User as UserModel
            user = UserModel.query.get(user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'reservation': reservation.to_dict(),
            'payment': reservation.payment.to_dict() if reservation.payment else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_user_reservations():
    """Get all reservations for current user"""
    try:
        user_id = int(get_jwt_identity())
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'reservations': [r.to_dict() for r in reservations],
            'count': len(reservations)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/reservations/<pnr>/cancel', methods=['POST'])
@jwt_required()
def cancel_reservation(pnr):
    """
    Cancel a reservation with refund logic:
    - >24 hrs before departure: full refund
    - 6-24 hrs before departure: 50% refund
    - <6 hrs before departure: no refund
    """
    try:
        user_id = int(get_jwt_identity())
        reservation = Reservation.query.filter_by(pnr=pnr).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.user_id != user_id:
            from models import User as UserModel
            user = UserModel.query.get(user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Unauthorized'}), 403
        
        if reservation.status == 'CANCELLED':
            return jsonify({'error': 'Reservation already cancelled'}), 400
        
        # Get train schedule to calculate departure time
        train_schedule = TrainSchedule.query.filter_by(
            train_id=reservation.train_id,
            station_id=reservation.train.source_station_id
        ).first()
        
        if train_schedule and train_schedule.departure_time:
            departure_time = datetime.combine(reservation.journey_date, train_schedule.departure_time.time())
            time_until_departure = departure_time - datetime.utcnow()
            hours_until_departure = time_until_departure.total_seconds() / 3600
            
            # Determine refund policy
            if hours_until_departure > 24:
                refund_status = 'FULL_REFUND'
                refund_amount = reservation.payment.amount if reservation.payment else 0
            elif hours_until_departure > 6:
                refund_status = 'PARTIAL_REFUND'
                refund_amount = (reservation.payment.amount * 0.5) if reservation.payment else 0
            else:
                refund_status = 'NO_REFUND'
                refund_amount = 0
        else:
            # If no schedule found, default to partial refund
            refund_status = 'PARTIAL_REFUND'
            refund_amount = (reservation.payment.amount * 0.5) if reservation.payment else 0
        
        reservation.status = 'CANCELLED'
        
        if reservation.payment:
            reservation.payment.refund_status = refund_status
            reservation.payment.refund_amount = refund_amount
            reservation.payment.refunded_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation cancelled successfully',
            'pnr': pnr,
            'refund': {
                'status': refund_status,
                'amount': float(refund_amount) if refund_amount else 0
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
