"""Configuration for LLM models."""
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel


class DeepSeekModel(str, Enum):
    """Available DeepSeek models through OpenRouter."""
    
    CHAT = "deepseek-ai/deepseek-chat-v3"  # 685B универсальная модель
    CODE = "deepseek-ai/deepseek-llama-70b"  # Для кода и математики


class LLMConfig(BaseModel):
    """Configuration for LLM integration."""
    
    # OpenRouter settings
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Model settings
    default_model: DeepSeekModel = DeepSeekModel.CHAT
    max_tokens: int = 4096
    temperature: float = 0.7
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API requests."""
        return {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/your-username/notion-telegram-llm",  # Замените на ваш репозиторий
            "Content-Type": "application/json"
        }
    
    def get_model_name(self, model_type: Optional[DeepSeekModel] = None) -> str:
        """Get the full model name for API requests."""
        return (model_type or self.default_model).value 