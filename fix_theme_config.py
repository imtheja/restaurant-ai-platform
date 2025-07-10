#!/usr/bin/env python3
"""
Script to fix theme_config that's showing as null
"""

import sys
import os
sys.path.append('/Users/tejasmachine/Research/restaurant-ai-platform/backend')

from shared.database.connection import get_db_context, text
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_theme_config():
    """Fix theme configuration"""
    try:
        with get_db_context() as db:
            # Update theme config for Chip Cookies
            theme_config = {
                "primary": "#aa8a40",
                "secondary": "#d4a854", 
                "accent": "#ede7d4",
                "background": "#ffffff",
                "text": "#333333",
                "gradients": {
                    "header": "linear-gradient(135deg, #aa8a40 0%, #d4a854 50%, #aa8a40 100%)",
                    "button": "linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)",
                    "fab": "linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)"
                }
            }
            
            theme_json = json.dumps(theme_config)
            
            db.execute(text("""
                UPDATE restaurants 
                SET theme_config = :theme_config
                WHERE slug = 'baker-bettys'
            """), {
                "theme_config": theme_json
            })
            
            db.commit()
            logger.info("Updated theme configuration")
            
            # Verify
            result = db.execute(text("SELECT theme_config FROM restaurants WHERE slug = 'baker-bettys'"))
            theme = result.fetchone()
            if theme[0]:
                parsed_theme = json.loads(theme[0])
                logger.info(f"Theme primary color: {parsed_theme.get('primary')}")
                logger.info("✅ Theme config updated successfully")
            else:
                logger.error("❌ Theme config is still null")
                
    except Exception as e:
        logger.error(f"Failed to fix theme config: {e}")

if __name__ == "__main__":
    fix_theme_config()