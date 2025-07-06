#!/usr/bin/env python3
"""
Массовое обновление обложек через локальный HTTP сервер
Временное решение без внешних сервисов
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
from bs4 import BeautifulSoup
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import webbrowser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_server_cover_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalImageServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.server_thread = None
        self.images_dir = "temp_images"
        self.base_url = f"http://localhost:{port}"
        
        # Создаем директорию для изображений
        os.makedirs(self.images_dir, exist_ok=True)
    
    def start_server(self):
        """Запустить HTTP сервер в отдельном потоке"""
        try:
            # Проверяем, свободен ли порт
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            
            if result == 0:
                logger.warning(f"Порт {self.port} занят, пробуем следующий")
                self.port += 1
                self.base_url = f"http://localhost:{self.port}"
            
            # Меняем рабочую директорию для сервера
            original_cwd = os.getcwd()
            os.chdir(self.images_dir)
            
            # Запускаем сервер
            self.server = HTTPServer(('localhost', self.port), SimpleHTTPRequestHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Возвращаем рабочую директорию
            os.chdir(original_cwd)
            
            logger.info(f"Локальный сервер запущен на {self.base_url}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска сервера: {e}")
            return False
    
    def stop_server(self):
        """Остановить HTTP сервер"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Локальный сервер остановлен")
    
    def save_image(self, image_data: bytes, filename: str) -> str:
        """Сохранить изображение и вернуть URL"""
        try:
            filepath = os.path.join(self.images_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            image_url = f"{self.base_url}/{filename}"
            logger.info(f"Изображение сохранено: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"Ошибка сохранения изображения: {e}")
            return None
    
    def cleanup_images(self):
        """Очистить все временные изображения"""
        try:
            for filename in os.listdir(self.images_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    filepath = os.path.join(self.images_dir, filename)
                    os.remove(filepath)
                    logger.info(f"Удален файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")

class LocalServerCoverUpdater:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.ideas_db_id = 'ad92a6e21485428c84de8587706b3be1'
        self.notion = AsyncClient(auth=self.notion_token)
        self.image_server = LocalImageServer()
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
    
    async def get_yandex_page_content(self, url: str) -> Optional[str]:
        """Получить содержимое страницы Яндекс.Диск"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Получена страница: {len(content)} символов")
                        return content
                    else:
                        logger.error(f"Ошибка получения страницы: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка получения страницы: {e}")
            return None
    
    def extract_download_link_from_html(self, html_content: str) -> Optional[str]:
        """Извлечь прямую ссылку на скачивание из HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ищем в мета-тегах (самый надежный способ для Яндекс.Диск)
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('property') == 'og:image' or meta.get('name') == 'twitter:image':
                    link = meta.get('content')
                    if link:
                        logger.info(f"Найдена ссылка в мета-теге: {link[:50]}...")
                        return link
            
            # Если не нашли в мета-тегах, ищем по паттернам
            patterns = [
                r'https://[^"]*\.yadi\.sk/[^"]*\.(jpg|jpeg|png|gif|bmp|webp|mp4|avi|mov|mkv|webm)',
                r'data-href="([^"]*)"',
                r'href="([^"]*download[^"]*)"',
                r'src="([^"]*\.(jpg|jpeg|png|gif|bmp|webp|mp4|avi|mov|mkv|webm))"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    logger.info(f"Найдены совпадения: {len(matches)}")
                    # Берем первое совпадение
                    if isinstance(matches[0], tuple):
                        link = matches[0][0]
                    else:
                        link = matches[0]
                    
                    # Если ссылка относительная, делаем абсолютной
                    if link.startswith('//'):
                        link = 'https:' + link
                    elif link.startswith('/'):
                        link = 'https://yadi.sk' + link
                    
                    logger.info(f"Извлечена ссылка: {link[:50]}...")
                    return link
            
            logger.warning("Не удалось найти прямую ссылку на файл")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка извлечения ссылки: {e}")
            return None
    
    async def download_file(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Скачать файл по URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        data = await response.read()
                        
                        logger.info(f"Скачан файл: {len(data)} байт, тип: {content_type}")
                        
                        # Определяем тип файла
                        if 'image' in content_type or any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                            return data, 'image'
                        elif 'video' in content_type or any(url.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                            return data, 'video'
                        else:
                            logger.warning(f"Неизвестный тип файла: {content_type}")
                            return None
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
            
            # Получаем содержимое страницы Яндекс.Диск
            html_content = await self.get_yandex_page_content(idea['url'])
            if not html_content:
                self.stats['download_failed'] += 1
                return False, "Не удалось получить содержимое страницы"
            
            # Извлекаем прямую ссылку на файл
            download_url = self.extract_download_link_from_html(html_content)
            if not download_url:
                self.stats['download_failed'] += 1
                return False, "Не удалось извлечь прямую ссылку на файл"
            
            # Скачиваем файл
            file_result = await self.download_file(download_url)
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
            
            # Сохраняем изображение на локальный сервер
            filename = f"cover_{idea['id'][:8]}.jpg"
            cover_url = self.image_server.save_image(image_data, filename)
            if not cover_url:
                self.stats['upload_failed'] += 1
                return False, "Не удалось сохранить изображение на сервер"
            
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
        logger.info(f"Начинаем массовое обновление обложек через локальный сервер (лимит: {limit})")
        
        # Запускаем локальный сервер
        if not self.image_server.start_server():
            logger.error("Не удалось запустить локальный сервер")
            return
        
        try:
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
            
        finally:
            # Останавливаем сервер
            self.image_server.stop_server()
    
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
        filename = f"local_server_cover_update_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Результаты сохранены в {filename}")
    
    def cleanup(self):
        """Очистить временные файлы"""
        self.image_server.cleanup_images()

async def main():
    """Главная функция"""
    updater = LocalServerCoverUpdater()
    try:
        await updater.run_analysis(limit=10)
    finally:
        updater.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 