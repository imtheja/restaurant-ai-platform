from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    cuisine_type = Column(String(100))
    description = Column(Text)
    avatar_config = Column(JSON)
    contact_info = Column(JSON)
    settings = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    menu_categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="restaurant", cascade="all, delete-orphan")

class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_categories")
    menu_items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("menu_categories.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    is_signature = Column(Boolean, default=False)
    spice_level = Column(Integer, default=0)
    preparation_time = Column(Integer)  # in minutes
    nutritional_info = Column(JSON)
    allergen_info = Column(JSON)
    tags = Column(JSON)  # dietary tags like "vegan", "gluten-free"
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    category = relationship("MenuCategory", back_populates="menu_items")
    ingredients = relationship("MenuItemIngredient", back_populates="menu_item", cascade="all, delete-orphan")
    signature_components = relationship("SignatureItemComponent", 
                                      foreign_keys="SignatureItemComponent.signature_item_id",
                                      back_populates="signature_item", cascade="all, delete-orphan")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100))
    allergen_info = Column(JSON)
    nutritional_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    menu_items = relationship("MenuItemIngredient", back_populates="ingredient")

class MenuItemIngredient(Base):
    __tablename__ = "menu_item_ingredients"

    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(String(50))
    unit = Column(String(20))
    is_optional = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)  # main ingredient vs garnish/seasoning

    # Relationships
    menu_item = relationship("MenuItem", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="menu_items")

class SignatureItemComponent(Base):
    __tablename__ = "signature_item_components"

    signature_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True)
    base_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer, default=1)
    modifications = Column(JSON)  # custom modifications for this component
    display_order = Column(Integer, default=0)

    # Relationships
    signature_item = relationship("MenuItem", foreign_keys=[signature_item_id], back_populates="signature_components")
    base_item = relationship("MenuItem", foreign_keys=[base_item_id])

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True))  # For future user management
    context = Column(JSON)  # conversation context and preferences
    meta_data = Column(JSON)  # additional data like user agent, IP, etc.
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    restaurant = relationship("Restaurant", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('restaurant_id', 'session_id', name='unique_restaurant_session'),
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'customer' or 'ai'
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, suggestion, recommendation
    meta_data = Column(JSON)  # additional message data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class InteractionAnalytics(Base):
    __tablename__ = "interaction_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON)
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    restaurant = relationship("Restaurant")
    conversation = relationship("Conversation")