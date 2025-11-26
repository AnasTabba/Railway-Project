"""
Seed data script for Railway Management System
Run with: python seed_data.py
"""
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from models import (
    Station, Train, TrainSchedule, CoachClass, Coach, Seat, 
    Fare, Service, User
)

def seed_database():
    """Populate database with seed data"""
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
            name='John Doe',
            email='john@example.com',
            phone='9876543210',
            role='USER'
        )
        user1.set_password('user123')
        db.session.add(user1)
        
        user2 = User(
            name='Jane Smith',
            email='jane@example.com',
            phone='9765432109',
            role='USER'
        )
        user2.set_password('user123')
        db.session.add(user2)
        
        # 3. Create Coach Classes
        print("Creating coach classes...")
        classes = [
            CoachClass(name='AC', description='Air Conditioned', capacity_per_coach=72),
            CoachClass(name='SLEEPER', description='Sleeper Coach', capacity_per_coach=72),
            CoachClass(name='BUSINESS', description='Business Class', capacity_per_coach=48),
            CoachClass(name='ECONOMY', description='Economy Class', capacity_per_coach=108),
        ]
        for cls in classes:
            db.session.add(cls)
        db.session.flush()
        
        # 4. Create 10 Stations (Pakistan)
        print("Creating stations (Pakistan)...")
        # (name, code, city, province)
        stations_data = [
            ('Karachi', 'KHI', 'Karachi', 'Sindh'),
            ('Lahore', 'LHE', 'Lahore', 'Punjab'),
            ('Islamabad', 'ISB', 'Islamabad', 'Islamabad Capital Territory'),
            ('Rawalpindi', 'RWP', 'Rawalpindi', 'Punjab'),
            ('Faisalabad', 'FSD', 'Faisalabad', 'Punjab'),
            ('Multan', 'MUX', 'Multan', 'Punjab'),
            ('Peshawar', 'PEW', 'Peshawar', 'Khyber Pakhtunkhwa'),
            ('Quetta', 'QTA', 'Quetta', 'Balochistan'),
            ('Sialkot', 'SKT', 'Sialkot', 'Punjab'),
            ('Sukkur', 'SUK', 'Sukkur', 'Sindh'),
        ]
        
        stations = {}
        for name, code, city, province in stations_data:
            station = Station(
                name=name,
                code=code,
                city=city,
                province=province,
                country='Pakistan',
                platform_count=4
            )
            db.session.add(station)
            stations[code] = station
        db.session.flush()
        
        # 5. Create 6 Trains (Pakistan)
        print("Creating trains (Pakistan)...")
        trains_data = [
            ('PK001', 'Karakoram Express', 'Pakistan Railways', 'KHI', 'LHE'),
            ('PK002', 'Green Line', 'Pakistan Railways', 'ISB', 'KHI'),
            ('PK003', 'Shalimar Express', 'Pakistan Railways', 'LHE', 'FSD'),
            ('PK004', 'Balochistan Express', 'Pakistan Railways', 'KHI', 'QTA'),
            ('PK005', 'Khyber Mail', 'Pakistan Railways', 'PEW', 'ISB'),
            ('PK006', 'Multan Express', 'Pakistan Railways', 'MUX', 'LHE'),
        ]
        
        trains = []
        for train_number, name, operator, source_code, dest_code in trains_data:
            train = Train(
                train_number=train_number,
                name=name,
                operator=operator,
                source_station_id=stations[source_code].station_id,
                destination_station_id=stations[dest_code].station_id,
                active=True
            )
            db.session.add(train)
            trains.append(train)
        db.session.flush()
        
        # 6. Create Train Schedules
        print("Creating train schedules...")
        base_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        for idx, train in enumerate(trains):
            source_schedule = TrainSchedule(
                train_id=train.train_id,
                station_id=train.source_station_id,
                departure_time=base_time + timedelta(days=idx),
                arrival_time=None,
                stop_order=1,
                platform_number='1'
            )
            db.session.add(source_schedule)
            
            dest_schedule = TrainSchedule(
                train_id=train.train_id,
                station_id=train.destination_station_id,
                arrival_time=base_time + timedelta(days=idx, hours=8),
                departure_time=None,
                stop_order=2,
                platform_number='2'
            )
            db.session.add(dest_schedule)
        
        # 7. Create Coaches
        print("Creating coaches...")
        coach_idx = 1
        for train in trains:
            for cls in classes:
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
        for coach in coaches:
            for seat_num in range(1, coach.capacity + 1):
                berth_type = None
                if coach.coach_class.name == 'SLEEPER':
                    berth_type = ['UPPER', 'LOWER', 'SIDE'][seat_num % 3]
                
                seat = Seat(
                    coach_id=coach.coach_id,
                    seat_number=str(seat_num),
                    berth_type=berth_type
                )
                db.session.add(seat)
        
        # 9. Create Fares
        print("Creating fares...")
        today = date.today()
        for cls in classes:
            if cls.name == 'AC':
                price = 2500.00
            elif cls.name == 'SLEEPER':
                price = 1500.00
            elif cls.name == 'BUSINESS':
                price = 3500.00
            else:  # ECONOMY
                price = 800.00
            
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
            ('Meal Service', 'Complimentary meals and beverages', 'AC'),
            ('Wi-Fi', 'High-speed Wi-Fi connectivity', 'AC'),
            ('Pillow & Bedding', 'Comfortable bedding', 'SLEEPER'),
            ('Power Socket', 'USB charging points', 'BUSINESS'),
            ('Reading Light', 'Individual reading lights', 'SLEEPER'),
        ]
        
        for service_name, description, class_name in services_data:
            cls = CoachClass.query.filter_by(name=class_name).first()
            if cls:
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
        
        print("\n✅ Database seeded successfully with Pakistani data!")
        print(f"✓ Created 1 admin user and 2 test users")
        print(f"✓ Created 4 coach classes")
        print(f"✓ Created 10 stations")
        print(f"✓ Created 6 trains with schedules")
        print(f"✓ Created coaches and seats")
        print(f"✓ Created fares and services")
        print("\nTest Credentials:")
        print("Admin: admin@railway.pk / admin123")
        print("User: john@example.com / user123")

if __name__ == '__main__':
    seed_database()
