#!/usr/bin/env python3
"""
Generic database comparison script to verify data consistency
"""
import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Add backend path for local database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Local database imports
try:
    from shared.database.connection import get_db_context
    from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
    from sqlalchemy.orm import joinedload
    LOCAL_DB_AVAILABLE = True
except ImportError:
    LOCAL_DB_AVAILABLE = False

# Remote database imports
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class DatabaseComparator:
    def __init__(self, source_config: dict, target_config: dict, restaurant_slugs: List[str] = None):
        self.source_config = source_config
        self.target_config = target_config
        self.restaurant_slugs = restaurant_slugs or []
        self.source_data = {}
        self.target_data = {}
        self.differences = []
        
    def extract_data_from_database(self, config: dict, data_store: dict):
        """Extract data from a database (local or remote)"""
        db_type = config.get("type")
        
        if db_type == "local":
            return self._extract_local_data(data_store)
        elif db_type == "remote":
            return self._extract_remote_data(config.get("url"), data_store)
        else:
            print(f"❌ Unknown database type: {db_type}")
            return False
    
    def _extract_local_data(self, data_store: dict):
        """Extract data from local database"""
        if not LOCAL_DB_AVAILABLE:
            print("❌ Local database modules not available")
            return False
        
        try:
            with get_db_context() as db:
                # Get all restaurants if no specific slugs provided
                if not self.restaurant_slugs:
                    restaurants = db.query(Restaurant).filter(Restaurant.is_active == True).all()
                    self.restaurant_slugs = [r.slug for r in restaurants]
                
                data_store["restaurants"] = {}
                
                for slug in self.restaurant_slugs:
                    restaurant = db.query(Restaurant).filter(Restaurant.slug == slug).first()
                    if not restaurant:
                        print(f"⚠️ Restaurant '{slug}' not found in local database")
                        continue
                    
                    # Extract restaurant data
                    restaurant_data = {
                        "restaurant": {
                            "name": restaurant.name,
                            "slug": restaurant.slug,
                            "cuisine_type": restaurant.cuisine_type,
                            "description": restaurant.description,
                            "avatar_config": restaurant.avatar_config,
                            "theme_config": restaurant.theme_config,
                            "contact_info": restaurant.contact_info,
                            "settings": restaurant.settings,
                            "is_active": restaurant.is_active
                        },
                        "categories": [],
                        "items": []
                    }
                    
                    # Get categories
                    categories = db.query(MenuCategory).filter(
                        MenuCategory.restaurant_id == restaurant.id,
                        MenuCategory.is_active == True
                    ).order_by(MenuCategory.display_order, MenuCategory.name).all()
                    
                    for cat in categories:
                        restaurant_data["categories"].append({
                            "name": cat.name,
                            "description": cat.description,
                            "display_order": cat.display_order,
                            "is_active": cat.is_active
                        })
                    
                    # Get menu items with ingredients
                    items = db.query(MenuItem).options(
                        joinedload(MenuItem.ingredients).joinedload(MenuItemIngredient.ingredient)
                    ).filter(
                        MenuItem.restaurant_id == restaurant.id
                    ).order_by(MenuItem.display_order, MenuItem.name).all()
                    
                    for item in items:
                        # Find category name
                        category_name = None
                        if item.category_id:
                            category = next((c for c in categories if c.id == item.category_id), None)
                            if category:
                                category_name = category.name
                        
                        item_data = {
                            "name": item.name,
                            "description": item.description,
                            "price": float(item.price) if item.price else None,
                            "image_url": item.image_url,
                            "is_available": item.is_available,
                            "is_signature": item.is_signature,
                            "spice_level": item.spice_level,
                            "preparation_time": item.preparation_time,
                            "nutritional_info": item.nutritional_info,
                            "allergen_info": item.allergen_info,
                            "tags": item.tags,
                            "display_order": item.display_order,
                            "category_name": category_name,
                            "ingredients": []
                        }
                        
                        # Get ingredients
                        for item_ingredient in item.ingredients:
                            if item_ingredient.ingredient and item_ingredient.ingredient.is_active:
                                item_data["ingredients"].append({
                                    "ingredient_name": item_ingredient.ingredient.name,
                                    "quantity": item_ingredient.quantity,
                                    "unit": item_ingredient.unit,
                                    "is_optional": item_ingredient.is_optional,
                                    "is_primary": item_ingredient.is_primary
                                })
                        
                        # Sort ingredients by name for consistent comparison
                        item_data["ingredients"].sort(key=lambda x: x["ingredient_name"])
                        restaurant_data["items"].append(item_data)
                    
                    data_store["restaurants"][slug] = restaurant_data
                
                print(f"✅ Extracted local data for {len(data_store['restaurants'])} restaurants")
                return True
                
        except Exception as e:
            print(f"❌ Error extracting local data: {e}")
            return False
    
    def _extract_remote_data(self, database_url: str, data_store: dict):
        """Extract data from remote database"""
        if not PSYCOPG2_AVAILABLE:
            print("❌ psycopg2 not available for remote database connections")
            return False
        
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get all restaurants if no specific slugs provided
            if not self.restaurant_slugs:
                cursor.execute("SELECT slug FROM restaurants WHERE is_active = true")
                restaurants = cursor.fetchall()
                self.restaurant_slugs = [r["slug"] for r in restaurants]
            
            data_store["restaurants"] = {}
            
            for slug in self.restaurant_slugs:
                # Get restaurant
                cursor.execute("""
                    SELECT name, slug, cuisine_type, description, avatar_config, theme_config, 
                           contact_info, settings, is_active, id
                    FROM restaurants 
                    WHERE slug = %s
                """, (slug,))
                
                restaurant = cursor.fetchone()
                if not restaurant:
                    print(f"⚠️ Restaurant '{slug}' not found in remote database")
                    continue
                
                restaurant_data = {
                    "restaurant": {
                        "name": restaurant["name"],
                        "slug": restaurant["slug"],
                        "cuisine_type": restaurant["cuisine_type"],
                        "description": restaurant["description"],
                        "avatar_config": restaurant["avatar_config"],
                        "theme_config": restaurant["theme_config"],
                        "contact_info": restaurant["contact_info"],
                        "settings": restaurant["settings"],
                        "is_active": restaurant["is_active"]
                    },
                    "categories": [],
                    "items": []
                }
                
                restaurant_id = restaurant["id"]
                
                # Get categories
                cursor.execute("""
                    SELECT name, description, display_order, is_active
                    FROM menu_categories 
                    WHERE restaurant_id = %s AND is_active = true
                    ORDER BY display_order, name
                """, (restaurant_id,))
                
                restaurant_data["categories"] = [dict(row) for row in cursor.fetchall()]
                
                # Get menu items
                cursor.execute("""
                    SELECT mi.name, mi.description, mi.price, mi.image_url, mi.is_available,
                           mi.is_signature, mi.spice_level, mi.preparation_time, mi.nutritional_info,
                           mi.allergen_info, mi.tags, mi.display_order, mc.name as category_name,
                           mi.id as item_id
                    FROM menu_items mi
                    LEFT JOIN menu_categories mc ON mi.category_id = mc.id
                    WHERE mi.restaurant_id = %s
                    ORDER BY mi.display_order, mi.name
                """, (restaurant_id,))
                
                items = cursor.fetchall()
                
                for item in items:
                    item_data = dict(item)
                    item_data["price"] = float(item_data["price"]) if item_data["price"] else None
                    
                    # Get ingredients for this item
                    cursor.execute("""
                        SELECT i.name as ingredient_name, mii.quantity, mii.unit, 
                               mii.is_optional, mii.is_primary
                        FROM menu_item_ingredients mii
                        JOIN ingredients i ON mii.ingredient_id = i.id
                        WHERE mii.menu_item_id = %s AND i.is_active = true
                        ORDER BY i.name
                    """, (item["item_id"],))
                    
                    item_data["ingredients"] = [dict(row) for row in cursor.fetchall()]
                    
                    # Remove item_id as it's not needed for comparison
                    del item_data["item_id"]
                    
                    restaurant_data["items"].append(item_data)
                
                data_store["restaurants"][slug] = restaurant_data
            
            cursor.close()
            conn.close()
            
            print(f"✅ Extracted remote data for {len(data_store['restaurants'])} restaurants")
            return True
            
        except Exception as e:
            print(f"❌ Error extracting remote data: {e}")
            return False
    
    def compare_json_fields(self, field_name: str, local_val: Any, remote_val: Any) -> bool:
        """Compare JSON fields"""
        local_json = json.dumps(local_val, sort_keys=True) if local_val else None
        remote_json = json.dumps(remote_val, sort_keys=True) if remote_val else None
        return local_json == remote_json
    
    def compare_restaurants(self, slug: str) -> bool:
        """Compare restaurant data"""
        if slug not in self.source_data["restaurants"] or slug not in self.target_data["restaurants"]:
            self.differences.append(f"Restaurant '{slug}' missing in one database")
            return False
        
        source_rest = self.source_data["restaurants"][slug]["restaurant"]
        target_rest = self.target_data["restaurants"][slug]["restaurant"]
        
        print(f"\n🏪 RESTAURANT '{slug}' COMPARISON:")
        
        fields_to_compare = ["name", "slug", "cuisine_type", "description", "is_active"]
        json_fields = ["avatar_config", "theme_config", "contact_info", "settings"]
        
        restaurant_matches = True
        
        for field in fields_to_compare:
            source_val = source_rest.get(field)
            target_val = target_rest.get(field)
            
            if source_val == target_val:
                print(f"   ✅ {field}: MATCH")
            else:
                print(f"   ❌ {field}: MISMATCH")
                print(f"      Source: {source_val}")
                print(f"      Target: {target_val}")
                self.differences.append(f"Restaurant {slug} {field} mismatch")
                restaurant_matches = False
        
        for field in json_fields:
            source_val = source_rest.get(field)
            target_val = target_rest.get(field)
            
            if self.compare_json_fields(field, source_val, target_val):
                print(f"   ✅ {field}: MATCH")
            else:
                print(f"   ❌ {field}: MISMATCH")
                self.differences.append(f"Restaurant {slug} {field} JSON mismatch")
                restaurant_matches = False
        
        return restaurant_matches
    
    def compare_categories(self, slug: str) -> bool:
        """Compare categories"""
        source_cats = self.source_data["restaurants"][slug]["categories"]
        target_cats = self.target_data["restaurants"][slug]["categories"]
        
        print(f"\n📚 CATEGORIES COMPARISON for '{slug}':")
        
        categories_match = True
        
        if len(source_cats) != len(target_cats):
            print(f"   ❌ COUNT MISMATCH: Source={len(source_cats)}, Target={len(target_cats)}")
            self.differences.append(f"Restaurant {slug} category count mismatch")
            categories_match = False
        else:
            print(f"   ✅ COUNT: {len(source_cats)} categories")
        
        # Compare each category
        for i, (source_cat, target_cat) in enumerate(zip(source_cats, target_cats)):
            name = source_cat["name"]
            matches = True
            
            for field in ["name", "description", "display_order", "is_active"]:
                if source_cat.get(field) != target_cat.get(field):
                    matches = False
                    categories_match = False
                    break
            
            if matches:
                print(f"   ✅ {name}: MATCH")
            else:
                print(f"   ❌ {name}: MISMATCH")
                self.differences.append(f"Restaurant {slug} category {name} mismatch")
        
        return categories_match
    
    def compare_menu_items(self, slug: str) -> bool:
        """Compare menu items"""
        source_items = self.source_data["restaurants"][slug]["items"]
        target_items = self.target_data["restaurants"][slug]["items"]
        
        print(f"\n🍪 MENU ITEMS COMPARISON for '{slug}':")
        
        items_match = True
        
        if len(source_items) != len(target_items):
            print(f"   ❌ COUNT MISMATCH: Source={len(source_items)}, Target={len(target_items)}")
            self.differences.append(f"Restaurant {slug} menu items count mismatch")
            items_match = False
        else:
            print(f"   ✅ COUNT: {len(source_items)} menu items")
        
        # Compare each item
        for i, (source_item, target_item) in enumerate(zip(source_items, target_items)):
            name = source_item["name"]
            matches = True
            
            # Compare basic fields
            fields_to_compare = [
                "name", "description", "price", "image_url", "is_available",
                "is_signature", "spice_level", "preparation_time", "display_order",
                "category_name"
            ]
            
            for field in fields_to_compare:
                source_val = source_item.get(field)
                target_val = target_item.get(field)
                
                if source_val != target_val:
                    matches = False
                    items_match = False
                    break
            
            # Compare JSON fields
            json_fields = ["nutritional_info", "allergen_info", "tags"]
            for field in json_fields:
                source_val = source_item.get(field)
                target_val = target_item.get(field)
                
                if not self.compare_json_fields(field, source_val, target_val):
                    matches = False
                    items_match = False
                    break
            
            # Compare ingredients
            source_ingredients = source_item.get("ingredients", [])
            target_ingredients = target_item.get("ingredients", [])
            
            if len(source_ingredients) != len(target_ingredients):
                matches = False
                items_match = False
            else:
                for source_ing, target_ing in zip(source_ingredients, target_ingredients):
                    if source_ing != target_ing:
                        matches = False
                        items_match = False
                        break
            
            if matches:
                print(f"   ✅ {name}: MATCH")
            else:
                print(f"   ❌ {name}: MISMATCH")
                self.differences.append(f"Restaurant {slug} menu item {name} mismatch")
        
        return items_match
    
    def run_comparison(self) -> bool:
        """Run complete comparison"""
        print("🔍 COMPARING DATABASES")
        print("=" * 50)
        
        # Extract data from both databases
        source_name = self.source_config.get("name", "Source")
        target_name = self.target_config.get("name", "Target")
        
        print(f"📊 Extracting data from {source_name} database...")
        if not self.extract_data_from_database(self.source_config, self.source_data):
            return False
        
        print(f"📊 Extracting data from {target_name} database...")
        if not self.extract_data_from_database(self.target_config, self.target_data):
            return False
        
        # Find common restaurants
        source_slugs = set(self.source_data["restaurants"].keys())
        target_slugs = set(self.target_data["restaurants"].keys())
        common_slugs = source_slugs.intersection(target_slugs)
        
        if not common_slugs:
            print("❌ No common restaurants found in both databases")
            return False
        
        # Compare each restaurant
        all_match = True
        for slug in sorted(common_slugs):
            restaurant_matches = self.compare_restaurants(slug)
            categories_match = self.compare_categories(slug)
            items_match = self.compare_menu_items(slug)
            
            if not (restaurant_matches and categories_match and items_match):
                all_match = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 COMPARISON SUMMARY")
        
        if all_match and not self.differences:
            print("🎉 ✅ DATABASES ARE IDENTICAL!")
            print("   All data matches perfectly between databases.")
        else:
            print(f"⚠️  Found {len(self.differences)} differences:")
            for diff in self.differences:
                print(f"   - {diff}")
            
            # Show missing restaurants
            only_in_source = source_slugs - target_slugs
            only_in_target = target_slugs - source_slugs
            
            if only_in_source:
                print(f"\n📍 Restaurants only in {source_name}: {', '.join(only_in_source)}")
            
            if only_in_target:
                print(f"📍 Restaurants only in {target_name}: {', '.join(only_in_target)}")
        
        return all_match and len(self.differences) == 0

