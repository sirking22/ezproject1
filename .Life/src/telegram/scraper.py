#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 РАБОЧИЙ TELEGRAM SCRAPER БЕЗ АДМИН ПРАВ

Комбинирует:
1. Bot API → подписчики, инфо канала
2. RSShub → RSS фид с постами  
3. t.me/s/ → HTML с просмотрами
"""

import os
import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

class TelegramWorkingScraper:
    """Рабочий скрапер для Telegram без админ прав"""
    
    def __init__(self, channel="rawmid"):
        self.channel = channel.replace("@", "")
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def get_channel_info_via_bot(self):
        """Получает информацию о канале через Bot API"""
        
        print("🤖 ПОЛУЧЕНИЕ ИНФО КАНАЛА ЧЕРЕЗ BOT API")
        print("=" * 50)
        
        if not self.bot_token:
            print("❌ Токен бота не найден")
            return None
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            params = {'chat_id': f"@{self.channel}"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    chat_info = result['result']
                    
                    print(f"✅ Канал найден!")
                    print(f"📝 Название: {chat_info.get('title', 'N/A')}")
                    print(f"🆔 ID: {chat_info.get('id', 'N/A')}")
                    print(f"🔗 Username: @{chat_info.get('username', 'N/A')}")
                    
                    return chat_info
                else:
                    print(f"❌ API ошибка: {result.get('description', 'Unknown')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        return None
    
    def get_subscriber_count_via_bot(self):
        """Получает количество подписчиков через Bot API"""
        
        print(f"\n👥 ПОДПИСЧИКИ ЧЕРЕЗ BOT API")
        print("=" * 40)
        
        if not self.bot_token:
            print("❌ Токен бота не найден")
            return None
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getChatMemberCount"
            params = {'chat_id': f"@{self.channel}"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    count = result['result']
                    print(f"✅ Подписчики: {count:,}")
                    return count
                else:
                    print(f"❌ API ошибка: {result.get('description', 'Unknown')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        return None
    
    def get_posts_via_rss(self):
        """Получает посты через RSS фид"""
        
        print(f"\n📡 ПОЛУЧЕНИЕ ПОСТОВ ЧЕРЕЗ RSS")
        print("=" * 40)
        
        rss_url = f"https://rsshub.app/telegram/channel/{self.channel}"
        
        try:
            response = requests.get(rss_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ RSS загружен: {len(response.content)} байт")
                
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                
                print(f"📰 Найдено постов в RSS: {len(items)}")
                
                posts = []
                for i, item in enumerate(items, 1):
                    try:
                        title_elem = item.find('title')
                        description_elem = item.find('description')
                        link_elem = item.find('link')
                        pubdate_elem = item.find('pubDate')
                        
                        post_data = {
                            'id': f"rss_{i}",
                            'title': title_elem.text if title_elem is not None else "",
                            'description': description_elem.text if description_elem is not None else "",
                            'link': link_elem.text if link_elem is not None else "",
                            'pub_date': pubdate_elem.text if pubdate_elem is not None else "",
                            'views': None  # RSS не содержит просмотры
                        }
                        
                        posts.append(post_data)
                        
                        # Выводим первые 3 поста
                        if i <= 3:
                            title = post_data['title'][:50] + "..." if len(post_data['title']) > 50 else post_data['title']
                            print(f"   {i}. RSS: {title}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Ошибка парсинга RSS поста {i}: {e}")
                        continue
                
                return posts
            else:
                print(f"❌ RSS недоступен: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Ошибка RSS: {e}")
        
        return []
    
    def get_posts_with_views_via_html(self):
        """Получает посты с просмотрами через HTML"""
        
        print(f"\n🌐 ПОЛУЧЕНИЕ ПОСТОВ С ПРОСМОТРАМИ ЧЕРЕЗ HTML")
        print("=" * 50)
        
        html_url = f"https://t.me/s/{self.channel}"
        
        try:
            response = requests.get(html_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ HTML загружен: {len(response.content)} байт")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                posts_elements = soup.find_all('div', class_='tgme_widget_message')
                
                print(f"📝 Найдено постов в HTML: {len(posts_elements)}")
                
                posts = []
                for i, post_elem in enumerate(posts_elements, 1):
                    try:
                        # ID поста
                        post_link = post_elem.get('data-post', '')
                        post_id = post_link.split('/')[-1] if post_link else f"html_{i}"
                        
                        # Дата
                        date_elem = post_elem.find('time', class_='datetime')
                        post_date = ""
                        if date_elem:
                            datetime_attr = date_elem.get('datetime', '')
                            if datetime_attr:
                                try:
                                    date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                                    post_date = date_obj.strftime('%Y-%m-%d %H:%M')
                                except:
                                    post_date = date_elem.text.strip()
                        
                        # Текст
                        text_elem = post_elem.find('div', class_='tgme_widget_message_text')
                        post_text = text_elem.get_text(strip=True) if text_elem else ""
                        
                        # Просмотры - ключевая информация!
                        views_elem = post_elem.find('span', class_='tgme_widget_message_views')
                        views_raw = ""
                        views_number = 0
                        
                        if views_elem:
                            views_raw = views_elem.text.strip()
                            # Конвертируем в число
                            views_number = self.convert_views_to_number(views_raw)
                        
                        # Тип медиа
                        has_photo = bool(post_elem.find('a', class_='tgme_widget_message_photo_wrap'))
                        has_video = bool(post_elem.find('a', class_='tgme_widget_message_video_wrap'))
                        
                        media_type = "text"
                        if has_photo and has_video:
                            media_type = "photo_video"
                        elif has_photo:
                            media_type = "photo"
                        elif has_video:
                            media_type = "video"
                        
                        post_data = {
                            'id': post_id,
                            'date': post_date,
                            'text': post_text,
                            'views_raw': views_raw,
                            'views_number': views_number,
                            'media_type': media_type,
                            'link': f"https://t.me/{self.channel}/{post_id}" if post_id.isdigit() else ""
                        }
                        
                        posts.append(post_data)
                        
                        # Выводим первые 3 поста
                        if i <= 3:
                            text_preview = post_text[:40] + "..." if len(post_text) > 40 else post_text
                            print(f"   {i}. 👀 {views_raw} | {media_type} | {text_preview}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Ошибка парсинга HTML поста {i}: {e}")
                        continue
                
                return posts
            else:
                print(f"❌ HTML недоступен: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Ошибка HTML: {e}")
        
        return []
    
    def convert_views_to_number(self, views_str):
        """Конвертирует строку просмотров в число"""
        
        if not views_str or views_str == "N/A":
            return 0
        
        views_str = str(views_str).replace(' ', '').replace(',', '').lower()
        
        try:
            if 'k' in views_str:
                number = float(views_str.replace('k', ''))
                return int(number * 1000)
            elif 'm' in views_str:
                number = float(views_str.replace('m', ''))
                return int(number * 1000000)
            else:
                return int(float(views_str))
        except:
            return 0
    
    def analyze_statistics(self, posts):
        """Анализирует статистику постов"""
        
        print(f"\n📊 АНАЛИЗ СТАТИСТИКИ")
        print("=" * 40)
        
        if not posts:
            print("❌ Нет постов для анализа")
            return None
        
        # Фильтруем посты с просмотрами
        posts_with_views = [p for p in posts if p.get('views_number', 0) > 0]
        
        if not posts_with_views:
            print("⚠️ Нет постов с данными о просмотрах")
            return None
        
        views = [p['views_number'] for p in posts_with_views]
        
        stats = {
            'total_posts': len(posts),
            'posts_with_views': len(posts_with_views),
            'avg_views': sum(views) / len(views),
            'max_views': max(views),
            'min_views': min(views),
            'total_views': sum(views)
        }
        
        print(f"📈 Всего постов: {stats['total_posts']}")
        print(f"👀 С просмотрами: {stats['posts_with_views']}")
        print(f"📊 Средние просмотры: {stats['avg_views']:,.0f}")
        print(f"🔥 Максимум: {stats['max_views']:,.0f}")
        print(f"📉 Минимум: {stats['min_views']:,.0f}")
        print(f"🎯 Всего просмотров: {stats['total_views']:,.0f}")
        
        return stats
    
    def scrape_all_data(self):
        """Собирает все данные канала"""
        
        print("🎯 ПОЛНЫЙ СБОР ДАННЫХ КАНАЛА RAWMID БЕЗ АДМИН ПРАВ")
        print("=" * 80)
        
        result = {
            'channel_info': None,
            'subscriber_count': None,
            'posts_rss': [],
            'posts_html': [],
            'statistics': None,
            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 1. Информация о канале
        result['channel_info'] = self.get_channel_info_via_bot()
        
        # 2. Количество подписчиков
        result['subscriber_count'] = self.get_subscriber_count_via_bot()
        
        # 3. Посты через RSS
        result['posts_rss'] = self.get_posts_via_rss()
        
        # 4. Посты с просмотрами через HTML
        result['posts_html'] = self.get_posts_with_views_via_html()
        
        # 5. Анализ статистики
        result['statistics'] = self.analyze_statistics(result['posts_html'])
        
        print(f"\n✅ СБОР ДАННЫХ ЗАВЕРШЕН!")
        print("=" * 50)
        
        if result['subscriber_count']:
            print(f"✅ Подписчики: {result['subscriber_count']:,}")
        
        if result['posts_html']:
            print(f"✅ Посты с просмотрами: {len(result['posts_html'])}")
        
        if result['posts_rss']:
            print(f"✅ Посты из RSS: {len(result['posts_rss'])}")
        
        if result['statistics']:
            print(f"✅ Статистика рассчитана")
        
        print(f"\n🎯 ГОТОВО К ИНТЕГРАЦИИ С NOTION!")
        
        return result

def main():
    """Главная функция"""
    
    scraper = TelegramWorkingScraper("rawmid")
    data = scraper.scrape_all_data()
    
    # Сохраняем результат в JSON для анализа
    with open("telegram_rawmid_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Данные сохранены в telegram_rawmid_data.json")

if __name__ == "__main__":
    main() 