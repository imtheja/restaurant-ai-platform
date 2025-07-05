import redis
import hashlib
import json
import re
import os
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import MenuItem, MenuCategory, Restaurant

class MenuCacheService:
    """Redis caching service for common menu questions"""
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Cache TTL (24 hours)
        self.cache_ttl = 24 * 60 * 60
        
        # Question patterns that are cacheable
        self.cacheable_patterns = {
            'description': [
                r'tell me about (?:the )?(.+)',
                r'what is (?:the )?(.+)',
                r'describe (?:the )?(.+)',
                r'(?:what )?about (?:the )?(.+)',
            ],
            'ingredients': [
                r'what (?:are )?(?:the )?ingredients (?:in )?(?:the )?(.+)',
                r'(?:what )?(?:is )?(?:in )?(?:the )?(.+) (?:made )?(?:of|with)',
                r'(?:what )?(?:are )?(?:the )?contents (?:of )?(?:the )?(.+)',
            ],
            'allergens': [
                r'(?:does )?(?:the )?(.+) (?:contain|have) (?:any )?(.+)',
                r'(?:is )?(?:the )?(.+) (?:safe )?(?:for )?(.+)',
                r'(?:any )?allergens (?:in )?(?:the )?(.+)',
            ],
            'price': [
                r'how much (?:does )?(?:is )?(?:the )?(.+) (?:cost)?',
                r'(?:what )?(?:is )?(?:the )?price (?:of )?(?:the )?(.+)',
                r'(?:how )?(?:much )?(?:for )?(?:the )?(.+)',
            ],
            'preparation': [
                r'how long (?:does )?(?:the )?(.+) (?:take)',
                r'(?:what )?(?:is )?(?:the )?preparation time (?:for )?(?:the )?(.+)',
                r'(?:how )?(?:long )?(?:to )?(?:make )?(?:the )?(.+)',
            ]
        }

    def _normalize_item_name(self, item_name: str) -> str:
        """Normalize item name for matching"""
        return re.sub(r'[^\w\s]', '', item_name.lower().strip())

    def _find_menu_item(self, restaurant_id: str, item_name: str) -> Optional[MenuItem]:
        """Find menu item by name with fuzzy matching"""
        normalized_search = self._normalize_item_name(item_name)
        
        # First try exact match
        item = self.db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True,
            func.lower(MenuItem.name) == normalized_search
        ).first()
        
        if item:
            return item
            
        # Then try partial match
        items = self.db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True
        ).all()
        
        for item in items:
            normalized_item = self._normalize_item_name(item.name)
            if normalized_search in normalized_item or normalized_item in normalized_search:
                return item
                
        return None

    def _classify_question(self, message: str) -> Optional[tuple]:
        """Classify question type and extract item name"""
        message_lower = message.lower().strip()
        
        for question_type, patterns in self.cacheable_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    item_name = match.group(1).strip()
                    return question_type, item_name
                    
        return None

    def _generate_cache_key(self, restaurant_id: str, question_type: str, item_id: str) -> str:
        """Generate cache key for the question"""
        key_data = f"menu_question:{restaurant_id}:{question_type}:{item_id}"
        return key_data

    def _generate_deterministic_response(self, question_type: str, item: MenuItem) -> Optional[str]:
        """Generate deterministic response for cacheable questions"""
        try:
            if question_type == 'description':
                response = f"{item.name} - {item.description}"
                if item.price:
                    response += f" This delicious item is priced at ${item.price:.2f}."
                if item.is_signature:
                    response += " This is one of our signature items!"
                return response
                
            elif question_type == 'ingredients':
                if item.ingredients:
                    ingredient_names = [ing.ingredient.name for ing in item.ingredients if ing.ingredient.is_active]
                    if ingredient_names:
                        return f"The {item.name} contains: {', '.join(ingredient_names)}."
                return f"I don't have the specific ingredient list for {item.name} available right now."
                
            elif question_type == 'allergens':
                if item.allergen_info:
                    allergens = ', '.join(item.allergen_info)
                    return f"The {item.name} contains the following allergens: {allergens}. Please let us know if you have any specific allergies!"
                return f"I don't have specific allergen information for {item.name}. Please let our staff know about any allergies."
                
            elif question_type == 'price':
                if item.price:
                    return f"The {item.name} costs ${item.price:.2f}."
                return f"I don't have the current price for {item.name}. Please check with our staff."
                
            elif question_type == 'preparation':
                if item.preparation_time:
                    return f"The {item.name} takes approximately {item.preparation_time} minutes to prepare."
                return f"I don't have the specific preparation time for {item.name}."
                
        except Exception as e:
            print(f"Error generating response for {question_type}: {e}")
            
        return None

    async def get_cached_response(self, restaurant_id: str, message: str) -> Optional[str]:
        """Check if we have a cached response for this question"""
        try:
            # Classify the question
            classification = self._classify_question(message)
            if not classification:
                return None
                
            question_type, item_name = classification
            
            # Find the menu item
            item = self._find_menu_item(restaurant_id, item_name)
            if not item:
                return None
                
            # Check cache
            cache_key = self._generate_cache_key(restaurant_id, question_type, str(item.id))
            cached_response = self.redis_client.get(cache_key)
            
            if cached_response:
                return cached_response
                
            # Generate and cache response
            response = self._generate_deterministic_response(question_type, item)
            if response:
                self.redis_client.setex(cache_key, self.cache_ttl, response)
                return response
                
        except Exception as e:
            print(f"Cache lookup error: {e}")
            
        return None

    def invalidate_item_cache(self, restaurant_id: str, item_id: str):
        """Invalidate all cached responses for a specific menu item"""
        try:
            for question_type in self.cacheable_patterns.keys():
                cache_key = self._generate_cache_key(restaurant_id, question_type, item_id)
                self.redis_client.delete(cache_key)
        except Exception as e:
            print(f"Cache invalidation error: {e}")

    def invalidate_restaurant_cache(self, restaurant_id: str):
        """Invalidate all cached responses for a restaurant"""
        try:
            pattern = f"menu_question:{restaurant_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Restaurant cache invalidation error: {e}")