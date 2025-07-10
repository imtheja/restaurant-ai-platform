#!/usr/bin/env python3
"""
Compare local and Render databases to ensure data is identical
"""
import os
import sys
import json
from datetime import datetime

# Add backend path for local database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Local database imports
from shared.database.connection import get_db_context
from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
from sqlalchemy.orm import joinedload

# Render database imports
import psycopg2
import psycopg2.extras

class DatabaseComparator:
    def __init__(self, render_database_url: str, restaurant_slug: str = "chip-cookies"):
        self.render_url = render_database_url
        self.restaurant_slug = restaurant_slug
        self.local_data = {}
        self.render_data = {}
        self.differences = []
        
    def extract_local_data(self):
        """Extract data from local database"""
        try:
            with get_db_context() as db:
                # Get restaurant
                restaurant = db.query(Restaurant).filter(
                    Restaurant.slug == self.restaurant_slug
                ).first()
                
                if not restaurant:
                    print(f"❌ Restaurant '{self.restaurant_slug}' not found in local database!")
                    return False
                
                self.local_data["restaurant"] = {
                    "name": restaurant.name,
                    "slug": restaurant.slug,
                    "cuisine_type": restaurant.cuisine_type,
                    "description": restaurant.description,
                    "avatar_config": restaurant.avatar_config,
                    "theme_config": restaurant.theme_config,
                    "contact_info": restaurant.contact_info,
                    "settings": restaurant.settings,
                    "is_active": restaurant.is_active
                }
                
                # Get categories
                categories = db.query(MenuCategory).filter(
                    MenuCategory.restaurant_id == restaurant.id,
                    MenuCategory.is_active == True
                ).order_by(MenuCategory.display_order, MenuCategory.name).all()
                
                self.local_data["categories"] = []
                for cat in categories:
                    self.local_data["categories"].append({
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
                
                self.local_data["items"] = []
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
                    self.local_data["items"].append(item_data)
                
                print(f"✅ Extracted local data:")
                print(f"   Restaurant: {restaurant.name}")
                print(f"   Categories: {len(self.local_data['categories'])}")
                print(f"   Menu Items: {len(self.local_data['items'])}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error extracting local data: {e}")
            return False
    
    def extract_render_data(self):
        """Extract data from Render database"""
        try:
            conn = psycopg2.connect(self.render_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get restaurant
            cursor.execute("""
                SELECT name, slug, cuisine_type, description, avatar_config, theme_config, 
                       contact_info, settings, is_active
                FROM restaurants 
                WHERE slug = %s
            """, (self.restaurant_slug,))
            
            restaurant = cursor.fetchone()
            if not restaurant:
                print(f"❌ Restaurant '{self.restaurant_slug}' not found in Render database!")
                return False
            
            self.render_data["restaurant"] = dict(restaurant)
            restaurant_id = None
            
            # Get restaurant ID
            cursor.execute("SELECT id FROM restaurants WHERE slug = %s", (self.restaurant_slug,))
            restaurant_id = cursor.fetchone()["id"]
            
            # Get categories
            cursor.execute("""
                SELECT name, description, display_order, is_active
                FROM menu_categories 
                WHERE restaurant_id = %s AND is_active = true
                ORDER BY display_order, name
            """, (restaurant_id,))
            
            self.render_data["categories"] = [dict(row) for row in cursor.fetchall()]
            
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
            self.render_data["items"] = []
            
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
                
                # Remove item_id as it's not in local data
                del item_data["item_id"]
                
                self.render_data["items"].append(item_data)
            
            cursor.close()
            conn.close()
            
            print(f"✅ Extracted Render data:")
            print(f"   Restaurant: {restaurant['name']}")
            print(f"   Categories: {len(self.render_data['categories'])}")
            print(f"   Menu Items: {len(self.render_data['items'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting Render data: {e}")
            return False
    
    def compare_restaurants(self):
        """Compare restaurant data"""
        local_rest = self.local_data["restaurant"]
        render_rest = self.render_data["restaurant"]
        
        print("\n🏪 RESTAURANT COMPARISON:")
        
        fields_to_compare = ["name", "slug", "cuisine_type", "description", "is_active"]
        json_fields = ["avatar_config", "theme_config", "contact_info", "settings"]
        
        for field in fields_to_compare:
            local_val = local_rest.get(field)
            render_val = render_rest.get(field)
            
            if local_val == render_val:
                print(f"   ✅ {field}: MATCH")
            else:
                print(f"   ❌ {field}: MISMATCH")
                print(f"      Local:  {local_val}")
                print(f"      Render: {render_val}")
                self.differences.append(f"Restaurant {field} mismatch")
        
        for field in json_fields:
            local_val = local_rest.get(field)
            render_val = render_rest.get(field)
            
            # Convert to JSON string for comparison
            local_json = json.dumps(local_val, sort_keys=True) if local_val else None
            render_json = json.dumps(render_val, sort_keys=True) if render_val else None
            
            if local_json == render_json:
                print(f"   ✅ {field}: MATCH")
            else:
                print(f"   ❌ {field}: MISMATCH")
                self.differences.append(f"Restaurant {field} JSON mismatch")
    
    def compare_categories(self):
        """Compare categories"""
        local_cats = self.local_data["categories"]
        render_cats = self.render_data["categories"]
        
        print(f"\n📚 CATEGORIES COMPARISON:")
        
        if len(local_cats) != len(render_cats):
            print(f"   ❌ COUNT MISMATCH: Local={len(local_cats)}, Render={len(render_cats)}")
            self.differences.append("Category count mismatch")
        else:
            print(f"   ✅ COUNT: {len(local_cats)} categories")
        
        # Compare each category
        for i, (local_cat, render_cat) in enumerate(zip(local_cats, render_cats)):
            name = local_cat["name"]
            matches = True
            
            for field in ["name", "description", "display_order", "is_active"]:
                if local_cat.get(field) != render_cat.get(field):
                    matches = False
                    break
            
            if matches:
                print(f"   ✅ {name}: MATCH")
            else:
                print(f"   ❌ {name}: MISMATCH")
                self.differences.append(f"Category {name} mismatch")
    
    def compare_menu_items(self):
        """Compare menu items"""
        local_items = self.local_data["items"]
        render_items = self.render_data["items"]
        
        print(f"\n🍪 MENU ITEMS COMPARISON:")
        
        if len(local_items) != len(render_items):
            print(f"   ❌ COUNT MISMATCH: Local={len(local_items)}, Render={len(render_items)}")
            self.differences.append("Menu items count mismatch")
        else:
            print(f"   ✅ COUNT: {len(local_items)} menu items")
        
        # Compare each item
        for i, (local_item, render_item) in enumerate(zip(local_items, render_items)):
            name = local_item["name"]
            matches = True
            
            # Compare basic fields
            fields_to_compare = [
                "name", "description", "price", "image_url", "is_available",
                "is_signature", "spice_level", "preparation_time", "display_order",
                "category_name"
            ]
            
            for field in fields_to_compare:
                local_val = local_item.get(field)
                render_val = render_item.get(field)
                
                if local_val != render_val:
                    matches = False
                    break
            
            # Compare JSON fields
            json_fields = ["nutritional_info", "allergen_info", "tags"]
            for field in json_fields:
                local_val = local_item.get(field)
                render_val = render_item.get(field)
                
                local_json = json.dumps(local_val, sort_keys=True) if local_val else None
                render_json = json.dumps(render_val, sort_keys=True) if render_val else None
                
                if local_json != render_json:
                    matches = False
                    break
            
            # Compare ingredients
            local_ingredients = local_item.get("ingredients", [])
            render_ingredients = render_item.get("ingredients", [])
            
            if len(local_ingredients) != len(render_ingredients):
                matches = False
            else:
                for local_ing, render_ing in zip(local_ingredients, render_ingredients):
                    if local_ing != render_ing:
                        matches = False
                        break
            
            if matches:
                print(f"   ✅ {name}: MATCH")
            else:
                print(f"   ❌ {name}: MISMATCH")
                self.differences.append(f"Menu item {name} mismatch")
    
    def run_comparison(self):
        """Run complete comparison"""
        print("🔍 COMPARING LOCAL AND RENDER DATABASES")
        print("=" * 50)
        
        # Extract data from both databases
        if not self.extract_local_data():
            return False
        
        if not self.extract_render_data():
            return False
        
        # Run comparisons
        self.compare_restaurants()
        self.compare_categories()
        self.compare_menu_items()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 COMPARISON SUMMARY")
        
        if not self.differences:
            print("🎉 ✅ DATABASES ARE IDENTICAL!")
            print("   All data matches perfectly between local and Render databases.")
        else:
            print(f"⚠️  Found {len(self.differences)} differences:")
            for diff in self.differences:
                print(f"   - {diff}")
        
        return len(self.differences) == 0

def main():
    render_url = os.getenv("RENDER_DATABASE_URL")
    if not render_url:
        print("❌ RENDER_DATABASE_URL not set!")
        print("Please set it with:")
        print("export RENDER_DATABASE_URL='postgresql://username:password@hostname:port/database'")
        return
    
    comparator = DatabaseComparator(render_url, "chip-cookies")
    success = comparator.run_comparison()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()