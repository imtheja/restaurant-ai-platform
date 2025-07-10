#!/usr/bin/env python3
"""
Update menu items with the correct Cookie Jar menu
"""

import os
import sys
from pathlib import Path

# Add the shared module to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "shared"))

from database.connection import get_db_context
from sqlalchemy import text

def update_menu():
    """Update the menu with correct Cookie Jar items"""
    
    print("🍪 UPDATING COOKIE JAR MENU")
    print("=" * 60)
    
    # Correct menu structure
    signature_cookies = [
        ("Boneless", "Our original signature warm gourmet cookie with a perfectly balanced buttery flavor.", 3.99, 1),
        ("OG", "Our signature warm gourmet chocolate chip cookie.", 4.49, 2),
        ("Biscoff", "A warm gourmet chip cookie made with Biscoff cookie crumbs, white chocolate chips, and stuffed with Biscoff cookie butter.", 5.49, 3),
        ("Semi Sweet", "A warm gourmet cookie made with semi-sweet chocolate wafers and topped with Maldon sea salt.", 4.99, 4),
        ("Cocoa", "A warm gourmet cocoa cookie made with rich Belgian cocoa powder.", 4.49, 5),
        ("Sugar Cookie", "Our signature sugar cookie topped with house-made cream cheese frosting and confetti sprinkles.", 4.99, 6),
    ]
    
    specialty_cookies = [
        ("Better Than Sex Chip", "Base cocoa cookie infused with caramel, and topped with whipped topping, more caramel, and toffee bits.", 6.99, 1),
        ("Oreo Dunk Chip", "A rich cocoa cookie infused with sweetened condensed milk and topped with white chocolate and crushed Oreos.", 6.49, 2),
        ("Tres Leches Chip", "A warm gourmet buttery cookie infused with sweetened condensed milk and topped with whipped topping and cinnamon sugar.", 6.49, 3),
        ("Choconut Chip", "A warm OG chip capped with melted milk chocolate and topped with fresh toasted coconut.", 6.99, 4),
        ("Dubai Chocolate Pistachio Cream", "A cocoa cookie infused with pistachio cream and kataifi.", 7.99, 5),
    ]
    
    beverages = [
        ("Fresh Milk", "Cold fresh milk - perfect with warm cookies.", 2.99, 1),
        ("Chocolate Milk", "Rich chocolate milk.", 3.49, 2),
        ("Hot Coffee", "Freshly brewed hot coffee.", 2.49, 3),
        ("Cookie Milkshake", "Thick milkshake made with our cookies.", 5.99, 4),
    ]
    
    with get_db_context() as db:
        # Get category IDs
        categories = db.execute(text("""
            SELECT id, name FROM menu_categories 
            WHERE name IN ('Signature Cookies', 'Specialty Cookies', 'Beverages')
        """)).fetchall()
        
        category_map = {cat[1]: cat[0] for cat in categories}
        
        print(f"📂 Found categories: {list(category_map.keys())}")
        
        # Clear existing menu items
        print("🧹 Clearing existing menu items...")
        db.execute(text("DELETE FROM menu_item_ingredients"))
        db.execute(text("DELETE FROM menu_items"))
        
        # Insert Signature Cookies
        print("📋 Adding Signature Cookies...")
        for name, desc, price, order in signature_cookies:
            db.execute(text("""
                INSERT INTO menu_items (
                    id, restaurant_id, category_id, name, description, price, 
                    display_order, is_available, is_signature, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), 
                    (SELECT id FROM restaurants WHERE slug = 'the-cookie-jar' LIMIT 1),
                    :category_id, :name, :description, :price, 
                    :display_order, true, true, NOW(), NOW()
                )
            """), {
                'category_id': category_map['Signature Cookies'],
                'name': name,
                'description': desc,
                'price': price,
                'display_order': order
            })
            print(f"  ✅ Added: {name}")
        
        # Insert Specialty Cookies
        print("📋 Adding Specialty Cookies...")
        for name, desc, price, order in specialty_cookies:
            db.execute(text("""
                INSERT INTO menu_items (
                    id, restaurant_id, category_id, name, description, price, 
                    display_order, is_available, is_signature, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), 
                    (SELECT id FROM restaurants WHERE slug = 'the-cookie-jar' LIMIT 1),
                    :category_id, :name, :description, :price, 
                    :display_order, true, false, NOW(), NOW()
                )
            """), {
                'category_id': category_map['Specialty Cookies'],
                'name': name,
                'description': desc,
                'price': price,
                'display_order': order
            })
            print(f"  ✅ Added: {name}")
        
        # Insert Beverages
        print("📋 Adding Beverages...")
        for name, desc, price, order in beverages:
            db.execute(text("""
                INSERT INTO menu_items (
                    id, restaurant_id, category_id, name, description, price, 
                    display_order, is_available, is_signature, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), 
                    (SELECT id FROM restaurants WHERE slug = 'the-cookie-jar' LIMIT 1),
                    :category_id, :name, :description, :price, 
                    :display_order, true, false, NOW(), NOW()
                )
            """), {
                'category_id': category_map['Beverages'],
                'name': name,
                'description': desc,
                'price': price,
                'display_order': order
            })
            print(f"  ✅ Added: {name}")
        
        # Verify the update
        result = db.execute(text("""
            SELECT mc.name as category, COUNT(mi.id) as count
            FROM menu_categories mc
            LEFT JOIN menu_items mi ON mc.id = mi.category_id
            GROUP BY mc.name, mc.display_order
            ORDER BY mc.display_order
        """)).fetchall()
        
        print("\n📊 Updated Menu Summary:")
        total_items = 0
        for row in result:
            print(f"  {row[0]}: {row[1]} items")
            total_items += row[1]
        print(f"  Total: {total_items} items")
        
        print("\n🎉 Menu update completed!")
        
        return True

if __name__ == "__main__":
    try:
        update_menu()
    except Exception as e:
        print(f"❌ Error updating menu: {e}")
        sys.exit(1)