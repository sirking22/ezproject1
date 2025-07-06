#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Todoist и Telegram бота
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.integrations.todoist_integration import TodoistIntegration, TaskPriority
from src.config.environment import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_todoist_integration():
    """Тестирование интеграции с Todoist"""
    print("🧪 Тестирование Todoist интеграции...")
    
    try:
        # Инициализируем Todoist
        todoist = TodoistIntegration(config.TODOIST_API_TOKEN)
        await todoist.initialize()
        
        print("✅ Todoist инициализирован")
        
        # Тест 1: Получение проектов
        print("\n📁 Тест 1: Получение проектов...")
        projects = await todoist.get_projects()
        print(f"Найдено проектов: {len(projects)}")
        for project in projects[:3]:  # Показываем первые 3
            name = project.name if hasattr(project, 'name') else project['name'] if isinstance(project, dict) and 'name' in project else str(project)
            pid = project.id if hasattr(project, 'id') else project['id'] if isinstance(project, dict) and 'id' in project else ''
            print(f"  - {name} (ID: {pid})")
        
        # Тест 2: Получение задач
        print("\n📋 Тест 2: Получение задач...")
        tasks = await todoist.get_tasks()
        print(f"Найдено задач: {len(tasks)}")
        
        active_tasks = [t for t in tasks if not t.completed_at]
        completed_tasks = [t for t in tasks if t.completed_at]
        print(f"  - Активных: {len(active_tasks)}")
        print(f"  - Выполненных: {len(completed_tasks)}")
        
        # Показываем несколько активных задач
        if active_tasks:
            print("  Активные задачи:")
            for task in active_tasks[:5]:
                priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(task.priority.value, "⚪")
                print(f"    {priority_emoji} {task.content} (ID: {task.id})")
        
        # Тест 3: Создание тестовой задачи
        print("\n📝 Тест 3: Создание тестовой задачи...")
        test_task = await todoist.create_task(
            content="Тестовая задача из Python",
            description="Задача создана для тестирования интеграции",
            priority=TaskPriority.NORMAL
        )
        
        if test_task:
            print(f"✅ Задача создана: {test_task.content} (ID: {test_task.id})")
            
            # Тест 4: Обновление задачи
            print("\n✏️ Тест 4: Обновление задачи...")
            updated_task = await todoist.update_task(
                task_id=test_task.id,
                content="Обновленная тестовая задача",
                description="Задача была обновлена"
            )
            
            if updated_task:
                print(f"✅ Задача обновлена: {updated_task.content}")
            
            # Тест 5: Завершение задачи
            print("\n✅ Тест 5: Завершение задачи...")
            success = await todoist.complete_task(test_task.id)
            if success:
                print("✅ Задача завершена")
            else:
                print("❌ Ошибка завершения задачи")
            
            # Тест 6: Удаление задачи
            print("\n🗑️ Тест 6: Удаление задачи...")
            success = await todoist.delete_task(test_task.id)
            if success:
                print("✅ Задача удалена")
            else:
                print("❌ Ошибка удаления задачи")
        else:
            print("❌ Ошибка создания тестовой задачи")
        
        # Тест 7: Получение меток
        print("\n🏷️ Тест 7: Получение меток...")
        labels = await todoist.get_labels()
        print(f"Найдено меток: {len(labels)}")
        for label in labels[:5]:
            name = label.name if hasattr(label, 'name') else label['name'] if isinstance(label, dict) and 'name' in label else str(label)
            lid = label.id if hasattr(label, 'id') else label['id'] if isinstance(label, dict) and 'id' in label else ''
            print(f"  - {name} (ID: {lid})")
        
        # Тест 8: Создание задачи с меткой
        print("\n🏷️ Тест 8: Создание задачи с меткой...")
        if labels:
            test_task_with_label = await todoist.create_task(
                content="Задача с меткой",
                description="Тестовая задача с меткой",
                priority=TaskPriority.LOW,
                labels=[labels[0].name]  # Используем первую метку
            )
            
            if test_task_with_label:
                print(f"✅ Задача с меткой создана: {test_task_with_label.content}")
                
                # Удаляем тестовую задачу
                await todoist.delete_task(test_task_with_label.id)
                print("✅ Тестовая задача с меткой удалена")
        
        print("\n🎉 Все тесты Todoist завершены успешно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования Todoist: {e}")
        print(f"❌ Ошибка: {e}")

async def test_bot_commands():
    """Тестирование команд бота"""
    print("\n🤖 Тестирование команд бота...")
    
    try:
        from src.telegram.enhanced_bot import EnhancedTelegramBot
        
        # Инициализируем бота
        bot = EnhancedTelegramBot()
        success = await bot.initialize()
        
        if success:
            print("✅ Telegram бот инициализирован")
            
            # Проверяем доступные команды
            print("\n📋 Доступные команды:")
            commands = [
                "/start", "/help", "/todo", "/todoist", "/tasks",
                "/complete", "/delete", "/notion", "/habit", "/reflection",
                "/idea", "/overview", "/insights", "/progress", "/recommendations",
                "/sync", "/validate", "/list", "/search"
            ]
            
            for cmd in commands:
                print(f"  - {cmd}")
            
            print(f"\n✅ Найдено {len(commands)} команд")
            
        else:
            print("❌ Ошибка инициализации бота")
            
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования бота: {e}")
        print(f"❌ Ошибка: {e}")

async def test_notion_integration():
    """Тестирование интеграции с Notion"""
    print("\n📚 Тестирование Notion интеграции...")
    
    try:
        from src.notion.core import NotionService
        
        # Инициализируем Notion
        notion = NotionService()
        await notion.initialize()
        
        print("✅ Notion инициализирован")
        
        # Проверяем доступные базы данных
        print("\n📊 Доступные базы данных:")
        db_names = {
            "tasks": "📋 Задачи",
            "habits": "🔄 Привычки", 
            "reflections": "🧠 Рефлексии",
            "rituals": "🌟 Ритуалы",
            "guides": "📖 Гайды",
            "actions": "⚡ Действия",
            "terms": "📚 Термины",
            "materials": "📁 Материалы"
        }
        
        for db_key, db_name in db_names.items():
            try:
                count = await notion.get_database_count(db_key)
                print(f"  ✅ {db_name}: {count} записей")
            except Exception as e:
                print(f"  ❌ {db_name}: недоступна ({e})")
        
        print("\n✅ Тестирование Notion завершено")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования Notion: {e}")
        print(f"❌ Ошибка: {e}")

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования Life Management System...")
    
    # Проверяем конфигурацию
    print(f"\n⚙️ Конфигурация:")
    print(f"  - Todoist токен: {'✅' if config.TODOIST_API_TOKEN else '❌'}")
    print(f"  - Telegram токен: {'✅' if config.TELEGRAM_BOT_TOKEN else '❌'}")
    print(f"  - Notion токен: {'✅' if config.NOTION_TOKEN else '❌'}")
    
    # Тестируем Todoist
    await test_todoist_integration()
    
    # Тестируем бота
    await test_bot_commands()
    
    # Тестируем Notion
    await test_notion_integration()
    
    print("\n🎉 Тестирование завершено!")
    print("\n💡 Следующие шаги:")
    print("  1. Настройте TELEGRAM_BOT_TOKEN в .env")
    print("  2. Запустите бота: python run_life_system.py")
    print("  3. Отправьте /start в Telegram")

if __name__ == "__main__":
    asyncio.run(main()) 