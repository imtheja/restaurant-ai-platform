from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import openai
import json
import asyncio
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database.models import Restaurant, Conversation, Message, MenuItem, MenuCategory, InteractionAnalytics, Ingredient, MenuItemIngredient
from database.connection import db_manager
from schemas import ChatResponse
from utils import generate_session_id, extract_keywords, safe_json_loads, safe_json_dumps
from .menu_cache_service import MenuCacheService

class AIService:
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize cache service
        self.cache_service = MenuCacheService(db)
        
        # OpenAI API configuration (standardized to use only OpenAI)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Faster model for real-time
            
        self.max_conversation_length = 50
    
    def get_or_create_conversation(
        self, 
        restaurant_slug: str, 
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Conversation]:
        """Get existing conversation or create a new one"""
        
        # Get restaurant
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.slug == restaurant_slug,
            Restaurant.is_active == True
        ).first()
        
        if not restaurant:
            return None
        
        # Try to get existing conversation
        conversation = self.db.query(Conversation).filter(
            Conversation.restaurant_id == restaurant.id,
            Conversation.session_id == session_id,
            Conversation.is_active == True
        ).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                restaurant_id=restaurant.id,
                session_id=session_id,
                context=context or {},
                metadata={}
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
        
        return conversation
    
    async def process_chat_message(
        self, 
        conversation: Conversation, 
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process incoming chat message and generate AI response"""
        
        # Record user message
        user_message = Message(
            conversation_id=conversation.id,
            sender_type="customer",
            content=message,
            meta_data=context
        )
        self.db.add(user_message)
        
        # Get restaurant and menu context
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.id == conversation.restaurant_id
        ).first()
        
        # Check cache for common menu questions first
        cached_response = await self.cache_service.get_cached_response(
            restaurant_id=str(restaurant.id),
            message=message
        )
        
        if cached_response:
            # Record cached AI response
            ai_message = Message(
                conversation_id=conversation.id,
                sender_type="ai",
                content=cached_response,
                meta_data={"from_cache": True}
            )
            self.db.add(ai_message)
            
            # Update conversation activity
            conversation.last_activity = datetime.utcnow()
            if context:
                conversation.context = {**(conversation.context or {}), **context}
            
            # Record analytics
            self._record_interaction_analytics(
                restaurant_id=restaurant.id,
                conversation_id=conversation.id,
                event_type="chat_message_cached",
                event_data={
                    "user_message": message,
                    "ai_response": cached_response,
                    "from_cache": True
                }
            )
            
            self.db.commit()
            
            return {
                "message": cached_response,
                "suggestions": [],
                "recommendations": [],
                "conversation_id": str(conversation.id),
                "message_id": str(ai_message.id)
            }
        
        menu_context = await self._get_menu_context(restaurant.id)
        avatar_config = restaurant.avatar_config or {}
        
        # Add restaurant info to context
        restaurant_info = {
            "name": restaurant.name,
            "cuisine_type": restaurant.cuisine_type,
            "description": restaurant.description,
            "contact_info": restaurant.contact_info or {},
            "settings": restaurant.settings or {}
        }
        
        # Build conversation history
        conversation_history = self._get_conversation_history(conversation.id)
        
        # Generate AI response
        ai_response_text, suggestions, recommendations = await self._generate_ai_response(
            message=message,
            conversation_history=conversation_history,
            restaurant=restaurant,
            restaurant_info=restaurant_info,
            menu_context=menu_context,
            avatar_config=avatar_config,
            context=context
        )
        
        # Record AI message
        ai_message = Message(
            conversation_id=conversation.id,
            sender_type="ai",
            content=ai_response_text,
            meta_data={
                "suggestions": suggestions,
                "recommendations": recommendations
            }
        )
        self.db.add(ai_message)
        
        # Update conversation activity
        conversation.last_activity = datetime.utcnow()
        if context:
            conversation.context = {**(conversation.context or {}), **context}
        
        # Record analytics
        self._record_interaction_analytics(
            restaurant_id=restaurant.id,
            conversation_id=conversation.id,
            event_type="chat_message",
            event_data={
                "user_message": message,
                "ai_response": ai_response_text,
                "suggestions_count": len(suggestions),
                "recommendations_count": len(recommendations)
            }
        )
        
        self.db.commit()
        
        return {
            "message": ai_response_text,
            "suggestions": suggestions,
            "recommendations": recommendations,
            "conversation_id": str(conversation.id),
            "message_id": str(ai_message.id)
        }
    
    async def process_chat_message_stream(
        self, 
        conversation: Conversation, 
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Process chat message with streaming response for real-time conversation"""
        import json
        
        # Record user message (async to reduce blocking)
        user_message = Message(
            conversation_id=conversation.id,
            sender_type="customer",
            content=message,
            meta_data=context
        )
        self.db.add(user_message)
        
        # Get cached restaurant data (optimize with simple query)
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.id == conversation.restaurant_id
        ).first()
        
        # Check cache for common menu questions first (faster than AI)
        cached_response = await self.cache_service.get_cached_response(
            restaurant_id=str(restaurant.id),
            message=message
        )
        
        if cached_response:
            # Yield cached response as a single chunk
            ai_message = Message(
                conversation_id=conversation.id,
                sender_type="ai",
                content=cached_response,
                meta_data={"from_cache": True}
            )
            self.db.add(ai_message)
            
            # Update conversation activity
            conversation.last_activity = datetime.utcnow()
            if context:
                conversation.context = {**(conversation.context or {}), **context}
            
            # Commit changes
            self.db.commit()
            
            # Yield the cached response
            yield f"data: {json.dumps({'content': cached_response})}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # Build lightweight context for faster processing
        quick_context = {
            "restaurant_name": restaurant.name,
            "cuisine_type": restaurant.cuisine_type,
            "avatar_name": restaurant.avatar_config.get("name", "Assistant") if restaurant.avatar_config else "Assistant"
        }
        
        # Get recent conversation history (limit to 3 messages for speed)
        recent_history = self._get_conversation_history(conversation.id, limit=3)
        
        # Build streamlined prompt
        system_prompt = f"""You are {quick_context['avatar_name']}, a friendly {quick_context['cuisine_type']} restaurant assistant for {quick_context['restaurant_name']}. 
Keep responses under 50 words, warm and helpful. Focus on menu questions and recommendations."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add limited recent history
        for msg in recent_history:
            messages.append({
                "role": "user" if msg["sender_type"] == "customer" else "assistant",
                "content": msg["content"]
            })
        
        messages.append({"role": "user", "content": message})
        
        # Streaming response
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key.startswith("your_") or api_key == "sk-fake-key-for-development-only":
                # Quick fallback for development
                fallback_response = f"I'd be happy to help you with {quick_context['restaurant_name']}! What would you like to know about our menu?"
                yield json.dumps({"type": "token", "content": fallback_response})
                yield json.dumps({"type": "done", "message_id": str(user_message.id)})
                return
            
            # Stream from OpenAI
            response_stream = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=messages,
                max_tokens=75,  # Shorter for faster responses
                temperature=0.8,  # Slightly higher for personality
                stream=True
            )
            
            full_response = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield json.dumps({"type": "token", "content": content})
            
            # Record AI message after streaming
            ai_message = Message(
                conversation_id=conversation.id,
                sender_type="ai",
                content=full_response,
                meta_data={}
            )
            self.db.add(ai_message)
            
            # Update conversation activity
            conversation.last_activity = datetime.utcnow()
            self.db.commit()
            
            yield json.dumps({"type": "done", "message_id": str(ai_message.id)})
            
        except Exception as e:
            # Quick fallback on error
            error_response = "I'm here to help! What can I tell you about our delicious options?"
            yield json.dumps({"type": "token", "content": error_response})
            yield json.dumps({"type": "error", "error": str(e)})
    
    async def _generate_ai_response(
        self, 
        message: str,
        conversation_history: List[Dict[str, str]],
        restaurant: Restaurant,
        restaurant_info: Dict[str, Any],
        menu_context: Dict[str, Any],
        avatar_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, List[str], List[Dict[str, Any]]]:
        """Generate AI response using OpenAI API"""
        
        # Check if this is the very first message in the conversation
        is_first_interaction = len(conversation_history) == 0
        
        # Build system prompt
        system_prompt = self._build_system_prompt(restaurant, restaurant_info, menu_context, avatar_config, is_first_interaction)
        
        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": "user" if msg["sender_type"] == "customer" else "assistant",
                "content": msg["content"]
            })
        
        # Analyze customer intent for appropriate response style
        customer_intent = self._analyze_customer_intent(message, conversation_history)
        
        # Add current message with intent context
        enhanced_message = message
        if customer_intent == "browsing":
            enhanced_message = f"[Customer is browsing/asking questions - focus on being helpful, no prices or upselling] {message}"
        elif customer_intent == "ordering":
            enhanced_message = f"[Customer is ready to order - prices and upselling appropriate] {message}"
        
        messages.append({"role": "user", "content": enhanced_message})
        
        try:
            # Check if we have a valid OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key.startswith("your_") or api_key == "sk-fake-key-for-development-only":
                # Use fallback response for development
                return self._generate_fallback_response(message, restaurant, avatar_config, is_first_interaction), [], []
            
            # Call AI API (OpenAI compatible)
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=messages,
                max_tokens=100,  # Shorter for faster responses
                temperature=0.8,  # Slightly higher for personality
                # Note: Grok might not support functions yet, so we'll handle this gracefully
                # functions=[...] - removed for better compatibility
            )
            
            ai_message = response.choices[0].message
            ai_response_text = ai_message.content or ""
            
            suggestions = []
            recommendations = []
            
            # Parse function call if present
            if ai_message.function_call:
                try:
                    function_args = json.loads(ai_message.function_call.arguments)
                    suggestions = function_args.get("suggestions", [])
                    recommendations = function_args.get("recommended_items", [])
                except:
                    pass
            
            # Generate default suggestions if none provided
            if not suggestions:
                suggestions = self._generate_default_suggestions(message, menu_context)
            
            return ai_response_text, suggestions, recommendations
            
        except Exception as e:
            # Fallback response if AI service fails
            return self._generate_fallback_response(message, restaurant, avatar_config, is_first_interaction), [], []
    
    def _build_system_prompt(
        self, 
        restaurant: Restaurant, 
        restaurant_info: Dict[str, Any],
        menu_context: Dict[str, Any],
        avatar_config: Dict[str, Any],
        is_first_interaction: bool = False
    ) -> str:
        """Build system prompt for AI assistant"""
        
        avatar_name = avatar_config.get("name", "Assistant")
        personality = avatar_config.get("personality", "friendly_knowledgeable")
        greeting = avatar_config.get("greeting", f"Welcome to {restaurant.name}!")
        tone = avatar_config.get("tone", "warm")
        special_instructions = avatar_config.get("special_instructions", "")
        
        # Build menu summary
        menu_summary = self._build_menu_summary(menu_context)
        
        # Build restaurant info summary
        contact_info = restaurant_info.get("contact_info", {})
        settings = restaurant_info.get("settings", {})
        business_hours = settings.get("business_hours", {})
        
        restaurant_summary = f"""
