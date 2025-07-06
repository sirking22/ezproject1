#!/usr/bin/env python3
"""
Исправленный скрипт для создания relations в KPI базе
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)
import json

# API настройки
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Базы данных
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"

def create_relation_property(property_name, target_db_id):
    """Создает relation property в KPI базе"""
    
    # Исправленный URL и формат данных
    url = f"{NOTION_BASE_URL}/databases/{KPI_DB}"
    
    # Получаем текущую структуру
    get_try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
    if get_response.status_code != 200:
        print(f"❌ Не удалось получить структуру KPI базы: {get_response.status_code}")
        return False
    
    current_data = get_response.json()
    current_properties = current_data.get('properties', {})
    
    # Добавляем новое свойство
    new_property = {
        "type": "relation",
        "relation": {
            "database_id": target_db_id
        }
    }
    
    # Обновляем базу
    update_data = {
        "properties": {
            **current_properties,
            property_name: new_property
        }
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=update_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
    
    
        print(f"✅ Создана связь: {property_name} → {target_db_id}")
        return True
    else:
        print(f"❌ Ошибка создания {property_name}: {response.status_code}")
        print(f"   Ответ: {response.text[:300]}")
        return False

def test_basic_access():
    """Тестирует базовый доступ к KPI базе"""
    print("🔍 Тестирование доступа к KPI базе...")
    
    url = f"{NOTION_BASE_URL}/databases/{KPI_DB}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
    
    
        data = response.json()
        properties_count = len(data.get('properties', {}))
        print(f"✅ Доступ к KPI базе: {properties_count} полей")
        return True
    else:
        print(f"❌ Нет доступа к KPI базе: {response.status_code}")
        print(f"   Ответ: {response.text}")
        return False

def main():
    print("🚀 ИСПРАВЛЕННОЕ СОЗДАНИЕ KPI RELATIONS")
    print("=" * 50)
    
    # Тестируем доступ
    if not test_basic_access():
        return
    
    # Новые связи для создания (по одной)
    relations_to_create = {
        "Связанные задачи": "d09df250ce7e4e0d9fbe4e036d320def",
        "Связанные проекты": "342f18c67a5e41fead73dcec00770f4e", 
        "Связанные эпики": "6fc4322e6d0c45a6b37ac49b818a063a"
    }
    
    success_count = 0
    
    print("\n🔗 Создание связей (по одной):")
    for name, db_id in relations_to_create.items():
        print(f"\n⏳ Создаю: {name}...")
        if create_relation_property(name, db_id):
            success_count += 1
        else:
            # Попробуем без дефисов в ID
            clean_id = db_id.replace("-", "")
            print(f"   🔄 Пробую без дефисов: {clean_id}")
            if create_relation_property(name, clean_id):
                success_count += 1
    
    print(f"\n📈 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ Успешно создано: {success_count}/{len(relations_to_create)}")
    
    if success_count > 0:
        print("\n🎉 ПРОГРЕСС ЕСТЬ!")
        print("✅ Некоторые связи созданы")
        
        # Показываем следующие шаги
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Создать тестовые KPI записи")
        print("2. Настроить rollup из RDT")
        print("3. Добавить формулы расчета")
        
    else:
        print("\n⚠️ Связи не созданы")
        print("🔧 Возможные причины:")
        print("   • Нет прав на изменение базы")
        print("   • Неверные ID баз")
        print("   • Ограничения Notion API")

if __name__ == "__main__":
    main() 