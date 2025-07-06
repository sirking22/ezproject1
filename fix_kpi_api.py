#!/usr/bin/env python3
"""
✅ ПРАВИЛЬНЫЙ API ДЛЯ KPI
Использует корректный endpoint для обновления базы
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)
import json
from datetime import datetime

NOTION_TOKEN = os.getenv('NOTION_TOKEN', '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')
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json", 
    "Notion-Version": "2022-06-28"
}

KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
TASKS_DB = "9c5f4269d61449b6a7485579a3c21da3"

def update_kpi_database():
    """ПРАВИЛЬНОЕ обновление KPI базы"""
    print("✅ ОБНОВЛЕНИЕ KPI БАЗЫ (правильный API)")
    print("=" * 40)
    
    # ПРАВИЛЬНЫЙ URL - обновление всей базы
    url = f"https://api.notion.com/v1/databases/{KPI_DB}"
    
    # Новые свойства
    new_properties = {
        "Объект KPI": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Сотрудник", "color": "blue"},
                    {"name": "Команда", "color": "green"}, 
                    {"name": "Проект", "color": "purple"},
                    {"name": "Задача", "color": "orange"}
                ]
            }
        },
        
        "Категория метрики": {
            "type": "select", 
            "select": {
                "options": [
                    {"name": "Сроки", "color": "red"},
                    {"name": "Качество", "color": "green"},
                    {"name": "Объем", "color": "blue"},
                    {"name": "Эффективность", "color": "yellow"}
                ]
            }
        },
        
        "Автоподсчет": {
            "type": "checkbox",
            "checkbox": {}
        },
        
        "Статус KPI": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Достигнуто", "color": "green"},
                    {"name": "В процессе", "color": "blue"},
                    {"name": "Провалено", "color": "red"}
                ]
            }
        },
        
        "Достижение процент": {
            "type": "formula",
            "formula": {
                "expression": "if(toNumber(prop(\"Целевое значение\")) > 0, round((prop(\"Факт (результат)\") / toNumber(prop(\"Целевое значение\"))) * 100, 1), 0)"
            }
        }
    }
    
    # Данные для обновления
    update_data = {
        "properties": new_properties
    }
    
    try:
        print(f"📍 URL: {url}")
        print(f"📦 Добавляем {len(new_properties)} новых полей...")
        
        try:
        response = requests.patch(url, headers=HEADERS, json=update_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
        
        print(f"📊 Статус: {response.status_code}")
        
        
            print("✅ KPI база успешно обновлена!")
            data = response.json()
            properties = data.get('properties', {})
            print(f"📋 Всего полей в базе: {len(properties)}")
            
            print("\n🆕 НОВЫЕ ПОЛЯ:")
            for prop_name in new_properties.keys():
                if prop_name in properties:
                    print(f"  ✅ {prop_name}")
                else:
                    print(f"  ❌ {prop_name}")
            
            return True
        else:
            print(f"❌ Ошибка обновления: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def update_tasks_database():
    """Обновление TASKS базы"""
    print("\n📋 ОБНОВЛЕНИЕ TASKS БАЗЫ")
    print("=" * 30)
    
    url = f"https://api.notion.com/v1/databases/{TASKS_DB}"
    
    new_properties = {
        "Тип работы": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Полиграфия", "color": "red"},
                    {"name": "Дизайн", "color": "blue"},
                    {"name": "Контент", "color": "green"},
                    {"name": "Техническое", "color": "purple"}
                ]
            }
        },
        
        "Сложность": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Простая", "color": "green"},
                    {"name": "Средняя", "color": "yellow"},
                    {"name": "Сложная", "color": "red"}
                ]
            }
        },
        
        "Планируемое время": {
            "type": "number",
            "number": {"format": "number"}
        }
    }
    
    update_data = {
        "properties": new_properties
    }
    
    try:
        try:
        response = requests.patch(url, headers=HEADERS, json=update_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
        
        print(f"📊 Статус: {response.status_code}")
        
        
            print("✅ TASKS база успешно обновлена!")
            print(f"📋 Добавлено {len(new_properties)} полей")
            return True
        else:
            print(f"❌ Ошибка TASKS: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TASKS исключение: {e}")
        return False

def create_sample_kpi_records():
    """Создание примеров KPI записей"""
    print("\n📊 СОЗДАНИЕ KPI ЗАПИСЕЙ")
    print("=" * 25)
    
    sample_records = [
        {
            "name": "% задач в срок - Команда - Декабрь 2024",
            "object": "Команда",
            "category": "Сроки",
            "target": "85",
            "auto": True
        },
        {
            "name": "Качество дизайна - Команда - Декабрь 2024", 
            "object": "Команда",
            "category": "Качество",
            "target": "4.5",
            "auto": True
        }
    ]
    
    url = f"https://api.notion.com/v1/pages"
    created = 0
    
    for record in sample_records:
        try:
            page_data = {
                "parent": {"database_id": KPI_DB},
                "properties": {
                    "Name": {"title": [{"text": {"content": record["name"]}}]},
                    "Объект KPI": {"select": {"name": record["object"]}},
                    "Категория метрики": {"select": {"name": record["category"]}},
                    "Целевое значение": {"rich_text": [{"text": {"content": record["target"]}}]},
                    "Автоподсчет": {"checkbox": record["auto"]},
                    "Дата периода": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
                }
            }
            
            try:
        response = requests.post(url, headers=HEADERS, json=page_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
            
            
                print(f"✅ KPI запись: {record['name'][:40]}...")
                created += 1
            else:
                print(f"❌ KPI запись ошибка: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
        except Exception as e:
            print(f"❌ KPI запись исключение: {e}")
    
    return created

def main():
    print("🚀 ПРАВИЛЬНАЯ МИГРАЦИЯ KPI")
    print("=" * 40)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    
    # ЭТАП 1: Обновление KPI базы
    if update_kpi_database():
        success_count += 1
        print("✅ Этап 1 завершен")
    else:
        print("❌ Этап 1 провален")
    
    # ЭТАП 2: Обновление TASKS базы
    if update_tasks_database():
        success_count += 1
        print("✅ Этап 2 завершен")
    else:
        print("❌ Этап 2 провален")
    
    # ЭТАП 3: Создание записей (только если базы обновлены)
    if success_count >= 2:
        created = create_sample_kpi_records()
        if created > 0:
            success_count += 1
            print(f"✅ Этап 3 завершен: {created} записей")
    
    # РЕЗУЛЬТАТ
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ Завершенных этапов: {success_count}/3")
    
    if success_count >= 2:
        print("\n🎉 ОСНОВНАЯ МИГРАЦИЯ ЗАВЕРШЕНА!")
        print("\n📋 ЧТО ГОТОВО:")
        print("✅ KPI база структурирована с новыми полями")
        print("✅ TASKS база готова для шаблонов")
        print("✅ Можно создавать KPI записи")
        
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Создать полиграфические задачи")
        print("2. Настроить связь KPI ↔ TASKS")
        print("3. Создать дашборд метрик")
    else:
        print(f"\n⚠️ Миграция не завершена: {success_count} этапов")
    
    return success_count

if __name__ == "__main__":
    main() 