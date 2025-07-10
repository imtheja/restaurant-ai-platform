#!/usr/bin/env python3
"""
Script to fix avatar configuration and restaurant data
"""

import sys
import os
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

from shared.database.connection import get_db_context, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_avatar_and_restaurant():
    """Fix avatar configuration and restaurant data"""
    try:
        with get_db_context() as db:
            # First, check current restaurant data
            result = db.execute(text("SELECT id, name, slug, avatar_config FROM restaurants WHERE slug = 'baker-bettys'"))
            restaurant = result.fetchone()
            
            if restaurant:
                logger.info(f"Found restaurant: {restaurant[1]} (slug: {restaurant[2]})")
                
                # Update avatar config to match Chip Cookies branding
                import json
                new_avatar_config = {
                    "name": "Cookie Expert Betty",
                    "personality": "friendly_knowledgeable", 
                    "greeting": "Welcome to Chip Cookies! I am Cookie Expert Betty, your personal guide to our delicious warm gourmet cookies. What kind of amazing cookie experience can I help you create today?",
                    "tone": "warm",
                    "special_instructions": "Always emphasize the warmth, freshness and gourmet quality of our cookies. Mention they are made to order and suggest perfect pairings. Be enthusiastic about ingredients and flavor profiles."
                }
                
                # Update restaurant with correct avatar config
                avatar_json = json.dumps(new_avatar_config)
                db.execute(text("""
                    UPDATE restaurants 
                    SET 
                        avatar_config = :avatar_config
                    WHERE slug = 'baker-bettys'
                """), {
                    "avatar_config": avatar_json
                })
                
                logger.info("Updated avatar configuration for Chip Cookies")
                
                # Also ensure description matches
                db.execute(text("""
                    UPDATE restaurants 
                    SET 
                        description = 'Fresh baked gourmet cookies made to order with premium ingredients. Warm, gooey, and irresistibly delicious!'
                    WHERE slug = 'baker-bettys'
                """))
                
                db.commit()
                
                # Verify the changes
                result = db.execute(text("SELECT name, avatar_config FROM restaurants WHERE slug = 'baker-bettys'"))
                updated = result.fetchone()
                logger.info(f"Updated restaurant: {updated[0]}")
                
                if updated[1]:
                    import json
                    avatar_data = json.loads(updated[1])
                    logger.info(f"Avatar name: {avatar_data.get('name')}")
                    logger.info(f"Avatar greeting: {avatar_data.get('greeting')[:50]}...")
                    
            else:
                logger.error("Restaurant with slug 'baker-bettys' not found!")
                
                # Check what restaurants exist
                result = db.execute(text("SELECT id, name, slug FROM restaurants"))
                restaurants = result.fetchall()
                logger.info("Available restaurants:")
                for r in restaurants:
                    logger.info(f"  - {r[1]} (slug: {r[2]})")
                    
    except Exception as e:
        logger.error(f"Failed to fix avatar config: {e}")

if __name__ == "__main__":
    fix_avatar_and_restaurant()