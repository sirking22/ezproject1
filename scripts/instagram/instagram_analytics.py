#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Instagram Analytics Integration
Модуль для сбора аналитики из Instagram Business API и сохранения в Notion
"""

import os
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Логирование
logger = logging.getLogger(__name__)

@dataclass
class InstagramPost:
    """Данные поста Instagram"""
    id: str
    caption: str
    media_type: str  # IMAGE, VIDEO, CAROUSEL_ALBUM
    media_url: str
    timestamp: str
    permalink: str
    
    # Метрики
    impressions: int = 0
    reach: int = 0
    likes_count: int = 0
    comments_count: int = 0
    saves_count: int = 0
    shares_count: int = 0
    
    # Engagement
    engagement_rate: float = 0.0
    ctr: float = 0.0

@dataclass
class InstagramAccount:
    """Данные аккаунта Instagram"""
    id: str
    username: str
    name: str
    profile_picture_url: str
    followers_count: int = 0
    follows_count: int = 0
    media_count: int = 0

class InstagramAPI:
    """Клиент для Instagram Business API"""
    
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.business_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'
        
        if not self.access_token:
            logger.warning("Instagram Access Token не найден в .env")
        if not self.business_account_id:
            logger.warning("Instagram Business Account ID не найден в .env")
    
    async def get_account_info(self) -> Optional[InstagramAccount]:
        """Получить информацию об аккаунте"""
        if not self.access_token or not self.business_account_id:
            return None
            
        url = f"{self.base_url}/{self.business_account_id}"
        params = {
            'fields': 'id,username,name,profile_picture_url,followers_count,follows_count,media_count',
            'access_token': self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return InstagramAccount(
                            id=data.get('id', ''),
                            username=data.get('username', ''),
                            name=data.get('name', ''),
                            profile_picture_url=data.get('profile_picture_url', ''),
                            followers_count=data.get('followers_count', 0),
                            follows_count=data.get('follows_count', 0),
                            media_count=data.get('media_count', 0)
                        )
                    else:
                        logger.error(f"Instagram API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка получения данных аккаунта: {e}")
            return None
    
    async def get_recent_posts(self, limit: int = 25) -> List[InstagramPost]:
        """Получить последние посты"""
        if not self.access_token or not self.business_account_id:
            return []
            
        # Получаем список медиа
        url = f"{self.base_url}/{self.business_account_id}/media"
        params = {
            'fields': 'id,caption,media_type,media_url,timestamp,permalink',
            'limit': limit,
            'access_token': self.access_token
        }
        
        posts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Получаем метрики для каждого поста
                        for media in data.get('data', []):
                            post = InstagramPost(
                                id=media.get('id', ''),
                                caption=media.get('caption', ''),
                                media_type=media.get('media_type', 'IMAGE'),
                                media_url=media.get('media_url', ''),
                                timestamp=media.get('timestamp', ''),
                                permalink=media.get('permalink', '')
                            )
                            
                            # Получаем метрики поста
                            metrics = await self.get_post_metrics(post.id)
                            if metrics:
                                post.impressions = metrics.get('impressions', 0)
                                post.reach = metrics.get('reach', 0)
                                post.likes_count = metrics.get('likes', 0)
                                post.comments_count = metrics.get('comments', 0)
                                post.saves_count = metrics.get('saved', 0)
                                post.shares_count = metrics.get('shares', 0)
                                
                                # Рассчитываем engagement rate
                                if post.reach > 0:
                                    total_engagement = post.likes_count + post.comments_count + post.saves_count + post.shares_count
                                    post.engagement_rate = (total_engagement / post.reach) * 100
                            
                            posts.append(post)
                            
                    else:
                        logger.error(f"Instagram media API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Ошибка получения постов: {e}")
            
        return posts
    
    async def get_post_metrics(self, media_id: str) -> Optional[Dict]:
        """Получить метрики конкретного поста"""
        if not self.access_token:
            return None
            
        url = f"{self.base_url}/{media_id}/insights"
        params = {
            'metric': 'impressions,reach,likes,comments,saved,shares',
            'access_token': self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        metrics = {}
                        for insight in data.get('data', []):
                            metric_name = insight.get('name')
                            metric_value = insight.get('values', [{}])[0].get('value', 0)
                            metrics[metric_name] = metric_value
                            
                        return metrics
                    else:
                        logger.debug(f"Metrics API error for {media_id}: {response.status}")
                        return {}
        except Exception as e:
            logger.debug(f"Ошибка получения метрик для {media_id}: {e}")
            return {}

class InstagramNotionSync:
    """Синхронизация Instagram аналитики с Notion"""
    
    def __init__(self, notion_token: str, metrics_db_id: str):
        self.notion_token = notion_token
        self.metrics_db_id = metrics_db_id
        self.notion_headers = {
            'Authorization': f'Bearer {notion_token}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
        self.instagram = InstagramAPI()
    
    async def sync_posts_to_notion(self, days_back: int = 7) -> int:
        """Синхронизировать посты Instagram в Notion"""
        logger.info(f"Начинаю синхронизацию Instagram постов за {days_back} дней")
        
        # Получаем посты
        posts = await self.instagram.get_recent_posts(limit=50)
        
        if not posts:
            logger.warning("Посты Instagram не найдены")
            return 0
        
        # Фильтруем по дате
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_posts = []
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.timestamp.replace('Z', '+00:00'))
                if post_date.replace(tzinfo=None) >= cutoff_date:
                    recent_posts.append(post)
            except:
                continue
        
        logger.info(f"Найдено {len(recent_posts)} постов за {days_back} дней")
        
        # Сохраняем в Notion
        saved_count = 0
        for post in recent_posts:
            success = await self.save_post_to_notion(post)
            if success:
                saved_count += 1
            
            # Небольшая пауза между запросами
            await asyncio.sleep(0.5)
        
        logger.info(f"Сохранено {saved_count} постов в Notion")
        return saved_count
    
    async def save_post_to_notion(self, post: InstagramPost) -> bool:
        """Сохранить пост в Notion"""
        url = 'https://api.notion.com/v1/pages'
        
        # Формируем caption для поста
        caption_text = post.caption[:100] + "..." if len(post.caption) > 100 else post.caption
        
        # Определяем категорию по типу медиа
        category = {
            'IMAGE': '📸 Instagram Photo',
            'VIDEO': '🎥 Instagram Video', 
            'CAROUSEL_ALBUM': '📚 Instagram Carousel'
        }.get(post.media_type, '📱 Instagram Post')
        
        properties = {
            "Метрика": {
                "title": [{"text": {"content": f"Instagram: {caption_text}"}}]
            },
            "Значение": {
                "rich_text": [{"text": {"content": f"ER: {post.engagement_rate:.2f}%"}}]
            },
            "Категория": {
                "select": {"name": "📈 Marketing"}
            },
            "Комментарий": {
                "rich_text": [{
                    "text": {
                        "content": (
                            f"👀 Impressions: {post.impressions:,}\n"
                            f"🎯 Reach: {post.reach:,}\n"
                            f"❤️ Likes: {post.likes_count:,}\n"
                            f"💬 Comments: {post.comments_count:,}\n"
                            f"💾 Saves: {post.saves_count:,}\n"
                            f"📤 Shares: {post.shares_count:,}\n"
                            f"📊 ER: {post.engagement_rate:.2f}%\n"
                            f"🔗 {post.permalink}"
                        )
                    }
                }]
            },
            "Дата": {
                "date": {"start": post.timestamp[:10]}  # YYYY-MM-DD
            },
            "Платформа": {
                "select": {"name": "Instagram"}
            },
            "Тип": {
                "select": {"name": category}
            }
        }
        
        data = {
            'parent': {'database_id': self.metrics_db_id},
            'properties': properties
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.notion_headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.debug(f"Пост сохранен: {result['id']}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка сохранения поста в Notion: {response.status} - {error}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при сохранении поста: {e}")
            return False
    
    async def get_account_summary(self) -> Optional[Dict]:
        """Получить сводку по аккаунту"""
        account = await self.instagram.get_account_info()
        if not account:
            return None
        
        # Получаем посты за последние 30 дней
        posts = await self.instagram.get_recent_posts(limit=100)
        
        # Анализируем метрики
        total_impressions = sum(p.impressions for p in posts)
        total_reach = sum(p.reach for p in posts)
        total_engagement = sum(p.likes_count + p.comments_count + p.saves_count + p.shares_count for p in posts)
        avg_engagement_rate = sum(p.engagement_rate for p in posts) / len(posts) if posts else 0
        
        return {
            'account': account,
            'stats': {
                'posts_count': len(posts),
                'total_impressions': total_impressions,
                'total_reach': total_reach,
                'total_engagement': total_engagement,
                'avg_engagement_rate': avg_engagement_rate,
                'followers': account.followers_count
            }
        }

class InstagramScheduler:
    """Планировщик для автоматической синхронизации"""
    
    def __init__(self, sync_manager: InstagramNotionSync):
        self.sync_manager = sync_manager
        self.is_running = False
    
    async def start_hourly_sync(self):
        """Запустить почасовую синхронизацию"""
        self.is_running = True
        logger.info("🚀 Запущена автоматическая синхронизация Instagram (каждый час)")
        
        while self.is_running:
            try:
                # Синхронизируем посты за последние 3 дня
                count = await self.sync_manager.sync_posts_to_notion(days_back=3)
                logger.info(f"✅ Автосинхронизация: обработано {count} постов")
                
                # Ждем час
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Ошибка автосинхронизации: {e}")
                await asyncio.sleep(600)  # Ждем 10 минут при ошибке
    
    def stop(self):
        """Остановить синхронизацию"""
        self.is_running = False
        logger.info("⏹ Автосинхронизация Instagram остановлена")

# Функции для интеграции с ботом
async def quick_instagram_sync(notion_token: str, metrics_db_id: str) -> str:
    """Быстрая синхронизация для бота"""
    sync_manager = InstagramNotionSync(notion_token, metrics_db_id)
    
    try:
        count = await sync_manager.sync_posts_to_notion(days_back=1)
        return f"📱 Instagram: синхронизировано {count} постов за сутки"
    except Exception as e:
        return f"❌ Ошибка синхронизации Instagram: {e}"

async def get_instagram_summary(notion_token: str, metrics_db_id: str) -> str:
    """Получить сводку Instagram для бота"""
    sync_manager = InstagramNotionSync(notion_token, metrics_db_id)
    
    try:
        summary = await sync_manager.get_account_summary()
        if not summary:
            return "❌ Не удалось получить данные Instagram"
        
        account = summary['account']
        stats = summary['stats']
        
        return (
            f"📱 **INSTAGRAM АНАЛИТИКА**\n\n"
            f"**@{account.username}**\n"
            f"👥 Подписчики: {account.followers_count:,}\n"
            f"📸 Всего постов: {account.media_count:,}\n\n"
            f"**За месяц:**\n"
            f"📊 Постов: {stats['posts_count']}\n"
            f"👀 Impressions: {stats['total_impressions']:,}\n"
            f"🎯 Reach: {stats['total_reach']:,}\n"
            f"❤️ Engagement: {stats['total_engagement']:,}\n"
            f"📈 Средний ER: {stats['avg_engagement_rate']:.2f}%"
        )
    except Exception as e:
        return f"❌ Ошибка получения аналитики: {e}"

if __name__ == "__main__":
    # Тестирование модуля
    async def test_instagram():
        notion_token = os.getenv('NOTION_TOKEN')
        metrics_db_id = os.getenv('NOTION_METRICS_DB_ID', '1d9ace03d9ff804191a4d35aeedcbbd4')
        
        if not notion_token:
            print("❌ NOTION_TOKEN не найден")
            return
        
        print("🧪 Тестирование Instagram Analytics...")
        
        sync_manager = InstagramNotionSync(notion_token, metrics_db_id)
        
        # Тест получения информации об аккаунте
        account = await sync_manager.instagram.get_account_info()
        if account:
            print(f"✅ Аккаунт: @{account.username} ({account.followers_count:,} подписчиков)")
        else:
            print("❌ Не удалось получить информацию об аккаунте")
        
        # Тест синхронизации
        result = await quick_instagram_sync(notion_token, metrics_db_id)
        print(result)
    
    asyncio.run(test_instagram()) 