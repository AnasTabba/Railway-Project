"""
Apply database enhancements: indexes, views, triggers, stored procedures
Run this after initial database setup
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 3307)),
    user=os.getenv('DB_USER', 'railway_user'),
    password=os.getenv('DB_PASSWORD', 'railway_pass'),
    database=os.getenv('DB_NAME', 'railway_booking'),
    autocommit=False
)

cursor = conn.cursor()

print("=" * 80)
print("APPLYING DATABASE ENHANCEMENTS")
print("=" * 80)

try:
    # Read SQL file
    with open('database_enhancements.sql', 'r') as f:
        sql_content = f.read()
    
    # Split by delimiter changes and execute
    statements = []
    current_statement = []
    delimiter = ';'
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--') or line.startswith('USE ') or line.startswith('=='):
            continue
            
        # Handle delimiter changes
        if line.upper().startswith('DELIMITER'):
            new_delimiter = line.split()[1]
            if current_statement:
                statements.append('\n'.join(current_statement))
                current_statement = []
            delimiter = new_delimiter
            continue
        
        current_statement.append(line)
        
        # Check if statement is complete
        if line.endswith(delimiter):
            stmt = '\n'.join(current_statement).rstrip(delimiter)
            if stmt.strip():
                statements.append(stmt)
            current_statement = []
    
    # Add any remaining statement
    if current_statement:
        stmt = '\n'.join(current_statement)
        if stmt.strip():
            statements.append(stmt)
    
    # Execute each statement
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            # Skip section headers
            if statement.strip().startswith('--'):
                continue
                
            cursor.execute(statement)
            conn.commit()
            success_count += 1
            
            # Print progress for major operations
            if 'CREATE INDEX' in statement:
                index_name = statement.split('CREATE INDEX')[1].split('ON')[0].strip()
                print(f"✓ Created index: {index_name}")
            elif 'CREATE VIEW' in statement:
                view_name = statement.split('CREATE VIEW')[1].split('AS')[0].strip()
                print(f"✓ Created view: {view_name}")
            elif 'CREATE PROCEDURE' in statement:
                proc_name = statement.split('CREATE PROCEDURE')[1].split('(')[0].strip()
                print(f"✓ Created procedure: {proc_name}")
            elif 'CREATE TRIGGER' in statement:
                trigger_name = statement.split('CREATE TRIGGER')[1].split('AFTER')[0].split('BEFORE')[0].strip()
                print(f"✓ Created trigger: {trigger_name}")
            elif 'CREATE EVENT' in statement:
                event_name = statement.split('CREATE EVENT')[1].split('ON')[0].strip()
                print(f"✓ Created event: {event_name}")
            elif 'CREATE TABLE' in statement and 'audit' in statement.lower():
                table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                print(f"✓ Created table: {table_name}")
                
        except Exception as e:
            error_count += 1
            print(f"✗ Error in statement {i}: {str(e)[:100]}")
            continue
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {success_count} successful, {error_count} errors")
    print("=" * 80)
    
    # Verify created objects
    print("\n📊 Verifying Database Objects...")
    
    # Count indexes
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.statistics 
        WHERE table_schema = 'railway_booking' 
        AND index_name LIKE 'idx_%'
    """)
    index_count = cursor.fetchone()[0]
    print(f"✓ Indexes created: {index_count}")
    
    # Count views
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.views 
        WHERE table_schema = 'railway_booking'
    """)
    view_count = cursor.fetchone()[0]
    print(f"✓ Views created: {view_count}")
    
    # Count stored procedures
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.routines 
        WHERE routine_schema = 'railway_booking' 
        AND routine_type = 'PROCEDURE'
    """)
    proc_count = cursor.fetchone()[0]
    print(f"✓ Stored procedures created: {proc_count}")
    
    # Count triggers
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.triggers 
        WHERE trigger_schema = 'railway_booking'
    """)
    trigger_count = cursor.fetchone()[0]
    print(f"✓ Triggers created: {trigger_count}")
    
    # Count events
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.events 
        WHERE event_schema = 'railway_booking'
    """)
    event_count = cursor.fetchone()[0]
    print(f"✓ Events created: {event_count}")
    
    print("\n✅ Database enhancements applied successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
