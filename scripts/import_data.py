#!/usr/bin/env python3
"""
Smart import script for restaurant data with overwrite capabilities
"""
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.database.connection import get_db_context
from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

class SmartDataImporter:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = None
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
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def validate_data(self) -> bool:
        """Validate data structure"""
        if not self.data:
            print("❌ No data loaded")
            return False
        
        required_keys = ["restaurant", "categories", "items", "ingredients"]
        for key in required_keys:
            if key not in self.data:
                print(f"❌ Missing required key: {key}")
                return False
        
        if not self.data["restaurant"]:
            print("❌ Restaurant data is missing")
            return False
        
        print("✅ Data structure is valid")
        return True
    
    def import_restaurant(self, db) -> Optional[Restaurant]:
        """Import or update restaurant"""
        try:
            restaurant_data = self.data["restaurant"]
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
                db.flush()  # Get ID without committing
                
                print(f"✨ Created new restaurant: {restaurant.name}")
                self.stats["restaurants_created"] += 1
                return restaurant
                
        except Exception as e:
            error_msg = f"Error importing restaurant: {e}"
            print(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return None
    
    def import_ingredients(self, db) -> Dict[str, Ingredient]:
        """Import or update ingredients"""
        ingredient_map = {}
        
        for ing_data in self.data["ingredients"]:
            try:
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
                    
            except Exception as e:
                error_msg = f"Error importing ingredient {ing_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        print(f"✅ Processed {len(ingredient_map)} ingredients")
        return ingredient_map
    
    def import_categories(self, db, restaurant: Restaurant) -> Dict[str, MenuCategory]:
        """Import or update categories"""
        category_map = {}
        
        for cat_data in self.data["categories"]:
            try:
                name = cat_data["name"]
                
                # Check if category exists for this restaurant
                existing = db.query(MenuCategory).filter(
                    MenuCategory.restaurant_id == restaurant.id,
                    MenuCategory.name == name
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in cat_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    
                    category_map[name] = existing
                    self.stats["categories_updated"] += 1
                else:
                    # Create new
                    category = MenuCategory(
                        restaurant_id=restaurant.id,
                        **cat_data
                    )
                    db.add(category)
                    db.flush()
                    
                    category_map[name] = category
                    self.stats["categories_created"] += 1
                    
            except Exception as e:
                error_msg = f"Error importing category {cat_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        print(f"✅ Processed {len(category_map)} categories")
        return category_map
    
    def import_menu_items(self, db, restaurant: Restaurant, category_map: Dict[str, MenuCategory], ingredient_map: Dict[str, Ingredient]):
        """Import or update menu items"""
        
        for item_data in self.data["items"]:
            try:
                name = item_data["name"]
                
                # Get category if specified
                category = None
                if item_data.get("category_name"):
                    category = category_map.get(item_data["category_name"])
                
                # Check if item exists for this restaurant
                existing = db.query(MenuItem).filter(
                    MenuItem.restaurant_id == restaurant.id,
                    MenuItem.name == name
                ).first()
                
                # Prepare item data (exclude ingredients and category_name)
                menu_item_data = {k: v for k, v in item_data.items() 
                                if k not in ["ingredients", "category_name"]}
                menu_item_data["restaurant_id"] = restaurant.id
                menu_item_data["category_id"] = category.id if category else None
                
                if existing:
                    # Update existing item
                    for key, value in menu_item_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    
                    menu_item = existing
                    self.stats["items_updated"] += 1
                    
                    # Clear existing ingredients
                    db.query(MenuItemIngredient).filter(
                        MenuItemIngredient.menu_item_id == menu_item.id
                    ).delete()
                    
                else:
                    # Create new item
                    menu_item = MenuItem(**menu_item_data)
                    db.add(menu_item)
                    db.flush()
                    
                    self.stats["items_created"] += 1
                
                # Add ingredients
                for ing_data in item_data.get("ingredients", []):
                    ingredient = ingredient_map.get(ing_data["ingredient_name"])
                    if ingredient:
                        menu_item_ingredient = MenuItemIngredient(
                            menu_item_id=menu_item.id,
                            ingredient_id=ingredient.id,
                            quantity=ing_data.get("quantity"),
                            unit=ing_data.get("unit"),
                            is_optional=ing_data.get("is_optional", False),
                            is_primary=ing_data.get("is_primary", False)
                        )
                        db.add(menu_item_ingredient)
                    
            except Exception as e:
                error_msg = f"Error importing menu item {item_data.get('name', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                self.stats["errors"].append(error_msg)
        
        print(f"✅ Processed menu items")
    
    def import_data(self) -> bool:
        """Main import function"""
        if not self.load_data() or not self.validate_data():
            return False
        
        try:
            with get_db_context() as db:
                print("\n🚀 Starting smart data import...")
                
                # Import restaurant
                restaurant = self.import_restaurant(db)
                if not restaurant:
                    return False
                
                # Import ingredients first (they're referenced by menu items)
                ingredient_map = self.import_ingredients(db)
                
                # Import categories
                category_map = self.import_categories(db, restaurant)
                
                # Import menu items
                self.import_menu_items(db, restaurant, category_map, ingredient_map)
                
                # Commit all changes
                db.commit()
                
                print("\n🎉 Import completed successfully!")
                self.print_stats()
                return True
                
        except Exception as e:
            print(f"❌ Critical error during import: {e}")
            self.stats["errors"].append(f"Critical error: {e}")
            return False
    
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
    
    parser = argparse.ArgumentParser(description="Smart restaurant data importer")
    parser.add_argument("data_file", help="JSON file containing restaurant data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be imported without making changes")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_file):
        print(f"❌ File not found: {args.data_file}")
        return
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Add dry run functionality
        return
    
    importer = SmartDataImporter(args.data_file)
    success = importer.import_data()
    
    if success:
        print("\n✅ Data import successful!")
    else:
        print("\n❌ Data import failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()