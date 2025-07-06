#!/usr/bin/env python3
"""
🔗 АВТОМАТИЧЕСКАЯ НАСТРОЙКА РЕАЛЬНЫХ СЕРВИСОВ
Интеграция с Notion и Telegram
"""

import asyncio
import json
import logging
import os
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealServicesSetup:
    """Настройка реальных сервисов"""
    
    def __init__(self):
        load_dotenv()
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    def print_header(self):
        """Вывод заголовка"""
        print("🔗" + "="*60)
        print("🎯 НАСТРОЙКА РЕАЛЬНЫХ СЕРВИСОВ")
        print("="*62)
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)
    
    def check_current_config(self):
        """Проверка текущей конфигурации"""
        print("\n🔍 ПРОВЕРКА ТЕКУЩЕЙ КОНФИГУРАЦИИ")
        print("-" * 40)
        
        config_status = {
            "notion_token": bool(self.notion_token),
            "telegram_token": bool(self.telegram_token),
            "telegram_chat_id": bool(self.telegram_chat_id)
        }
        
        print(f"Notion Token: {'✅' if config_status['notion_token'] else '❌'}")
        print(f"Telegram Token: {'✅' if config_status['telegram_token'] else '❌'}")
        print(f"Telegram Chat ID: {'✅' if config_status['telegram_chat_id'] else '❌'}")
        
        return config_status
    
    def test_notion_connection(self):
        """Тестирование подключения к Notion"""
        print("\n📝 ТЕСТИРОВАНИЕ NOTION")
        print("-" * 30)
        
        if not self.notion_token:
            print("❌ Notion токен не настроен")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            # Тест API
            response = requests.get(
                "https://api.notion.com/v1/users/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Notion подключен: {user_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Ошибка Notion API: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка подключения к Notion: {e}")
            return False
    
    def test_telegram_connection(self):
        """Тестирование подключения к Telegram"""
        print("\n📱 ТЕСТИРОВАНИЕ TELEGRAM")
        print("-" * 30)
        
        if not self.telegram_token:
            print("❌ Telegram токен не настроен")
            return False
        
        try:
            # Тест API
            url = f"https://api.telegram.org/bot{self.telegram_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_data = response.json()
                if bot_data.get("ok"):
                    bot_info = bot_data["result"]
                    print(f"✅ Telegram бот подключен: @{bot_info.get('username', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Ошибка Telegram API: {bot_data.get('description', 'Unknown')}")
                    return False
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка подключения к Telegram: {e}")
            return False
    
    def test_telegram_send(self):
        """Тестирование отправки в Telegram"""
        print("\n📤 ТЕСТИРОВАНИЕ ОТПРАВКИ В TELEGRAM")
        print("-" * 40)
        
        if not self.telegram_token or not self.telegram_chat_id:
            print("❌ Telegram не настроен полностью")
            return False
        
        try:
            message = f"🧪 Тестовое сообщение от Quick Voice Assistant\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print("✅ Сообщение отправлено в Telegram")
                    return True
                else:
                    print(f"❌ Ошибка отправки: {result.get('description', 'Unknown')}")
                    return False
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def test_notion_create(self):
        """Тестирование создания в Notion с учетом реальной структуры"""
        print("\n📝 ТЕСТИРОВАНИЕ СОЗДАНИЯ В NOTION")
        print("-" * 40)
        
        if not self.notion_token:
            print("❌ Notion токен не настроен")
            return False
        
        tasks_db_id = os.getenv("NOTION_TASKS_DB")
        if not tasks_db_id:
            print("❌ ID базы данных задач не настроен")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            # Получаем структуру базы
            url = f"https://api.notion.com/v1/databases/{tasks_db_id}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"❌ Ошибка получения структуры: {resp.status_code}")
                print(f"Ответ: {resp.text}")
                return False
            db = resp.json()
            props = db.get("properties", {})
            # Определяем поле title
            title_field = None
            for k, v in props.items():
                if v.get("type") == "title":
                    title_field = k
                    break
            if not title_field:
                print("❌ Не найдено поле title")
                return False
            # Собираем payload
            payload = {
                "parent": {"database_id": tasks_db_id},
                "properties": {
                    title_field: {
                        "title": [{"text": {"content": "🧪 Тестовая задача (реальные поля)"}}]
                    }
                }
            }
            # Добавляем select-поля с первым вариантом
            for field in ["Статус", "Приоритет", "Категория"]:
                if field in props and props[field]["type"] == "select":
                    options = props[field]["select"].get("options", [])
                    if options:
                        payload["properties"][field] = {"select": {"name": options[0]["name"]}}
            # Добавляем дату
            for field in ["Дедлайн", "Дата старта"]:
                if field in props and props[field]["type"] == "date":
                    payload["properties"][field] = {"date": {"start": datetime.now().isoformat()}}
            # Отправляем
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Тестовая задача создана в Notion (реальные поля)")
                return True
            else:
                print(f"❌ Ошибка создания: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка создания в Notion: {e}")
            return False
    
    def test_server_integration(self):
        """Тестирование интеграции через сервер"""
        print("\n🖥️ ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЧЕРЕЗ СЕРВЕР")
        print("-" * 45)
        
        try:
            # Тест голосовой команды
            test_payload = {
                "query": "добавь задачу протестировать реальные сервисы",
                "context": "test",
                "timestamp": int(datetime.now().timestamp()),
                "user_id": "test_user"
            }
            
            response = requests.post(
                "http://localhost:8000/watch/voice",
                json=test_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Команда обработана сервером")
                print(f"   Ответ: {data.get('response', 'N/A')[:50]}...")
                print(f"   Действие: {data.get('action', 'N/A')}")
                return True
            else:
                print(f"❌ Ошибка сервера: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Сервер не запущен. Запустите: python start_quick_voice_assistant.py")
            return False
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
    
    def generate_setup_instructions(self):
        """Генерация инструкций по настройке"""
        print("\n📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ")
        print("="*50)
        
        print("🔗 NOTION:")
        print("1. Перейди на: https://www.notion.so/my-integrations")
        print("2. Создай новую интеграцию")
        print("3. Скопируй Internal Integration Token")
        print("4. Создай базы данных: Tasks, Reflections, Habits")
        print("5. Добавь интеграцию к каждой базе")
        print("6. Скопируй Database IDs из URL")
        
        print("\n📱 TELEGRAM:")
        print("1. Найди @BotFather в Telegram")
        print("2. Отправь: /newbot")
        print("3. Следуй инструкциям")
        print("4. Скопируй токен бота")
        print("5. Отправь сообщение боту")
        print("6. Получи Chat ID: https://api.telegram.org/bot<TOKEN>/getUpdates")
        
        print("\n⚙️ КОНФИГУРАЦИЯ:")
        print("1. Отредактируй файл .env")
        print("2. Добавь все токены и ID")
        print("3. Запусти этот скрипт снова")
    
    def run_full_test(self):
        """Полное тестирование системы"""
        print("\n🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
        print("="*50)
        
        tests = [
            ("Проверка конфигурации", self.check_current_config),
            ("Подключение к Notion", self.test_notion_connection),
            ("Подключение к Telegram", self.test_telegram_connection),
            ("Отправка в Telegram", self.test_telegram_send),
            ("Создание в Notion", self.test_notion_create),
            ("Интеграция через сервер", self.test_server_integration)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}...")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = asyncio.run(test_func())
                else:
                    result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Ошибка в тесте {test_name}: {e}")
                results.append((test_name, False))
        
        # Итоговый отчет
        print("\n📊" + "="*50)
        print("📋 ИТОГОВЫЙ ОТЧЕТ")
        print("="*52)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{status} | {test_name}")
        
        print(f"\n📈 Результат: {passed}/{total} тестов пройдено")
        
        if passed == total:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к использованию!")
        else:
            print("⚠️  Некоторые тесты провалены. Проверьте конфигурацию.")
            self.generate_setup_instructions()
        
        return passed == total

def main():
    """Основная функция"""
    setup = RealServicesSetup()
    setup.print_header()
    
    # Проверяем, есть ли токены
    config = setup.check_current_config()
    
    if not any(config.values()):
        print("\n❌ Токены не настроены")
        setup.generate_setup_instructions()
        return
    
    # Запускаем полное тестирование
    success = setup.run_full_test()
    
    if success:
        print("\n🚀 СИСТЕМА ГОТОВА К ПРОДУКТИВНОМУ ИСПОЛЬЗОВАНИЮ!")
        print("📱 Установи приложение на часы и протестируй голосовые команды!")
    else:
        print("\n🔧 НЕОБХОДИМО ДОНАСТРОИТЬ СЕРВИСЫ")
        print("📋 Следуй инструкциям выше для настройки")

if __name__ == "__main__":
    main() 