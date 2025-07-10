#!/usr/bin/env python3
"""
Import restaurant data to Render PostgreSQL database
"""
import os
import sys
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class RenderDataImporter:
    def __init__(self, data_file: str, database_url: str):
        self.data_file = data_file
        self.database_url = database_url
        self.data = None
        self.conn = None
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
    
    def connect_to_database(self) -> bool:
        """Connect to Render database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = False
            print("✅ Connected to Render database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Create tables (simplified schema for import)
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
            self.conn.rollback()
            raise
    
    def load_data(self) -> bool:
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            print(f"✅ Loaded data from {self.data_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def import_restaurant(self) -> Optional[str]:
        """Import or update restaurant"""
        try:
            restaurant_data = self.data["restaurant"]
            slug = restaurant_data["slug"]
            
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Check if restaurant exists
            cursor.execute("SELECT id FROM restaurants WHERE slug = %s", (slug,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing restaurant
                update_sql = """
                UPDATE restaurants SET 
                    name = %s,
                    cuisine_type = %s,
                    description = %s,
                    avatar_config = %s,
                    theme_config = %s,
                    contact_info = %s,
                    settings = %s,
                    is_active = %s,
                    updated_at = NOW()
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
                
        except Exception as e:
            error_msg = f"Error importing restaurant: {e}"
            print(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return None
    
    def import_ingredients(self) -> Dict[str, str]:
        """Import or update ingredients"""
        ingredient_map = {}
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        for ing_data in self.data["ingredients"]:
            try:
                name = ing_data["name"]
                
                # Check if ingredient exists
                cursor.execute("SELECT id FROM ingredients WHERE name = %s", (name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE ingredients SET 
                            category = %s,
                            allergen_info = %s,
                            nutritional_info = %s,
                            is_active = %s
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
                    
            except Exception as e:
                error_msg = f"Error importing ingredient {ing_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        cursor.close()
        print(f"✅ Processed {len(ingredient_map)} ingredients")
        return ingredient_map
    
    def import_categories(self, restaurant_id: str) -> Dict[str, str]:
        """Import or update categories"""
        category_map = {}
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        for cat_data in self.data["categories"]:
            try:
                name = cat_data["name"]
                
                # Check if category exists for this restaurant
                cursor.execute("""
                    SELECT id FROM menu_categories 
                    WHERE restaurant_id = %s AND name = %s
                """, (restaurant_id, name))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE menu_categories SET 
                            description = %s,
                            display_order = %s,
                            is_active = %s,
                            updated_at = NOW()
                        WHERE restaurant_id = %s AND name = %s
                        RETURNING id
                    """, (
                        cat_data.get("description"),
                        cat_data.get("display_order", 0),
                        cat_data.get("is_active", True),
                        restaurant_id,
                        name
                    ))
                    category_id = cursor.fetchone()["id"]
                    self.stats["categories_updated"] += 1
                else:
                    # Create new
                    cursor.execute("""
                        INSERT INTO menu_categories (id, restaurant_id, name, description, display_order, is_active)
                        VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        restaurant_id,
                        name,
                        cat_data.get("description"),
                        cat_data.get("display_order", 0),
                        cat_data.get("is_active", True)
                    ))
                    category_id = cursor.fetchone()["id"]
                    self.stats["categories_created"] += 1
                
                category_map[name] = str(category_id)
                    
            except Exception as e:
                error_msg = f"Error importing category {cat_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        cursor.close()
        print(f"✅ Processed {len(category_map)} categories")
        return category_map
    
    def import_menu_items(self, restaurant_id: str, category_map: Dict[str, str], ingredient_map: Dict[str, str]):
        """Import or update menu items"""
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        for item_data in self.data["items"]:
            try:
                name = item_data["name"]
                
                # Get category ID
                category_id = None
                if item_data.get("category_name"):
                    category_id = category_map.get(item_data["category_name"])
                
                # Check if item exists for this restaurant
                cursor.execute("""
                    SELECT id FROM menu_items 
                    WHERE restaurant_id = %s AND name = %s
                """, (restaurant_id, name))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing item
                    cursor.execute("""
                        UPDATE menu_items SET 
                            category_id = %s,
                            description = %s,
                            price = %s,
                            image_url = %s,
                            is_available = %s,
                            is_signature = %s,
                            spice_level = %s,
                            preparation_time = %s,
                            nutritional_info = %s,
                            allergen_info = %s,
                            tags = %s,
                            display_order = %s,
                            updated_at = NOW()
                        WHERE restaurant_id = %s AND name = %s
                        RETURNING id
                    """, (
                        category_id,
                        item_data.get("description"),
                        item_data.get("price"),
                        item_data.get("image_url"),
                        item_data.get("is_available", True),
                        item_data.get("is_signature", False),
                        item_data.get("spice_level", 0),
                        item_data.get("preparation_time"),
                        json.dumps(item_data.get("nutritional_info")),
                        json.dumps(item_data.get("allergen_info")),
                        json.dumps(item_data.get("tags")),
                        item_data.get("display_order", 0),
                        restaurant_id,
                        name
                    ))
                    menu_item_id = cursor.fetchone()["id"]
                    self.stats["items_updated"] += 1
                    
                    # Clear existing ingredients
                    cursor.execute("""
                        DELETE FROM menu_item_ingredients 
                        WHERE menu_item_id = %s
                    """, (menu_item_id,))
                    
                else:
                    # Create new item
                    cursor.execute("""
                        INSERT INTO menu_items (
                            id, restaurant_id, category_id, name, description, price, image_url,
                            is_available, is_signature, spice_level, preparation_time,
                            nutritional_info, allergen_info, tags, display_order
                        )
                        VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        restaurant_id,
                        category_id,
                        name,
                        item_data.get("description"),
                        item_data.get("price"),
                        item_data.get("image_url"),
                        item_data.get("is_available", True),
                        item_data.get("is_signature", False),
                        item_data.get("spice_level", 0),
                        item_data.get("preparation_time"),
                        json.dumps(item_data.get("nutritional_info")),
                        json.dumps(item_data.get("allergen_info")),
                        json.dumps(item_data.get("tags")),
                        item_data.get("display_order", 0)
                    ))
                    menu_item_id = cursor.fetchone()["id"]
                    self.stats["items_created"] += 1
                
                # Add ingredients
                for ing_data in item_data.get("ingredients", []):
                    ingredient_id = ingredient_map.get(ing_data["ingredient_name"])
                    if ingredient_id:
                        cursor.execute("""
                            INSERT INTO menu_item_ingredients (
                                menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING
                        """, (
                            menu_item_id,
                            ingredient_id,
                            ing_data.get("quantity"),
                            ing_data.get("unit"),
                            ing_data.get("is_optional", False),
                            ing_data.get("is_primary", False)
                        ))
                    
            except Exception as e:
                error_msg = f"Error importing menu item {item_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        cursor.close()
        print(f"✅ Processed menu items")
    
    def import_data(self) -> bool:
        """Main import function"""
        if not self.load_data():
            return False
        
        if not self.connect_to_database():
            return False
        
        try:
            print("\n🚀 Starting Render data import...")
            
            # Create database schema
            self.create_tables()
            
            # Import restaurant
            restaurant_id = self.import_restaurant()
            if not restaurant_id:
                return False
            
            # Import ingredients first
            ingredient_map = self.import_ingredients()
            
            # Import categories
            category_map = self.import_categories(restaurant_id)
            
            # Import menu items
            self.import_menu_items(restaurant_id, category_map, ingredient_map)
            
            # Commit all changes
            self.conn.commit()
            
            print("\n🎉 Import completed successfully!")
            self.print_stats()
            return True
            
        except Exception as e:
            print(f"❌ Critical error during import: {e}")
            self.conn.rollback()
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Import restaurant data to Render PostgreSQL")
    parser.add_argument("data_file", help="JSON file containing restaurant data")
    parser.add_argument("--database-url", help="Render database URL (or set RENDER_DATABASE_URL)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_file):
        print(f"❌ File not found: {args.data_file}")
        return
    
    database_url = args.database_url or os.getenv("RENDER_DATABASE_URL")
    if not database_url:
        print("❌ Database URL not provided!")
        print("Either use --database-url or set RENDER_DATABASE_URL environment variable")
        return
    
    importer = RenderDataImporter(args.data_file, database_url)
    success = importer.import_data()
    
    if success:
        print("\n✅ Data import to Render successful!")
    else:
        print("\n❌ Data import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()