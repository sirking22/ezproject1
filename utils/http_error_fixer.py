#!/usr/bin/env python3
"""
Утилита для исправления HTTP запросов без обработки ошибок
Автоматически добавляет try-catch блоки к requests.get/post
"""

import re
import os
from typing import List, Tuple

def find_unsafe_requests(file_path: str) -> List[Tuple[int, str]]:
    """Находит небезопасные HTTP запросы в файле"""
    unsafe_patterns = [
        r'response\s*=\s*requests\.get\([^)]*\)',
        r'response\s*=\s*requests\.post\([^)]*\)',
        r'response\s*=\s*requests\.put\([^)]*\)',
        r'response\s*=\s*requests\.delete\([^)]*\)'
    ]
    
    unsafe_lines = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines, 1):
        for pattern in unsafe_patterns:
            if re.search(pattern, line.strip()):
                # Проверяем, есть ли уже try-catch
                if not _has_try_catch_context(lines, i-1):
                    unsafe_lines.append((i, line.strip()))
                break
    
    return unsafe_lines

def _has_try_catch_context(lines: List[str], line_index: int) -> bool:
    """Проверяет, есть ли try-catch контекст вокруг строки"""
    # Ищем try выше
    try_found = False
    for i in range(line_index, -1, -1):
        if 'try:' in lines[i]:
            try_found = True
            break
        elif lines[i].strip() and not lines[i].strip().startswith('#'):
            break
    
    if not try_found:
        return False
    
    # Ищем except ниже
    for i in range(line_index, len(lines)):
        if 'except' in lines[i]:
            return True
        elif lines[i].strip() and not lines[i].strip().startswith('#'):
            break
    
    return False

def generate_safe_request_code(original_line: str) -> str:
    """Генерирует безопасный код для HTTP запроса"""
    # Извлекаем параметры запроса
    match = re.search(r'requests\.(\w+)\(([^)]*)\)', original_line)
    if not match:
        return original_line
    
    method = match.group(1)
    params = match.group(2)
    
    # Определяем переменную для response
    var_match = re.search(r'(\w+)\s*=\s*requests\.', original_line)
    var_name = var_match.group(1) if var_match else 'response'
    
    safe_code = f"""try:
    {var_name} = requests.{method}({params})
    {var_name}.raise_for_status()
    return {var_name}.json()
except requests.RequestException as e:
    logger.error(f"Error in {method.upper()} request: {{e}}")
    raise"""
    
    return safe_code

def fix_file(file_path: str) -> bool:
    """Исправляет файл, добавляя обработку ошибок"""
    print(f"🔧 Исправляю {file_path}...")
    
    unsafe_lines = find_unsafe_requests(file_path)
    if not unsafe_lines:
        print(f"✅ {file_path} - безопасен")
        return True
    
    print(f"⚠️  Найдено {len(unsafe_lines)} небезопасных запросов:")
    for line_num, line in unsafe_lines:
        print(f"   Строка {line_num}: {line}")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем импорт если нужно
    if 'import requests' in content and 'logger' not in content:
        content = content.replace(
            'import requests',
            'import requests\nimport logging\n\nlogger = logging.getLogger(__name__)'
        )
    
    # Показываем примеры исправлений
    print(f"\n📝 Примеры исправлений для {file_path}:")
    for line_num, line in unsafe_lines[:3]:  # Показываем первые 3
        safe_code = generate_safe_request_code(line)
        print(f"\nСтрока {line_num}:")
        print(f"❌ {line}")
        print(f"✅ {safe_code}")
    
    return False

def main():
    """Основная функция"""
    print("🚨 ПРОВЕРКА HTTP ЗАПРОСОВ НА БЕЗОПАСНОСТЬ")
    print("=" * 50)
    
    # Файлы для проверки
    files_to_check = [
        'universal_social_metrics.py',
        'telegram_analytics_framework.py',
        'setup_templates_chain.py',
        'setup_kpi_relations.py',
        'setup_business_chains.py',
        'optimize_existing_kpi.py',
        'notion_universal_fields.py',
        'notion_fields_setup.py',
        'link_guides_to_templates.py',
        'kpi_migration_full.py',
        'kpi_simple_migration.py',
        'fix_kpi_relations.py',
        'fix_kpi_api.py',
        'dual_level_analytics.py',
        'daily_telegram_monitor.py'
    ]
    
    unsafe_files = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if not fix_file(file_path):
                unsafe_files.append(file_path)
        else:
            print(f"⚠️  Файл {file_path} не найден")
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print(f"✅ Безопасных файлов: {len(files_to_check) - len(unsafe_files)}")
    print(f"❌ Файлов с ошибками: {len(unsafe_files)}")
    
    if unsafe_files:
        print(f"\n🚨 ФАЙЛЫ ТРЕБУЮТ ИСПРАВЛЕНИЯ:")
        for file_path in unsafe_files:
            print(f"   • {file_path}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("   1. Добавить try-catch блоки к HTTP запросам")
        print("   2. Использовать response.raise_for_status()")
        print("   3. Добавить логирование ошибок")
        print("   4. Использовать утилиту utils/console_helpers.safe_request()")

if __name__ == "__main__":
    main() 