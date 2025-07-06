#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Тест нового менеджера Notion
Демонстрация четкой работы с базами данных
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# Импортируем наши модули
from src.services.notion_manager_simple import SimpleNotionManager
from notion_database_schemas import DATABASE_SCHEMAS

load_dotenv()

async def test_notion_manager():
    """Тестируем новый менеджер Notion"""
    
    # Инициализация
    notion_client = AsyncClient(auth=os.getenv('NOTION_TOKEN'))
    manager = SimpleNotionManager(notion_client, DATABASE_SCHEMAS)
    
    print("🚀 Тестируем новый NotionManager...")
    
    # ===== ТЕСТ 1: Создание задачи =====
    print("\n1️⃣ Создаем новую задачу...")
    
    task_data = {
        "title": "Протестировать новый менеджер Notion",
        "description": "Убедиться что все работает корректно",
        "status": "To do",
        "priority": "!!!"
    }
    
    result = await manager.create_task(task_data)
    
    if result.success:
        print(f"✅ Задача создана: {result.data['id']}")
        task_id = result.data['id']
        
        # Обновляем статус
        print("\n2️⃣ Обновляем статус задачи...")
        update_result = await manager.update_task_status(task_id, "In Progress")
        
        if update_result.success:
            print(f"✅ Статус обновлен на: {update_result.data['properties']['Статус']}")
        else:
            print(f"❌ Ошибка обновления: {update_result.error}")
    else:
        print(f"❌ Ошибка создания задачи: {result.error}")
    
    # ===== ТЕСТ 2: Создание идеи =====
    print("\n3️⃣ Создаем новую идею...")
    
    idea_data = {
        "name": "Улучшенная система работы с Notion",
        "description": "Создать более удобную и надежную систему для работы с базами данных Notion",
        "tags": ["автоматизация", "notion", "разработка"],
        "importance": 8,
        "url": "https://github.com/example/notion-manager"
    }
    
    idea_result = await manager.create_idea(idea_data)
    
    if idea_result.success:
        print(f"✅ Идея создана: {idea_result.data['id']}")
        print(f"   Название: {idea_result.data['properties']['Name']}")
        print(f"   Теги: {idea_result.data['properties']['Теги']}")
        print(f"   Важность: {idea_result.data['properties']['Вес']}")
    else:
        print(f"❌ Ошибка создания идеи: {idea_result.error}")
    
    # ===== ТЕСТ 3: Создание материала =====
    print("\n4️⃣ Создаем новый материал...")
    
    material_data = {
        "name": "Руководство по новому менеджеру",
        "description": "Подробное руководство по использованию улучшенного менеджера Notion",
        "url": "https://disk.yandex.ru/i/example-guide",
        "tags": ["документация", "руководство"]
    }
    
    material_result = await manager.create_material(material_data)
    
    if material_result.success:
        print(f"✅ Материал создан: {material_result.data['id']}")
        print(f"   Название: {material_result.data['properties']['Name']}")
        print(f"   URL: {material_result.data['properties']['URL']}")
    else:
        print(f"❌ Ошибка создания материала: {material_result.error}")
    
    # ===== ТЕСТ 4: Получение данных =====
    print("\n5️⃣ Получаем список задач...")
    
    tasks_result = await manager.get_tasks(limit=5)
    
    if tasks_result.success:
        tasks = tasks_result.data
        print(f"✅ Получено {len(tasks)} задач:")
        
        for i, task in enumerate(tasks[:3], 1):  # Показываем только первые 3
            print(f"   {i}. {task['properties'].get('Задача', 'Без названия')} "
                  f"[{task['properties'].get('Статус', 'Без статуса')}]")
    else:
        print(f"❌ Ошибка получения задач: {tasks_result.error}")
    
    # ===== ТЕСТ 5: Фильтрация =====
    print("\n6️⃣ Фильтруем задачи по статусу...")
    
    filtered_result = await manager.get_tasks(
        filters={"status": "To do"},
        limit=5
    )
    
    if filtered_result.success:
        filtered_tasks = filtered_result.data
        print(f"✅ Найдено {len(filtered_tasks)} задач со статусом 'To do'")
    else:
        print(f"❌ Ошибка фильтрации: {filtered_result.error}")
    
    # ===== ТЕСТ 6: Получение идей =====
    print("\n7️⃣ Получаем список идей...")
    
    ideas_result = await manager.get_ideas(limit=5)
    
    if ideas_result.success:
        ideas = ideas_result.data
        print(f"✅ Получено {len(ideas)} идей:")
        
        for i, idea in enumerate(ideas[:3], 1):  # Показываем только первые 3
            name = idea['properties'].get('Name', 'Без названия')
            weight = idea['properties'].get('Вес', 0)
            print(f"   {i}. {name} (важность: {weight})")
    else:
        print(f"❌ Ошибка получения идей: {ideas_result.error}")
    
    # ===== СТАТИСТИКА =====
    print("\n📊 Статистика работы:")
    stats = manager.get_stats()
    print(f"   Всего запросов: {stats['total_requests']}")
    print(f"   Успешных: {stats['successful_requests']}")
    print(f"   Неудачных: {stats['failed_requests']}")
    print(f"   Процент успеха: {stats['success_rate']:.1f}%")

async def test_specific_operations():
    """Тест специфичных операций"""
    
    notion_client = AsyncClient(auth=os.getenv('NOTION_TOKEN'))
    manager = SimpleNotionManager(notion_client, DATABASE_SCHEMAS)
    
    print("\n🔬 Тестируем специфичные операции...")
    
    # Тест создания задачи с полными данными
    complete_task = {
        "title": "Комплексная задача с полными данными",
        "description": "Эта задача содержит все возможные поля для тестирования",
        "status": "In Progress",
        "priority": "!!",
        "date": "2024-01-30"
    }
    
    result = await manager.create_task(complete_task)
    
    if result.success:
        print(f"✅ Создана комплексная задача: {result.data['id']}")
        
        # Тестируем установку обложки (если есть URL изображения)
        cover_result = await manager.set_cover_image(
            result.data['id'], 
            "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400"
        )
        
        if cover_result.success:
            print("✅ Обложка установлена")
        else:
            print(f"❌ Ошибка установки обложки: {cover_result.error}")
    else:
        print(f"❌ Ошибка создания комплексной задачи: {result.error}")

def validate_environment():
    """Проверка окружения"""
    print("🔍 Проверяем окружение...")
    
    required_vars = ['NOTION_TOKEN', 'NOTION_TASKS_DB_ID', 'NOTION_IDEAS_DB_ID', 'NOTION_MATERIALS_DB_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {missing_vars}")
        return False
    
    print("✅ Все необходимые переменные настроены")
    return True

async def main():
    """Главная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ НОВОГО МЕНЕДЖЕРА NOTION")
    print("=" * 50)
    
    # Проверяем окружение
    if not validate_environment():
        print("\n❌ Тестирование остановлено из-за проблем с окружением")
        return
    
    try:
        # Основные тесты
        await test_notion_manager()
        
        # Специфичные операции
        await test_specific_operations()
        
        print("\n🎉 Все тесты завершены!")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())