"""
Test suite for Railway Management System
Run tests with: pytest tests/ -v
"""
import pytest
import json
from datetime import datetime, date, timedelta
from app import create_app, db
from models import User, Station, Train, Coach, CoachClass, Fare, Reservation, Payment

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Create admin user"""
    admin = User(
        name='Admin',
        email='admin@test.com',
        phone='9999999999',
        role='ADMIN'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture
def user(app):
    """Create regular user"""
    user = User(
        name='John Doe',
        email='john@test.com',
        phone='9876543210',
        role='USER'
    )
    user.set_password('user123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def tokens(client, admin_user, user):
    """Generate JWT tokens for testing"""
    # Admin token
    admin_login = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    admin_token = admin_login.json['access_token']
    
    # User token
    user_login = client.post('/api/auth/login', json={
        'email': 'john@test.com',
        'password': 'user123'
    })
    user_token = user_login.json['access_token']
    
    return {'admin': admin_token, 'user': user_token}

@pytest.fixture
def test_data(app, admin_user):
    """Create test data"""
    # Stations
    station1 = Station(name='Delhi', code='DEL', city='Delhi', province='Delhi')
    station2 = Station(name='Mumbai', code='BOM', city='Mumbai', province='Maharashtra')
    db.session.add_all([station1, station2])
    db.session.flush()
    
    # Coach Classes
    coach_class = CoachClass(name='AC', description='AC', capacity_per_coach=72)
    db.session.add(coach_class)
    db.session.flush()
    
    # Train
    train = Train(
        train_number='12001',
        name='Rajdhani Express',
        operator='Indian Railways',
        source_station_id=station1.station_id,
        destination_station_id=station2.station_id,
        active=True
    )
    db.session.add(train)
    db.session.flush()
    
    # Coach
    coach = Coach(
        train_id=train.train_id,
        class_id=coach_class.class_id,
        coach_number='C1',
        capacity=72
    )
    db.session.add(coach)
    db.session.flush()
    
    # Fare
    today = date.today()
    fare = Fare(
        class_id=coach_class.class_id,
        price=2500.00,
        start_date=today,
        end_date=today + timedelta(days=365)
    )
    db.session.add(fare)
    db.session.commit()
    
    return {
        'station1': station1,
        'station2': station2,
        'coach_class': coach_class,
        'train': train,
        'coach': coach,
        'fare': fare
    }

# ============= Authentication Tests =============

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'name': 'Jane Doe',
        'email': 'jane@test.com',
        'password': 'secure123',
        'phone': '9876543210'
    })
    assert response.status_code == 201
    assert response.json['access_token']
    assert response.json['user']['email'] == 'jane@test.com'

def test_user_login(client, user):
    """Test user login"""
    response = client.post('/api/auth/login', json={
        'email': 'john@test.com',
        'password': 'user123'
    })
    assert response.status_code == 200
    assert response.json['access_token']
    assert response.json['user']['name'] == 'John Doe'

def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@test.com',
        'password': 'wrong'
    })
    assert response.status_code == 401

def test_get_current_user(client, tokens, user):
    """Test getting current user info"""
    response = client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code == 200
    assert response.json['name'] == 'John Doe'

# ============= Station Tests =============

def test_get_stations(client, test_data):
    """Test getting all stations"""
    response = client.get('/api/stations')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_create_station(client, tokens, admin_user):
    """Test admin creating station"""
    response = client.post(
        '/api/admin/stations',
        json={
            'name': 'Bangalore',
            'code': 'BLR',
            'city': 'Bangalore',
            'province': 'Karnataka',
            'platform_count': 4
        },
        headers={'Authorization': f'Bearer {tokens["admin"]}'}
    )
    assert response.status_code == 201
    assert response.json['station']['code'] == 'BLR'

def test_non_admin_cannot_create_station(client, tokens):
    """Test non-admin cannot create station"""
    response = client.post(
        '/api/admin/stations',
        json={
            'name': 'Bangalore',
            'code': 'BLR',
            'city': 'Bangalore',
            'province': 'Karnataka'
        },
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code == 403

# ============= Train Tests =============

def test_get_trains(client, test_data):
    """Test getting all trains"""
    response = client.get('/api/trains')
    assert response.status_code == 200
    assert len(response.json) >= 1
    assert response.json[0]['train_number'] == '12001'

def test_get_train_by_id(client, test_data):
    """Test getting specific train"""
    train_id = test_data['train'].train_id
    response = client.get(f'/api/trains/{train_id}')
    assert response.status_code == 200
    assert response.json['train_number'] == '12001'

# ============= Search Tests =============

def test_search_trains(client, test_data):
    """Test train search functionality"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(f'/api/search?source=DEL&destination=BOM&date={tomorrow}')
    assert response.status_code == 200
    assert response.json['count'] >= 0

