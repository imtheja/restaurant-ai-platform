import redis
import os
import asyncio
import hashlib
from typing import Optional, Dict, Any
import openai

class AudioCacheService:
    """Service to pre-cache audio for common responses"""
    
    def __init__(self):
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("your_"):
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            
        # Cache TTL (7 days for audio)
        self.cache_ttl = 7 * 24 * 60 * 60
        
    def _generate_audio_cache_key(self, restaurant_id: str, text: str, voice: str = "nova") -> str:
        """Generate cache key for audio"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"restaurant:{restaurant_id}:audio_cache:{voice}:{text_hash}"
        
    async def get_cached_audio(self, restaurant_id: str, text: str, voice: str = "nova") -> Optional[bytes]:
        """Get cached audio for text"""
        try:
            cache_key = self._generate_audio_cache_key(restaurant_id, text, voice)
            cached_audio = self.redis_client.get(cache_key)
            return cached_audio
        except Exception as e:
            print(f"Error getting cached audio: {e}")
            return None
            
    async def cache_audio(self, restaurant_id: str, text: str, audio_data: bytes, voice: str = "nova"):
        """Cache audio data"""
        try:
            cache_key = self._generate_audio_cache_key(restaurant_id, text, voice)
            self.redis_client.setex(cache_key, self.cache_ttl, audio_data)
        except Exception as e:
            print(f"Error caching audio: {e}")
            
    async def generate_and_cache_audio(self, restaurant_id: str, text: str, voice: str = "nova") -> Optional[bytes]:
        """Generate audio and cache it"""
        if not self.openai_client:
            return None
            
        try:
            # Check cache first
            cached = await self.get_cached_audio(restaurant_id, text, voice)
            if cached:
                return cached
                
            # Generate new audio
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # Fast model
                voice=voice,
                input=text,
                response_format="mp3",
                speed=1.0
            )
            
            audio_data = response.content
            
            # Cache for future use
            await self.cache_audio(restaurant_id, text, audio_data, voice)
            
            return audio_data
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
            
    async def warmup_common_responses(self, restaurant_id: str, restaurant_name: str):
        """Pre-generate and cache audio for common responses"""
        # Customize responses with restaurant name
        common_responses = [
            # Greetings
            f"Hello! Welcome to {restaurant_name}! I'm your cookie expert. What delicious treat can I help you find today?",
            f"Hi there! Welcome to {restaurant_name}! What kind of cookie are you craving today?",
            f"Good morning! Welcome to {restaurant_name}! Nothing beats fresh cookies to start your day. What would you like?",
            
            # Common responses
            "Our Classic Chocolate Chip Cookie is our all-time best seller! It's made with premium butter, semi-sweet chocolate chips, and baked to perfection. Would you like to try one?",
            "Yes! We have several chocolate options: Classic Chocolate Chip, Double Chocolate Chip, Chocolate Peanut Butter Chip, and White Chocolate Macadamia. Which one sounds good to you?",
            "You're very welcome! Enjoy your delicious cookies! Have a wonderful day!",
            
            # Quick confirmations
            "Sure! Let me help you with that.",
            "Absolutely! That's a great choice.",
            "Of course! I'd be happy to help.",
        ]
        
        print("Starting audio cache warmup...")
        
        for response in common_responses:
            try:
                await self.generate_and_cache_audio(restaurant_id, response, "nova")
                await asyncio.sleep(0.1)  # Small delay to avoid rate limits
            except Exception as e:
                print(f"Error warming up audio for response: {e}")
                
        print(f"Audio cache warmup completed for restaurant {restaurant_id}!")