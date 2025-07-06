#!/usr/bin/env python3
"""
Проверка URL в базе идей для анализа
"""

import os
import asyncio
import logging
from notion_client import AsyncClient
from urllib.parse import urlparse

# Настройка логирования без эмодзи
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('check_urls.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IdeasURLChecker:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.ideas_db_id = 'ad92a6e21485428c84de8587706b3be1'
        self.notion = AsyncClient(auth=self.notion_token)
        
    async def check_all_urls(self, limit: int = 20):
        """Проверить все URL в базе идей"""
        try:
            response = await self.notion.databases.query(
                database_id=self.ideas_db_id,
                filter={
                    "property": "URL",
                    "url": {
                        "is_not_empty": True
                    }
                },
                page_size=limit
            )
            
            logger.info(f"Найдено {len(response['results'])} записей с URL")
            
            url_types = {
                'yandex': [],
                'telegram': [],
                'other': []
            }
            
            for page in response['results']:
                url_prop = page['properties'].get('URL', {})
                url = url_prop.get('url', '') if url_prop else ''
                title = page['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Unknown')
                
                if url:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    
                    if 'yandex' in domain:
                        url_types['yandex'].append({
                            'id': page['id'],
                            'title': title,
                            'url': url
                        })
                    elif 't.me' in domain or 'telegram' in domain:
                        url_types['telegram'].append({
                            'id': page['id'],
                            'title': title,
                            'url': url
                        })
                    else:
                        url_types['other'].append({
                            'id': page['id'],
                            'title': title,
                            'url': url
                        })
            
            # Выводим статистику
            logger.info("=" * 50)
            logger.info("СТАТИСТИКА URL В БАЗЕ ИДЕЙ")
            logger.info("=" * 50)
            logger.info(f"Yandex URL: {len(url_types['yandex'])}")
            logger.info(f"Telegram URL: {len(url_types['telegram'])}")
            logger.info(f"Другие URL: {len(url_types['other'])}")
            
            # Показываем примеры
            if url_types['yandex']:
                logger.info("\nПРИМЕРЫ YANDEX URL:")
                for item in url_types['yandex'][:5]:
                    logger.info(f"  - {item['title']}: {item['url']}")
            
            if url_types['telegram']:
                logger.info("\nПРИМЕРЫ TELEGRAM URL:")
                for item in url_types['telegram'][:5]:
                    logger.info(f"  - {item['title']}: {item['url']}")
            
            if url_types['other']:
                logger.info("\nПРИМЕРЫ ДРУГИХ URL:")
                for item in url_types['other'][:5]:
                    logger.info(f"  - {item['title']}: {item['url']}")
            
            return url_types
            
        except Exception as e:
            logger.error(f"Ошибка проверки URL: {e}")
            return None

async def main():
    checker = IdeasURLChecker()
    await checker.check_all_urls(limit=50)

if __name__ == "__main__":
    asyncio.run(main()) 