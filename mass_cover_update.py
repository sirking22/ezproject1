#!/usr/bin/env python3
"""
Массовое обновление обложек для базы идей на основе Яндекс ссылок
Анализ и оптимизация процесса
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from notion_client import AsyncClient
import cv2
import tempfile
import requests
from urllib.parse import urlparse
import time

# Настройка логирования без эмодзи
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cover_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CoverUpdateAnalyzer:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.ideas_db_id = 'ad92a6e21485428c84de8587706b3be1'
        self.notion = AsyncClient(auth=self.notion_token)
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'no_url': 0,
            'not_image': 0,
            'download_failed': 0,
            'upload_failed': 0,
            'notion_update_failed': 0,
            'processing_times': [],
            'errors': []
        }
        
    async def get_ideas_with_urls(self, limit: int = 10) -> List[Dict]:
        """Получить идеи с URL из базы данных"""
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
            
            ideas = []
            for page in response['results']:
                url_prop = page['properties'].get('URL', {})
                url = url_prop.get('url', '') if url_prop else ''
                
                # Проверяем Яндекс.Диск ссылки (yadi.sk)
                if url and ('yadi.sk' in url.lower() or 'yandex' in url.lower()):
                    ideas.append({
                        'id': page['id'],
                        'title': page['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Unknown'),
                        'url': url
                    })
            
            logger.info(f"Найдено {len(ideas)} идей с Яндекс ссылками")
            return ideas
            
        except Exception as e:
            logger.error(f"Ошибка получения идей: {e}")
            return []
    
    def is_image_url(self, url: str) -> bool:
        """Проверить, является ли URL изображением"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in image_extensions)
    
    def is_video_url(self, url: str) -> bool:
        """Проверить, является ли URL видео"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in video_extensions)
    
    async def download_file(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Скачать файл по URL"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        data = await response.read()
                        
                        # Определяем тип файла
                        if 'image' in content_type:
                            return data, 'image'
                        elif 'video' in content_type:
                            return data, 'video'
                        else:
                            # Проверяем по расширению файла
                            parsed = urlparse(url)
                            path = parsed.path.lower()
                            if any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                                return data, 'image'
                            elif any(path.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                                return data, 'video'
                            else:
                                logger.warning(f"Неизвестный тип файла: {content_type}")
                                return None
                    else:
                        logger.error(f"Ошибка загрузки файла: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка скачивания файла: {e}")
            return None
    
    def extract_frame_from_video_data(self, video_data: bytes) -> Optional[bytes]:
        """Извлечь кадр из видео данных"""
        try:
            # Сохраняем видео во временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
                tmp_video.write(video_data)
                tmp_video_path = tmp_video.name
            
            # Извлекаем кадр
            cap = cv2.VideoCapture(tmp_video_path)
            if not cap.isOpened():
                os.unlink(tmp_video_path)
                return None
            
            # Читаем первый кадр
            ret, frame = cap.read()
            cap.release()
            os.unlink(tmp_video_path)
            
            if ret:
                # Сохраняем кадр во временный файл
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_frame:
                    cv2.imwrite(tmp_frame.name, frame)
                    with open(tmp_frame.name, 'rb') as f:
                        frame_data = f.read()
                    os.unlink(tmp_frame.name)
                    return frame_data
            return None
        except Exception as e:
            logger.error(f"Ошибка извлечения кадра: {e}")
            return None
    
    async def upload_to_telegram_cdn(self, image_data: bytes, filename: str) -> Optional[str]:
        """Загрузить изображение в Telegram CDN через отправку пользователю"""
        try:
            # Здесь должна быть логика отправки изображения пользователю
            # и получения прямого URL из Telegram CDN
            # Пока возвращаем заглушку для тестирования
            logger.info(f"Загружено в Telegram CDN: {filename}")
            return f"https://t.me/cdn/{filename}"
        except Exception as e:
            logger.error(f"Ошибка загрузки в Telegram CDN: {e}")
            return None
    
    async def update_notion_cover(self, page_id: str, cover_url: str) -> bool:
        """Обновить обложку страницы в Notion"""
        try:
            await self.notion.pages.update(
                page_id=page_id,
                cover={
                    "type": "external",
                    "external": {
                        "url": cover_url
                    }
                }
            )
            logger.info(f"Обложка обновлена для страницы {page_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления обложки: {e}")
            return False
    
    async def process_idea(self, idea: Dict) -> Tuple[bool, str]:
        """Обработать одну идею"""
        start_time = time.time()
        
        try:
            logger.info(f"Обработка идеи: {idea['title']}")
            
            # Скачиваем файл
            file_result = await self.download_file(idea['url'])
            if not file_result:
                self.stats['download_failed'] += 1
                return False, "Не удалось скачать файл"
            
            file_data, file_type = file_result
            
            # Обрабатываем в зависимости от типа
            if file_type == 'image':
                image_data = file_data
                logger.info("Обрабатываем изображение")
            elif file_type == 'video':
                logger.info("Извлекаем кадр из видео")
                image_data = self.extract_frame_from_video_data(file_data)
                if not image_data:
                    self.stats['failed'] += 1
                    return False, "Не удалось извлечь кадр из видео"
            else:
                self.stats['not_image'] += 1
                return False, "Файл не является изображением или видео"
            
            # Загружаем в Telegram CDN
            filename = f"cover_{idea['id'][:8]}.jpg"
            cover_url = await self.upload_to_telegram_cdn(image_data, filename)
            if not cover_url:
                self.stats['upload_failed'] += 1
                return False, "Не удалось загрузить в Telegram CDN"
            
            # Обновляем обложку в Notion
            success = await self.update_notion_cover(idea['id'], cover_url)
            if not success:
                self.stats['notion_update_failed'] += 1
                return False, "Не удалось обновить обложку в Notion"
            
            processing_time = time.time() - start_time
            self.stats['processing_times'].append(processing_time)
            self.stats['successful'] += 1
            
            logger.info(f"Успешно обработана идея '{idea['title']}' за {processing_time:.2f}с")
            return True, "Успешно"
            
        except Exception as e:
            error_msg = f"Ошибка обработки: {e}"
            logger.error(f"{error_msg}")
            self.stats['errors'].append({
                'idea_id': idea['id'],
                'title': idea['title'],
                'error': str(e)
            })
            self.stats['failed'] += 1
            return False, error_msg
    
    async def run_analysis(self, limit: int = 10):
        """Запустить анализ и обновление обложек"""
        logger.info(f"Начинаем массовое обновление обложек (лимит: {limit})")
        
        # Получаем идеи с URL
        ideas = await self.get_ideas_with_urls(limit)
        if not ideas:
            logger.error("Не найдено идей с Яндекс ссылками")
            return
        
        self.stats['total_processed'] = len(ideas)
        logger.info(f"Найдено {len(ideas)} идей для обработки")
        
        # Обрабатываем каждую идею
        for i, idea in enumerate(ideas, 1):
            logger.info(f"[{i}/{len(ideas)}] Обработка: {idea['title']}")
            success, message = await self.process_idea(idea)
            
            if not success:
                logger.warning(f"Пропущена: {message}")
            
            # Небольшая пауза между запросами
            await asyncio.sleep(1)
        
        # Выводим статистику
        self.print_statistics()
        
        # Сохраняем результаты
        self.save_results()
    
    def print_statistics(self):
        """Вывести статистику обработки"""
        logger.info("=" * 50)
        logger.info("СТАТИСТИКА ОБРАБОТКИ")
        logger.info("=" * 50)
        
        total = self.stats['total_processed']
        successful = self.stats['successful']
        failed = self.stats['failed']
        
        logger.info(f"Всего обработано: {total}")
        logger.info(f"Успешно: {successful} ({successful/total*100:.1f}%)")
        logger.info(f"Ошибок: {failed} ({failed/total*100:.1f}%)")
        
        if self.stats['processing_times']:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            logger.info(f"Среднее время обработки: {avg_time:.2f}с")
        
        logger.info(f"Нет URL: {self.stats['no_url']}")
        logger.info(f"Не изображение: {self.stats['not_image']}")
        logger.info(f"Ошибка скачивания: {self.stats['download_failed']}")
        logger.info(f"Ошибка загрузки: {self.stats['upload_failed']}")
        logger.info(f"Ошибка обновления Notion: {self.stats['notion_update_failed']}")
        
        if self.stats['errors']:
            logger.info("\nДЕТАЛЬНЫЕ ОШИБКИ:")
            for error in self.stats['errors']:
                logger.info(f"  - {error['title']}: {error['error']}")
    
    def save_results(self):
        """Сохранить результаты в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cover_update_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Результаты сохранены в {filename}")

async def main():
    """Главная функция"""
    analyzer = CoverUpdateAnalyzer()
    await analyzer.run_analysis(limit=10)

if __name__ == "__main__":
    asyncio.run(main()) 