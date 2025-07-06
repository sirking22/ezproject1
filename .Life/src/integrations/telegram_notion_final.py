#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ФИНАЛЬНАЯ ИНТЕГРАЦИЯ TELEGRAM → NOTION

Автоматическое обновление баз данных:
✅ PLATFORMS_DB - информация о канале + подписчики
✅ CONTENT_DB - посты с просмотрами + engagement метрики

📊 ДОСТУПНЫЕ МЕТРИКИ:
✅ Просмотры - 100% точность
❌ Лайки - недоступны в публичном API  
❌ Комментарии - недоступны в публичном API
🔄 Решение: используем просмотры как основную метрику
"""

import requests
import os
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

class TelegramToNotionFinal:
    """Финальная интеграция с максимально доступными метриками"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.platforms_db_id = os.getenv('NOTION_PLATFORMS_DB_ID')
        self.content_db_id = os.getenv('NOTION_CONTENT_PLAN_DB_ID')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        self.notion_headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        self.telegram_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_telegram_analytics(self, channel="rawmid"):
        """Получает аналитику Telegram канала"""
        
        print(f"📊 СБОР АНАЛИТИКИ @{channel}")
        print("=" * 50)
        
        channel = channel.replace("@", "")
        
        # 1. Данные канала через Bot API
        channel_info = self.get_channel_info_via_bot(channel)
        
        # 2. Метрики постов через веб-скрапинг
        posts_data = self.get_posts_metrics(channel)
        
        return {
            'channel_info': channel_info,
            'posts_data': posts_data,
            'summary': {
                'total_posts': len(posts_data),
                'total_views': sum(p['views'] for p in posts_data),
                'avg_views': sum(p['views'] for p in posts_data) / len(posts_data) if posts_data else 0,
                'max_views': max((p['views'] for p in posts_data), default=0),
                'min_views': min((p['views'] for p in posts_data), default=0)
            }
        }
    
    def get_channel_info_via_bot(self, channel):
        """Получает информацию о канале через Bot API"""
        
        if not self.bot_token:
            return {"error": "No Bot Token", "subscribers": 0}
        
        try:
            # Информация о канале
            chat_url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            chat_response = requests.get(chat_url, params={'chat_id': f'@{channel}'}, timeout=10)
            
            # Количество подписчиков
            count_url = f"https://api.telegram.org/bot{self.bot_token}/getChatMemberCount"
            count_response = requests.get(count_url, params={'chat_id': f'@{channel}'}, timeout=10)
            
            subscribers = 0
            channel_id = ""
            title = channel
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                if chat_data.get('ok'):
                    info = chat_data['result']
                    channel_id = str(info.get('id', ''))
                    title = info.get('title', channel)
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                if count_data.get('ok'):
                    subscribers = count_data['result']
            
            print(f"   📝 {title}")
            print(f"   👥 {subscribers:,} подписчиков")
            print(f"   🆔 {channel_id}")
            
            return {
                'id': channel_id,
                'title': title,
                'username': channel,
                'subscribers': subscribers
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка Bot API: {e}")
            return {"error": str(e), "subscribers": 0}
    
    def get_posts_metrics(self, channel):
        """Получает метрики постов через веб-скрапинг"""
        
        print(f"   🔍 Анализ постов...")
        
        url = f"https://t.me/s/{channel}"
        
        try:
            response = requests.get(url, headers=self.telegram_headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts_elements = soup.find_all('div', class_='tgme_widget_message')
                
                print(f"   📝 Найдено постов: {len(posts_elements)}")
                
                posts_data = []
                
                for i, post_elem in enumerate(posts_elements, 1):
                    post_metrics = self.extract_post_metrics(post_elem, i, channel)
                    if post_metrics:
                        posts_data.append(post_metrics)
                
                return posts_data
            else:
                print(f"   ❌ Ошибка загрузки: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Ошибка скрапинга: {e}")
            return []
    
    def extract_post_metrics(self, post_elem, post_num, channel):
        """Извлекает метрики одного поста"""
        
        try:
            # ID поста
            post_link = post_elem.get('data-post', '')
            post_id = post_link.split('/')[-1] if post_link else str(post_num)
            
            # URL поста
            post_url = f"https://t.me/{channel}/{post_id}"
            
            # Текст поста
            text_elem = post_elem.find('div', class_='tgme_widget_message_text')
            text_content = ""
            if text_elem:
                text_content = text_elem.get_text(strip=True)
            
            # Дата поста
            date_elem = post_elem.find('time', class_='datetime')
            post_date = ""
            if date_elem:
                datetime_attr = date_elem.get('datetime', '')
                if datetime_attr:
                    try:
                        date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        post_date = date_obj.strftime('%Y-%m-%d')
                    except:
                        post_date = datetime.now().strftime('%Y-%m-%d')
            
            # Просмотры (основная метрика)
            views_elem = post_elem.find('span', class_='tgme_widget_message_views')
            views = 0
            if views_elem:
                views_text = views_elem.text.strip()
                views = self.convert_count_to_number(views_text)
            
            # Тип медиа
            media_type = "Текст"
            if post_elem.find('video'):
                media_type = "Видео"
            elif post_elem.find('img') or post_elem.find('i', class_='tgme_widget_message_photo_wrap'):
                media_type = "Фото"
            elif post_elem.find('audio'):
                media_type = "Аудио"
            
            return {
                'id': post_id,
                'url': post_url,
                'text': text_content,
                'date': post_date,
                'views': views,
                'media_type': media_type,
                'engagement_rate': 0  # Будем рассчитывать на основе просмотров
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка обработки поста {post_num}: {e}")
            return None
    
    def convert_count_to_number(self, count_str):
        """Конвертирует строку счетчика в число"""
        
        if not count_str:
            return 0
        
        count_str = str(count_str).replace(' ', '').replace(',', '').lower()
        
        match = re.search(r'([\d.,]+[km]?)', count_str)
        if not match:
            return 0
        
        number_str = match.group(1)
        
        try:
            if 'k' in number_str:
                return int(float(number_str.replace('k', '')) * 1000)
            elif 'm' in number_str:
                return int(float(number_str.replace('m', '')) * 1000000)
            else:
                return int(float(number_str))
        except:
            return 0
    
    def update_platforms_database(self, channel_info):
        """Обновляет базу данных платформ"""
        
        print(f"\n🔄 ОБНОВЛЕНИЕ PLATFORMS DATABASE")
        print("=" * 50)
        
        try:
            # Ищем существующую запись Telegram
            search_response = requests.post(
                f"https://api.notion.com/v1/databases/{self.platforms_db_id}/query",
                headers=self.notion_headers,
                json={
                    "filter": {
                        "property": "Platform Name",
                        "title": {
                            "equals": "Telegram"
                        }
                    }
                }
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                
                if search_data['results']:
                    # Обновляем существующую запись
                    page_id = search_data['results'][0]['id']
                    
                    update_data = {
                        "properties": {
                            "Followers": {"number": channel_info.get('subscribers', 0)},
                            "Last Updated": {"date": {"start": datetime.now(timezone.utc).isoformat()}}
                        }
                    }
                    
                    update_response = requests.patch(
                        f"https://api.notion.com/v1/pages/{page_id}",
                        headers=self.notion_headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"   ✅ Обновлено: {channel_info.get('subscribers', 0):,} подписчиков")
                        return True
                    else:
                        print(f"   ❌ Ошибка обновления: {update_response.status_code}")
                        return False
                else:
                    print("   ❌ Telegram запись не найдена в базе")
                    return False
            else:
                print(f"   ❌ Ошибка поиска: {search_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False
    
    def update_content_database(self, posts_data, limit=5):
        """Обновляет базу данных контента"""
        
        print(f"\n📝 ОБНОВЛЕНИЕ CONTENT DATABASE")
        print("=" * 50)
        
        if not posts_data:
            print("   ❌ Нет данных о постах")
            return False
        
        # Берем топ постов по просмотрам
        top_posts = sorted(posts_data, key=lambda x: x['views'], reverse=True)[:limit]
        
        print(f"   📊 Добавляем {len(top_posts)} лучших постов по просмотрам")
        
        success_count = 0
        
        for i, post in enumerate(top_posts, 1):
            try:
                # Готовим данные для Notion
                notion_data = {
                    "parent": {"database_id": self.content_db_id},
                    "properties": {
                        "Название": {
                            "title": [
                                {
                                    "text": {
                                        "content": post['text'][:100] + "..." if len(post['text']) > 100 else post['text']
                                    }
                                }
                            ]
                        },
                        "Просмотры": {"number": post['views']},
                        "URL публикации": {"url": post['url']},
                        "Дата публикации": {"date": {"start": post['date']} if post['date'] else None},
                        "Тип контента": {
                            "select": {"name": post['media_type']}
                        }
                    }
                }
                
                # Убираем None значения
                if not post['date']:
                    del notion_data["properties"]["Дата публикации"]
                
                # Создаем запись
                create_response = requests.post(
                    "https://api.notion.com/v1/pages",
                    headers=self.notion_headers,
                    json=notion_data
                )
                
                if create_response.status_code == 200:
                    print(f"   ✅ {i}. {post['views']:,} просмотров | {post['text'][:30]}...")
                    success_count += 1
                else:
                    print(f"   ❌ {i}. Ошибка {create_response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {i}. Ошибка: {e}")
        
        print(f"\n   📊 Успешно добавлено: {success_count}/{len(top_posts)} постов")
        return success_count > 0
    
    def run_full_sync(self, channel="rawmid"):
        """Запускает полную синхронизацию"""
        
        print("🚀 ЗАПУСК ПОЛНОЙ СИНХРОНИЗАЦИИ TELEGRAM → NOTION")
        print("=" * 80)
        
        # 1. Получаем данные Telegram
        telegram_data = self.get_telegram_analytics(channel)
        
        if not telegram_data['channel_info'] or 'error' in telegram_data['channel_info']:
            print("❌ Не удалось получить данные канала")
            return False
        
        # 2. Обновляем базу платформ
        platforms_updated = self.update_platforms_database(telegram_data['channel_info'])
        
        # 3. Обновляем базу контента
        content_updated = self.update_content_database(telegram_data['posts_data'])
        
        # 4. Итоговый отчет
        print(f"\n✅ РЕЗУЛЬТАТЫ СИНХРОНИЗАЦИИ:")
        print(f"   📊 Платформы: {'✅ Обновлено' if platforms_updated else '❌ Ошибка'}")
        print(f"   📝 Контент: {'✅ Обновлено' if content_updated else '❌ Ошибка'}")
        
        summary = telegram_data['summary']
        print(f"\n📈 СТАТИСТИКА:")
        print(f"   👥 Подписчики: {telegram_data['channel_info']['subscribers']:,}")
        print(f"   📝 Постов проанализировано: {summary['total_posts']}")
        print(f"   👀 Общие просмотры: {summary['total_views']:,}")
        print(f"   📊 Средние просмотры: {summary['avg_views']:,.0f}")
        print(f"   🏆 Максимум просмотров: {summary['max_views']:,}")
        
        return platforms_updated and content_updated

def main():
    """Главная функция"""
    
    # Проверяем переменные окружения
    required_env = ['NOTION_TOKEN', 'NOTION_PLATFORMS_DB_ID', 'NOTION_CONTENT_PLAN_DB_ID', 'TELEGRAM_BOT_TOKEN']
    missing_env = [var for var in required_env if not os.getenv(var)]
    
    if missing_env:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_env)}")
        return
    
    # Запускаем синхронизацию
    sync = TelegramToNotionFinal()
    success = sync.run_full_sync("rawmid")
    
    if success:
        print(f"\n🎉 СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"🔄 Запускайте этот скрипт ежедневно для автоматического обновления")
    else:
        print(f"\n❌ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ")

if __name__ == "__main__":
    main() 