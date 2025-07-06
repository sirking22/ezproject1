#!/usr/bin/env python3
"""
Тест интеграции с локальной LLM
"""

import asyncio
import logging
from pathlib import Path
import sys

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from src.llm.client import LocalLLMClient, quick_generate, quick_work_generate, quick_home_generate
from src.notion.llm_service import LLMService, LLMConfig
from src.notion.client import NotionClient
from src.utils.config import Config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_local_llm_client():
    """Тест локального LLM клиента"""
    print("🧪 Тестирование локального LLM клиента...")
    
    try:
        async with LocalLLMClient() as client:
            # Тест базовой генерации
            print("📝 Тест базовой генерации...")
            response = await client.generate(
                prompt="Привет! Как дела?",
                context="home",
                session_id="test_session"
            )
            print(f"✅ Ответ: {response.text[:100]}...")
            print(f"📊 Модель: {response.model}, Контекст: {response.context}")
            print(f"⏱️ Время: {response.processing_time:.2f}с, Уверенность: {response.confidence:.2f}")
            
            # Тест переключения контекста
            print("\n🔄 Тест переключения контекста...")
            await client.set_session_context("test_session", "work")
            response = await client.generate(
                prompt="Расскажи о продуктивности",
                context="work",
                session_id="test_session"
            )
            print(f"✅ Рабочий ответ: {response.text[:100]}...")
            
            # Тест информации о сессии
            print("\n📋 Тест информации о сессии...")
            session_info = await client.get_session_info("test_session")
            print(f"✅ Информация о сессии: {session_info}")
            
            # Тест проверки здоровья
            print("\n💚 Тест проверки здоровья...")
            health = await client.health_check()
            print(f"✅ Здоровье сервера: {health}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования клиента: {e}")

async def test_quick_functions():
    """Тест быстрых функций"""
    print("\n🚀 Тестирование быстрых функций...")
    
    try:
        # Тест быстрой генерации
        print("⚡ Тест быстрой генерации...")
        response = await quick_generate("Расскажи о привычках", context="home")
        print(f"✅ Быстрый ответ: {response[:100]}...")
        
        # Тест рабочей генерации
        print("💼 Тест рабочей генерации...")
        response = await quick_work_generate("Планирование проекта")
        print(f"✅ Рабочий ответ: {response[:100]}...")
        
        # Тест домашней генерации
        print("🏠 Тест домашней генерации...")
        response = await quick_home_generate("Личное развитие")
        print(f"✅ Домашний ответ: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования быстрых функций: {e}")

async def test_llm_service():
    """Тест LLM сервиса с Notion интеграцией"""
    print("\n🔗 Тестирование LLM сервиса с Notion...")
    
    try:
        # Загружаем конфигурацию
        config = Config()
        
        # Создаем Notion клиент
        notion_client = NotionClient(config.notion_token, config.notion_dbs)
        
        # Создаем LLM сервис
        llm_config = LLMConfig(
            use_local=True,
            local_url="http://localhost:8000",
            openrouter_api_key=config.openrouter_api_key,
            fallback_to_openrouter=True
        )
        
        async with LLMService(notion_client, llm_config) as llm_service:
            # Тест генерации с контекстом Notion
            print("📊 Тест генерации с контекстом Notion...")
            response = await llm_service.generate_response(
                prompt="Проанализируй мои привычки",
                context="home",
                user_id="test_user",
                use_notion_context=True
            )
            print(f"✅ Ответ с контекстом: {response[:200]}...")
            
            # Тест генерации инсайта
            print("\n💡 Тест генерации инсайта...")
            insight = await llm_service.generate_insight(
                topic="Продуктивность",
                context="work",
                user_id="test_user"
            )
            print(f"✅ Инсайт: {insight[:200]}...")
            
            # Тест предсказания
            print("\n🔮 Тест предсказания...")
            prediction = await llm_service.generate_prediction(
                habit_or_goal="Медитация",
                context="home",
                user_id="test_user"
            )
            print(f"✅ Предсказание: {prediction[:200]}...")
            
            # Тест оптимизации
            print("\n⚡ Тест оптимизации...")
            optimization = await llm_service.generate_optimization(
                area="Временное управление",
                context="work",
                user_id="test_user"
            )
            print(f"✅ Оптимизация: {optimization[:200]}...")
            
            # Тест проверки здоровья
            print("\n💚 Тест здоровья сервиса...")
            health = await llm_service.health_check()
            print(f"✅ Здоровье: {health}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования LLM сервиса: {e}")

async def test_context_switching():
    """Тест переключения контекстов"""
    print("\n🔄 Тестирование переключения контекстов...")
    
    try:
        async with LocalLLMClient() as client:
            session_id = "context_test_session"
            
            # Тест домашнего контекста
            print("🏠 Тест домашнего контекста...")
            await client.set_session_context(session_id, "home")
            response = await client.generate(
                prompt="Как улучшить личное развитие?",
                session_id=session_id
            )
            print(f"✅ Домашний ответ: {response.text[:100]}...")
            
            # Тест рабочего контекста
            print("💼 Тест рабочего контекста...")
            await client.set_session_context(session_id, "work")
            response = await client.generate(
                prompt="Как улучшить продуктивность?",
                session_id=session_id
            )
            print(f"✅ Рабочий ответ: {response.text[:100]}...")
            
            # Тест общего контекста
            print("🌐 Тест общего контекста...")
            await client.set_session_context(session_id, "general")
            response = await client.generate(
                prompt="Общие советы по развитию",
                session_id=session_id
            )
            print(f"✅ Общий ответ: {response.text[:100]}...")
            
            # Проверяем историю сессии
            print("\n📋 История сессии...")
            session_info = await client.get_session_info(session_id)
            print(f"✅ Информация о сессии: {session_info}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования переключения контекстов: {e}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов локальной LLM интеграции...")
    
    # Тест 1: Локальный LLM клиент
    await test_local_llm_client()
    
    # Тест 2: Быстрые функции
    await test_quick_functions()
    
    # Тест 3: LLM сервис с Notion
    await test_llm_service()
    
    # Тест 4: Переключение контекстов
    await test_context_switching()
    
    print("\n✅ Все тесты завершены!")

if __name__ == "__main__":
    asyncio.run(main()) 