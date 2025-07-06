#!/usr/bin/env python3
"""
🎯 ПОЛНАЯ МИГРАЦИЯ KPI + ПОЛИГРАФИЯ
Переносит формулы RDT → KPI + создает полиграфические шаблоны
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)
import json
from datetime import datetime

# API настройки
NOTION_TOKEN = os.getenv('NOTION_TOKEN', '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')
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json", 
    "Notion-Version": "2022-06-28"
}

# ID баз данных (БЕЗ ДЕФИСОВ!)
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"
TASKS_DB = "9c5f4269d61449b6a7485579a3c21da3"
TEMPLATES_DB = "7bb1a2fc7dfa43a88b581b7a09b5a123"

def check_database_access():
    """Проверяет доступ к базам данных"""
    print("🔍 Проверка доступа к базам...")
    
    databases = {
        "KPI": KPI_DB,
        "RDT": RDT_DB, 
        "TASKS": TASKS_DB,
        "TEMPLATES": TEMPLATES_DB
    }
    
    accessible = {}
    for name, db_id in databases.items():
        try:
            url = f"https://api.notion.com/v1/databases/{db_id}"
            try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
            
            
                data = response.json()
                title = data.get('title', [{}])[0].get('plain_text', 'Untitled')
                print(f"✅ {name}: {title}")
                accessible[name] = True
            else:
                print(f"❌ {name}: {response.status_code}")
                accessible[name] = False
        except Exception as e:
            print(f"❌ {name}: {e}")
            accessible[name] = False
    
    return accessible

def create_kpi_connection_to_tasks():
    """Создает связь KPI ↔ TASKS"""
    print("🔗 Создание связи KPI ↔ TASKS...")
    
    # Добавляем поле TASKS в KPI базу
    kpi_property = {
        "Задачи": {
            "type": "relation",
            "relation": {
                "database_id": TASKS_DB,
                "type": "dual_property",
                "dual_property": {}
            }
        }
    }
    
    url = f"https://api.notion.com/v1/databases/{KPI_DB}/properties"
    
    try:
        try:
        response = requests.patch(url, headers=HEADERS, json={
            "properties": kpi_property
        })
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
        
        
            print("✅ Связь KPI ↔ TASKS создана")
            return True
        else:
            print(f"❌ Ошибка связи: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Исключение связи: {e}")
        return False

def create_kpi_formula_properties():
    """Создает KPI формулы на основе RDT"""
    print("📊 Создание KPI формул...")
    
    properties = {
        # КПИ ФОРМУЛЫ (упрощенные для работы)
        "Процент в срок": {
            "type": "formula",
            "formula": {
                "expression": "if(prop(\"Задачи\").length() > 0, round((prop(\"Задачи\").filter(current.prop(\"В срок\") == true).length() / prop(\"Задачи\").length()) * 100, 1), 0)"
            }
        },
        
        "Процент без правок": {
            "type": "formula", 
            "formula": {
                "expression": "if(prop(\"Задачи\").length() > 0, round((prop(\"Задачи\").filter(current.prop(\"Без правок\") == true).length() / prop(\"Задачи\").length()) * 100, 1), 0)"
            }
        },

        "Количество задач": {
            "type": "formula",
            "formula": {
                "expression": "prop(\"Задачи\").length()"
            }
        },

        "Время всего": {
            "type": "formula", 
            "formula": {
                "expression": "round(prop(\"Задачи\").map(current.prop(\"Потрачено времени\")).sum() * 10) / 10"
            }
        },

        # СТРУКТУРНЫЕ ПОЛЯ
        "Объект KPI": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Сотрудник", "color": "blue"},
                    {"name": "Команда", "color": "green"}, 
                    {"name": "Проект", "color": "purple"},
                    {"name": "Задача", "color": "orange"},
                    {"name": "Шаблон", "color": "yellow"}
                ]
            }
        },
        
        "Категория": {
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
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ KPI исключение {prop_name}: {e}")
    
    return success_count, len(properties)

def create_templates_properties():
    """Добавляет поля для работы с шаблонами"""
    print("📋 Создание полей шаблонов...")
    
    # Поля для TASKS базы
    tasks_properties = {
        "Тип шаблона": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Полиграфия", "color": "red"},
                    {"name": "Дизайн", "color": "blue"},
                    {"name": "Контент", "color": "green"},
                    {"name": "Техническое", "color": "purple"},
                    {"name": "Универсальное", "color": "gray"}
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
        
        "Среднее время": {
            "type": "number",
            "number": {"format": "number"}
        },
        
        "Связь с шаблоном": {
            "type": "relation",
            "relation": {
                "database_id": TEMPLATES_DB,
                "type": "dual_property",
                "dual_property": {}
            }
        }
    }
    
    url = f"https://api.notion.com/v1/databases/{TASKS_DB}/properties"
    
    success = 0
    for prop_name, config in tasks_properties.items():
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
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ TASKS исключение {prop_name}: {e}")
    
    return success

def create_polygraphy_templates():
    """Создает полиграфические шаблоны в TEMPLATES базе"""
    print("🎨 Создание полиграфических шаблонов...")
    
    templates = [
        {"name": "Листовка A4", "type": "Полиграфия", "complexity": "Простая", "time": 2, "desc": "Стандартная листовка формата A4"},
        {"name": "Листовка A5", "type": "Полиграфия", "complexity": "Простая", "time": 1.5, "desc": "Компактная листовка формата A5"},
        {"name": "Флаер", "type": "Полиграфия", "complexity": "Простая", "time": 2, "desc": "Рекламный флаер для распространения"},
        {"name": "Буклет 2-fold", "type": "Полиграфия", "complexity": "Средняя", "time": 4, "desc": "Буклет с одним сгибом"},
        {"name": "Буклет 3-fold", "type": "Полиграфия", "complexity": "Средняя", "time": 5, "desc": "Буклет с двумя сгибами"},
        {"name": "Визитки", "type": "Полиграфия", "complexity": "Простая", "time": 1, "desc": "Стандартные визитные карточки"},
        {"name": "Баннер стандартный", "type": "Полиграфия", "complexity": "Средняя", "time": 3, "desc": "Баннер для наружной рекламы"},
        {"name": "Каталог", "type": "Полиграфия", "complexity": "Сложная", "time": 8, "desc": "Многостраничный каталог продукции"},
        {"name": "Упаковка", "type": "Полиграфия", "complexity": "Сложная", "time": 6, "desc": "Дизайн упаковки товара"}
    ]
    
    url = f"https://api.notion.com/v1/pages"
    
    created = 0
    for template in templates:
        try:
            page_data = {
                "parent": {"database_id": TEMPLATES_DB},
                "properties": {
                    "Name": {"title": [{"text": {"content": template["name"]}}]},
                    "Описание": {"rich_text": [{"text": {"content": template["desc"]}}]},
                    "Категория": {"select": {"name": template["type"]}},
                    "Сложность": {"select": {"name": template["complexity"]}},
                    "Примерное время": {"number": template["time"]}
                }
            }
            
            try:
        response = requests.post(url, headers=HEADERS, json=page_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
            
            
                print(f"✅ Шаблон: {template['name']}")
                created += 1
            else:
                print(f"❌ Шаблон ошибка {template['name']}: {response.status_code}")
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ Шаблон исключение {template['name']}: {e}")
    
    return created

def create_sample_kpi_record():
    """Создает пример KPI записи"""
    print("📊 Создание примера KPI записи...")
    
    try:
        page_data = {
            "parent": {"database_id": KPI_DB},
            "properties": {
                "Name": {"title": [{"text": {"content": f"% задач в срок - Команда - {datetime.now().strftime('%B %Y')}"}}]},
                "Объект KPI": {"select": {"name": "Команда"}},
                "Категория": {"select": {"name": "Сроки"}},
                "Целевое значение": {"rich_text": [{"text": {"content": "85"}}]},
                "Автоподсчет": {"checkbox": True},
                "Дата периода": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
            }
        }
        
        url = f"https://api.notion.com/v1/pages"
        try:
        response = requests.post(url, headers=HEADERS, json=page_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
        
        
            print("✅ Пример KPI записи создан")
            return True
        else:
            print(f"❌ Ошибка KPI записи: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Исключение KPI записи: {e}")
        return False

def main():
    print("🚀 ПОЛНАЯ МИГРАЦИЯ KPI + ПОЛИГРАФИЯ")
    print("=" * 50)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ПРОВЕРКА ДОСТУПА К БАЗАМ
    accessible = check_database_access()
    
    if not all(accessible.values()):
        print("\n❌ НЕ ВСЕ БАЗЫ ДОСТУПНЫ")
        print("🔧 Проверьте ID баз и права доступа")
        return 0
    
    total_success = 0
    
    # ЭТАП 1: Связь KPI ↔ TASKS  
    print("\n🔗 ЭТАП 1: Создание связей...")
    if create_kpi_connection_to_tasks():
        total_success += 1
    
    # ЭТАП 2: KPI формулы
    print("\n📊 ЭТАП 2: KPI формулы...")
    kpi_success, kpi_total = create_kpi_formula_properties()
    print(f"   Создано: {kpi_success}/{kpi_total}")
    total_success += min(kpi_success, 5)  # Ограничиваем для подсчета
    
    # ЭТАП 3: Поля шаблонов
    print("\n📋 ЭТАП 3: Поля шаблонов...")
    templates_fields = create_templates_properties()
    print(f"   Создано: {templates_fields}/4")
    total_success += templates_fields
    
    # ЭТАП 4: Полиграфия
    print("\n🎨 ЭТАП 4: Полиграфические шаблоны...")
    polygraphy_created = create_polygraphy_templates()
    print(f"   Создано: {polygraphy_created}/9")
    total_success += min(polygraphy_created, 5)  # Ограничиваем для подсчета
    
    # ЭТАП 5: Пример KPI
    print("\n📊 ЭТАП 5: Пример KPI записи...")
    if create_sample_kpi_record():
        total_success += 1
    
    # РЕЗУЛЬТАТ
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ Успешных операций: {total_success}")
    print(f"📊 KPI база обновлена с формулами")
    print(f"🎨 Полиграфические шаблоны созданы")
    print(f"🔗 Связи между базами настроены")
    
    if total_success >= 10:
        print("\n🎉 МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("\n📋 ЧТО ГОТОВО:")
        print("✅ KPI формулы в центральной базе")
        print("✅ Полиграфические шаблоны созданы")
        print("✅ Связи TASKS ↔ KPI настроены")
        print("✅ Структура для автоподсчета готова")
        
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Создать KPI записи для каждого сотрудника")
        print("2. Настроить автоприкрепление шаблонов к задачам")
        print("3. Создать дашборд полиграфии")
        print("4. Начать отслеживать метрики")
    else:
        print(f"\n⚠️ Частичная миграция: {total_success} операций")
        print("🔧 Проверьте права доступа к базам")
    
    return total_success

if __name__ == "__main__":
    main() 