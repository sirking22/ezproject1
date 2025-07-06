#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TELEGRAM → NOTION ИНТЕГРАЦИЯ

Автоматическая запись данных канала RAWMID в базы Notion:
1. PLATFORMS_DB → подписчики, общая статистика
2. CONTENT_DB → посты с просмотрами
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram_working_scraper import TelegramWorkingScraper

load_dotenv()

class TelegramNotionIntegration:
    """Интеграция Telegram данных в Notion"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.platforms_db = os.getenv('NOTION_PLATFORMS_DB_ID')
        self.content_db = os.getenv('NOTION_CONTENT_PLAN_DB_ID')
        
        if not self.notion_token:
            raise ValueError("❌ NOTION_TOKEN не найден в .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        self.scraper = TelegramWorkingScraper("rawmid")
    
    def update_platform_statistics(self, telegram_data):
        """Обновляет статистику платформы в базе PLATFORMS"""
        
        print("📊 ОБНОВЛЕНИЕ СТАТИСТИКИ ПЛАТФОРМЫ")
        print("=" * 50)
        
        if not self.platforms_db:
            print("❌ NOTION_PLATFORMS_DB_ID не найден")
            return False
        
        # Ищем существующую запись Telegram
        telegram_page = self.find_telegram_platform()
        
        if telegram_page:
            print(f"✅ Найдена существующая запись Telegram")
            return self.update_existing_platform(telegram_page['id'], telegram_data)
        else:
            print(f"🆕 Создаем новую запись Telegram")
            return self.create_new_platform(telegram_data)
    
    def find_telegram_platform(self):
        """Ищет существующую запись Telegram в базе платформ"""
        
        try:
            query_data = {
                "filter": {
                    "property": "Platforms",
                    "title": {
                        "contains": "Telegram"
                    }
                }
            }
            
            response = requests.post(
                f"https://api.notion.com/v1/databases/{self.platforms_db}/query",
                headers=self.headers,
                json=query_data
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                # Ищем точное совпадение с RAWMID
                for page in results:
                    title_prop = page.get('properties', {}).get('Platforms', {})
                    if title_prop.get('title'):
                        title_text = title_prop['title'][0].get('text', {}).get('content', '')
                        if 'rawmid' in title_text.lower() or 'telegram' in title_text.lower():
                            print(f"   📋 Найдена запись: {title_text}")
                            return page
                
                print(f"   ⚠️ Записи Telegram не найдено среди {len(results)} платформ")
                return None
            else:
                print(f"❌ Ошибка поиска: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка поиска платформы: {e}")
            return None
    
    def create_new_platform(self, telegram_data):
        """Создает новую запись платформы"""
        
        print(f"🆕 Создание новой платформы Telegram")
        
        channel_info = telegram_data.get('channel_info', {})
        subscriber_count = telegram_data.get('subscriber_count', 0)
        stats = telegram_data.get('statistics', {})
        
        # Формируем данные для создания страницы
        page_data = {
            "parent": {"database_id": self.platforms_db},
            "properties": {
                "Platforms": {
                    "title": [
                        {
                            "text": {
                                "content": f"Telegram RAWMID (@rawmid)"
                            }
                        }
                    ]
                },
                "Followers": {
                    "number": subscriber_count
                },
                "Upload": {
                    "number": stats.get('posts_with_views', 0) if stats else 0
                },
                "My account link": {
                    "url": "https://t.me/rawmid"
                }
            }
        }
        
        # Добавляем опциональные поля если они есть
        if stats:
            # Followers target - ставим на 20% больше текущих
            target_followers = int(subscriber_count * 1.2) if subscriber_count else 10000
            page_data["properties"]["Followers target"] = {"number": target_followers}
        
        try:
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                page = response.json()
                print(f"✅ Платформа создана: {page['id']}")
                return True
            else:
                print(f"❌ Ошибка создания: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка создания платформы: {e}")
            return False
    
    def update_existing_platform(self, page_id, telegram_data):
        """Обновляет существующую запись платформы"""
        
        print(f"🔄 Обновление существующей платформы")
        
        subscriber_count = telegram_data.get('subscriber_count', 0)
        stats = telegram_data.get('statistics', {})
        
        update_data = {
            "properties": {
                "Followers": {
                    "number": subscriber_count
                },
                "Upload": {
                    "number": stats.get('posts_with_views', 0) if stats else 0
                }
            }
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"✅ Платформа обновлена")
                print(f"   👥 Подписчики: {subscriber_count:,}")
                print(f"   📝 Постов: {stats.get('posts_with_views', 0) if stats else 0}")
                return True
            else:
                print(f"❌ Ошибка обновления: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обновления платформы: {e}")
            return False
    
    def add_posts_to_content_db(self, telegram_data):
        """Добавляет посты в базу контента"""
        
        print(f"\n📝 ДОБАВЛЕНИЕ ПОСТОВ В БАЗУ КОНТЕНТА")
        print("=" * 50)
        
        if not self.content_db:
            print("❌ NOTION_CONTENT_PLAN_DB_ID не найден")
            return False
        
        posts = telegram_data.get('posts_html', [])
        if not posts:
            print("❌ Нет постов для добавления")
            return False
        
        # Берем только последние 5 постов чтобы не спамить
        recent_posts = posts[:5]
        print(f"📤 Добавляем {len(recent_posts)} последних постов...")
        
        success_count = 0
        
        for i, post in enumerate(recent_posts, 1):
            if self.add_single_post(post, i):
                success_count += 1
        
        print(f"\n✅ Успешно добавлено: {success_count}/{len(recent_posts)} постов")
        return success_count > 0
    
    def add_single_post(self, post, post_num):
        """Добавляет отдельный пост в базу контента"""
        
        try:
            # Формируем название поста
            post_text = post.get('text', '')
            post_title = post_text[:50] + "..." if len(post_text) > 50 else post_text
            if not post_title:
                post_title = f"Telegram пост {post.get('id', post_num)}"
            
            # Проверяем не существует ли уже такой пост
            existing_post = self.find_existing_post(post_title)
            if existing_post:
                print(f"   {post_num}. ⚠️ Пост уже существует: {post_title[:30]}...")
                return False
            
            page_data = {
                "parent": {"database_id": self.content_db},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": post_title
                                }
                            }
                        ]
                    },
                    "Просмотры": {
                        "number": post.get('views_number', 0)
                    },
                    "URL публикации": {
                        "url": post.get('link', '') if post.get('link') else None
                    },
                    "Опубликовано": {
                        "checkbox": True
                    }
                }
            }
            
            # Добавляем дату если есть
            if post.get('date'):
                try:
                    # Конвертируем дату в формат Notion
                    date_obj = datetime.strptime(post['date'], '%Y-%m-%d %H:%M')
                    page_data["properties"]["Дата публикации"] = {
                        "date": {
                            "start": date_obj.strftime('%Y-%m-%d')
                        }
                    }
                except:
                    pass  # Если дата не распарсилась, пропускаем
            
            # Убираем None значения
            if page_data["properties"]["URL публикации"]["url"] is None:
                del page_data["properties"]["URL публикации"]
            
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                views = post.get('views_number', 0)
                print(f"   {post_num}. ✅ {post_title[:30]}... | 👀 {views:,}")
                return True
            else:
                print(f"   {post_num}. ❌ Ошибка: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   {post_num}. ❌ Ошибка добавления: {e}")
            return False
    
    def find_existing_post(self, post_title):
        """Проверяет существует ли пост с таким названием"""
        
        try:
            query_data = {
                "filter": {
                    "property": "Name",
                    "title": {
                        "contains": post_title[:20]  # Ищем по первым 20 символам
                    }
                },
                "page_size": 1
            }
            
            response = requests.post(
                f"https://api.notion.com/v1/databases/{self.content_db}/query",
                headers=self.headers,
                json=query_data
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                return len(results) > 0
            
            return False
            
        except:
            return False  # В случае ошибки считаем что поста нет
    
    def run_full_integration(self):
        """Запускает полную интеграцию"""
        
        print("🚀 ПОЛНАЯ ИНТЕГРАЦИЯ TELEGRAM → NOTION")
        print("🎯 Канал: @rawmid")
        print("=" * 80)
        
        # 1. Собираем данные из Telegram
        print("1️⃣ СБОР ДАННЫХ ИЗ TELEGRAM...")
        telegram_data = self.scraper.scrape_all_data()
        
        if not telegram_data.get('subscriber_count'):
            print("❌ Не удалось получить данные из Telegram")
            return False
        
        # 2. Обновляем базу платформ
        print(f"\n2️⃣ ОБНОВЛЕНИЕ БАЗЫ ПЛАТФОРМ...")
        platform_success = self.update_platform_statistics(telegram_data)
        
        # 3. Добавляем посты в базу контента
        print(f"\n3️⃣ ДОБАВЛЕНИЕ ПОСТОВ В БАЗУ КОНТЕНТА...")
        content_success = self.add_posts_to_content_db(telegram_data)
        
        # 4. Итоги
        print(f"\n📋 ИТОГИ ИНТЕГРАЦИИ")
        print("=" * 50)
        
        if platform_success:
            print("✅ База платформ обновлена")
        else:
            print("❌ Ошибка обновления базы платформ")
        
        if content_success:
            print("✅ Посты добавлены в базу контента")
        else:
            print("⚠️ Посты не добавлены (возможно уже существуют)")
        
        if platform_success or content_success:
            print(f"\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("📊 Данные Telegram синхронизированы с Notion")
            print("🔄 Можно настроить автоматический запуск")
            return True
        else:
            print(f"\n❌ ИНТЕГРАЦИЯ НЕ УДАЛАСЬ")
            return False

def main():
    """Главная функция"""
    
    try:
        integration = TelegramNotionIntegration()
        success = integration.run_full_integration()
        
        if success:
            print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Проверьте базы данных в Notion")
            print("2. Настройте автоматический запуск (ежедневно)")
            print("3. Добавьте другие социальные сети")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 