RESTAURANT INFORMATION:
- Name: {restaurant_info.get('name')}
- Type: {restaurant_info.get('cuisine_type')} restaurant
- Description: {restaurant_info.get('description')}
- Phone: {contact_info.get('phone', 'Available upon request')}
- Address: {contact_info.get('address', 'Available upon request')}
"""
        
        if business_hours:
            restaurant_summary += "\nBUSINESS HOURS:\n"
            for day, hours in business_hours.items():
                restaurant_summary += f"- {day.capitalize()}: {hours}\n"

        system_prompt = f"""
I'm {avatar_name}, and I work here at {restaurant.name}. I'm like that friendly actress who landed a perfect role as a bakery assistant - warm, genuine, and absolutely in love with what I do here.

CRITICAL ACCURACY RULES:
- ONLY discuss items, ingredients, and prices that are EXACTLY in our menu below
- NEVER make up ingredients, prices, or menu items that aren't listed
- If a customer asks about something not on our menu, politely say we don't have it
- Use EXACT ingredient names and allergen information from our database
- For prices, use EXACT amounts listed - never estimate or round
- If unsure about ingredients/allergens, suggest checking with kitchen staff
- For business info (hours, location, phone), use EXACT information from restaurant data

IMPORTANT: The customer has already been welcomed when they opened the chat, so jump straight into helping them with their question.

