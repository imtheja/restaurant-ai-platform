import os
import json
import logging
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from functools import wraps
import re
import uuid
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from text.
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    
    # Add random suffix if needed to ensure uniqueness
    if len(slug) < 3:
        slug += '-' + secrets.token_hex(3)
    
    return slug[:100]  # Limit length

def generate_session_id() -> str:
    """
    Generate a unique session ID.
    """
    return f"session_{secrets.token_urlsafe(16)}"

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt.
    For production, use bcrypt or similar.
    """
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ':' + salt

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    """
    try:
        hash_part, salt = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_part
    except:
        return False

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'<script',
        r'</script>'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Limit length
    return text[:max_length].strip()

def format_price(price: Decimal) -> str:
    """
    Format price for display.
    """
    return f"${price:.2f}"

def parse_allergens(allergen_list: List[str]) -> Dict[str, bool]:
    """
    Parse allergen list into a structured format.
    """
    common_allergens = [
        'gluten', 'dairy', 'eggs', 'nuts', 'tree_nuts', 'peanuts',
        'soy', 'fish', 'shellfish', 'sesame', 'sulfites'
    ]
    
    result = {}
    for allergen in common_allergens:
        result[allergen] = allergen in [a.lower().replace(' ', '_') for a in allergen_list]
    
    return result

def calculate_spice_emoji(spice_level: int) -> str:
    """
    Convert spice level to emoji representation.
    """
    if spice_level == 0:
        return ""
    elif spice_level == 1:
        return "🌶️"
    elif spice_level == 2:
        return "🌶️🌶️"
    elif spice_level == 3:
        return "🌶️🌶️🌶️"
    elif spice_level >= 4:
        return "🌶️🌶️🌶️🔥"
    else:
        return ""

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text for search and analysis.
    """
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    
    return list(set(keywords))  # Remove duplicates

def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format.
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    """
    try:
        return json.loads(json_string) if json_string else default
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON string.
    """
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def get_client_ip(request) -> str:
    """
    Extract client IP address from request.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if hasattr(request, 'client') else "unknown"

def log_performance(func):
    """
    Decorator to log function performance.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

def rate_limit_key(identifier: str, window: str = "1min") -> str:
    """
    Generate rate limiting key.
    """
    timestamp = datetime.now()
    
    if window == "1min":
        window_key = timestamp.strftime("%Y%m%d%H%M")
    elif window == "1hour":
        window_key = timestamp.strftime("%Y%m%d%H")
    elif window == "1day":
        window_key = timestamp.strftime("%Y%m%d")
    else:
        window_key = timestamp.strftime("%Y%m%d%H%M")
    
    return f"rate_limit:{identifier}:{window_key}"

class CacheManager:
    """
    Simple cache management utility.
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set cache value"""
        if not self.redis:
            return False
        
        try:
            serialized = safe_json_dumps(value)
            return self.redis.setex(key, expire, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        if not self.redis:
            return default
        
        try:
            value = self.redis.get(key)
            return safe_json_loads(value, default) if value else default
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete cache value"""
        if not self.redis:
            return False
        
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

class ConfigManager:
    """
    Configuration management utility.
    """
    
    def __init__(self):
        self.config = {
            'max_conversation_length': int(os.getenv('MAX_CONVERSATION_LENGTH', '50')),
            'session_timeout_minutes': int(os.getenv('SESSION_TIMEOUT_MINUTES', '30')),
            'rate_limit_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '100')),
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '10')),
            'ai_response_timeout': int(os.getenv('AI_RESPONSE_TIMEOUT', '30')),
            'cache_ttl_seconds': int(os.getenv('CACHE_TTL_SECONDS', '3600'))
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

# Global instances
config = ConfigManager()

def create_error_response(message: str, errors: List[str] = None) -> Dict[str, Any]:
    """
    Create standardized error response.
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or []
    }

def create_success_response(data: Any = None, message: str = "Operation successful") -> Dict[str, Any]:
    """
    Create standardized success response.
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": None
    }