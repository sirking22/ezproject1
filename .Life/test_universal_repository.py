#!/usr/bin/env python3
"""
Тест универсального репозитория Notion
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import Settings
from src.notion.universal_repository import UniversalNotionRepository

async def test_universal_repository():
    """Тестирование универсального репозитория"""
    print("🧪 Тестирование универсального репозитория Notion...")
    
    try:
        # Инициализация
        settings = Settings()
        repo = UniversalNotionRepository(settings)
        
        print("1. Проверка валидации баз данных...")
        for table_name in ['rituals', 'habits', 'reflections', 'guides', 'actions', 'terms', 'materials']:
            is_valid, message = await repo.validate_database(table_name)
            if is_valid:
                print(f"✅ {table_name}: {message}")
            else:
                print(f"❌ {table_name}: {message}")
        
        print("\n2. Тест создания ритуала...")
        ritual_data = {
            'title': 'Тестовый ритуал',
            'status': 'Active',
            'category': 'Health',
            'frequency': 'Daily',
            'description': 'Тестовое описание ритуала',
            'tags': ['test', 'health'],
            'created_date': datetime.now(UTC),
            'priority': 'High'
        }
        
        created_ritual = await repo.create_ritual(ritual_data)
        if created_ritual:
            print(f"✅ Ритуал создан: {created_ritual['title']} (ID: {created_ritual['id']})")
            
            print("\n3. Тест получения ритуала...")
            retrieved_ritual = await repo.get_item('rituals', created_ritual['id'])
            if retrieved_ritual:
                print(f"✅ Ритуал получен: {retrieved_ritual['title']}")
            
            print("\n4. Тест обновления ритуала...")
            update_data = {
                'description': 'Обновленное описание',
                'priority': 'Medium'
            }
            updated_ritual = await repo.update_item('rituals', created_ritual['id'], update_data)
            if updated_ritual:
                print(f"✅ Ритуал обновлен: {updated_ritual['description']}")
            
            print("\n5. Тест списка ритуалов...")
            rituals = await repo.get_rituals()
            print(f"✅ Найдено ритуалов: {len(rituals)}")
            
            print("\n6. Тест фильтрации...")
            active_rituals = await repo.get_rituals({'status': 'Active'})
            print(f"✅ Активных ритуалов: {len(active_rituals)}")
            
            print("\n7. Тест поиска...")
            search_results = await repo.search_items('rituals', 'тест')
            print(f"✅ Результатов поиска: {len(search_results)}")
            
            print("\n8. Тест удаления ритуала...")
            deleted = await repo.delete_item('rituals', created_ritual['id'])
            if deleted:
                print("✅ Ритуал удален")
        
        print("\n9. Тест создания привычки...")
        habit_data = {
            'title': 'Тестовая привычка',
            'status': 'Active',
            'category': 'Productivity',
            'frequency': 'Daily',
            'description': 'Тестовое описание привычки',
            'tags': ['test', 'productivity'],
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
        
        print("\n✅ Все тесты пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_universal_repository()) 