def main():
    parser = argparse.ArgumentParser(description="Compare database contents")
    
    # Source database
    parser.add_argument("--source", choices=["local", "remote"], default="local",
                       help="Source database type")
    parser.add_argument("--source-url", help="Source database URL (for remote)")
    
    # Target database
    parser.add_argument("--target", choices=["local", "remote"], default="remote",
                       help="Target database type")
    parser.add_argument("--target-url", help="Target database URL (for remote)")
    
    # Options
    parser.add_argument("--restaurants", nargs="*", help="Specific restaurant slugs to compare")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Prepare source config
    source_config = {"type": args.source, "name": f"{args.source.title()} DB"}
    if args.source == "remote":
        source_url = args.source_url or os.getenv("SOURCE_DATABASE_URL")
        if not source_url:
            print("❌ Source database URL required for remote source")
            print("Use --source-url or set SOURCE_DATABASE_URL environment variable")
            return
        source_config["url"] = source_url
    
    # Prepare target config
    target_config = {"type": args.target, "name": f"{args.target.title()} DB"}
    if args.target == "remote":
        target_url = args.target_url or os.getenv("TARGET_DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")
        if not target_url:
            print("❌ Target database URL required for remote target")
            print("Use --target-url or set TARGET_DATABASE_URL/RENDER_DATABASE_URL environment variable")
            return
        target_config["url"] = target_url
    
    # Run comparison
    comparator = DatabaseComparator(source_config, target_config, args.restaurants)
    success = comparator.run_comparison()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()