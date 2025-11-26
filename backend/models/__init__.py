from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.Enum('USER', 'ADMIN'), default='USER', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Station(db.Model):
    __tablename__ = 'stations'
    
    station_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='India')
    platform_count = db.Column(db.Integer, default=1)
    
    # Relationships
    trains_from = db.relationship('Train', foreign_keys='Train.source_station_id', backref='source_station', lazy=True)
    trains_to = db.relationship('Train', foreign_keys='Train.destination_station_id', backref='destination_station', lazy=True)
    schedules = db.relationship('TrainSchedule', backref='station', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'station_id': self.station_id,
            'name': self.name,
            'code': self.code,
            'city': self.city,
            'province': self.province,
            'country': self.country,
            'platform_count': self.platform_count
        }


class Train(db.Model):
    __tablename__ = 'trains'
    
    train_id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    operator = db.Column(db.String(100), nullable=False)
    source_station_id = db.Column(db.Integer, db.ForeignKey('stations.station_id'), nullable=False)
    destination_station_id = db.Column(db.Integer, db.ForeignKey('stations.station_id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    schedules = db.relationship('TrainSchedule', backref='train', lazy=True, cascade='all, delete-orphan')
    coaches = db.relationship('Coach', backref='train', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='train', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_schedule=False):
        data = {
            'train_id': self.train_id,
            'train_number': self.train_number,
            'name': self.name,
            'operator': self.operator,
            'source_station': self.source_station.to_dict() if self.source_station else None,
            'destination_station': self.destination_station.to_dict() if self.destination_station else None,
            'active': self.active
        }
        if include_schedule:
            data['schedule'] = [s.to_dict() for s in self.schedules]
        return data


class TrainSchedule(db.Model):
    __tablename__ = 'train_schedule'
    
    schedule_id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.train_id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.station_id'), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=True)
    departure_time = db.Column(db.DateTime, nullable=True)
    stop_order = db.Column(db.Integer, nullable=False)
    platform_number = db.Column(db.String(10), nullable=True)
    
    __table_args__ = (
        db.Index('idx_train_schedule', 'train_id', 'station_id'),
    )
    
    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'train_id': self.train_id,
            'station': self.station.to_dict() if self.station else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'stop_order': self.stop_order,
            'platform_number': self.platform_number
        }


class CoachClass(db.Model):
    __tablename__ = 'coach_classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    capacity_per_coach = db.Column(db.Integer, nullable=False)
    
    # Relationships
    coaches = db.relationship('Coach', backref='coach_class', lazy=True, cascade='all, delete-orphan')
    fares = db.relationship('Fare', backref='coach_class', lazy=True, cascade='all, delete-orphan')
    services = db.relationship('Service', backref='coach_class', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'class_id': self.class_id,
            'name': self.name,
            'description': self.description,
            'capacity_per_coach': self.capacity_per_coach
        }


class Coach(db.Model):
    __tablename__ = 'coaches'
    
    coach_id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.train_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('coach_classes.class_id'), nullable=False)
    coach_number = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    seats = db.relationship('Seat', backref='coach', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='coach', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('train_id', 'coach_number', name='uc_train_coach'),
    )
    
    def to_dict(self):
        return {
            'coach_id': self.coach_id,
            'train_id': self.train_id,
            'class': self.coach_class.to_dict() if self.coach_class else None,
            'coach_number': self.coach_number,
            'capacity': self.capacity
        }


class Seat(db.Model):
    __tablename__ = 'seats'
    
    seat_id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.coach_id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    berth_type = db.Column(db.String(50), nullable=True)  # e.g., UPPER, LOWER, SIDE
    
    # Relationships
    reservations = db.relationship('Reservation', backref='seat', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('coach_id', 'seat_number', name='uc_coach_seat'),
    )
    
    def to_dict(self):
        return {
            'seat_id': self.seat_id,
            'coach_id': self.coach_id,
            'seat_number': self.seat_number,
            'berth_type': self.berth_type
        }


class Fare(db.Model):
    __tablename__ = 'fares'
    
    fare_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('coach_classes.class_id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    def to_dict(self):
        return {
            'fare_id': self.fare_id,
            'class_id': self.class_id,
            'class_name': self.coach_class.name if self.coach_class else None,
            'price': float(self.price),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }


class Service(db.Model):
    __tablename__ = 'services'
    
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('coach_classes.class_id'), nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'name': self.name,
            'description': self.description,
            'class_id': self.class_id,
            'class_name': self.coach_class.name if self.coach_class else None,
            'valid_from': self.valid_from.isoformat(),
            'valid_to': self.valid_to.isoformat()
        }


class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    pnr = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.train_id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.coach_id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.seat_id'), nullable=True)
    status = db.Column(db.Enum('BOOKED', 'CANCELLED', 'HOLD'), default='HOLD', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hold_expires_at = db.Column(db.DateTime, nullable=True)
    # Passenger snapshot fields (denormalized for historical accuracy)
    passenger_name = db.Column(db.String(120), nullable=True)
    passenger_age = db.Column(db.Integer, nullable=True)
    passenger_email = db.Column(db.String(120), nullable=True)
    
    # Relationships
    payment = db.relationship('Payment', backref='reservation', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_user_pnr', 'user_id', 'pnr'),
    )
    
    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'pnr': self.pnr,
            'user_id': self.user_id,
            'train': self.train.to_dict() if self.train else None,
            'journey_date': self.journey_date.isoformat(),
            'coach': self.coach.to_dict() if self.coach else None,
            'seat': self.seat.to_dict() if self.seat else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'hold_expires_at': self.hold_expires_at.isoformat() if self.hold_expires_at else None,
            'passenger_name': self.passenger_name,
            'passenger_age': self.passenger_age,
            'passenger_email': self.passenger_email
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.reservation_id'), nullable=False, unique=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50), nullable=False)  # CREDIT_CARD, DEBIT_CARD, UPI, etc.
    status = db.Column(db.Enum('PENDING', 'PAID', 'FAILED'), default='PENDING', nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    refund_status = db.Column(db.Enum('NO_REFUND', 'PARTIAL_REFUND', 'FULL_REFUND'), default='NO_REFUND')
    refund_amount = db.Column(db.Numeric(10, 2), default=0)
    refunded_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'reservation_id': self.reservation_id,
            'amount': float(self.amount),
            'method': self.method,
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'refund_status': self.refund_status,
            'refund_amount': float(self.refund_amount),
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None
        }
