from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from schemas import (
    ChatRequest,
    ChatResponse,
    APIResponse
)
from utils import create_success_response, create_error_response
from services.ai_service import AIService

router = APIRouter()


@router.post("/restaurants/{restaurant_slug}/chat", response_model=APIResponse)
async def chat_with_ai(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    chat_request: ChatRequest = ...,
    db: Session = Depends(get_db)
):
    """Send a message to the AI assistant for a specific restaurant"""
    try:
        service = AIService(db)
        
        # Get or create conversation
        conversation = service.get_or_create_conversation(
            restaurant_slug=restaurant_slug,
            session_id=chat_request.session_id,
            context=chat_request.context
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Process AI response
        ai_response = await service.process_chat_message(
            conversation=conversation,
            message=chat_request.message,
            context=chat_request.context
        )
        
        return create_success_response(
            data=ai_response,
            message="Chat response generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/restaurants/{restaurant_slug}/chat/stream")
async def chat_with_ai_stream(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    chat_request: ChatRequest = ...,
    db: Session = Depends(get_db)
):
    """Stream AI response for real-time conversation"""
    try:
        service = AIService(db)
        
        # Get or create conversation
        conversation = service.get_or_create_conversation(
            restaurant_slug=restaurant_slug,
            session_id=chat_request.session_id,
            context=chat_request.context
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Stream AI response
        async def generate_stream():
            async for chunk in service.process_chat_message_stream(
                conversation=conversation,
                message=chat_request.message,
                context=chat_request.context
            ):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/chat/suggestions", response_model=APIResponse)
async def get_chat_suggestions(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    context: str = None,
    db: Session = Depends(get_db)
):
    """Get conversation starter suggestions for a restaurant"""
    try:
        service = AIService(db)
        
        suggestions = await service.get_conversation_suggestions(
            restaurant_slug=restaurant_slug,
            context=context
        )
        
        return create_success_response(
            data={"suggestions": suggestions},
            message="Suggestions retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/restaurants/{restaurant_slug}/chat/feedback", response_model=APIResponse)
async def submit_chat_feedback(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    feedback_data: dict = ...,
    db: Session = Depends(get_db)
):
    """Submit feedback about chat interaction"""
    try:
        service = AIService(db)
        
        success = service.record_chat_feedback(
            restaurant_slug=restaurant_slug,
            feedback_data=feedback_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return create_success_response(
            message="Feedback recorded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/chat/analytics", response_model=APIResponse)
async def get_chat_analytics(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get chat analytics for a restaurant"""
    try:
        service = AIService(db)
        
        analytics = service.get_chat_analytics(
            restaurant_slug=restaurant_slug,
            days=days
        )
        
        return create_success_response(
            data=analytics,
            message="Chat analytics retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")