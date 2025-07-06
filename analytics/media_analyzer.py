#!/usr/bin/env python3
"""
🎬 MEDIA ANALYZER
Анализ медиа контента без использования LLM токенов

ВОЗМОЖНОСТИ:
1. Анализ изображений (размер, формат, качество)
2. Анализ видео (длительность, разрешение, размер)
3. Анализ аудио (длительность, качество)
4. Извлечение метаданных
5. Автоматическая категоризация
6. Определение ценности контента

ТЕХНОЛОГИИ:
- PIL/Pillow для изображений
- OpenCV для видео
- librosa для аудио
- exifread для метаданных
- Без использования LLM API
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

# Попытка импорта библиотек (с fallback)
try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

@dataclass
class MediaInfo:
    """Информация о медиа файле"""
    file_path: str
    file_type: str
    file_size: int
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    quality_score: float = 0.0
    metadata: Dict = None
    content_tags: List[str] = None
    value_score: float = 0.0
    processing_notes: List[str] = None

class MediaAnalyzer:
    """Анализатор медиа контента"""
    
    def __init__(self):
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
        }
        
        # Критерии качества
        self.quality_thresholds = {
            'image': {
                'min_resolution': (640, 480),
                'good_resolution': (1920, 1080),
                'excellent_resolution': (3840, 2160),
                'min_file_size': 50 * 1024,  # 50KB
                'max_file_size': 50 * 1024 * 1024  # 50MB
            },
            'video': {
                'min_duration': 5,  # секунд
                'good_duration': 60,
                'max_duration': 3600,  # 1 час
                'min_resolution': (720, 480),
                'good_resolution': (1920, 1080)
            },
            'audio': {
                'min_duration': 10,
                'good_duration': 300,  # 5 минут
                'max_duration': 7200  # 2 часа
            }
        }
        
        # Автоматические теги
        self.auto_tags = {
            'high_quality': ['качество', 'hd', '4k'],
            'screenshot': ['скриншот', 'screenshot'],
            'meme': ['мем', 'meme', 'funny'],
            'tutorial': ['туториал', 'tutorial', 'guide'],
            'presentation': ['презентация', 'presentation', 'slides'],
            'design': ['дизайн', 'design', 'ui', 'ux'],
            'code': ['код', 'code', 'programming']
        }

    async def analyze_media_from_telegram_data(self, analysis_data: Dict) -> Dict:
        """Анализирует медиа из данных Telegram"""
        print("🎬 АНАЛИЗ МЕДИА КОНТЕНТА")
        print("="*50)
        
        media_analysis = {}
        total_files = 0
        analyzed_files = 0
        
        for page_id, data in analysis_data.items():
            files = data.get('extracted_files', [])
            if not files:
                continue
            
            total_files += len(files)
            page_media_info = []
            
            for file_info in files:
                try:
                    media_info = await self._analyze_single_file(file_info)
                    if media_info:
                        page_media_info.append(media_info)
                        analyzed_files += 1
                except Exception as e:
                    print(f"⚠️ Ошибка анализа файла {file_info}: {e}")
            
            if page_media_info:
                media_analysis[page_id] = {
                    'files_count': len(files),
                    'analyzed_count': len(page_media_info),
                    'media_info': page_media_info,
                    'summary': self._create_page_media_summary(page_media_info)
                }
        
        print(f"📊 Всего файлов: {total_files}")
        print(f"✅ Проанализировано: {analyzed_files}")
        print(f"📄 Страниц с медиа: {len(media_analysis)}")
        
        return media_analysis

    async def _analyze_single_file(self, file_info: str) -> Optional[MediaInfo]:
        """Анализирует один файл"""
        # Парсим информацию о файле из строки Telegram
        file_data = self._parse_telegram_file_info(file_info)
        if not file_data:
            return None
        
        # Определяем тип файла
        file_type = self._detect_file_type(file_data['name'])
        if not file_type:
            return None
        
        # Создаем базовую информацию
        media_info = MediaInfo(
            file_path=file_data['name'],
            file_type=file_type,
            file_size=file_data.get('size', 0),
            metadata={},
            content_tags=[],
            processing_notes=[]
        )
        
        # Анализируем в зависимости от типа
        if file_type == 'image':
            await self._analyze_image(media_info, file_data)
        elif file_type == 'video':
            await self._analyze_video(media_info, file_data)
        elif file_type == 'audio':
            await self._analyze_audio(media_info, file_data)
        
        # Вычисляем оценки
        media_info.quality_score = self._calculate_quality_score(media_info)
        media_info.value_score = self._calculate_value_score(media_info)
        
        # Добавляем автоматические теги
        media_info.content_tags.extend(self._generate_auto_tags(media_info))
        
        return media_info

    def _parse_telegram_file_info(self, file_info: str) -> Optional[Dict]:
        """Парсит информацию о файле из Telegram"""
        # Пример: "• image@12-01-2024_15-30-45.jpg (2.5MB) [photo] - Описание"
        import re
        
        patterns = [
            r'•\s*([^@]+)@[\d-_]+\.(\w+)\s*\(([^)]+)\)\s*\[([^\]]+)\]\s*-?\s*(.*)',
            r'•\s*([^(]+)\s*\(([^)]+)\)\s*\[([^\]]+)\]\s*-?\s*(.*)',
            r'([^(]+)\s*\(([^)]+)\)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, file_info.strip())
            if match:
                groups = match.groups()
                
                name = groups[0].strip() if len(groups) > 0 else "unknown"
                size_str = groups[-3] if len(groups) > 2 else groups[-2] if len(groups) > 1 else "0MB"
                
                # Парсим размер
                size = self._parse_file_size(size_str)
                
                return {
                    'name': name,
                    'size': size,
                    'raw_info': file_info
                }
        
        # Если паттерны не сработали, возвращаем базовую информацию
        return {
            'name': file_info.strip(),
            'size': 0,
            'raw_info': file_info
        }

    def _parse_file_size(self, size_str: str) -> int:
        """Парсит размер файла"""
        import re
        
        match = re.search(r'([\d.]+)\s*(KB|MB|GB)', size_str.upper())
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            
            multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            return int(value * multipliers.get(unit, 1))
        
        return 0

    def _detect_file_type(self, filename: str) -> Optional[str]:
        """Определяет тип файла по расширению"""
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.supported_formats.items():
            if ext in extensions:
                return file_type
        
        return None

    async def _analyze_image(self, media_info: MediaInfo, file_data: Dict):
        """Анализирует изображение"""
        # Извлекаем информацию из имени файла
        filename = file_data['name'].lower()
        
        # Определяем разрешение по имени (если есть)
        import re
        resolution_match = re.search(r'(\d{3,4})x(\d{3,4})', filename)
        if resolution_match:
            width, height = int(resolution_match.group(1)), int(resolution_match.group(2))
            media_info.dimensions = (width, height)
        
        # Анализируем по ключевым словам в имени
        if any(word in filename for word in ['screenshot', 'скриншот', 'screen']):
            media_info.content_tags.append('скриншот')
        
        if any(word in filename for word in ['photo', 'img', 'pic']):
            media_info.content_tags.append('фото')
        
        # Если файл доступен локально и PIL установлен
        if PIL_AVAILABLE and os.path.exists(file_data['name']):
            try:
                with Image.open(file_data['name']) as img:
                    media_info.dimensions = img.size
                    media_info.metadata['format'] = img.format
                    media_info.metadata['mode'] = img.mode
                    
                    # Извлекаем EXIF данные
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        media_info.metadata['exif'] = {}
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            media_info.metadata['exif'][tag] = value
                            
            except Exception as e:
                media_info.processing_notes.append(f"Ошибка PIL анализа: {e}")

    async def _analyze_video(self, media_info: MediaInfo, file_data: Dict):
        """Анализирует видео"""
        filename = file_data['name'].lower()
        
        # Определяем тип видео по имени
        if any(word in filename for word in ['reel', 'story', 'stories']):
            media_info.content_tags.append('социальные сети')
        
        if any(word in filename for word in ['tutorial', 'guide', 'lesson']):
            media_info.content_tags.append('обучение')
        
        # Если OpenCV доступен и файл существует
        if CV2_AVAILABLE and os.path.exists(file_data['name']):
            try:
                cap = cv2.VideoCapture(file_data['name'])
                
                # Получаем основные параметры
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                media_info.dimensions = (width, height)
                media_info.duration = frame_count / fps if fps > 0 else 0
                media_info.metadata['fps'] = fps
                media_info.metadata['frame_count'] = frame_count
                
                cap.release()
                
            except Exception as e:
                media_info.processing_notes.append(f"Ошибка CV2 анализа: {e}")

    async def _analyze_audio(self, media_info: MediaInfo, file_data: Dict):
        """Анализирует аудио"""
        filename = file_data['name'].lower()
        
        # Определяем тип аудио
        if any(word in filename for word in ['voice', 'голос', 'запись']):
            media_info.content_tags.append('голосовое сообщение')
        
        if any(word in filename for word in ['music', 'song', 'музыка']):
            media_info.content_tags.append('музыка')
        
        # Если librosa доступен и файл существует
        if LIBROSA_AVAILABLE and os.path.exists(file_data['name']):
            try:
                y, sr = librosa.load(file_data['name'])
                media_info.duration = librosa.get_duration(y=y, sr=sr)
                media_info.metadata['sample_rate'] = sr
                media_info.metadata['channels'] = 1 if y.ndim == 1 else y.shape[0]
                
            except Exception as e:
                media_info.processing_notes.append(f"Ошибка librosa анализа: {e}")

    def _calculate_quality_score(self, media_info: MediaInfo) -> float:
        """Вычисляет оценку качества медиа"""
        score = 0.0
        thresholds = self.quality_thresholds.get(media_info.file_type, {})
        
        if media_info.file_type == 'image':
            # Оценка по размеру файла
            if media_info.file_size > thresholds.get('min_file_size', 0):
                score += 0.3
            
            # Оценка по разрешению
            if media_info.dimensions:
                width, height = media_info.dimensions
                pixels = width * height
                
                min_res = thresholds.get('min_resolution', (0, 0))
                good_res = thresholds.get('good_resolution', (1920, 1080))
                excellent_res = thresholds.get('excellent_resolution', (3840, 2160))
                
                min_pixels = min_res[0] * min_res[1]
                good_pixels = good_res[0] * good_res[1]
                excellent_pixels = excellent_res[0] * excellent_res[1]
                
                if pixels >= excellent_pixels:
                    score += 0.7
                elif pixels >= good_pixels:
                    score += 0.5
                elif pixels >= min_pixels:
                    score += 0.3
        
        elif media_info.file_type == 'video':
            # Оценка по длительности
            if media_info.duration:
                min_dur = thresholds.get('min_duration', 0)
                good_dur = thresholds.get('good_duration', 60)
                
                if media_info.duration >= good_dur:
                    score += 0.4
                elif media_info.duration >= min_dur:
                    score += 0.2
            
            # Оценка по разрешению
            if media_info.dimensions:
                width, height = media_info.dimensions
                if width >= 1920 and height >= 1080:
                    score += 0.6
                elif width >= 1280 and height >= 720:
                    score += 0.4
                elif width >= 640 and height >= 480:
                    score += 0.2
        
        elif media_info.file_type == 'audio':
            # Оценка по длительности
            if media_info.duration:
                min_dur = thresholds.get('min_duration', 0)
                good_dur = thresholds.get('good_duration', 300)
                
                if media_info.duration >= good_dur:
                    score += 0.5
                elif media_info.duration >= min_dur:
                    score += 0.3
            
            # Оценка по размеру файла (качество кодирования)
            if media_info.file_size > 1024 * 1024:  # > 1MB
                score += 0.5
        
        return min(score, 1.0)

    def _calculate_value_score(self, media_info: MediaInfo) -> float:
        """Вычисляет оценку ценности контента"""
        score = 0.0
        
        # Базовая оценка качества
        score += media_info.quality_score * 0.4
        
        # Бонусы за тип контента
        valuable_tags = ['обучение', 'tutorial', 'дизайн', 'код', 'презентация']
        if any(tag in media_info.content_tags for tag in valuable_tags):
            score += 0.3
        
        # Бонус за размер (не слишком маленький, не слишком большой)
        if media_info.file_type == 'image':
            if 100*1024 <= media_info.file_size <= 10*1024*1024:  # 100KB - 10MB
                score += 0.2
        elif media_info.file_type == 'video':
            if media_info.duration and 30 <= media_info.duration <= 1800:  # 30сек - 30мин
                score += 0.2
        elif media_info.file_type == 'audio':
            if media_info.duration and 60 <= media_info.duration <= 3600:  # 1мин - 1час
                score += 0.2
        
        # Штраф за низкое качество
        if media_info.quality_score < 0.3:
            score -= 0.2
        
        return max(0.0, min(score, 1.0))

    def _generate_auto_tags(self, media_info: MediaInfo) -> List[str]:
        """Генерирует автоматические теги"""
        tags = []
        filename = media_info.file_path.lower()
        
        # Теги по качеству
        if media_info.quality_score >= 0.7:
            tags.append('высокое качество')
        elif media_info.quality_score <= 0.3:
            tags.append('низкое качество')
        
        # Теги по размеру
        if media_info.file_type == 'image' and media_info.dimensions:
            width, height = media_info.dimensions
            if width >= 3840 or height >= 2160:
                tags.append('4K')
            elif width >= 1920 or height >= 1080:
                tags.append('HD')
        
        # Теги по ключевым словам в имени файла
        for tag_category, keywords in self.auto_tags.items():
            if any(keyword in filename for keyword in keywords):
                tags.append(tag_category)
        
        return list(set(tags))  # Убираем дубликаты

    def _create_page_media_summary(self, media_info_list: List[MediaInfo]) -> Dict:
        """Создает сводку по медиа на странице"""
        if not media_info_list:
            return {}
        
        summary = {
            'total_files': len(media_info_list),
            'by_type': {},
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'value_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'total_size': 0,
            'avg_quality': 0,
            'avg_value': 0,
            'top_tags': {}
        }
        
        # Анализируем каждый файл
        for media in media_info_list:
            # По типам
            if media.file_type not in summary['by_type']:
                summary['by_type'][media.file_type] = 0
            summary['by_type'][media.file_type] += 1
            
            # По качеству
            if media.quality_score >= 0.7:
                summary['quality_distribution']['high'] += 1
            elif media.quality_score >= 0.4:
                summary['quality_distribution']['medium'] += 1
            else:
                summary['quality_distribution']['low'] += 1
            
            # По ценности
            if media.value_score >= 0.7:
                summary['value_distribution']['high'] += 1
            elif media.value_score >= 0.4:
                summary['value_distribution']['medium'] += 1
            else:
                summary['value_distribution']['low'] += 1
            
            # Размер
            summary['total_size'] += media.file_size
            
            # Теги
            for tag in media.content_tags:
                if tag not in summary['top_tags']:
                    summary['top_tags'][tag] = 0
                summary['top_tags'][tag] += 1
        
        # Средние значения
        summary['avg_quality'] = sum(m.quality_score for m in media_info_list) / len(media_info_list)
        summary['avg_value'] = sum(m.value_score for m in media_info_list) / len(media_info_list)
        
        # Топ теги (сортированные)
        summary['top_tags'] = dict(sorted(summary['top_tags'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5])
        
        return summary

    async def save_analysis_results(self, media_analysis: Dict):
        """Сохраняет результаты анализа"""
        # Конвертируем MediaInfo в словари для JSON
        json_data = {}
        for page_id, page_data in media_analysis.items():
            json_data[page_id] = {
                'files_count': page_data['files_count'],
                'analyzed_count': page_data['analyzed_count'],
                'media_info': [asdict(media) for media in page_data['media_info']],
                'summary': page_data['summary']
            }
        
        with open('media_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print("💾 Результаты анализа медиа сохранены: media_analysis_results.json")

async def main():
    """Главная функция для тестирования"""
    analyzer = MediaAnalyzer()
    
    # Загружаем данные анализа Telegram
    try:
        with open("telegram_full_analysis.json", "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
            # Конвертируем список в словарь
            if isinstance(analysis_data, list):
                analysis_dict = {item["page_id"]: item for item in analysis_data}
            else:
                analysis_dict = analysis_data
    except FileNotFoundError:
        print("❌ Файл telegram_full_analysis.json не найден")
        return
    
    # Анализируем медиа
    media_analysis = await analyzer.analyze_media_from_telegram_data(analysis_dict)
    
    # Сохраняем результаты
    await analyzer.save_analysis_results(media_analysis)
    
    # Выводим статистику
    print("\n📊 СТАТИСТИКА МЕДИА АНАЛИЗА")
    print("="*50)
    
    total_pages = len(media_analysis)
    total_files = sum(data['files_count'] for data in media_analysis.values())
    total_analyzed = sum(data['analyzed_count'] for data in media_analysis.values())
    
    print(f"📄 Страниц с медиа: {total_pages}")
    print(f"📁 Всего файлов: {total_files}")
    print(f"✅ Проанализировано: {total_analyzed}")
    
    if total_analyzed > 0:
        high_quality = sum(1 for data in media_analysis.values() 
                          for media in data['media_info'] 
                          if media.quality_score >= 0.7)
        high_value = sum(1 for data in media_analysis.values() 
                        for media in data['media_info'] 
                        if media.value_score >= 0.7)
        
        print(f"⭐ Высокое качество: {high_quality} ({high_quality/total_analyzed*100:.1f}%)")
        print(f"💎 Высокая ценность: {high_value} ({high_value/total_analyzed*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main()) 