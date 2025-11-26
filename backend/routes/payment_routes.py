from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Payment, Reservation, User
from datetime import datetime
import random
import string

payment_bp = Blueprint('payments', __name__, url_prefix='/api')

@payment_bp.route('/payments/<int:reservation_id>', methods=['POST'])
@jwt_required()
def process_payment(reservation_id):
    """
    Simulate payment processing
    Body: {
        method: str (CREDIT_CARD, DEBIT_CARD, UPI, etc.),
        card_number: str (optional, for demo)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.user_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Unauthorized'}), 403
        
        if reservation.status != 'HOLD':
            return jsonify({'error': 'Reservation must be in HOLD status to process payment'}), 400
        
        payment = reservation.payment
        if not payment:
            return jsonify({'error': 'No payment record found'}), 404
        
        data = request.get_json()
        method = data.get('method', 'CREDIT_CARD')
        
        # Simulate payment processing (in real scenario, call payment gateway)
        # Random success rate of 95% for demo
        is_success = random.random() < 0.95
        
        if is_success:
            payment.method = method
            payment.status = 'PAID'
            payment.paid_at = datetime.utcnow()
            reservation.status = 'BOOKED'
            reservation.hold_expires_at = None
            
            db.session.commit()
            
            return jsonify({
                'message': 'Payment processed successfully',
                'pnr': reservation.pnr,
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'status': 'PAID',
                'transaction_id': f"TXN{''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}"
            }), 200
        else:
            payment.status = 'FAILED'
            db.session.commit()
            
            return jsonify({
                'error': 'Payment failed. Please try again.',
                'status': 'FAILED'
            }), 402
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details"""
    try:
        user_id = int(get_jwt_identity())
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.reservation.user_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(payment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/reservations/<pnr>/payment', methods=['GET'])
@jwt_required()
def get_reservation_payment(pnr):
    """Get payment details for a reservation"""
    try:
        user_id = int(get_jwt_identity())
        
        reservation = Reservation.query.filter_by(pnr=pnr).first()
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.user_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role != 'ADMIN':
                return jsonify({'error': 'Unauthorized'}), 403
        
        if not reservation.payment:
            return jsonify({'error': 'No payment record for this reservation'}), 404
        
        return jsonify(reservation.payment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
