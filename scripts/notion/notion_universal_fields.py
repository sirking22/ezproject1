#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ДОБАВЛЕНИЕ УНИВЕРСАЛЬНЫХ ПОЛЕЙ В NOTION ДАШБОРД

Добавляет ключевые поля для всех социальных платформ:
✅ Engagement Rate, Growth Rate, Platform Rank
✅ Content Score, vs Industry
✅ Алерты и рекомендации
"""

import requests
import os
import json
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

class NotionUniversalFields:
    """Класс для добавления универсальных полей в Notion"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.platforms_db_id = os.getenv('NOTION_PLATFORMS_DB_ID')
        
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
    
    def add_universal_fields(self):
        """Добавляет универсальные поля в базу данных платформ"""
        
        print("🔧 ДОБАВЛЕНИЕ УНИВЕРСАЛЬНЫХ ПОЛЕЙ В NOTION")
        print("=" * 60)
        
        # Поля для добавления
        fields_to_add = {
            "Engagement Rate": {
                "number": {
                    "format": "percent"
                }
            },
            "Growth Rate": {
                "number": {
                    "format": "percent"
                }
            },
            "Platform Rank": {
                "select": {
                    "options": [
                        {"name": "Excellent", "color": "green"},
                        {"name": "High", "color": "blue"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"}
                    ]
                }
            },
            "Content Score": {
                "number": {
                    "format": "number"
                }
            },
            "vs Industry": {
                "number": {
                    "format": "percent"
                }
            },
            "Reach Rate": {
                "number": {
                    "format": "percent"
                }
            },
            "Posts per Week": {
                "number": {
                    "format": "number"
                }
            },
            "Alert Status": {
                "select": {
                    "options": [
                        {"name": "🚀 Excellent", "color": "green"},
                        {"name": "✅ Good", "color": "blue"},
                        {"name": "⚠️ Warning", "color": "yellow"},
                        {"name": "🚨 Critical", "color": "red"}
                    ]
                }
            },
            "Last Analytics": {
                "date": {}
            },
            "Next Action": {
                "rich_text": {}
            }
        }
        
        try:
            url = f"https://api.notion.so/v1/databases/{self.platforms_db_id}"
            
            # Получаем текущую структуру базы
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
                db_data = response.json()
                current_properties = db_data.get('properties', {})
                
                # Добавляем новые поля
                updated_properties = current_properties.copy()
                
                for field_name, field_config in fields_to_add.items():
                    if field_name not in current_properties:
                        updated_properties[field_name] = field_config
                        print(f"   ➕ Добавляю поле: {field_name}")
                    else:
                        print(f"   ✅ Поле уже существует: {field_name}")
                
                # Обновляем базу данных
                update_data = {
                    "properties": updated_properties
                }
                
                update_response = requests.patch(url, headers=self.headers, json=update_data)
                
                if update_response.status_code == 200:
                    print("\n✅ Поля успешно добавлены!")
                    self.show_field_descriptions()
                    return True
                else:
                    print(f"\n❌ Ошибка обновления: {update_response.status_code}")
                    print(update_response.text)
                    return False
            
        except requests.RequestException as e:
            logger.error(f"Error in GET request: {e}")
            return None
    
    def show_field_descriptions(self):
        """Показывает описание добавленных полей"""
        
        descriptions = """
📊 ОПИСАНИЕ УНИВЕРСАЛЬНЫХ ПОЛЕЙ:

🎯 ОСНОВНЫЕ KPI:
   • Engagement Rate - % взаимодействий (лайки + комментарии + шейры) / подписчики
   • Growth Rate - % рост подписчиков за месяц
   • Reach Rate - % охвата аудитории (просмотры / подписчики)

🏆 КАЧЕСТВЕННЫЕ ПОКАЗАТЕЛИ:
   • Platform Rank - Рейтинг платформы (Excellent/High/Medium/Low)
   • Content Score - Оценка качества контента (1-10)
   • vs Industry - % отклонение от индустриальных бенчмарков

📈 ОПЕРАЦИОННЫЕ МЕТРИКИ:
   • Posts per Week - Частота публикаций
   • Alert Status - Текущий статус алертов
   • Next Action - Рекомендуемые действия

⏰ ВРЕМЕННЫЕ МЕТРИКИ:
   • Last Analytics - Дата последнего анализа

ИСПОЛЬЗОВАНИЕ:
1. Запускать universal_social_metrics.py для автообновления
2. Алерты будут автоматически проставляться в Alert Status
3. Next Action будет содержать конкретные рекомендации
"""
        print(descriptions)

def main():
    """Главная функция"""
    
    print("🚀 НАСТРОЙКА УНИВЕРСАЛЬНЫХ ПОЛЕЙ В NOTION")
    print("=" * 60)
    
    notion_fields = NotionUniversalFields()
    
    success = notion_fields.add_universal_fields()
    
    if success:
        print("\n🎉 ГОТОВО! Теперь можно запускать universal_social_metrics.py")
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("   1. Проверить новые поля в Notion дашборде")
        print("   2. Запустить python universal_social_metrics.py")
        print("   3. Настроить автоматический запуск")
    else:
        print("\n❌ Что-то пошло не так. Проверьте токены и права доступа.")

if __name__ == "__main__":
    main() 