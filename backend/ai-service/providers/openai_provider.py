"""
OpenAI Provider Implementation
Handles OpenAI API integration with the standardized interface
"""
import openai
import time
import hashlib
from typing import Dict, List, AsyncIterator, Optional, Any
import tempfile
import os
import asyncio

from .base import BaseAIProvider, AIMessage, AIResponse, AIProviderConfig

class OpenAIProvider(BaseAIProvider):
    """OpenAI implementation of the AI provider interface"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.api_endpoint
        )
        
        # Token costs per model (per 1K tokens)
        self.token_costs = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
        }
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate response using OpenAI API"""
        try:
            start_time = time.time()
            
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": openai_messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": stream
            }
            
            # Add extra parameters if provided
            if self.config.extra_params:
                request_params.update(self.config.extra_params)
            
            if stream:
                # Streaming response
                async def stream_response():
                    try:
                        response = await asyncio.to_thread(
                            self.client.chat.completions.create,
                            **request_params
                        )
                        
                        for chunk in response:
                            if chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                    except Exception as e:
                        yield f"Error: {str(e)}"
                
                async for token in stream_response():
                    yield token
            else:
                # Non-streaming response
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    **request_params
                )
                
                yield response.choices[0].message.content or ""
                
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    async def generate_speech(
        self, 
        text: str, 
        voice: str = "nova"
    ) -> bytes:
        """Generate speech using OpenAI TTS"""
        try:
            # Clean text for speech synthesis
            clean_text = text.strip()
            if not clean_text:
                # Return silent audio for empty text
                return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            
            response = await asyncio.to_thread(
                self.client.audio.speech.create,
                model="tts-1",
                voice=voice,
                input=clean_text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Speech generation error: {e}")
            # Return silent audio on error
            return b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    async def transcribe_audio(
        self, 
        audio_data: bytes
    ) -> str:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Transcribe using Whisper
                with open(temp_file.name, 'rb') as audio_file:
                    transcript = await asyncio.to_thread(
                        self.client.audio.transcriptions.create,
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
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get OpenAI TTS voices"""
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        model_info = {
            "provider": "openai",
            "model": self.model_name,
            "capabilities": {
                "text_generation": True,
                "speech_synthesis": True,
                "speech_recognition": True,
                "streaming": True,
                "function_calling": True
            },
            "limits": {
                "max_tokens": self.config.max_tokens,
                "context_window": self._get_context_window(),
                "rate_limits": "Varies by tier"
            },
            "costs": self.token_costs.get(self.model_name, {})
        }
        
        return model_info
    
    def _get_context_window(self) -> int:
        """Get context window size for the model"""
        context_windows = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385
        }
        
        return context_windows.get(self.model_name, 4096)
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        try:
            # Check if API key is provided
            if not self.config.api_key or self.config.api_key.startswith("your_"):
                return False
            
            # Check if model is supported
            supported_models = list(self.token_costs.keys())
            if self.model_name not in supported_models:
                print(f"Warning: Model {self.model_name} not in supported list: {supported_models}")
            
            # Try to make a simple API call to validate
            test_client = openai.OpenAI(api_key=self.config.api_key)
            test_client.models.list()
            
            return True
            
        except Exception as e:
            print(f"OpenAI config validation error: {e}")
            return False
    
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """Calculate cost for OpenAI API usage"""
        costs = self.token_costs.get(self.model_name, {"input": 0.001, "output": 0.002})
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost