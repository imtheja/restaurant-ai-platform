#!/usr/bin/env python3
"""
Pure Python database sync - no pg_dump dependency
Uses psycopg2 directly to copy data from local to production
"""

import os
import sys
import json
from pathlib import Path

# Add the shared module to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "shared"))

import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db(url, description):
    """Connect to database and return connection"""
    try:
        conn = psycopg2.connect(url)
        print(f"✅ Connected to {description}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to {description}: {e}")
        sys.exit(1)

def copy_table_data(local_conn, prod_conn, table_name, columns, conflict_column=None):
    """Copy data from local to production table"""
    
    print(f"🔄 Syncing {table_name}...")
    
    try:
        # Get data from local
        with local_conn.cursor(cursor_factory=RealDictCursor) as local_cursor:
            local_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
            rows = local_cursor.fetchall()
        
        if not rows:
            print(f"⚠️  No data found in local {table_name}")
            return True
        
        # Clear production table first (simple approach)
        with prod_conn.cursor() as prod_cursor:
            prod_cursor.execute(f"DELETE FROM {table_name}")
            
            # Insert data into production
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                # Convert dict values to list in column order
                values = []
                for col in columns:
                    value = row[col]
                    # Handle JSON columns - ensure they're properly formatted
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    values.append(value)
                
                prod_cursor.execute(insert_sql, values)
            
            prod_conn.commit()
        
        print(f"✅ Synced {len(rows)} records in {table_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to sync {table_name}: {e}")
        prod_conn.rollback()
        return False

def main():
    """Main sync function"""
    
    print("🔄 SYNC TO PRODUCTION: Local → Production")
    print("=" * 60)
    print("Syncing your local development data to production database")
    
    # Database URLs
    local_url = "postgresql://restaurant_user:secure_password_123@localhost:5432/restaurant_ai_db"
    prod_url = os.getenv("DATABASE_URL")
    
    if not prod_url:
        print("❌ DATABASE_URL not set!")
        sys.exit(1)
    
    print(f"🔗 Local: {local_url[:50]}...")
    print(f"🌐 Production: {prod_url[:50]}...")
    
    # Connect to both databases
    local_conn = connect_db(local_url, "local database")
    prod_conn = connect_db(prod_url, "production database")
    
    try:
        # Sync tables in dependency order
        success = True
        
        # 1. Restaurants (no dependencies)
        if success:
            success = copy_table_data(
                local_conn, prod_conn, 
                "restaurants",
                ["id", "name", "slug", "cuisine_type", "description", "avatar_config", "contact_info", "settings", "is_active", "created_at", "updated_at"]
            )
        
        # 2. Menu Categories (depends on restaurants)
        if success:
            success = copy_table_data(
                local_conn, prod_conn,
                "menu_categories", 
                ["id", "restaurant_id", "name", "description", "display_order", "is_active", "created_at", "updated_at"]
            )
        
        # 3. Ingredients (no dependencies)
        if success:
            success = copy_table_data(
                local_conn, prod_conn,
                "ingredients",
                ["id", "name", "category", "allergen_info", "nutritional_info", "is_active", "created_at"]
            )
        
        # 4. Menu Items (depends on categories)
        if success:
            success = copy_table_data(
                local_conn, prod_conn,
                "menu_items",
                ["id", "restaurant_id", "category_id", "name", "description", "price", "image_url", "is_available", "is_signature", "spice_level", "preparation_time", "nutritional_info", "allergen_info", "tags", "display_order", "created_at", "updated_at"]
            )
        
        # 5. Menu Item Ingredients (depends on menu items and ingredients)
        if success:
            success = copy_table_data(
                local_conn, prod_conn,
                "menu_item_ingredients",
                ["menu_item_id", "ingredient_id", "quantity", "unit"]
            )
        
        if success:
            print("\n🎉 ALL DATA SYNCED SUCCESSFULLY!")
            
            # Verify counts
            print("\n🔍 Verification:")
            tables = ["restaurants", "menu_categories", "ingredients", "menu_items", "menu_item_ingredients"]
            
            for table in tables:
                try:
                    with local_conn.cursor() as local_cursor:
                        local_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        local_count = local_cursor.fetchone()[0]
                    
                    with prod_conn.cursor() as prod_cursor:
                        prod_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        prod_count = prod_cursor.fetchone()[0]
                    
                    if local_count == prod_count:
                        print(f"✅ {table}: {local_count} records (MATCH)")
                    else:
                        print(f"❌ {table}: Local={local_count}, Prod={prod_count} (MISMATCH)")
                        
                except Exception as e:
                    print(f"⚠️  {table}: Verification failed - {e}")
        
        else:
            print("\n❌ SYNC FAILED - Some tables could not be synced")
    
    finally:
        local_conn.close()
        prod_conn.close()
    
    print("\n🌐 Production database updated!")
    print("\n🎯 Quick verification:")
    print("  python scripts/run_query.py \"SELECT name FROM restaurants\"")
    print("  python scripts/run_query.py \"SELECT COUNT(*) FROM menu_items\"")

if __name__ == "__main__":
    main()