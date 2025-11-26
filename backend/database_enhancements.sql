-- ============================================================================
-- RAILWAY BOOKING SYSTEM - DATABASE ENHANCEMENTS
-- Advanced Database Features: Triggers, Stored Procedures, Views, Indexes
-- ============================================================================

USE railway_booking;

-- ============================================================================
-- SECTION 1: INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Index on frequently searched columns for train search
CREATE INDEX IF NOT EXISTS idx_route_source_dest_date 
ON train_schedules(source_station_id, destination_station_id, departure_time);

-- Index for booking lookups by user
CREATE INDEX IF NOT EXISTS idx_reservations_user 
ON reservations(user_id, status);

-- Index for seat availability queries
CREATE INDEX IF NOT EXISTS idx_seats_status 
ON seats(status, coach_id);

-- Index for payment tracking
CREATE INDEX IF NOT EXISTS idx_payments_booking 
ON payments(booking_id, status);

-- Composite index for date-based searches
CREATE INDEX IF NOT EXISTS idx_schedules_date 
ON train_schedules(departure_time, arrival_time);

-- Index for coach lookups by train
CREATE INDEX IF NOT EXISTS idx_coaches_train 
ON coaches(train_id, coach_class_id);

-- ============================================================================
-- SECTION 2: VIEWS FOR REPORTING & ANALYTICS
-- ============================================================================

-- View: Booking History with Full Details
DROP VIEW IF EXISTS vw_booking_details;
CREATE VIEW vw_booking_details AS
SELECT 
    r.reservation_id,
    r.pnr,
    u.username,
    u.email,
    t.train_number,
    t.train_name,
    ss.name AS source_station,
    ds.name AS destination_station,
    ts.departure_time,
    ts.arrival_time,
    cc.class_name,
    r.num_passengers,
    r.total_fare,
    r.booking_date,
    r.journey_date,
    r.status,
    p.payment_status,
    p.payment_method,
    p.amount AS payment_amount
FROM reservations r
JOIN users u ON r.user_id = u.user_id
JOIN train_schedules ts ON r.schedule_id = ts.schedule_id
JOIN trains t ON ts.train_id = t.train_id
JOIN stations ss ON ts.source_station_id = ss.station_id
JOIN stations ds ON ts.destination_station_id = ds.station_id
JOIN coach_classes cc ON r.coach_class_id = cc.class_id
LEFT JOIN payments p ON r.reservation_id = p.booking_id;

-- View: Revenue Report by Route
DROP VIEW IF EXISTS vw_revenue_by_route;
CREATE VIEW vw_revenue_by_route AS
SELECT 
    CONCAT(ss.name, ' → ', ds.name) AS route,
    COUNT(r.reservation_id) AS total_bookings,
    SUM(r.num_passengers) AS total_passengers,
    SUM(r.total_fare) AS total_revenue,
    AVG(r.total_fare) AS avg_booking_value,
    t.train_name,
    cc.class_name
FROM reservations r
JOIN train_schedules ts ON r.schedule_id = ts.schedule_id
JOIN trains t ON ts.train_id = t.train_id
JOIN stations ss ON ts.source_station_id = ss.station_id
JOIN stations ds ON ts.destination_station_id = ds.station_id
JOIN coach_classes cc ON r.coach_class_id = cc.class_id
WHERE r.status IN ('CONFIRMED', 'COMPLETED')
GROUP BY route, t.train_name, cc.class_name;

-- View: Seat Availability Summary
DROP VIEW IF EXISTS vw_seat_availability;
CREATE VIEW vw_seat_availability AS
SELECT 
    t.train_number,
    t.train_name,
    c.coach_number,
    cc.class_name,
    COUNT(CASE WHEN s.status = 'AVAILABLE' THEN 1 END) AS available_seats,
    COUNT(CASE WHEN s.status = 'BOOKED' THEN 1 END) AS booked_seats,
    COUNT(CASE WHEN s.status = 'HOLD' THEN 1 END) AS hold_seats,
    COUNT(*) AS total_seats,
    ROUND((COUNT(CASE WHEN s.status = 'BOOKED' THEN 1 END) * 100.0 / COUNT(*)), 2) AS occupancy_rate
