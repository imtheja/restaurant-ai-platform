import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
import logging
from contextlib import contextmanager
from typing import Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://restaurant_user:secure_password_123@localhost:5432/restaurant_ai_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Redis connection
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Metadata for table operations
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Automatically handles session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    Use when you need database access outside of FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database context error: {e}")
        raise
    finally:
        db.close()

def get_redis():
    """
    Get Redis client instance.
    """
    try:
        # Test connection
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        return None

def init_database():
    """
    Initialize database tables and run any setup scripts.
    """
    from .models import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test connection
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

def check_database_health() -> bool:
    """
    Check if database and Redis are healthy.
    """
    try:
        # Check PostgreSQL
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        
        # Check Redis
        redis_client.ping()
        
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

class DatabaseManager:
    """
    Centralized database operations manager.
    """
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
        self.redis = redis_client
    
    def get_session(self):
        """Get a new database session"""
        return self.session_factory()
    
    def execute_raw_query(self, query: str, params: dict = None):
        """Execute raw SQL query"""
        with get_db_context() as db:
            result = db.execute(text(query), params or {})
            return result.fetchall()
    
    def cache_set(self, key: str, value: str, expire: int = 3600):
        """Set cache value with expiration"""
        try:
            return self.redis.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def cache_get(self, key: str):
        """Get cache value"""
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def cache_delete(self, key: str):
        """Delete cache value"""
        try:
            return self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()