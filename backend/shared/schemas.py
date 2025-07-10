from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }

# Restaurant schemas
class RestaurantBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    cuisine_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None

class RestaurantCreate(RestaurantBase):
    avatar_config: Optional[Dict[str, Any]] = None

class RestaurantUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cuisine_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Restaurant(RestaurantBase):
    id: uuid.UUID
    avatar_config: Optional[Dict[str, Any]]
    theme_config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Avatar configuration schemas
class AvatarConfig(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    personality: str = Field(..., pattern="^(friendly_knowledgeable|professional_formal|casual_fun|expert_chef)$")
    greeting: str = Field(..., min_length=10, max_length=500)
    tone: str = Field(..., pattern="^(warm|professional|enthusiastic|casual)$")
    special_instructions: Optional[str] = Field(None, max_length=1000)

class AvatarUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    personality: Optional[str] = Field(None, pattern="^(friendly_knowledgeable|professional_formal|casual_fun|expert_chef)$")
    greeting: Optional[str] = Field(None, min_length=10, max_length=500)
    tone: Optional[str] = Field(None, pattern="^(warm|professional|enthusiastic|casual)$")
    special_instructions: Optional[str] = Field(None, max_length=1000)

# Menu category schemas
class MenuCategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    display_order: int = Field(default=0, ge=0)

class MenuCategoryCreate(MenuCategoryBase):
    restaurant_id: uuid.UUID

class MenuCategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class MenuCategory(MenuCategoryBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Ingredient schemas
class IngredientBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    allergen_info: Optional[List[str]] = []
    nutritional_info: Optional[Dict[str, Any]] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    allergen_info: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Ingredient(IngredientBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

# Menu item ingredient schemas
class MenuItemIngredientBase(BaseSchema):
    ingredient_id: uuid.UUID
    quantity: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=20)
    is_optional: bool = False
    is_primary: bool = False

class MenuItemIngredientCreate(MenuItemIngredientBase):
    pass

class MenuItemIngredient(MenuItemIngredientBase):
    ingredient: Ingredient

# Menu item schemas
class MenuItemBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    spice_level: int = Field(default=0, ge=0, le=5)
    preparation_time: Optional[int] = Field(None, ge=0)
    nutritional_info: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []
    display_order: int = Field(default=0, ge=0)

class MenuItemCreate(MenuItemBase):
    restaurant_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    is_signature: bool = False
    ingredients: Optional[List[MenuItemIngredientCreate]] = []

class MenuItemUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    spice_level: Optional[int] = Field(None, ge=0, le=5)
    preparation_time: Optional[int] = Field(None, ge=0)
    nutritional_info: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    display_order: Optional[int] = Field(None, ge=0)

class MenuItem(MenuItemBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    is_available: bool
    is_signature: bool
    allergen_info: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    category: Optional[MenuCategory]
    ingredients: List[MenuItemIngredient] = []

# Conversation schemas
class MessageBase(BaseSchema):
    content: str = Field(..., min_length=1)
    sender_type: str = Field(..., pattern="^(customer|ai)$")
    message_type: str = Field(default="text", max_length=50)
    meta_data: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    conversation_id: uuid.UUID

class Message(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime

class ConversationBase(BaseSchema):
    session_id: str = Field(..., min_length=1, max_length=255)
    context: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None

class ConversationCreate(ConversationBase):
    restaurant_id: uuid.UUID

class Conversation(ConversationBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    customer_id: Optional[uuid.UUID]
    is_active: bool
    started_at: datetime
    last_activity: datetime
    messages: List[Message] = []

# AI chat request/response schemas
class ChatRequest(BaseSchema):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=1, max_length=255)
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseSchema):
    message: str
    suggestions: Optional[List[str]] = []
    recommendations: Optional[List[Dict[str, Any]]] = []
    conversation_id: uuid.UUID
    message_id: uuid.UUID

# API response schemas
class APIResponse(BaseSchema):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginationMeta(BaseSchema):
    page: int
    per_page: int
    total: int
    pages: int

class PaginatedResponse(APIResponse):
    meta: PaginationMeta

# Health check schema
class HealthCheck(BaseSchema):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    services: Dict[str, bool] = {}

# Analytics schemas
class AnalyticsEvent(BaseSchema):
    event_type: str = Field(..., max_length=100)
    event_data: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)

class InteractionAnalytics(AnalyticsEvent):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    conversation_id: Optional[uuid.UUID]
    timestamp: datetime