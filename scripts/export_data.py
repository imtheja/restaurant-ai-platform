#!/usr/bin/env python3
"""
Export restaurant data for migration to Render
"""
import sys
import os
import json
from datetime import datetime

# Add backend path
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

from shared.database.connection import get_db_context
from shared.database.models import Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
from sqlalchemy.orm import joinedload

def export_restaurant_data(restaurant_slug: str = "chip-cookies"):
    """Export all data for a specific restaurant"""
    
    export_data = {
        "restaurant": None,
        "categories": [],
        "items": [],
        "ingredients": [],
        "exported_at": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
    
    try:
        with get_db_context() as db:
            # Get restaurant
            restaurant = db.query(Restaurant).filter(
                Restaurant.slug == restaurant_slug
            ).first()
            
            if not restaurant:
                print(f"Restaurant with slug '{restaurant_slug}' not found!")
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
            categories = db.query(MenuCategory).filter(
                MenuCategory.restaurant_id == restaurant.id,
                MenuCategory.is_active == True
            ).order_by(MenuCategory.display_order).all()
            
            for category in categories:
                export_data["categories"].append({
                    "name": category.name,
                    "description": category.description,
                    "display_order": category.display_order,
                    "is_active": category.is_active
                })
            
            print(f"✅ Exported {len(categories)} categories")
            
            # Export menu items
            items = db.query(MenuItem).options(
                joinedload(MenuItem.ingredients).joinedload(MenuItemIngredient.ingredient)
            ).filter(
                MenuItem.restaurant_id == restaurant.id
            ).order_by(MenuItem.display_order).all()
            
            for item in items:
                # Find category name
                category_name = None
                if item.category_id:
                    category = next((c for c in categories if str(c.id) == str(item.category_id)), None)
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
                    if item_ingredient.ingredient and item_ingredient.ingredient.is_active:
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
            
            ingredients = db.query(Ingredient).filter(
                Ingredient.name.in_(used_ingredient_names),
                Ingredient.is_active == True
            ).all()
            
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

def save_export(data, filename="restaurant_export.json"):
    """Save export data to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Data exported to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving export: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting restaurant data export...")
    
    # Export Chip Cookies data
    data = export_restaurant_data("chip-cookies")
    
    if data:
        filename = f"chip_cookies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if save_export(data, filename):
            print(f"\n🎉 Export completed successfully!")
            print(f"📁 File: {filename}")
            print(f"📊 Restaurant: {data['restaurant']['name']}")
            print(f"📚 Categories: {len(data['categories'])}")
            print(f"🍪 Menu Items: {len(data['items'])}")
            print(f"🥘 Ingredients: {len(data['ingredients'])}")
        else:
            print("❌ Failed to save export file")
    else:
        print("❌ Export failed")