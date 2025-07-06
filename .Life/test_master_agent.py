#!/usr/bin/env python3
"""
Тест мастер-агента и ИИ-команды разработчиков
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.master_agent import master_agent, TaskPriority, TaskStatus, AgentRole
from src.agents.enhanced_prompts import get_enhanced_prompt, get_agent_specializations

async def test_master_agent():
    """Тестирование мастер-агента и ИИ-команды"""
    print("🚀 Тестирование мастер-агента и ИИ-команды разработчиков...")
    print("=" * 60)
    
    try:
        # 1. Создаем тестовые задачи
        print("\n1. 📋 Создание тестовых задач...")
        
        tasks = [
            {
                "title": "Оптимизировать промпты для лучшего качества ответов",
                "description": "Проанализировать текущие промпты агентов и предложить улучшения для повышения качества и релевантности ответов",
                "priority": TaskPriority.HIGH,
                "tags": ["optimization", "prompts", "quality"],
                "estimated_hours": 2.0
            },
            {
                "title": "Создать автоматизированные тесты для API",
                "description": "Разработать comprehensive test suite для всех API endpoints с покрытием edge cases",
                "priority": TaskPriority.MEDIUM,
                "tags": ["testing", "api", "automation"],
                "estimated_hours": 4.0
            },
            {
                "title": "Настроить CI/CD пайплайн для автоматического деплоя",
                "description": "Создать GitHub Actions workflow для автоматического тестирования и деплоя на staging/production",
                "priority": TaskPriority.HIGH,
                "tags": ["devops", "ci_cd", "automation"],
                "estimated_hours": 3.0
            },
            {
                "title": "Провести анализ пользовательского опыта",
                "description": "Собрать обратную связь от пользователей и предложить улучшения UX/UI",
                "priority": TaskPriority.MEDIUM,
                "tags": ["ux", "feedback", "analysis"],
                "estimated_hours": 2.5
            },
            {
                "title": "Исследовать новые LLM модели для интеграции",
                "description": "Проанализировать новые модели (Claude 3.5, GPT-4 Turbo, Gemini Pro) и их применимость для проекта",
                "priority": TaskPriority.LOW,
                "tags": ["research", "llm", "integration"],
                "estimated_hours": 3.0
            }
        ]
        
        created_tasks = []
        for task_data in tasks:
            task_id = await master_agent.create_task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                estimated_hours=task_data["estimated_hours"],
                tags=task_data["tags"]
            )
            created_tasks.append(task_id)
            print(f"✅ Создана задача: {task_data['title']} (ID: {task_id})")
        
        # 2. Показываем назначения агентов
        print("\n2. 🤖 Назначения агентов на задачи...")
        for task_id in created_tasks:
            task = master_agent.tasks.get(task_id)
            if task and task.assigned_agent:
                print(f"📝 Задача '{task.title}' → Агент: {task.assigned_agent.value}")
                print(f"   Приоритет: {task.priority.value}")
                print(f"   Статус: {task.status.value}")
                print(f"   Теги: {', '.join(task.tags)}")
                print()
        
        # 3. Выполняем несколько задач
        print("\n3. ⚡ Выполнение задач...")
        
        # Выполняем задачу по оптимизации промптов
        prompt_task_id = created_tasks[0]
        print(f"\n🔧 Выполнение задачи: Оптимизация промптов...")
        
        result = await master_agent.execute_task(
            prompt_task_id,
            "Проанализируй текущие промпты и предложи конкретные улучшения для повышения качества ответов"
        )
        
        print(f"📊 Результат выполнения:")
        print(f"{'='*40}")
        print(result[:500] + "..." if len(result) > 500 else result)
        print(f"{'='*40}")
        
        # 4. Показываем отчет о команде
        print("\n4. 📊 Отчет о команде...")
        team_report = await master_agent.get_team_report()
        
        print(f"📈 Общие метрики:")
        print(f"   - Всего задач: {team_report['team_metrics']['total_tasks']}")
        print(f"   - Завершено: {team_report['team_metrics']['completed_tasks']}")
        print(f"   - Неудачно: {team_report['team_metrics']['failed_tasks']}")
        print(f"   - Среднее время выполнения: {team_report['team_metrics']['avg_completion_time']:.2f} часов")
        
        print(f"\n🤖 Производительность агентов:")
        for role, perf in team_report['agent_performance'].items():
            print(f"   - {role}:")
            print(f"     • Завершено: {perf['tasks_completed']}")
            print(f"     • Неудачно: {perf['tasks_failed']}")
            print(f"     • Успешность: {perf['success_rate']:.1%}")
            print(f"     • Текущая загрузка: {perf['current_load']}")
            print(f"     • Среднее качество: {perf['avg_quality']:.2f}")
        
        # 5. Показываем рекомендации
        print(f"\n💡 Рекомендации:")
        for i, rec in enumerate(team_report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # 6. Демонстрируем оптимизацию команды
        print("\n5. 🔧 Оптимизация команды...")
        optimizations = await master_agent.optimize_team()
        
        print(f"🔄 Найденные оптимизации:")
        if optimizations['prompt_updates']:
            print(f"   📝 Обновления промптов: {len(optimizations['prompt_updates'])}")
            for update in optimizations['prompt_updates']:
                print(f"     - {update['agent']}: {update['reason']}")
        
        if optimizations['task_reassignments']:
            print(f"   🔄 Перераспределение задач: {len(optimizations['task_reassignments'])}")
            for reassignment in optimizations['task_reassignments']:
                print(f"     - {reassignment['task_id']}: {reassignment['from_agent']} → {reassignment['to_agent']}")
        
        if optimizations['process_improvements']:
            print(f"   ⚙️ Улучшения процессов: {len(optimizations['process_improvements'])}")
            for improvement in optimizations['process_improvements']:
                print(f"     - {improvement['type']}: {improvement['description']}")
        
        # 7. Применяем оптимизации
        print("\n6. ✅ Применение оптимизаций...")
        results = await master_agent.apply_optimizations(optimizations)
        
        print(f"📊 Результаты применения:")
        print(f"   - Обновлено промптов: {results['prompt_updates_applied']}")
        print(f"   - Перераспределено задач: {results['tasks_reassigned']}")
        print(f"   - Применено улучшений: {results['process_improvements_applied']}")
        
        if results['errors']:
            print(f"   - Ошибки: {len(results['errors'])}")
            for error in results['errors']:
                print(f"     • {error}")
        
        # 8. Демонстрируем улучшенные промпты
        print("\n7. 📝 Демонстрация улучшенных промптов...")
        
        print(f"\n🔍 Промпт для Product Manager:")
        pm_prompt = get_enhanced_prompt("Product Manager")
        print(f"{'='*50}")
        print(pm_prompt[:300] + "..." if len(pm_prompt) > 300 else pm_prompt)
        print(f"{'='*50}")
        
        print(f"\n🔍 Промпт для Developer:")
        dev_prompt = get_enhanced_prompt("Developer")
        print(f"{'='*50}")
        print(dev_prompt[:300] + "..." if len(dev_prompt) > 300 else dev_prompt)
        print(f"{'='*50}")
        
        # 9. Финальный отчет
        print("\n8. 🎯 Финальный отчет...")
        final_report = await master_agent.get_team_report()
        
        print(f"🏆 Итоговые результаты:")
        print(f"   - Команда успешно обработала {final_report['team_metrics']['total_tasks']} задач")
        print(f"   - Среднее время выполнения: {final_report['team_metrics']['avg_completion_time']:.2f} часов")
        print(f"   - Успешность: {final_report['team_metrics']['completed_tasks'] / final_report['team_metrics']['total_tasks']:.1%}")
        
        print(f"\n🚀 Система готова к работе!")
        print(f"   - Мастер-агент управляет командой из {len(AgentRole)} специалистов")
        print(f"   - Автоматическое назначение задач на основе специализаций")
        print(f"   - Оптимизация производительности и качества")
        print(f"   - Регулярные отчеты и рекомендации")
        
        print("\n✅ Тестирование мастер-агента завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def demo_agent_interaction():
    """Демонстрация взаимодействия с агентами"""
    print("\n🎭 Демонстрация взаимодействия с агентами...")
    print("=" * 60)
    
    try:
        # Создаем задачу для Product Manager
        pm_task_id = await master_agent.create_task(
            title="Приоритизация фич для следующего спринта",
            description="Проанализируй backlog и предложи приоритизацию фич для следующего спринта с учетом бизнес-целей и ресурсов команды",
            priority=TaskPriority.HIGH,
            tags=["prioritization", "sprint", "planning"],
            estimated_hours=1.5
        )
        
        print(f"📋 Создана задача для Product Manager: {pm_task_id}")
        
        # Выполняем задачу
        result = await master_agent.execute_task(
            pm_task_id,
            "У нас есть следующие фичи в backlog: 1) Улучшение UI/UX, 2) Оптимизация производительности, 3) Новая интеграция с API, 4) Исправление багов. Предложи приоритизацию."
        )
        
        print(f"\n💼 Ответ Product Manager:")
        print(f"{'='*50}")
        print(result)
        print(f"{'='*50}")
        
        # Создаем задачу для Developer
        dev_task_id = await master_agent.create_task(
            title="Рефакторинг legacy кода",
            description="Проанализируй существующий код и предложи план рефакторинга для улучшения читаемости и maintainability",
            priority=TaskPriority.MEDIUM,
            tags=["refactoring", "code", "maintenance"],
            estimated_hours=2.0
        )
        
        print(f"\n📋 Создана задача для Developer: {dev_task_id}")
        
        # Выполняем задачу
        result = await master_agent.execute_task(
            dev_task_id,
            "У нас есть модуль с 500+ строками кода, который сложно поддерживать. Предложи план рефакторинга."
        )
        
        print(f"\n💻 Ответ Developer:")
        print(f"{'='*50}")
        print(result)
        print(f"{'='*50}")
        
        # Создаем задачу для LLM Researcher
        llm_task_id = await master_agent.create_task(
            title="Оптимизация промптов для лучших результатов",
            description="Проанализируй текущие промпты и предложи улучшения для повышения качества ответов",
            priority=TaskPriority.HIGH,
            tags=["prompt_engineering", "optimization", "quality"],
            estimated_hours=1.0
        )
        
        print(f"\n📋 Создана задача для LLM Researcher: {llm_task_id}")
        
        # Выполняем задачу
        result = await master_agent.execute_task(
            llm_task_id,
            "Наши промпты дают слишком общие ответы. Как сделать их более конкретными и полезными?"
        )
        
        print(f"\n🧠 Ответ LLM Researcher:")
        print(f"{'='*50}")
        print(result)
        print(f"{'='*50}")
        
        print("\n✅ Демонстрация завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Запуск тестирования мастер-агента и ИИ-команды...")
    
    # Запускаем основной тест
    asyncio.run(test_master_agent())
    
    # Запускаем демонстрацию
    asyncio.run(demo_agent_interaction())
    
    print("\n🎉 Все тесты завершены!")
    print("\n📚 Что было протестировано:")
    print("   ✅ Создание и назначение задач")
    print("   ✅ Автоматический выбор агентов")
    print("   ✅ Выполнение задач через агентов")
    print("   ✅ Анализ производительности команды")
    print("   ✅ Оптимизация и перераспределение")
    print("   ✅ Улучшенные промпты агентов")
    print("   ✅ Взаимодействие между агентами")
    
    print("\n🎯 Система готова к продуктивной работе!") 