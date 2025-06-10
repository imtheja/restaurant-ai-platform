from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from database.models import Restaurant, MenuCategory, MenuItem
from schemas import (
    Restaurant as RestaurantSchema,
    RestaurantCreate,
    RestaurantUpdate,
    MenuCategory as MenuCategorySchema,
    MenuItem as MenuItemSchema,
    APIResponse,
    HealthCheck
)
from utils import generate_slug, create_success_response, create_error_response
from services.restaurant_service import RestaurantService

router = APIRouter()

@router.get("/restaurants/{restaurant_slug}", response_model=APIResponse)
async def get_restaurant_by_slug(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    db: Session = Depends(get_db)
):
    """Get restaurant information by slug for public access"""
    try:
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_slug(restaurant_slug)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Convert to schema
        restaurant_data = RestaurantSchema.from_orm(restaurant)
        
        return create_success_response(
            data=restaurant_data.dict(),
            message="Restaurant retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/menu", response_model=APIResponse)
async def get_restaurant_menu(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    include_unavailable: bool = Query(False, description="Include unavailable items"),
    db: Session = Depends(get_db)
):
    """Get restaurant menu with optional filtering"""
    try:
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_slug(restaurant_slug)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Get menu data
        menu_data = service.get_restaurant_menu(
            restaurant.id,
            category_id=category_id,
            include_unavailable=include_unavailable
        )
        
        return create_success_response(
            data=menu_data,
            message="Menu retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/categories", response_model=APIResponse)
async def get_restaurant_categories(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    db: Session = Depends(get_db)
):
    """Get restaurant menu categories"""
    try:
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_slug(restaurant_slug)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        categories = service.get_menu_categories(restaurant.id)
        
        return create_success_response(
            data=[MenuCategorySchema.from_orm(cat).dict() for cat in categories],
            message="Categories retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/avatar", response_model=APIResponse)
async def get_restaurant_avatar_config(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    db: Session = Depends(get_db)
):
    """Get restaurant AI avatar configuration"""
    try:
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_slug(restaurant_slug)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        avatar_config = restaurant.avatar_config or {}
        
        # Ensure default avatar configuration
        default_config = {
            "name": "Assistant",
            "personality": "friendly_knowledgeable",
            "greeting": f"Welcome to {restaurant.name}! How can I help you today?",
            "tone": "warm",
            "special_instructions": ""
        }
        
        # Merge with existing config
        final_config = {**default_config, **avatar_config}
        
        return create_success_response(
            data=final_config,
            message="Avatar configuration retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_slug}/items/{item_id}", response_model=APIResponse)
async def get_menu_item_details(
    restaurant_slug: str = Path(..., description="Restaurant slug"),
    item_id: str = Path(..., description="Menu item ID"),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific menu item"""
    try:
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_slug(restaurant_slug)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Validate item_id format
        try:
            item_uuid = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item ID format")
        
        menu_item = service.get_menu_item_details(restaurant.id, item_uuid)
        
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return create_success_response(
            data=MenuItemSchema.from_orm(menu_item).dict(),
            message="Menu item retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/search/restaurants", response_model=APIResponse)
async def search_restaurants(
    q: str = Query(..., min_length=2, description="Search query"),
    cuisine_type: Optional[str] = Query(None, description="Filter by cuisine type"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Search restaurants by name, cuisine, or description"""
    try:
        service = RestaurantService(db)
        restaurants = service.search_restaurants(
            query=q,
            cuisine_type=cuisine_type,
            limit=limit
        )
        
        return create_success_response(
            data=[RestaurantSchema.from_orm(r).dict() for r in restaurants],
            message=f"Found {len(restaurants)} restaurants"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")