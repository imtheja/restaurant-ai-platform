#!/usr/bin/env python3
"""
Generic database import script with smart overwrite capabilities
"""
import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Try to import local database modules
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
    from shared.database.connection import get_db_context
    from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
    from sqlalchemy.orm import joinedload
    from sqlalchemy.exc import IntegrityError
    LOCAL_DB_AVAILABLE = True
except ImportError:
    LOCAL_DB_AVAILABLE = False

# For remote database imports
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class GenericDataImporter:
    def __init__(self, data_file: str, target: str = "local", database_url: str = None):
        self.data_file = data_file
        self.target = target  # "local" or "remote"
        self.database_url = database_url
        self.data = None
        self.conn = None  # For remote connections
        self.stats = {
            "restaurants_created": 0,
            "restaurants_updated": 0,
            "categories_created": 0,
            "categories_updated": 0,
            "items_created": 0,
            "items_updated": 0,
            "ingredients_created": 0,
            "ingredients_updated": 0,
            "errors": []
        }
    
    def load_data(self) -> bool:
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            print(f"✅ Loaded data from {self.data_file}")
            
            # Validate data structure
            if "version" in self.data and self.data["version"] == "2.0":
                # New format with multiple restaurants
                if "restaurants" in self.data:
                    print(f"📊 Found {len(self.data['restaurants'])} restaurants to import")
                elif "restaurant" in self.data:
                    print("📊 Found single restaurant to import")
                else:
                    print("❌ Invalid data format - no restaurant data found")
                    return False
            else:
                # Legacy format - assume single restaurant
                if "restaurant" not in self.data:
                    print("❌ Invalid data format - no restaurant data found")
                    return False
                print("📊 Found single restaurant to import (legacy format)")
            
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def connect_to_remote_database(self) -> bool:
        """Connect to remote database"""
        if not PSYCOPG2_AVAILABLE:
            print("❌ psycopg2 not available for remote database connections")
            return False
        
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = False
            print("✅ Connected to remote database")
            return True
        except Exception as e:
            print(f"❌ Remote database connection failed: {e}")
            return False
    
    def create_remote_tables(self):
        """Create tables if they don't exist (for remote databases)"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Create tables schema
            tables_sql = """
            -- Enable UUID extension
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            
            -- Restaurants table
            CREATE TABLE IF NOT EXISTS restaurants (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                cuisine_type VARCHAR(100),
                description TEXT,
                avatar_config JSONB,
                theme_config JSONB,
                contact_info JSONB,
                settings JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Menu categories table
            CREATE TABLE IF NOT EXISTS menu_categories (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Ingredients table
            CREATE TABLE IF NOT EXISTS ingredients (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255) UNIQUE NOT NULL,
                category VARCHAR(100),
                allergen_info JSONB,
                nutritional_info JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Menu items table
            CREATE TABLE IF NOT EXISTS menu_items (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
                category_id UUID REFERENCES menu_categories(id) ON DELETE SET NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                image_url VARCHAR(500),
                is_available BOOLEAN DEFAULT TRUE,
                is_signature BOOLEAN DEFAULT FALSE,
                spice_level INTEGER DEFAULT 0,
                preparation_time INTEGER,
                nutritional_info JSONB,
                allergen_info JSONB,
                tags JSONB,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Menu item ingredients junction table
            CREATE TABLE IF NOT EXISTS menu_item_ingredients (
                menu_item_id UUID REFERENCES menu_items(id) ON DELETE CASCADE,
                ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
                quantity VARCHAR(50),
                unit VARCHAR(20),
                is_optional BOOLEAN DEFAULT FALSE,
                is_primary BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (menu_item_id, ingredient_id)
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_restaurants_slug ON restaurants(slug);
            CREATE INDEX IF NOT EXISTS idx_menu_categories_restaurant ON menu_categories(restaurant_id);
            CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant ON menu_items(restaurant_id);
            CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category_id);
            CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
            """
            
            cursor.execute(tables_sql)
            self.conn.commit()
            print("✅ Database schema ready")
            cursor.close()
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def import_single_restaurant(self, restaurant_data: dict) -> bool:
        """Import a single restaurant's data"""
        try:
            if self.target == "local":
                return self._import_restaurant_local(restaurant_data)
            else:
                return self._import_restaurant_remote(restaurant_data)
        except Exception as e:
            print(f"❌ Error importing restaurant: {e}")
            self.stats["errors"].append(f"Restaurant import error: {e}")
            return False
    
    def _import_restaurant_local(self, restaurant_data: dict) -> bool:
        """Import restaurant data to local database"""
        if not LOCAL_DB_AVAILABLE:
            print("❌ Local database modules not available")
            return False
        
        try:
            with get_db_context() as db:
                # Import restaurant
                restaurant = self._import_restaurant_data_local(db, restaurant_data["restaurant"])
                if not restaurant:
                    return False
                
                # Import ingredients first
                ingredient_map = self._import_ingredients_local(db, restaurant_data["ingredients"])
                
                # Import categories
                category_map = self._import_categories_local(db, restaurant, restaurant_data["categories"])
                
                # Import menu items
                self._import_menu_items_local(db, restaurant, category_map, ingredient_map, restaurant_data["items"])
                
                db.commit()
                return True
                
        except Exception as e:
            print(f"❌ Local import error: {e}")
            self.stats["errors"].append(f"Local import error: {e}")
            return False
    
    def _import_restaurant_remote(self, restaurant_data: dict) -> bool:
        """Import restaurant data to remote database"""
        if not self.conn:
            return False
        
        try:
            # Import restaurant
            restaurant_id = self._import_restaurant_data_remote(restaurant_data["restaurant"])
            if not restaurant_id:
                return False
            
            # Import ingredients first
            ingredient_map = self._import_ingredients_remote(restaurant_data["ingredients"])
            
            # Import categories
            category_map = self._import_categories_remote(restaurant_id, restaurant_data["categories"])
            
            # Import menu items
            self._import_menu_items_remote(restaurant_id, category_map, ingredient_map, restaurant_data["items"])
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Remote import error: {e}")
            if self.conn:
                self.conn.rollback()
            self.stats["errors"].append(f"Remote import error: {e}")
            return False
    
    def _import_restaurant_data_local(self, db, restaurant_data: dict):
        """Import restaurant data to local database"""
        slug = restaurant_data["slug"]
        
        # Check if restaurant exists
        existing = db.query(Restaurant).filter(Restaurant.slug == slug).first()
        
        if existing:
            # Update existing restaurant
            for key, value in restaurant_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            
            print(f"🔄 Updated existing restaurant: {existing.name}")
            self.stats["restaurants_updated"] += 1
            return existing
        else:
            # Create new restaurant
            restaurant = Restaurant(**restaurant_data)
            db.add(restaurant)
            db.flush()
            
            print(f"✨ Created new restaurant: {restaurant.name}")
            self.stats["restaurants_created"] += 1
            return restaurant
    
    def _import_restaurant_data_remote(self, restaurant_data: dict) -> Optional[str]:
        """Import restaurant data to remote database"""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        slug = restaurant_data["slug"]
        
        # Check if restaurant exists
        cursor.execute("SELECT id FROM restaurants WHERE slug = %s", (slug,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing restaurant
            update_sql = """
            UPDATE restaurants SET 
                name = %s, cuisine_type = %s, description = %s,
                avatar_config = %s, theme_config = %s, contact_info = %s,
                settings = %s, is_active = %s, updated_at = NOW()
            WHERE slug = %s
            RETURNING id
            """
            cursor.execute(update_sql, (
                restaurant_data["name"],
                restaurant_data.get("cuisine_type"),
                restaurant_data.get("description"),
                json.dumps(restaurant_data.get("avatar_config")),
                json.dumps(restaurant_data.get("theme_config")),
                json.dumps(restaurant_data.get("contact_info")),
                json.dumps(restaurant_data.get("settings")),
                restaurant_data.get("is_active", True),
                slug
            ))
            restaurant_id = cursor.fetchone()["id"]
            print(f"🔄 Updated existing restaurant: {restaurant_data['name']}")
            self.stats["restaurants_updated"] += 1
        else:
            # Create new restaurant
            insert_sql = """
            INSERT INTO restaurants (id, name, slug, cuisine_type, description, avatar_config, theme_config, contact_info, settings, is_active)
            VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            cursor.execute(insert_sql, (
                restaurant_data["name"],
                slug,
                restaurant_data.get("cuisine_type"),
                restaurant_data.get("description"),
                json.dumps(restaurant_data.get("avatar_config")),
                json.dumps(restaurant_data.get("theme_config")),
                json.dumps(restaurant_data.get("contact_info")),
                json.dumps(restaurant_data.get("settings")),
                restaurant_data.get("is_active", True)
            ))
            restaurant_id = cursor.fetchone()["id"]
            print(f"✨ Created new restaurant: {restaurant_data['name']}")
            self.stats["restaurants_created"] += 1
        
        cursor.close()
        return str(restaurant_id)
    
    def _import_ingredients_local(self, db, ingredients_data: list) -> Dict[str, Ingredient]:
        """Import ingredients to local database"""
        ingredient_map = {}
        
        for ing_data in ingredients_data:
            name = ing_data["name"]
            
            # Check if ingredient exists
            existing = db.query(Ingredient).filter(Ingredient.name == name).first()
            
            if existing:
                # Update existing
                for key, value in ing_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                
                ingredient_map[name] = existing
                self.stats["ingredients_updated"] += 1
            else:
                # Create new
                ingredient = Ingredient(**ing_data)
                db.add(ingredient)
                db.flush()
                
                ingredient_map[name] = ingredient
                self.stats["ingredients_created"] += 1
        
        print(f"✅ Processed {len(ingredient_map)} ingredients")
        return ingredient_map
    
    def _import_ingredients_remote(self, ingredients_data: list) -> Dict[str, str]:
        """Import ingredients to remote database"""
        ingredient_map = {}
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        for ing_data in ingredients_data:
            name = ing_data["name"]
            
            # Check if ingredient exists
            cursor.execute("SELECT id FROM ingredients WHERE name = %s", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE ingredients SET 
                        category = %s, allergen_info = %s, nutritional_info = %s, is_active = %s
                    WHERE name = %s
                    RETURNING id
                """, (
                    ing_data.get("category"),
                    json.dumps(ing_data.get("allergen_info")),
                    json.dumps(ing_data.get("nutritional_info")),
                    ing_data.get("is_active", True),
                    name
                ))
                ingredient_id = cursor.fetchone()["id"]
                self.stats["ingredients_updated"] += 1
            else:
                # Create new
                cursor.execute("""
                    INSERT INTO ingredients (id, name, category, allergen_info, nutritional_info, is_active)
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    name,
                    ing_data.get("category"),
                    json.dumps(ing_data.get("allergen_info")),
                    json.dumps(ing_data.get("nutritional_info")),
                    ing_data.get("is_active", True)
                ))
                ingredient_id = cursor.fetchone()["id"]
                self.stats["ingredients_created"] += 1
            
            ingredient_map[name] = str(ingredient_id)
        
        cursor.close()
        print(f"✅ Processed {len(ingredient_map)} ingredients")
        return ingredient_map
    
    def import_data(self) -> bool:
        """Main import function"""
        if not self.load_data():
            return False
        
        # Connect to target database
        if self.target == "remote":
            if not self.database_url:
                print("❌ Database URL required for remote import")
                return False
            
            if not self.connect_to_remote_database():
                return False
            
            # Create schema if needed
            self.create_remote_tables()
        elif self.target == "local":
            if not LOCAL_DB_AVAILABLE:
                print("❌ Local database modules not available")
                return False
        
        print(f"\n🚀 Starting data import to {self.target} database...")
        
        try:
            # Handle different data formats
            if "version" in self.data and self.data["version"] == "2.0" and "restaurants" in self.data:
                # New format with multiple restaurants
                success_count = 0
                for restaurant_data in self.data["restaurants"]:
                    if self.import_single_restaurant(restaurant_data):
                        success_count += 1
                
                if success_count == len(self.data["restaurants"]):
                    print(f"\n🎉 All {success_count} restaurants imported successfully!")
                    self.print_stats()
                    return True
                else:
                    print(f"\n⚠️ Only {success_count}/{len(self.data['restaurants'])} restaurants imported successfully")
                    self.print_stats()
                    return False
            else:
                # Single restaurant format
                if self.import_single_restaurant(self.data):
                    print(f"\n🎉 Restaurant imported successfully!")
                    self.print_stats()
                    return True
                else:
                    print(f"\n❌ Restaurant import failed!")
                    self.print_stats()
                    return False
                    
        except Exception as e:
            print(f"❌ Critical error during import: {e}")
            self.stats["errors"].append(f"Critical error: {e}")
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    def print_stats(self):
        """Print import statistics"""
        print("\n📊 Import Statistics:")
        print(f"  Restaurants: {self.stats['restaurants_created']} created, {self.stats['restaurants_updated']} updated")
        print(f"  Categories: {self.stats['categories_created']} created, {self.stats['categories_updated']} updated")
        print(f"  Menu Items: {self.stats['items_created']} created, {self.stats['items_updated']} updated")
        print(f"  Ingredients: {self.stats['ingredients_created']} created, {self.stats['ingredients_updated']} updated")
        
        if self.stats["errors"]:
            print(f"\n⚠️  Errors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"    - {error}")

def main():
    parser = argparse.ArgumentParser(description="Generic restaurant data importer")
    parser.add_argument("data_file", help="JSON file containing restaurant data")
    parser.add_argument("--target", choices=["local", "remote"], default="local", 
                       help="Target database (local or remote)")
    parser.add_argument("--database-url", help="Database URL for remote imports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be imported")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_file):
        print(f"❌ File not found: {args.data_file}")
        return
    
    if args.target == "remote":
        database_url = args.database_url or os.getenv("DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")
        if not database_url:
            print("❌ Database URL not provided for remote import!")
            print("Use --database-url or set DATABASE_URL/RENDER_DATABASE_URL environment variable")
            return
    else:
        database_url = None
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Add dry run functionality
        return
    
    importer = GenericDataImporter(args.data_file, args.target, database_url)
    success = importer.import_data()
    
    if success:
        print(f"\n✅ Data import to {args.target} database successful!")
    else:
        print(f"\n❌ Data import to {args.target} database failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()