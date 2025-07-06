from notion_client import Client
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class NotionManager:
    def __init__(self):
        self.client = Client(auth=os.getenv("NOTION_TOKEN"))
        
    async def sync_database(self, database_id: str) -> List[Dict]:
        """Получает данные из базы данных Notion"""
        try:
            response = self.client.databases.query(database_id=database_id)
            return response["results"]
        except Exception as e:
            print(f"Ошибка при синхронизации с Notion: {e}")
            return []
    
    async def create_page(self, database_id: str, properties: Dict) -> Dict:
        """Создает новую страницу в базе данных Notion"""
        try:
            return self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
        except Exception as e:
            print(f"Ошибка при создании страницы в Notion: {e}")
            return {}
    
    async def update_page(self, page_id: str, properties: Dict) -> Dict:
        """Обновляет существующую страницу в Notion"""
        try:
            return self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
        except Exception as e:
            print(f"Ошибка при обновлении страницы в Notion: {e}")
            return {}

notion_manager = NotionManager() 