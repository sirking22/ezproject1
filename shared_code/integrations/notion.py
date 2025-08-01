import os
import aiohttp
import json
from typing import Optional, Dict, Any

class NotionClient:
    """Универсальный клиент для Notion. Настройки берутся из env вызывающего проекта."""
    def __init__(self):
        self.api_key = os.getenv("NOTION_TOKEN")
        self.base_url = os.getenv("NOTION_BASE_URL", "https://api.notion.com/v1/")
        if not self.api_key:
            raise ValueError("NOTION_TOKEN должен быть задан в env")

    async def create_database(self, title: str, description: str, properties: Dict[str, Any], 
                            icon: str = "🏆", cover: str = "") -> str:
        """Создает новую базу данных в Notion"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Получаем ID родительской страницы из env
        parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
        if not parent_page_id:
            raise ValueError("NOTION_PARENT_PAGE_ID должен быть задан в env")
        
        data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"text": {"content": title}}],
            "properties": properties,
            "icon": {"type": "emoji", "emoji": icon}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}databases",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["id"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Ошибка создания базы данных: {response.status} - {error_text}")

    async def create_page(self, database_id: str, properties: Dict[str, Any]) -> Optional[str]:
        """Создает новую страницу в базе данных Notion"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Преобразуем свойства в формат Notion
        notion_properties = {}
        for key, value in properties.items():
            if isinstance(value, str):
                if key == "Компания/Продукт" or key == "Область силы" or key == "Название продукта" or key == "Название контента" or key == "Название правила" or key == "Название направления" or key == "Профиль клиента":
                    notion_properties[key] = {"title": [{"text": {"content": value}}]}
                elif key == "Веб-сайт" or key == "Социальные сети":
                    notion_properties[key] = {"url": value}
                elif key == "Последнее обновление" or key == "Сроки" or key == "Дата публикации":
                    notion_properties[key] = {"date": {"start": value}}
                elif key == "Категория" or key == "Отрасль" or key == "Позиционирование" or key == "Уровень влияния" or key == "Приоритет" or key == "Стадия производства" or key == "Статус" or key == "Тип контента" or key == "Платформа" or key == "Тип правила" or key == "Сегмент" or key == "Ценовой сегмент" or key == "Возраст" or key == "Доход" or key == "Тип" or key == "Уровень зрелости":
                    notion_properties[key] = {"select": {"name": value}}
                else:
                    notion_properties[key] = {"rich_text": [{"text": {"content": value}}]}
            elif isinstance(value, int) or isinstance(value, float):
                if key == "Рыночная доля" or key == "Успешность (%)":
                    notion_properties[key] = {"number": value / 100}  # Процент в десятичную дробь
                else:
                    notion_properties[key] = {"number": value}
            elif isinstance(value, list):
                notion_properties[key] = {"multi_select": [{"name": item} for item in value]}
            elif isinstance(value, dict):
                notion_properties[key] = value
            else:
                notion_properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        
        data = {
            "parent": {"database_id": database_id},
            "properties": notion_properties
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}pages",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["id"]
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка создания записи: {error_text}")
                    # Не прерываем выполнение, продолжаем с другими записями
                    return None

    def do_something(self):
        # TODO: реализовать вызовы к Notion
        pass 