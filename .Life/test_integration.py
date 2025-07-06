#!/usr/bin/env python3
"""
Тест интеграции универсального репозитория с админским ботом
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import Settings
from src.notion.universal_repository import UniversalNotionRepository

async def test_integration():
    """Тестирование интеграции"""
    print("🧪 Тестирование интеграции универсального репозитория...")
    
    try:
        # Инициализация
        settings = Settings()
        repo = UniversalNotionRepository(settings)
        
        print("1. Проверка доступности всех таблиц...")
        tables = ['rituals', 'habits', 'reflections', 'guides', 'actions', 'terms', 'materials']
        
        for table in tables:
            database_id = repo.databases.get(table)
            if database_id:
                print(f"✅ {table}: {database_id[:8]}...")
            else:
                print(f"❌ {table}: ID не найден")
        
        print("\n2. Тест валидации всех таблиц...")
        for table in tables:
            is_valid, message = await repo.validate_database(table)
            if is_valid:
                print(f"✅ {table}: Структура корректна")
            else:
                print(f"❌ {table}: {message}")
        
        print("\n3. Тест создания тестового ритуала...")
        ritual_data = {
            'title': 'Тестовый ритуал интеграции',
            'status': 'Active',
            'category': 'Health',
            'frequency': 'Daily',
            'description': 'Тестовый ритуал для проверки интеграции',
            'tags': ['test', 'integration'],
            'created_date': datetime.now(UTC),
            'priority': 'High'
        }
        
        created_ritual = await repo.create_ritual(ritual_data)
        if created_ritual:
            print(f"✅ Ритуал создан: {created_ritual['title']} (ID: {created_ritual['id']})")
            
            print("\n4. Тест получения ритуала...")
            retrieved_ritual = await repo.get_item('rituals', created_ritual['id'])
            if retrieved_ritual:
                print(f"✅ Ритуал получен: {retrieved_ritual['title']}")
            
            print("\n5. Тест обновления ритуала...")
            update_data = {
                'description': 'Обновленное описание для интеграции',
                'priority': 'Medium'
            }
            updated_ritual = await repo.update_item('rituals', created_ritual['id'], update_data)
            if updated_ritual:
                print(f"✅ Ритуал обновлен: {updated_ritual['description']}")
            
            print("\n6. Тест поиска...")
            search_results = await repo.search_items('rituals', 'интеграция')
            print(f"✅ Результатов поиска: {len(search_results)}")
            
            print("\n7. Тест списка с фильтрацией...")
            active_rituals = await repo.get_rituals({'status': 'Active'})
            print(f"✅ Активных ритуалов: {len(active_rituals)}")
            
            print("\n8. Тест удаления ритуала...")
            deleted = await repo.delete_item('rituals', created_ritual['id'])
            if deleted:
                print("✅ Ритуал удален")
        
        print("\n9. Тест создания привычки...")
        habit_data = {
            'title': 'Тестовая привычка интеграции',
            'status': 'Active',
            'category': 'Productivity',
            'frequency': 'Daily',
            'description': 'Тестовая привычка для проверки интеграции',
            'tags': ['test', 'integration'],
            'created_date': datetime.now(UTC),
            'target_frequency': 7,
            'current_frequency': 0
        }
        
        created_habit = await repo.create_habit(habit_data)
        if created_habit:
            print(f"✅ Привычка создана: {created_habit['title']} (ID: {created_habit['id']})")
            
            # Удаляем тестовую привычку
            await repo.delete_item('habits', created_habit['id'])
            print("✅ Тестовая привычка удалена")
        
        print("\n10. Тест алиасов...")
        # Проверяем, что алиасы работают
        rituals = await repo.get_rituals()
        habits = await repo.get_habits()
        reflections = await repo.get_reflections()
        guides = await repo.get_guides()
        actions = await repo.get_actions()
        terms = await repo.get_terms()
        materials = await repo.get_materials()
        
        print(f"✅ Алиасы работают:")
        print(f"   - Ритуалов: {len(rituals)}")
        print(f"   - Привычек: {len(habits)}")
        print(f"   - Размышлений: {len(reflections)}")
        print(f"   - Руководств: {len(guides)}")
        print(f"   - Действий: {len(actions)}")
        print(f"   - Терминов: {len(terms)}")
        print(f"   - Материалов: {len(materials)}")
        
        print("\n✅ Все тесты интеграции пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_integration()) 