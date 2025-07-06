#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 АВТОМАТИЗИРОВАННАЯ СИСТЕМА ЧЕКЛИСТОВ
Создание задач из гайдов с автоматическим дублированием чеклистов
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"

class ChecklistAutomationSystem:
    """Система автоматизации чеклистов"""
    
    def __init__(self):
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN не найден в переменных окружения")
        self.client = AsyncClient(auth=token)
    
    async def create_task_from_guide(self, guide_id: str, task_title: str, task_url: str = None):
        """
        Создает задачу из гайда с автоматическим дублированием чеклистов
        
        Args:
            guide_id: ID гайда
            task_title: Название задачи
            task_url: URL задачи (опционально)
        """
        
        print(f"🤖 СОЗДАНИЕ ЗАДАЧИ ИЗ ГАЙДА")
        print("=" * 50)
        
        try:
            # 1. Получаем информацию о гайде
            print(f"1️⃣ Получение информации о гайде...")
            guide = await self.client.pages.retrieve(page_id=guide_id)
            guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Неизвестный гайд')
            
            print(f"✅ Гайд: {guide_title}")
            print(f"   🆔 {guide_id}")
            
            # 2. Извлекаем чеклисты из гайда
            print(f"\n2️⃣ Извлечение чеклистов из гайда...")
            checklist_items = await self._extract_checklists_from_guide(guide_id)
            
            if not checklist_items:
                print("⚠️ Чеклисты не найдены в гайде")
                return None
            
            print(f"✅ Найдено чеклистов: {len(checklist_items)}")
            for item in checklist_items:
                status = "✅" if item.get('checked', False) else "❌"
                print(f"   {status} {item['content']}")
            
            # 3. Создаем задачу
            print(f"\n3️⃣ Создание задачи...")
            task_data = {
                "parent": {"database_id": TASKS_DB},
                "properties": {
                    "Задача": {
                        "title": [{
                            "type": "text",
                            "text": {"content": task_title}
                        }]
                    },
                    "📬 Гайды": {
                        "relation": [{"id": guide_id}]
                    },
                    "Статус": {
                        "status": {"name": "In Progress"}
                    }
                }
            }
            
            # Добавляем URL если указан
            if task_url:
                task_data["properties"]["Ф задачи"] = {"url": task_url}
            
            new_task = await self.client.pages.create(**task_data)
            task_id = new_task['id']
            
            print(f"✅ Задача создана:")
            print(f"   🆔 {task_id}")
            print(f"   🔗 https://www.notion.so/dreamclub22/{task_id.replace('-', '')}")
            
            # 4. Добавляем чеклисты в задачу
            print(f"\n4️⃣ Добавление чеклистов в задачу...")
            await self._add_checklists_to_task(task_id, checklist_items)
            
            # 5. Проверяем результат
            print(f"\n5️⃣ Проверка результата...")
            final_checklists = await self._get_task_checklists(task_id)
            
            print(f"✅ Чеклистов добавлено: {len(final_checklists)}")
            print(f"🎯 Задача готова!")
            
            return {
                'task_id': task_id,
                'guide_id': guide_id,
                'guide_title': guide_title,
                'checklists_count': len(final_checklists),
                'task_url': f"https://www.notion.so/dreamclub22/{task_id.replace('-', '')}",
                'guide_url': f"https://www.notion.so/dreamclub22/{guide_id.replace('-', '')}"
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    async def _extract_checklists_from_guide(self, guide_id: str):
        """Извлекает чеклисты из гайда"""
        
        guide_blocks = await self.client.blocks.children.list(block_id=guide_id)
        blocks = guide_blocks.get('results', [])
        
        checklist_items = []
        for block in blocks:
            if block.get('type') == 'to_do':
                content = block['to_do']['rich_text'][0]['text']['content'] if block['to_do']['rich_text'] else 'Без текста'
                checked = block['to_do']['checked']
                checklist_items.append({
                    'content': content,
                    'checked': checked,
                    'block_id': block['id']
                })
        
        return checklist_items
    
    async def _add_checklists_to_task(self, task_id: str, checklist_items: list):
        """Добавляет чеклисты в задачу"""
        
        checklist_blocks = []
        for item in checklist_items:
            checklist_blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": item['content']}
                    }],
                    "checked": item.get('checked', False)
                }
            })
        
        await self.client.blocks.children.append(
            block_id=task_id,
            children=checklist_blocks
        )
        
        print(f"✅ Добавлено чеклистов: {len(checklist_blocks)}")
        for item in checklist_items:
            status = "✅" if item.get('checked', False) else "❌"
            print(f"   {status} {item['content']}")
    
    async def _get_task_checklists(self, task_id: str):
        """Получает чеклисты из задачи"""
        
        task_blocks = await self.client.blocks.children.list(block_id=task_id)
        return [b for b in task_blocks.get('results', []) if b.get('type') == 'to_do']
    
    async def batch_create_tasks(self, tasks_data: list):
        """
        Создает несколько задач из гайдов
        
        Args:
            tasks_data: Список словарей с данными задач
                       [{'guide_id': '...', 'task_title': '...', 'task_url': '...'}]
        """
        
        print(f"🚀 МАССОВОЕ СОЗДАНИЕ ЗАДАЧ")
        print("=" * 50)
        print(f"📋 Всего задач для создания: {len(tasks_data)}")
        
        results = []
        
        for i, task_data in enumerate(tasks_data, 1):
            print(f"\n📋 Задача {i}/{len(tasks_data)}")
            print("-" * 30)
            
            result = await self.create_task_from_guide(
                guide_id=task_data['guide_id'],
                task_title=task_data['task_title'],
                task_url=task_data.get('task_url')
            )
            
            if result:
                results.append(result)
                print(f"✅ Успешно создана")
            else:
                print(f"❌ Ошибка создания")
        
        print(f"\n🎯 ИТОГИ:")
        print(f"✅ Успешно создано: {len(results)}")
        print(f"❌ Ошибок: {len(tasks_data) - len(results)}")
        
        return results

# Функции для удобного использования
async def create_task_from_guide(guide_id: str, task_title: str, task_url: str = None):
    """Создает одну задачу из гайда"""
    system = ChecklistAutomationSystem()
    return await system.create_task_from_guide(guide_id, task_title, task_url)

async def batch_create_tasks(tasks_data: list):
    """Создает несколько задач из гайдов"""
    system = ChecklistAutomationSystem()
    return await system.batch_create_tasks(tasks_data)

# Пример использования
if __name__ == "__main__":
    # Тестовый пример
    async def test_example():
        # Создаем одну задачу
        result = await create_task_from_guide(
            guide_id="213ace03-d9ff-8139-a219-ecb38bc433bd",
            task_title="Тестовая задача из гайда",
            task_url="https://example.com/test"
        )
        
        if result:
            print(f"\n🎉 ПРИМЕР РАБОТЫ:")
            print(f"📋 Задача: {result['task_url']}")
            print(f"📚 Гайд: {result['guide_url']}")
            print(f"☐ Чеклистов: {result['checklists_count']}")
    
    asyncio.run(test_example()) 