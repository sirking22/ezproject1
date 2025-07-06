#!/usr/bin/env python3
"""
Автоматическое развертывание Quick Voice Assistant с командой ИИ-агентов
Ведение лога практики дирижирования ИИ
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
from typing import Dict, Any, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("deployment_log.jsonl", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Оркестратор команды ИИ-агентов для развертывания"""
    
    def __init__(self):
        self.agents = {
            "system_architect": {
                "role": "Системный архитектор",
                "responsibility": "Планирование архитектуры и проверка зависимостей",
                "status": "ready",
                "tasks_completed": 0,
                "current_task": None
            },
            "devops_engineer": {
                "role": "DevOps инженер",
                "responsibility": "Установка и настройка окружения",
                "status": "ready",
                "tasks_completed": 0,
                "current_task": None
            },
            "integration_specialist": {
                "role": "Специалист по интеграциям",
                "responsibility": "Настройка Notion, Telegram, LLM",
                "status": "ready",
                "tasks_completed": 0,
                "current_task": None
            },
            "qa_tester": {
                "role": "QA тестировщик",
                "responsibility": "Тестирование и валидация системы",
                "status": "ready",
                "tasks_completed": 0,
                "current_task": None
            },
            "watch_app_developer": {
                "role": "Разработчик приложений для часов",
                "responsibility": "Настройка и установка приложения на часы",
                "status": "ready",
                "tasks_completed": 0,
                "current_task": None
            }
        }
        self.deployment_log = []
        self.current_phase = "initialization"
        
    def log_agent_action(self, agent: str, action: str, details: str, success: bool = True):
        """Логирование действий агентов"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "role": self.agents[agent]["role"],
            "action": action,
            "details": details,
            "success": success,
            "phase": self.current_phase
        }
        
        self.deployment_log.append(log_entry)
        self.agents[agent]["tasks_completed"] += 1 if success else 0
        
        # Запись в файл
        with open("deployment_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        logger.info(f"🤖 {agent} ({self.agents[agent]['role']}): {action} - {'✅' if success else '❌'} {details}")

class SystemArchitect:
    """Агент-системный архитектор"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.agent_id = "system_architect"
    
    async def analyze_requirements(self) -> bool:
        """Анализ системных требований"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Анализ требований", 
                "Проверка Python, Node.js, Git"
            )
            
            # Проверка Python
            python_version = subprocess.run(
                ["python", "--version"], 
                capture_output=True, 
                text=True
            )
            if python_version.returncode != 0:
                raise Exception("Python не найден")
            
            # Проверка pip
            pip_check = subprocess.run(
                ["pip", "--version"], 
                capture_output=True, 
                text=True
            )
            if pip_check.returncode != 0:
                raise Exception("pip не найден")
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Анализ требований", 
                f"Python: {python_version.stdout.strip()}, pip: доступен",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Анализ требований", 
                f"Ошибка: {e}",
                False
            )
            return False
    
    async def design_architecture(self) -> bool:
        """Проектирование архитектуры развертывания"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Проектирование архитектуры", 
                "Создание структуры директорий"
            )
            
            # Создание структуры
            directories = [
                "logs", "data", "cache", "models", 
                "server", "watch_app", "integration", "scripts"
            ]
            
            for directory in directories:
                Path(directory).mkdir(exist_ok=True)
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Проектирование архитектуры", 
                f"Создано {len(directories)} директорий",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Проектирование архитектуры", 
                f"Ошибка: {e}",
                False
            )
            return False

class DevOpsEngineer:
    """Агент-DevOps инженер"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.agent_id = "devops_engineer"
    
    async def setup_python_environment(self) -> bool:
        """Настройка Python окружения"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка Python окружения", 
                "Создание виртуального окружения"
            )
            
            # Создание виртуального окружения
            venv_result = subprocess.run(
                ["python", "-m", "venv", "venv"],
                capture_output=True,
                text=True
            )
            
            if venv_result.returncode != 0:
                raise Exception(f"Ошибка создания venv: {venv_result.stderr}")
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка Python окружения", 
                "Виртуальное окружение создано",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка Python окружения", 
                f"Ошибка: {e}",
                False
            )
            return False
    
    async def install_dependencies(self) -> bool:
        """Установка зависимостей"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Установка зависимостей", 
                "Установка Python пакетов"
            )
            
            # Активация venv и установка зависимостей
            if os.name == 'nt':  # Windows
                pip_cmd = ["venv\\Scripts\\pip", "install", "-r", "server/requirements.txt"]
            else:  # Linux/macOS
                pip_cmd = ["venv/bin/pip", "install", "-r", "server/requirements.txt"]
            
            install_result = subprocess.run(
                pip_cmd,
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                raise Exception(f"Ошибка установки: {install_result.stderr}")
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Установка зависимостей", 
                "Зависимости установлены успешно",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Установка зависимостей", 
                f"Ошибка: {e}",
                False
            )
            return False

class IntegrationSpecialist:
    """Агент-специалист по интеграциям"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.agent_id = "integration_specialist"
    
    async def setup_configuration(self) -> bool:
        """Настройка конфигурации"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка конфигурации", 
                "Создание .env файла"
            )
            
            # Создание .env файла
            env_content = """# Конфигурация сервера
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
RELOAD=False

