#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 УЛУЧШЕННЫЙ TELEGRAM SCRAPER 

Извлекает все доступные метрики:
✅ Просмотры - 100% работает
❓ Лайки/реакции - ищем 
❓ Комментарии - ищем
📊 Итоговая сумма engagement
"""

import requests
import os
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramEnhancedScraper:
    """Улучшенный скрапер с полной аналитикой"""
    
    def __init__(self, channel="rawmid"):
        self.channel = channel.replace("@", "")
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
    
    def get_channel_info_bot_api(self):
        """Получает базовую информацию о канале через Bot API"""
        
        if not self.bot_token:
            return {"error": "No Bot Token"}
        
        try:
            # Получаем информацию о канале
            chat_info_url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            chat_response = requests.get(chat_info_url, params={'chat_id': f'@{self.channel}'}, timeout=10)
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                if chat_data.get('ok'):
                    chat_info = chat_data['result']
                    
                    # Получаем количество подписчиков
                    count_url = f"https://api.telegram.org/bot{self.bot_token}/getChatMemberCount"
                    count_response = requests.get(count_url, params={'chat_id': f'@{self.channel}'}, timeout=10)
                    
                    subscribers = 0
                    if count_response.status_code == 200:
                        count_data = count_response.json()
                        if count_data.get('ok'):
                            subscribers = count_data['result']
                    
                    return {
                        'id': chat_info.get('id', ''),
                        'title': chat_info.get('title', ''),
                        'username': chat_info.get('username', ''),
                        'description': chat_info.get('description', ''),
                        'subscribers': subscribers,
                        'type': chat_info.get('type', '')
                    }
            
            return {"error": f"Bot API error: {chat_response.status_code}"}
            
        except Exception as e:
            return {"error": f"Exception: {e}"}
    
    def extract_posts_with_all_metrics(self):
        """Извлекает посты со всеми доступными метриками"""
        
        print(f"📊 ИЗВЛЕЧЕНИЕ ПОЛНЫХ МЕТРИК ИЗ @{self.channel}")
        print("=" * 60)
        
        url = f"https://t.me/s/{self.channel}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts_elements = soup.find_all('div', class_='tgme_widget_message')
                
                print(f"📝 Найдено постов: {len(posts_elements)}")
                
                posts_data = []
                
                for i, post_elem in enumerate(posts_elements, 1):
                    post_metrics = self.extract_comprehensive_post_metrics(post_elem, i)
                    if post_metrics:
                        posts_data.append(post_metrics)
                
                # Анализируем результаты
                self.analyze_metrics_availability(posts_data)
                
                return posts_data
            else:
                print(f"❌ Ошибка загрузки: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
    
    def extract_comprehensive_post_metrics(self, post_elem, post_num):
        """Извлекает все возможные метрики из поста"""
        
        try:
            metrics = {
                'post_num': post_num,
                'id': '',
                'text_preview': '',
                'date': '',
                'views': 0,
                'likes': 0,
                'comments': 0,
                'reposts': 0,
                'total_engagement': 0,
                'url': '',
                'media_type': 'text'
            }
            
            # ID поста и URL
            post_link = post_elem.get('data-post', '')
            if post_link:
                metrics['id'] = post_link.split('/')[-1]
                metrics['url'] = f"https://t.me/{post_link}"
            else:
                metrics['id'] = f"post_{post_num}"
            
            # Текст поста (превью)
            text_elem = post_elem.find('div', class_='tgme_widget_message_text')
            if text_elem:
                text_content = text_elem.get_text(strip=True)
                metrics['text_preview'] = text_content[:100] + "..." if len(text_content) > 100 else text_content
            
            # Дата
            date_elem = post_elem.find('time', class_='datetime')
            if date_elem:
                datetime_attr = date_elem.get('datetime', '')
                if datetime_attr:
                    try:
                        date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        metrics['date'] = date_obj.strftime('%Y-%m-%d %H:%M')
                    except:
                        metrics['date'] = date_elem.text.strip()
            
            # Тип медиа
            if post_elem.find('video'):
                metrics['media_type'] = 'video'
            elif post_elem.find('img') or post_elem.find('i', class_='tgme_widget_message_photo_wrap'):
                metrics['media_type'] = 'photo'
            elif post_elem.find('audio'):
                metrics['media_type'] = 'audio'
            
            # ПРОСМОТРЫ (работает точно)
            views_elem = post_elem.find('span', class_='tgme_widget_message_views')
            if views_elem:
                views_text = views_elem.text.strip()
                metrics['views'] = self.convert_count_to_number(views_text)
            
            # ЛАЙКИ/РЕАКЦИИ (экспериментально)
            metrics['likes'] = self.try_extract_likes(post_elem)
            
            # КОММЕНТАРИИ (экспериментально)
            metrics['comments'] = self.try_extract_comments(post_elem)
            
            # РЕПОСТЫ (экспериментально)
            metrics['reposts'] = self.try_extract_reposts(post_elem)
            
            # Общий engagement (лайки + комментарии)
            metrics['total_engagement'] = metrics['likes'] + metrics['comments']
            
            return metrics
            
        except Exception as e:
            print(f"   ❌ Ошибка обработки поста {post_num}: {e}")
            return None
    
    def try_extract_likes(self, post_elem):
        """Пытается извлечь лайки всеми возможными способами"""
        
        # Проверяем различные селекторы для реакций
        possible_like_selectors = [
            '.tgme_widget_message_reactions',
            '.tgme_widget_message_reaction',
            '[class*="reaction"]',
            '[class*="like"]',
            '[class*="heart"]',
            'span[title*="❤"]',
            'span[title*="👍"]',
            '.message_reactions',
            '.post_reactions'
        ]
        
        for selector in possible_like_selectors:
            elements = post_elem.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and re.search(r'\d', text):
                    # Если нашли число в элементе с реакциями
                    return self.convert_count_to_number(text)
        
        # Telegram обычно не показывает лайки в публичном веб-интерфейсе
        # без админ доступа, поэтому скорее всего будет 0
        return 0
    
    def try_extract_comments(self, post_elem):
        """Пытается извлечь комментарии всеми возможными способами"""
        
        possible_comment_selectors = [
            '.tgme_widget_message_comments',
            '.tgme_widget_message_comment',
            '[class*="comment"]',
            '[class*="discussion"]',
            '[href*="comment"]',
            'span[title*="💬"]',
            'a[href*="/c/"]',  # Ссылки на комментарии
            '.message_comments',
            '.post_comments'
        ]
        
        for selector in possible_comment_selectors:
            elements = post_elem.select(selector)
            for elem in elements:
                # Проверяем href для ссылок на комментарии
                href = elem.get('href', '')
                if href and '/c/' in href:
                    # Пытаемся извлечь количество из href или текста
                    text = elem.get_text(strip=True)
                    if text and re.search(r'\d', text):
                        return self.convert_count_to_number(text)
                
                # Проверяем текст элемента
                text = elem.get_text(strip=True)
                if text and re.search(r'\d', text):
                    return self.convert_count_to_number(text)
        
        # Telegram обычно не показывает количество комментариев
        # в публичном веб-интерфейсе без специального доступа
        return 0
    
    def try_extract_reposts(self, post_elem):
        """Пытается извлечь репосты/пересылки"""
        
        possible_repost_selectors = [
            '.tgme_widget_message_forwards',
            '.tgme_widget_message_forward',
            '[class*="forward"]',
            '[class*="share"]',
            '[class*="repost"]',
            'span[title*="🔄"]',
            '.message_forwards',
            '.post_shares'
        ]
        
        for selector in possible_repost_selectors:
            elements = post_elem.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and re.search(r'\d', text):
                    return self.convert_count_to_number(text)
        
        return 0
    
    def convert_count_to_number(self, count_str):
        """Конвертирует строку счетчика в число"""
        
        if not count_str or count_str == "N/A":
            return 0
        
        count_str = str(count_str).replace(' ', '').replace(',', '').lower()
        
        # Извлекаем число из строки
        match = re.search(r'([\d.,]+[km]?)', count_str)
        if not match:
            return 0
        
        number_str = match.group(1)
        
        try:
            if 'k' in number_str:
                number = float(number_str.replace('k', ''))
                return int(number * 1000)
            elif 'm' in number_str:
                number = float(number_str.replace('m', ''))
                return int(number * 1000000)
            else:
                return int(float(number_str))
        except:
            return 0
    
    def analyze_metrics_availability(self, posts_data):
        """Анализирует доступность метрик"""
        
        if not posts_data:
            print("❌ Нет данных для анализа")
            return
        
        total_posts = len(posts_data)
        
        # Подсчитываем доступность каждой метрики
        has_views = sum(1 for p in posts_data if p['views'] > 0)
        has_likes = sum(1 for p in posts_data if p['likes'] > 0)
        has_comments = sum(1 for p in posts_data if p['comments'] > 0)
        has_reposts = sum(1 for p in posts_data if p['reposts'] > 0)
        
        print(f"\n📊 ДОСТУПНОСТЬ МЕТРИК (из {total_posts} постов):")
        print(f"   👀 Просмотры: {has_views}/{total_posts} ({has_views/total_posts*100:.1f}%) ✅")
        print(f"   ❤️ Лайки: {has_likes}/{total_posts} ({has_likes/total_posts*100:.1f}%)")
        print(f"   💬 Комментарии: {has_comments}/{total_posts} ({has_comments/total_posts*100:.1f}%)")
        print(f"   🔄 Репосты: {has_reposts}/{total_posts} ({has_reposts/total_posts*100:.1f}%)")
        
        # Показываем топ 5 постов по просмотрам
        print(f"\n🏆 ТОП-5 ПОСТОВ ПО ПРОСМОТРАМ:")
        top_posts = sorted(posts_data, key=lambda x: x['views'], reverse=True)[:5]
        
        for i, post in enumerate(top_posts, 1):
            engagement_info = ""
            if post['likes'] > 0 or post['comments'] > 0:
                engagement_info = f" | ❤️ {post['likes']} 💬 {post['comments']}"
            
            print(f"   {i}. 👀 {post['views']:,}{engagement_info}")
            print(f"      📝 {post['text_preview'][:50]}...")
            print(f"      🔗 {post['url']}")
        
        # Сохраняем детальные данные
        with open("telegram_enhanced_metrics.json", "w", encoding="utf-8") as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Детальные метрики сохранены в telegram_enhanced_metrics.json")
        
        return {
            'total_posts': total_posts,
            'views_available': has_views,
            'likes_available': has_likes,
            'comments_available': has_comments,
            'reposts_available': has_reposts,
            'top_posts': top_posts
        }
    
    def get_full_analytics(self):
        """Получает полную аналитику канала"""
        
        print(f"🚀 ПОЛНАЯ АНАЛИТИКА @{self.channel}")
        print("=" * 80)
        
        # 1. Информация о канале
        channel_info = self.get_channel_info_bot_api()
        print(f"📊 ИНФОРМАЦИЯ О КАНАЛЕ:")
        if 'error' not in channel_info:
            print(f"   📝 Название: {channel_info['title']}")
            print(f"   👥 Подписчики: {channel_info['subscribers']:,}")
            print(f"   🆔 ID: {channel_info['id']}")
        else:
            print(f"   ❌ {channel_info['error']}")
        
        # 2. Метрики постов
        posts_data = self.extract_posts_with_all_metrics()
        
        return {
            'channel_info': channel_info,
            'posts_data': posts_data,
            'summary': {
                'total_posts': len(posts_data),
                'total_views': sum(p['views'] for p in posts_data),
                'total_likes': sum(p['likes'] for p in posts_data),
                'total_comments': sum(p['comments'] for p in posts_data),
                'avg_views': sum(p['views'] for p in posts_data) / len(posts_data) if posts_data else 0
            }
        }

def main():
    """Главная функция"""
    
    scraper = TelegramEnhancedScraper("rawmid")
    
    # Получаем полную аналитику
    full_data = scraper.get_full_analytics()
    
    print(f"\n✅ ИТОГОВАЯ СТАТИСТИКА:")
    summary = full_data['summary']
    print(f"   📝 Всего постов: {summary['total_posts']}")
    print(f"   👀 Всего просмотров: {summary['total_views']:,}")
    print(f"   📊 Средние просмотры: {summary['avg_views']:,.0f}")
    
    if summary['total_likes'] > 0:
        print(f"   ❤️ Всего лайков: {summary['total_likes']:,}")
    
    if summary['total_comments'] > 0:
        print(f"   💬 Всего комментариев: {summary['total_comments']:,}")

if __name__ == "__main__":
    main() 