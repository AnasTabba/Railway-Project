#!/usr/bin/env python3
"""
System Health Check Script
Verifies all components are working correctly
"""
import os
import sys
import requests
from datetime import datetime

def print_status(component, status, details=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {component}: {'OK' if status else 'FAILED'} {details}")

def check_backend():
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_frontend():
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_database():
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='railway_user',
            password='railway_pass',
            database='railway_booking'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trains")
        train_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM stations")
        station_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM seats")
        seat_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, train_count, station_count, seat_count
    except:
        return False, 0, 0, 0

def check_api_endpoints():
    try:
        # Check stations endpoint
        response = requests.get("http://localhost:5001/api/stations", timeout=5)
        stations_ok = response.status_code == 200
        
        # Check search endpoint
        response = requests.get(
            "http://localhost:5001/api/search",
            params={"source": "KHI", "destination": "LHE", "date": "2025-12-01"},
            timeout=5
        )
        search_ok = response.status_code == 200 and response.json().get('count', 0) > 0
        
        return stations_ok and search_ok
    except:
        return False

def check_enhancements():
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='railway_user',
            password='railway_pass',
            database='railway_booking'
        )
        cursor = conn.cursor()
        
        # Check views
        cursor.execute("SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'railway_booking'")
        view_count = cursor.fetchone()[0]
        
        # Check indexes
        cursor.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = 'railway_booking' AND index_name LIKE 'idx_%'")
        index_count = cursor.fetchone()[0]
        
        # Check triggers
        cursor.execute("SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'railway_booking'")
        trigger_count = cursor.fetchone()[0]
        
        # Check stored procedures
        cursor.execute("SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'railway_booking' AND routine_type = 'PROCEDURE'")
        proc_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return view_count, index_count, trigger_count, proc_count
    except:
        return 0, 0, 0, 0

print("=" * 80)
print("RAILWAY BOOKING SYSTEM - HEALTH CHECK")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check services
print("🔍 Checking Services...")
print_status("Backend API", check_backend(), "- http://localhost:5001/health")
print_status("Frontend", check_frontend(), "- http://localhost:5173")

db_ok, trains, stations, seats = check_database()
print_status("Database", db_ok, f"- {trains} trains, {stations} stations, {seats} seats")

# Check API functionality
print("\n🔍 Checking API Endpoints...")
print_status("API Endpoints", check_api_endpoints(), "- /api/stations, /api/search")

# Check database enhancements
print("\n🔍 Checking Advanced Database Features...")
views, indexes, triggers, procs = check_enhancements()

if views > 0 or indexes > 0 or triggers > 0 or procs > 0:
    print(f"✅ Views: {views}")
    print(f"✅ Indexes: {indexes}")
    print(f"✅ Triggers: {triggers}")
    print(f"✅ Stored Procedures: {procs}")
else:
    print("⚠️  No advanced features found - Run: docker-compose exec backend python apply_enhancements.py")

# Summary
print("\n" + "=" * 80)
all_ok = check_backend() and check_frontend() and db_ok and check_api_endpoints()
if all_ok:
    print("✅ ALL SYSTEMS OPERATIONAL")
    if views == 0:
        print("\n💡 Next step: Apply database enhancements")
        print("   Run: docker-compose exec backend python apply_enhancements.py")
else:
    print("❌ SOME SYSTEMS NEED ATTENTION")
    print("\n💡 Try restarting: docker-compose restart")
print("=" * 80)
