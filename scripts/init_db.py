#!/usr/bin/env python3
"""
Database initialization script for Restaurant AI Platform
"""

import os
import sys
import logging
from pathlib import Path

# Add the shared module to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "shared"))

from database.connection import init_database, check_database_health, engine
from database.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database with tables and sample data"""
    
    logger.info("Starting database initialization...")
    
    try:
        # Check if database is accessible
        logger.info("Checking database connection...")
        if not check_database_health():
            logger.error("Database health check failed")
            sys.exit(1)
        
        logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Run initialization
        init_database()
        logger.info("Database initialization completed successfully")
        
        # Verify setup
        logger.info("Verifying database setup...")
        if check_database_health():
            logger.info("Database setup verification passed")
            print("✅ Database initialization completed successfully!")
        else:
            logger.error("Database setup verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()