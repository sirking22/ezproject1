#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ДВУХУРОВНЕВАЯ СИСТЕМА АНАЛИТИКИ СОЦСЕТЕЙ

УРОВЕНЬ 1: ПЛАТФОРМЫ (общая статистика)
УРОВЕНЬ 2: ПОСТЫ (детальная аналитика) 

Интеграция с существующими базами Notion
"""

import os
import asyncio
import aiohttp
import requests
import logging

logger = logging.getLogger(__name__)
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ===== БАЗЫ ДАННЫХ =====
PLATFORMS_DB = os.getenv('NOTION_PLATFORMS_DB_ID')
CONTENT_DB = os.getenv('NOTION_CONTENT_PLAN_DB_ID') 
NOTION_TOKEN = os.getenv('NOTION_TOKEN')

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

class DatabaseInspector:
    """Инспектор структуры баз данных Notion"""
    
    def __init__(self):
        if not NOTION_TOKEN:
            raise ValueError("❌ NOTION_TOKEN не найден в .env")
        if not PLATFORMS_DB:
            print("⚠️ NOTION_PLATFORMS_DB_ID не найден в .env")
        if not CONTENT_DB:
            print("⚠️ NOTION_CONTENT_PLAN_DB_ID не найден в .env")
    
    def inspect_database(self, db_id: str, db_name: str):
        """Инспектирует структуру базы данных"""
        
        if not db_id:
            print(f"❌ {db_name}: ID базы не найден")
            return None
        
        print(f"\n🔍 АНАЛИЗ БАЗЫ: {db_name}")
        print(f"📊 ID: {db_id}")
        print("=" * 60)
        
        try:
            # Получаем структуру базы
            try:
        response = requests.get(
                f"https://api.notion.com/v1/databases/{db_id}",
                headers=HEADERS
            )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
            
            if response.status_code != 200:
                print(f"❌ Ошибка доступа: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None
            
            db_data = response.json()
            
            # Основная информация
            title = db_data.get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            print(f"📝 Название: {title}")
            
            # Анализируем свойства
            properties = db_data.get('properties', {})
            print(f"🔧 Полей: {len(properties)}")
            print()
            
            print("📋 СТРУКТУРА ПОЛЕЙ:")
            for field_name, field_info in properties.items():
                field_type = field_info.get('type', 'unknown')
                
                print(f"   • {field_name} ({field_type})")
                
                # Дополнительная информация для select полей
                if field_type == 'select' and 'select' in field_info:
                    options = field_info['select'].get('options', [])
                    if options:
                        option_names = [opt.get('name', '') for opt in options]
                        print(f"     Варианты: {', '.join(option_names[:3])}{'...' if len(option_names) > 3 else ''}")
                
                # Дополнительная информация для multi_select полей
                elif field_type == 'multi_select' and 'multi_select' in field_info:
                    options = field_info['multi_select'].get('options', [])
                    if options:
                        option_names = [opt.get('name', '') for opt in options]
                        print(f"     Варианты: {', '.join(option_names[:3])}{'...' if len(option_names) > 3 else ''}")
            
            # Получаем примеры записей
            print(f"\n📄 ПРИМЕРЫ ЗАПИСЕЙ:")
            
            query_try:
        response = requests.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=HEADERS,
                json={"page_size": 3}
            )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
            
            if query_response.status_code == 200:
                records = query_response.json().get('results', [])
                print(f"Найдено записей: {len(records)}")
                
                for i, record in enumerate(records, 1):
                    print(f"\n   {i}. Запись:")
                    props = record.get('properties', {})
                    
                    # Показываем значения ключевых полей
                    for field_name, field_data in props.items():
                        if field_name in ['Название', 'Name', 'title', 'Заголовок']:
                            if field_data.get('type') == 'title':
                                title_content = field_data.get('title', [{}])[0].get('text', {}).get('content', '')
                                if title_content:
                                    print(f"      📝 {field_name}: {title_content}")
                        
                        elif field_data.get('type') == 'select':
                            select_value = field_data.get('select', {})
                            if select_value:
                                print(f"      🔹 {field_name}: {select_value.get('name', '')}")
                        
                        elif field_data.get('type') == 'multi_select':
                            multi_values = field_data.get('multi_select', [])
                            if multi_values:
                                names = [v.get('name', '') for v in multi_values]
                                print(f"      🔸 {field_name}: {', '.join(names)}")
                        
                        elif field_data.get('type') == 'number':
                            number_value = field_data.get('number')
                            if number_value is not None:
                                print(f"      🔢 {field_name}: {number_value}")
            
            else:
                print(f"❌ Ошибка получения записей: {query_response.status_code}")
            
            return db_data
            
        except Exception as e:
            print(f"❌ Ошибка анализа базы: {e}")
            return None
    
    def analyze_both_databases(self):
        """Анализирует обе базы данных"""
        
        print("🚀 АНАЛИЗ СУЩЕСТВУЮЩИХ БАЗ ДАННЫХ")
        print("🎯 Подготовка к автоматическому сбору статистики")
        print("=" * 80)
        
        # Анализируем базу платформ
        platforms_data = self.inspect_database(PLATFORMS_DB, "ПЛАТФОРМЫ")
        
        # Анализируем базу контента
        content_data = self.inspect_database(CONTENT_DB, "КОНТЕНТ-ПЛАН")
        
        # Генерируем рекомендации
        print(f"\n\n🎯 РЕКОМЕНДАЦИИ ДЛЯ АВТОМАТИЗАЦИИ:")
        print("=" * 60)
        
        self.generate_recommendations(platforms_data, content_data)
        
        return platforms_data, content_data
    
    def generate_recommendations(self, platforms_data, content_data):
        """Генерирует рекомендации по оптимизации"""
        
        if platforms_data:
            print("📊 БАЗА ПЛАТФОРМ:")
            platform_props = platforms_data.get('properties', {})
            
            # Проверяем нужные поля для автоматизации
            required_platform_fields = [
                'Подписчики', 'Охват', 'Engagement Rate', 'Дата обновления'
            ]
            
            missing_fields = []
            for field in required_platform_fields:
                if not any(field.lower() in prop_name.lower() for prop_name in platform_props.keys()):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Отсутствуют поля: {', '.join(missing_fields)}")
                print("   💡 Рекомендуется добавить для автоматического сбора")
            else:
                print("   ✅ Структура готова к автоматизации")
        
        if content_data:
            print("\n📝 БАЗА КОНТЕНТА:")
            content_props = content_data.get('properties', {})
            
            # Проверяем нужные поля для постов
            required_content_fields = [
                'Просмотры', 'Лайки', 'Комментарии', 'Репосты', 'URL'
            ]
            
            missing_fields = []
            for field in required_content_fields:
                if not any(field.lower() in prop_name.lower() for prop_name in content_props.keys()):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Отсутствуют поля: {', '.join(missing_fields)}")
                print("   💡 Рекомендуется добавить для детальной аналитики")
            else:
                print("   ✅ Структура готова к автоматизации")
        
        print(f"\n🔧 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Добавить недостающие поля в базы")
        print("2. Настроить API ключи социальных сетей")  
        print("3. Запустить автоматический сбор данных")

class SocialMediaAnalytics:
    """Основной класс для сбора аналитики соцсетей"""
    
    def __init__(self):
        self.platforms_db = PLATFORMS_DB
        self.content_db = CONTENT_DB
        
        # API токены
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.instagram_account = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        self.youtube_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube_channel = os.getenv('YOUTUBE_CHANNEL_ID')
        self.telegram_bot = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel = os.getenv('TELEGRAM_CHANNEL_ID')
        self.vk_token = os.getenv('VK_ACCESS_TOKEN')
        self.vk_group = os.getenv('VK_GROUP_ID')
    
    def check_api_setup(self):
        """Проверяет настройку API ключей"""
        
        print("\n🔑 ПРОВЕРКА API КЛЮЧЕЙ:")
        print("=" * 40)
        
        apis = {
            'Instagram': (self.instagram_token, self.instagram_account),
            'YouTube': (self.youtube_key, self.youtube_channel),
            'Telegram': (self.telegram_bot, self.telegram_channel),
            'VK': (self.vk_token, self.vk_group)
        }
        
        for platform, (token, account) in apis.items():
            if token and account:
                print(f"✅ {platform}: Настроен")
            elif token:
                print(f"⚠️ {platform}: Токен есть, но нет ID аккаунта/канала")
            else:
                print(f"❌ {platform}: Не настроен")
        
        return apis
    
    async def collect_instagram_data(self):
        """Собирает данные Instagram"""
        
        if not self.instagram_token or not self.instagram_account:
            return {"error": "Instagram API не настроен"}
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.instagram_account}"
            params = {
                'fields': 'followers_count,media_count,name,username',
                'access_token': self.instagram_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'platform': 'Instagram',
                            'followers': data.get('followers_count', 0),
                            'content_count': data.get('media_count', 0),
                            'name': data.get('name', ''),
                            'username': data.get('username', '')
                        }
                    else:
                        return {"error": f"Instagram API error: {response.status}"}
        except Exception as e:
            return {"error": f"Instagram error: {e}"}
    
    async def test_all_integrations(self):
        """Тестирует все интеграции"""
        
        print("\n🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИЙ:")
        print("=" * 50)
        
        # Тестируем Instagram
        instagram_result = await self.collect_instagram_data()
        if 'error' in instagram_result:
            print(f"❌ Instagram: {instagram_result['error']}")
        else:
            print(f"✅ Instagram: @{instagram_result['username']} - {instagram_result['followers']:,} подписчиков")
        
        # TODO: Добавить тесты других платформ
        
        return {
            'instagram': instagram_result
        }

def main():
    """Главная функция для анализа и тестирования"""
    
    print("🎯 ДВУХУРОВНЕВАЯ АНАЛИТИКА СОЦСЕТЕЙ")
    print("📊 Анализ существующих баз данных Notion")
    print()
    
    # Инспектируем базы данных
    inspector = DatabaseInspector()
    platforms_data, content_data = inspector.analyze_both_databases()
    
    # Проверяем API интеграции
    analytics = SocialMediaAnalytics()
    apis_status = analytics.check_api_setup()
    
    # Тестируем подключения
    async def test_apis():
        return await analytics.test_all_integrations()
    
    print(f"\n🚀 Запуск тестирования API...")
    try:
        results = asyncio.run(test_apis())
        print(f"\n✅ Тестирование завершено!")
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
    
    print(f"\n📋 ИТОГИ АНАЛИЗА:")
    print("=" * 50)
    print("✅ Структура баз данных проанализирована")
    print("✅ API интеграции проверены")
    print("📊 Готовность к автоматизации оценена")
    print(f"\n🎯 Следующий шаг: Реализация автоматического сбора")

if __name__ == "__main__":
    main() 