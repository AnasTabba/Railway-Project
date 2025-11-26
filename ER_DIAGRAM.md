# 📊 Database Schema & ER Diagram

## Entity-Relationship Diagram

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ PK: user_id     │
│     username    │
│     email       │
│     password    │
│     role        │
│     created_at  │
└────────┬────────┘
         │
         │ 1:M
         │
         ▼
┌─────────────────┐         ┌──────────────────┐
│  RESERVATIONS   │    M:1  │ TRAIN_SCHEDULES  │
├─────────────────┤◄────────┤──────────────────┤
│ PK: reservation_│         │ PK: schedule_id  │
│     id          │         │ FK: train_id     │
│ FK: user_id     │         │ FK: source_stn   │
│ FK: schedule_id │         │ FK: dest_stn     │
│ FK: class_id    │         │     departure    │
│     pnr         │         │     arrival      │
│     num_pass    │         │     days         │
│     total_fare  │         └────────┬─────────┘
│     booking_date│                  │
│     journey_date│                  │ M:1
│     status      │                  │
└────────┬────────┘                  ▼
         │                  ┌─────────────────┐
         │ 1:1              │     TRAINS      │
         │                  ├─────────────────┤
         ▼                  │ PK: train_id    │
┌─────────────────┐         │     train_number│
│    PAYMENTS     │         │     train_name  │
├─────────────────┤         │     status      │
│ PK: payment_id  │         └────────┬────────┘
│ FK: booking_id  │                  │
│     amount      │                  │ 1:M
│     method      │                  │
│     status      │                  ▼
│     txn_id      │         ┌─────────────────┐
│     date        │         │    COACHES      │
└─────────────────┘         ├─────────────────┤
                            │ PK: coach_id    │
┌─────────────────┐         │ FK: train_id    │
│  COACH_CLASSES  │    1:M  │ FK: class_id    │
├─────────────────┤◄────────┤     coach_number│
│ PK: class_id    │         │     capacity    │
│     class_name  │         └────────┬────────┘
│     description │                  │
└─────────────────┘                  │ 1:M
         ▲                           │
         │                           ▼
         │ M:1              ┌─────────────────┐
┌────────┴────────┐         │      SEATS      │
│     FARES       │         ├─────────────────┤
├─────────────────┤         │ PK: seat_id     │
│ PK: fare_id     │         │ FK: coach_id    │
│ FK: schedule_id │         │     seat_number │
│ FK: class_id    │         │     status      │
│     amount      │         │     type        │
│     valid_from  │         └─────────────────┘
│     valid_to    │
└─────────────────┘
         
┌─────────────────┐
│    STATIONS     │
├─────────────────┤
│ PK: station_id  │
│     name        │
│     code        │
│     city        │
│     state       │
└─────────────────┘
         ▲
         │
         │ Referenced by
         │ source_station_id
         │ destination_station_id
         │ in TRAIN_SCHEDULES
         
┌─────────────────────┐
│  AUDIT_RESERVATIONS │
├─────────────────────┤
│ PK: audit_id        │
│ FK: reservation_id  │
│     old_status      │
│     new_status      │
│     changed_by      │
│     change_date     │
│     change_reason   │
└─────────────────────┘
```

## Relationship Cardinalities

| Relationship | Type | Description |
|-------------|------|-------------|
| User → Reservations | 1:M | One user can make multiple bookings |
| Reservation → Payment | 1:1 | Each reservation has one payment |
| Schedule → Reservations | 1:M | One schedule can have multiple bookings |
| Train → Schedules | 1:M | One train can have multiple schedules |
| Train → Coaches | 1:M | One train has multiple coaches |
| Coach → Seats | 1:M | One coach has multiple seats |
| CoachClass → Coaches | 1:M | One class applies to multiple coaches |
| CoachClass → Fares | 1:M | One class has multiple fare entries |
| Schedule → Fares | 1:M | One schedule has fares for each class |
| Station → Schedules | 1:M | Station referenced as source/destination |

## Table Definitions

### Core Entities

#### 1. users
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'ADMIN') DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

#### 2. stations
```sql
CREATE TABLE stations (
    station_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    INDEX idx_code (code),
    INDEX idx_city (city)
);
```

#### 3. trains
```sql
CREATE TABLE trains (
    train_id INT PRIMARY KEY AUTO_INCREMENT,
    train_number VARCHAR(10) UNIQUE NOT NULL,
    train_name VARCHAR(100) NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE',
    INDEX idx_train_number (train_number)
);
```

#### 4. train_schedules
```sql
CREATE TABLE train_schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    source_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    days_of_operation VARCHAR(20),
    FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
    FOREIGN KEY (source_station_id) REFERENCES stations(station_id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(station_id),
    INDEX idx_route_search (source_station_id, destination_station_id, departure_time)
);
```

#### 5. coach_classes
```sql
CREATE TABLE coach_classes (
    class_id INT PRIMARY KEY AUTO_INCREMENT,
    class_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);
