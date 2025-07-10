"""
Dynamic Chat Router
Handles chat interactions with dynamic AI configuration
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import asyncio
import redis

# Add shared module to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db, get_redis_client
from schemas import APIResponse
from utils import create_success_response, create_error_response

from services.dynamic_ai_service import DynamicAIService
from config.ai_config import RestaurantAIConfig, AIConfigManager, AIMode

router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=100)
    context: Optional[Dict[str, Any]] = {}

class ConfigUpdateRequest(BaseModel):
    mode: str = Field(..., description="AI mode: text_only, speech_enabled, or hybrid")
    speech_synthesis: bool = False
    speech_recognition: bool = False
    default_voice: str = "nova"
    voice_selection_enabled: bool = False
    max_tokens: int = Field(150, ge=10, le=1000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    streaming_enabled: bool = True
    cache_responses: bool = True

# Global service instance
ai_service: Optional[DynamicAIService] = None

def get_ai_service(redis_client: redis.Redis = Depends(get_redis_client)) -> DynamicAIService:
    """Get or create AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = DynamicAIService(redis_client=redis_client)
    return ai_service

@router.get("/restaurants/{restaurant_slug}/ai/config")
async def get_ai_config(
    restaurant_slug: str,
    service: DynamicAIService = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """Get AI configuration for a restaurant"""
    try:
        # TODO: Get restaurant_id from restaurant_slug via database
        # For now, use restaurant_slug as restaurant_id
        restaurant_id = restaurant_slug
        
        config = await service.get_frontend_config(restaurant_id)
        
        return create_success_response(
            data=config,
            message="AI configuration retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI config: {str(e)}")

@router.put("/restaurants/{restaurant_slug}/ai/config")
async def update_ai_config(
    restaurant_slug: str,
    config_request: ConfigUpdateRequest,
    service: DynamicAIService = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """Update AI configuration for a restaurant"""
    try:
        # TODO: Get restaurant_id from restaurant_slug via database
        # For now, use restaurant_slug as restaurant_id
        restaurant_id = restaurant_slug
        
        # Convert request to config object
        ai_mode = AIMode(config_request.mode)
        
        config = AIConfigManager.get_default_config()
        config.mode = ai_mode
        config.speech.synthesis_enabled = config_request.speech_synthesis
        config.speech.recognition_enabled = config_request.speech_recognition
        config.speech.default_voice = config_request.default_voice
        config.speech.voice_selection_enabled = config_request.voice_selection_enabled
        config.model.max_tokens = config_request.max_tokens
        config.model.temperature = config_request.temperature
        config.performance.streaming_enabled = config_request.streaming_enabled
        config.performance.cache_responses = config_request.cache_responses
        
        # Update configuration
        success = await service.update_restaurant_config(restaurant_id, config)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid configuration")
        
        return create_success_response(
            data=await service.get_frontend_config(restaurant_id),
            message="AI configuration updated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI config: {str(e)}")

@router.post("/restaurants/{restaurant_slug}/chat")
async def chat(
    restaurant_slug: str,
    chat_request: ChatMessage,
    service: DynamicAIService = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """Send a chat message (non-streaming)"""
    try:
        # TODO: Get restaurant and conversation from database
        restaurant_id = restaurant_slug
        
        # Mock conversation context for now
        context = {
            "restaurant": {
                "name": "Chip Cookies",
                "cuisine_type": "Gourmet Cookie Shop",
                "description": "Warm fresh gourmet cookies delivered to your door"
            },
            "menu_context": {
                "categories": ["Signature Cookies", "Specialty Cookies", "Beverages"],
                "featured_items": ["OG Chip", "Boneless", "Oreo Dunk Chip"]
            }
        }
        
        # Format messages
        messages = [{"role": "user", "content": chat_request.message}]
        
        # Generate response
        response_generator = service.generate_response(
            restaurant_id=restaurant_id,
            messages=messages,
            context={**context, **chat_request.context},
            stream=False
        )
        
        # Get the response
        response_content = ""
        async for token in response_generator:
            response_content += token
        
        return create_success_response(
            data={
                "response": response_content,
                "session_id": chat_request.session_id
            },
            message="Chat response generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/restaurants/{restaurant_slug}/chat/stream")
async def chat_stream(
    restaurant_slug: str,
    chat_request: ChatMessage,
    service: DynamicAIService = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """Send a chat message (streaming)"""
    try:
        # TODO: Get restaurant and conversation from database
        restaurant_id = restaurant_slug
        
        # Mock conversation context for now
        context = {
            "restaurant": {
                "name": "Chip Cookies",
                "cuisine_type": "Gourmet Cookie Shop",
                "description": "Warm fresh gourmet cookies delivered to your door"
            },
            "menu_context": {
                "categories": ["Signature Cookies", "Specialty Cookies", "Modifiers"],
                "featured_items": ["OG Chip", "Boneless", "Oreo Dunk Chip"]
            }
        }
        
        # Format messages
        messages = [{"role": "user", "content": chat_request.message}]
        
        async def generate_stream():
            """Generate streaming response"""
            try:
                response_generator = service.generate_response(
                    restaurant_id=restaurant_id,
                    messages=messages,
                    context={**context, **chat_request.context},
                    stream=True
                )
                
                async for token in response_generator:
                    if token:
                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat stream error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/ai/voices")
async def get_available_voices(
    restaurant_slug: str,
    service: DynamicAIService = Depends(get_ai_service)
):
    """Get available voices for the restaurant"""
    try:
        # TODO: Get restaurant_id from restaurant_slug via database
        restaurant_id = restaurant_slug
        
        voices = service.get_available_voices(restaurant_id)
        
        return create_success_response(
            data={"voices": voices},
            message="Available voices retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/ai/health")
async def ai_health_check(
    restaurant_slug: str,
    service: DynamicAIService = Depends(get_ai_service)
):
    """Check AI service health for the restaurant"""
    try:
        # TODO: Get restaurant_id from restaurant_slug via database
        restaurant_id = restaurant_slug
        
        config = await service.get_restaurant_config(restaurant_id)
        
        return create_success_response(
            data={
                "status": "healthy",
                "api_available": service.api_key_available,
                "mode": config.mode.value,
                "speech_enabled": config.is_speech_enabled()
            },
            message="AI service is healthy"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Backward compatibility endpoint
@router.get("/speech/config")
async def get_speech_config_legacy(
    service: DynamicAIService = Depends(get_ai_service)
):
    """Legacy endpoint for speech configuration"""
    try:
        # Use default restaurant for legacy support
        config = await service.get_restaurant_config("default")
        
        return create_success_response(
            data={
                "text_only_mode": config.mode == AIMode.TEXT_ONLY,
                "api_available": service.api_key_available,
                "speech_synthesis_enabled": config.speech.synthesis_enabled,
                "speech_recognition_enabled": config.speech.recognition_enabled
            },
            message="Speech configuration retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get speech config: {str(e)}")