#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 TELEGRAM ANALYTICS ТЕСТ

Получение статистики из Telegram без записи в Notion
Тестирование API и вывод данных в консоль
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class TelegramAnalytics:
    """Класс для работы с Telegram Analytics"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')  # Может быть пустым
        
        if not self.bot_token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def test_bot_connection(self):
        """Проверяет подключение к боту"""
        
        print("🤖 ТЕСТИРОВАНИЕ TELEGRAM BOT API")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/getMe")
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    bot_data = bot_info['result']
                    print(f"✅ Бот подключен успешно!")
                    print(f"📝 Имя: {bot_data.get('first_name', 'N/A')}")
                    print(f"🔗 Username: @{bot_data.get('username', 'N/A')}")
                    print(f"🆔 ID: {bot_data.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Ошибка API: {bot_info.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def get_chat_info(self, chat_id):
        """Получает информацию о чате/канале"""
        
        try:
            response = requests.get(f"{self.base_url}/getChat", 
                                  params={'chat_id': chat_id})
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    return result['result']
                else:
                    print(f"❌ Ошибка получения чата: {result.get('description', 'Unknown')}")
                    return None
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_chat_member_count(self, chat_id):
        """Получает количество участников чата"""
        
        try:
            response = requests.get(f"{self.base_url}/getChatMemberCount",
                                  params={'chat_id': chat_id})
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    return result['result']
                else:
                    print(f"❌ Ошибка получения участников: {result.get('description', 'Unknown')}")
                    return None
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_recent_messages(self, chat_id, limit=10):
        """Получает последние сообщения из чата"""
        
        # Примечание: Для получения сообщений бот должен быть админом канала
        # или канал должен быть публичным
        
        print(f"📬 Попытка получить последние {limit} сообщений...")
        
        # Метод getUpdates для получения обновлений
        try:
            response = requests.get(f"{self.base_url}/getUpdates",
                                  params={'limit': limit, 'timeout': 10})
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    updates = result['result']
                    print(f"📨 Получено обновлений: {len(updates)}")
                    
                    messages = []
                    for update in updates:
                        if 'message' in update:
                            messages.append(update['message'])
                        elif 'channel_post' in update:
                            messages.append(update['channel_post'])
                    
                    return messages
                else:
                    print(f"❌ Ошибка получения сообщений: {result.get('description', 'Unknown')}")
                    return []
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
    
    def analyze_channel_statistics(self):
        """Анализирует статистику канала"""
        
        print("\n📊 АНАЛИЗ TELEGRAM СТАТИСТИКИ")
        print("=" * 60)
        
        # Если есть ID канала - анализируем его
        if self.channel_id:
            print(f"🎯 Анализируем канал: {self.channel_id}")
            
            # Информация о канале
            chat_info = self.get_chat_info(self.channel_id)
            if chat_info:
                print(f"\n📋 ИНФОРМАЦИЯ О КАНАЛЕ:")
                print(f"   📝 Название: {chat_info.get('title', 'N/A')}")
                print(f"   📝 Описание: {chat_info.get('description', 'N/A')[:100]}...")
                print(f"   🔗 Username: @{chat_info.get('username', 'N/A')}")
                print(f"   📅 Тип: {chat_info.get('type', 'N/A')}")
            
            # Количество участников
            member_count = self.get_chat_member_count(self.channel_id)
            if member_count:
                print(f"\n👥 УЧАСТНИКИ: {member_count:,} человек")
            
            # Последние сообщения
            messages = self.get_recent_messages(self.channel_id)
            if messages:
                print(f"\n📨 ПОСЛЕДНИЕ СООБЩЕНИЯ:")
                for i, msg in enumerate(messages[:5], 1):
                    date = datetime.fromtimestamp(msg.get('date', 0))
                    text = msg.get('text', msg.get('caption', 'Медиа'))[:50]
                    views = msg.get('views', 'N/A')
                    print(f"   {i}. {date.strftime('%d.%m %H:%M')} | 👀 {views} | {text}...")
        
        else:
            print("⚠️ TELEGRAM_CHANNEL_ID не указан")
            print("💡 Для анализа конкретного канала добавьте в .env:")
            print("   TELEGRAM_CHANNEL_ID=@your_channel_username")
            print("   или TELEGRAM_CHANNEL_ID=-100123456789")
        
        # Получаем общие обновления
        print(f"\n📬 ПОЛУЧЕНИЕ ОБНОВЛЕНИЙ:")
        updates = self.get_recent_messages(None)
        if updates:
            print(f"✅ Получено {len(updates)} обновлений")
            
            # Группируем по типам
            channels = set()
            for msg in updates:
                chat = msg.get('chat', {})
                if chat.get('type') in ['channel', 'supergroup']:
                    channels.add(f"{chat.get('title', 'Unknown')} (@{chat.get('username', 'private')})")
            
            if channels:
                print(f"\n📺 НАЙДЕННЫЕ КАНАЛЫ:")
                for i, channel in enumerate(sorted(channels), 1):
                    print(f"   {i}. {channel}")
        
        return {
            'channel_info': chat_info if self.channel_id else None,
            'member_count': member_count if self.channel_id else None,
            'recent_messages': messages if self.channel_id else updates
        }
    
    def recommend_setup(self):
        """Рекомендации по настройке"""
        
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО НАСТРОЙКЕ:")
        print("=" * 50)
        
        print("1️⃣ Для анализа канала добавьте в .env:")
        print("   TELEGRAM_CHANNEL_ID=@your_channel_username")
        print("   или TELEGRAM_CHANNEL_ID=-100123456789")
        
        print("\n2️⃣ Чтобы бот мог читать сообщения:")
        print("   • Добавьте бота как админа канала")
        print("   • Или сделайте канал публичным")
        
        print("\n3️⃣ Для подробной аналитики:")
        print("   • Включите статистику в настройках канала")
        print("   • Используйте Telegram Analytics API (требует approval)")
        
        print("\n4️⃣ Альтернативные методы:")
        print("   • Экспорт статистики из Telegram Desktop")
        print("   • Интеграция с TelemetryDeck или подобными")

def main():
    """Главная функция тестирования"""
    
    print("📱 TELEGRAM ANALYTICS - ТЕСТИРОВАНИЕ")
    print("🎯 Проверка API и получение статистики")
    print("=" * 80)
    
    try:
        # Создаем экземпляр аналитики
        analytics = TelegramAnalytics()
        
        # Тестируем подключение
        if analytics.test_bot_connection():
            
            # Анализируем статистику
            results = analytics.analyze_channel_statistics()
            
            # Рекомендации
            analytics.recommend_setup()
            
            print(f"\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
            print("📊 Данные готовы для интеграции с Notion")
        
        else:
            print("❌ Ошибка подключения к Telegram Bot API")
            print("💡 Проверьте TELEGRAM_BOT_TOKEN в .env файле")
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 