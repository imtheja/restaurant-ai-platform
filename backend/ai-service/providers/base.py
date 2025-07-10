"""
Base AI Provider Interface
Defines the contract that all AI providers must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, List, AsyncIterator, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class AIMessage:
    """Standard message format across all providers"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """Standard response format across all providers"""
    content: str
    model_used: str
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    response_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""
    provider_name: str
    model_name: str
    api_key: str
    api_endpoint: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    timeout_seconds: int = 30
    extra_params: Optional[Dict[str, Any]] = None

class BaseAIProvider(ABC):
    """Base class that all AI providers must inherit from"""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.provider_name = config.provider_name
        self.model_name = config.model_name
        
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        stream: bool = False
    ) -> AsyncIterator[str]:
        """
        Generate AI response
        
        Args:
            messages: List of conversation messages
            stream: Whether to stream the response
            
        Yields:
            str: Response tokens (for streaming) or complete response
        """
        pass
    
    @abstractmethod
    async def generate_speech(
        self, 
        text: str, 
        voice: str = "default"
    ) -> bytes:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            voice: Voice identifier
            
        Returns:
            bytes: Audio data
        """
        pass
    
    @abstractmethod
    async def transcribe_audio(
        self, 
        audio_data: bytes
    ) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data to transcribe
            
        Returns:
            str: Transcribed text
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices for speech synthesis
        
        Returns:
            List[Dict]: List of voice configurations
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dict: Model information including capabilities, costs, etc.
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the provider configuration
        
        Returns:
            bool: True if configuration is valid
        """
        pass
    
    def format_system_prompt(
        self, 
        restaurant_context: Dict[str, Any], 
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Format system prompt with restaurant context
        
        Args:
            restaurant_context: Restaurant-specific information
            custom_instructions: Additional custom instructions
            
        Returns:
            str: Formatted system prompt
        """
        base_prompt = f"""You are an AI assistant for {restaurant_context.get('name', 'this restaurant')}.

Restaurant Information:
- Name: {restaurant_context.get('name', 'N/A')}
- Cuisine: {restaurant_context.get('cuisine_type', 'N/A')}
- Description: {restaurant_context.get('description', 'N/A')}

Your role is to help customers with menu questions, recommendations, ingredients, allergens, and ordering decisions.
Be friendly, knowledgeable, and helpful. Keep responses concise but informative.

Menu Context:
{json.dumps(restaurant_context.get('menu_context', {}), indent=2)}
"""
        
        if custom_instructions:
            base_prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"
            
        return base_prompt
    
    def calculate_cost(self, tokens_used: int) -> float:
        """
        Calculate cost based on token usage
        Override in provider-specific implementations
        
        Args:
            tokens_used: Number of tokens used
            
        Returns:
            float: Cost in USD
        """
        return 0.0  # Default implementation
    
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and responsive
        
        Returns:
            bool: True if provider is healthy
        """
        try:
            # Simple test message
            test_messages = [
                AIMessage(role="user", content="Hello")
            ]
            
            response_generator = self.generate_response(test_messages, stream=False)
            response = await response_generator.__anext__()
            
            return len(response) > 0
        except Exception:
            return False