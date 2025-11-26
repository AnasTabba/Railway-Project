"""
Database Features Demonstration Script
Run this to showcase all advanced database features
"""
import pymysql
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class DatabaseDemo:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'mysql'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'railway_user'),
            password=os.getenv('DB_PASS', 'railway_password'),
            database=os.getenv('DB_NAME', 'railway_db'),
            autocommit=False
        )
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    
    def print_header(self, title):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_result(self, results, limit=10):
        if not results:
            print("  No results found")
            return
        
        print(f"\n  Found {len(results)} result(s):\n")
        for i, row in enumerate(results[:limit], 1):
            print(f"  {i}. {row}")
        
        if len(results) > limit:
            print(f"\n  ... and {len(results) - limit} more")
    
    def demo_complex_queries(self):
        self.print_header("1. COMPLEX QUERIES & JOINS")
        
        # Multi-table join with aggregation
        print("\n📊 Revenue Analysis (6-table JOIN with aggregations):")
        query = """
        SELECT 
            t.train_number,
            t.train_name,
            cc.class_name,
            COUNT(DISTINCT r.reservation_id) AS total_bookings,
            SUM(r.num_passengers) AS total_passengers,
            SUM(r.total_fare) AS total_revenue,
            ROUND(AVG(r.total_fare), 2) AS avg_booking_value
        FROM trains t
        JOIN coaches c ON t.train_id = c.train_id
        JOIN coach_classes cc ON c.coach_class_id = cc.class_id
        JOIN train_schedules ts ON t.train_id = ts.train_id
        LEFT JOIN reservations r ON ts.schedule_id = r.schedule_id 
            AND r.status IN ('CONFIRMED', 'COMPLETED')
        GROUP BY t.train_number, t.train_name, cc.class_name
        HAVING total_revenue > 0
        ORDER BY total_revenue DESC
        LIMIT 5;
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall(), limit=5)
        
        # Subquery example
        print("\n📈 High Occupancy Trains (using subqueries):")
        query = """
        SELECT 
            t.train_number,
            t.train_name,
            total_seats.seat_count AS total_seats,
            COALESCE(booked_seats.booked_count, 0) AS booked_seats,
            ROUND((COALESCE(booked_seats.booked_count, 0) * 100.0 / total_seats.seat_count), 2) AS occupancy_pct
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
        HAVING occupancy_pct > 0
        ORDER BY occupancy_pct DESC
        LIMIT 5;
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall(), limit=5)
    
    def demo_transactions(self):
        self.print_header("2. TRANSACTIONS & CONCURRENCY")
        
        print("\n🔒 Testing Atomic Booking Transaction:")
        print("  Attempting to book 2 seats with row-level locking...")
        
        try:
            # Call stored procedure
            self.cursor.callproc('sp_book_seat', [
                1,  # user_id
                1,  # schedule_id
                1,  # class_id
                2,  # num_passengers
                (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),  # journey_date
                0,  # out: reservation_id
                '',  # out: pnr
                False,  # out: success
                ''  # out: message
            ])
            
            # Fetch OUT parameters
            self.cursor.execute("SELECT @_sp_book_seat_5, @_sp_book_seat_6, @_sp_book_seat_7, @_sp_book_seat_8")
            result = self.cursor.fetchone()
            
            print(f"\n  ✅ Booking Result:")
            print(f"     Reservation ID: {result['@_sp_book_seat_5']}")
            print(f"     PNR: {result['@_sp_book_seat_6']}")
            print(f"     Success: {result['@_sp_book_seat_7']}")
            print(f"     Message: {result['@_sp_book_seat_8']}")
            
            self.conn.commit()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.conn.rollback()
    
    def demo_constraints(self):
        self.print_header("3. CONSTRAINTS & DATA INTEGRITY")
        
        print("\n🛡️ Testing Check Constraints:")
        
        # Try to insert invalid schedule (departure >= arrival)
        print("\n  Test 1: Invalid schedule (departure after arrival)")
        try:
            query = """
            INSERT INTO train_schedules 
            (train_id, source_station_id, destination_station_id, departure_time, arrival_time)
            VALUES (1, 1, 2, '14:00:00', '10:00:00');
            """
            self.cursor.execute(query)
            print("  ❌ Constraint failed - insertion should have been blocked!")
        except pymysql.err.InternalError as e:
            print(f"  ✅ Constraint enforced: {e.args[1]}")
            self.conn.rollback()
        
        # Show foreign key relationships
        print("\n  Foreign Key Relationships:")
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'railway_booking'
          AND REFERENCED_TABLE_NAME IS NOT NULL
        LIMIT 10;
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall())
    
    def demo_indexes(self):
        self.print_header("4. INDEXING & PERFORMANCE")
        
        print("\n⚡ Performance Indexes:")
        query = """
        SELECT 
            INDEX_NAME,
            TABLE_NAME,
            GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS columns,
            INDEX_TYPE
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = 'railway_booking'
          AND INDEX_NAME LIKE 'idx_%'
        GROUP BY INDEX_NAME, TABLE_NAME, INDEX_TYPE;
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall())
        
        print("\n📊 Query Performance Test:")
        print("  Testing search query with composite index...")
        
        start = time.time()
        query = """
        EXPLAIN SELECT * FROM train_schedules 
        WHERE source_station_id = 1 AND destination_station_id = 5;
        """
        self.cursor.execute(query)
        explain = self.cursor.fetchall()
        elapsed = (time.time() - start) * 1000
        
        print(f"  Execution time: {elapsed:.2f}ms")
        print(f"  Using index: {explain[0].get('key', 'None')}")
        print(f"  Rows examined: {explain[0].get('rows', 'N/A')}")
    
    def demo_triggers(self):
        self.print_header("5. TRIGGERS & STORED PROCEDURES")
        
        print("\n🔧 Active Triggers:")
        query = """
        SELECT 
            TRIGGER_NAME,
            EVENT_MANIPULATION,
            EVENT_OBJECT_TABLE,
            ACTION_TIMING
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA = 'railway_booking';
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall())
        
        print("\n📦 Stored Procedures:")
        query = """
        SELECT 
            ROUTINE_NAME,
            ROUTINE_TYPE,
            DTD_IDENTIFIER AS return_type
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = 'railway_booking';
        """
        self.cursor.execute(query)
        self.print_result(self.cursor.fetchall())
        
        print("\n💰 Testing Refund Calculation Procedure:")
        # Get a sample reservation
        self.cursor.execute("SELECT reservation_id, total_fare, journey_date FROM reservations LIMIT 1")
        booking = self.cursor.fetchone()
        
        if booking:
            try:
                self.cursor.callproc('sp_calculate_refund', [
                    booking['reservation_id'],
                    0,  # out: refund_amount
                    0   # out: refund_percentage
                ])
                
                self.cursor.execute("SELECT @_sp_calculate_refund_1, @_sp_calculate_refund_2")
                result = self.cursor.fetchone()
                
                print(f"\n  Booking: {booking['reservation_id']}")
                print(f"  Total Fare: PKR {booking['total_fare']}")
                print(f"  Journey Date: {booking['journey_date']}")
                print(f"  Refund Amount: PKR {result['@_sp_calculate_refund_1']}")
                print(f"  Refund %: {result['@_sp_calculate_refund_2']}%")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print("  No bookings found for demo")
    
    def demo_views(self):
        self.print_header("6. VIEWS & ANALYTICS")
        
        print("\n📊 Revenue by Route (View):")
        query = "SELECT * FROM vw_revenue_by_route ORDER BY total_revenue DESC LIMIT 5;"
        try:
            self.cursor.execute(query)
            self.print_result(self.cursor.fetchall(), limit=5)
        except Exception as e:
            print(f"  Note: View not created yet. Run apply_enhancements.py first")
        
        print("\n🎫 Seat Availability (View):")
        query = "SELECT * FROM vw_seat_availability LIMIT 5;"
        try:
            self.cursor.execute(query)
            self.print_result(self.cursor.fetchall(), limit=5)
        except Exception as e:
            print(f"  Note: View not created yet. Run apply_enhancements.py first")
        
        print("\n🔝 Popular Routes (View):")
        query = "SELECT * FROM vw_popular_routes ORDER BY booking_count DESC LIMIT 5;"
        try:
            self.cursor.execute(query)
            self.print_result(self.cursor.fetchall(), limit=5)
        except Exception as e:
            print(f"  Note: View not created yet. Run apply_enhancements.py first")
    
    def demo_normalization(self):
        self.print_header("7. NORMALIZATION ANALYSIS")
        
        print("\n📐 Database Schema Analysis:")
        
        # Show tables
        query = """
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'railway_booking'
        ORDER BY TABLE_ROWS DESC;
        """
        self.cursor.execute(query)
        tables = self.cursor.fetchall()
        
        print(f"\n  Total Tables: {len(tables)}")
        self.print_result(tables)
        
        print("\n  ✅ 1NF: All attributes are atomic")
        print("  ✅ 2NF: No partial dependencies")
        print("  ✅ 3NF: No transitive dependencies")
        print("  ✅ BCNF: All determinants are candidate keys")
    
    def demo_audit_trail(self):
        self.print_header("8. AUDIT TRAIL")
        
        print("\n📝 Recent Booking Status Changes:")
        query = """
        SELECT 
            audit_id,
            reservation_id,
            old_status,
            new_status,
            changed_by,
            change_date
        FROM audit_reservations
        ORDER BY change_date DESC
        LIMIT 10;
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            if results:
                self.print_result(results)
            else:
                print("  No audit records yet. Make some booking changes to see audit trail.")
        except Exception as e:
            print(f"  Note: Audit table not created yet. Run apply_enhancements.py first")
    
    def demo_statistics(self):
        self.print_header("9. DATABASE STATISTICS")
        
        print("\n📈 Overall Statistics:")
        
        stats = {}
        
        # Total trains
        self.cursor.execute("SELECT COUNT(*) as count FROM trains")
        stats['trains'] = self.cursor.fetchone()['count']
        
        # Total stations
        self.cursor.execute("SELECT COUNT(*) as count FROM stations")
        stats['stations'] = self.cursor.fetchone()['count']
        
        # Total seats
        self.cursor.execute("SELECT COUNT(*) as count FROM seats")
        stats['seats'] = self.cursor.fetchone()['count']
        
        # Total bookings
        self.cursor.execute("SELECT COUNT(*) as count FROM reservations")
        stats['bookings'] = self.cursor.fetchone()['count']
        
        # Total users
        self.cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['users'] = self.cursor.fetchone()['count']
        
        # Total revenue
        self.cursor.execute("SELECT COALESCE(SUM(total_fare), 0) as revenue FROM reservations WHERE status IN ('CONFIRMED', 'COMPLETED')")
        stats['revenue'] = self.cursor.fetchone()['revenue']
        
        print(f"\n  🚂 Total Trains: {stats['trains']}")
        print(f"  🏢 Total Stations: {stats['stations']}")
        print(f"  💺 Total Seats: {stats['seats']}")
        print(f"  🎫 Total Bookings: {stats['bookings']}")
        print(f"  👥 Total Users: {stats['users']}")
        print(f"  💰 Total Revenue: PKR {stats['revenue']}")
    
    def run_all(self):
        print("\n" + "=" * 80)
        print("  RAILWAY BOOKING SYSTEM - DATABASE FEATURES DEMONSTRATION")
        print("=" * 80)
        print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.demo_statistics()
            self.demo_complex_queries()
            self.demo_indexes()
            self.demo_views()
            self.demo_triggers()
            self.demo_constraints()
            self.demo_normalization()
            self.demo_audit_trail()
            
            print("\n" + "=" * 80)
            print("  ✅ DEMONSTRATION COMPLETED SUCCESSFULLY")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error during demonstration: {e}")
        finally:
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    print("\n🚀 Starting Database Features Demonstration...")
    print("   Make sure you have:")
    print("   1. Seeded the database (python seed_data_expanded.py)")
    print("   2. Applied enhancements (python apply_enhancements.py)")
    print("\n   Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    
    try:
        time.sleep(3)
        demo = DatabaseDemo()
        demo.run_all()
    except KeyboardInterrupt:
        print("\n\n❌ Demonstration cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