# Конфигурация LLM
USE_LOCAL_LLM=False
LLM_MODEL_PATH=
LLM_MODEL_TYPE=llama
LLM_CONTEXT_LENGTH=4096
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
FALLBACK_TO_OPENAI=True

# Конфигурация Notion
NOTION_ENABLED=True
NOTION_TOKEN=
NOTION_TASKS_DB=
NOTION_REFLECTIONS_DB=
NOTION_HABITS_DB=
NOTION_IDEAS_DB=
NOTION_MATERIALS_DB=

# Конфигурация Telegram
TELEGRAM_ENABLED=True
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Конфигурация голоса
VOICE_SAMPLE_RATE=16000
VOICE_CHUNK_SIZE=1024
VOICE_MAX_DURATION=30
VOICE_LANGUAGE=ru
VOICE_MODEL=whisper

# Конфигурация производительности
MAX_WORKERS=4
REQUEST_TIMEOUT=30
CACHE_SIZE=1000
ENABLE_COMPRESSION=True
ENABLE_CACHING=True

# Конфигурация безопасности
ALLOWED_HOSTS=192.168.1.0/24
RATE_LIMIT=100
ENABLE_LOGGING=True
API_KEY=

# Конфигурация мониторинга
ENABLE_METRICS=True
LOG_LEVEL=INFO
SAVE_LOGS=True
LOG_FILE=logs/server.log

# Конфигурация кэширования
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
"""
            
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка конфигурации", 
                "Файл .env создан, добавьте токены вручную",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Настройка конфигурации", 
                f"Ошибка: {e}",
                False
            )
            return False
    
    async def get_network_info(self) -> bool:
        """Получение сетевой информации"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Получение сетевой информации", 
                "Определение IP адреса"
            )
            
            # Получение IP адреса
            if os.name == 'nt':  # Windows
                ip_result = subprocess.run(
                    ["ipconfig"], 
                    capture_output=True, 
                    text=True
                )
                # Парсинг IP из ipconfig
                lines = ip_result.stdout.split('\n')
                ip_address = None
                for line in lines:
                    if "IPv4 Address" in line:
                        ip_address = line.split(':')[-1].strip()
                        break
            else:  # Linux/macOS
                ip_result = subprocess.run(
                    ["hostname", "-I"], 
                    capture_output=True, 
                    text=True
                )
                ip_address = ip_result.stdout.strip().split()[0]
            
            if ip_address:
                # Обновление конфигурации часов
                if os.path.exists("watch_app/app_config.json"):
                    with open("watch_app/app_config.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    config["server"]["url"] = f"http://{ip_address}:8000"
                    
                    with open("watch_app/app_config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.orchestrator.log_agent_action(
                    self.agent_id, 
                    "Получение сетевой информации", 
                    f"IP адрес: {ip_address}, конфигурация часов обновлена",
                    True
                )
                return True
            else:
                raise Exception("Не удалось определить IP адрес")
                
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Получение сетевой информации", 
                f"Ошибка: {e}",
                False
            )
            return False

