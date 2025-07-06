#!/usr/bin/env python3
"""
🎯 ПРЯМОЕ ОБНОВЛЕНИЕ NOTION
Прямое применение изменений в Notion по ID записей
"""

import os
import json
import asyncio
from typing import Dict, List
from notion_client import AsyncClient
from datetime import datetime

class DirectNotionUpdater:
    """Прямое обновление Notion"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = "ad92a6e21485428c84de8587706b3be1"
        
        # Загружаем данные анализа
        self.analysis_data = self._load_analysis_data()
        
    def _load_analysis_data(self) -> Dict:
        """Загружает данные анализа"""
        try:
            with open("telegram_full_analysis.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {item["page_id"]: item for item in data}
                return data
        except FileNotFoundError:
            print("❌ Файл анализа не найден")
            return {}

    async def apply_direct_changes(self):
        """Применяет прямые изменения в Notion"""
        print("🎯 ПРЯМОЕ ОБНОВЛЕНИЕ NOTION")
        print("="*50)
        
        # Список изменений на основе ваших комментариев
        changes = [
            {
                'page_id': '1104',
                'action': 'delete',
                'reason': 'Устаревшая информация о брендинге'
            },
            {
                'page_id': '526', 
                'action': 'update',
                'title_cleanup': True,
                'description_cleanup': True,
                'add_tags': ['Дизайн', 'Видеогенераторы', 'Нейросети'],
                'set_importance': 5,
                'reason': 'Очистка от билиберды, добавление тегов для визуальных хуков'
            }
        ]
        
        applied = 0
        errors = 0
        
        for change in changes:
            try:
                page_id = change['page_id']
                print(f"📝 Обработка записи {page_id}: {change['reason']}")
                
                if change['action'] == 'delete':
                    await self._delete_page(page_id)
                    print(f"   🗑️ Удалена запись {page_id}")
                
                elif change['action'] == 'update':
                    await self._update_page_direct(page_id, change)
                    print(f"   ✅ Обновлена запись {page_id}")
                
                applied += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                errors += 1
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"✅ Применено: {applied}")
        print(f"❌ Ошибок: {errors}")

    async def _delete_page(self, page_id: str):
        """Удаляет страницу в Notion"""
        await self.notion.pages.update(
            page_id=page_id,
            archived=True  # Архивируем вместо удаления
        )

    async def _update_page_direct(self, page_id: str, change: Dict):
        """Прямое обновление страницы"""
        properties = {}
        
        # Получаем текущие данные записи
        if page_id in self.analysis_data:
            current_data = self.analysis_data[page_id]
            
            # Очистка названия
            if change.get('title_cleanup'):
                new_title = self._clean_title(current_data['current_title'])
                if new_title != current_data['current_title']:
                    properties["Name"] = {
                        "title": [
                            {
                                "text": {
                                    "content": new_title
                                }
                            }
                        ]
                    }
            
            # Очистка описания
            if change.get('description_cleanup'):
                new_description = self._clean_description(current_data.get('current_description', ''))
                if new_description != current_data.get('current_description', ''):
                    properties["Описание"] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": new_description
                                }
                            }
                        ]
                    }
            
            # Добавление тегов
            if change.get('add_tags'):
                current_tags = current_data.get('current_tags', [])
                new_tags = list(set(current_tags + change['add_tags']))
                properties["Теги"] = {
                    "multi_select": [
                        {"name": tag} for tag in new_tags
                    ]
                }
            
            # Установка важности
            if change.get('set_importance'):
                properties["Важность"] = {
                    "number": change['set_importance']
                }
        
        # Применяем изменения
        if properties:
            await self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )

    def _clean_title(self, title: str) -> str:
        """Очищает название от билиберды"""
        import re
        
        # Удаляем лишние пробелы
        title = re.sub(r'\s+', ' ', title)
        
        # Удаляем английские слова-мусор
        garbage_words = ['om', 'ok', "i'll", 'look', 'video', 'about', "i don't know what this is"]
        for word in garbage_words:
            title = re.sub(rf'\b{word}\b', '', title, flags=re.IGNORECASE)
        
        # Удаляем специальные символы
        title = re.sub(r'[^\w\s\-\.]', '', title)
        
        # Убираем пробелы в начале и конце
        title = title.strip()
        
        return title

    def _clean_description(self, description: str) -> str:
        """Очищает описание от мусора"""
        import re
        
        # Удаляем ссылки на Wildberries
        description = re.sub(r'https?://[^\s]*wildberries[^\s]*', '', description, flags=re.IGNORECASE)
        
        # Удаляем упоминания цветов (если не по теме)
        color_words = ['зеленый', 'голубой', 'красный', 'синий']
        for color in color_words:
            description = re.sub(rf'\b{color}\b', '', description, flags=re.IGNORECASE)
        
        # Удаляем лишние пробелы
        description = re.sub(r'\s+', ' ', description)
        
        return description.strip()

async def main():
    """Главная функция"""
    updater = DirectNotionUpdater()
    await updater.apply_direct_changes()

if __name__ == "__main__":
    asyncio.run(main()) 