#!/usr/bin/env python3
"""
Интеграция MCP с проектом для работы с обложками Notion
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from notion_mcp_client import NotionMCPClient, NotionCoverManager
from smart_cover_applier import SmartCoverApplier

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPNotionIntegration:
    def __init__(self):
        self.mcp_client = NotionMCPClient()
        self.cover_manager = NotionCoverManager(self.mcp_client)
        self.smart_applier = SmartCoverApplier()
        
    async def start(self):
        """Запуск интеграции"""
        await self.mcp_client.start_server()
        logger.info("🚀 MCP интеграция запущена")
        
    async def stop(self):
        """Остановка интеграции"""
        await self.mcp_client.stop_server()
        logger.info("🛑 MCP интеграция остановлена")
        
    async def get_database_status(self, database_id: str) -> str:
        """Получить статус базы данных"""
        try:
            info = await self.mcp_client.get_database_info(database_id)
            pages = await self.mcp_client.get_pages(database_id, limit=10)
            
            status = f"📊 Статус базы данных:\n{info}\n\n"
            status += f"📄 Последние страницы:\n{pages}"
            
            return status
        except Exception as e:
            return f"❌ Ошибка получения статуса: {e}"
    
    async def apply_covers_with_mcp(self, database_id: str) -> str:
        """Применить обложки через MCP"""
        try:
            logger.info("🎨 Начинаем применение обложек через MCP")
            
            # Получаем страницы без обложек
            pages_result = await self.mcp_client.get_pages(database_id, limit=100)
            logger.info(f"📄 Получены страницы: {pages_result}")
            
            # Используем smart_applier для поиска обложек
            # Сначала сканируем папку Telegram импорта
            file_mapping = self.smart_applier.scan_telegram_import_folder()
            
            if not file_mapping:
                return "❌ Не найдены файлы в папке Telegram импорта"
            
            # Получаем идеи с Яндекс.Диск ссылками
            ideas = await self.smart_applier.get_ideas_with_yandex_links(limit=50)
            
            if not ideas:
                return "❌ Не найдены идеи с Яндекс.Диск ссылками"
            
            # Показываем превью маппинга
            await self.smart_applier.show_mapping_preview(ideas, file_mapping, limit=5)
            
            return f"✅ Найдено {len(ideas)} идей и {len(file_mapping)} групп файлов"
                
        except Exception as e:
            logger.error(f"❌ Ошибка применения обложек: {e}")
            return f"❌ Ошибка: {e}"
    
    async def search_and_update_pages(self, database_id: str, query: str) -> str:
        """Поиск и обновление страниц"""
        try:
            # Поиск страниц
            search_result = await self.mcp_client.search_pages(query, database_id, limit=20)
            logger.info(f"🔍 Результаты поиска '{query}': {search_result}")
            
            return search_result
            
        except Exception as e:
            return f"❌ Ошибка поиска: {e}"
    
    async def create_test_page(self, database_id: str) -> str:
        """Создать тестовую страницу"""
        try:
            test_title = f"Тест MCP {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            result = await self.mcp_client.create_page(
                database_id=database_id,
                title=test_title,
                description="Тестовая страница для проверки MCP интеграции",
                tags=["MCP", "Тест"],
                importance=7
            )
            
            return f"✅ Создана тестовая страница:\n{result}"
            
        except Exception as e:
            return f"❌ Ошибка создания страницы: {e}"

async def main():
    """Основная функция для тестирования MCP интеграции"""
    integration = MCPNotionIntegration()
    
    try:
        await integration.start()
        
        # Используем правильный ID базы IDEAS
        database_id = "ad92a6e2-1485-428c-84de-8587706b3be1"
        
        print("🔧 Тестирование MCP интеграции с Notion")
        print("=" * 50)
        print(f"✅ Используем базу IDEAS: {database_id}")
        
        # 1. Статус базы данных
        print("\n1️⃣ Статус базы данных:")
        status = await integration.get_database_status(database_id)
        print(status)
        
        # 2. Поиск страниц
        print("\n2️⃣ Поиск страниц с 'дизайн':")
        search = await integration.search_and_update_pages(database_id, "дизайн")
        print(search)
        
        # 3. Создание тестовой страницы
        print("\n3️⃣ Создание тестовой страницы:")
        test_page = await integration.create_test_page(database_id)
        print(test_page)
        
        # 4. Применение обложек
        print("\n4️⃣ Применение обложек:")
        covers = await integration.apply_covers_with_mcp(database_id)
        print(covers)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}")
    finally:
        await integration.stop()

if __name__ == "__main__":
    asyncio.run(main()) 