def test_search_invalid_date(client):
    """Test search with past date"""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.get(f'/api/search?source=DEL&destination=BOM&date={yesterday}')
    assert response.status_code == 400

def test_search_same_source_destination(client):
    """Test search with same source and destination"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(f'/api/search?source=DEL&destination=DEL&date={tomorrow}')
    assert response.status_code == 400

# ============= Booking Tests =============

def test_create_reservation(client, tokens, user, test_data):
    """Test creating reservation"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.post(
        '/api/reservations',
        json={
            'train_id': test_data['train'].train_id,
            'journey_date': tomorrow,
            'class_id': test_data['coach_class'].class_id
        },
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code == 201
    assert response.json['reservation']['status'] == 'HOLD'
    assert response.json['reservation']['pnr']

def test_get_user_reservations(client, tokens, user, test_data):
    """Test getting user reservations"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # Create reservation
    client.post(
        '/api/reservations',
        json={
            'train_id': test_data['train'].train_id,
            'journey_date': tomorrow,
            'class_id': test_data['coach_class'].class_id
        },
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    
    # Get reservations
    response = client.get(
        '/api/reservations',
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code == 200
    assert len(response.json['reservations']) >= 1

# ============= Cancellation & Refund Tests =============

def test_cancel_reservation_full_refund(client, tokens, user, test_data):
    """Test cancellation >24 hrs before departure (full refund)"""
    # Create reservation far in future
    future_date = (date.today() + timedelta(days=3)).isoformat()
    res_response = client.post(
        '/api/reservations',
        json={
            'train_id': test_data['train'].train_id,
            'journey_date': future_date,
            'class_id': test_data['coach_class'].class_id
        },
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    pnr = res_response.json['reservation']['pnr']
    
    # Cancel reservation
    response = client.post(
        f'/api/reservations/{pnr}/cancel',
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code == 200
    assert response.json['refund']['status'] == 'FULL_REFUND'

def test_cancel_unauthorized(client, user, test_data):
    """Test unauthorized cancellation"""
    response = client.post('/api/reservations/INVALID_PNR/cancel')
    assert response.status_code == 401

# ============= Admin Tests =============

def test_admin_get_all_users(client, tokens, admin_user):
    """Test admin getting all users"""
    response = client.get(
        '/api/admin/users',
        headers={'Authorization': f'Bearer {tokens["admin"]}'}
    )
    assert response.status_code == 200

def test_admin_get_coach_classes(client, tokens, test_data):
    """Test getting coach classes"""
    response = client.get(
        '/api/admin/coach-classes',
        headers={'Authorization': f'Bearer {tokens["admin"]}'}
    )
    assert response.status_code == 200
    assert len(response.json) >= 1

# ============= Payment Tests =============

def test_process_payment(client, tokens, user, test_data):
    """Test payment processing"""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Create reservation
    res_response = client.post(
        '/api/reservations',
        json={
            'train_id': test_data['train'].train_id,
            'journey_date': tomorrow,
            'class_id': test_data['coach_class'].class_id
        },
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    reservation_id = res_response.json['reservation']['reservation_id']
    
    # Process payment
    response = client.post(
        f'/api/payments/{reservation_id}',
        json={'method': 'CREDIT_CARD'},
        headers={'Authorization': f'Bearer {tokens["user"]}'}
    )
    assert response.status_code in [200, 402]  # Either success or failure (simulated)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