FROM trains t
JOIN coaches c ON t.train_id = c.train_id
JOIN coach_classes cc ON c.coach_class_id = cc.class_id
JOIN seats s ON c.coach_id = s.coach_id
GROUP BY t.train_number, t.train_name, c.coach_number, cc.class_name;

-- View: Popular Routes Analysis
DROP VIEW IF EXISTS vw_popular_routes;
CREATE VIEW vw_popular_routes AS
SELECT 
    ss.name AS source,
    ds.name AS destination,
    COUNT(DISTINCT r.reservation_id) AS booking_count,
    SUM(r.num_passengers) AS passenger_count,
    SUM(r.total_fare) AS total_revenue,
    COUNT(DISTINCT ts.train_id) AS trains_on_route,
    AVG(r.total_fare / r.num_passengers) AS avg_fare_per_passenger
FROM train_schedules ts
JOIN stations ss ON ts.source_station_id = ss.station_id
JOIN stations ds ON ts.destination_station_id = ds.station_id
LEFT JOIN reservations r ON ts.schedule_id = r.schedule_id AND r.status IN ('CONFIRMED', 'COMPLETED')
GROUP BY ss.name, ds.name
ORDER BY booking_count DESC;

-- View: User Booking Statistics
DROP VIEW IF EXISTS vw_user_statistics;
CREATE VIEW vw_user_statistics AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(r.reservation_id) AS total_bookings,
    SUM(r.num_passengers) AS total_passengers,
    SUM(r.total_fare) AS total_spent,
    MAX(r.booking_date) AS last_booking_date,
    COUNT(CASE WHEN r.status = 'CONFIRMED' THEN 1 END) AS confirmed_bookings,
    COUNT(CASE WHEN r.status = 'CANCELLED' THEN 1 END) AS cancelled_bookings
FROM users u
LEFT JOIN reservations r ON u.user_id = r.user_id
GROUP BY u.user_id, u.username, u.email;

-- View: Daily Revenue Report
DROP VIEW IF EXISTS vw_daily_revenue;
CREATE VIEW vw_daily_revenue AS
SELECT 
    DATE(r.booking_date) AS booking_date,
    COUNT(r.reservation_id) AS bookings_count,
    SUM(r.num_passengers) AS passengers_count,
    SUM(r.total_fare) AS total_revenue,
    AVG(r.total_fare) AS avg_booking_value,
    COUNT(DISTINCT r.user_id) AS unique_customers
FROM reservations r
WHERE r.status IN ('CONFIRMED', 'COMPLETED')
GROUP BY DATE(r.booking_date)
ORDER BY booking_date DESC;

-- ============================================================================
-- SECTION 3: STORED PROCEDURES
-- ============================================================================

-- Procedure: Calculate Refund Amount Based on Cancellation Time
DROP PROCEDURE IF EXISTS sp_calculate_refund;
DELIMITER //
CREATE PROCEDURE sp_calculate_refund(
    IN p_reservation_id INT,
    OUT p_refund_amount DECIMAL(10,2),
    OUT p_refund_percentage INT
)
BEGIN
    DECLARE v_total_fare DECIMAL(10,2);
    DECLARE v_journey_date DATE;
    DECLARE v_departure_time TIME;
    DECLARE v_hours_until_departure INT;
    DECLARE v_journey_datetime DATETIME;
    
    -- Get booking details
    SELECT r.total_fare, r.journey_date, ts.departure_time
    INTO v_total_fare, v_journey_date, v_departure_time
    FROM reservations r
    JOIN train_schedules ts ON r.schedule_id = ts.schedule_id
    WHERE r.reservation_id = p_reservation_id;
    
    -- Combine date and time
    SET v_journey_datetime = TIMESTAMP(v_journey_date, v_departure_time);
    
    -- Calculate hours until departure
    SET v_hours_until_departure = TIMESTAMPDIFF(HOUR, NOW(), v_journey_datetime);
    
    -- Apply refund policy
    IF v_hours_until_departure > 24 THEN
        -- More than 24 hours: Full refund (100%)
        SET p_refund_percentage = 100;
        SET p_refund_amount = v_total_fare;
    ELSEIF v_hours_until_departure BETWEEN 6 AND 24 THEN
        -- 6-24 hours: Partial refund (50%)
        SET p_refund_percentage = 50;
        SET p_refund_amount = v_total_fare * 0.50;
    ELSE
        -- Less than 6 hours: No refund
        SET p_refund_percentage = 0;
        SET p_refund_amount = 0;
    END IF;
