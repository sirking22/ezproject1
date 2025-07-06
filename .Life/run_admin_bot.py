#!/usr/bin/env python3
"""
Скрипт для запуска админского Telegram бота
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.telegram.admin_bot import admin_bot

async def main():
    """Основная функция"""
    print("👑 Запуск админского Telegram бота...")
    
    try:
        await admin_bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 