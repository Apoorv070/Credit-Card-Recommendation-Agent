import sqlite3
import csv
from config import DB_PATH, CSV_FILE
import os

def create_sqlite_schema():
    """Create SQLite database and tables"""
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating SQLite schema...")
    
    # Table 1: reward_rules
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reward_rules (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_name TEXT NOT NULL,
        spend_category TEXT,
        reward_rate TEXT,
        monthly_cap TEXT,
        annual_cap TEXT,
        exclusion_flag BOOLEAN,
        exclusion_details TEXT,
        milestone_condition TEXT,
        milestone_reward TEXT,
        annual_fee TEXT,
        fee_waiver_condition TEXT,
        effective_date TEXT,
        source_pdf TEXT,
        confidence_score TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ reward_rules table created")
    
    # Table 2: transfer_partners (for future use)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transfer_partners (
        partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_name TEXT,
        partner_name TEXT,
        partner_type TEXT,
        transfer_ratio REAL,
        minimum_points INTEGER,
        maximum_points INTEGER,
        effective_date TEXT,
        source_pdf TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ transfer_partners table created")
    
    # Table 3: document_metadata
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_metadata (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_name TEXT UNIQUE,
        file_name TEXT,
        file_path TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ document_metadata table created")
    
    conn.commit()
    return conn, cursor

def load_csv_to_sqlite(conn, cursor):
    """Load CSV data into reward_rules table"""
    
    print(f"\nLoading CSV from {CSV_FILE}...")
    
    # Read CSV using built-in csv module
    row_count = 0
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            for row in csv_reader:
                cursor.execute('''
                INSERT INTO reward_rules 
                (card_name, spend_category, reward_rate, monthly_cap, annual_cap, 
                 exclusion_flag, exclusion_details, milestone_condition, milestone_reward,
                 annual_fee, fee_waiver_condition, effective_date, source_pdf, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Card Name', ''),
                    row.get('Spend Category', ''),
                    row.get('Reward Rate', ''),
                    row.get('Monthly Cap', ''),
                    row.get('Annual Cap', ''),
                    row.get('Exclusion Flag', ''),
                    row.get('Exclusion Details', ''),
                    row.get('Milestone Condition', ''),
                    row.get('Milestone Reward', ''),
                    row.get('Annual Fee', ''),
                    row.get('Fee Waiver Condition', ''),
                    row.get('Effective Date', ''),
                    row.get('Source PDF & Page', ''),
                    row.get('Confidence Score', '')
                ))
                row_count += 1
        
        conn.commit()
        print(f"✓ {row_count} rows inserted into reward_rules")
    
    except FileNotFoundError:
        print(f"❌ CSV file not found at {CSV_FILE}")
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")

def verify_database():
    """Verify database contents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM reward_rules")
    count = cursor.fetchone()[0]
    print(f"\n✓ Database verified: {count} reward rules stored")
    
    cursor.execute("SELECT card_name, spend_category FROM reward_rules LIMIT 3")
    rows = cursor.fetchall()
    print("\nSample data:")
    for row in rows:
        print(f"  - {row[0]}: {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: SQLite Setup & Data Loading")
    print("=" * 60)
    
    # Create schema
    conn, cursor = create_sqlite_schema()
    
    # Load CSV
    if os.path.exists(CSV_FILE):
        load_csv_to_sqlite(conn, cursor)
    else:
        print(f"⚠ CSV file not found at {CSV_FILE}")
    
    conn.close()
    
    # Verify
    verify_database()
    
    print("\n" + "=" * 60)
    print("✓ SQLite setup complete!")
    print(f"Database location: {DB_PATH}")
    print("=" * 60)