END //
DELIMITER ;

-- Procedure: Get Available Seats Count for a Train/Class
DROP PROCEDURE IF EXISTS sp_get_available_seats;
DELIMITER //
CREATE PROCEDURE sp_get_available_seats(
    IN p_train_id INT,
    IN p_class_id INT,
    OUT p_available_count INT
)
BEGIN
    SELECT COUNT(*)
    INTO p_available_count
    FROM seats s
    JOIN coaches c ON s.coach_id = c.coach_id
    WHERE c.train_id = p_train_id
      AND c.coach_class_id = p_class_id
      AND s.status = 'AVAILABLE';
END //
DELIMITER ;

-- Procedure: Get Route Statistics
DROP PROCEDURE IF EXISTS sp_route_statistics;
DELIMITER //
CREATE PROCEDURE sp_route_statistics(
    IN p_source_station_id INT,
    IN p_destination_station_id INT
)
BEGIN
    SELECT 
        COUNT(DISTINCT ts.train_id) AS total_trains,
        COUNT(DISTINCT r.reservation_id) AS total_bookings,
        SUM(r.num_passengers) AS total_passengers,
        SUM(r.total_fare) AS total_revenue,
        AVG(r.total_fare) AS avg_fare,
        MIN(ts.departure_time) AS earliest_departure,
        MAX(ts.departure_time) AS latest_departure,
        AVG(TIMESTAMPDIFF(MINUTE, ts.departure_time, ts.arrival_time)) AS avg_duration_minutes
    FROM train_schedules ts
    LEFT JOIN reservations r ON ts.schedule_id = r.schedule_id 
        AND r.status IN ('CONFIRMED', 'COMPLETED')
    WHERE ts.source_station_id = p_source_station_id
      AND ts.destination_station_id = p_destination_station_id;
END //
DELIMITER ;

