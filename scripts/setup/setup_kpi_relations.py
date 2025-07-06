#!/usr/bin/env python3
"""
Настройка связей KPI с RDT и TASKS для автоматизации метрик
"""

import os
import requests
import json
import logging
from typing import Dict, Any
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
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"
TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"

def analyze_kpi_structure():
    """Анализирует структуру KPI базы"""
    print("🔍 Анализ структуры KPI базы...")
    
    try:
        response = requests.get(f"{NOTION_BASE_URL}/databases/{KPI_DB}", headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {e}")
        return None
    
    data = response.json()
    properties = data.get('properties', {})
    
    print(f"📊 KPI база содержит {len(properties)} полей:")
    
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get('type')
        print(f"  • {prop_name}: {prop_type}")
        
        if prop_type == 'relation':
            target_db = prop_data.get('relation', {}).get('database_id')
            print(f"    → связь с: {target_db}")
    
    return properties

def analyze_rdt_structure():
    """Анализирует структуру RDT базы"""
    print("\n🔍 Анализ структуры RDT базы...")
    
    try:
        response = requests.get(f"{NOTION_BASE_URL}/databases/{RDT_DB}", headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {e}")
        return None
    
    data = response.json()
    properties = data.get('properties', {})
    
    print(f"📊 RDT база содержит {len(properties)} полей:")
    
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get('type')
        print(f"  • {prop_name}: {prop_type}")
        
        if prop_type == 'relation':
            target_db = prop_data.get('relation', {}).get('database_id')
            print(f"    → связь с: {target_db}")
    
    return properties

def get_sample_records(db_id, db_name, limit=3):
    """Получает примеры записей из базы"""
    print(f"\n📋 Получение примеров из {db_name}...")
    
    response = requests.post(
        f"{NOTION_BASE_URL}/databases/{db_id}/query",
        headers=HEADERS,
        json={"page_size": limit}
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print(f"📝 Найдено {len(results)} записей:")
        
        for i, record in enumerate(results, 1):
            properties = record.get('properties', {})
            title = "Без названия"
            
            # Ищем заголовок
            for prop_name, prop_data in properties.items():
                if prop_data.get('type') == 'title':
                    title_list = prop_data.get('title', [])
                    if title_list:
                        title = title_list[0].get('plain_text', 'Без названия')
                    break
                    
            print(f"  {i}. {title}")
        
        return results
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return []

def create_optimization_plan(kpi_props, rdt_props, rdt_kpi_fields):
    """Создает план оптимизации KPI"""
    print("\n🎯 ПЛАН ОПТИМИЗАЦИИ KPI:")
    print("=" * 50)
    
    plan = {
        "immediate_actions": [],
        "relations_to_create": [],
        "formulas_to_update": [],
        "new_properties": []
    }
    
    # Анализ текущих связей
    print("📊 ТЕКУЩИЕ СВЯЗИ:")
    for prop_name, prop_data in kpi_props.items():
        if prop_data.get('type') == 'relation':
            target_db = prop_data.get('relation', {}).get('database_id')
            print(f"  • {prop_name} → {target_db}")
            
            if target_db == RDT_DB:
                plan["immediate_actions"].append(f"✅ Связь с RDT уже есть: {prop_name}")
            elif target_db == TASKS_DB:
                plan["immediate_actions"].append(f"✅ Связь с TASKS уже есть: {prop_name}")
    
    # Проверяем нужные связи
    if not any(prop.get('relation', {}).get('database_id') == RDT_DB for prop in kpi_props.values()):
        plan["relations_to_create"].append("🔗 Создать связь KPI ↔ RDT")
        
    if not any(prop.get('relation', {}).get('database_id') == TASKS_DB for prop in kpi_props.values()):
        plan["relations_to_create"].append("🔗 Создать связь KPI ↔ TASKS")
    
    # RDT KPI поля для интеграции
    print(f"\n📈 RDT KPI ПОЛЯ ДЛЯ ИНТЕГРАЦИИ:")
    for field in rdt_kpi_fields:
        print(f"  • {field}")
        plan["formulas_to_update"].append(f"📊 Интегрировать {field} в KPI базу")
    
    # Новые метрики
    plan["new_properties"].extend([
        "📊 Количество правок (авто-подсчет)",
        "⏰ Срок выполнения (план vs факт)", 
        "🎯 Эффективность по типам задач",
        "📈 Среднее время по шаблонам"
    ])
    
    return plan

def main():
    print("🚀 НАСТРОЙКА KPI RELATIONS")
    print("=" * 40)
    
    # Анализируем базы
    kpi_props = analyze_kpi_structure()
    rdt_props, rdt_kpi_fields = analyze_rdt_structure()
    
    if not kpi_props or not rdt_props:
        print("❌ Не удалось получить структуру баз")
        return
    
    # Получаем примеры записей
    kpi_records = get_sample_records(KPI_DB, "KPI")
    rdt_records = get_sample_records(RDT_DB, "RDT") 
    tasks_records = get_sample_records(TASKS_DB, "TASKS")
    
    # Создаем план
    plan = create_optimization_plan(kpi_props, rdt_props, rdt_kpi_fields)
    
    # Выводим план
    print("\n🎯 ПЛАН ДЕЙСТВИЙ:")
    print("-" * 30)
    
    if plan["immediate_actions"]:
        print("\n✅ ГОТОВО:")
        for action in plan["immediate_actions"]:
            print(f"  {action}")
    
    if plan["relations_to_create"]:
        print("\n🔗 СОЗДАТЬ СВЯЗИ:")
        for relation in plan["relations_to_create"]:
            print(f"  {relation}")
    
    if plan["formulas_to_update"]:
        print("\n📊 ОБНОВИТЬ ФОРМУЛЫ:")
        for formula in plan["formulas_to_update"]:
            print(f"  {formula}")
    
    if plan["new_properties"]:
        print("\n➕ ДОБАВИТЬ СВОЙСТВА:")
        for prop in plan["new_properties"]:
            print(f"  {prop}")
    
    # Сохраняем план
    with open("kpi_optimization_plan.json", 'w', encoding='utf-8') as f:
        json.dump({
            "kpi_structure": kpi_props,
            "rdt_structure": rdt_props, 
            "rdt_kpi_fields": rdt_kpi_fields,
            "optimization_plan": plan,
            "next_steps": [
                "1. Создать недостающие relations",
                "2. Настроить автоподсчет метрик",
                "3. Интегрировать RDT KPI в основную базу",
                "4. Создать формулы для новых метрик"
            ]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 План сохранен в: kpi_optimization_plan.json")
    print("\n🚀 ГОТОВО! Можно приступать к настройке.")

if __name__ == "__main__":
    main() 