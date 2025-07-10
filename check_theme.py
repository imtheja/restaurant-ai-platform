#!/usr/bin/env python3
"""
Script to check theme configuration in database
"""

import sys
import os
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

from shared.database.connection import get_db_context, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_theme():
    """Check theme configuration"""
    try:
        with get_db_context() as db:
            result = db.execute(text("SELECT name, slug, theme_config FROM restaurants WHERE slug = 'baker-bettys'"))
            restaurant = result.fetchone()
            
            if restaurant:
                logger.info(f"Restaurant: {restaurant[0]} (slug: {restaurant[1]})")
                theme_config = restaurant[2]
                if theme_config:
                    logger.info(f"Theme config (raw): {theme_config}")
                    logger.info("✅ Theme config exists in database")
                else:
                    logger.info("❌ Theme config is NULL in database")
                    
                    # Let's also check the column type
                    result = db.execute(text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'restaurants' AND column_name = 'theme_config'
                    """))
                    col_info = result.fetchone()
                    if col_info:
                        logger.info(f"Column info: {col_info[0]} - {col_info[1]}")
            else:
                logger.error("Restaurant not found")
                
    except Exception as e:
        logger.error(f"Failed to check theme: {e}")

if __name__ == "__main__":
    check_theme()