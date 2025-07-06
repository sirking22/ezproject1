#!/usr/bin/env python3
"""
Связывание гайдов с шаблонами полиграфии
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)
import time

# API настройки
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Database IDs
GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"
TEMPLATES_DB = "1f2ace03d9ff806db364e869f27d83de"

# Связи гайдов с шаблонами (по названиям)
GUIDE_TEMPLATE_LINKS = {
    "🎨 Гайд: Листовка A4": ["Листовка A4"],
    "💳 Гайд: Визитки": ["Визитки"],
    "📄 Гайд: Флаер": ["Флаер"],
    "📑 Гайд: Буклет": ["Буклет"],
    "🖼️ Гайд: Баннер": ["Баннер"],
    "📦 Гайд: Упаковка": ["Упаковка"],
    "📖 Гайд: Каталог": ["Каталог"]
}

def get_database_pages(db_id, title_field="Name"):
    """Получает все страницы из базы данных"""
    
    try:
        pages = {}
        has_more = True
        start_cursor = None
        
        while has_more:
            query_params = {"page_size": 100}
            if start_cursor:
                query_params["start_cursor"] = start_cursor
            
            try:
        response = requests.post(
                f"{NOTION_BASE_URL}/databases/{db_id}/query", 
                headers=HEADERS, 
                json=query_params
            )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
            
            if response.status_code != 200:
                print(f"❌ Ошибка запроса: {response.status_code}")
                break
            
            data = response.json()
            
            for page in data["results"]:
                title_prop = page["properties"].get(title_field, {})
                
                if title_prop.get("type") == "title":
                    title_list = title_prop.get("title", [])
                    if title_list:
                        title = title_list[0].get("plain_text", "")
                        pages[title] = page["id"]
                        
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(0.1)  # Rate limiting
        
        return pages
        
    except Exception as e:
        print(f"❌ Ошибка получения страниц из базы {db_id}: {e}")
        return {}

def check_templates_guides_relation():
    """Проверяет наличие связи между TEMPLATES и GUIDES"""
    
    try:
        try:
        response = requests.get(f"{NOTION_BASE_URL}/databases/{TEMPLATES_DB}", headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
        
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к базе: {response.status_code}")
            return None
        
        db_info = response.json()
        properties = db_info.get('properties', {})
        
        # Ищем связь с GUIDES
        guides_relation = None
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'relation':
                target_db = prop_data.get('relation', {}).get('database_id')
                if target_db == GUIDES_DB:
                    guides_relation = prop_name
                    break
        
        if guides_relation:
            print(f"✅ Найдена связь TEMPLATES → GUIDES: {guides_relation}")
            return guides_relation
        else:
            print("❌ Связь TEMPLATES → GUIDES не найдена")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка проверки связи: {e}")
        return None

def create_templates_guides_relation():
    """Создает связь между TEMPLATES и GUIDES если её нет"""
    
    print("🔗 Создание связи TEMPLATES → GUIDES...")
    
    try:
        # Добавляем новое поле связи с гайдами
        new_property = {
            "Связанные гайды": {
                "type": "relation",
                "relation": {
                    "database_id": GUIDES_DB
                }
            }
        }
        
        # Обновляем базу
        try:
        response = requests.patch(
            f"{NOTION_BASE_URL}/databases/{TEMPLATES_DB}",
            headers=HEADERS,
            json={"properties": new_property}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
        
        
            print("✅ Связь TEMPLATES → GUIDES создана")
            return "Связанные гайды"
        else:
            print(f"❌ Ошибка создания связи: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"❌ Ошибка создания связи: {e}")
        return None

def link_guide_to_templates(guide_id, template_ids, relation_field):
    """Связывает гайд с шаблонами через relation поле"""
    
    try:
        success_count = 0
        
        for template_id in template_ids:
            try:
        response = requests.patch(
                f"{NOTION_BASE_URL}/pages/{template_id}",
                headers=HEADERS,
                json={
                    "properties": {
                        relation_field: {
                            "relation": [{"id": guide_id}]
                        }
                    }
                }
            )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
            
            
                success_count += 1
            
            time.sleep(0.1)  # Rate limiting
        
        return success_count
        
    except Exception as e:
        print(f"❌ Ошибка связывания: {e}")
        return 0

def link_all_guides_to_templates():
    """Связывает все гайды с соответствующими шаблонами"""
    
    print("🚀 СВЯЗЫВАНИЕ ГАЙДОВ С ШАБЛОНАМИ")
    print("=" * 60)
    
    # Проверяем связь между базами
    relation_field = check_templates_guides_relation()
    
    if not relation_field:
        relation_field = create_templates_guides_relation()
        
    if not relation_field:
        print("❌ Невозможно создать связь")
        return
    
    # Получаем все страницы из баз
    print("\n📊 Получение данных из баз...")
    guides_pages = get_database_pages(GUIDES_DB, "Name")
    templates_pages = get_database_pages(TEMPLATES_DB, "Name")
    
    print(f"   Найдено гайдов: {len(guides_pages)}")
    print(f"   Найдено шаблонов: {len(templates_pages)}")
    
    # Связываем гайды с шаблонами
    print(f"\n🔗 Создание связей:")
    total_links = 0
    
    for guide_name, template_names in GUIDE_TEMPLATE_LINKS.items():
        if guide_name in guides_pages:
            guide_id = guides_pages[guide_name]
            
            # Находим ID шаблонов
            template_ids = []
            for template_name in template_names:
                # Проверяем различные варианты названий
                found_template = None
                for existing_name in templates_pages.keys():
                    if template_name.lower() in existing_name.lower():
                        found_template = existing_name
                        break
                
                if found_template:
                    template_ids.append(templates_pages[found_template])
                else:
                    print(f"   ⚠️ Шаблон не найден: {template_name}")
            
            if template_ids:
                linked_count = link_guide_to_templates(guide_id, template_ids, relation_field)
                total_links += linked_count
                print(f"   ✅ {guide_name} → {len(template_ids)} шаблонов")
            else:
                print(f"   ❌ Нет шаблонов для: {guide_name}")
        else:
            print(f"   ❌ Гайд не найден: {guide_name}")
    
    print(f"\n📈 РЕЗУЛЬТАТ:")
    print(f"✅ Создано связей: {total_links}")
    
    if total_links > 0:
        print(f"\n🎉 АВТОПРИКРЕПЛЕНИЕ НАСТРОЕНО!")
        print(f"🔗 Ссылка на шаблоны: https://www.notion.so/{TEMPLATES_DB.replace('-', '')}")
        
        print(f"\n🎯 ТЕПЕРЬ ПРИ СОЗДАНИИ ЗАДАЧ:")
        print("1. Выбираешь шаблон полиграфии")
        print("2. Гайд автоматически прикрепляется")
        print("3. Все технические требования под рукой")
        print("4. Чеклисты для проверки качества")
    else:
        print(f"\n⚠️ Связи не созданы")

def create_dashboard_view():
    """Инструкции для создания dashboard полиграфии"""
    
    print(f"\n📊 DASHBOARD ПОЛИГРАФИИ")
    print("=" * 40)
    
    print(f"🎯 В базе TEMPLATES создать представления:")
    print(f"https://www.notion.so/{TEMPLATES_DB.replace('-', '')}")
    
    print(f"\n1. 📋 'Полиграфия Dashboard':")
    print("   - Фильтр: Название содержит полиграфию")
    print("   - Группировка: по типу шаблона")
    print("   - Показывать связанные гайды")
    
    print(f"\n2. 📊 'Метрики полиграфии':")
    print("   - Самые используемые шаблоны")
    print("   - Среднее время выполнения")
    print("   - Связь с KPI системой")

if __name__ == "__main__":
    # Связываем гайды с шаблонами
    link_all_guides_to_templates()
    
    # Показываем инструкции для dashboard
    create_dashboard_view() 