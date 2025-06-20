#!/usr/bin/env python3
"""
Run the same SQL query on both local and production databases
"""

import os
import sys
from pathlib import Path
from tabulate import tabulate

# Add the shared module to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "shared"))

from sqlalchemy import create_engine, text

def run_query_on_databases(query: str):
    """Run a query on both local and production databases"""
    
    # Database URLs
    local_url = "postgresql://restaurant_user:secure_password_123@localhost:5432/restaurant_ai_db"
    prod_url = os.getenv("DATABASE_URL")
    
    if not prod_url:
        print("❌ DATABASE_URL not set!")
        print("Set it with: export DATABASE_URL='your_render_postgres_url'")
        sys.exit(1)
    
    print(f"🔗 Running query on both databases...")
    print(f"📝 Query: {query}")
    print("=" * 80)
    
    try:
        # Local database
        print("\n🏠 LOCAL DATABASE RESULTS:")
        print("-" * 40)
        
        local_engine = create_engine(local_url)
        with local_engine.connect() as conn:
            local_result = conn.execute(text(query)).fetchall()
            
        if local_result:
            # Convert to list of dicts for better display
            local_data = [dict(row._mapping) for row in local_result]
            print(tabulate(local_data, headers="keys", tablefmt="grid"))
        else:
            print("No results found.")
        
        print(f"\n📊 Local count: {len(local_result)} records")
        
        # Production database
        print("\n🌐 PRODUCTION DATABASE RESULTS:")
        print("-" * 40)
        
        prod_engine = create_engine(prod_url)
        with prod_engine.connect() as conn:
            prod_result = conn.execute(text(query)).fetchall()
            
        if prod_result:
            # Convert to list of dicts for better display
            prod_data = [dict(row._mapping) for row in prod_result]
            print(tabulate(prod_data, headers="keys", tablefmt="grid"))
        else:
            print("No results found.")
        
        print(f"\n📊 Production count: {len(prod_result)} records")
        
        # Comparison
        print("\n" + "=" * 80)
        print("🔍 COMPARISON RESULTS")
        print("=" * 80)
        
        if len(local_result) != len(prod_result):
            print(f"⚠️  COUNT MISMATCH: Local={len(local_result)}, Production={len(prod_result)}")
        else:
            print(f"✅ COUNT MATCH: Both have {len(local_result)} records")
        
        # Check if data is identical
        if local_result and prod_result:
            local_data = [dict(row._mapping) for row in local_result]
            prod_data = [dict(row._mapping) for row in prod_result]
            
            if local_data == prod_data:
                print("✅ DATA MATCH: Results are identical")
            else:
                print("❌ DATA MISMATCH: Results differ")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("🔍 DATABASE QUERY & COMPARISON TOOL")
        print("=" * 60)
        print("Compare local development data with production")
        print("\nUsage: python scripts/run_query.py 'YOUR_SQL_QUERY'")
        print("\n📊 Quick Health Checks:")
        print("  python scripts/run_query.py 'SELECT COUNT(*) FROM restaurants'")
        print("  python scripts/run_query.py 'SELECT COUNT(*) FROM menu_items'")
        print("  python scripts/run_query.py 'SELECT name FROM restaurants'")
        print("\n🍽️  Menu Analysis:")
        print("  python scripts/run_query.py 'SELECT mc.name as category, COUNT(mi.id) as items FROM menu_categories mc LEFT JOIN menu_items mi ON mc.id = mi.category_id GROUP BY mc.name'")
        print("\n🔄 To sync local → production:")
        print("  python scripts/sync_to_prod.py")
        sys.exit(1)
    
    query = sys.argv[1]
    run_query_on_databases(query)

if __name__ == "__main__":
    main()