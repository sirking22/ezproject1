#!/usr/bin/env python3
"""
Быстрое исправление HTTP запросов в оставшихся файлах
"""

import re
import os

def fix_file_quick(file_path: str):
    """Быстрое исправление файла"""
    print(f"🔧 Быстрое исправление {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"⚠️  Файл {file_path} не найден")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем импорт logging если нет
    if 'import logging' not in content:
        content = content.replace(
            'import requests',
            'import requests\nimport logging\n\nlogger = logging.getLogger(__name__)'
        )
    
    # Исправляем HTTP запросы
    patterns = [
        # requests.get без обработки ошибок
        (r'response\s*=\s*requests\.get\(([^)]+)\)', 
         r'try:\n        response = requests.get(\1)\n        response.raise_for_status()\n    except requests.RequestException as e:\n        logger.error(f"Error in GET request: {{e}}")\n        return None\n    \n    response'),
        
        # requests.post без обработки ошибок
        (r'response\s*=\s*requests\.post\(([^)]+)\)',
         r'try:\n        response = requests.post(\1)\n        response.raise_for_status()\n    except requests.RequestException as e:\n        logger.error(f"Error in POST request: {{e}}")\n        return None\n    \n    response'),
        
        # requests.patch без обработки ошибок
        (r'response\s*=\s*requests\.patch\(([^)]+)\)',
         r'try:\n        response = requests.patch(\1)\n        response.raise_for_status()\n    except requests.RequestException as e:\n        logger.error(f"Error in PATCH request: {{e}}")\n        return None\n    \n    response'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Убираем проверки status_code == 200
    content = re.sub(r'if response\.status_code == 200:', '', content)
    content = re.sub(r'else:\s*\n\s*print\(f"❌ Ошибка: \{response\.status_code\}"\)\s*\n\s*return None', '', content)
    content = re.sub(r'else:\s*\n\s*print\(f"❌ Ошибка: \{response\.status_code\}"\)\s*\n\s*return \{\}', '', content)
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {file_path} исправлен")

def main():
    """Основная функция"""
    print("🚀 БЫСТРОЕ ИСПРАВЛЕНИЕ HTTP ЗАПРОСОВ")
    print("=" * 50)
    
    files_to_fix = [
        'link_guides_to_templates.py',
        'kpi_migration_full.py',
        'kpi_simple_migration.py',
        'fix_kpi_relations.py',
        'fix_kpi_api.py',
        'dual_level_analytics.py',
        'daily_telegram_monitor.py'
    ]
    
    for file_path in files_to_fix:
        fix_file_quick(file_path)
    
    print("\n✅ Все файлы исправлены!")

if __name__ == "__main__":
    main() 