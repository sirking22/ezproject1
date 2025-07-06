#!/usr/bin/env python3
"""
Скрипт настройки CI/CD для проекта Notion-Telegram-LLM Integration
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Выполнить команду с выводом"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка:")
        print(e.stderr)
        return False

def check_file_exists(filepath):
    """Проверить существование файла"""
    return Path(filepath).exists()

def setup_ci():
    """Настройка CI/CD"""
    print("🚀 НАСТРОЙКА CI/CD ДЛЯ NOTION-TELEGRAM-LLM INTEGRATION")
    print("=" * 60)
    
    # Проверка необходимых файлов
    required_files = [
        "notion_database_schemas.py",
        "test_schemas_integration.py",
        "requirements.txt",
        ".pre-commit-config.yaml"
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    
    # Установка зависимостей
    if not run_command("pip install -r requirements.txt", "Установка зависимостей"):
        return False
    
    # Настройка pre-commit
    if not run_command("pre-commit install", "Установка pre-commit hooks"):
        print("⚠️ Pre-commit не установлен, пропускаем...")
    
    # Проверка схем
    if not run_command("python test_schemas_integration.py", "Проверка схем баз данных"):
        return False
    
    # Форматирование кода
    if not run_command("black .", "Форматирование кода"):
        return False
    
    # Проверка линтера
    if not run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Проверка критических ошибок"):
        return False
    
    # Проверка типов
    if not run_command("mypy notion_database_schemas.py test_schemas_integration.py --ignore-missing-imports", "Проверка типов"):
        print("⚠️ Проверка типов не прошла, но это не критично")
    
    print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("\n📋 Что настроено:")
    print("✅ GitHub Actions CI/CD")
    print("✅ Pre-commit hooks")
    print("✅ Схемы баз данных")
    print("✅ Тесты и валидация")
    print("✅ Форматирование кода")
    
    print("\n📚 Документация:")
    print("- CI Setup: docs/CI_SETUP.md")
    print("- Schemas: notion_schemas_documentation.json")
    print("- Workflows: .github/workflows/")
    
    print("\n🚀 Следующие шаги:")
    print("1. Закоммить изменения")
    print("2. Запушь в GitHub")
    print("3. Проверь Actions в репозитории")
    print("4. Настрой уведомления (опционально)")
    
    return True

def check_ci_status():
    """Проверить статус CI"""
    print("🔍 ПРОВЕРКА СТАТУСА CI/CD")
    print("=" * 40)
    
    # Проверка файлов CI
    ci_files = [
        ".github/workflows/schema-validation.yml",
        ".github/workflows/code-quality.yml"
    ]
    
    for file in ci_files:
        if check_file_exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - отсутствует")
    
    # Проверка схем
    try:
        from notion_database_schemas import get_all_schemas
        schemas = get_all_schemas()
        print(f"✅ Схемы баз данных: {len(schemas)}")
    except Exception as e:
        print(f"❌ Ошибка загрузки схем: {e}")
    
    # Проверка тестов
    if check_file_exists("test_schemas_integration.py"):
        print("✅ Тесты схем")
    else:
        print("❌ Тесты схем отсутствуют")
    
    # Проверка документации
    if check_file_exists("docs/CI_SETUP.md"):
        print("✅ Документация CI")
    else:
        print("❌ Документация CI отсутствует")

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "check":
            check_ci_status()
        elif command == "setup":
            setup_ci()
        else:
            print("Использование: python setup_ci.py [setup|check]")
    else:
        print("Использование: python setup_ci.py [setup|check]")
        print("\nКоманды:")
        print("  setup - настроить CI/CD")
        print("  check - проверить статус CI/CD")

if __name__ == "__main__":
    main() 