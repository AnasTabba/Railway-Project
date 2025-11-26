from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Train, TrainSchedule, Station, Seat, Coach, Fare, Reservation, CoachClass
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_

search_bp = Blueprint('search', __name__, url_prefix='/api')

@search_bp.route('/search', methods=['GET'])
def search_trains():
    """
    Search trains between two stations on a given date
    Query params: source (station code), destination (station code), date (YYYY-MM-DD)
    """
    try:
        source_code = request.args.get('source')
        destination_code = request.args.get('destination')
        journey_date_str = request.args.get('date')
        
        if not all([source_code, destination_code, journey_date_str]):
            return jsonify({'error': 'source, destination, and date are required'}), 400
        
        journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
        if journey_date < date.today():
            return jsonify({'error': 'Journey date cannot be in the past'}), 400
        
        source_station = Station.query.filter_by(code=source_code).first()
        dest_station = Station.query.filter_by(code=destination_code).first()
        
        if not source_station or not dest_station:
            return jsonify({'error': 'Invalid station code'}), 404
        
        # Find trains that go from source to destination
        trains = Train.query.filter_by(
            source_station_id=source_station.station_id,
            destination_station_id=dest_station.station_id,
            active=True
        ).all()
        
        results = []
        for train in trains:
            source_schedule = TrainSchedule.query.filter_by(
                train_id=train.train_id,
                station_id=source_station.station_id
            ).first()
            
            dest_schedule = TrainSchedule.query.filter_by(
                train_id=train.train_id,
                station_id=dest_station.station_id
            ).first()
            
            if not source_schedule or not dest_schedule:
                continue
            
            # Calculate duration
            if source_schedule.departure_time and dest_schedule.arrival_time:
                duration = dest_schedule.arrival_time - source_schedule.departure_time
                duration_hours = duration.total_seconds() / 3600
            else:
                duration_hours = 0
            
            # Get available seats per class
            available_seats = {}
            fares = {}
            coaches = Coach.query.filter_by(train_id=train.train_id).all()
            
            for coach in coaches:
                class_name = coach.coach_class.name
                if class_name not in available_seats:
                    available_seats[class_name] = 0
                    fares[class_name] = None
                
                # Count available (unreserved) seats
                reserved_count = Reservation.query.filter(
                    Reservation.coach_id == coach.coach_id,
                    Reservation.journey_date == journey_date,
                    Reservation.status.in_(['BOOKED', 'HOLD'])
                ).count()
                
                available_seats[class_name] += coach.capacity - reserved_count
                
                # Get fare for this class
                if not fares[class_name]:
                    fare = Fare.query.filter(
                        Fare.class_id == coach.class_id,
                        Fare.start_date <= journey_date,
                        Fare.end_date >= journey_date
                    ).first()
                    if fare:
                        fares[class_name] = float(fare.price)
            
            # Check if any seats available
            total_available = sum(available_seats.values())
            
            # Build classes array with ids for frontend mapping
            classes_detail = []
            for coach in coaches:
                class_name = coach.coach_class.name
                fare_price = fares.get(class_name)
                classes_detail.append({
                    'class_id': coach.class_id,
                    'class_name': class_name,
                    'capacity': coach.capacity,
                    'seats_available': available_seats.get(class_name, 0),
                    'fare': fare_price
                })

            results.append({
                'train': train.to_dict(),
                'source_station': source_station.to_dict(),
                'destination_station': dest_station.to_dict(),
                'departure_time': source_schedule.departure_time.isoformat() if source_schedule.departure_time else None,
                'arrival_time': dest_schedule.arrival_time.isoformat() if dest_schedule.arrival_time else None,
                'departure_time_local': source_schedule.departure_time.strftime('%Y-%m-%d %H:%M') if source_schedule.departure_time else None,
                'arrival_time_local': dest_schedule.arrival_time.strftime('%Y-%m-%d %H:%M') if dest_schedule.arrival_time else None,
                'duration_hours': duration_hours,
                'available_seats': available_seats,
                'fares': fares,
                'classes': classes_detail,
                'total_seats_available': total_available
            })
        
        # Optional filters and sorting
        depart_after = request.args.get('depart_after')  # HH:MM
        depart_before = request.args.get('depart_before')  # HH:MM
        max_price = request.args.get('max_price', type=float)
        class_name_filter = request.args.get('class')  # e.g., 'ECONOMY', 'AC STANDARD'
        sort_by = request.args.get('sort_by')  # 'fare' | 'duration' | 'departure'

        def parse_time_str(tstr):
            try:
                return datetime.strptime(tstr, '%H:%M').time()
            except Exception:
                return None

        after_t = parse_time_str(depart_after) if depart_after else None
        before_t = parse_time_str(depart_before) if depart_before else None

        # Apply filters
        filtered = []
        for r in results:
            # Depart time window filter
            if after_t or before_t:
                if r['departure_time']:
                    dep_dt = datetime.fromisoformat(r['departure_time'])
                    dep_time = dep_dt.time()
                    if after_t and dep_time < after_t:
                        continue
                    if before_t and dep_time > before_t:
                        continue
                else:
                    continue

            # Class availability and max price filter
            if class_name_filter or max_price is not None:
                class_ok = False
                for cls in r.get('classes', []):
                    if class_name_filter and cls['class_name'] != class_name_filter:
                        continue
                    if max_price is not None and (cls.get('fare') is None or cls['fare'] > max_price):
                        continue
                    if cls.get('seats_available', 0) > 0:
                        class_ok = True
                        break
                if not class_ok:
                    continue

            filtered.append(r)

        # Sorting
        if sort_by == 'fare':
            # sort by lowest available fare
            def min_fare(r):
                fares = [cls['fare'] for cls in r.get('classes', []) if cls.get('seats_available', 0) > 0 and cls.get('fare') is not None]
                return min(fares) if fares else float('inf')
            filtered.sort(key=min_fare)
        elif sort_by == 'duration':
            filtered.sort(key=lambda r: r.get('duration_hours') or float('inf'))
        elif sort_by == 'departure':
            filtered.sort(key=lambda r: datetime.fromisoformat(r['departure_time']) if r.get('departure_time') else datetime.max)

        return jsonify({
            'search_params': {
                'source': source_code,
                'destination': destination_code,
                'date': journey_date_str,
                'depart_after': depart_after,
                'depart_before': depart_before,
                'max_price': max_price,
                'class': class_name_filter,
                'sort_by': sort_by
            },
            'results': filtered,
            'count': len(filtered)
        }), 200
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/trains/<int:train_id>/availability', methods=['GET'])
def get_train_availability(train_id):
    """Get seat availability for a train on a specific date"""
    try:
        journey_date_str = request.args.get('date')
        if not journey_date_str:
            return jsonify({'error': 'date parameter is required'}), 400
        
        journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
        
        train = Train.query.get(train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        
        coaches = Coach.query.filter_by(train_id=train_id).all()
        availability = {}
        
        for coach in coaches:
            class_name = coach.coach_class.name
            if class_name not in availability:
                availability[class_name] = {
                    'total_capacity': 0,
                    'booked': 0,
                    'on_hold': 0,
                    'available': 0
                }
            
            booked_count = Reservation.query.filter(
                Reservation.coach_id == coach.coach_id,
                Reservation.journey_date == journey_date,
                Reservation.status == 'BOOKED'
            ).count()
            
            hold_count = Reservation.query.filter(
                Reservation.coach_id == coach.coach_id,
                Reservation.journey_date == journey_date,
                Reservation.status == 'HOLD'
            ).count()
            
            availability[class_name]['total_capacity'] += coach.capacity
            availability[class_name]['booked'] += booked_count
            availability[class_name]['on_hold'] += hold_count
            availability[class_name]['available'] += coach.capacity - booked_count - hold_count
        
        return jsonify({
            'train_id': train_id,
            'journey_date': journey_date_str,
            'availability': availability
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
