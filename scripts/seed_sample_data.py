#!/usr/bin/env python3
"""
Sample Data Seeder for Restaurant AI Platform
Seeds the database with sample restaurant data for testing
"""
import os
import sys
import psycopg2
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSeeder:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def seed_sample_restaurants(self, conn):
        """Seed sample restaurant data"""
        sample_restaurants = [
            {
                'name': 'Baker Betty\'s Cookie Shop',
                'slug': 'baker-bettys',
                'cuisine_type': 'Bakery',
                'description': 'Fresh baked cookies and sweet treats daily',
                'ai_config': {
                    "mode": "hybrid",
                    "provider": "openai",
                    "features": {
                        "speech_synthesis": True,
                        "speech_recognition": True,
                        "streaming": True,
                        "voice_selection": True
                    },
                    "model_config": {
                        "model_name": "gpt-4o-mini",
                        "max_tokens": 150,
                        "temperature": 0.8,
                        "context_messages": 10
                    },
                    "performance": {
                        "streaming_enabled": True,
                        "cache_responses": True,
                        "max_daily_requests": 2000,
                        "max_daily_cost_usd": 20.0,
                        "rate_limit_per_minute": 100
                    }
                },
                'avatar_config': {
                    'name': 'Baker Betty',
                    'personality': 'friendly_knowledgeable',
                    'greeting': 'Welcome to Baker Betty\'s! What delicious cookies can I help you discover today?',
                    'tone': 'warm'
                }
            },
            {
                'name': 'Mario\'s Italian Restaurant',
                'slug': 'marios-italian',
                'cuisine_type': 'Italian',
                'description': 'Authentic Italian cuisine with fresh ingredients',
                'ai_config': {
                    "mode": "text_only",
                    "provider": "openai",
                    "features": {
                        "speech_synthesis": False,
                        "speech_recognition": False,
                        "streaming": True,
                        "voice_selection": False
                    },
                    "model_config": {
                        "model_name": "gpt-4o-mini",
                        "max_tokens": 200,
                        "temperature": 0.7,
                        "context_messages": 15
                    },
                    "performance": {
                        "streaming_enabled": True,
                        "cache_responses": True,
                        "max_daily_requests": 1500,
                        "max_daily_cost_usd": 15.0,
                        "rate_limit_per_minute": 80
                    }
                },
                'avatar_config': {
                    'name': 'Chef Mario',
                    'personality': 'professional_formal',
                    'greeting': 'Benvenuto! Welcome to Mario\'s Italian Restaurant. How may I assist you with our authentic Italian menu?',
                    'tone': 'professional'
                }
            },
            {
                'name': 'Tokyo Sushi Bar',
                'slug': 'tokyo-sushi',
                'cuisine_type': 'Japanese',
                'description': 'Fresh sushi and traditional Japanese dishes',
                'ai_config': {
                    "mode": "speech_enabled",
                    "provider": "openai",
                    "features": {
                        "speech_synthesis": True,
                        "speech_recognition": True,
                        "streaming": True,
                        "voice_selection": True
                    },
                    "model_config": {
                        "model_name": "gpt-4o",
                        "max_tokens": 180,
                        "temperature": 0.6,
                        "context_messages": 12
                    },
                    "performance": {
                        "streaming_enabled": True,
                        "cache_responses": True,
                        "max_daily_requests": 1000,
                        "max_daily_cost_usd": 25.0,
                        "rate_limit_per_minute": 60
                    }
                },
                'avatar_config': {
                    'name': 'Sushi Master Yuki',
                    'personality': 'expert_chef',
                    'greeting': 'Irasshaimase! Welcome to Tokyo Sushi Bar. I can help you explore our fresh sushi and traditional dishes.',
                    'tone': 'professional'
                }
            }
        ]
        
        with conn.cursor() as cur:
            for restaurant in sample_restaurants:
                # Check if restaurant already exists
                cur.execute("SELECT id FROM restaurants WHERE slug = %s", (restaurant['slug'],))
                if cur.fetchone():
                    logger.info(f"Restaurant {restaurant['name']} already exists, skipping...")
                    continue
                
                # Insert restaurant
                cur.execute("""
                    INSERT INTO restaurants (
                        name, slug, cuisine_type, description, 
                        ai_config, avatar_config, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    restaurant['name'],
                    restaurant['slug'],
                    restaurant['cuisine_type'],
                    restaurant['description'],
                    json.dumps(restaurant['ai_config']),
                    json.dumps(restaurant['avatar_config']),
                    True
                ))
                
                restaurant_id = cur.fetchone()[0]
                logger.info(f"Created restaurant: {restaurant['name']} (ID: {restaurant_id})")
        
        conn.commit()
        logger.info("Sample restaurant data seeded successfully")
    
    def seed_sample_categories_and_items(self, conn):
        """Seed sample menu categories and items"""
        
        # Get Baker Betty's restaurant ID
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM restaurants WHERE slug = 'baker-bettys' LIMIT 1")
            result = cur.fetchone()
            if not result:
                logger.warning("Baker Betty's restaurant not found, skipping menu items")
                return
            
            restaurant_id = result[0]
            
            # Sample categories and items
            categories_items = [
                {
                    'category': 'Signature Cookies',
                    'items': [
                        {
                            'name': 'Cookie Jar Special',
                            'description': 'Our famous chocolate chip cookie with a twist of sea salt',
                            'price': 3.50,
                            'is_signature': True,
                            'allergen_info': ['gluten', 'dairy', 'eggs']
                        },
                        {
                            'name': 'Semi Sweet Delight',
                            'description': 'Semi-sweet chocolate chips in our classic cookie dough',
                            'price': 3.25,
                            'is_signature': True,
                            'allergen_info': ['gluten', 'dairy', 'eggs']
                        }
                    ]
                },
                {
                    'category': 'Specialty Cookies',
                    'items': [
                        {
                            'name': 'Biscoff Dreams',
                            'description': 'Crunchy Biscoff cookie pieces in soft vanilla dough',
                            'price': 4.00,
                            'is_signature': False,
                            'allergen_info': ['gluten', 'dairy', 'eggs', 'soy']
                        },
                        {
                            'name': 'Oreo Madness',
                            'description': 'Crushed Oreo cookies mixed into chocolate cookie base',
                            'price': 4.25,
                            'is_signature': False,
                            'allergen_info': ['gluten', 'dairy', 'eggs', 'soy']
                        }
                    ]
                }
            ]
            
            for cat_data in categories_items:
                # Create category
                cur.execute("""
                    INSERT INTO menu_categories (restaurant_id, name, display_order, is_active)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (restaurant_id, cat_data['category'], 1, True))
                
                result = cur.fetchone()
                if result:
                    category_id = result[0]
                    logger.info(f"Created category: {cat_data['category']}")
                else:
                    # Category already exists, get its ID
                    cur.execute("""
                        SELECT id FROM menu_categories 
                        WHERE restaurant_id = %s AND name = %s
                    """, (restaurant_id, cat_data['category']))
                    category_id = cur.fetchone()[0]
                
                # Create items
                for item in cat_data['items']:
                    cur.execute("""
                        INSERT INTO menu_items (
                            restaurant_id, category_id, name, description, 
                            price, is_signature, allergen_info, is_available, display_order
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        restaurant_id, category_id, item['name'], item['description'],
                        item['price'], item['is_signature'], item['allergen_info'], 
                        True, 1
                    ))
                    
                    if cur.rowcount > 0:
                        logger.info(f"Created menu item: {item['name']}")
            
            conn.commit()
            logger.info("Sample menu data seeded successfully")
    
    def run_seeding(self, include_menu: bool = True):
        """Run all seeding operations"""
        try:
            logger.info("Starting data seeding...")
            
            conn = self.get_db_connection()
            
            # Seed restaurants
            self.seed_sample_restaurants(conn)
            
            # Seed menu items
            if include_menu:
                self.seed_sample_categories_and_items(conn)
            
            conn.close()
            logger.info("Data seeding completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed sample data')
    parser.add_argument('--restaurants-only', action='store_true',
                       help='Seed only restaurants, not menu items')
    parser.add_argument('--database-url', type=str,
                       help='Database URL (overrides DATABASE_URL env var)')
    
    args = parser.parse_args()
    
    try:
        seeder = DataSeeder(database_url=args.database_url)
        success = seeder.run_seeding(include_menu=not args.restaurants_only)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()