#!/usr/bin/env python3
"""
Оптимизация существующих KPI связей через RDT
"""

import os
import requests
import json
from datetime import datetime

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
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"

def create_kpi_records_for_team():
    """Создает KPI записи для каждого сотрудника из RDT"""
    print("🎯 Создание KPI записей для команды...")
    
    # Получаем список сотрудников из RDT
    rdt_response = requests.post(
        f"{NOTION_BASE_URL}/databases/{RDT_DB}/query",
        headers=HEADERS,
        json={"page_size": 50}
    )
    
    if rdt_response.status_code != 200:
        print(f"❌ Не удалось получить сотрудников: {rdt_response.status_code}")
        return []
    
    rdt_data = rdt_response.json()
    employees = rdt_data.get('results', [])
    
    print(f"📋 Найдено {len(employees)} сотрудников в RDT")
    
    created_kpis = []
    current_month = datetime.now().strftime("%B %Y")
    
    # KPI шаблоны для создания
    kpi_templates = [
        {
            "name_template": "% задач в срок - {} - {}",
            "category": "Сроки",
            "target": "85"
        },
        {
            "name_template": "% задач без правок - {} - {}",
            "category": "Качество", 
            "target": "70"
        },
        {
            "name_template": "Качество работы - {} - {}",
            "category": "Качество",
            "target": "4.5"
        }
    ]
    
    # Создаем KPI для каждого сотрудника
    for employee in employees:
        employee_id = employee.get('id')
        employee_props = employee.get('properties', {})
        
        # Получаем имя сотрудника
        employee_name = "Без имени"
        for prop_name, prop_data in employee_props.items():
            if prop_data.get('type') == 'title':
                title_list = prop_data.get('title', [])
                if title_list:
                    employee_name = title_list[0].get('plain_text', 'Без имени')
                break
        
        print(f"\n👤 Создаю KPI для: {employee_name}")
        
        # Создаем KPI записи для сотрудника
        for template in kpi_templates:
            kpi_name = template["name_template"].format(employee_name, current_month)
            
            kpi_data = {
                "parent": {"database_id": KPI_DB},
                "properties": {
                    "Name": {
                        "title": [{"text": {"content": kpi_name}}]
                    },
                    "Целевое значение": {
                        "rich_text": [{"text": {"content": template["target"]}}]
                    },
                    "Тип контента / направление": {
                        "rich_text": [{"text": {"content": template["category"]}}]
                    },
                    "RDT": {
                        "relation": [{"id": employee_id}]
                    },
                    "Дата периода": {
                        "date": {"start": datetime.now().strftime("%Y-%m-01")}
                    },
                    "Комментарий": {
                        "rich_text": [{"text": {"content": f"Автоматически созданный KPI для {employee_name}"}}]
                    }
                }
            }
            
            # Создаем запись
            create_response = requests.post(
                f"{NOTION_BASE_URL}/pages",
                headers=HEADERS,
                json=kpi_data
            )
            
            if create_response.status_code == 200:
                print(f"  ✅ {template['category']}: {template['target']}")
                created_kpis.append(kpi_name)
            else:
                print(f"  ❌ Ошибка создания {template['category']}: {create_response.status_code}")
    
    return created_kpis

def test_kpi_rollup():
    """Тестирует работу rollup полей из RDT"""
    print("\n🔍 Тестирование rollup из RDT...")
    
    # Получаем KPI записи
    kpi_response = requests.post(
        f"{NOTION_BASE_URL}/databases/{KPI_DB}/query",
        headers=HEADERS,
        json={"page_size": 10}
    )
    
    if kpi_response.status_code != 200:
        print(f"❌ Не удалось получить KPI: {kpi_response.status_code}")
        return
    
    kpi_data = kpi_response.json()
    kpi_records = kpi_data.get('results', [])
    
    print(f"📊 Найдено {len(kpi_records)} KPI записей:")
    
    for i, record in enumerate(kpi_records[:5], 1):
        properties = record.get('properties', {})
        
        # Название KPI
        kpi_name = "Без названия"
        if 'Name' in properties:
            title_list = properties['Name'].get('title', [])
            if title_list:
                kpi_name = title_list[0].get('plain_text', 'Без названия')
        
        # Факт (результат)
        fact_value = "Не задано"
        if 'Факт (результат)' in properties:
            fact_number = properties['Факт (результат)'].get('number')
            if fact_number is not None:
                fact_value = str(fact_number)
        
        # Целевое значение
        target_value = "Не задано"
        if 'Целевое значение' in properties:
            target_list = properties['Целевое значение'].get('rich_text', [])
            if target_list:
                target_value = target_list[0].get('plain_text', 'Не задано')
        
        print(f"  {i}. {kpi_name}")
        print(f"     Цель: {target_value} | Факт: {fact_value}")

def main():
    print("🚀 ОПТИМИЗАЦИЯ СУЩЕСТВУЮЩИХ KPI")
    print("=" * 50)
    
    # Создаем KPI записи для команды
    created_kpis = create_kpi_records_for_team()
    
    print(f"\n📈 РЕЗУЛЬТАТ:")
    print(f"✅ Создано KPI записей: {len(created_kpis)}")
    
    if created_kpis:
        print("\n📋 Созданные KPI:")
        for kpi in created_kpis[:10]:  # Показываем первые 10
            print(f"  • {kpi}")
        
        if len(created_kpis) > 10:
            print(f"  ... и еще {len(created_kpis) - 10}")
    
    # Тестируем rollup
    test_kpi_rollup()
    
    print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Настроить формулы автоподсчета из RDT")
    print("2. Создать дашборд KPI")
    print("3. Обновить целевые значения")
    print("4. Настроить уведомления")

if __name__ == "__main__":
    main() 