#!/usr/bin/env python3
"""
Скрипт запуска LLM сервера с проверками окружения
"""

import os
import sys
import subprocess
import socket
import time
from datetime import datetime

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Требуется Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Проверяет установленные зависимости"""
    try:
        import requests
        print("✅ requests установлен")
    except ImportError:
        print("❌ requests не установлен")
        return False
    
    try:
        import json
        print("✅ json доступен")
    except ImportError:
        print("❌ json недоступен")
        return False
    
    return True

def check_port_availability(port=8000):
    """Проверяет доступность порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ Порт {port} свободен")
            return True
    except OSError:
        print(f"❌ Порт {port} занят")
        return False

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
    except Exception:
        return "127.0.0.1"

def install_dependencies():
    """Устанавливает зависимости"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀============================================================")
    print("🧠 LLM SERVER - ПРОВЕРКА И ЗАПУСК")
    print("==============================================================")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================================================")
    
    # Проверки
    print("🔍 ПРОВЕРКА ОКРУЖЕНИЯ")
    print("------------------------------")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("📦 Попытка установки зависимостей...")
        if not install_dependencies():
            sys.exit(1)
    
    if not check_port_availability():
        print("🔧 Попробуйте другой порт или остановите процесс на порту 8000")
        sys.exit(1)
    
    print("✅ Окружение готово")
    
    print("⚙️ ПРОВЕРКА КОНФИГУРАЦИИ")
    print("------------------------------")
    
    # Проверяем наличие файла сервера
    if not os.path.exists("simple_llm_server.py"):
        print("❌ Файл simple_llm_server.py не найден")
        sys.exit(1)
    
    print("✅ Конфигурация корректна")
    
    print("🚀 ЗАПУСК СЕРВЕРА")
    print("------------------------------")
    
    local_ip = get_local_ip()
    print(f"🎯 Запуск: {sys.executable} simple_llm_server.py")
    
    try:
        # Запускаем сервер
        subprocess.run([sys.executable, "simple_llm_server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 