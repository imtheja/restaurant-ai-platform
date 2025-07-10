#!/usr/bin/env python3
"""
Script to update restaurant slug from 'the-cookie-jar' to 'chip-cookies'
"""

import sys
import os
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

from shared.database.connection import get_db_context, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_slug():
    """Update restaurant slug from the-cookie-jar to chip-cookies"""
    try:
        with get_db_context() as db:
            # First, check current state
            result = db.execute(text("""
                SELECT id, name, slug 
                FROM restaurants 
                WHERE slug = 'the-cookie-jar'
            """))
            
            restaurant = result.fetchone()
            if not restaurant:
                logger.error("Restaurant with slug 'the-cookie-jar' not found!")
                return
            
            logger.info(f"Current restaurant:")
            logger.info(f"  ID: {restaurant[0]}")
            logger.info(f"  Name: {restaurant[1]}")
            logger.info(f"  Current Slug: {restaurant[2]}")
            
            # Update the slug
            result = db.execute(text("""
                UPDATE restaurants 
                SET slug = 'chip-cookies'
                WHERE slug = 'the-cookie-jar'
            """))
            
            if result.rowcount > 0:
                db.commit()
                logger.info(f"\n✅ Successfully updated slug from 'the-cookie-jar' to 'chip-cookies'")
                
                # Verify the change
                result = db.execute(text("""
                    SELECT name, slug 
                    FROM restaurants 
                    WHERE slug = 'chip-cookies'
                """))
                
                updated = result.fetchone()
                if updated:
                    logger.info(f"\nVerified update:")
                    logger.info(f"  Name: {updated[0]}")
                    logger.info(f"  New Slug: {updated[1]}")
                    logger.info(f"\n🌐 New URL will be: http://localhost:3000/r/chip-cookies")
            else:
                logger.error("No rows were updated!")
                    
    except Exception as e:
        logger.error(f"Error updating slug: {e}")
        raise

if __name__ == "__main__":
    update_slug()