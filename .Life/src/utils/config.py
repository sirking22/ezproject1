"""Configuration management for the application."""
from typing import Dict, Optional, Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Project info
    PROJECT_NAME: str = "Global Impact Ideas Platform"
    VERSION: str = "0.1.0"
    
    # API Keys
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Notion Database IDs
    NOTION_DATABASES: Dict[str, Optional[str]] = {
        "ideas": os.getenv("NOTION_IDEAS_DB_ID"),
        "projects": os.getenv("NOTION_PROJECTS_DB_ID"),
        "resources": os.getenv("NOTION_RESOURCES_DB_ID"),
        "metrics": os.getenv("NOTION_METRICS_DB_ID"),
        "collaborators": os.getenv("NOTION_COLLABORATORS_DB_ID")
    }
    
    # LLM Configuration
    DEFAULT_MODEL: str = "deepseek/deepseek-chat-v3-0324:free"  # Latest 685B MoE model
    SPECIAL_MODEL: str = "deepseek/deepseek-r1-distill-llama-70b:free"  # For math & code
    LLM_TEMPERATURE: float = 0.7
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    
    # Model selection based on task type
    TASK_TYPE: Literal["default", "special"] = "default"
    
    @property
    def current_model(self) -> str:
        """Get the appropriate model based on task type."""
        return self.SPECIAL_MODEL if self.TASK_TYPE == "special" else self.DEFAULT_MODEL
    
    # Telegram Bot Configuration
    BOT_COMMAND_PREFIX: str = "/"
    BOT_HELP_TEXT: str = """🌍 Global Impact Ideas Bot

Commands:
/new - Add a new impact idea
/list - View your impact ideas
/analyze - Analyze an existing idea
/priority - Show priority ideas
/trends - Show global impact trends
/set_model - Выбрать модель (обычная/специальная)

Let's make the world better together! 🚀"""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Validate required settings
if not settings.TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required")
if not settings.NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN is required")
if not settings.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required")
if not settings.NOTION_DATABASES["ideas"]:
    raise ValueError("NOTION_IDEAS_DB_ID is required")

def get_notion_headers(self) -> Dict[str, str]:
    """Get headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {self.NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

def get_openrouter_headers(self) -> Dict[str, str]:
    """Get headers for OpenRouter API requests."""
    return {
        "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/your-repo",  # Replace with your repo
        "X-Title": self.PROJECT_NAME
    }

def validate_notion_config(self) -> None:
    """Validate Notion configuration.
    
    Raises:
        ValueError: If required configuration is missing
    """
    if not self.NOTION_TOKEN:
        raise ValueError("NOTION_TOKEN must be set")
        
    required_dbs = ["ideas"]  # Add more as needed
    missing_dbs = [db for db in required_dbs if not self.NOTION_DATABASES.get(db)]
    if missing_dbs:
        raise ValueError(f"Missing required Notion database IDs: {', '.join(missing_dbs)}")
        
def validate_llm_config(self) -> None:
    """Validate LLM configuration.
    
    Raises:
        ValueError: If required configuration is missing
    """
    if not self.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY must be set") 