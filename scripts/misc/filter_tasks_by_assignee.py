#!/usr/bin/env python3
"""
Фильтрация задач по исполнителю через MCP Notion Server
Быстрый скрипт для работы с дизайнерскими задачами
"""

import asyncio
import sys
from mcp_notion_server import NotionMCPServer

async def filter_tasks_by_assignee(assignee_name: str | None = None):
    """Фильтрация задач по исполнителю"""
    try:
        # Инициализация сервера
        server = NotionMCPServer()
        
        # Получение всех задач - используем правильный ID из .env
        tasks_db_id = server.tasks_db_id or "d09df250ce7e4e0d9fbe4e036d320def"  # fallback на известный ID
        print(f"🔍 Получение задач из базы Tasks...")
        print(f"🔍 Используем Tasks DB ID: {tasks_db_id}")
        tasks_response = await server.get_database_pages(tasks_db_id)
        
        if not tasks_response.get('success'):
            print(f"❌ Ошибка получения задач: {tasks_response.get('error')}")
            return
        
        all_tasks = tasks_response.get('pages', [])
        print(f"📊 Всего задач: {len(all_tasks)}")
        
        # Фильтрация по исполнителю
        if assignee_name:
            filtered_tasks = []
            for task in all_tasks:
                properties = task.get('properties', {})
                participants = properties.get('Участники', [])
                
                # Проверяем есть ли указанный исполнитель
                if isinstance(participants, list):
                    for participant in participants:
                        if assignee_name.lower() in str(participant).lower():
                            filtered_tasks.append(task)
                            break
                elif assignee_name.lower() in str(participants).lower():
                    filtered_tasks.append(task)
            
            print(f"🎯 Задач для '{assignee_name}': {len(filtered_tasks)}")
            tasks_to_show = filtered_tasks
        else:
            tasks_to_show = all_tasks
        
        # Вывод результатов
        print("\n" + "="*80)
        print("📋 СПИСОК ЗАДАЧ")
        print("="*80)
        
        for i, task in enumerate(tasks_to_show[:20], 1):  # Показываем первые 20
            properties = task.get('properties', {})
            
            # Извлекаем основные поля
            title = properties.get('Задача', 'Без названия')
            status = properties.get('Статус', 'Не указан')
            participants = properties.get('Участники', [])
            priority = properties.get('Приоритет', 'Не указан')
            
            print(f"\n{i}. {title}")
            print(f"   📊 Статус: {status}")
            print(f"   👥 Исполнители: {participants}")
            print(f"   🔥 Приоритет: {priority}")
            print(f"   🆔 ID: {task['id']}")
        
        if len(tasks_to_show) > 20:
            print(f"\n... и ещё {len(tasks_to_show) - 20} задач")
        
        # Статистика по статусам
        print("\n" + "="*80)
        print("📊 СТАТИСТИКА ПО СТАТУСАМ")
        print("="*80)
        
        status_counts = {}
        for task in tasks_to_show:
            status = task.get('properties', {}).get('Статус', 'Не указан')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count}")
        
        return tasks_to_show
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

async def main():
    """Основная функция"""
    print("🚀 Фильтрация задач по исполнителю")
    print("="*50)
    
    # Получаем имя исполнителя из аргументов командной строки
    assignee_name = None
    if len(sys.argv) > 1:
        assignee_name = sys.argv[1]
        print(f"🎯 Фильтр по исполнителю: {assignee_name}")
    else:
        print("📋 Показываем все задачи (для фильтрации используйте: python filter_tasks_by_assignee.py 'имя')")
    
    # Выполняем фильтрацию
    tasks = await filter_tasks_by_assignee(assignee_name)
    
    print(f"\n✅ Обработано {len(tasks or [])} задач")

if __name__ == "__main__":
    asyncio.run(main()) 