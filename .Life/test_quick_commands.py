#!/usr/bin/env python3
"""
Тест быстрых команд для личностного развития
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Settings
from src.notion.universal_repository import UniversalNotionRepository

async def test_quick_commands():
    """Тестирование быстрых команд"""
    print("🚀 Тестирование быстрых команд для личностного развития...")
    
    try:
        # Инициализация
        settings = Settings()
        repo = UniversalNotionRepository(settings)
        
        print("1. Тест быстрого добавления задачи...")
        task_data = {
            'title': 'Тестовая задача',
            'status': 'Pending',
            'priority': 'Medium',
            'category': 'General',
            'description': 'Тестовая задача для проверки',
            'tags': ['todo', 'quick', 'test'],
            'created_date': datetime.now(UTC)
        }
        
        created_task = await repo.create_item('actions', task_data)
        if created_task:
            print(f"✅ Задача создана: {created_task['title']} (ID: {created_task['id']})")
            
            # Удаляем тестовую задачу
            await repo.delete_item('actions', created_task['id'])
            print("✅ Тестовая задача удалена")
        
        print("\n2. Тест быстрого добавления привычки...")
        habit_data = {
            'title': 'Тестовая привычка',
            'status': 'Active',
            'category': 'General',
            'frequency': 'Daily',
            'description': 'Тестовая привычка для проверки',
            'tags': ['habit', 'quick', 'test'],
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
        
        print("\n3. Тест быстрого добавления рефлексии...")
        reflection_data = {
            'title': f"Тестовая рефлексия {datetime.now().strftime('%d.%m.%Y')}",
            'type': 'Daily',
            'mood': 'Positive',
            'content': 'Тестовая рефлексия для проверки функциональности',
            'tags': ['reflection', 'quick', 'test'],
            'created_date': datetime.now(UTC)
        }
        
        created_reflection = await repo.create_reflection(reflection_data)
        if created_reflection:
            print(f"✅ Рефлексия создана: {created_reflection['title']} (ID: {created_reflection['id']})")
            
            # Удаляем тестовую рефлексию
            await repo.delete_item('reflections', created_reflection['id'])
            print("✅ Тестовая рефлексия удалена")
        
        print("\n4. Тест быстрого сохранения идеи...")
        idea_data = {
            'title': 'Тестовая идея',
            'type': 'Idea',
            'category': 'General',
            'description': 'Тестовая идея для проверки функциональности',
            'tags': ['idea', 'quick', 'test'],
            'created_date': datetime.now(UTC),
            'status': 'Active'
        }
        
        created_idea = await repo.create_material(idea_data)
        if created_idea:
            print(f"✅ Идея сохранена: {created_idea['title']} (ID: {created_idea['id']})")
            
            # Удаляем тестовую идею
            await repo.delete_item('materials', created_idea['id'])
            print("✅ Тестовая идея удалена")
        
        print("\n5. Тест утреннего ритуала...")
        ritual_data = {
            'title': f"Утренний ритуал {datetime.now().strftime('%d.%m.%Y')}",
            'status': 'Active',
            'category': 'Morning',
            'frequency': 'Daily',
            'description': 'Утренний ритуал для продуктивного дня',
            'tags': ['morning', 'ritual', 'daily', 'test'],
            'created_date': datetime.now(UTC),
            'priority': 'High'
        }
        
        created_ritual = await repo.create_ritual(ritual_data)
        if created_ritual:
            print(f"✅ Утренний ритуал создан: {created_ritual['title']} (ID: {created_ritual['id']})")
            
            # Удаляем тестовый ритуал
            await repo.delete_item('rituals', created_ritual['id'])
            print("✅ Тестовый ритуал удален")
        
        print("\n6. Тест вечерней рефлексии...")
        evening_reflection_data = {
            'title': f"Вечерняя рефлексия {datetime.now().strftime('%d.%m.%Y')}",
            'type': 'Evening',
            'mood': 'Neutral',
            'content': 'Время для размышлений о прошедшем дне',
            'tags': ['evening', 'reflection', 'daily', 'test'],
            'created_date': datetime.now(UTC)
        }
        
        created_evening = await repo.create_reflection(evening_reflection_data)
        if created_evening:
            print(f"✅ Вечерняя рефлексия создана: {created_evening['title']} (ID: {created_evening['id']})")
            
            # Удаляем тестовую вечернюю рефлексию
            await repo.delete_item('reflections', created_evening['id'])
            print("✅ Тестовая вечерняя рефлексия удалена")
        
        print("\n7. Тест аналитики...")
        # Получаем данные для аналитики
        rituals = await repo.get_rituals()
        habits = await repo.get_habits()
        reflections = await repo.get_reflections()
        actions = await repo.get_actions()
        
        print(f"📊 Статистика:")
        print(f"   - Ритуалов: {len(rituals)}")
        print(f"   - Привычек: {len(habits)}")
        print(f"   - Рефлексий: {len(reflections)}")
        print(f"   - Задач: {len(actions)}")
        
        # Анализ настроения
        if reflections:
            mood_counts = {}
            for reflection in reflections:
                mood = reflection.get('mood', 'Unknown')
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            print(f"😊 Анализ настроения:")
            for mood, count in mood_counts.items():
                percentage = (count / len(reflections)) * 100
                print(f"   - {mood}: {count} ({percentage:.1f}%)")
        
        print("\n✅ Все тесты быстрых команд пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quick_commands()) 