```

#### 6. coaches
```sql
CREATE TABLE coaches (
    coach_id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    coach_class_id INT NOT NULL,
    coach_number VARCHAR(10) NOT NULL,
    total_seats INT NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_class_id) REFERENCES coach_classes(class_id),
    UNIQUE KEY unique_coach (train_id, coach_number),
    INDEX idx_train_class (train_id, coach_class_id)
);
```

#### 7. seats
```sql
CREATE TABLE seats (
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    coach_id INT NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    status ENUM('AVAILABLE', 'BOOKED', 'HOLD') DEFAULT 'AVAILABLE',
    seat_type ENUM('WINDOW', 'AISLE', 'MIDDLE') DEFAULT 'AISLE',
    FOREIGN KEY (coach_id) REFERENCES coaches(coach_id) ON DELETE CASCADE,
    UNIQUE KEY unique_seat (coach_id, seat_number),
    INDEX idx_seat_status (status, coach_id)
);
```

### Transaction Entities

#### 8. reservations
```sql
CREATE TABLE reservations (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    coach_class_id INT NOT NULL,
    num_passengers INT NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    journey_date DATE NOT NULL,
    status ENUM('HOLD', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'EXPIRED') DEFAULT 'HOLD',
    pnr VARCHAR(10) UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES train_schedules(schedule_id) ON DELETE RESTRICT,
    FOREIGN KEY (coach_class_id) REFERENCES coach_classes(class_id),
    INDEX idx_user_bookings (user_id, status),
    INDEX idx_journey_date (journey_date),
    INDEX idx_pnr (pnr)
);
```

#### 9. payments
```sql
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('CREDIT_CARD', 'DEBIT_CARD', 'NET_BANKING', 'UPI', 'WALLET') NOT NULL,
    payment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED') DEFAULT 'PENDING',
    transaction_id VARCHAR(100) UNIQUE,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE,
    INDEX idx_booking_payment (booking_id, payment_status)
);
```

#### 10. fares
```sql
CREATE TABLE fares (
    fare_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT NOT NULL,
    coach_class_id INT NOT NULL,
    fare_amount DECIMAL(10,2) NOT NULL,
    valid_from DATE,
    valid_to DATE,
    FOREIGN KEY (schedule_id) REFERENCES train_schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_class_id) REFERENCES coach_classes(class_id),
    UNIQUE KEY unique_schedule_class (schedule_id, coach_class_id)
);
```

### Audit Entity

#### 11. audit_reservations
```sql
CREATE TABLE audit_reservations (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    reservation_id INT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by VARCHAR(100),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(255),
    INDEX idx_audit_reservation (reservation_id),
    INDEX idx_audit_date (change_date)
);
```

## Normalization Analysis

### 1NF (First Normal Form) ✅
- All attributes contain atomic values
- No repeating groups
- Primary keys defined for all tables

### 2NF (Second Normal Form) ✅
- All non-key attributes fully dependent on primary key
- No partial dependencies

**Example:** In `reservations`, all attributes depend on `reservation_id`, not just part of it.

### 3NF (Third Normal Form) ✅
- No transitive dependencies
- Non-key attributes depend only on primary key

**Example:** 
- `train_name` stored in `trains`, not in `schedules`
- `class_name` stored in `coach_classes`, not in `fares`
- `station_name` stored in `stations`, not in `schedules`

### BCNF (Boyce-Codd Normal Form) ✅
All determinants are candidate keys

## Constraints Summary

### Primary Keys
- All tables have single-column integer primary keys with AUTO_INCREMENT

### Foreign Keys
- 15 foreign key relationships enforcing referential integrity
- CASCADE deletes for dependent data (coaches, seats)
- RESTRICT deletes for historical data (schedules with bookings)

### Unique Constraints
- `users`: username, email
- `stations`: code
- `trains`: train_number
- `coaches`: (train_id, coach_number)
- `seats`: (coach_id, seat_number)
- `reservations`: pnr
- `payments`: transaction_id

### Check Constraints (via Triggers)
- Departure time < Arrival time
- num_passengers > 0
- total_fare > 0
- Available seats >= requested passengers

### Indexes (14 total)
Performance-optimized indexes on:
- Search columns (source, destination, date)
- Foreign keys
- Status columns
- Lookup columns (PNR, email, train_number)

## Business Rules Enforced

1. **Booking Hold Timeout**: Reservations in HOLD status for >10 minutes are auto-expired
2. **Payment Confirmation**: Payment completion triggers reservation confirmation
3. **Seat Release**: Cancelled bookings automatically release seats
4. **Refund Policy**: 
   - >24 hours before departure: 100% refund
   - 6-24 hours: 50% refund
   - <6 hours: No refund
5. **Overbooking Prevention**: Row-level locks prevent double booking
6. **Audit Trail**: All status changes are logged
7. **User Roles**: USER vs ADMIN permissions
8. **Schedule Validation**: Departure must precede arrival

## Database Size Estimates

With current seed data (45 trains, 15 stations):
- **trains**: 45 rows
- **stations**: 15 rows
- **train_schedules**: ~90 rows (2 schedules per train)
- **coaches**: ~450 rows (10 coaches per train)
- **seats**: ~30,600 rows (68 seats per coach average)
- **users**: Variable (grows with registrations)
- **reservations**: Variable (grows with bookings)
- **payments**: 1:1 with reservations

**Estimated Database Size**: ~50MB with full data + indexes
