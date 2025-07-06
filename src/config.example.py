"""Example configuration file for the application.

Copy this file to config.py and update with your values.
"""
from pathlib import Path
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Resolve .env path relative to project root  
ENV_PATH = Path(__file__).parent.parent / '.env'

# Load environment variables from the correct location
load_dotenv(ENV_PATH)

# Default database IDs for development
DEFAULT_DBS = {
    "tasks": "your_tasks_db_id_here",
    "learning": "your_learning_db_id_here",
    "projects": "your_projects_db_id_here",
    "guides": "your_guides_db_id_here"
}

class Settings(BaseSettings):
    """Main application settings."""
    
    # Required configuration with defaults for development
    TELEGRAM_BOT_TOKEN: str = "your_telegram_token_here"
    NOTION_API_KEY: str = "your_notion_token_here"
    
    # Optional Notion databases with defaults
    NOTION_TASKS_DB_ID: str = DEFAULT_DBS["tasks"]
    NOTION_LEARNING_DB_ID: str = DEFAULT_DBS["learning"]
    NOTION_PROJECTS_DB_ID: str = DEFAULT_DBS["projects"]
    NOTION_GUIDES_DB_ID: str = DEFAULT_DBS["guides"]
    
    # Other optional databases
    NOTION_IDEAS_DB_ID: Optional[str] = None
    NOTION_EPICS_DB_ID: Optional[str] = None
    NOTION_MATERIALS_DB_ID: Optional[str] = None
    NOTION_CHECKLISTS_DB_ID: Optional[str] = None
    NOTION_LINKS_DB_ID: Optional[str] = None
    
    # LLM settings
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_API_URL: str = "https://hubai.loe.gg/v1"
    
    # Local LLM settings
    USE_LOCAL_MODEL: bool = False
    LOCAL_MODEL_PATH: Optional[str] = None
    LOCAL_MODEL_TYPE: str = "ggml"
    
    # Other settings
    ADMIN_USER_IDS: Optional[str] = None
    
    class Config:
        env_file = ENV_PATH
        case_sensitive = True

    def get_notion_headers(self) -> Dict[str, str]:
        """Get headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
    def get_deepseek_headers(self) -> Dict[str, str]:
        """Get headers for Deepseek API requests."""
        if not self.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is not set")
        return {
            "Authorization": f"Bearer {self.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
    @property
    def NOTION_DATABASES(self) -> Dict[str, Optional[str]]:
        """Get mapping of database names to their IDs."""
        return {
            "tasks": self.NOTION_TASKS_DB_ID,
            "learning": self.NOTION_LEARNING_DB_ID,
            "projects": self.NOTION_PROJECTS_DB_ID,
            "guides": self.NOTION_GUIDES_DB_ID,
            "ideas": self.NOTION_IDEAS_DB_ID,
            "epics": self.NOTION_EPICS_DB_ID,
            "materials": self.NOTION_MATERIALS_DB_ID,
            "checklists": self.NOTION_CHECKLISTS_DB_ID,
            "links": self.NOTION_LINKS_DB_ID
        }

    def validate_required_databases(self, required_dbs: list[str], strict: bool = False) -> None:
        """Validate that required database IDs are set.
        
        Args:
            required_dbs: List of database names that must have IDs set
            strict: If True, raises error when IDs not set. If False, just warns.
            
        Raises:
            ValueError: If strict=True and any required database ID is not set
        """
        for db_name in required_dbs:
            if not self.NOTION_DATABASES.get(db_name):
                msg = f"Required database ID for {db_name} is not set"
                if strict:
                    raise ValueError(msg)
                print(f"Warning: {msg}")

# Create settings instance
settings = Settings()

# Export settings and tokens
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
NOTION_API_KEY = settings.NOTION_API_KEY

# Validate required databases but don't raise errors
settings.validate_required_databases(["tasks", "learning"], strict=False) 