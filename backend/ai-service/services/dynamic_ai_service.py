"""
Dynamic AI Service
OpenAI-based service that adapts based on restaurant configuration
"""
import openai
import asyncio
import time
import json
import os
import tempfile
from typing import Dict, List, AsyncIterator, Optional, Any, Tuple
import redis

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.ai_config import RestaurantAIConfig, AIConfigManager, AIMode, ModelType

class DynamicAIService:
    """AI service that adapts based on restaurant configuration"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        # OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        self.api_key_available = bool(
            api_key and 
            not api_key.startswith("your_") and 
            api_key != "sk-fake-key-for-development-only" and
            len(api_key) > 20
        )
        
        if self.api_key_available:
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            self.openai_client = None
        
        # Redis for caching
        self.redis_client = redis_client
        
        # Token costs (per 1K tokens)
        self.token_costs = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
        }
    
    async def get_restaurant_config(self, restaurant_id: str) -> RestaurantAIConfig:
        """
        Get AI configuration for a restaurant
        Falls back to default if not found
        """
        try:
            if self.redis_client:
                # Try to get from cache first
                cache_key = f"ai_config:{restaurant_id}"
                cached_config = self.redis_client.get(cache_key)
                
                if cached_config:
                    return RestaurantAIConfig.from_json(cached_config.decode())
            
            # TODO: Get from database when we implement restaurant config storage
            # For now, return default based on TEXT_ONLY_MODE env var
            text_only_mode = os.getenv("TEXT_ONLY_MODE", "false").lower() == "true"
            
            if text_only_mode:
                return AIConfigManager.get_default_config()
            else:
                return AIConfigManager.get_hybrid_config()
                
        except Exception as e:
            print(f"Error getting restaurant config: {e}")
            return AIConfigManager.get_default_config()
    
    async def update_restaurant_config(
        self, 
        restaurant_id: str, 
        config: RestaurantAIConfig
    ) -> bool:
        """Update AI configuration for a restaurant"""
        try:
            # Validate configuration
            is_valid, error = AIConfigManager.validate_config(config)
            if not is_valid:
                print(f"Invalid config: {error}")
                return False
            
            if self.redis_client:
                # Cache the configuration
                cache_key = f"ai_config:{restaurant_id}"
                self.redis_client.setex(
                    cache_key, 
                    3600,  # 1 hour cache
                    config.to_json()
                )
            
            # TODO: Save to database when we implement restaurant config storage
            
            return True
            
        except Exception as e:
            print(f"Error updating restaurant config: {e}")
            return False
    
    async def generate_response(
        self,
        restaurant_id: str,
        messages: List[Dict[str, str]],
        context: Dict[str, Any],
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate AI response based on restaurant configuration"""
        
        # Get restaurant configuration
        config = await self.get_restaurant_config(restaurant_id)
        
        # Check if streaming is enabled
        if stream and not config.performance.streaming_enabled:
            stream = False
        
        try:
            # Format messages with context
            formatted_messages = await self._format_messages_with_context(
                messages, 
                context, 
                config
            )
            
            # Check for cached response
            if config.performance.cache_responses:
                cached_response = await self._get_cached_response(
                    restaurant_id, 
                    formatted_messages[-1]["content"]
                )
                if cached_response:
                    yield cached_response
                    return
            
            # Generate response using OpenAI
            if not self.api_key_available:
                yield self._get_fallback_response(formatted_messages[-1]["content"])
                return
            
            # Prepare OpenAI request
            request_params = {
                "model": config.model.model.value,
                "messages": formatted_messages,
                "max_tokens": config.model.max_tokens,
                "temperature": config.model.temperature,
                "stream": stream
            }
            
            if stream:
                # Streaming response
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    **request_params
                )
                
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response += token
                        yield token
                
                # Cache the full response
                if config.performance.cache_responses and full_response:
                    await self._cache_response(
                        restaurant_id, 
                        formatted_messages[-1]["content"], 
                        full_response
                    )
            else:
                # Non-streaming response
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    **request_params
                )
                
                content = response.choices[0].message.content or ""
                
                # Cache the response
                if config.performance.cache_responses and content:
                    await self._cache_response(
                        restaurant_id, 
                        formatted_messages[-1]["content"], 
                        content
                    )
                
                yield content
                
        except Exception as e:
            print(f"Error generating response: {e}")
            yield f"I apologize, but I'm having trouble responding right now. Please try again."
    
    async def generate_speech(
        self,
        restaurant_id: str,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """Generate speech if enabled for the restaurant"""
        
        # Get restaurant configuration
        config = await self.get_restaurant_config(restaurant_id)
        
        # Check if speech synthesis is enabled
        if not config.is_speech_enabled() or not config.speech.synthesis_enabled:
            # Return silent audio
            return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        # Use configured voice or fallback
        voice_to_use = voice or config.speech.default_voice
        
        try:
            if not self.api_key_available:
                return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            
            response = await asyncio.to_thread(
                self.openai_client.audio.speech.create,
                model="tts-1",
                voice=voice_to_use,
                input=text.strip(),
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Speech generation error: {e}")
            return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    async def transcribe_audio(
        self,
        restaurant_id: str,
        audio_data: bytes
    ) -> str:
        """Transcribe audio if enabled for the restaurant"""
        
        # Get restaurant configuration
        config = await self.get_restaurant_config(restaurant_id)
        
        # Check if speech recognition is enabled
        if not config.is_speech_enabled() or not config.speech.recognition_enabled:
            return "Speech recognition is not enabled for this restaurant."
        
        try:
            if not self.api_key_available:
                return "Speech recognition is not available in development mode."
            
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Transcribe using Whisper
                with open(temp_file.name, 'rb') as audio_file:
                    transcript = await asyncio.to_thread(
                        self.openai_client.audio.transcriptions.create,
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return transcript.text
                
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            return f"Transcription error: {str(e)}"
    
    async def get_frontend_config(self, restaurant_id: str) -> Dict[str, Any]:
        """Get configuration for frontend consumption"""
        config = await self.get_restaurant_config(restaurant_id)
        return config.get_frontend_config()
    
    def get_available_voices(self, restaurant_id: Optional[str] = None) -> List[Dict[str, str]]:
        """Get available voices (OpenAI TTS voices)"""
        return [
            {
                "id": "alloy",
                "name": "Alloy",
                "description": "Female voice, natural and versatile",
                "gender": "female",
                "recommended_for": "general_purpose"
            },
            {
                "id": "echo",
                "name": "Echo", 
                "description": "Male voice, clear and professional",
                "gender": "male",
                "recommended_for": "professional_announcements"
            },
            {
                "id": "fable",
                "name": "Fable",
                "description": "Male voice, warm and storytelling",
                "gender": "male",
                "recommended_for": "friendly_conversations"
            },
            {
                "id": "onyx",
                "name": "Onyx",
                "description": "Male voice, deep and authoritative",
                "gender": "male",
                "recommended_for": "formal_interactions"
            },
            {
                "id": "nova",
                "name": "Nova",
                "description": "Female voice, young and energetic",
                "gender": "female",
                "recommended_for": "bakery_assistant"
            },
            {
                "id": "shimmer",
                "name": "Shimmer",
                "description": "Female voice, soft and gentle",
                "gender": "female",
                "recommended_for": "calm_interactions"
            }
        ]
    
    async def _format_messages_with_context(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any],
        config: RestaurantAIConfig
    ) -> List[Dict[str, str]]:
        """Format messages with restaurant context"""
        
        # Build system prompt
        system_prompt = config.model.system_prompt_override or self._build_system_prompt(context)
        
        # Start with system message
        formatted_messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation messages (limit based on config)
        recent_messages = messages[-config.model.context_messages:]
        formatted_messages.extend(recent_messages)
        
        return formatted_messages
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt from restaurant context"""
        restaurant_info = context.get('restaurant', {})
        menu_context = context.get('menu_context', {})
        
        prompt = f"""You are an AI assistant for {restaurant_info.get('name', 'this restaurant')}.

Restaurant Information:
- Name: {restaurant_info.get('name', 'N/A')}
- Cuisine: {restaurant_info.get('cuisine_type', 'N/A')}
- Description: {restaurant_info.get('description', 'N/A')}

Your role is to help customers with menu questions, recommendations, ingredients, allergens, and ordering decisions.
Be friendly, knowledgeable, and helpful. Keep responses concise but informative.

Menu Context:
{json.dumps(menu_context, indent=2) if menu_context else 'Menu information not available.'}

Always prioritize food safety when discussing allergens and ingredients."""
        
        return prompt
    
    async def _get_cached_response(
        self, 
        restaurant_id: str, 
        message: str
    ) -> Optional[str]:
        """Get cached response if available"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"response_cache:{restaurant_id}:{hash(message.lower())}"
            cached = self.redis_client.get(cache_key)
            return cached.decode() if cached else None
        except Exception:
            return None
    
    async def _cache_response(
        self, 
        restaurant_id: str, 
        message: str, 
        response: str
    ) -> None:
        """Cache response for future use"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"response_cache:{restaurant_id}:{hash(message.lower())}"
            # Cache for 1 hour
            self.redis_client.setex(cache_key, 3600, response)
        except Exception:
            pass
    
    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when OpenAI is not available"""
        common_responses = {
            "hello": "Hello! Welcome to our restaurant. How can I help you today?",
            "hi": "Hi there! I'm here to help you with our menu. What would you like to know?",
            "menu": "I'd love to help you with our menu, but I'm currently in demo mode. Please check back later!",
            "ingredients": "I can help with ingredient questions, but I'm currently in demo mode.",
            "allergens": "For allergen information, I'm currently in demo mode. Please ask your server for detailed allergen info."
        }
        
        message_lower = message.lower().strip()
        for key, response in common_responses.items():
            if key in message_lower:
                return response
        
        return "I'm currently in demo mode. Please try again later or ask your server for assistance!"