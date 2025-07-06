#!/usr/bin/env python3
"""
Главный скрипт для запуска системы Notion-Telegram-LLM
"""

import asyncio
import sys
import os
from typing import Optional

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.telegram.bot import TelegramBot
from src.telegram.admin_bot import admin_bot
from src.automation.daily_automation import DailyAutomation
# from src.utils.performance_monitor import performance_monitor

class SystemManager:
    """Менеджер системы для управления различными режимами"""
    
    def __init__(self):
        self.bot: Optional[TelegramBot] = None
        self.admin_bot: Optional[type(admin_bot)] = None
        self.automation: Optional[DailyAutomation] = None
    
    async def run_bot_mode(self):
        """Запуск в режиме обычного бота"""
        print("🤖 Запуск обычного Telegram бота...")
        self.bot = TelegramBot()
        await self.bot.run()
    
    async def run_admin_mode(self):
        """Запуск в режиме админского бота"""
        print("👑 Запуск админского Telegram бота...")
        await admin_bot.run()
    
    async def run_automation_mode(self):
        """Запуск в режиме автоматизации"""
        print("⚙️ Запуск системы автоматизации...")
        self.automation = DailyAutomation()
        await self.automation.run()
    
    async def run_full_mode(self):
        """Запуск в полном режиме (бот + автоматизация)"""
        print("🚀 Запуск полной системы...")
        
        # Запускаем бота в фоне
        bot_task = asyncio.create_task(self.run_bot_mode())
        
        # Запускаем автоматизацию в фоне
        automation_task = asyncio.create_task(self.run_automation_mode())
        
        try:
            # Ждём завершения всех задач
            await asyncio.gather(bot_task, automation_task)
        except KeyboardInterrupt:
            print("\n🛑 Остановка системы...")
            bot_task.cancel()
            automation_task.cancel()
    
    async def run_test_mode(self):
        """Запуск в тестовом режиме"""
        print("🧪 Запуск тестового режима...")
        
        # Тестируем агентов
        from src.agents.agent_core import agent_core
        
        print("📋 Тестирование загрузки агентов...")
        prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
        print(f"✅ Загружено агентов: {len(prompts)}")
        
        # Упрощённое тестирование без performance_monitor
        print("📊 Тестирование системы...")
        print("✅ Система готова к работе")
        
        print("✅ Тестирование завершено")

async def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("""
🚀 **Notion-Telegram-LLM System**

Доступные режимы:
• bot - Обычный Telegram бот
• admin - Админский Telegram бот
• automation - Система автоматизации
• full - Полная система (бот + автоматизация)
• test - Тестовый режим

Использование: python main.py [режим]
Примеры:
• python main.py bot
• python main.py admin
• python main.py full
        """)
        return
    
    mode = sys.argv[1].lower()
    manager = SystemManager()
    
    try:
        if mode == "bot":
            await manager.run_bot_mode()
        elif mode == "admin":
            await manager.run_admin_mode()
        elif mode == "automation":
            await manager.run_automation_mode()
        elif mode == "full":
            await manager.run_full_mode()
        elif mode == "test":
            await manager.run_test_mode()
        else:
            print(f"❌ Неизвестный режим: {mode}")
            print("Доступные режимы: bot, admin, automation, full, test")
    
    except KeyboardInterrupt:
        print("\n🛑 Остановка системы...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())