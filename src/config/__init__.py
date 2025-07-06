"""Configuration module."""
from typing import Dict, Any, Optional
from functools import lru_cache
import os
from pathlib import Path
from pydantic import BaseSettings
from dotenv import load_dotenv


# Resolve .env path relative to this file
ENV_PATH = Path(__file__).parent.parent / '.env'

# Load environment variables from the correct location
load_dotenv(ENV_PATH)

class Settings(BaseSettings):
    """Application settings."""
    
    # Bot settings
    TELEGRAM_BOT_TOKEN: str
    
    # Notion settings
    NOTION_API_KEY: str
    NOTION_VERSION: str = "2022-06-28"
    
    # Notion databases
    NOTION_DATABASES: Dict[str, str] = {}
    
    # Local LLM settings
    LOCAL_MODEL_PATH: str = "models/llama-2-8b-chat.Q4_K_M.gguf"
    LOCAL_MODEL_TYPE: str = "llama"  # llama, mistral, phi
    USE_GPU: bool = True
    GPU_LAYERS: int = 32
    
    # Model parameters
    CONTEXT_WINDOW: int = 8192
    MAX_TOKENS: int = 2048
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Performance settings
    BATCH_SIZE: int = 512
    NUM_THREADS: int = 6
    USE_MLOCK: bool = True
    USE_MMAP: bool = True
    
    # Cache settings
    ENABLE_CACHE: bool = True
    CACHE_DIR: str = ".cache"
    MAX_CACHE_SIZE: int = 1000
    
    def get_notion_headers(self) -> Dict[str, str]:
        """Get headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.NOTION_API_KEY}",
            "Notion-Version": self.NOTION_VERSION,
            "Content-Type": "application/json"
        }
    
    def get_model_path(self) -> Path:
        """Get absolute path to model file."""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / self.LOCAL_MODEL_PATH
    
    def get_cache_path(self) -> Path:
        """Get absolute path to cache directory."""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / self.CACHE_DIR
    
    class Config:
        """Pydantic settings config."""
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create settings instance and export variables
settings = get_settings()
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN 