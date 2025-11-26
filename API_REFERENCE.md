# 📡 API Quick Reference

## Base URL
```
http://localhost:5000/api
```

## Authentication Header
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register User
```
POST /auth/register
Content-Type: application/json

Request:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "phone": "9876543210"
}

Response: 201
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "USER"
  }
}
```

### Login
```
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "john@example.com",
  "password": "secure123"
}

Response: 200
{
  "access_token": "...",
  "user": {...}
}
```

### Get Current User
```
GET /auth/me
Authorization: Bearer <token>

Response: 200
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "USER",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 🔍 Search Endpoints

### Search Trains
```
GET /search?source=DEL&destination=BOM&date=2024-12-25

Response: 200
{
  "search_params": {
    "source": "DEL",
    "destination": "BOM",
    "date": "2024-12-25"
  },
  "count": 3,
  "results": [
    {
      "train": {
        "train_id": 1,
        "train_number": "12001",
        "name": "Rajdhani Express",
        "operator": "Indian Railways"
      },
      "departure_time": "2024-12-25T06:00:00",
      "arrival_time": "2024-12-26T09:00:00",
      "duration_hours": 27.0,
      "available_seats": {
        "AC": 45,
        "SLEEPER": 60,
        "BUSINESS": 30,
        "ECONOMY": 75
      },
      "fares": {
        "AC": 2500.00,
        "SLEEPER": 1500.00,
        "BUSINESS": 3500.00,
        "ECONOMY": 800.00
      },
      "total_seats_available": 210
    }
  ]
}
```

### Get Train Availability
```
GET /trains/{train_id}/availability?date=2024-12-25

Response: 200
{
  "train_id": 1,
  "journey_date": "2024-12-25",
  "availability": {
    "AC": {
      "total_capacity": 72,
      "booked": 20,
      "on_hold": 5,
      "available": 47
    },
    "SLEEPER": {
      "total_capacity": 72,
      "booked": 15,
      "on_hold": 3,
      "available": 54
    }
  }
}
```

---

## 📍 Station Endpoints

### Get All Stations
```
GET /stations

Response: 200
[
  {
    "station_id": 1,
    "name": "Delhi",
    "code": "DEL",
    "city": "Delhi",
    "province": "Delhi",
    "country": "India",
    "platform_count": 4
  },
  ...
]
```

### Get Station by ID
```
GET /stations/{id}

Response: 200
{
  "station_id": 1,
  "name": "Delhi",
  "code": "DEL",
  ...
}
```

### Create Station (Admin Only)
```
POST /admin/stations
Authorization: Bearer <admin_token>
Content-Type: application/json

Request:
{
  "name": "Bangalore",
  "code": "BLR",
  "city": "Bangalore",
  "province": "Karnataka",
  "country": "India",
  "platform_count": 4
}

Response: 201
{
  "message": "Station created successfully",
  "station": {...}
}
```

---

## 🚂 Train Endpoints

### Get All Trains
```
GET /trains

Response: 200
[
  {
    "train_id": 1,
    "train_number": "12001",
    "name": "Rajdhani Express",
    "operator": "Indian Railways",
    "source_station": {...},
    "destination_station": {...},
    "active": true
  },
  ...
]
```

### Get Train by ID
```
GET /trains/{id}

Response: 200
{
  "train_id": 1,
  "train_number": "12001",
  "name": "Rajdhani Express",
  "schedule": [
    {
      "schedule_id": 1,
      "station": {...},
      "arrival_time": "2024-12-25T06:00:00",
      "departure_time": "2024-12-25T06:15:00",
      "stop_order": 1,
      "platform_number": "1"
    }
  ]
}
```

---

## 🎫 Booking Endpoints

### Create Reservation
```
POST /reservations
Authorization: Bearer <user_token>
Content-Type: application/json

Request:
{
  "train_id": 1,
  "journey_date": "2024-12-25",
  "class_id": 1
}

Response: 201
{
  "message": "Reservation created (HOLD for 10 minutes)",
  "reservation": {
    "pnr": "PNR4A7B2C9D",
    "train_id": 1,
    "journey_date": "2024-12-25",
    "status": "HOLD",
    "hold_expires_at": "2024-12-20T14:10:00",
    "fare_amount": 2500.00
  }
}
```

### Get User Reservations
```
GET /reservations
Authorization: Bearer <user_token>

Response: 200
{
  "count": 3,
  "reservations": [
    {
      "reservation_id": 1,
      "pnr": "PNR4A7B2C9D",
      "train": {...},
      "journey_date": "2024-12-25",
      "status": "BOOKED",
      "created_at": "2024-12-20T14:00:00"
    }
  ]
}
```

### Get Reservation by PNR
```
GET /reservations/{pnr}
Authorization: Bearer <user_token>

