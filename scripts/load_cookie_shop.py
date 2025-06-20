#!/usr/bin/env python3
"""
Load Cookie Shop sample data into the database
"""
import sys
import os
from pathlib import Path
from uuid import uuid4
from decimal import Decimal

# Add backend to path
backend_path = str(Path(__file__).parent.parent / 'backend' / 'shared')
sys.path.append(backend_path)

from sqlalchemy.orm import Session
from database.connection import SessionLocal, engine
from database.models import Base, Restaurant, MenuCategory, MenuItem, Ingredient, MenuItemIngredient
import json
import uuid

def create_cookie_shop_data():
    """Create and load Cookie Shop sample data"""
    session = SessionLocal()
    
    try:
        # Create restaurant
        restaurant = Restaurant(
            id=uuid4(),
            name="The Cookie Jar",
            slug="the-cookie-jar",
            cuisine_type="Dessert",
            description="Gourmet warm cookies made fresh daily with premium ingredients",
            avatar_config={
                "name": "Baker Betty",
                "personality": "friendly_knowledgeable",
                "greeting": "Hi! I'm Baker Betty from The Cookie Jar. What can I help you with?",
                "tone": "warm",
                "special_instructions": "Always emphasize the warmth and freshness of cookies, mention that they're made to order, and suggest milk pairings"
            },
            contact_info={
                "phone": "(555) 123-4567",
                "email": "hello@thecookiejar.com",
                "address": "123 Sweet Street, Dessert City, DC 12345"
            },
            settings={
                "business_hours": {
                    "monday": "10:00 AM - 10:00 PM",
                    "tuesday": "10:00 AM - 10:00 PM",
                    "wednesday": "10:00 AM - 10:00 PM",
                    "thursday": "10:00 AM - 10:00 PM",
                    "friday": "10:00 AM - 11:00 PM",
                    "saturday": "10:00 AM - 11:00 PM",
                    "sunday": "11:00 AM - 9:00 PM"
                },
                "order_types": ["dine-in", "takeout", "delivery"],
                "primary_color": "#8B4513",  # Saddle brown
                "accent_color": "#D2691E"    # Chocolate
            },
            is_active=True
        )
        session.add(restaurant)
        session.flush()
        
        # Create categories
        categories = {
            "signature": MenuCategory(
                id=uuid4(),
                restaurant_id=restaurant.id,
                name="Signature Cookies",
                description="Our classic warm gourmet cookies",
                display_order=1
            ),
            "specialty": MenuCategory(
                id=uuid4(),
                restaurant_id=restaurant.id,
                name="Specialty Cookies",
                description="Unique creations with special toppings and infusions",
                display_order=2
            ),
            "beverages": MenuCategory(
                id=uuid4(),
                restaurant_id=restaurant.id,
                name="Beverages",
                description="Perfect pairings for your cookies",
                display_order=3
            )
        }
        
        for cat in categories.values():
            session.add(cat)
        session.flush()
        
        # Create ingredients
        ingredients = {}
        ingredient_list = [
            # Base ingredients
            ("butter", "Unsalted AA butter", "Dairy", ["dairy"]),
            ("white_sugar", "White granulated sugar", "Sweetener", []),
            ("brown_sugar", "Brown sugar", "Sweetener", []),
            ("egg", "Liquid egg", "Protein", ["eggs"]),
            ("vanilla", "Vanilla extract", "Flavoring", []),
            ("flour", "All-purpose flour", "Grain", ["gluten"]),
            ("baking_powder", "Baking powder", "Leavening", []),
            
            # Chocolate varieties
            ("milk_chocolate", "Milk chocolate chips", "Chocolate", ["dairy"]),
            ("semi_sweet", "Semi-sweet chocolate wafers", "Chocolate", ["dairy"]),
            ("white_chocolate", "White chocolate chips", "Chocolate", ["dairy"]),
            
            # Special ingredients
            ("biscoff_crumbs", "Biscoff cookie crumbs", "Cookie", ["gluten"]),
            ("biscoff_butter", "Biscoff cookie butter", "Spread", ["gluten"]),
            ("cocoa", "Belgian cocoa powder", "Chocolate", []),
            ("sea_salt", "Maldon sea salt", "Seasoning", []),
            ("shortening", "Vegetable shortening", "Fat", []),
            ("almond_extract", "Almond extract", "Flavoring", ["tree_nuts"]),
            ("salt", "Salt", "Seasoning", []),
            
            # Toppings
            ("caramel", "Caramel sauce", "Topping", ["dairy"]),
            ("toffee", "Toffee bits", "Topping", ["dairy"]),
            ("condensed_milk", "Sweetened condensed milk", "Dairy", ["dairy"]),
            ("oreos", "Crushed Oreos", "Cookie", ["gluten"]),
            ("cinnamon_sugar", "Cinnamon sugar", "Topping", []),
            ("toasted_coconut", "Fresh toasted coconut", "Topping", ["tree_nuts"]),
            ("pistachio_cream", "Pistachio cream", "Nut Spread", ["tree_nuts"]),
            ("kataifi", "Kataifi (shredded phyllo)", "Pastry", ["gluten"]),
            
            # Frosting ingredients
            ("cream_cheese", "Cream cheese", "Dairy", ["dairy"]),
            ("confetti", "Confetti sprinkles", "Topping", []),
            
            # Beverage ingredients
            ("whole_milk", "Whole milk", "Dairy", ["dairy"]),
            ("chocolate_syrup", "Chocolate syrup", "Flavoring", []),
            ("coffee", "Fresh brewed coffee", "Beverage", []),
            ("ice_cream", "Vanilla ice cream", "Dairy", ["dairy"])
        ]
        
        for key, name, category, allergens in ingredient_list:
            ing = Ingredient(
                id=uuid4(),
                name=name,
                category=category,
                allergen_info=allergens
            )
            ingredients[key] = ing
            session.add(ing)
        session.flush()
        
        # Create menu items
        menu_items = []
        
        # Signature Cookies
        signature_cookies = [
            {
                "name": "Boneless",
                "description": "Our original signature warm gourmet cookie with a perfectly balanced buttery flavor",
                "price": 3.99,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder"],
                "prep_time": 12
            },
            {
                "name": "OG",
                "description": "Our signature warm gourmet chocolate chip cookie",
                "price": 4.49,
                "ingredients": ["milk_chocolate", "butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder"],
                "prep_time": 12
            },
            {
                "name": "Biscoff",
                "description": "A warm gourmet chip cookie made with Biscoff cookie crumbs, white chocolate chips, and stuffed with Biscoff cookie butter",
                "price": 5.49,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "white_chocolate", "biscoff_crumbs", "biscoff_butter", "egg", "vanilla", "flour", "baking_powder"],
                "prep_time": 15,
                "is_signature": True
            },
            {
                "name": "Semi Sweet",
                "description": "A warm gourmet cookie made with semi-sweet chocolate wafers and topped with Maldon sea salt",
                "price": 4.99,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "semi_sweet", "egg", "vanilla", "flour", "baking_powder", "sea_salt"],
                "prep_time": 12
            },
            {
                "name": "Cocoa",
                "description": "A warm gourmet cocoa cookie made with rich Belgian cocoa powder",
                "price": 4.49,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "cocoa"],
                "prep_time": 12
            },
            {
                "name": "Sugar Cookie",
                "description": "Our signature sugar cookie topped with house-made cream cheese frosting and confetti sprinkles",
                "price": 4.99,
                "ingredients": ["butter", "shortening", "white_sugar", "egg", "vanilla", "almond_extract", "baking_powder", "salt", "flour", "cream_cheese", "confetti"],
                "prep_time": 15
            }
        ]
        
        # Specialty Cookies
        specialty_cookies = [
            {
                "name": "Better Than Sex Chip",
                "description": "Base cocoa cookie infused with caramel, and topped with whipped topping, more caramel, and toffee bits",
                "price": 6.99,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "cocoa", "caramel", "toffee"],
                "prep_time": 18,
                "is_signature": True
            },
            {
                "name": "Oreo Dunk Chip",
                "description": "A rich cocoa cookie infused with sweetened condensed milk and topped with white chocolate and crushed Oreos",
                "price": 6.49,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "cocoa", "condensed_milk", "white_chocolate", "oreos"],
                "prep_time": 18
            },
            {
                "name": "Tres Leches Chip",
                "description": "A warm gourmet buttery cookie infused with sweetened condensed milk and topped with whipped topping and cinnamon sugar",
                "price": 6.49,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "condensed_milk", "cinnamon_sugar"],
                "prep_time": 18
            },
            {
                "name": "Choconut Chip",
                "description": "A warm OG chip capped with melted milk chocolate and topped with fresh toasted coconut",
                "price": 6.99,
                "ingredients": ["milk_chocolate", "butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "toasted_coconut"],
                "prep_time": 20
            },
            {
                "name": "Dubai Chocolate Pistachio Cream",
                "description": "A cocoa cookie infused with pistachio cream and kataifi",
                "price": 7.99,
                "ingredients": ["butter", "white_sugar", "brown_sugar", "egg", "vanilla", "flour", "baking_powder", "cocoa", "pistachio_cream", "kataifi"],
                "prep_time": 20,
                "is_signature": True
            }
        ]
        
        # Beverages
        beverages = [
            {
                "name": "Fresh Milk",
                "description": "Ice cold whole milk - the perfect cookie companion",
                "price": 2.99,
                "ingredients": ["whole_milk"],
                "prep_time": 1,
                "category": "beverages"
            },
            {
                "name": "Chocolate Milk",
                "description": "Rich chocolate milk made with premium chocolate syrup",
                "price": 3.49,
                "ingredients": ["whole_milk", "chocolate_syrup"],
                "prep_time": 2,
                "category": "beverages"
            },
            {
                "name": "Cookie Milkshake",
                "description": "Vanilla milkshake blended with your choice of cookie",
                "price": 5.99,
                "ingredients": ["whole_milk", "ice_cream"],
                "prep_time": 5,
                "category": "beverages"
            },
            {
                "name": "Hot Coffee",
                "description": "Fresh brewed coffee - great with our chocolate cookies",
                "price": 2.49,
                "ingredients": ["coffee"],
                "prep_time": 3,
                "category": "beverages"
            }
        ]
        
        # Add signature cookies
        for cookie_data in signature_cookies:
            cookie = MenuItem(
                id=uuid4(),
                restaurant_id=restaurant.id,
                category_id=categories["signature"].id,
                name=cookie_data["name"],
                description=cookie_data["description"],
                price=Decimal(str(cookie_data["price"])),
                is_available=True,
                is_signature=cookie_data.get("is_signature", False),
                spice_level=0,
                preparation_time=cookie_data["prep_time"],
                allergen_info=[],  # Will be calculated from ingredients
                tags=["warm", "fresh-baked", "gourmet"]
            )
            session.add(cookie)
            session.flush()
            
            # Add ingredients
            allergens = set()
            for i, ing_key in enumerate(cookie_data["ingredients"]):
                if ing_key in ingredients:
                    menu_ing = MenuItemIngredient(
                        menu_item_id=cookie.id,
                        ingredient_id=ingredients[ing_key].id,
                        quantity="1",
                        unit="portion",
                        is_primary=(i < 4)  # First 4 ingredients are primary
                    )
                    session.add(menu_ing)
                    allergens.update(ingredients[ing_key].allergen_info)
            
            cookie.allergen_info = list(allergens)
            menu_items.append(cookie)
        
        # Add specialty cookies
        for cookie_data in specialty_cookies:
            cookie = MenuItem(
                id=uuid4(),
                restaurant_id=restaurant.id,
                category_id=categories["specialty"].id,
                name=cookie_data["name"],
                description=cookie_data["description"],
                price=Decimal(str(cookie_data["price"])),
                is_available=True,
                is_signature=cookie_data.get("is_signature", False),
                spice_level=0,
                preparation_time=cookie_data["prep_time"],
                allergen_info=[],
                tags=["specialty", "gourmet", "indulgent"]
            )
            session.add(cookie)
            session.flush()
            
            # Add ingredients
            allergens = set()
            for i, ing_key in enumerate(cookie_data["ingredients"]):
                if ing_key in ingredients:
                    menu_ing = MenuItemIngredient(
                        menu_item_id=cookie.id,
                        ingredient_id=ingredients[ing_key].id,
                        quantity="1",
                        unit="portion",
                        is_primary=(i < 4)
                    )
                    session.add(menu_ing)
                    allergens.update(ingredients[ing_key].allergen_info)
            
            cookie.allergen_info = list(allergens)
            menu_items.append(cookie)
        
        # Add beverages
        for bev_data in beverages:
            beverage = MenuItem(
                id=uuid4(),
                restaurant_id=restaurant.id,
                category_id=categories["beverages"].id,
                name=bev_data["name"],
                description=bev_data["description"],
                price=Decimal(str(bev_data["price"])),
                is_available=True,
                is_signature=False,
                spice_level=0,
                preparation_time=bev_data["prep_time"],
                allergen_info=[],
                tags=["beverage", "drink"]
            )
            session.add(beverage)
            session.flush()
            
            # Add ingredients
            allergens = set()
            for ing_key in bev_data["ingredients"]:
                if ing_key in ingredients:
                    menu_ing = MenuItemIngredient(
                        menu_item_id=beverage.id,
                        ingredient_id=ingredients[ing_key].id,
                        quantity="1",
                        unit="serving",
                        is_primary=True
                    )
                    session.add(menu_ing)
                    allergens.update(ingredients[ing_key].allergen_info)
            
            beverage.allergen_info = list(allergens)
            menu_items.append(beverage)
        
        # Commit all changes
        session.commit()
        
        print(f"✅ Successfully created The Cookie Jar restaurant with:")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(ingredients)} ingredients")
        print(f"   - {len(menu_items)} menu items")
        print(f"\n🍪 Visit http://localhost:3000/r/the-cookie-jar to see your cookie shop!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error loading cookie shop data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🍪 Loading The Cookie Jar sample data...")
    create_cookie_shop_data()