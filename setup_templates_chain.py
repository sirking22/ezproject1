#!/usr/bin/env python3
"""
Настройка цепочки TASKS_TEMPLATES → TASKS → GUIDES
Автоматическое прикрепление гайдов и расчет среднего времени
"""

import os
import requests
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# API настройки
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ID баз
TEMPLATES_DB = "1f2ace03d9ff806db364e869f27d83de"
TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"

def analyze_templates_structure():
    """Анализирует структуру типовых задач"""
    print("🔍 Анализ структуры TASKS_TEMPLATES...")
    
    try:
    response = requests.get(f"{NOTION_BASE_URL}/databases/{TEMPLATES_DB}", headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {e}")
        return None
    
        data = response.json()
        properties = data.get('properties', {})
        
        print(f"📊 TEMPLATES база содержит {len(properties)} полей:")
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type')
            print(f"  • {prop_name}: {prop_type}")
            
            if prop_type == 'relation':
                target_db = prop_data.get('relation', {}).get('database_id')
                print(f"    → связь с: {target_db}")
        
        return properties

def get_templates_records():
    """Получает все типовые задачи"""
    print("\n📋 Получение типовых задач...")
    
    try:
    response = requests.post(
        f"{NOTION_BASE_URL}/databases/{TEMPLATES_DB}/query",
        headers=HEADERS,
        json={"page_size": 100}
    )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {e}")
        return []
    
        data = response.json()
        results = data.get('results', [])
        
        templates = []
        print(f"📝 Найдено {len(results)} типовых задач:")
        
        for i, record in enumerate(results, 1):
            properties = record.get('properties', {})
            template_data = {"id": record.get('id')}
            
            # Извлекаем данные
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get('type')
                
                if prop_type == 'title':
                    title_list = prop_data.get('title', [])
                    if title_list:
                        template_data['title'] = title_list[0].get('plain_text', 'Без названия')
                elif prop_type == 'select':
                    select_data = prop_data.get('select')
                    if select_data:
                        template_data[prop_name] = select_data.get('name')
                elif prop_type == 'number':
                    template_data[prop_name] = prop_data.get('number')
                elif prop_type == 'relation':
                    relations = prop_data.get('relation', [])
                    template_data[prop_name] = [rel.get('id') for rel in relations]
            
            templates.append(template_data)
            title = template_data.get('title', 'Без названия')
            print(f"  {i}. {title}")
        
        return templates

def analyze_polygraphy_templates(templates):
    """Находит типовые задачи полиграфии"""
    print("\n🎨 Поиск задач полиграфии...")
    
    polygraphy_templates = []
    polygraphy_keywords = ['полиграф', 'печат', 'листовк', 'флаер', 'буклет', 'дизайн']
    
    for template in templates:
        title = template.get('title', '').lower()
        
        # Ищем по ключевым словам
        if any(keyword in title for keyword in polygraphy_keywords):
            polygraphy_templates.append(template)
            print(f"  🎯 НАЙДЕНО: {template.get('title')}")
        
        # Проверяем категории/теги
        for key, value in template.items():
            if isinstance(value, str) and any(keyword in value.lower() for keyword in polygraphy_keywords):
                if template not in polygraphy_templates:
                    polygraphy_templates.append(template)
                    print(f"  🎯 НАЙДЕНО (по категории): {template.get('title')}")
    
    print(f"\n📊 Всего найдено полиграфических шаблонов: {len(polygraphy_templates)}")
    return polygraphy_templates

def check_tasks_connection(templates):
    """Проверяет связь с обычными задачами"""
    print("\n🔗 Проверка связи с задачами...")
    
    # Получаем структуру TASKS
    try:
    response = requests.get(f"{NOTION_BASE_URL}/databases/{TASKS_DB}", headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {e}")
        return False
    
    data = response.json()
    properties = data.get('properties', {})
    
    # Ищем связь с templates
    template_relation = None
    for prop_name, prop_data in properties.items():
        if prop_data.get('type') == 'relation':
            target_db = prop_data.get('relation', {}).get('database_id')
            if target_db == TEMPLATES_DB:
                template_relation = prop_name
                print(f"✅ Найдена связь: {prop_name} → TEMPLATES")
                break
    
    if not template_relation:
        print("❌ Связь TASKS → TEMPLATES не найдена")
        return False
    
    # Проверяем есть ли задачи с шаблонами
    try:
    query_response = requests.post(
        f"{NOTION_BASE_URL}/databases/{TASKS_DB}/query",
        headers=HEADERS,
        json={
            "filter": {
                "property": template_relation,
                "relation": {
                    "is_not_empty": True
                }
            },
            "page_size": 5
        }
    )
        query_response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {e}")
        return False
    
        query_data = query_response.json()
        linked_tasks = len(query_data.get('results', []))
        print(f"📊 Задач с привязанными шаблонами: {linked_tasks}")
        return linked_tasks > 0

def create_template_optimization_plan(templates, polygraphy_templates, has_tasks_connection):
    """Создает план оптимизации шаблонов"""
    print("\n🎯 ПЛАН ОПТИМИЗАЦИИ ШАБЛОНОВ:")
    print("=" * 50)
    
    plan = {
        "current_status": {
            "total_templates": len(templates),
            "polygraphy_templates": len(polygraphy_templates), 
            "tasks_connection": has_tasks_connection
        },
        "immediate_actions": [],
        "polygraphy_focus": [],
        "guides_integration": [],
        "metrics_setup": []
    }
    
    # Статус связей
    if has_tasks_connection:
        plan["immediate_actions"].append("✅ Связь TASKS ↔ TEMPLATES работает")
    else:
        plan["immediate_actions"].append("❌ Нужно создать связь TASKS ↔ TEMPLATES")
    
    # Полиграфия фокус
    plan["polygraphy_focus"].extend([
        f"🎨 {len(polygraphy_templates)} полиграфических шаблонов найдено",
        "📋 Создать недостающие шаблоны полиграфии",
        "🔗 Связать все шаблоны с гайдами",
        "⏱️ Добавить поле 'Среднее время выполнения'"
    ])
    
    # Интеграция с гайдами
    plan["guides_integration"].extend([
        "📚 Создать связь TEMPLATES → GUIDES",
        "🤖 Автоприкрепление гайдов при создании задачи",
        "📖 Создать гайды для каждого типа полиграфии",
        "✅ Чеклисты в гайдах для контроля качества"
    ])
    
    # Настройка метрик
    plan["metrics_setup"].extend([
        "⏱️ Автоподсчет среднего времени по шаблону",
        "📊 Связь с KPI для отслеживания эффективности",
        "🎯 Метрики качества (количество правок)",
        "📈 Dashboard полиграфии для команды"
    ])
    
    return plan

def main():
    print("🚀 НАСТРОЙКА TEMPLATES CHAIN")
    print("=" * 40)
    
    # Анализируем структуру
    templates_props = analyze_templates_structure()
    if not templates_props:
        return
    
    # Получаем все шаблоны
    templates = get_templates_records()
    if not templates:
        return
    
    # Анализируем полиграфию
    polygraphy_templates = analyze_polygraphy_templates(templates)
    
    # Проверяем связь с задачами
    has_tasks_connection = check_tasks_connection(templates)
    
    # Создаем план
    plan = create_template_optimization_plan(templates, polygraphy_templates, has_tasks_connection)
    
    # Выводим план
    print("\n🎯 ПЛАН ДЕЙСТВИЙ:")
    print("-" * 30)
    
    print(f"\n📊 ТЕКУЩИЙ СТАТУС:")
    print(f"  • Всего шаблонов: {plan['current_status']['total_templates']}")
    print(f"  • Полиграфия: {plan['current_status']['polygraphy_templates']}")
    print(f"  • Связь с задачами: {'✅' if plan['current_status']['tasks_connection'] else '❌'}")
    
    print(f"\n🎨 ФОКУС НА ПОЛИГРАФИИ:")
    for action in plan["polygraphy_focus"]:
        print(f"  {action}")
    
    print(f"\n📚 ИНТЕГРАЦИЯ С ГАЙДАМИ:")
    for action in plan["guides_integration"]:
        print(f"  {action}")
    
    print(f"\n📊 НАСТРОЙКА МЕТРИК:")
    for action in plan["metrics_setup"]:
        print(f"  {action}")
    
    # Сохраняем план
    result_data = {
        "templates_structure": templates_props,
        "all_templates": templates,
        "polygraphy_templates": polygraphy_templates,
        "optimization_plan": plan,
        "next_steps": [
            "1. Создать недостающие связи",
            "2. Добавить полиграфические шаблоны", 
            "3. Связать шаблоны с гайдами",
            "4. Настроить автоподсчет метрик",
            "5. Создать dashboard полиграфии"
        ]
    }
    
    with open("templates_optimization_plan.json", 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 План сохранен в: templates_optimization_plan.json")
    print("\n🚀 ГОТОВО! Полиграфия - приоритет #1")

if __name__ == "__main__":
    main() 