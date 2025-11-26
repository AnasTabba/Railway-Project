"""
Expanded seed data with 40+ realistic Pakistani trains
Run this to populate the database with comprehensive train data
"""

from extensions import db
from models import (
    User, Station, Train, TrainSchedule, Coach, CoachClass,
    Seat, Fare, Service
)
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def seed_expanded_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # 1. Create Admin User
        print("Creating admin user...")
        admin = User(
            name='Admin User',
            email='admin@railway.pk',
            phone='9999999999',
            role='ADMIN'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 2. Create Test Users
        print("Creating test users...")
        user1 = User(
            name='Ahmed Khan',
            email='ahmed@example.pk',
            phone='03001234567',
            role='USER'
        )
        user1.set_password('user123')
        db.session.add(user1)
        
        user2 = User(
            name='Fatima Ali',
            email='fatima@example.pk',
            phone='03211234567',
            role='USER'
        )
        user2.set_password('user123')
        db.session.add(user2)
        
        # 3. Create Coach Classes
        print("Creating coach classes...")
        classes = [
            CoachClass(name='AC BUSINESS', description='Air Conditioned Business Class', capacity_per_coach=48),
            CoachClass(name='AC STANDARD', description='Air Conditioned Standard', capacity_per_coach=64),
            CoachClass(name='AC SLEEPER', description='Air Conditioned Sleeper', capacity_per_coach=72),
            CoachClass(name='ECONOMY', description='Economy Class', capacity_per_coach=80),
        ]
        for cls in classes:
            db.session.add(cls)
        db.session.flush()
        
        # 4. Create Stations (Major Pakistani cities + some smaller stations)
        print("Creating stations...")
        stations_data = [
            # Major cities
            ('Karachi Cantt', 'KHI', 'Karachi', 'Sindh'),
            ('Lahore Junction', 'LHE', 'Lahore', 'Punjab'),
            ('Islamabad', 'ISB', 'Islamabad', 'Islamabad Capital Territory'),
            ('Rawalpindi', 'RWP', 'Rawalpindi', 'Punjab'),
            ('Faisalabad', 'FSD', 'Faisalabad', 'Punjab'),
            ('Multan Cantt', 'MUX', 'Multan', 'Punjab'),
            ('Peshawar Cantt', 'PEW', 'Peshawar', 'Khyber Pakhtunkhwa'),
            ('Quetta', 'QTA', 'Quetta', 'Balochistan'),
            ('Hyderabad', 'HYD', 'Hyderabad', 'Sindh'),
            ('Sukkur', 'SUK', 'Sukkur', 'Sindh'),
            # Intermediate stations
            ('Rohri Junction', 'ROR', 'Sukkur', 'Sindh'),
            ('Bahawalpur', 'BWP', 'Bahawalpur', 'Punjab'),
            ('Sahiwal', 'SWL', 'Sahiwal', 'Punjab'),
            ('Gujranwala', 'GJW', 'Gujranwala', 'Punjab'),
            ('Sialkot Cantt', 'SKT', 'Sialkot', 'Punjab'),
        ]
        
        stations = {}
        for name, code, city, province in stations_data:
            station = Station(
                name=name,
                code=code,
                city=city,
                province=province,
                country='Pakistan',
                platform_count=6
            )
            db.session.add(station)
            stations[code] = station
        db.session.flush()
        
        # 5. Create 40+ Trains with realistic schedules
        print("Creating expanded train fleet...")
        
        # Format: (number, name, operator, source, dest, departure_hour, duration_hours, frequency)
        trains_data = [
            # Karachi - Lahore route (most popular)
            ('1UP', 'Tezgam Express', 'Pakistan Railways', 'KHI', 'LHE', 7, 18, 'daily'),
            ('3UP', 'Pakistan Express', 'Pakistan Railways', 'KHI', 'LHE', 10, 19, 'daily'),
            ('5UP', 'Karachi Express', 'Pakistan Railways', 'KHI', 'LHE', 14, 18, 'daily'),
            ('7UP', 'Awam Express', 'Pakistan Railways', 'KHI', 'LHE', 18, 19, 'daily'),
            ('9UP', 'Green Line Express', 'Pakistan Railways', 'KHI', 'LHE', 23, 17, 'daily'),
            
            # Lahore - Karachi route
            ('2DN', 'Tezgam Express', 'Pakistan Railways', 'LHE', 'KHI', 7, 18, 'daily'),
            ('4DN', 'Pakistan Express', 'Pakistan Railways', 'LHE', 'KHI', 11, 19, 'daily'),
            ('6DN', 'Karachi Express', 'Pakistan Railways', 'LHE', 'KHI', 15, 18, 'daily'),
            ('8DN', 'Awam Express', 'Pakistan Railways', 'LHE', 'KHI', 19, 19, 'daily'),
            
            # Karachi - Rawalpindi/Islamabad
            ('11UP', 'Khyber Mail', 'Pakistan Railways', 'KHI', 'RWP', 6, 22, 'daily'),
            ('13UP', 'Business Express', 'Pakistan Railways', 'KHI', 'ISB', 9, 20, 'daily'),
            ('15UP', 'Shalimar Express', 'Pakistan Railways', 'KHI', 'RWP', 16, 22, 'daily'),
            ('17UP', 'Karakoram Express', 'Pakistan Railways', 'KHI', 'RWP', 20, 21, 'daily'),
            
            # Rawalpindi/Islamabad - Karachi
            ('12DN', 'Khyber Mail', 'Pakistan Railways', 'RWP', 'KHI', 7, 22, 'daily'),
            ('14DN', 'Business Express', 'Pakistan Railways', 'ISB', 'KHI', 10, 20, 'daily'),
            ('16DN', 'Shalimar Express', 'Pakistan Railways', 'RWP', 'KHI', 17, 22, 'daily'),
            
            # Karachi - Peshawar
            ('21UP', 'Pak Business Express', 'Pakistan Railways', 'KHI', 'PEW', 8, 28, 'daily'),
            ('23UP', 'Khyber Express', 'Pakistan Railways', 'KHI', 'PEW', 19, 29, 'daily'),
            
            # Peshawar - Karachi
            ('22DN', 'Pak Business Express', 'Pakistan Railways', 'PEW', 'KHI', 9, 28, 'daily'),
            ('24DN', 'Khyber Express', 'Pakistan Railways', 'PEW', 'KHI', 18, 29, 'daily'),
            
            # Karachi - Quetta
            ('31UP', 'Bolan Mail', 'Pakistan Railways', 'KHI', 'QTA', 6, 16, 'daily'),
            ('33UP', 'Jaffar Express', 'Pakistan Railways', 'KHI', 'QTA', 13, 15, 'daily'),
            ('35UP', 'Chiltan Express', 'Pakistan Railways', 'KHI', 'QTA', 21, 16, 'daily'),
            
            # Quetta - Karachi
            ('32DN', 'Bolan Mail', 'Pakistan Railways', 'QTA', 'KHI', 7, 16, 'daily'),
            ('34DN', 'Jaffar Express', 'Pakistan Railways', 'QTA', 'KHI', 14, 15, 'daily'),
            
            # Lahore - Multan
            ('41UP', 'Multan Express', 'Pakistan Railways', 'LHE', 'MUX', 7, 6, 'daily'),
            ('43UP', 'Bahauddin Zakaria Express', 'Pakistan Railways', 'LHE', 'MUX', 13, 6, 'daily'),
            ('45UP', 'Pak Express', 'Pakistan Railways', 'LHE', 'MUX', 18, 6, 'daily'),
            
            # Multan - Lahore
            ('42DN', 'Multan Express', 'Pakistan Railways', 'MUX', 'LHE', 8, 6, 'daily'),
            ('44DN', 'Bahauddin Zakaria Express', 'Pakistan Railways', 'MUX', 'LHE', 14, 6, 'daily'),
            
            # Lahore - Faisalabad
            ('51UP', 'Faisalabad Express', 'Pakistan Railways', 'LHE', 'FSD', 6, 3, 'daily'),
            ('53UP', 'Chenab Express', 'Pakistan Railways', 'LHE', 'FSD', 12, 3, 'daily'),
            ('55UP', 'Business Special', 'Pakistan Railways', 'LHE', 'FSD', 17, 3, 'daily'),
            
            # Faisalabad - Lahore
            ('52DN', 'Faisalabad Express', 'Pakistan Railways', 'FSD', 'LHE', 7, 3, 'daily'),
            ('54DN', 'Chenab Express', 'Pakistan Railways', 'FSD', 'LHE', 13, 3, 'daily'),
            
            # Rawalpindi - Lahore
            ('61UP', 'Subak Raftar', 'Pakistan Railways', 'RWP', 'LHE', 6, 4, 'daily'),
            ('63UP', 'Rehman Baba Express', 'Pakistan Railways', 'RWP', 'LHE', 11, 4, 'daily'),
            ('65UP', 'Allama Iqbal Express', 'Pakistan Railways', 'RWP', 'LHE', 16, 4, 'daily'),
            
            # Lahore - Rawalpindi
            ('62DN', 'Subak Raftar', 'Pakistan Railways', 'LHE', 'RWP', 7, 4, 'daily'),
            ('64DN', 'Rehman Baba Express', 'Pakistan Railways', 'LHE', 'RWP', 12, 4, 'daily'),
            
            # Karachi - Hyderabad (short route)
            ('71UP', 'Hyderabad Express', 'Pakistan Railways', 'KHI', 'HYD', 7, 2, 'daily'),
            ('73UP', 'Shah Latif Express', 'Pakistan Railways', 'KHI', 'HYD', 14, 2, 'daily'),
            ('75UP', 'Evening Special', 'Pakistan Railways', 'KHI', 'HYD', 18, 2, 'daily'),
            
            # Hyderabad - Karachi
            ('72DN', 'Hyderabad Express', 'Pakistan Railways', 'HYD', 'KHI', 8, 2, 'daily'),
            ('74DN', 'Shah Latif Express', 'Pakistan Railways', 'HYD', 'KHI', 15, 2, 'daily'),
        ]
        
        trains = []
        for train_number, name, operator, source_code, dest_code, dept_hour, duration, frequency in trains_data:
            train = Train(
                train_number=train_number,
                name=name,
                operator=operator,
                source_station_id=stations[source_code].station_id,
                destination_station_id=stations[dest_code].station_id,
                active=True
            )
            db.session.add(train)
            trains.append((train, dept_hour, duration))
        db.session.flush()
        
        # 6. Create Train Schedules with realistic times
        print("Creating train schedules...")
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for train, dept_hour, duration in trains:
            source_schedule = TrainSchedule(
                train_id=train.train_id,
                station_id=train.source_station_id,
                departure_time=base_date.replace(hour=dept_hour),
                arrival_time=None,
                stop_order=1,
                platform_number='1'
            )
            db.session.add(source_schedule)
            
            dest_schedule = TrainSchedule(
                train_id=train.train_id,
                station_id=train.destination_station_id,
                arrival_time=base_date.replace(hour=dept_hour) + timedelta(hours=duration),
                departure_time=None,
                stop_order=2,
                platform_number='2'
            )
            db.session.add(dest_schedule)
        
        # 7. Create Coaches (2-3 per class per train)
        print("Creating coaches...")
        coach_idx = 1
        for train_tuple in trains:
            train = train_tuple[0]
            for cls in classes:
                # Business and AC Standard get 2 coaches, others get 3
                coach_count = 2 if cls.name in ['AC BUSINESS', 'AC STANDARD'] else 3
                for i in range(coach_count):
                    coach = Coach(
                        train_id=train.train_id,
                        class_id=cls.class_id,
                        coach_number=f'C{coach_idx}',
                        capacity=cls.capacity_per_coach
                    )
                    db.session.add(coach)
                    coach_idx += 1
        db.session.flush()
        
        # 8. Create Seats
        print("Creating seats...")
        coaches = Coach.query.all()
        seat_count = 0
        for coach in coaches:
            for seat_num in range(1, coach.capacity + 1):
                berth_type = None
                if 'SLEEPER' in coach.coach_class.name:
                    berth_type = ['UPPER', 'LOWER', 'SIDE'][seat_num % 3]
                
                seat = Seat(
                    coach_id=coach.coach_id,
                    seat_number=str(seat_num),
                    berth_type=berth_type
                )
                db.session.add(seat)
                seat_count += 1
        
        # 9. Create Fares (realistic Pakistani prices)
        print("Creating fares...")
        today = datetime.now().date()
        
        # Define fare structure per class
        fare_structure = {
            'AC BUSINESS': {'short': 1500, 'medium': 3500, 'long': 6000},
            'AC STANDARD': {'short': 1000, 'medium': 2500, 'long': 4500},
            'AC SLEEPER': {'short': 1200, 'medium': 3000, 'long': 5000},
            'ECONOMY': {'short': 500, 'medium': 1200, 'long': 2000},
        }
        
        for cls in classes:
            for duration_type, price in fare_structure[cls.name].items():
                fare = Fare(
                    class_id=cls.class_id,
                    price=price,
                    start_date=today,
                    end_date=today + timedelta(days=365)
                )
                db.session.add(fare)
        
        # 10. Create Services
        print("Creating services...")
        services_data = [
            ('WiFi', 'Free WiFi', ['AC BUSINESS', 'AC STANDARD']),
            ('Meals', 'Complimentary meals', ['AC BUSINESS']),
            ('Power Outlets', 'Charging ports', ['AC BUSINESS', 'AC STANDARD']),
            ('Blanket & Pillow', 'Bedding included', ['AC SLEEPER', 'AC BUSINESS']),
            ('Entertainment', 'Screens with movies', ['AC BUSINESS']),
        ]
        
        for service_name, description, applicable_classes in services_data:
            for cls in classes:
                if cls.name in applicable_classes:
                    service = Service(
                        name=service_name,
                        description=description,
                        class_id=cls.class_id,
                        valid_from=today,
                        valid_to=today + timedelta(days=365)
                    )
                    db.session.add(service)
        
        # Commit all changes
        print("Committing seed data...")
        db.session.commit()
        
        print("\n✅ Expanded database seeded successfully!")
        print(f"✓ Created 1 admin user and 2 test users")
        print(f"✓ Created 4 coach classes")
        print(f"✓ Created {len(stations_data)} stations")
        print(f"✓ Created {len(trains_data)} trains with schedules")
        print(f"✓ Created {coach_idx-1} coaches")
        print(f"✓ Created {seat_count} seats")
        print(f"✓ Created fares and services")
        print("\nTest Credentials:")
        print("Admin: admin@railway.pk / admin123")
        print("User: ahmed@example.pk / user123")
        print("\n🚆 Major routes covered:")
        print("• Karachi ↔ Lahore (5 trains each way)")
        print("• Karachi ↔ Rawalpindi/Islamabad (4 trains)")
        print("• Karachi ↔ Peshawar (2 trains each way)")
        print("• Karachi ↔ Quetta (3 trains each way)")
        print("• Lahore ↔ Multan (3 trains each way)")
        print("• Lahore ↔ Faisalabad (3 trains each way)")
        print("• Rawalpindi ↔ Lahore (3 trains each way)")
        print("• Karachi ↔ Hyderabad (3 trains each way)")

if __name__ == '__main__':
    seed_expanded_database()
