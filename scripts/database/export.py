#!/usr/bin/env python3
"""
Generic database export script for restaurant data
"""
import sys
import os
import json
import argparse
from datetime import datetime
from typing import Optional, List

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from shared.database.connection import get_db_context
from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
from sqlalchemy.orm import joinedload

class RestaurantDataExporter:
    def __init__(self, output_dir: str = ".", include_inactive: bool = False):
        self.output_dir = output_dir
        self.include_inactive = include_inactive
        
    def export_restaurant_data(self, restaurant_slug: str) -> Optional[dict]:
        """Export all data for a specific restaurant"""
        
        export_data = {
            "restaurant": None,
            "categories": [],
            "items": [],
            "ingredients": [],
            "exported_at": datetime.now().isoformat(),
            "version": "2.0",
            "metadata": {
                "restaurant_slug": restaurant_slug,
                "include_inactive": self.include_inactive,
                "exporter": "restaurant-ai-platform"
            }
        }
        
        try:
            with get_db_context() as db:
                # Get restaurant
                query = db.query(Restaurant).filter(Restaurant.slug == restaurant_slug)
                if not self.include_inactive:
                    query = query.filter(Restaurant.is_active == True)
                
                restaurant = query.first()
                
                if not restaurant:
                    print(f"❌ Restaurant with slug '{restaurant_slug}' not found!")
                    return None
                    
                # Export restaurant data
                export_data["restaurant"] = {
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
                
                print(f"✅ Exported restaurant: {restaurant.name}")
                
                # Export categories
                cat_query = db.query(MenuCategory).filter(
                    MenuCategory.restaurant_id == restaurant.id
                )
                if not self.include_inactive:
                    cat_query = cat_query.filter(MenuCategory.is_active == True)
                
                categories = cat_query.order_by(MenuCategory.display_order).all()
                
                for category in categories:
                    export_data["categories"].append({
                        "name": category.name,
                        "description": category.description,
                        "display_order": category.display_order,
                        "is_active": category.is_active
                    })
                
                print(f"✅ Exported {len(categories)} categories")
                
                # Export menu items
                item_query = db.query(MenuItem).options(
                    joinedload(MenuItem.ingredients).joinedload(MenuItemIngredient.ingredient)
                ).filter(MenuItem.restaurant_id == restaurant.id)
                
                if not self.include_inactive:
                    item_query = item_query.filter(MenuItem.is_available == True)
                
                items = item_query.order_by(MenuItem.display_order).all()
                
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
                    
                    # Export item ingredients
                    for item_ingredient in item.ingredients:
                        if item_ingredient.ingredient:
                            # Include inactive ingredients only if include_inactive is True
                            if self.include_inactive or item_ingredient.ingredient.is_active:
                                item_data["ingredients"].append({
                                    "ingredient_name": item_ingredient.ingredient.name,
                                    "quantity": item_ingredient.quantity,
                                    "unit": item_ingredient.unit,
                                    "is_optional": item_ingredient.is_optional,
                                    "is_primary": item_ingredient.is_primary
                                })
                    
                    export_data["items"].append(item_data)
                
                print(f"✅ Exported {len(items)} menu items")
                
                # Export all ingredients (only those used)
                used_ingredient_names = set()
                for item in export_data["items"]:
                    for ing in item["ingredients"]:
                        used_ingredient_names.add(ing["ingredient_name"])
                
                ing_query = db.query(Ingredient).filter(
                    Ingredient.name.in_(used_ingredient_names)
                )
                if not self.include_inactive:
                    ing_query = ing_query.filter(Ingredient.is_active == True)
                
                ingredients = ing_query.all()
                
                for ingredient in ingredients:
                    export_data["ingredients"].append({
                        "name": ingredient.name,
                        "category": ingredient.category,
                        "allergen_info": ingredient.allergen_info,
                        "nutritional_info": ingredient.nutritional_info,
                        "is_active": ingredient.is_active
                    })
                
                print(f"✅ Exported {len(ingredients)} ingredients")
                
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return None
        
        return export_data
    
    def export_all_restaurants(self) -> Optional[dict]:
        """Export data for all restaurants"""
        export_data = {
            "restaurants": [],
            "exported_at": datetime.now().isoformat(),
            "version": "2.0",
            "metadata": {
                "export_type": "all_restaurants",
                "include_inactive": self.include_inactive,
                "exporter": "restaurant-ai-platform"
            }
        }
        
        try:
            with get_db_context() as db:
                query = db.query(Restaurant)
                if not self.include_inactive:
                    query = query.filter(Restaurant.is_active == True)
                
                restaurants = query.order_by(Restaurant.name).all()
                
                for restaurant in restaurants:
                    restaurant_data = self.export_restaurant_data(restaurant.slug)
                    if restaurant_data:
                        export_data["restaurants"].append(restaurant_data)
                
                print(f"✅ Exported {len(export_data['restaurants'])} restaurants")
                
        except Exception as e:
            print(f"❌ Error exporting all restaurants: {e}")
            return None
        
        return export_data
    
    def save_export(self, data: dict, filename: str) -> bool:
        """Save export data to file"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✅ Data exported to {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving export: {e}")
            return False
    
    def generate_filename(self, restaurant_slug: str = None, export_type: str = "restaurant") -> str:
        """Generate export filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_type == "all":
            return f"all_restaurants_export_{timestamp}.json"
        elif restaurant_slug:
            # Sanitize slug for filename
            safe_slug = restaurant_slug.replace("-", "_").replace(" ", "_")
            return f"{safe_slug}_export_{timestamp}.json"
        else:
            return f"restaurant_export_{timestamp}.json"

def main():
    parser = argparse.ArgumentParser(description="Export restaurant data")
    parser.add_argument("--restaurant", "-r", help="Restaurant slug to export (exports all if not specified)")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive items and ingredients")
    parser.add_argument("--filename", "-f", help="Custom output filename")
    parser.add_argument("--list", action="store_true", help="List available restaurants")
    
    args = parser.parse_args()
    
    # List restaurants if requested
    if args.list:
        try:
            with get_db_context() as db:
                restaurants = db.query(Restaurant).filter(Restaurant.is_active == True).all()
                print("📋 Available restaurants:")
                for restaurant in restaurants:
                    print(f"  - {restaurant.name} (slug: {restaurant.slug})")
        except Exception as e:
            print(f"❌ Error listing restaurants: {e}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    exporter = RestaurantDataExporter(args.output_dir, args.include_inactive)
    
    print("🚀 Starting restaurant data export...")
    
    if args.restaurant:
        # Export specific restaurant
        data = exporter.export_restaurant_data(args.restaurant)
        if data:
            filename = args.filename or exporter.generate_filename(args.restaurant)
            if exporter.save_export(data, filename):
                print(f"\n🎉 Export completed successfully!")
                print(f"📁 File: {os.path.join(args.output_dir, filename)}")
                print(f"📊 Restaurant: {data['restaurant']['name']}")
                print(f"📚 Categories: {len(data['categories'])}")
                print(f"🍪 Menu Items: {len(data['items'])}")
                print(f"🥘 Ingredients: {len(data['ingredients'])}")
            else:
                print("❌ Failed to save export file")
                sys.exit(1)
        else:
            print("❌ Export failed")
            sys.exit(1)
    else:
        # Export all restaurants
        data = exporter.export_all_restaurants()
        if data:
            filename = args.filename or exporter.generate_filename(export_type="all")
            if exporter.save_export(data, filename):
                print(f"\n🎉 Export completed successfully!")
                print(f"📁 File: {os.path.join(args.output_dir, filename)}")
                print(f"🏪 Restaurants: {len(data['restaurants'])}")
            else:
                print("❌ Failed to save export file")
                sys.exit(1)
        else:
            print("❌ Export failed")
            sys.exit(1)

if __name__ == "__main__":
    main()