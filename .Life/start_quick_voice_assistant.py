#!/usr/bin/env python3
"""
🚀 ЗАПУСК QUICK VOICE ASSISTANT
Автоматический запуск системы с проверкой всех компонентов
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class QuickVoiceAssistantLauncher:
    """Запуск системы Quick Voice Assistant"""
    
    def __init__(self):
        self.server_process = None
        self.status = {
            "server": False,
            "notion": False,
            "telegram": False,
            "watch_app": False
        }
    
    def print_header(self):
        """Вывод заголовка"""
        print("🚀" + "="*60)
        print("🎤 QUICK VOICE ASSISTANT - ЗАПУСК СИСТЕМЫ")
        print("="*62)
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)
    
    def check_environment(self) -> bool:
        """Проверка окружения"""
        print("\n🔍 ПРОВЕРКА ОКРУЖЕНИЯ")
        print("-" * 30)
        
        # Проверка виртуального окружения
        if not os.path.exists("venv"):
            print("❌ Виртуальное окружение не найдено")
            print("💡 Запустите: python DEPLOYMENT_PACKAGE/scripts/auto_deploy.py")
            return False
        
        # Проверка конфигурации
        if not os.path.exists(".env"):
            print("❌ Файл .env не найден")
            return False
        
        # Проверка сервера
        if not os.path.exists("server/llm_api_server.py"):
            print("❌ Файл сервера не найден")
            return False
        
        print("✅ Окружение готово")
        return True
    
    def check_configuration(self) -> bool:
        """Проверка конфигурации"""
        print("\n⚙️ ПРОВЕРКА КОНФИГУРАЦИИ")
        print("-" * 30)
        
        try:
            # Загрузка .env
            env_vars = {}
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value
            
            # Проверка обязательных параметров
            required_vars = [
                "NOTION_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not env_vars.get(var):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"⚠️  Не настроены переменные: {', '.join(missing_vars)}")
                print("💡 Отредактируйте файл .env и добавьте токены")
                return False
            
            print("✅ Конфигурация корректна")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка проверки конфигурации: {e}")
            return False
    
    def get_network_info(self) -> str:
        """Получение сетевой информации"""
        try:
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except:
            return "192.168.1.100"  # По умолчанию
    
    def start_server(self) -> bool:
        """Запуск сервера"""
        print("\n🚀 ЗАПУСК СЕРВЕРА")
        print("-" * 30)
        
        try:
            # Активация виртуального окружения
            if os.name == 'nt':  # Windows
                python_path = "venv\\Scripts\\python.exe"
            else:  # Linux/macOS
                python_path = "venv/bin/python"
            
            # Запуск сервера
            server_script = "server/llm_api_server.py"
            
            print(f"🎯 Запуск: {python_path} {server_script}")
            
            self.server_process = subprocess.Popen(
                [python_path, server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ожидание запуска
            time.sleep(3)
            
            # Проверка статуса
            if self.server_process.poll() is None:
                print("✅ Сервер запущен успешно")
                self.status["server"] = True
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Ошибка запуска сервера: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            return False
    
    def test_endpoints(self) -> bool:
        """Тестирование эндпоинтов"""
        print("\n🧪 ТЕСТИРОВАНИЕ API")
        print("-" * 30)
        
        try:
            import requests
            
            # Тест ping
            response = requests.get("http://localhost:8000/ping", timeout=5)
            if response.status_code == 200:
                print("✅ /ping - работает")
            else:
                print("❌ /ping - не отвечает")
                return False
            
            # Тест health
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                components = data.get("components", {})
                print(f"✅ /health - работает")
                print(f"   LLM: {'✅' if components.get('llm') else '❌'}")
                print(f"   Notion: {'✅' if components.get('notion') else '❌'}")
                print(f"   Telegram: {'✅' if components.get('telegram') else '❌'}")
            else:
                print("❌ /health - не отвечает")
                return False
            
            # Тест голосовой команды
            test_payload = {
                "query": "тестовая команда",
                "context": "test",
                "timestamp": int(time.time()),
                "user_id": "test_user"
            }
            
            response = requests.post(
                "http://localhost:8000/watch/voice",
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ /watch/voice - работает")
            else:
                print("❌ /watch/voice - не отвечает")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
    
    def show_usage_instructions(self):
        """Показать инструкции по использованию"""
        print("\n📱 ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ")
        print("="*50)
        
        ip_address = self.get_network_info()
        
        print("🎯 СЕРВЕР ЗАПУЩЕН:")
        print(f"   🌐 Локально: http://localhost:8000")
        print(f"   🌐 В сети: http://{ip_address}:8000")
        print(f"   📊 Документация: http://localhost:8000/docs")
        
        print("\n📱 УСТАНОВКА НА ЧАСЫ:")
        print("   1. Подключи часы к компьютеру")
        print("   2. Открой Xiaomi Wear")
        print("   3. Перейди в 'Приложения'")
        print("   4. Установи: watch_app/xiaomi_watch_app.js")
        print(f"   5. IP сервера: {ip_address}")
        
        print("\n🎤 ГОЛОСОВЫЕ КОМАНДЫ:")
        print("   • 'добавь задачу медитация'")
        print("   • 'запиши мысль о продуктивности'")
        print("   • 'создай привычку читать книги'")
        print("   • 'покажи прогресс'")
        print("   • 'как мое здоровье'")
        
        print("\n🔧 УПРАВЛЕНИЕ:")
        print("   • Остановка: Ctrl+C")
        print("   • Логи: logs/server.log")
        print("   • Тесты: python scripts/test_system.py")
        
        print("\n📞 ПОДДЕРЖКА:")
        print("   • Документация: INSTALLATION_GUIDE.md")
        print("   • Лог развертывания: deployment_log.jsonl")
        print("   • Практика ИИ: AI_ORCHESTRATION_PRACTICE.md")
    
    def run(self):
        """Основной метод запуска"""
        self.print_header()
        
        # Проверки
        if not self.check_environment():
            return False
        
        if not self.check_configuration():
            return False
        
        # Запуск сервера
        if not self.start_server():
            return False
        
        # Тестирование
        if not self.test_endpoints():
            print("⚠️  Сервер запущен, но есть проблемы с API")
        
        # Инструкции
        self.show_usage_instructions()
        
        print("\n🎉 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("="*50)
        
        try:
            # Ожидание завершения
            self.server_process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  Получен сигнал остановки...")
            if self.server_process:
                self.server_process.terminate()
                print("✅ Сервер остановлен")
        
        return True

def main():
    """Основная функция"""
    launcher = QuickVoiceAssistantLauncher()
    
    try:
        success = launcher.run()
        if not success:
            print("\n❌ Запуск не удался. Проверьте логи и конфигурацию.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 