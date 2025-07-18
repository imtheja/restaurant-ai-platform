"""Menu service business logic."""
import os
import uuid as uuid_lib
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from PIL import Image
import io
from database.models import (
    MenuItem, MenuCategory, Restaurant,
    Ingredient, MenuItemIngredient
)
from schemas import (
    MenuItemCreate, MenuItemUpdate,
    MenuCategoryCreate, MenuCategoryUpdate
)


class MenuService:
    """Service class for menu-related operations."""
    
    @staticmethod
    async def get_categories(
        db: Session,
        restaurant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[MenuCategory]:
        """Get all menu categories for a restaurant."""
        return db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    async def create_category(
        db: Session,
        restaurant_id: UUID,
        category: MenuCategoryCreate
    ) -> MenuCategory:
        """Create a new menu category."""
        db_category = MenuCategory(
            restaurant_id=restaurant_id,
            **category.dict()
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    async def update_category(
        db: Session,
        category_id: UUID,
        category_update: MenuCategoryUpdate
    ) -> Optional[MenuCategory]:
        """Update a menu category."""
        db_category = db.query(MenuCategory).filter(
            MenuCategory.id == category_id
        ).first()
        
        if not db_category:
            return None
            
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
            
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    async def delete_category(
        db: Session,
        category_id: UUID
    ) -> bool:
        """Delete a menu category."""
        db_category = db.query(MenuCategory).filter(
            MenuCategory.id == category_id
        ).first()
        
        if not db_category:
            return False
            
        db.delete(db_category)
        db.commit()
        return True
    
    @staticmethod
    async def get_menu_items(
        db: Session,
        restaurant_id: UUID,
        category_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MenuItem]:
        """Get menu items for a restaurant."""
        query = db.query(MenuItem).join(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id
        )
        
        if category_id:
            query = query.filter(MenuItem.category_id == category_id)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_menu_item(
        db: Session,
        item_id: UUID
    ) -> Optional[MenuItem]:
        """Get a specific menu item."""
        return db.query(MenuItem).filter(
            MenuItem.id == item_id
        ).first()
    
    @staticmethod
    async def create_menu_item(
        db: Session,
        category_id: UUID,
        item: MenuItemCreate
    ) -> MenuItem:
        """Create a new menu item."""
        # Extract ingredients from the item data
        ingredient_ids = item.dict().pop('ingredient_ids', [])
        
        # Create the menu item
        db_item = MenuItem(
            category_id=category_id,
            **item.dict()
        )
        db.add(db_item)
        db.flush()  # Flush to get the ID
        
        # Add ingredients if provided
        for ingredient_id in ingredient_ids:
            item_ingredient = MenuItemIngredient(
                menu_item_id=db_item.id,
                ingredient_id=ingredient_id
            )
            db.add(item_ingredient)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    async def update_menu_item(
        db: Session,
        item_id: UUID,
        item_update: MenuItemUpdate
    ) -> Optional[MenuItem]:
        """Update a menu item."""
        db_item = db.query(MenuItem).filter(
            MenuItem.id == item_id
        ).first()
        
        if not db_item:
            return None
        
        # Handle ingredient updates separately
        update_data = item_update.dict(exclude_unset=True)
        ingredient_ids = update_data.pop('ingredient_ids', None)
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        # Update ingredients if provided
        if ingredient_ids is not None:
            # Remove existing ingredients
            db.query(MenuItemIngredient).filter(
                MenuItemIngredient.menu_item_id == item_id
            ).delete()
            
            # Add new ingredients
            for ingredient_id in ingredient_ids:
                item_ingredient = MenuItemIngredient(
                    menu_item_id=item_id,
                    ingredient_id=ingredient_id
                )
                db.add(item_ingredient)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    async def delete_menu_item(
        db: Session,
        item_id: UUID
    ) -> bool:
        """Delete a menu item."""
        db_item = db.query(MenuItem).filter(
            MenuItem.id == item_id
        ).first()
        
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        return True
    
    @staticmethod
    async def search_menu_items(
        db: Session,
        restaurant_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MenuItem]:
        """Search menu items by name or description."""
        search_pattern = f"%{query}%"
        
        return db.query(MenuItem).join(MenuCategory).filter(
            and_(
                MenuCategory.restaurant_id == restaurant_id,
                db.query(MenuItem).filter(
                    MenuItem.name.ilike(search_pattern) |
                    MenuItem.description.ilike(search_pattern)
                ).exists()
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    async def upload_menu_item_image(
        db: Session,
        restaurant_id: UUID,
        item_id: UUID,
        filename: str,
        content: bytes
    ) -> Optional[str]:
        """Upload and process an image for a menu item."""
        # Verify menu item exists and belongs to restaurant
        db_item = db.query(MenuItem).join(MenuCategory).filter(
            MenuItem.id == item_id,
            MenuCategory.restaurant_id == restaurant_id
        ).first()
        
        if not db_item:
            return None
        
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), "uploads", "menu-items")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
            unique_filename = f"{item_id}_{uuid_lib.uuid4().hex[:8]}.{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Process and optimize image using PIL
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary (for JPEG support)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Create multiple sizes
            sizes = {
                'thumbnail': (150, 150),
                'card': (300, 300),
                'full': (800, 800)
            }
            
            saved_files = {}
            for size_name, (width, height) in sizes.items():
                # Calculate aspect ratio preserving resize
                image_copy = image.copy()
                image_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # Create filename for this size
                size_filename = f"{item_id}_{uuid_lib.uuid4().hex[:8]}_{size_name}.jpg"
                size_path = os.path.join(upload_dir, size_filename)
                
                # Save optimized image
                image_copy.save(size_path, 'JPEG', quality=85, optimize=True)
                
                # Store relative URL for serving
                saved_files[size_name] = f"/uploads/menu-items/{size_filename}"
            
            # Update menu item with primary image URL (card size)
            db_item.image_url = saved_files['card']
            db.commit()
            db.refresh(db_item)
            
            return saved_files['card']
            
        except Exception as e:
            # If image processing fails, save original file
            try:
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Update menu item with basic URL
                relative_url = f"/uploads/menu-items/{unique_filename}"
                db_item.image_url = relative_url
                db.commit()
                db.refresh(db_item)
                
                return relative_url
                
            except Exception:
                return None