Response: 200
{
  "reservation": {...},
  "payment": {
    "payment_id": 1,
    "amount": 2500.00,
    "method": "CREDIT_CARD",
    "status": "PAID",
    "paid_at": "2024-12-20T14:05:00"
  }
}
```

### Cancel Reservation
```
POST /reservations/{pnr}/cancel
Authorization: Bearer <user_token>

Response: 200
{
  "message": "Reservation cancelled successfully",
  "pnr": "PNR4A7B2C9D",
  "refund": {
    "status": "FULL_REFUND",
    "amount": 2500.00
  }
}
```

---

## 💳 Payment Endpoints

### Process Payment
```
POST /payments/{reservation_id}
Authorization: Bearer <user_token>
Content-Type: application/json

Request:
{
  "method": "CREDIT_CARD"
}

Response: 200
{
  "message": "Payment processed successfully",
  "pnr": "PNR4A7B2C9D",
  "payment_id": 1,
  "amount": 2500.00,
  "status": "PAID",
  "transaction_id": "TXN123ABC456DEF"
}

OR

Response: 402
{
  "error": "Payment failed. Please try again.",
  "status": "FAILED"
}
```

---

## 🛠️ Admin Endpoints (Admin Token Required)

### Coach Classes
```
GET    /admin/coach-classes
POST   /admin/coach-classes

Request (POST):
{
  "name": "FIRST_CLASS",
  "description": "First Class Compartment",
  "capacity_per_coach": 60
}
```

### Coaches
```
GET    /admin/coaches?train_id=1
POST   /admin/coaches

Request (POST):
{
  "train_id": 1,
  "class_id": 1,
  "coach_number": "C1",
  "capacity": 72
}
```

### Seats
```
GET    /admin/seats?coach_id=1
POST   /admin/seats

Request (POST):
{
  "coach_id": 1,
  "seat_number": "A1",
  "berth_type": "UPPER"
}
```

### Fares
```
GET    /admin/fares?class_id=1
POST   /admin/fares

Request (POST):
{
  "class_id": 1,
  "price": 2500.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### All Reservations
```
GET /admin/reservations?page=1

Response: 200
{
  "total": 150,
  "pages": 8,
  "current_page": 1,
  "reservations": [...]
}
```

---

## ❌ Error Responses

### 400 - Bad Request
```json
{
  "error": "source, destination, and date are required",
  "errors": {
    "email": ["Missing data for required field."]
  }
}
```

### 401 - Unauthorized
```json
{
  "error": "Invalid email or password"
}
```

### 403 - Forbidden
```json
{
  "error": "Admin access required"
}
```

### 404 - Not Found
```json
{
  "error": "Station not found"
}
```

### 409 - Conflict
```json
{
  "error": "Email already exists"
}
```

### 500 - Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 🔑 Station Codes Reference

```
DEL  - Delhi
BOM  - Mumbai
BLR  - Bangalore
HYD  - Hyderabad
CHE  - Chennai
KOL  - Kolkata
PUN  - Pune
AMD  - Ahmedabad
JAI  - Jaipur
LKO  - Lucknow
```

---

## 🎓 Common Use Cases

### 1. Complete Booking Flow
```bash
# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"user123"}'

# 2. Search trains
curl -X GET "http://localhost:5000/api/search?source=DEL&destination=BOM&date=2024-12-25"

# 3. Create reservation
curl -X POST http://localhost:5000/api/reservations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"train_id":1,"journey_date":"2024-12-25","class_id":1}'

# 4. Process payment
curl -X POST http://localhost:5000/api/payments/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"method":"CREDIT_CARD"}'

# 5. Get confirmation
curl -X GET http://localhost:5000/api/reservations/PNR4A7B2C9D \
  -H "Authorization: Bearer <token>"
```

### 2. Admin Operations
```bash
# Create new station
curl -X POST http://localhost:5000/api/admin/stations \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Nagpur","code":"NGP","city":"Nagpur","province":"Maharashtra"}'

# Set new fare
curl -X POST http://localhost:5000/api/admin/fares \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"class_id":1,"price":2800,"start_date":"2024-01-01","end_date":"2024-12-31"}'
```

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid credentials |
| 402 | Payment Required - Payment failed |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Duplicate resource |
| 500 | Server Error - Internal error |

---

## 🧪 Test with Postman

1. Import all endpoints from `/docs/postman_collection.json`
2. Set `{{base_url}}` = `http://localhost:5000/api`
3. Set `{{token}}` from login response
4. Run requests in sequence

---

**Last Updated:** 2024
