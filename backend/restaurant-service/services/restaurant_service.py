from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any, Tuple
import uuid
from datetime import datetime, timedelta
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.models import Restaurant, MenuCategory, MenuItem, MenuItemIngredient, Ingredient
from schemas import (
    RestaurantCreate,
    RestaurantUpdate,
    AvatarUpdate,
    MenuCategoryCreate,
    MenuCategoryUpdate
)
from utils import generate_slug, safe_json_dumps, safe_json_loads

class RestaurantService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_restaurant(self, restaurant_data: RestaurantCreate) -> Restaurant:
        """Create a new restaurant"""
        # Create restaurant instance
        restaurant = Restaurant(
            name=restaurant_data.name,
            slug=restaurant_data.slug,
            cuisine_type=restaurant_data.cuisine_type,
            description=restaurant_data.description,
            avatar_config=restaurant_data.avatar_config,
            contact_info=restaurant_data.contact_info,
            settings=restaurant_data.settings
        )
        
        self.db.add(restaurant)
        self.db.commit()
        self.db.refresh(restaurant)
        
        return restaurant
    
    def get_restaurant_by_id(self, restaurant_id: uuid.UUID) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        return self.db.query(Restaurant).filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True
        ).first()
    
    def get_restaurant_by_slug(self, slug: str) -> Optional[Restaurant]:
        """Get restaurant by slug"""
        return self.db.query(Restaurant).filter(
            Restaurant.slug == slug,
            Restaurant.is_active == True
        ).first()
    
    def list_restaurants(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        active_only: bool = True
    ) -> Tuple[List[Restaurant], int]:
        """List restaurants with pagination"""
        query = self.db.query(Restaurant)
        
        if active_only:
            query = query.filter(Restaurant.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        restaurants = query.order_by(Restaurant.created_at.desc()).offset(offset).limit(per_page).all()
        
        return restaurants, total
    
    def update_restaurant(
        self, 
        restaurant_id: uuid.UUID, 
        restaurant_data: RestaurantUpdate
    ) -> Optional[Restaurant]:
        """Update restaurant information"""
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            return None
        
        # Update fields
        update_data = restaurant_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(restaurant, field, value)
        
        restaurant.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(restaurant)
        
        return restaurant
    
    def delete_restaurant(self, restaurant_id: uuid.UUID) -> bool:
        """Soft delete restaurant"""
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            return False
        
        restaurant.is_active = False
        restaurant.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def update_avatar_config(
        self, 
        restaurant_id: uuid.UUID, 
        avatar_config: AvatarUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update restaurant avatar configuration"""
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            return None
        
        # Get current config
        current_config = restaurant.avatar_config or {}
        
        # Update with new data
        update_data = avatar_config.dict(exclude_unset=True)
        updated_config = {**current_config, **update_data}
        
        restaurant.avatar_config = updated_config
        restaurant.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return updated_config
    
    def search_restaurants(
        self, 
        query: str, 
        cuisine_type: Optional[str] = None, 
        limit: int = 10
    ) -> List[Restaurant]:
        """Search restaurants by name, description, or cuisine"""
        db_query = self.db.query(Restaurant).filter(Restaurant.is_active == True)
        
        # Add text search
        search_filter = or_(
            Restaurant.name.ilike(f"%{query}%"),
            Restaurant.description.ilike(f"%{query}%"),
            Restaurant.cuisine_type.ilike(f"%{query}%")
        )
        db_query = db_query.filter(search_filter)
        
        # Add cuisine filter
        if cuisine_type:
            db_query = db_query.filter(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
        
        # Order by relevance (name matches first)
        db_query = db_query.order_by(
            Restaurant.name.ilike(f"%{query}%").desc(),
            Restaurant.created_at.desc()
        )
        
        return db_query.limit(limit).all()
    
    def get_restaurant_menu(
        self, 
        restaurant_id: uuid.UUID, 
        category_id: Optional[str] = None,
        include_unavailable: bool = False
    ) -> Dict[str, Any]:
        """Get restaurant menu with categories and items"""
        # Get categories
        categories = self.get_menu_categories(restaurant_id, include_inactive=False)
        
        # Build menu structure
        menu_data = {
            "categories": [],
            "items": []
        }
        
        for category in categories:
            # Skip if filtering by specific category
            if category_id and str(category.id) != category_id:
                continue
            
            # Get items for this category
            items_query = self.db.query(MenuItem).options(
                joinedload(MenuItem.ingredients).joinedload(MenuItemIngredient.ingredient)
            ).filter(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.category_id == category.id
            )
            
            if not include_unavailable:
                items_query = items_query.filter(MenuItem.is_available == True)
            
            items = items_query.order_by(MenuItem.display_order, MenuItem.name).all()
            
            # Build category data
            category_data = {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "display_order": category.display_order,
                "items": []
            }
            
            # Add items to category
            for item in items:
                item_data = self._build_menu_item_data(item)
                category_data["items"].append(item_data)
                menu_data["items"].append(item_data)
            
            menu_data["categories"].append(category_data)
        
        return menu_data
    
    def get_menu_item_details(
        self, 
        restaurant_id: uuid.UUID, 
        item_id: uuid.UUID
    ) -> Optional[MenuItem]:
        """Get detailed menu item information"""
        return self.db.query(MenuItem).options(
            joinedload(MenuItem.category),
            joinedload(MenuItem.ingredients).joinedload(MenuItemIngredient.ingredient)
        ).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.id == item_id,
            MenuItem.is_available == True
        ).first()
    
    def create_menu_category(self, category_data: MenuCategoryCreate) -> MenuCategory:
        """Create a new menu category"""
        category = MenuCategory(
            restaurant_id=category_data.restaurant_id,
            name=category_data.name,
            description=category_data.description,
            display_order=category_data.display_order
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_menu_categories(
        self, 
        restaurant_id: uuid.UUID, 
        include_inactive: bool = False
    ) -> List[MenuCategory]:
        """Get menu categories for a restaurant"""
        query = self.db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id
        )
        
        if not include_inactive:
            query = query.filter(MenuCategory.is_active == True)
        
        return query.order_by(MenuCategory.display_order, MenuCategory.name).all()
    
    def update_menu_category(
        self, 
        restaurant_id: uuid.UUID, 
        category_id: uuid.UUID, 
        category_data: MenuCategoryUpdate
    ) -> Optional[MenuCategory]:
        """Update menu category"""
        category = self.db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id,
            MenuCategory.id == category_id
        ).first()
        
        if not category:
            return None
        
        # Update fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        category.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_menu_category(
        self, 
        restaurant_id: uuid.UUID, 
        category_id: uuid.UUID
    ) -> bool:
        """Soft delete menu category"""
        category = self.db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id,
            MenuCategory.id == category_id
        ).first()
        
        if not category:
            return False
        
        category.is_active = False
        category.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_restaurant_analytics(
        self, 
        restaurant_id: uuid.UUID, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get basic restaurant analytics"""
        # For Phase 1, return mock analytics
        # In Phase 2, implement real analytics from interaction_analytics table
        
        return {
            "total_conversations": 0,
            "total_menu_views": 0,
            "popular_items": [],
            "common_questions": [],
            "avg_session_duration": 0,
            "customer_satisfaction": 0,
            "period_days": days,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _build_menu_item_data(self, item: MenuItem) -> Dict[str, Any]:
        """Build menu item data structure"""
        # Extract allergen information
        allergens = []
        for ingredient_rel in item.ingredients:
            if ingredient_rel.ingredient.allergen_info:
                allergens.extend(ingredient_rel.ingredient.allergen_info)
        
        # Remove duplicates
        allergens = list(set(allergens))
        
        return {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "image_url": item.image_url,
            "is_available": item.is_available,
            "is_signature": item.is_signature,
            "spice_level": item.spice_level,
            "preparation_time": item.preparation_time,
            "allergen_info": allergens,
            "tags": item.tags or [],
            "category_id": str(item.category_id) if item.category_id else None,
            "ingredients": [
                {
                    "name": ing_rel.ingredient.name,
                    "quantity": ing_rel.quantity,
                    "unit": ing_rel.unit,
                    "is_optional": ing_rel.is_optional,
                    "is_primary": ing_rel.is_primary,
                    "allergen_info": ing_rel.ingredient.allergen_info or []
                }
                for ing_rel in item.ingredients
            ]
        }