#!/usr/bin/env python3
"""
Быстрый запуск системы Notion-Telegram-LLM
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SystemManager

async def quick_start():
    """Быстрый запуск с выбором режима"""
    print("🚀 **Notion-Telegram-LLM Quick Start**")
    print()
    print("Выберите режим запуска:")
    print("1. 🤖 Обычный бот")
    print("2. 👑 Админский бот")
    print("3. ⚙️ Автоматизация")
    print("4. 🚀 Полная система")
    print("5. 🧪 Тестовый режим")
    print("0. ❌ Выход")
    print()
    
    try:
        choice = input("Введите номер (0-5): ").strip()
        
        manager = SystemManager()
        
        if choice == "1":
            await manager.run_bot_mode()
        elif choice == "2":
            await manager.run_admin_mode()
        elif choice == "3":
            await manager.run_automation_mode()
        elif choice == "4":
            await manager.run_full_mode()
        elif choice == "5":
            await manager.run_test_mode()
        elif choice == "0":
            print("👋 До свидания!")
            return
        else:
            print("❌ Неверный выбор")
            return
            
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(quick_start()) 