-- Procedure: Book Seat (Atomic Transaction)
DROP PROCEDURE IF EXISTS sp_book_seat;
DELIMITER //
CREATE PROCEDURE sp_book_seat(
    IN p_user_id INT,
    IN p_schedule_id INT,
    IN p_class_id INT,
    IN p_num_passengers INT,
    IN p_journey_date DATE,
    OUT p_reservation_id INT,
    OUT p_pnr VARCHAR(10),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_available_seats INT;
    DECLARE v_fare DECIMAL(10,2);
    DECLARE v_total_fare DECIMAL(10,2);
    DECLARE v_train_id INT;
    
    -- Start transaction
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Booking failed due to database error';
    END;
    
    START TRANSACTION;
    
    -- Get train_id for this schedule
    SELECT train_id INTO v_train_id
    FROM train_schedules
    WHERE schedule_id = p_schedule_id;
    
    -- Check available seats with row lock
    SELECT COUNT(*) INTO v_available_seats
    FROM seats s
    JOIN coaches c ON s.coach_id = c.coach_id
    WHERE c.train_id = v_train_id
      AND c.coach_class_id = p_class_id
      AND s.status = 'AVAILABLE'
    FOR UPDATE;
    
    IF v_available_seats < p_num_passengers THEN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = CONCAT('Only ', v_available_seats, ' seats available');
        SET p_reservation_id = NULL;
        SET p_pnr = NULL;
    ELSE
        -- Get fare
        SELECT fare_amount INTO v_fare
        FROM fares
        WHERE schedule_id = p_schedule_id AND coach_class_id = p_class_id
        LIMIT 1;
        
        SET v_total_fare = v_fare * p_num_passengers;
        
        -- Generate PNR
        SET p_pnr = CONCAT('PNR', LPAD(FLOOR(RAND() * 1000000), 6, '0'));
        
        -- Create reservation
        INSERT INTO reservations (
            user_id, schedule_id, coach_class_id, num_passengers,
            total_fare, booking_date, journey_date, status, pnr
        ) VALUES (
            p_user_id, p_schedule_id, p_class_id, p_num_passengers,
            v_total_fare, NOW(), p_journey_date, 'HOLD', p_pnr
        );
        
        SET p_reservation_id = LAST_INSERT_ID();
        
        -- Mark seats as HOLD (will be updated to BOOKED after payment)
        UPDATE seats s
        JOIN coaches c ON s.coach_id = c.coach_id
        SET s.status = 'HOLD'
        WHERE c.train_id = v_train_id
          AND c.coach_class_id = p_class_id
          AND s.status = 'AVAILABLE'
        LIMIT p_num_passengers;
        
        COMMIT;
        SET p_success = TRUE;
        SET p_message = 'Booking successful';
    END IF;
END //
DELIMITER ;

-- ============================================================================
-- SECTION 4: TRIGGERS
-- ============================================================================

-- Trigger: Auto-release expired HOLD bookings (after 10 minutes)
DROP EVENT IF EXISTS evt_release_expired_holds;
CREATE EVENT evt_release_expired_holds
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    -- Release seats from expired HOLD bookings
    UPDATE seats s
    JOIN coaches c ON s.coach_id = c.coach_id
    JOIN trains t ON c.train_id = t.train_id
    JOIN train_schedules ts ON t.train_id = ts.train_id
    JOIN reservations r ON ts.schedule_id = r.schedule_id
    SET s.status = 'AVAILABLE'
    WHERE r.status = 'HOLD'
      AND TIMESTAMPDIFF(MINUTE, r.booking_date, NOW()) > 10
      AND s.status = 'HOLD';
    
    -- Update reservation status to EXPIRED
    UPDATE reservations
    SET status = 'EXPIRED'
    WHERE status = 'HOLD'
      AND TIMESTAMPDIFF(MINUTE, booking_date, NOW()) > 10;
END;

-- Trigger: Update seat status after payment confirmation
DROP TRIGGER IF EXISTS trg_after_payment_confirmed;
DELIMITER //
CREATE TRIGGER trg_after_payment_confirmed
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'COMPLETED' AND OLD.payment_status != 'COMPLETED' THEN
        -- Update reservation status to CONFIRMED
        UPDATE reservations
        SET status = 'CONFIRMED'
        WHERE reservation_id = NEW.booking_id;
        
        -- Update seat status from HOLD to BOOKED
        UPDATE seats s
        JOIN coaches c ON s.coach_id = c.coach_id
        JOIN trains t ON c.train_id = t.train_id
        JOIN train_schedules ts ON t.train_id = ts.train_id
        JOIN reservations r ON ts.schedule_id = r.schedule_id
        SET s.status = 'BOOKED'
        WHERE r.reservation_id = NEW.booking_id
          AND s.status = 'HOLD';
    END IF;
END //
DELIMITER ;

-- Trigger: Release seats after cancellation
DROP TRIGGER IF EXISTS trg_after_booking_cancelled;
DELIMITER //
CREATE TRIGGER trg_after_booking_cancelled
AFTER UPDATE ON reservations
FOR EACH ROW
BEGIN
    IF NEW.status = 'CANCELLED' AND OLD.status != 'CANCELLED' THEN
        -- Release seats back to AVAILABLE
        UPDATE seats s
        JOIN coaches c ON s.coach_id = c.coach_id
        JOIN trains t ON c.train_id = t.train_id
        JOIN train_schedules ts ON t.train_id = ts.train_id
        SET s.status = 'AVAILABLE'
        WHERE ts.schedule_id = NEW.schedule_id
          AND s.status IN ('BOOKED', 'HOLD');
    END IF;
END //
DELIMITER ;

-- Trigger: Audit trail for booking changes
DROP TABLE IF EXISTS audit_reservations;
CREATE TABLE audit_reservations (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    reservation_id INT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by VARCHAR(100),
    change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(255),
    INDEX idx_audit_reservation (reservation_id),
    INDEX idx_audit_date (change_date)
);

DROP TRIGGER IF EXISTS trg_audit_reservation_update;
DELIMITER //
CREATE TRIGGER trg_audit_reservation_update
AFTER UPDATE ON reservations
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_reservations (
            reservation_id, old_status, new_status, changed_by
        ) VALUES (
            NEW.reservation_id, OLD.status, NEW.status, USER()
        );
    END IF;
END //
DELIMITER ;

-- Trigger: Validate departure time before arrival time
DROP TRIGGER IF EXISTS trg_validate_schedule_times;
DELIMITER //
CREATE TRIGGER trg_validate_schedule_times
BEFORE INSERT ON train_schedules
FOR EACH ROW
BEGIN
    IF NEW.departure_time >= NEW.arrival_time THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Departure time must be before arrival time';
    END IF;
END //
DELIMITER ;

-- Trigger: Prevent overbooking (additional safety check)
DROP TRIGGER IF EXISTS trg_prevent_overbooking;
DELIMITER //
CREATE TRIGGER trg_prevent_overbooking
BEFORE INSERT ON reservations
FOR EACH ROW
BEGIN
    DECLARE v_available_seats INT;
    DECLARE v_train_id INT;
    
    SELECT train_id INTO v_train_id
    FROM train_schedules
    WHERE schedule_id = NEW.schedule_id;
    
    SELECT COUNT(*) INTO v_available_seats
    FROM seats s
    JOIN coaches c ON s.coach_id = c.coach_id
    WHERE c.train_id = v_train_id
      AND c.coach_class_id = NEW.coach_class_id
      AND s.status = 'AVAILABLE';
    
    IF v_available_seats < NEW.num_passengers THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough seats available';
    END IF;
END //
DELIMITER ;

-- ============================================================================
-- SECTION 5: COMPLEX QUERIES FOR DEMONSTRATION
-- ============================================================================

-- Query 1: Multi-table join with aggregation - Revenue by train and class
-- This demonstrates: JOINs, GROUP BY, aggregation functions
SELECT 
    t.train_number,
    t.train_name,
    cc.class_name,
    COUNT(DISTINCT r.reservation_id) AS total_bookings,
    SUM(r.num_passengers) AS total_passengers,
    SUM(r.total_fare) AS total_revenue,
    AVG(r.total_fare) AS avg_booking_value,
    MAX(r.total_fare) AS max_booking_value,
    MIN(r.total_fare) AS min_booking_value
FROM trains t
JOIN coaches c ON t.train_id = c.train_id
JOIN coach_classes cc ON c.coach_class_id = cc.class_id
JOIN train_schedules ts ON t.train_id = ts.train_id
LEFT JOIN reservations r ON ts.schedule_id = r.schedule_id 
    AND c.coach_class_id = r.coach_class_id
    AND r.status IN ('CONFIRMED', 'COMPLETED')
GROUP BY t.train_number, t.train_name, cc.class_name
ORDER BY total_revenue DESC;

-- Query 2: Subquery for finding trains with high occupancy
-- This demonstrates: Subquery, percentage calculation, HAVING clause
SELECT 
    t.train_number,
    t.train_name,
    total_seats.seat_count,
    booked_seats.booked_count,
    ROUND((booked_seats.booked_count * 100.0 / total_seats.seat_count), 2) AS occupancy_percentage
FROM trains t
JOIN (
    SELECT c.train_id, COUNT(*) AS seat_count
    FROM coaches c
    JOIN seats s ON c.coach_id = s.coach_id
    GROUP BY c.train_id
) AS total_seats ON t.train_id = total_seats.train_id
LEFT JOIN (
    SELECT c.train_id, COUNT(*) AS booked_count
    FROM coaches c
    JOIN seats s ON c.coach_id = s.coach_id
    WHERE s.status = 'BOOKED'
    GROUP BY c.train_id
) AS booked_seats ON t.train_id = booked_seats.train_id
HAVING occupancy_percentage > 70
ORDER BY occupancy_percentage DESC;

-- Query 3: Window function for ranking popular routes
-- This demonstrates: Window functions, CTEs
WITH route_bookings AS (
    SELECT 
        CONCAT(ss.name, ' → ', ds.name) AS route,
        COUNT(r.reservation_id) AS booking_count,
        SUM(r.total_fare) AS revenue
    FROM train_schedules ts
    JOIN stations ss ON ts.source_station_id = ss.station_id
    JOIN stations ds ON ts.destination_station_id = ds.station_id
    LEFT JOIN reservations r ON ts.schedule_id = r.schedule_id
        AND r.status IN ('CONFIRMED', 'COMPLETED')
    GROUP BY route
)
SELECT 
    route,
    booking_count,
    revenue,
    RANK() OVER (ORDER BY booking_count DESC) AS popularity_rank,
    ROUND((revenue * 100.0 / SUM(revenue) OVER ()), 2) AS revenue_percentage
FROM route_bookings
ORDER BY popularity_rank;

-- ============================================================================
-- END OF DATABASE ENHANCEMENTS
-- ============================================================================
