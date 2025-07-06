from pydantic_settings import BaseSettings
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Knowledge Management System"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    
    # API Keys
    OPENAI_API_KEY: str
    NOTION_TOKEN: str
    
    # Notion Database IDs
    NOTION_DATABASES: Dict[str, str] = {
        "ideas": "",  # ID базы идей
        "guides": "",  # ID базы гайдов
        "projects": "",  # ID базы проектов
        "materials": "",  # ID базы материалов
        "products": "",  # ID базы товаров
        "employees": "",  # ID базы сотрудников
        "kpi": "",  # ID базы KPI
    }
    
    class Config:
        env_file = ".env"

settings = Settings() 