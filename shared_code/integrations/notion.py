import os
from typing import Optional

class NotionClient:
    """Универсальный клиент для Notion. Настройки берутся из env вызывающего проекта."""
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.base_url = os.getenv("NOTION_BASE_URL", "https://api.notion.com/v1/")
        if not self.api_key:
            raise ValueError("NOTION_API_KEY должен быть задан в env")

    def do_something(self):
        # TODO: реализовать вызовы к Notion
        pass 