from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from schemas import (
    Ingredient as IngredientSchema,
    IngredientCreate,
    IngredientUpdate,
    APIResponse
)
from utils import create_success_response, create_error_response

router = APIRouter()

@router.get("/ingredients", response_model=APIResponse)
async def list_ingredients(
    search: Optional[str] = Query(None, description="Search ingredients by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db)
):
    """List ingredients with optional filtering"""
    try:
        # For now, return empty list - implement actual logic later
        return create_success_response(
            data=[],
            message="Ingredients retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/ingredients", response_model=APIResponse)
async def create_ingredient(
    ingredient_data: IngredientCreate,
    db: Session = Depends(get_db)
):
    """Create a new ingredient"""
    try:
        # For now, return mock response - implement actual logic later
        return create_success_response(
            data={"id": "new-ingredient-id", "name": ingredient_data.name},
            message="Ingredient created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")