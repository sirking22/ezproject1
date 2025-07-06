#!/usr/bin/env python3
"""
Скрипт для автоматического деплоя на Railway
с поддержкой DeepSea LLM и твоими настройками
"""

import os
import subprocess
import json
import requests
from pathlib import Path

class RailwayDeployer:
    def __init__(self):
        self.project_name = "life-system-bots"
        self.railway_token = os.getenv("RAILWAY_TOKEN")
        
    def create_railway_config(self):
        """Создание конфигурации для Railway"""
        
        # Создаем railway.json
        railway_config = {
            "build": {
                "builder": "DOCKERFILE"
            },
            "deploy": {
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        
        with open("railway.json", "w") as f:
            json.dump(railway_config, f, indent=2)
            
        print("✅ railway.json создан")
        
    def create_procfile(self):
        """Создание Procfile для Railway"""
        
        procfile_content = """# Railway Procfile
web: python server/llm_api_server.py
admin-bot: python run_admin_bot.py
enhanced-bot: python run_enhanced_bot.py
agent-team: python run_agent_team.py
"""
        
        with open("Procfile", "w") as f:
            f.write(procfile_content)
            
        print("✅ Procfile создан")
        
    def create_railway_toml(self):
        """Создание railway.toml для переменных окружения"""
        
        toml_content = f"""[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "python server/llm_api_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[deploy.variables]
# Telegram Bot Tokens
TELEGRAM_BOT_TOKEN = "{os.getenv('TELEGRAM_BOT_TOKEN', '')}"
TELEGRAM_ENHANCED_BOT_TOKEN = "{os.getenv('TELEGRAM_ENHANCED_BOT_TOKEN', '')}"
TELEGRAM_AGENT_BOT_TOKEN = "{os.getenv('TELEGRAM_AGENT_BOT_TOKEN', '')}"
TELEGRAM_ALLOWED_USERS = "{os.getenv('TELEGRAM_ALLOWED_USERS', '')}"
TELEGRAM_ADMIN_USERS = "{os.getenv('TELEGRAM_ADMIN_USERS', '')}"

# Notion Configuration
NOTION_TOKEN = "{os.getenv('NOTION_TOKEN', '')}"
NOTION_DATABASES = "{os.getenv('NOTION_DATABASES', '')}"

# DeepSea LLM Configuration
OPENROUTER_API_KEY = "{os.getenv('OPENROUTER_API_KEY', '')}"
DEEPSEA_API_URL = "https://api.deepsea.ai"
DEEPSEA_MODEL = "deepsea-codellama-34b-instruct"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = "8000"
DEBUG = "False"
RELOAD = "False"

# Performance Configuration
MAX_WORKERS = "4"
REQUEST_TIMEOUT = "30"
CACHE_SIZE = "1000"
ENABLE_COMPRESSION = "True"
ENABLE_CACHING = "True"

# Security Configuration
ALLOWED_HOSTS = "*"
RATE_LIMIT = "100"
ENABLE_LOGGING = "True"

# Monitoring Configuration
ENABLE_METRICS = "True"
LOG_LEVEL = "INFO"
SAVE_LOGS = "True"
LOG_FILE = "logs/server.log"
"""
        
        with open("railway.toml", "w") as f:
            f.write(toml_content)
            
        print("✅ railway.toml создан")
        
    def update_dockerfile_for_railway(self):
        """Обновление Dockerfile для Railway"""
        
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание директорий для логов
RUN mkdir -p logs

# Открытие порта
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск сервера
CMD ["python", "server/llm_api_server.py"]
"""
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
            
        print("✅ Dockerfile обновлен для Railway")
        
    def create_startup_script(self):
        """Создание скрипта запуска для Railway"""
        
        script_content = """#!/bin/bash
# Railway startup script

echo "🚀 Запуск Life System Bots на Railway..."

# Создание директорий
mkdir -p logs
mkdir -p cache
mkdir -p data

# Проверка переменных окружения
echo "📋 Проверка конфигурации..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN не установлен"
    exit 1
fi

if [ -z "$NOTION_TOKEN" ]; then
    echo "❌ NOTION_TOKEN не установлен"
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ OPENROUTER_API_KEY не установлен"
    exit 1
fi

echo "✅ Конфигурация проверена"

# Запуск сервера
echo "🌐 Запуск LLM API сервера..."
python server/llm_api_server.py
"""
        
        with open("startup.sh", "w") as f:
            f.write(script_content)
            
        # Делаем скрипт исполняемым
        os.chmod("startup.sh", 0o755)
        
        print("✅ startup.sh создан")
        
    def create_github_workflow(self):
        """Создание GitHub Actions workflow для автодеплоя"""
        
        workflow_content = """name: Deploy to Railway

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Railway CLI
      run: npm install -g @railway/cli
    
    - name: Deploy to Railway
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
      run: |
        railway login --token $RAILWAY_TOKEN
        railway up
"""
        
        # Создаем директорию .github/workflows
        Path(".github/workflows").mkdir(parents=True, exist_ok=True)
        
        with open(".github/workflows/railway-deploy.yml", "w") as f:
            f.write(workflow_content)
            
        print("✅ GitHub Actions workflow создан")
        
    def create_env_template(self):
        """Создание шаблона .env для Railway"""
        
        env_template = """# Railway Environment Variables Template
# Скопируй этот файл в .env и заполни значения

# Telegram Bot Tokens (создай 3 разных бота)
TELEGRAM_BOT_TOKEN=your_admin_bot_token
TELEGRAM_ENHANCED_BOT_TOKEN=your_enhanced_bot_token  
TELEGRAM_AGENT_BOT_TOKEN=your_agent_bot_token

# Telegram Users (твой ID)
TELEGRAM_ALLOWED_USERS=your_telegram_id
TELEGRAM_ADMIN_USERS=your_telegram_id

# Notion Configuration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASES={"tasks":"db_id","habits":"db_id","rituals":"db_id","reflections":"db_id","ideas":"db_id","materials":"db_id","agent_prompts":"db_id"}

# DeepSea LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
RELOAD=False

# Performance Configuration
MAX_WORKERS=4
REQUEST_TIMEOUT=30
CACHE_SIZE=1000
ENABLE_COMPRESSION=True
ENABLE_CACHING=True

# Security Configuration
ALLOWED_HOSTS=*
RATE_LIMIT=100
ENABLE_LOGGING=True

# Monitoring Configuration
ENABLE_METRICS=True
LOG_LEVEL=INFO
SAVE_LOGS=True
LOG_FILE=logs/server.log
"""
        
        with open(".env.template", "w") as f:
            f.write(env_template)
            
        print("✅ .env.template создан")
        
    def deploy_to_railway(self):
        """Основной процесс деплоя"""
        
        print("🚀 Начинаем деплой на Railway...")
        
        # Создаем все необходимые файлы
        self.create_railway_config()
        self.create_procfile()
        self.create_railway_toml()
        self.update_dockerfile_for_railway()
        self.create_startup_script()
        self.create_github_workflow()
        self.create_env_template()
        
        print("\n📋 Следующие шаги:")
        print("1. Создай аккаунт на Railway.app")
        print("2. Установи Railway CLI: npm install -g @railway/cli")
        print("3. Войди в Railway: railway login")
        print("4. Создай проект: railway init")
        print("5. Настрой переменные окружения в Railway Dashboard")
        print("6. Деплой: railway up")
        
        print("\n🔧 Или используй GitHub Actions для автодеплоя:")
        print("1. Добавь RAILWAY_TOKEN в GitHub Secrets")
        print("2. Запушь код в main ветку")
        print("3. Railway автоматически задеплоит изменения")

def main():
    deployer = RailwayDeployer()
    deployer.deploy_to_railway()

if __name__ == "__main__":
    main() 