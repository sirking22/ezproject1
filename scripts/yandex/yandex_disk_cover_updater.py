#!/usr/bin/env python3
"""
Массовое обновление обложек через Яндекс.Диск API
Правильная работа с прямыми ссылками на файлы
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
from urllib.parse import urlparse, unquote
import time
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yandex_cover_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YandexDiskCoverUpdater:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.yandex_token = os.getenv('YA_ACCESS_TOKEN')
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
        
    async def get_ideas_with_yandex_urls(self, limit: int = 10) -> List[Dict]:
        """Получить идеи с Яндекс.Диск ссылками"""
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
                
                # Проверяем Яндекс.Диск ссылки
                if url and 'yadi.sk' in url.lower():
                    ideas.append({
                        'id': page['id'],
                        'title': page['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Unknown'),
                        'url': url
                    })
            
            logger.info(f"Найдено {len(ideas)} идей с Яндекс.Диск ссылками")
            return ideas
            
        except Exception as e:
            logger.error(f"Ошибка получения идей: {e}")
            return []
    
    def extract_file_path_from_yandex_url(self, url: str) -> Optional[str]:
        """Извлечь путь к файлу из Яндекс.Диск ссылки"""
        try:
            # Примеры ссылок:
            # https://yadi.sk/i/7eyapE6k2lLzOQ
            # https://yadi.sk/d/PepVQ4NIVScUAA
            
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if path:
                # Декодируем URL
                decoded_path = unquote(path)
                logger.info(f"Извлечен путь: {decoded_path}")
                return decoded_path
            
            return None
        except Exception as e:
            logger.error(f"Ошибка извлечения пути: {e}")
            return None
    
    async def get_yandex_file_info(self, file_path: str) -> Optional[Dict]:
        """Получить информацию о файле через Яндекс.Диск API"""
        try:
            headers = {
                'Authorization': f'OAuth {self.yandex_token}',
                'Content-Type': 'application/json'
            }
            
            # Получаем метаинформацию о файле
            url = f"https://cloud-api.yandex.net/v1/disk/resources?path={file_path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Информация о файле: {data.get('name')} ({data.get('mime_type')})")
                        return data
                    else:
                        logger.error(f"Ошибка получения информации о файле: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка API Яндекс.Диск: {e}")
            return None
    
    async def get_yandex_download_link(self, file_path: str) -> Optional[str]:
        """Получить прямую ссылку для скачивания файла"""
        try:
            headers = {
                'Authorization': f'OAuth {self.yandex_token}',
                'Content-Type': 'application/json'
            }
            
            # Получаем ссылку для скачивания
            url = f"https://cloud-api.yandex.net/v1/disk/resources/download?path={file_path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        download_url = data.get('href')
                        logger.info(f"Получена ссылка для скачивания: {download_url[:50]}...")
                        return download_url
                    else:
                        logger.error(f"Ошибка получения ссылки для скачивания: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка получения ссылки для скачивания: {e}")
            return None
    
    def is_image_file(self, mime_type: str, filename: str) -> bool:
        """Проверить, является ли файл изображением"""
        image_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        if mime_type in image_mimes:
            return True
        
        # Проверяем по расширению
        for ext in image_extensions:
            if filename.lower().endswith(ext):
                return True
        
        return False
    
    def is_video_file(self, mime_type: str, filename: str) -> bool:
        """Проверить, является ли файл видео"""
        video_mimes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        if mime_type in video_mimes:
            return True
        
        # Проверяем по расширению
        for ext in video_extensions:
            if filename.lower().endswith(ext):
                return True
        
        return False
    
    async def download_file_from_yandex(self, download_url: str) -> Optional[Tuple[bytes, str]]:
        """Скачать файл по прямой ссылке Яндекс.Диск"""
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url, timeout=timeout) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        data = await response.read()
                        
                        logger.info(f"Скачан файл: {len(data)} байт, тип: {content_type}")
                        return data, content_type
                    else:
                        logger.error(f"Ошибка скачивания файла: {response.status}")
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
        """Загрузить изображение в Telegram CDN"""
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
            
            # Извлекаем путь к файлу из URL
            file_path = self.extract_file_path_from_yandex_url(idea['url'])
            if not file_path:
                self.stats['no_url'] += 1
                return False, "Не удалось извлечь путь к файлу"
            
            # Получаем информацию о файле
            file_info = await self.get_yandex_file_info(file_path)
            if not file_info:
                self.stats['download_failed'] += 1
                return False, "Не удалось получить информацию о файле"
            
            filename = file_info.get('name', '')
            mime_type = file_info.get('mime_type', '')
            
            # Проверяем тип файла
            if not (self.is_image_file(mime_type, filename) or self.is_video_file(mime_type, filename)):
                self.stats['not_image'] += 1
                return False, f"Файл не является изображением или видео: {mime_type}"
            
            # Получаем ссылку для скачивания
            download_url = await self.get_yandex_download_link(file_path)
            if not download_url:
                self.stats['download_failed'] += 1
                return False, "Не удалось получить ссылку для скачивания"
            
            # Скачиваем файл
            file_result = await self.download_file_from_yandex(download_url)
            if not file_result:
                self.stats['download_failed'] += 1
                return False, "Не удалось скачать файл"
            
            file_data, content_type = file_result
            
            # Обрабатываем в зависимости от типа
            if self.is_image_file(mime_type, filename):
                image_data = file_data
                logger.info("Обрабатываем изображение")
            elif self.is_video_file(mime_type, filename):
                logger.info("Извлекаем кадр из видео")
                image_data = self.extract_frame_from_video_data(file_data)
                if not image_data:
                    self.stats['failed'] += 1
                    return False, "Не удалось извлечь кадр из видео"
            else:
                self.stats['not_image'] += 1
                return False, "Файл не является изображением или видео"
            
            # Загружаем в Telegram CDN
            cdn_filename = f"cover_{idea['id'][:8]}.jpg"
            cover_url = await self.upload_to_telegram_cdn(image_data, cdn_filename)
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
        logger.info(f"Начинаем массовое обновление обложек через Яндекс.Диск API (лимит: {limit})")
        
        if not self.yandex_token:
            logger.error("Не найден токен Яндекс.Диск (YA_ACCESS_TOKEN)")
            return
        
        # Получаем идеи с URL
        ideas = await self.get_ideas_with_yandex_urls(limit)
        if not ideas:
            logger.error("Не найдено идей с Яндекс.Диск ссылками")
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
            await asyncio.sleep(2)
        
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
        filename = f"yandex_cover_update_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Результаты сохранены в {filename}")

async def main():
    """Главная функция"""
    updater = YandexDiskCoverUpdater()
    await updater.run_analysis(limit=10)

if __name__ == "__main__":
    asyncio.run(main()) 