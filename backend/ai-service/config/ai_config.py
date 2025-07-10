"""
AI Configuration Management
Handles restaurant-specific AI settings and modes
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from enum import Enum
import json

class AIMode(Enum):
    """AI interaction modes"""
    TEXT_ONLY = "text_only"           # No speech features
    SPEECH_ENABLED = "speech_enabled" # Full speech capabilities  
    HYBRID = "hybrid"                 # User can toggle speech on/off

class ModelType(Enum):
    """OpenAI model types"""
    GPT_4O_MINI = "gpt-4o-mini"      # Fast, cost-effective
    GPT_4O = "gpt-4o"                # Balanced performance
    GPT_4_TURBO = "gpt-4-turbo"      # High performance
    GPT_3_5_TURBO = "gpt-3.5-turbo" # Budget option

@dataclass
class SpeechConfig:
    """Speech-related configuration"""
    synthesis_enabled: bool = True
    recognition_enabled: bool = True
    default_voice: str = "nova"
    voice_selection_enabled: bool = True
    auto_play: bool = True

@dataclass
class ModelConfig:
    """AI model configuration"""
    model: ModelType = ModelType.GPT_4O_MINI
    max_tokens: int = 150
    temperature: float = 0.7
    system_prompt_override: Optional[str] = None
    context_messages: int = 10  # Number of messages to keep in context

@dataclass
class PerformanceConfig:
    """Performance and cost settings"""
    streaming_enabled: bool = True
    cache_responses: bool = True
    max_daily_requests: int = 1000
    max_daily_cost_usd: float = 10.0
    rate_limit_per_minute: int = 60

@dataclass
class RestaurantAIConfig:
    """Complete AI configuration for a restaurant"""
    mode: AIMode = AIMode.TEXT_ONLY
    speech: SpeechConfig = None
    model: ModelConfig = None
    performance: PerformanceConfig = None
    custom_features: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default configs if not provided"""
        if self.speech is None:
            self.speech = SpeechConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.custom_features is None:
            self.custom_features = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage"""
        return {
            "mode": self.mode.value,
            "speech": asdict(self.speech),
            "model": {
                "model": self.model.model.value,
                "max_tokens": self.model.max_tokens,
                "temperature": self.model.temperature,
                "system_prompt_override": self.model.system_prompt_override,
                "context_messages": self.model.context_messages
            },
            "performance": asdict(self.performance),
            "custom_features": self.custom_features
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RestaurantAIConfig':
        """Create from dictionary (from JSON storage)"""
        config = cls()
        
        # Parse mode
        if "mode" in data:
            config.mode = AIMode(data["mode"])
        
        # Parse speech config
        if "speech" in data:
            config.speech = SpeechConfig(**data["speech"])
        
        # Parse model config
        if "model" in data:
            model_data = data["model"]
            config.model = ModelConfig(
                model=ModelType(model_data.get("model", "gpt-4o-mini")),
                max_tokens=model_data.get("max_tokens", 150),
                temperature=model_data.get("temperature", 0.7),
                system_prompt_override=model_data.get("system_prompt_override"),
                context_messages=model_data.get("context_messages", 10)
            )
        
        # Parse performance config
        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])
        
        # Parse custom features
        if "custom_features" in data:
            config.custom_features = data["custom_features"]
        
        return config
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RestaurantAIConfig':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_speech_enabled(self) -> bool:
        """Check if any speech features are enabled"""
        return (
            self.mode in [AIMode.SPEECH_ENABLED, AIMode.HYBRID] and
            (self.speech.synthesis_enabled or self.speech.recognition_enabled)
        )
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Get configuration for frontend consumption"""
        return {
            "mode": self.mode.value,
            "speech_synthesis_enabled": (
                self.mode != AIMode.TEXT_ONLY and 
                self.speech.synthesis_enabled
            ),
            "speech_recognition_enabled": (
                self.mode != AIMode.TEXT_ONLY and 
                self.speech.recognition_enabled
            ),
            "voice_selection_enabled": (
                self.is_speech_enabled() and 
                self.speech.voice_selection_enabled
            ),
            "default_voice": self.speech.default_voice,
            "streaming_enabled": self.performance.streaming_enabled,
            "auto_play": self.speech.auto_play,
            "max_tokens": self.model.max_tokens
        }

class AIConfigManager:
    """Manages AI configurations for restaurants"""
    
    @staticmethod
    def get_default_config() -> RestaurantAIConfig:
        """Get default configuration for new restaurants"""
        return RestaurantAIConfig(
            mode=AIMode.TEXT_ONLY,
            speech=SpeechConfig(
                synthesis_enabled=False,
                recognition_enabled=False,
                default_voice="nova",
                voice_selection_enabled=False,
                auto_play=False
            ),
            model=ModelConfig(
                model=ModelType.GPT_4O_MINI,
                max_tokens=150,
                temperature=0.7,
                context_messages=10
            ),
            performance=PerformanceConfig(
                streaming_enabled=True,
                cache_responses=True,
                max_daily_requests=1000,
                max_daily_cost_usd=10.0,
                rate_limit_per_minute=60
            )
        )
    
    @staticmethod
    def get_speech_enabled_config() -> RestaurantAIConfig:
        """Get configuration with speech features enabled"""
        config = AIConfigManager.get_default_config()
        config.mode = AIMode.SPEECH_ENABLED
        config.speech.synthesis_enabled = True
        config.speech.recognition_enabled = True
        config.speech.voice_selection_enabled = True
        config.speech.auto_play = True
        return config
    
    @staticmethod
    def get_hybrid_config() -> RestaurantAIConfig:
        """Get hybrid configuration (user can toggle speech)"""
        config = AIConfigManager.get_speech_enabled_config()
        config.mode = AIMode.HYBRID
        return config
    
    @staticmethod
    def validate_config(config: RestaurantAIConfig) -> tuple[bool, str]:
        """
        Validate configuration
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check model tokens
            if config.model.max_tokens < 10 or config.model.max_tokens > 4000:
                return False, "max_tokens must be between 10 and 4000"
            
            # Check temperature
            if config.model.temperature < 0 or config.model.temperature > 2:
                return False, "temperature must be between 0 and 2"
            
            # Check context messages
            if config.model.context_messages < 1 or config.model.context_messages > 50:
                return False, "context_messages must be between 1 and 50"
            
            # Check daily limits
            if config.performance.max_daily_cost_usd < 0:
                return False, "max_daily_cost_usd must be positive"
            
            if config.performance.max_daily_requests < 1:
                return False, "max_daily_requests must be at least 1"
            
            # Check rate limiting
            if config.performance.rate_limit_per_minute < 1:
                return False, "rate_limit_per_minute must be at least 1"
            
            return True, ""
            
        except Exception as e:
            return False, f"Configuration validation error: {str(e)}"