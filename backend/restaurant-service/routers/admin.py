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
    Restaurant as RestaurantSchema,
    RestaurantCreate,
    RestaurantUpdate,
    AvatarConfig,
    AvatarUpdate,
    MenuCategory as MenuCategorySchema,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    APIResponse,
    PaginatedResponse
)
from utils import create_success_response, create_error_response, generate_slug
from services.restaurant_service import RestaurantService

router = APIRouter()

# Restaurant CRUD operations
@router.post("/restaurants", response_model=APIResponse)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: Session = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        service = RestaurantService(db)
        
        # Generate slug if not provided
        if not hasattr(restaurant_data, 'slug') or not restaurant_data.slug:
            restaurant_data.slug = generate_slug(restaurant_data.name)
        
        # Check if slug already exists
        existing = service.get_restaurant_by_slug(restaurant_data.slug)
        if existing:
            raise HTTPException(status_code=400, detail="Restaurant slug already exists")
        
        restaurant = service.create_restaurant(restaurant_data)
        
        return create_success_response(
            data=RestaurantSchema.from_orm(restaurant).dict(),
            message="Restaurant created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants", response_model=APIResponse)
async def list_restaurants(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Only show active restaurants"),
    db: Session = Depends(get_db)
):
    """List all restaurants with pagination"""
    try:
        service = RestaurantService(db)
        restaurants, total = service.list_restaurants(
            page=page,
            per_page=per_page,
            active_only=active_only
        )
        
        return {
            "success": True,
            "message": "Restaurants retrieved successfully",
            "data": [RestaurantSchema.from_orm(r).dict() for r in restaurants],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}", response_model=APIResponse)
async def get_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    db: Session = Depends(get_db)
):
    """Get restaurant by ID"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        restaurant = service.get_restaurant_by_id(restaurant_uuid)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return create_success_response(
            data=RestaurantSchema.from_orm(restaurant).dict(),
            message="Restaurant retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/restaurants/{restaurant_id}", response_model=APIResponse)
async def update_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    restaurant_data: RestaurantUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update restaurant information"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        restaurant = service.update_restaurant(restaurant_uuid, restaurant_data)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return create_success_response(
            data=RestaurantSchema.from_orm(restaurant).dict(),
            message="Restaurant updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/restaurants/{restaurant_id}", response_model=APIResponse)
async def delete_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    db: Session = Depends(get_db)
):
    """Delete restaurant (soft delete - marks as inactive)"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        success = service.delete_restaurant(restaurant_uuid)
        
        if not success:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return create_success_response(
            message="Restaurant deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Avatar configuration endpoints
@router.put("/restaurants/{restaurant_id}/avatar", response_model=APIResponse)
async def update_avatar_config(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    avatar_config: AvatarUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update restaurant AI avatar configuration"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        updated_config = service.update_avatar_config(restaurant_uuid, avatar_config)
        
        if updated_config is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return create_success_response(
            data=updated_config,
            message="Avatar configuration updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Menu categories management
@router.post("/restaurants/{restaurant_id}/categories", response_model=APIResponse)
async def create_menu_category(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    category_data: MenuCategoryCreate = ...,
    db: Session = Depends(get_db)
):
    """Create a new menu category"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        # Set restaurant_id in category data
        category_data.restaurant_id = restaurant_uuid
        
        service = RestaurantService(db)
        category = service.create_menu_category(category_data)
        
        return create_success_response(
            data=MenuCategorySchema.from_orm(category).dict(),
            message="Menu category created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}/categories", response_model=APIResponse)
async def get_menu_categories(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db)
):
    """Get all menu categories for a restaurant"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        categories = service.get_menu_categories(restaurant_uuid, include_inactive)
        
        return create_success_response(
            data=[MenuCategorySchema.from_orm(cat).dict() for cat in categories],
            message="Menu categories retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/restaurants/{restaurant_id}/categories/{category_id}", response_model=APIResponse)
async def update_menu_category(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    category_id: str = Path(..., description="Category ID"),
    category_data: MenuCategoryUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update menu category"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        service = RestaurantService(db)
        category = service.update_menu_category(
            restaurant_uuid, category_uuid, category_data
        )
        
        if not category:
            raise HTTPException(status_code=404, detail="Menu category not found")
        
        return create_success_response(
            data=MenuCategorySchema.from_orm(category).dict(),
            message="Menu category updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/restaurants/{restaurant_id}/categories/{category_id}", response_model=APIResponse)
async def delete_menu_category(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    category_id: str = Path(..., description="Category ID"),
    db: Session = Depends(get_db)
):
    """Delete menu category (soft delete)"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        service = RestaurantService(db)
        success = service.delete_menu_category(restaurant_uuid, category_uuid)
        
        if not success:
            raise HTTPException(status_code=404, detail="Menu category not found")
        
        return create_success_response(
            message="Menu category deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Analytics endpoints
@router.get("/restaurants/{restaurant_id}/analytics", response_model=APIResponse)
async def get_restaurant_analytics(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get restaurant analytics data"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = RestaurantService(db)
        analytics = service.get_restaurant_analytics(restaurant_uuid, days)
        
        return create_success_response(
            data=analytics,
            message="Analytics retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")