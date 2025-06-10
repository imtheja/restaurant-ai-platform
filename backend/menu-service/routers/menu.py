from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.connection import get_db
from schemas import (
    MenuItem as MenuItemSchema,
    MenuItemCreate,
    MenuItemUpdate,
    APIResponse,
    PaginatedResponse
)
from utils import create_success_response, create_error_response
from services.menu_service import MenuService

router = APIRouter()

@router.post("/restaurants/{restaurant_id}/menu/items", response_model=APIResponse)
async def create_menu_item(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    menu_item_data: MenuItemCreate = ...,
    db: Session = Depends(get_db)
):
    """Create a new menu item"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        # Set restaurant_id in menu item data
        menu_item_data.restaurant_id = restaurant_uuid
        
        service = MenuService(db)
        menu_item = service.create_menu_item(menu_item_data)
        
        return create_success_response(
            data=MenuItemSchema.from_orm(menu_item).dict(),
            message="Menu item created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}/menu/items", response_model=APIResponse)
async def list_menu_items(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    available_only: bool = Query(True, description="Only show available items"),
    search: Optional[str] = Query(None, description="Search in item names and descriptions"),
    db: Session = Depends(get_db)
):
    """List menu items with pagination and filtering"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = MenuService(db)
        items, total = service.list_menu_items(
            restaurant_id=restaurant_uuid,
            page=page,
            per_page=per_page,
            category_id=category_id,
            available_only=available_only,
            search=search
        )
        
        return {
            "success": True,
            "message": "Menu items retrieved successfully",
            "data": [MenuItemSchema.from_orm(item).dict() for item in items],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}/menu/items/{item_id}", response_model=APIResponse)
async def get_menu_item(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    item_id: str = Path(..., description="Menu item ID"),
    db: Session = Depends(get_db)
):
    """Get menu item by ID"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            item_uuid = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        service = MenuService(db)
        menu_item = service.get_menu_item_by_id(restaurant_uuid, item_uuid)
        
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

@router.put("/restaurants/{restaurant_id}/menu/items/{item_id}", response_model=APIResponse)
async def update_menu_item(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    item_id: str = Path(..., description="Menu item ID"),
    menu_item_data: MenuItemUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update menu item"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            item_uuid = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        service = MenuService(db)
        menu_item = service.update_menu_item(restaurant_uuid, item_uuid, menu_item_data)
        
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return create_success_response(
            data=MenuItemSchema.from_orm(menu_item).dict(),
            message="Menu item updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/restaurants/{restaurant_id}/menu/items/{item_id}", response_model=APIResponse)
async def delete_menu_item(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    item_id: str = Path(..., description="Menu item ID"),
    db: Session = Depends(get_db)
):
    """Delete menu item (soft delete)"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            item_uuid = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        service = MenuService(db)
        success = service.delete_menu_item(restaurant_uuid, item_uuid)
        
        if not success:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return create_success_response(
            message="Menu item deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/restaurants/{restaurant_id}/menu/items/{item_id}/image", response_model=APIResponse)
async def upload_menu_item_image(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    item_id: str = Path(..., description="Menu item ID"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image for menu item"""
    try:
        # Validate UUID formats
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            item_uuid = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        service = MenuService(db)
        image_url = service.upload_menu_item_image(
            restaurant_uuid, item_uuid, file.filename, content
        )
        
        if not image_url:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return create_success_response(
            data={"image_url": image_url},
            message="Image uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/restaurants/{restaurant_id}/menu/signature-items", response_model=APIResponse)
async def create_signature_item(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    signature_data: dict = ...,  # Custom schema for signature item creation
    db: Session = Depends(get_db)
):
    """Create a signature item from multiple base items"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = MenuService(db)
        signature_item = service.create_signature_item(restaurant_uuid, signature_data)
        
        return create_success_response(
            data=MenuItemSchema.from_orm(signature_item).dict(),
            message="Signature item created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}/menu/signature-items", response_model=APIResponse)
async def list_signature_items(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    db: Session = Depends(get_db)
):
    """List all signature items for a restaurant"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = MenuService(db)
        signature_items = service.list_signature_items(restaurant_uuid)
        
        return create_success_response(
            data=[MenuItemSchema.from_orm(item).dict() for item in signature_items],
            message="Signature items retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurants/{restaurant_id}/menu/analytics", response_model=APIResponse)
async def get_menu_analytics(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get menu analytics data"""
    try:
        # Validate UUID format
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid restaurant ID format")
        
        service = MenuService(db)
        analytics = service.get_menu_analytics(restaurant_uuid, days)
        
        return create_success_response(
            data=analytics,
            message="Menu analytics retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")