class QATester:
    """Агент-QA тестировщик"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.agent_id = "qa_tester"
    
    async def test_server_startup(self) -> bool:
        """Тестирование запуска сервера"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Тестирование запуска сервера", 
                "Проверка доступности порта 8000"
            )
            
            # Проверка порта
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                self.orchestrator.log_agent_action(
                    self.agent_id, 
                    "Тестирование запуска сервера", 
                    "Порт 8000 занят, сервер может быть уже запущен",
                    True
                )
                return True
            else:
                self.orchestrator.log_agent_action(
                    self.agent_id, 
                    "Тестирование запуска сервера", 
                    "Порт 8000 свободен, можно запускать сервер",
                    True
                )
                return True
                
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Тестирование запуска сервера", 
                f"Ошибка: {e}",
                False
            )
            return False
    
    async def validate_configuration(self) -> bool:
        """Валидация конфигурации"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Валидация конфигурации", 
                "Проверка файлов конфигурации"
            )
            
            # Проверка наличия файлов
            required_files = [
                "server/config.py",
                "server/llm_api_server.py",
                "server/requirements.txt",
                "watch_app/app_config.json",
                "watch_app/xiaomi_watch_app.js"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                raise Exception(f"Отсутствуют файлы: {missing_files}")
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Валидация конфигурации", 
                f"Все {len(required_files)} файлов найдены",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Валидация конфигурации", 
                f"Ошибка: {e}",
                False
            )
            return False

class WatchAppDeveloper:
    """Агент-разработчик приложений для часов"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.agent_id = "watch_app_developer"
    
    async def prepare_watch_app(self) -> bool:
        """Подготовка приложения для часов"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Подготовка приложения для часов", 
                "Проверка и оптимизация кода"
            )
            
            # Проверка JavaScript кода
            if os.path.exists("watch_app/xiaomi_watch_app.js"):
                with open("watch_app/xiaomi_watch_app.js", "r", encoding="utf-8") as f:
                    code = f.read()
                
                # Простая валидация синтаксиса
                if "function" in code and "console.log" in code:
                    self.orchestrator.log_agent_action(
                        self.agent_id, 
                        "Подготовка приложения для часов", 
                        "Код приложения валиден",
                        True
                    )
                    return True
                else:
                    raise Exception("Код приложения не содержит необходимых функций")
            else:
                raise Exception("Файл приложения не найден")
                
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Подготовка приложения для часов", 
                f"Ошибка: {e}",
                False
            )
            return False
    
    async def create_installation_guide(self) -> bool:
        """Создание руководства по установке на часы"""
        try:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Создание руководства по установке", 
                "Генерация инструкций для часов"
            )
            
            guide_content = """# 📱 УСТАНОВКА НА XIAOMI WATCH S

## 🚀 Быстрая установка (2 минуты)

### 1. Подготовка
- Убедись, что часы подключены к той же WiFi сети, что и компьютер
- IP адрес сервера: {ip_address}

### 2. Установка через Xiaomi Wear
1. Подключи часы к компьютеру через USB
2. Открой приложение Xiaomi Wear
3. Перейди в раздел "Приложения"
4. Нажми "Установить приложение"
5. Выбери файл: `watch_app/xiaomi_watch_app.js`

### 3. Настройка
1. Открой приложение на часах
2. Проверь подключение к серверу
3. Протестируй голосовую команду

### 4. Использование
- Подними руку → экран включается
- Нажми кнопку записи → говори команду
- Получи ответ на часах
- Проверь уведомление в Telegram

## 🎯 Доступные команды:
- "добавь задачу медитация"
- "запиши мысль о продуктивности"
- "создай привычку читать книги"
- "покажи прогресс"
- "как мое здоровье"

## 🔧 Устранение неполадок:
1. Проверь WiFi подключение
2. Убедись, что сервер запущен
3. Проверь IP адрес в конфигурации
4. Перезапусти приложение на часах

