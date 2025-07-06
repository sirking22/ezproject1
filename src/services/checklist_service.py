#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 УПРОЩЕННЫЙ СЕРВИС ЧЕКЛИСТОВ

Интеграция в основной проект Notion-Telegram-LLM.
Минимальная версия без избыточных полей.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from notion_client import AsyncClient

from ..core.config import settings
from ..models.base import BaseModel
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

print('DEBUG: checklist_service.py loaded')

class ChecklistService(BaseModel):
    """Упрощенный сервис для работы с чеклистами"""
    
    def __init__(self):
        super().__init__()
        self.client = AsyncClient(auth=settings.NOTION_TOKEN)
        
        # ID баз данных
        self.databases = {
            'tasks': 'd09df250ce7e4e0d9fbe4e036d320def',
            'guides': '47c6086858d442ebaeceb4fad1b23ba3',
            'checklists': '9c5f4269d61449b6a7485579a3c21da3'
        }
    
    async def extract_checklists_from_guide(self, guide_content: str) -> List[Dict[str, Any]]:
        """Извлекает чеклисты из контента гайда"""
        
        checklists = []
        
        # Простые паттерны для поиска чеклистов
        patterns = [
            r'## ✅ Чеклист качества:(.*?)(?=##|\Z)',
            r'## 📋 Чеклист:(.*?)(?=##|\Z)',
            r'## ✅ Чеклист:(.*?)(?=##|\Z)',
            r'### Чеклист:(.*?)(?=###|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, guide_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match.strip():
                    # Извлекаем отдельные пункты
                    items = re.findall(r'- \[ \] (.*?)(?=\n- \[ \]|\n##|\n###|\Z)', match, re.DOTALL)
                    if items:
                        checklists.append({
                            'title': 'Чеклист из гайда',
                            'items': [item.strip() for item in items if item.strip()]
                        })
        
        return checklists
    
    async def create_checklist_item(self, title: str, items: List[str], task_id: str, guide_id: str = None) -> Optional[str]:
        """Создает запись чеклиста (только необходимые поля)"""
        
        try:
            # Создаем контент чеклиста
            checklist_content = []
            for item in items:
                checklist_content.append({
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": item}}],
                        "checked": False
                    }
                })
            
            # ТОЛЬКО НЕОБХОДИМЫЕ ПОЛЯ
            properties = {
                "Подзадачи": {
                    "title": [{"text": {"content": title}}]
                },
                "Статус": {
                    "status": {"name": "To do"}
                },
                "Приоритет": {
                    "select": {"name": "Средний"}
                }
            }
            
            # Добавляем связи
            if task_id:
                properties["Задачи"] = {
                    "relation": [{"id": task_id}]
                }
            
            if guide_id:
                properties["📬 Гайды"] = {
                    "relation": [{"id": guide_id}]
                }
            
            # Создаем страницу чеклиста
            response = await self.client.pages.create(
                parent={"database_id": self.databases['checklists']},
                properties=properties,
                children=[
                    {
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"type": "text", "text": {"content": "Чеклист"}}]
                        }
                    },
                    *checklist_content,
                    {
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": f"Создан автоматически как копия из гайда. Пунктов: {len(items)}"}}]
                        }
                    }
                ]
            )
            
            checklist_id = response['id']
            logger.info(f"✅ Создан чеклист: {title} ({len(items)} пунктов)")
            
            return checklist_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания чеклиста: {e}")
            return None
    
    async def process_task_creation(self, task_id: str) -> int:
        """Обрабатывает создание новой задачи"""
        
        logger.info(f"🎯 Обработка задачи: {task_id}")
        
        try:
            # Получаем информацию о задаче
            task = await self.client.pages.retrieve(page_id=task_id)
            task_properties = task.get('properties', {})
            
            # Проверяем связанные гайды
            guides_relation = task_properties.get('📬 Гайды', {}).get('relation', [])
            
            if not guides_relation:
                logger.info("ℹ️ Нет связанных гайдов - чеклисты не создаются")
                return 0
            
            logger.info(f"📚 Найдено связанных гайдов: {len(guides_relation)}")
            
            total_checklists = 0
            
            # Обрабатываем каждый гайд
            for guide_relation in guides_relation:
                guide_id = guide_relation['id']
                
                # Получаем контент гайда
                guide = await self.client.pages.retrieve(page_id=guide_id)
                guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Неизвестный гайд')
                
                logger.info(f"📖 Обработка гайда: {guide_title}")
                
                # Получаем контент гайда
                guide_content = await self.get_guide_content(guide_id)
                
                if guide_content:
                    # Извлекаем чеклисты
                    checklists = await self.extract_checklists_from_guide(guide_content)
                    
                    if checklists:
                        logger.info(f"✅ Найдено чеклистов: {len(checklists)}")
                        
                        # Создаем копии чеклистов
                        for checklist in checklists:
                            checklist_title = f"Чеклист: {guide_title}"
                            checklist_id = await self.create_checklist_item(
                                title=checklist_title,
                                items=checklist['items'],
                                task_id=task_id,
                                guide_id=guide_id
                            )
                            
                            if checklist_id:
                                total_checklists += 1
                    else:
                        logger.info("ℹ️ Чеклисты в гайде не найдены")
                else:
                    logger.info("ℹ️ Контент гайда не найден")
            
            logger.info(f"📊 ИТОГО: Создано чеклистов: {total_checklists}")
            return total_checklists
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки задачи: {e}")
            return 0
    
    async def get_guide_content(self, guide_id: str) -> Optional[str]:
        """Получает контент гайда"""
        
        try:
            # Получаем блоки гайда
            blocks = await self.client.blocks.children.list(block_id=guide_id)
            
            content = []
            for block in blocks.get('results', []):
                if block['type'] == 'paragraph':
                    rich_text = block['paragraph'].get('rich_text', [])
                    if rich_text:
                        content.append(rich_text[0]['text']['content'])
                elif block['type'] == 'heading_2':
                    rich_text = block['heading_2'].get('rich_text', [])
                    if rich_text:
                        content.append(f"## {rich_text[0]['text']['content']}")
                elif block['type'] == 'heading_3':
                    rich_text = block['heading_3'].get('rich_text', [])
                    if rich_text:
                        content.append(f"### {rich_text[0]['text']['content']}")
                elif block['type'] == 'to_do':
                    rich_text = block['to_do'].get('rich_text', [])
                    checked = block['to_do'].get('checked', False)
                    if rich_text:
                        checkbox = "[x]" if checked else "[ ]"
                        content.append(f"- {checkbox} {rich_text[0]['text']['content']}")
            
            return "\n".join(content)
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения контента гайда: {e}")
            return None
    
    async def setup_checklist_automation(self) -> bool:
        """Настраивает автоматизацию чеклистов"""
        
        logger.info("🚀 Настройка упрощенной автоматизации чеклистов")
        
        try:
            # Проверяем базу чеклистов
            database = await self.client.databases.retrieve(
                database_id=self.databases['checklists']
            )
            logger.info(f"✅ База чеклистов найдена: {database['title'][0]['text']['content']}")
            
            # Проверяем наличие ключевых полей
            properties = database.get('properties', {})
            required_fields = ['Подзадачи', 'Статус', 'Задачи']
            
            missing_fields = []
            for field in required_fields:
                if field not in properties:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"⚠️ Отсутствуют поля: {', '.join(missing_fields)}")
                return False
            
            logger.info("✅ База чеклистов готова к использованию")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки: {e}")
            return False

    async def copy_checklists_from_guides_to_task(self, task_id: str) -> int:
        """Копирует чеклисты из всех связанных с задачей гайдов в задачу (универсально)"""
        return await self.process_task_creation(task_id)

    # process_task_creation оставляем как алиас для обратной совместимости
    process_task_creation = copy_checklists_from_guides_to_task


# Глобальный экземпляр сервиса
checklist_service = ChecklistService() 