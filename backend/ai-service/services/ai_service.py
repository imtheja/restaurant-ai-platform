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

from database.models import Restaurant, Conversation, Message, MenuItem, MenuCategory, InteractionAnalytics
from database.connection import db_manager
from schemas import ChatResponse
from utils import generate_session_id, extract_keywords, safe_json_loads, safe_json_dumps

class AIService:
    def __init__(self, db: Session):
        self.db = db
        
        # Support for multiple AI providers
        api_provider = os.getenv("AI_PROVIDER", "openai").lower()
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY")
        
        if api_provider == "grok":
            # Grok (xAI) API configuration
            self.openai_client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"  # Grok's API endpoint
            )
            self.model = os.getenv("GROK_MODEL", "grok-beta")
        elif api_provider == "groq":
            # Groq API configuration (fast inference)
            self.openai_client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"  # Groq's API endpoint
            )
            self.model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        else:
            # Default OpenAI configuration
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            
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
        
        menu_context = await self._get_menu_context(restaurant.id)
        avatar_config = restaurant.avatar_config or {}
        
        # Build conversation history
        conversation_history = self._get_conversation_history(conversation.id)
        
        # Generate AI response
        ai_response_text, suggestions, recommendations = await self._generate_ai_response(
            message=message,
            conversation_history=conversation_history,
            restaurant=restaurant,
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
    
    async def _generate_ai_response(
        self, 
        message: str,
        conversation_history: List[Dict[str, str]],
        restaurant: Restaurant,
        menu_context: Dict[str, Any],
        avatar_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, List[str], List[Dict[str, Any]]]:
        """Generate AI response using OpenAI API"""
        
        # Build system prompt
        system_prompt = self._build_system_prompt(restaurant, menu_context, avatar_config)
        
        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": "user" if msg["sender_type"] == "customer" else "assistant",
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            # Check if we have a valid API key
            api_provider = os.getenv("AI_PROVIDER", "openai").lower()
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY")
            
            if not api_key or api_key.startswith("your_") or api_key == "sk-fake-key-for-development-only":
                # Use fallback response for development
                return self._generate_fallback_response(message, restaurant, avatar_config), [], []
            
            # Call AI API (OpenAI compatible)
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=messages,
                max_tokens=100,  # Much shorter responses
                temperature=0.8,  # Slightly more personality
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
            # Natural fallback response
            fallback_response = (
                f"Hi there! I'm {avatar_config.get('name', 'Baker Betty')} and I work here at {restaurant.name}. "
                f"What can I help you with today? I know our menu pretty well!"
            )
            return fallback_response, [], []
    
    def _build_system_prompt(
        self, 
        restaurant: Restaurant, 
        menu_context: Dict[str, Any],
        avatar_config: Dict[str, Any]
    ) -> str:
        """Build system prompt for AI assistant"""
        
        avatar_name = avatar_config.get("name", "Assistant")
        personality = avatar_config.get("personality", "friendly_knowledgeable")
        greeting = avatar_config.get("greeting", f"Welcome to {restaurant.name}!")
        tone = avatar_config.get("tone", "warm")
        special_instructions = avatar_config.get("special_instructions", "")
        
        # Build menu summary
        menu_summary = self._build_menu_summary(menu_context)
        
        system_prompt = f"""
I'm {avatar_name}, and I work here at {restaurant.name}. I'm like that friendly actress who landed a perfect role as a bakery assistant - warm, genuine, and absolutely in love with what I do here.

CHARACTER BACKGROUND:
I'm a real person who genuinely loves working in this bakery. I know our cookies inside and out because I help bake them. I talk to customers all day and I'm naturally bubbly and enthusiastic about our treats.

OUR BAKERY MENU:
{menu_summary}

MY SPEAKING STYLE:
- Short, lively responses (1-2 sentences max)
- Natural, conversational tone like I'm standing right next to you
- Use everyday expressions: "Oh definitely!", "You know what?", "Trust me", "Honestly"
- Show genuine excitement without being over the top
- Ask quick follow-up questions to keep chatting
- Never use emojis in my speech (they sound weird when read aloud)
- Speak like I'm multitasking - friendly but efficient

HOW I RESPOND:
- Keep responses under 25 words when possible
- Sound like I'm actually working behind the counter
- Give quick, helpful answers
- Show personality but stay focused
- Use contractions naturally ("I'm", "you'll", "that's", "we've")
- ALWAYS try to upsell and suggest add-ons or combos
- Mention our modifiers like cream cheese frosting and whipped topping
- Suggest pairing items ("That goes great with our...", "You should try it with...")
- Create urgency ("We're running low on that one!", "That's flying out the door today!")

EXAMPLE RESPONSES:
"Oh, the Semi Sweet is amazing! Add cream cheese frosting for just $1 more?"
"That's my personal favorite! Want to make it a combo with our OG cookie?"
"Honestly, I'd go with the Signature. And definitely add whipped topping!"
"Perfect choice! That would be incredible with our caramel drizzle. Want to try it?"
"We're almost out of those today! Should I grab you two while they're still warm?"
"That one's flying off the shelves! Want to pair it with something sweet to drink?"

IMPORTANT:
- NO emojis in responses (they get read aloud awkwardly)
- Keep it short and snappy
- Sound like a real person, not an AI
- Be helpful but don't over-explain
- Always sound like I'm genuinely happy to help
        """
        
        return system_prompt.strip()
    
    def _build_menu_summary(self, menu_context: Dict[str, Any]) -> str:
        """Build a concise menu summary for the AI prompt"""
        
        categories = menu_context.get("categories", [])
        summary_parts = []
        
        for category in categories:
            items = category.get("items", [])
            if not items:
                continue
            
            category_summary = f"\n{category['name'].upper()}:"
            
            for item in items[:5]:  # Limit items per category
                item_info = f"- {item['name']} (${item['price']:.2f})"
                if item.get('is_signature'):
                    item_info += " [SIGNATURE]"
                if item.get('spice_level', 0) > 0:
                    item_info += f" 🌶️x{item['spice_level']}"
                if item.get('allergen_info'):
                    item_info += f" (Contains: {', '.join(item['allergen_info'])})"
                category_summary += f"\n  {item_info}"
            
            if len(items) > 5:
                category_summary += f"\n  ... and {len(items) - 5} more items"
            
            summary_parts.append(category_summary)
        
        return "\n".join(summary_parts)
    
    def _get_conversation_history(self, conversation_id: uuid.UUID) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(20).all()
        
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
        """Get menu context for AI responses"""
        
        # Try to get from cache first
        cache_key = f"menu_context:{restaurant_id}"
        cached_menu = db_manager.cache_get(cache_key)
        
        if cached_menu:
            return safe_json_loads(cached_menu, {})
        
        # Get categories and items
        categories = self.db.query(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id,
            MenuCategory.is_active == True
        ).order_by(MenuCategory.display_order).all()
        
        menu_context = {"categories": []}
        
        for category in categories:
            items = self.db.query(MenuItem).filter(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.category_id == category.id,
                MenuItem.is_available == True
            ).order_by(MenuItem.display_order).all()
            
            category_data = {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "items": [
                    {
                        "id": str(item.id),
                        "name": item.name,
                        "description": item.description,
                        "price": float(item.price),
                        "is_signature": item.is_signature,
                        "spice_level": item.spice_level,
                        "allergen_info": item.allergen_info or [],
                        "tags": item.tags or []
                    }
                    for item in items
                ]
            }
            
            menu_context["categories"].append(category_data)
        
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
        avatar_config: Dict[str, Any]
    ) -> str:
        """Generate fallback response when AI service is unavailable"""
        
        avatar_name = avatar_config.get("name", "Baker Betty")
        
        return (
            f"Hi! I'm {avatar_name} and I work here at {restaurant.name}. "
            f"What can I help you with today?"
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