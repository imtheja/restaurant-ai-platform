#!/usr/bin/env python3
"""
Migrate Render database schema to match current version
"""
import os
import sys
import psycopg2

def migrate_render_schema(database_url: str):
    """Add missing columns and update schema"""
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔧 Updating Render database schema...")
        
        # Check if theme_config column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurants' AND column_name = 'theme_config'
        """)
        
        if not cursor.fetchone():
            print("➕ Adding theme_config column to restaurants table...")
            cursor.execute("""
                ALTER TABLE restaurants 
                ADD COLUMN theme_config JSONB
            """)
            conn.commit()
            print("✅ Added theme_config column")
        else:
            print("✅ theme_config column already exists")
        
        # Check current schema
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'restaurants'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 Current restaurants table schema:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Schema migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema migration failed: {e}")
        return False

def main():
    database_url = os.getenv("RENDER_DATABASE_URL")
    if not database_url:
        print("❌ RENDER_DATABASE_URL not set!")
        print("Please set it with:")
        print("export RENDER_DATABASE_URL='postgresql://username:password@hostname:port/database'")
        return
    
    success = migrate_render_schema(database_url)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()