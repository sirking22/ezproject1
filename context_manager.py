#!/usr/bin/env python3
"""
Умный менеджер контекста для проекта
Автоматически определяет нужные файлы для прикрепления к чату
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class ContextManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.context_files = {
            'ai_context': 'AI_CONTEXT.md',
            'daily': 'DAILY.md',
            'status': 'STATUS.md',
            'mistakes': 'MISTAKES.md',
            'quick_commands': 'quick_commands.md',
            'bot_template': 'bot_template.py',
            'features': 'docs/FEATURES.md',
            'structure': 'docs/PROJECT_STRUCTURE.md',
            'env_management': 'docs/ENV_MANAGEMENT.md'
        }
        
    def check_file_exists(self, filename: str) -> bool:
        """Проверяет существование файла"""
        return (self.project_root / filename).exists()
    
    def get_file_info(self, filename: str) -> Dict:
        """Получает информацию о файле"""
        file_path = self.project_root / filename
        if file_path.exists():
            size = file_path.stat().st_size
            modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            return {
                'exists': True,
                'size': size,
                'modified': modified,
                'path': str(file_path)
            }
        return {'exists': False}
    
    def check_python_processes(self) -> int:
        """Проверяет количество процессов Python"""
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            python_processes = [line for line in lines if 'python.exe' in line]
            return len(python_processes) - 1  # Минус заголовок
        except:
            return 0
    
    def check_env_vars(self) -> List[str]:
        """Проверяет критические переменные окружения"""
        critical_vars = ['TELEGRAM_BOT_TOKEN', 'NOTION_TOKEN', 'YA_ACCESS_TOKEN']
        missing = []
        
        for var in critical_vars:
            if not os.getenv(var):
                missing.append(var)
        
        return missing
    
    def morning_routine(self):
        """Утренняя рутина"""
        print("🌅 УТРЕННЯЯ РУТИНА")
        print("=" * 50)
        
        # Проверяем состояние системы
        python_count = self.check_python_processes()
        missing_vars = self.check_env_vars()
        
        print(f"🔍 Проверка состояния:")
        if python_count > 0:
            print(f"⚠️  Найдено {python_count} Python процессов")
            print("   Рекомендация: taskkill /F /IM python.exe")
        else:
            print("✅ Нет лишних Python процессов")
        
        if missing_vars:
            print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        else:
            print("✅ Все критические переменные загружены")
        
        # Определяем файлы для прикрепления
        print(f"\n📋 ФАЙЛЫ ДЛЯ ПРИКРЕПЛЕНИЯ К ЧАТУ:")
        print("-" * 40)
        
        essential_files = ['ai_context', 'daily', 'status']
        for file_key in essential_files:
            filename = self.context_files[file_key]
            info = self.get_file_info(filename)
            if info['exists']:
                print(f"✅ {filename}")
            else:
                print(f"❌ {filename} (отсутствует)")
        
        print(f"\n🎯 ПРИОРИТЕТЫ СЕГОДНЯ:")
        print("-" * 40)
        
        # Читаем статус проекта
        status_file = self.context_files['status']
        if self.check_file_exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'В работе' in content:
                        print("🔄 Завершить материалы_bot_with_queue.py")
                    if 'Планы' in content:
                        print("📋 Система очередей и метаданные")
            except:
                print("📋 Проверить STATUS.md для приоритетов")
        
        print(f"\n🔧 СЛЕДУЮЩИЕ ШАГИ:")
        print("-" * 40)
        print("1. Прикрепить файлы к чату")
        print("2. Обновить план в DAILY.md")
        print("3. Запустить бота: python simple_bot.py")
    
    def problem_solver(self, problem_type: str):
        """Решает проблемы"""
        print(f"🚨 РЕШЕНИЕ ПРОБЛЕМЫ: {problem_type.upper()}")
        print("=" * 50)
        
        problem_files = {
            'event_loop': ['mistakes', 'quick_commands'],
            'telegram': ['mistakes', 'quick_commands'],
            'notion': ['mistakes', 'env_management'],
            'yandex': ['mistakes', 'env_management'],
            'bot': ['mistakes', 'quick_commands', 'bot_template'],
            'env': ['env_management', 'mistakes'],
            'default': ['mistakes', 'quick_commands']
        }
        
        files_to_show = problem_files.get(problem_type.lower(), problem_files['default'])
        
        print(f"📋 ФАЙЛЫ ДЛЯ РЕШЕНИЯ:")
        print("-" * 40)
        for file_key in files_to_show:
            filename = self.context_files[file_key]
            info = self.get_file_info(filename)
            if info['exists']:
                print(f"✅ {filename}")
            else:
                print(f"❌ {filename} (отсутствует)")
        
        print(f"\n🔧 БЫСТРЫЕ ДЕЙСТВИЯ:")
        print("-" * 40)
        
        if problem_type.lower() in ['event_loop', 'telegram', 'bot']:
            print("1. taskkill /F /IM python.exe")
            print("2. python daily_setup.py")
            print("3. python simple_bot.py")
        elif problem_type.lower() in ['notion', 'yandex', 'env']:
            print("1. Проверить переменные окружения")
            print("2. Обновить .env файл")
            print("3. Перезапустить бота")
        else:
            print("1. Посмотреть MISTAKES.md")
            print("2. Следовать quick_commands.md")
            print("3. Обновить DAILY.md с проблемой")
    
    def new_feature(self, feature_name: str = ""):
        """Подготовка к новой функции"""
        print(f"🆕 НОВАЯ ФУНКЦИЯ: {feature_name.upper() if feature_name else 'GENERAL'}")
        print("=" * 50)
        
        print(f"📋 ФАЙЛЫ ДЛЯ РАЗРАБОТКИ:")
        print("-" * 40)
        
        feature_files = ['features', 'structure', 'bot_template']
        for file_key in feature_files:
            filename = self.context_files[file_key]
            info = self.get_file_info(filename)
            if info['exists']:
                print(f"✅ {filename}")
            else:
                print(f"❌ {filename} (отсутствует)")
        
        print(f"\n🔧 ПОДГОТОВКА:")
        print("-" * 40)
        print("1. Изучить FEATURES.md")
        print("2. Проверить PROJECT_STRUCTURE.md")
        print("3. Использовать bot_template.py")
        print("4. Обновить STATUS.md")
        
        if feature_name:
            print(f"\n📝 ДЛЯ ФУНКЦИИ '{feature_name}':")
            print("-" * 40)
            print(f"1. Создать: copy bot_template.py {feature_name}_bot.py")
            print(f"2. Обновить DAILY.md с планом")
            print(f"3. Проверить приоритеты в STATUS.md")
    
    def check_status(self):
        """Проверка общего статуса"""
        print("📊 СТАТУС ПРОЕКТА")
        print("=" * 50)
        
        print(f"📁 ФАЙЛЫ ПРОЕКТА:")
        print("-" * 40)
        
        all_files = list(self.context_files.values())
        existing_files = []
        missing_files = []
        
        for filename in all_files:
            if self.check_file_exists(filename):
                existing_files.append(filename)
            else:
                missing_files.append(filename)
        
        print(f"✅ Существующие ({len(existing_files)}):")
        for filename in existing_files:
            print(f"   - {filename}")
        
        if missing_files:
            print(f"❌ Отсутствующие ({len(missing_files)}):")
            for filename in missing_files:
                print(f"   - {filename}")
        
        print(f"\n🔍 СИСТЕМНЫЕ ПРОВЕРКИ:")
        print("-" * 40)
        
        python_count = self.check_python_processes()
        missing_vars = self.check_env_vars()
        
        print(f"Python процессов: {python_count}")
        print(f"Отсутствующих переменных: {len(missing_vars)}")
        
        if python_count > 0:
            print("⚠️  Рекомендация: taskkill /F /IM python.exe")
        
        if missing_vars:
            print(f"⚠️  Рекомендация: проверить {', '.join(missing_vars)}")
        
        print(f"\n📋 РЕКОМЕНДАЦИИ:")
        print("-" * 40)
        if missing_files:
            print("1. Создать отсутствующие файлы")
        if python_count > 0:
            print("2. Очистить процессы Python")
        if missing_vars:
            print("3. Настроить переменные окружения")
        print("4. Обновить DAILY.md")

def main():
    parser = argparse.ArgumentParser(description='Умный менеджер контекста проекта')
    parser.add_argument('--morning', action='store_true', help='Утренняя рутина')
    parser.add_argument('--problem', type=str, help='Решение проблемы (event_loop, telegram, notion, yandex, bot, env)')
    parser.add_argument('--new-feature', type=str, nargs='?', const='', help='Новая функция')
    parser.add_argument('--check', action='store_true', help='Проверка статуса')
    
    args = parser.parse_args()
    
    manager = ContextManager()
    
    if args.morning:
        manager.morning_routine()
    elif args.problem:
        manager.problem_solver(args.problem)
    elif args.new_feature is not None:
        manager.new_feature(args.new_feature)
    elif args.check:
        manager.check_status()
    else:
        print("🤖 УМНЫЙ МЕНЕДЖЕР КОНТЕКСТА")
        print("=" * 50)
        print("Доступные команды:")
        print("  --morning     - Утренняя рутина")
        print("  --problem X   - Решение проблемы (event_loop, telegram, notion, yandex, bot, env)")
        print("  --new-feature - Новая функция")
        print("  --check       - Проверка статуса")
        print("\nПримеры:")
        print("  python context_manager.py --morning")
        print("  python context_manager.py --problem event_loop")
        print("  python context_manager.py --new-feature queue")

if __name__ == "__main__":
    main() 