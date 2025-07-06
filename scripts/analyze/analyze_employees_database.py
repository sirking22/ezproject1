#!/usr/bin/env python3
"""
Детальный анализ базы сотрудников
"""

import os
import json
import requests
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_employees_db():
    """Анализ базы сотрудников"""
    notion_token = os.getenv("NOTION_TOKEN")
    teams_db_id = os.getenv("NOTION_TEAMS_DB_ID")
    
    if not notion_token or not teams_db_id:
        raise ValueError("NOTION_TOKEN и NOTION_TEAMS_DB_ID должны быть установлены")
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Получаем схему базы
    schema_url = f"https://api.notion.com/v1/databases/{teams_db_id}"
    schema_response = requests.get(schema_url, headers=headers)
    schema_response.raise_for_status()
    schema = schema_response.json()
    
    print("🔍 СХЕМА БАЗЫ СОТРУДНИКОВ:")
    print(f"ID: {teams_db_id}")
    print(f"Название: {schema.get('title', [{}])[0].get('plain_text', 'Без названия')}")
    print("\n📋 ПОЛЯ:")
    
    for field_name, field_props in schema['properties'].items():
        field_type = field_props.get('type', 'unknown')
        print(f"  - {field_name} ({field_type})")
        
        # Детали для select полей
        if field_type == 'select':
            options = field_props.get('select', {}).get('options', [])
            if options:
                print(f"    Варианты: {[opt.get('name') for opt in options]}")
    
    # Получаем всех сотрудников
    query_url = f"https://api.notion.com/v1/databases/{teams_db_id}/query"
    all_employees = []
    has_more = True
    start_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor
            
        response = requests.post(query_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        all_employees.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
    
    print(f"\n👥 ВСЕГО СОТРУДНИКОВ: {len(all_employees)}")
    print("\n📊 ДЕТАЛЬНЫЙ АНАЛИЗ:")
    
    for i, employee in enumerate(all_employees, 1):
        props = employee.get("properties", {})
        
        # Извлекаем данные
        name = extract_title(props, "Name") or "Без имени"
        description = extract_rich_text(props, "Описание") or "Нет описания"
        rdt = extract_select(props, "RDT") or "Не указан"
        leader = extract_select(props, "Руководитель") or "Не указан"
        kpi1 = extract_number(props, "KPI 1") or 0
        on_time = extract_checkbox(props, "В срок") or False
        no_revisions = extract_checkbox(props, "Без правок") or False
        
        print(f"\n{i}. {name}")
        print(f"   Описание: {description[:100]}...")
        print(f"   RDT: {rdt}")
        print(f"   Руководитель: {leader}")
        print(f"   KPI 1: {kpi1}")
        print(f"   В срок: {'✅' if on_time else '❌'}")
        print(f"   Без правок: {'✅' if no_revisions else '❌'}")
        print(f"   ID: {employee['id']}")
    
    return all_employees

def extract_title(props: Dict, field_name: str) -> str:
    """Извлечь title поле"""
    if field_name in props and props[field_name].get("type") == "title":
        title_array = props[field_name].get("title", [])
        if title_array:
            return title_array[0].get("plain_text", "")
    return ""

def extract_rich_text(props: Dict, field_name: str) -> str:
    """Извлечь rich_text поле"""
    if field_name in props and props[field_name].get("type") == "rich_text":
        rich_text_array = props[field_name].get("rich_text", [])
        if rich_text_array:
            return rich_text_array[0].get("plain_text", "")
    return ""

def extract_select(props: Dict, field_name: str) -> str:
    """Извлечь select поле"""
    if field_name in props and props[field_name].get("type") == "select":
        select_obj = props[field_name].get("select")
        if select_obj:
            return select_obj.get("name", "")
    return ""

def extract_number(props: Dict, field_name: str) -> float:
    """Извлечь number поле"""
    if field_name in props and props[field_name].get("type") == "number":
        return props[field_name].get("number", 0)
    return 0

def extract_checkbox(props: Dict, field_name: str) -> bool:
    """Извлечь checkbox поле"""
    if field_name in props and props[field_name].get("type") == "checkbox":
        return props[field_name].get("checkbox", False)
    return False

if __name__ == "__main__":
    try:
        employees = analyze_employees_db()
        print(f"\n✅ Анализ завершен. Найдено {len(employees)} сотрудников.")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise 