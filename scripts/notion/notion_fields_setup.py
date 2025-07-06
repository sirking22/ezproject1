#!/usr/bin/env python3
"""
Автоматическое добавление полей в Notion базу данных
Добавляет все необходимые поля для аналитики социальных сетей
"""

import os
import json
import time
from typing import Dict, Any
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

load_dotenv()

class NotionFieldsManager:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.platforms_db_id = os.getenv("NOTION_PLATFORMS_DB_ID")
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
    def load_fields_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию полей из JSON"""
        with open("notion_fields_templates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_current_properties(self) -> Dict[str, Any]:
        """Получает текущие свойства базы данных"""
        url = f"https://api.notion.com/v1/databases/{self.platforms_db_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error in GET request: {e}")
            return {}
        
        return response.json().get("properties", {})
    
    def add_property(self, property_name: str, property_config: Dict[str, Any]) -> bool:
        """Добавляет одно свойство в базу данных"""
        url = f"https://api.notion.com/v1/databases/{self.platforms_db_id}"
        
        # Подготавливаем данные для обновления
        update_data = {
            "properties": {
                property_name: property_config
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json={})
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error in POST request: {e}")
            return False
        
        return True
    
    def setup_all_fields(self) -> None:
        """Добавляет все поля из конфигурации"""
        print("🚀 Начинаю настройку полей в Notion...")
        
        # Загружаем конфигурацию
        config = self.load_fields_config()
        fields_config = config["database_fields_config"]["fields"]
        
        # Получаем текущие свойства
        current_properties = self.get_current_properties()
        
        print(f"📊 Текущие поля в базе: {len(current_properties)}")
        print(f"🎯 Нужно добавить: {len(fields_config)} полей")
        
        success_count = 0
        skip_count = 0
        
        for field_name, field_config in fields_config.items():
            # Проверяем, существует ли поле
            if field_name in current_properties:
                print(f"⏭️  Поле '{field_name}' уже существует, пропускаю")
                skip_count += 1
                continue
            
            # Добавляем поле
            if self.add_property(field_name, field_config):
                success_count += 1
            
            # Небольшая задержка между запросами
            time.sleep(0.5)
        
        print(f"\n📈 ИТОГИ НАСТРОЙКИ:")
        print(f"✅ Добавлено полей: {success_count}")
        print(f"⏭️  Пропущено (уже существуют): {skip_count}")
        print(f"🎯 Всего полей в конфигурации: {len(fields_config)}")
        
    def fill_default_values(self) -> None:
        """Заполняет дефолтные значения для платформ"""
        print("\n🎯 Заполняю дефолтные значения...")
        
        config = self.load_fields_config()
        default_values = config["default_values"]["platforms"]
        
        # Получаем все записи платформ
        url = f"https://api.notion.com/v1/databases/{self.platforms_db_id}/query"
        response = requests.post(url, headers=self.headers, json={})
        
        if response.status_code != 200:
            print(f"❌ Ошибка получения записей: {response.status_code}")
            return
        
        platforms = response.json().get("results", [])
        
        for platform in platforms:
            platform_id = platform["id"]
            
            # Ищем название платформы
            platform_name = None
            if "Platforms" in platform["properties"]:
                title_prop = platform["properties"]["Platforms"]
                if title_prop["type"] == "title" and title_prop["title"]:
                    platform_name = title_prop["title"][0]["text"]["content"]
            
            if not platform_name or platform_name not in default_values:
                print(f"⏭️  Платформа '{platform_name}' не найдена в дефолтах")
                continue
            
            # Подготавливаем данные для обновления
            updates = {}
            defaults = default_values[platform_name]
            
            for field, value in defaults.items():
                if isinstance(value, (int, float)):
                    updates[field] = {"number": value}
                elif isinstance(value, str):
                    if field.endswith("Rate") or field == "vs Industry":
                        # Процентные поля
                        updates[field] = {"number": float(value) if value else 0}
                    else:
                        # Select поля
                        updates[field] = {"select": {"name": value}}
            
            # Обновляем запись
            update_url = f"https://api.notion.com/v1/pages/{platform_id}"
            update_data = {"properties": updates}
            
            response = requests.patch(update_url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                print(f"✅ Обновлены дефолты для '{platform_name}'")
            else:
                print(f"❌ Ошибка обновления '{platform_name}': {response.status_code}")
            
            time.sleep(0.5)
    
    def validate_setup(self) -> None:
        """Проверяет корректность настройки"""
        print("\n🔍 Проверяю настройку...")
        
        current_properties = self.get_current_properties()
        config = self.load_fields_config()
        expected_fields = config["database_fields_config"]["fields"]
        
        missing_fields = []
        for field_name in expected_fields:
            if field_name not in current_properties:
                missing_fields.append(field_name)
        
        if missing_fields:
            print(f"⚠️  Отсутствуют поля: {missing_fields}")
        else:
            print("✅ Все поля настроены корректно!")
        
        # Показываем типы полей
        formula_fields = []
        select_fields = []
        number_fields = []
        
        for field_name, field_data in current_properties.items():
            if field_data["type"] == "formula":
                formula_fields.append(field_name)
            elif field_data["type"] == "select":
                select_fields.append(field_name)
            elif field_data["type"] == "number":
                number_fields.append(field_name)
        
        print(f"\n📊 СТАТИСТИКА ПОЛЕЙ:")
        print(f"🔢 Number полей: {len(number_fields)}")
        print(f"📋 Select полей: {len(select_fields)}")
        print(f"⚡ Formula полей: {len(formula_fields)}")
        print(f"📅 Всего полей: {len(current_properties)}")

def main():
    """Основная функция"""
    print("🎯 НАСТРОЙКА NOTION ANALYTICS DASHBOARD")
    print("=" * 50)
    
    manager = NotionFieldsManager()
    
    try:
        # 1. Добавляем все поля
        manager.setup_all_fields()
        
        # 2. Заполняем дефолтные значения  
        manager.fill_default_values()
        
        # 3. Проверяем результат
        manager.validate_setup()
        
        print(f"\n🚀 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("Теперь твоя Notion база готова для автоматической аналитики!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 