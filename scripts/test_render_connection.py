#!/usr/bin/env python3
"""
Test connection to Render PostgreSQL database
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_render_connection():
    """Test connection to Render database"""
    
    # Render database connection string format
    # You'll need to get the full connection string from Render dashboard
    
    render_db_id = "dpg-d14booeuk2gs73anag9g-a"
    
    print("🔍 Testing Render PostgreSQL connection...")
    print(f"Database ID: {render_db_id}")
    
    # Common Render database URL format
    # postgresql://username:password@hostname:port/database
    
    print("\n📋 To get your connection string:")
    print("1. Go to Render Dashboard")
    print("2. Navigate to your PostgreSQL service")
    print("3. Click 'Connect' tab")
    print("4. Copy the 'External Database URL'")
    print("5. Set it as RENDER_DATABASE_URL environment variable")
    
    render_url = os.getenv("RENDER_DATABASE_URL")
    
    if not render_url:
        print("\n❌ RENDER_DATABASE_URL not set!")
        print("Please set it with:")
        print("export RENDER_DATABASE_URL='postgresql://username:password@hostname:port/database'")
        return False
    
    try:
        # Parse the URL
        parsed = urlparse(render_url)
        
        print(f"\n🔗 Connecting to:")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port}")
        print(f"  Database: {parsed.path[1:]}")  # Remove leading /
        print(f"  Username: {parsed.username}")
        
        # Test connection
        conn = psycopg2.connect(render_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"\n✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📊 Existing tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n📊 No tables found - database is empty")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_render_connection()
    if not success:
        sys.exit(1)