CHARACTER BACKGROUND:
I'm a real person who genuinely loves working in this bakery. I know our cookies inside and out because I help bake them. I talk to customers all day and I'm naturally bubbly and enthusiastic about our treats.

{restaurant_summary}

OUR COMPLETE MENU DATABASE:
{menu_summary}

MY SPEAKING STYLE:
- Natural, conversational tone like I'm standing right next to you
- Use everyday expressions: "Oh definitely!", "You know what?", "Trust me", "Honestly"
- Show genuine excitement without being over the top
- Ask quick follow-up questions to keep chatting
- Never use emojis in my speech (they sound weird when read aloud)
- Speak like I'm multitasking - friendly but efficient

HOW I RESPOND:
- Keep responses conversational but concise (30-50 words is perfect)
- Sound like I'm actually working behind the counter
- Give helpful, meaningful answers with just enough detail
- Show personality but stay focused
- Use contractions naturally ("I'm", "you'll", "that's", "we've")
- Answer questions directly without mentioning prices unless asked
- Focus on ingredients, taste, and what makes items special
- Only suggest add-ons or upsell when customer is ready to order
- Save sales tactics for when they're actually placing an order
- NO need to welcome customers - they've already been welcomed

EXAMPLE RESPONSES:
INGREDIENT QUESTION: "The Semi Sweet has premium chocolate chips, butter, flour, and sugar. Contains dairy and gluten."
PRICE QUESTION: "That's $4.50!"
ALLERGEN QUESTION: "The OG contains dairy, eggs, and gluten. We also work with nuts in our kitchen."
BUSINESS QUESTION: "We're open Monday through Saturday 10 AM to 10 PM, and Sunday 11 AM to 9 PM!"
NON-MENU ITEM: "Sorry, we don't have that item, but our Semi Sweet cookie has a similar flavor profile!"
TASTE QUESTION: "Oh, the Semi Sweet is perfectly balanced - not too sweet, with rich chocolate chunks throughout!"
ABOUT ITEM: "The OG is our classic recipe! It's got that perfect chewy texture with melted chocolate chips."
ORDERING CONTEXT: "Great choice! That's $4.50. Want to add cream cheese frosting for $1 more?"