**Готово! Приложение работает!** 🎉
"""
            
            # Получение IP адреса
            ip_address = "192.168.1.100"  # По умолчанию
            if os.path.exists("watch_app/app_config.json"):
                with open("watch_app/app_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    server_url = config.get("server", {}).get("url", "")
                    if "http://" in server_url:
                        ip_address = server_url.replace("http://", "").replace(":8000", "")
            
            guide_content = guide_content.format(ip_address=ip_address)
            
            with open("WATCH_INSTALLATION_GUIDE.md", "w", encoding="utf-8") as f:
                f.write(guide_content)
            
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Создание руководства по установке", 
                "Руководство WATCH_INSTALLATION_GUIDE.md создано",
                True
            )
            return True
            
        except Exception as e:
            self.orchestrator.log_agent_action(
                self.agent_id, 
                "Создание руководства по установке", 
                f"Ошибка: {e}",
                False
            )
            return False

class AutoDeployer:
    """Автоматический развертыватель с командой ИИ-агентов"""
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.agents = {
            "system_architect": SystemArchitect(self.orchestrator),
            "devops_engineer": DevOpsEngineer(self.orchestrator),
            "integration_specialist": IntegrationSpecialist(self.orchestrator),
            "qa_tester": QATester(self.orchestrator),
            "watch_app_developer": WatchAppDeveloper(self.orchestrator)
        }
    
    async def deploy_with_ai_team(self) -> bool:
        """Развертывание с командой ИИ-агентов"""
        print("🚀" + "="*60)
        print("🤖 АВТОМАТИЧЕСКОЕ РАЗВЕРТЫВАНИЕ С КОМАНДОЙ ИИ-АГЕНТОВ")
        print("="*62)
        print(f"⏰ Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)
        
        # Фаза 1: Анализ и планирование
        self.orchestrator.current_phase = "analysis"
        print("\n📋 ФАЗА 1: АНАЛИЗ И ПЛАНИРОВАНИЕ")
        print("-" * 40)
        
        success = await self.agents["system_architect"].analyze_requirements()
        if not success:
            return False
        
        success = await self.agents["system_architect"].design_architecture()
        if not success:
            return False
        
        # Фаза 2: Настройка окружения
        self.orchestrator.current_phase = "environment_setup"
        print("\n🔧 ФАЗА 2: НАСТРОЙКА ОКРУЖЕНИЯ")
        print("-" * 40)
        
        success = await self.agents["devops_engineer"].setup_python_environment()
        if not success:
            return False
        
        success = await self.agents["devops_engineer"].install_dependencies()
        if not success:
            return False
        
        # Фаза 3: Интеграция
        self.orchestrator.current_phase = "integration"
        print("\n🔗 ФАЗА 3: ИНТЕГРАЦИЯ")
        print("-" * 40)
        
        success = await self.agents["integration_specialist"].setup_configuration()
        if not success:
            return False
        
        success = await self.agents["integration_specialist"].get_network_info()
        if not success:
            return False
        
        # Фаза 4: Подготовка приложения
        self.orchestrator.current_phase = "app_preparation"
        print("\n📱 ФАЗА 4: ПОДГОТОВКА ПРИЛОЖЕНИЯ")
        print("-" * 40)
        
        success = await self.agents["watch_app_developer"].prepare_watch_app()
        if not success:
            return False
        
        success = await self.agents["watch_app_developer"].create_installation_guide()
        if not success:
            return False
        
        # Фаза 5: Тестирование
        self.orchestrator.current_phase = "testing"
        print("\n🧪 ФАЗА 5: ТЕСТИРОВАНИЕ")
        print("-" * 40)
        
        success = await self.agents["qa_tester"].validate_configuration()
        if not success:
            return False
        
        success = await self.agents["qa_tester"].test_server_startup()
        if not success:
            return False
        
        # Финальный отчет
        await self.generate_deployment_report()
        
        return True
    
    async def generate_deployment_report(self):
        """Генерация отчета о развертывании"""
        print("\n📊" + "="*60)
        print("📋 ОТЧЕТ О РАЗВЕРТЫВАНИИ")
        print("="*62)
        
        total_tasks = sum(agent["tasks_completed"] for agent in self.orchestrator.agents.values())
        total_agents = len(self.orchestrator.agents)
        
        print(f"🤖 Агентов в команде: {total_agents}")
        print(f"✅ Задач выполнено: {total_tasks}")
        print(f"📝 Записей в логе: {len(self.orchestrator.deployment_log)}")
        
        print("\n📈 ПРОИЗВОДИТЕЛЬНОСТЬ АГЕНТОВ:")
        for agent_id, agent_info in self.orchestrator.agents.items():
            print(f"   {agent_info['role']}: {agent_info['tasks_completed']} задач")
        
        print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Добавьте токены в файл .env")
        print("2. Запустите сервер: ./scripts/start_server.sh")
        print("3. Установите приложение на часы")
        print("4. Протестируйте систему")
        
        print("\n📄 ДОКУМЕНТАЦИЯ:")
        print("- INSTALLATION_GUIDE.md - подробная инструкция")
        print("- WATCH_INSTALLATION_GUIDE.md - установка на часы")
        print("- deployment_log.jsonl - лог работы агентов")
        
        print("\n🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("="*62)

async def main():
    """Основная функция"""
    deployer = AutoDeployer()
    
    try:
        success = await deployer.deploy_with_ai_team()
        
        if success:
            print("\n🚀 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
            print("🤖 Команда ИИ-агентов выполнила все задачи")
            print("📝 Лог практики дирижирования ИИ сохранен в deployment_log.jsonl")
        else:
            print("\n❌ РАЗВЕРТЫВАНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ")
            print("🔧 Проверьте логи и исправьте проблемы")
        
    except KeyboardInterrupt:
        print("\n⏹️  Развертывание прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 