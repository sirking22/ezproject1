#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Создание тестового гайда с чеклистами
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# Загружаем переменные окружения
load_dotenv()

GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"
TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
CHECKLISTS_DB = "9c5f4269d61449b6a7485579a3c21da3"

async def create_test_guide_with_checklist():
    """Создает тестовый гайд с чеклистами"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print("🧪 СОЗДАНИЕ ТЕСТОВОГО ГАЙДА С ЧЕКЛИСТАМИ")
    print("=" * 60)
    
    try:
        # 1. Создаем тестовый гайд
        print("1️⃣ Создание тестового гайда...")
        
        guide_properties = {
            "Name": {
                "title": [{"text": {"content": "🧪 Тестовый гайд с чеклистами"}}]
            },
            "Описание": {
                "rich_text": [{"text": {"content": "Тестовый гайд для проверки связки с задачами"}}]
            },
            "Статус": {
                "status": {"name": "Старт"}
            },
            "Guide Status": {
                "select": {"name": "Active"}
            }
        }
        
        guide_response = await client.pages.create(
            parent={"database_id": GUIDES_DB},
            properties=guide_properties,
            children=[
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "## ✅ Чеклист качества:"}}]
                    }
                },
                {
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": "Проверить все требования"}}],
                        "checked": False
                    }
                },
                {
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": "Протестировать функциональность"}}],
                        "checked": False
                    }
                },
                {
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": "Проверить совместимость"}}],
                        "checked": False
                    }
                },
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "## 📋 Чеклист:"}}]
                    }
                },
                {
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": "Создать документацию"}}],
                        "checked": False
                    }
                },
                {
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": "Провести код-ревью"}}],
                        "checked": False
                    }
                },
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Этот гайд создан для тестирования автоматического создания чеклистов из гайдов."}}]
                    }
                }
            ]
        )
        
        guide_id = guide_response['id']
        print(f"✅ Гайд создан: {guide_id}")
        
        # 2. Создаем тестовую задачу с этим гайдом
        print("\n2️⃣ Создание тестовой задачи...")
        
        task_properties = {
            "Ф задачи": {
                "url": "https://example.com/test-task"
            },
            "Описание": {
                "rich_text": [{"text": {"content": "Тестовая задача для проверки связки с гайдом"}}]
            },
            "Статус": {
                "status": {"name": "To do"}
            },
            "Категория": {
                "multi_select": [{"name": "Regular"}]
            },
            "📬 Гайды": {
                "relation": [{"id": guide_id}]
            }
        }
        
        task_response = await client.pages.create(
            parent={"database_id": TASKS_DB},
            properties=task_properties
        )
        
        task_id = task_response['id']
        print(f"✅ Задача создана: {task_id}")
        
        # 3. Тестируем извлечение чеклистов
        print("\n3️⃣ Тестирование извлечения чеклистов...")
        
        blocks = await client.blocks.children.list(block_id=guide_id)
        
        guide_text = []
        for block in blocks.get('results', []):
            block_type = block['type']
            
            if block_type == 'paragraph':
                rich_text = block['paragraph'].get('rich_text', [])
                if rich_text:
                    guide_text.append(rich_text[0]['text']['content'])
            elif block_type == 'heading_2':
                rich_text = block['heading_2'].get('rich_text', [])
                if rich_text:
                    guide_text.append(f"## {rich_text[0]['text']['content']}")
            elif block_type == 'to_do':
                rich_text = block['to_do'].get('rich_text', [])
                checked = block['to_do'].get('checked', False)
                if rich_text:
                    checkbox = "[x]" if checked else "[ ]"
                    guide_text.append(f"- {checkbox} {rich_text[0]['text']['content']}")
        
        full_text = "\n".join(guide_text)
        print(f"✅ Контент гайда получен ({len(full_text)} символов)")
        
        # 4. Извлекаем чеклисты
        import re
        checklists = []
        
        patterns = [
            r'## ✅ Чеклист качества:(.*?)(?=##|\Z)',
            r'## 📋 Чеклист:(.*?)(?=##|\Z)',
            r'## ✅ Чеклист:(.*?)(?=##|\Z)',
            r'### Чеклист:(.*?)(?=###|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, full_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match.strip():
                    items = re.findall(r'- \[ \] (.*?)(?=\n- \[ \]|\n##|\n###|\Z)', match, re.DOTALL)
                    if items:
                        checklists.append({
                            'title': 'Чеклист из гайда',
                            'items': [item.strip() for item in items if item.strip()]
                        })
        
        print(f"✅ Найдено чеклистов: {len(checklists)}")
        
        # 5. Создаем чеклисты в базе
        print("\n4️⃣ Создание чеклистов в базе...")
        
        created_checklists = 0
        for checklist in checklists:
            # Создаем контент чеклиста
            checklist_content = []
            for item in checklist['items']:
                checklist_content.append({
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": item}}],
                        "checked": False
                    }
                })
            
            # Свойства чеклиста
            checklist_properties = {
                "Подзадачи": {
                    "title": [{"text": {"content": f"Чеклист: Тестовая задача"}}]
                },
                " Статус": {
                    "status": {"name": "To do"}
                },
                "Приоритет": {
                    "select": {"name": "Средний"}
                },
                "Задачи": {
                    "relation": [{"id": task_id}]
                },
                "📬 Гайды": {
                    "relation": [{"id": guide_id}]
                }
            }
            
            # Создаем страницу чеклиста
            checklist_response = await client.pages.create(
                parent={"database_id": CHECKLISTS_DB},
                properties=checklist_properties,
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
                            "rich_text": [{"type": "text", "text": {"content": f"Создан автоматически как копия из гайда. Пунктов: {len(checklist['items'])}"}}]
                        }
                    }
                ]
            )
            
            created_checklists += 1
            print(f"✅ Создан чеклист {created_checklists}: {checklist_response['id']}")
        
        # 6. Результаты
        print("\n" + "=" * 60)
        print("🎯 РЕЗУЛЬТАТЫ ТЕСТА:")
        print(f"✅ Гайд создан: {guide_id}")
        print(f"✅ Задача создана: {task_id}")
        print(f"✅ Чеклистов найдено: {len(checklists)}")
        print(f"✅ Чеклистов создано: {created_checklists}")
        
        if created_checklists > 0:
            print("\n🎉 ТЕСТ ПРОЙДЕН! Связка гайд → задача → чеклисты работает!")
            print(f"🔗 Ссылка на гайд: https://www.notion.so/dreamclub22/{guide_id.replace('-', '')}")
            print(f"🔗 Ссылка на задачу: https://www.notion.so/dreamclub22/{task_id.replace('-', '')}")
        else:
            print("\n⚠️ Чеклисты не созданы. Проверьте логи.")
        
        return guide_id, task_id, created_checklists
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return None, None, 0

if __name__ == "__main__":
    asyncio.run(create_test_guide_with_checklist()) 