PRICING AND UPSELLING RULES:
- NEVER mention prices unless customer specifically asks about pricing
- ONLY upsell when customer says "I'll take", "I want to order", "Can I get" or similar ordering language
- Focus on being helpful first - describe taste, ingredients, what makes items special
- Save the sales pitch for when they're actually ready to buy
- If they ask "tell me about X", focus on taste and ingredients, not price or add-ons

IMPORTANT:
- NO emojis in responses (they get read aloud awkwardly)
- Sound like a real person, not an AI
- Be helpful but don't over-explain
- Always sound like I'm genuinely happy to help
- Jump straight into helping - no welcoming needed
- When customers ask about ingredients/allergens, be VERY specific and accurate
        """
        
        return system_prompt.strip()
    
    def _analyze_customer_intent(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """Analyze if customer is browsing or ready to order"""
        
        message_lower = message.lower()
        
        # Clear ordering intent keywords
        ordering_keywords = [
            "i'll take", "i want to order", "can i get", "i'd like", "let me get",
            "give me", "i'll have", "i want", "order", "buy", "purchase",
            "how much for", "what's the price", "how much does", "cost"
        ]
        
        # Browsing/information seeking keywords
        browsing_keywords = [
            "tell me about", "what is", "what's in", "ingredients", "allergens",
            "what are", "how", "why", "describe", "what makes", "what does",
            "contains", "made with", "taste like", "what kind"
        ]
        
        # Check for ordering intent
        if any(keyword in message_lower for keyword in ordering_keywords):
            return "ordering"
        
        # Check for browsing intent
        if any(keyword in message_lower for keyword in browsing_keywords):
            return "browsing"
        
        # Look at conversation history for context
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 messages
            for msg in recent_messages:
                if msg["sender_type"] == "customer":
                    msg_lower = msg["content"].lower()
                    if any(keyword in msg_lower for keyword in ordering_keywords):
                        return "ordering"
        
        # Default to browsing (be helpful first)
        return "browsing"
    
    def _build_menu_summary(self, menu_context: Dict[str, Any]) -> str:
        """Build a comprehensive menu summary for accurate AI responses"""
        
        categories = menu_context.get("categories", [])
        summary_parts = []
        
        # Add complete ingredient list first
        all_ingredients = menu_context.get("all_ingredients", [])
        if all_ingredients:
            summary_parts.append("\nAVAILABLE INGREDIENTS IN OUR KITCHEN:")
            for ingredient in all_ingredients:
                ing_info = f"- {ingredient['name']}"
                if ingredient.get('category'):
                    ing_info += f" ({ingredient['category']})"
                if ingredient.get('allergen_info'):
                    ing_info += f" [Contains: {', '.join(ingredient['allergen_info'])}]"
                summary_parts.append(f"  {ing_info}")
        
        # Add allergen summary
        allergens = menu_context.get("allergens", [])
        if allergens:
            summary_parts.append(f"\nALLERGENS WE WORK WITH: {', '.join(sorted(allergens))}")
        
        # Add detailed menu items
        for category in categories:
            items = category.get("items", [])
            if not items:
                continue
            
            category_summary = f"\n\n{category['name'].upper()}:"
            if category.get('description'):
                category_summary += f"\n{category['description']}"
            
            for item in items:  # Include ALL items, not just 5
                item_info = f"\n• {item['name']} - ${item['price']:.2f}"
                
                if item.get('description'):
                    item_info += f"\n  Description: {item['description']}"
                
                if item.get('is_signature'):
                    item_info += "\n  ⭐ SIGNATURE ITEM"
                
                # Add detailed ingredients
                ingredients = item.get('ingredients', [])
                if ingredients:
                    ingredient_names = [ing['name'] for ing in ingredients]
                    item_info += f"\n  Ingredients: {', '.join(ingredient_names)}"
                
                # Add allergen info
                if item.get('allergen_info'):
                    item_info += f"\n  ⚠️ Contains: {', '.join(item['allergen_info'])}"
                
                # Add tags if any
                if item.get('tags'):
                    item_info += f"\n  Tags: {', '.join(item['tags'])}"
                
                category_summary += item_info
            
            summary_parts.append(category_summary)
        
        return "\n".join(summary_parts)
    
    def _get_conversation_history(self, conversation_id: uuid.UUID, limit: int = 20) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {
                "sender_type": msg.sender_type,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    async def _get_menu_context(self, restaurant_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive menu context for AI responses"""
        
        # Try to get from cache first
        cache_key = f"menu_context:{restaurant_id}"
        cached_menu = db_manager.cache_get(cache_key)
        
        if cached_menu:
            return safe_json_loads(cached_menu, {})
        
        # Get categories and items with ingredients
        
        categories = self.db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id,
            MenuCategory.is_active == True
        ).order_by(MenuCategory.display_order).all()
        
        menu_context = {"categories": [], "all_ingredients": [], "allergens": set()}
        
        for category in categories:
            items = self.db.query(MenuItem).filter(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.category_id == category.id,
                MenuItem.is_available == True
            ).order_by(MenuItem.display_order).all()
            
            category_items = []
            for item in items:
                # Get ingredients for this item
                ingredients = self.db.query(Ingredient).join(MenuItemIngredient).filter(
                    MenuItemIngredient.menu_item_id == item.id
                ).all()
                
                ingredient_list = []
                for ingredient in ingredients:
                    ingredient_list.append({
                        "name": ingredient.name,
                        "allergen_info": ingredient.allergen_info or [],
                        "category": ingredient.category
                    })
                    # Collect all allergens
                    if ingredient.allergen_info:
                        menu_context["allergens"].update(ingredient.allergen_info)
                
                item_data = {
                    "id": str(item.id),
                    "name": item.name,
                    "description": item.description,
                    "price": float(item.price),
                    "is_signature": item.is_signature,
                    "spice_level": item.spice_level,
                    "allergen_info": item.allergen_info or [],
                    "tags": item.tags or [],
                    "ingredients": ingredient_list
                }
                category_items.append(item_data)
            
            category_data = {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "items": category_items
            }
            
            menu_context["categories"].append(category_data)
        
        # Get all ingredients for reference (ingredients are shared across restaurants)
        all_ingredients = self.db.query(Ingredient).filter(
            Ingredient.is_active == True
        ).all()
        
        menu_context["all_ingredients"] = [
            {
                "name": ingredient.name,
                "category": ingredient.category,
                "allergen_info": ingredient.allergen_info or []
            }
            for ingredient in all_ingredients
        ]
        
        # Convert allergens set to list
        menu_context["allergens"] = list(menu_context["allergens"])
        
        # Cache for 1 hour
        db_manager.cache_set(cache_key, safe_json_dumps(menu_context), 3600)
        
        return menu_context
    
    def _generate_default_suggestions(
        self, 
        message: str, 
        menu_context: Dict[str, Any]
    ) -> List[str]:
        """Generate default conversation suggestions"""
        
        keywords = extract_keywords(message.lower())
        suggestions = []
        
        # Keyword-based suggestions
        if any(word in keywords for word in ['spicy', 'hot', 'heat']):
            suggestions.append("What's your spice tolerance level?")
            suggestions.append("Would you like to see our mildest options?")
        
        if any(word in keywords for word in ['vegetarian', 'vegan', 'plant']):
            suggestions.append("Do you have any other dietary restrictions?")
            suggestions.append("Are you interested in our vegetarian specialties?")
        
        if any(word in keywords for word in ['allergy', 'allergic', 'allergen']):
            suggestions.append("Which specific allergens should I help you avoid?")
            suggestions.append("Would you like me to recommend allergen-free options?")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Would you like to hear about our signature dishes?",
                "Are you looking for something specific?",
                "Would you like to know about today's specials?"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_fallback_response(
        self, 
        message: str, 
        restaurant: Restaurant,
        avatar_config: Dict[str, Any],
        is_first_interaction: bool = False
    ) -> str:
        """Generate fallback response when AI service is unavailable"""
        
        avatar_name = avatar_config.get("name", "Baker Betty")
        
        return (
            f"I'm {avatar_name} and I work here at the bakery. "
            f"What can I help you with today? I know our menu pretty well!"
        )
    
    def _record_interaction_analytics(
        self, 
        restaurant_id: uuid.UUID,
        conversation_id: uuid.UUID,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Record interaction analytics"""
        
        analytics = InteractionAnalytics(
            restaurant_id=restaurant_id,
            conversation_id=conversation_id,
            event_type=event_type,
            event_data=event_data
        )
        
        self.db.add(analytics)
    
    async def get_conversation_suggestions(
        self, 
        restaurant_slug: str,
        context: Optional[str] = None
    ) -> List[str]:
        """Get conversation starter suggestions"""
        
        # Get restaurant
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.slug == restaurant_slug,
            Restaurant.is_active == True
        ).first()
        
        if not restaurant:
            return []
        
        # Get menu context
        menu_context = await self._get_menu_context(restaurant.id)
        
        # Generate context-based suggestions
        suggestions = [
            "What are your most popular dishes?",
            "Do you have any signature items I should try?",
            "Can you recommend something for someone who likes [cuisine type]?",
            "What's good for sharing?",
            "Do you have vegetarian/vegan options?"
        ]
        
        # Add restaurant-specific suggestions
        if restaurant.cuisine_type:
            suggestions.insert(2, f"What makes your {restaurant.cuisine_type} food special?")
        
        return suggestions[:5]
    
    def record_chat_feedback(
        self, 
        restaurant_slug: str,
        feedback_data: Dict[str, Any]
    ) -> bool:
        """Record chat feedback"""
        
        # Get restaurant
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.slug == restaurant_slug,
            Restaurant.is_active == True
        ).first()
        
        if not restaurant:
            return False
        
        # Record feedback analytics
        self._record_interaction_analytics(
            restaurant_id=restaurant.id,
            conversation_id=feedback_data.get("conversation_id"),
            event_type="chat_feedback",
            event_data=feedback_data
        )
        
        self.db.commit()
        return True
    
    def get_chat_analytics(
        self, 
        restaurant_slug: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get chat analytics for a restaurant"""
        
        # Get restaurant
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.slug == restaurant_slug,
            Restaurant.is_active == True
        ).first()
        
        if not restaurant:
            return {}
        
        # For Phase 1, return mock analytics
        # In Phase 2, implement real analytics
        
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "avg_conversation_length": 0,
            "common_topics": [],
            "satisfaction_rating": 0,
            "response_time_avg": 0,
            "period_days": days
        }