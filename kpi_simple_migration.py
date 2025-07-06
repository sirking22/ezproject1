#!/usr/bin/env python3
"""
🎯 УПРОЩЕННАЯ МИГРАЦИЯ KPI
Работает только с доступными базами: TASKS, KPI, RDT
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

# РАБОЧИЕ ID БАЗ
TASKS_DB = "9c5f4269d61449b6a7485579a3c21da3"
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"

def create_kpi_properties():
    """Создает только основные KPI поля"""
    print("📊 Создание KPI полей...")
    
    properties = {
        # ПРОСТЫЕ ФОРМУЛЫ (без сложных rollup)
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
                    {"name": "Провалено", "color": "red"},
                    {"name": "Приостановлено", "color": "gray"}
                ]
            }
        },
        
        "Достижение %": {
            "type": "formula",
            "formula": {
                "expression": "if(toNumber(prop(\"Целевое значение\")) > 0, round((prop(\"Факт (результат)\") / toNumber(prop(\"Целевое значение\"))) * 100, 1), 0)"
            }
        }
    }
    
    url = f"https://api.notion.com/v1/databases/{KPI_DB}/properties"
    
    success_count = 0
    for prop_name, prop_config in properties.items():
        try:
            try:
        response = requests.patch(url, headers=HEADERS, json={
                "properties": {prop_name: prop_config}
            })
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
            
            
                print(f"✅ KPI поле: {prop_name}")
                success_count += 1
            else:
                print(f"❌ KPI ошибка {prop_name}: {response.status_code}")
        except Exception as e:
            print(f"❌ KPI исключение {prop_name}: {e}")
    
    return success_count

def create_tasks_template_fields():
    """Добавляет поля для шаблонов в TASKS"""
    print("📋 Создание полей шаблонов в TASKS...")
    
    properties = {
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
        
        "Сложность работы": {
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
    
    url = f"https://api.notion.com/v1/databases/{TASKS_DB}/properties"
    
    success = 0
    for prop_name, config in properties.items():
        try:
            try:
        response = requests.patch(url, headers=HEADERS, json={
                "properties": {prop_name: config}
            })
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
            
            
                print(f"✅ TASKS поле: {prop_name}")
                success += 1
            else:
                print(f"❌ TASKS ошибка {prop_name}: {response.status_code}")
        except Exception as e:
            print(f"❌ TASKS исключение {prop_name}: {e}")
    
    return success

def create_sample_kpi_records():
    """Создает примеры KPI записей"""
    print("📊 Создание примеров KPI записей...")
    
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
        },
        {
            "name": "Объем полиграфии - Проект - Декабрь 2024",
            "object": "Проект", 
            "category": "Объем",
            "target": "50",
            "auto": False
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
            
            
                print(f"✅ KPI запись: {record['name'][:30]}...")
                created += 1
            else:
                print(f"❌ KPI запись ошибка: {response.status_code}")
        except Exception as e:
            print(f"❌ KPI запись исключение: {e}")
    
    return created

def main():
    print("🚀 УПРОЩЕННАЯ МИГРАЦИЯ KPI")
    print("=" * 40)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_operations = 0
    
    # ЭТАП 1: KPI поля
    print("\n📊 ЭТАП 1: KPI поля...")
    kpi_fields = create_kpi_properties()
    total_operations += kpi_fields
    print(f"   Создано: {kpi_fields}/5")
    
    # ЭТАП 2: TASKS поля
    print("\n📋 ЭТАП 2: TASKS поля...")
    tasks_fields = create_tasks_template_fields()
    total_operations += tasks_fields
    print(f"   Создано: {tasks_fields}/3")
    
    # ЭТАП 3: Примеры KPI
    print("\n📊 ЭТАП 3: Примеры KPI...")
    kpi_records = create_sample_kpi_records()
    total_operations += kpi_records
    print(f"   Создано: {kpi_records}/3")
    
    # РЕЗУЛЬТАТ
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ Успешных операций: {total_operations}")
    
    if total_operations >= 8:
        print("\n🎉 УПРОЩЕННАЯ МИГРАЦИЯ ЗАВЕРШЕНА!")
        print("\n📋 ЧТО ГОТОВО:")
        print("✅ KPI база структурирована")
        print("✅ TASKS готова для шаблонов")
        print("✅ Примеры KPI записей созданы")
        
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Создать связь KPI ↔ TASKS")
        print("2. Добавить полиграфические задачи")
        print("3. Настроить автоподсчет метрик")
        print("4. Создать dashboard")
    else:
        print(f"\n⚠️ Частичная миграция: {total_operations} операций")
    
    return total_operations

if __name__ == "__main__":
    main() 