#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 СИСТЕМА ДУБЛИРОВАНИЯ ПОДЗАДАЧ
Находит существующие подзадачи в гайде и создает их дубли для новой задачи
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# Загружаем переменные окружения
load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"
CHECKLISTS_DB = "9c5f4269d61449b6a7485579a3c21da3"

class DuplicateSubtasksSystem:
    """Система дублирования подзадач"""
    
    def __init__(self):
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN не найден в переменных окружения")
        self.client = AsyncClient(auth=token)
    
    async def create_task_with_duplicated_subtasks(self, guide_id: str, task_title: str, task_url: str = None):
        """
        Создает задачу и дублирует существующие подзадачи из гайда
        
        Args:
            guide_id: ID гайда
            task_title: Название задачи
            task_url: URL задачи (опционально)
        """
        
        print(f"🔄 СОЗДАНИЕ ЗАДАЧИ С ДУБЛИРОВАННЫМИ ПОДЗАДАЧАМИ")
        print("=" * 70)
        
        try:
            # 1. Получаем информацию о гайде
            print(f"1️⃣ Получение информации о гайде...")
            guide = await self.client.pages.retrieve(page_id=guide_id)
            guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Неизвестный гайд')
            
            print(f"✅ Гайд: {guide_title}")
            print(f"   🆔 {guide_id}")
            
            # 2. Находим существующие подзадачи в гайде
            print(f"\n2️⃣ Поиск существующих подзадач в гайде...")
            existing_subtasks = await self._find_existing_subtasks(guide_id)
            
            if not existing_subtasks:
                print("⚠️ Подзадачи не найдены в гайде")
                return None
            
            print(f"✅ Найдено подзадач: {len(existing_subtasks)}")
            for subtask in existing_subtasks:
                status = "✅" if subtask.get('checked', False) else "❌"
                print(f"   {status} {subtask['content']} (ID: {subtask['block_id']})")
            
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
            
            # 4. Дублируем подзадачи и привязываем к задаче
            print(f"\n4️⃣ Дублирование подзадач...")
            duplicated_subtasks = await self._duplicate_and_attach_subtasks(task_id, existing_subtasks)
            
            # 5. Проверяем результат
            print(f"\n5️⃣ Проверка результата...")
            print(f"✅ Дублировано подзадач: {len(duplicated_subtasks)}")
            print(f"✅ Привязано к задаче: {len(duplicated_subtasks)}")
            print(f"🎯 Задача с дублированными подзадачами готова!")
            
            return {
                'task_id': task_id,
                'guide_id': guide_id,
                'guide_title': guide_title,
                'subtasks_count': len(duplicated_subtasks),
                'subtask_ids': [s['id'] for s in duplicated_subtasks],
                'original_subtasks': existing_subtasks,
                'task_url': f"https://www.notion.so/dreamclub22/{task_id.replace('-', '')}",
                'guide_url': f"https://www.notion.so/dreamclub22/{guide_id.replace('-', '')}"
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    async def _find_existing_subtasks(self, guide_id: str):
        """Находит существующие подзадачи в гайде"""
        
        guide_blocks = await self.client.blocks.children.list(block_id=guide_id)
        blocks = guide_blocks.get('results', [])
        
        subtasks = []
        for block in blocks:
            if block.get('type') == 'to_do':
                content = block['to_do']['rich_text'][0]['text']['content'] if block['to_do']['rich_text'] else 'Без текста'
                checked = block['to_do']['checked']
                subtasks.append({
                    'content': content,
                    'checked': checked,
                    'block_id': block['id']
                })
        
        return subtasks
    
    async def _duplicate_and_attach_subtasks(self, task_id: str, existing_subtasks: list):
        """Дублирует подзадачи и привязывает к задаче"""
        
        duplicated_subtasks = []
        
        for subtask in existing_subtasks:
            # Создаем дубликат подзадачи в базе чеклистов
            subtask_data = {
                "parent": {"database_id": CHECKLISTS_DB},
                "properties": {
                    "Подзадачи": {
                        "title": [{
                            "type": "text",
                            "text": {"content": subtask['content']}
                        }]
                    },
                    "Задачи": {
                        "relation": [{"id": task_id}]
                    }
                }
            }
            
            # Создаем дубликат
            new_subtask = await self.client.pages.create(**subtask_data)
            subtask_id = new_subtask['id']
            
            duplicated_subtasks.append({
                'id': subtask_id,
                'content': subtask['content'],
                'checked': subtask.get('checked', False),
                'original_block_id': subtask['block_id']
            })
            
            status = "✅" if subtask.get('checked', False) else "❌"
            print(f"   📋 {status} {subtask['content']}")
            print(f"      🆔 Дубликат: {subtask_id}")
            print(f"      🔗 Оригинал: {subtask['block_id']}")
        
        return duplicated_subtasks
    
    async def batch_create_tasks_with_duplicated_subtasks(self, tasks_data: list):
        """
        Создает несколько задач с дублированными подзадачами
        
        Args:
            tasks_data: Список словарей с данными задач
                       [{'guide_id': '...', 'task_title': '...', 'task_url': '...'}]
        """
        
        print(f"🚀 МАССОВОЕ СОЗДАНИЕ ЗАДАЧ С ДУБЛИРОВАННЫМИ ПОДЗАДАЧАМИ")
        print("=" * 70)
        print(f"📋 Всего задач для создания: {len(tasks_data)}")
        
        results = []
        
        for i, task_data in enumerate(tasks_data, 1):
            print(f"\n📋 Задача {i}/{len(tasks_data)}")
            print("-" * 50)
            
            result = await self.create_task_with_duplicated_subtasks(
                guide_id=task_data['guide_id'],
                task_title=task_data['task_title'],
                task_url=task_data.get('task_url')
            )
            
            if result:
                results.append(result)
                print(f"✅ Успешно создана с {result['subtasks_count']} дублированными подзадачами")
            else:
                print(f"❌ Ошибка создания")
        
        print(f"\n🎯 ИТОГИ:")
        print(f"✅ Успешно создано: {len(results)}")
        print(f"❌ Ошибок: {len(tasks_data) - len(results)}")
        
        return results

# Функции для удобного использования
async def create_task_with_duplicated_subtasks(guide_id: str, task_title: str, task_url: str = None):
    """Создает одну задачу с дублированными подзадачами"""
    system = DuplicateSubtasksSystem()
    return await system.create_task_with_duplicated_subtasks(guide_id, task_title, task_url)

async def batch_create_tasks_with_duplicated_subtasks(tasks_data: list):
    """Создает несколько задач с дублированными подзадачами"""
    system = DuplicateSubtasksSystem()
    return await system.batch_create_tasks_with_duplicated_subtasks(tasks_data)

# Тестовый пример
if __name__ == "__main__":
    async def test_example():
        # Создаем задачу с дублированными подзадачами
        result = await create_task_with_duplicated_subtasks(
            guide_id="20face03-d9ff-8176-9357-ee1f5c52e5a5",
            task_title="Тестовая задача с дублированными подзадачами",
            task_url="https://example.com/test"
        )
        
        if result:
            print(f"\n🎉 ТЕСТ УСПЕШЕН!")
            print(f"📋 Задача: {result['task_url']}")
            print(f"📚 Гайд: {result['guide_url']}")
            print(f"📋 Подзадач дублировано: {result['subtasks_count']}")
            print(f"🆔 ID дубликатов: {result['subtask_ids']}")
            
            print(f"\n📋 ОРИГИНАЛЬНЫЕ ПОДЗАДАЧИ:")
            for subtask in result['original_subtasks']:
                status = "✅" if subtask.get('checked', False) else "❌"
                print(f"   {status} {subtask['content']} (ID: {subtask['block_id']})")
    
    asyncio.run(test_example()) 