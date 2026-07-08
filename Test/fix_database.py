import sqlite3
import csv
from config import DB_PATH

def fix_database():
    """Fix the database with corrected numerical reward rates"""
    
    print("=" * 60)
    print("FIXING DATABASE WITH CORRECTED REWARD RATES")
    print("=" * 60)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Step 1: Dropping old reward_rules table...")
    cursor.execute("DROP TABLE IF EXISTS reward_rules")
    print("✓ Old table dropped")
    
    print("\nStep 2: Creating new reward_rules table...")
    cursor.execute("""
        CREATE TABLE reward_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,
            spend_category TEXT NOT NULL,
            reward_rate REAL NOT NULL,
            monthly_cap REAL,
            annual_cap REAL,
            exclusions TEXT,
            conditions TEXT,
            annual_fee TEXT,
            effective_date TEXT,
            source TEXT,
            confidence_score TEXT
        )
    """)
    print("✓ New table created")
    
    print("\nStep 3: Loading corrected data from CSV...")
    csv_file = "data/card_data_corrected.csv"
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        rows_inserted = 0
        
        for row in csv_reader:
            monthly_cap = None if row['Monthly Cap'] == 'None' else float(row['Monthly Cap'])
            annual_cap = None if row['Annual Cap'] == 'None' else float(row['Annual Cap'])
            
            cursor.execute("""
                INSERT INTO reward_rules (
                    card_name, spend_category, reward_rate, monthly_cap, annual_cap,
                    exclusions, conditions, annual_fee, effective_date, source, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Card Name'],
                row['Spend Category'],
                float(row['Reward Rate']),
                monthly_cap,
                annual_cap,
                row['Exclusion Details'],
                row['Milestone Condition'],
                row['Annual Fee'],
                row['Effective Date'],
                row['Source PDF & Page'],
                row['Confidence Score']
            ))
            rows_inserted += 1
    
    conn.commit()
    print(f"✓ Inserted {rows_inserted} rows")
    
    print("\nStep 4: Verifying data...")
    cursor.execute("SELECT card_name, spend_category, reward_rate FROM reward_rules")
    results = cursor.fetchall()
    
    print(f"\n{'Card Name':<30} {'Category':<15} {'Reward Rate':<15}")
    print("-" * 60)
    for row in results:
        print(f"{row[0]:<30} {row[1]:<15} {row[2]:<15.2f}")
    
    print(f"\n✓ Total rows in database: {len(results)}")
    
    print("\nStep 5: Testing a sample calculation...")
    cursor.execute("""
        SELECT reward_rate, monthly_cap 
        FROM reward_rules 
        WHERE card_name = 'Axis Bank Atlas Credit Card' AND spend_category = 'flights'
    """)
    result = cursor.fetchone()
    
    if result:
        reward_rate, monthly_cap = result
        spend_amount = 50000
        base_points = spend_amount * reward_rate
        
        print(f"\nTest Calculation:")
        print(f"  Card: Axis Bank Atlas Credit Card")
        print(f"  Category: flights")
        print(f"  Spend: ₹{spend_amount:,}")
        print(f"  Reward Rate: {reward_rate} points per ₹")
        print(f"  Base Points: {base_points:,.0f}")
        cap_display = f"{monthly_cap:,.0f}" if monthly_cap else "None"
        print(f"  Monthly Cap: {cap_display}")
        
        if monthly_cap and base_points > monthly_cap:
            final_points = monthly_cap
            print(f"  Final Points (capped): {final_points:,.0f}")
        else:
            final_points = base_points
            print(f"  Final Points: {final_points:,.0f}")
        
        point_value = 0.5
        rupee_value = final_points * point_value
        print(f"  Rupee Value (@ ₹{point_value}/point): ₹{rupee_value:,.2f}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE FIXED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Test the agent: python test_agent.py")
    print("2. Launch Streamlit: streamlit run streamlit_app.py")
    print()


if __name__ == "__main__":
    fix_database()
