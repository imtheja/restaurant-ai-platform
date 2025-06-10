from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from schemas import (
    Conversation as ConversationSchema,
    APIResponse
)
from utils import create_success_response, create_error_response

router = APIRouter()

@router.get("/restaurants/{restaurant_slug}/conversations", response_model=APIResponse)
async def list_conversations(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    limit: int = Query(10, ge=1, le=100, description="Number of conversations"),
    db: Session = Depends(get_db)
):
    """List recent conversations for a restaurant"""
    try:
        # For now, return empty list - implement actual logic later
        return create_success_response(
            data=[],
            message="Conversations retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=APIResponse)
async def get_conversation(
    conversation_id: str = Path(..., description="Conversation ID"),
    db: Session = Depends(get_db)
):
    """Get conversation details with messages"""
    try:
        # Validate UUID format
        try:
            conv_uuid = uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation ID format")
        
        # For now, return empty conversation - implement actual logic later
        return create_success_response(
            data={"id": conversation_id, "messages": []},
            message="Conversation retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")