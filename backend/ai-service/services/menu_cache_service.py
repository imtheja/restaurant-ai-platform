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
        
        # Common greetings and responses for instant reply
        self.instant_responses = {
            # Greetings
            "hello": "Hello! Welcome to The Cookie Jar! I'm Baker Betty, your cookie expert. What delicious treat can I help you find today?",
            "hi": "Hi there! Welcome to The Cookie Jar! What kind of cookie are you craving today?",
            "hey": "Hey! Great to see you at The Cookie Jar! What can I get for you today?",
            "good morning": "Good morning! Welcome to The Cookie Jar! Nothing beats fresh cookies to start your day. What would you like?",
            "good afternoon": "Good afternoon! Welcome to The Cookie Jar! Ready for a sweet treat?",
            "good evening": "Good evening! Welcome to The Cookie Jar! How about a delicious cookie to end your day?",
            
            # Common questions
            "what do you have": "We have an amazing selection of cookies! Our menu includes Classic Chocolate Chip, Double Chocolate Chip, Oatmeal Raisin, Peanut Butter, Sugar Cookies, and many more specialty options. What type of cookie are you in the mood for?",
            "what's popular": "Our most popular cookies are the Classic Chocolate Chip and Double Chocolate Chip! The Chocolate Chip is a timeless favorite with semi-sweet chocolate chips, while the Double Chocolate is perfect for serious chocolate lovers. Would you like to try one of these?",
            "what's your best seller": "Our Classic Chocolate Chip Cookie is our all-time best seller! It's made with premium butter, semi-sweet chocolate chips, and baked to perfection. Would you like to try one?",
            "do you have chocolate": "Yes! We have several chocolate options: Classic Chocolate Chip, Double Chocolate Chip, Chocolate Peanut Butter Chip, and White Chocolate Macadamia. Which one sounds good to you?",
            
            # Closing
            "thank you": "You're very welcome! Enjoy your delicious cookies! Have a wonderful day!",
            "thanks": "My pleasure! Enjoy your treats!",
            "bye": "Goodbye! Thanks for visiting The Cookie Jar! Come back soon!",
            "goodbye": "Goodbye! It was lovely helping you today. Enjoy your cookies!"
        }
        
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
        key_data = f"restaurant:{restaurant_id}:menu_question:{question_type}:{item_id}"
        return key_data
        
    def _generate_instant_response_key(self, restaurant_id: str, message_key: str) -> str:
        """Generate cache key for instant responses"""
        return f"restaurant:{restaurant_id}:instant:{message_key}"

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

    def _check_instant_response(self, message: str) -> Optional[str]:
        """Check for instant responses to common greetings/questions"""
        message_lower = message.lower().strip()
        
        # Direct match
        if message_lower in self.instant_responses:
            return self.instant_responses[message_lower]
        
        # Fuzzy match for variations
        for key, response in self.instant_responses.items():
            if key in message_lower or message_lower in key:
                return response
                
        return None

    async def get_cached_response(self, restaurant_id: str, message: str) -> Optional[str]:
        """Check if we have a cached response for this question"""
        try:
            # First check instant responses (no Redis lookup needed)
            instant_response = self._check_instant_response(message)
            if instant_response:
                return instant_response
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
            # Updated pattern to match new key structure
            pattern = f"restaurant:{restaurant_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Restaurant cache invalidation error: {e}")