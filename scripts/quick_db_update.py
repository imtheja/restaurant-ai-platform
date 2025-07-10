#!/usr/bin/env python3
import os
import sqlite3

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'restaurant.db')

# Read the SQL file
with open('update_to_chip_cookies.sql', 'r') as f:
    sql_content = f.read()

# Connect and execute
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute all statements
    cursor.executescript(sql_content)
    
    conn.commit()
    print("✅ Database updated successfully with Chip Cookies branding")
    
    # Verify the update
    cursor.execute("SELECT name FROM restaurants WHERE slug = 'baker-bettys'")
    result = cursor.fetchone()
    if result:
        print(f"Restaurant name is now: {result[0]}")
    
    conn.close()
except Exception as e:
    print(f"❌ Error updating database: {e}")