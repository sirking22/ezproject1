#!/usr/bin/env python3
"""
🧹 АВТОМАТИЧЕСКИЙ ПРОЦЕССОР ОЧИСТКИ БАЗЫ
Улучшает качество базы данных без LLM токенов
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from notion_client import AsyncClient
from datetime import datetime

class AutoCleanupProcessor:
    """Автоматический процессор для улучшения качества базы"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = "ad92a6e21485428c84de8587706b3be1"
        
        # Загружаем анализ данных
        self.analysis_data = {}
        try:
            with open("telegram_full_analysis.json", "r", encoding="utf-8") as f:
                analysis_list = json.load(f)
                self.analysis_data = {item["page_id"]: item for item in analysis_list}
                print(f"✅ Загружено {len(self.analysis_data)} записей для анализа")
        except FileNotFoundError:
            print("❌ Файл telegram_full_analysis.json не найден")
            return

        # Статистика обработки
        self.stats = {
            'processed': 0,
            'titles_cleaned': 0,
            'descriptions_cleaned': 0,
            'tags_added': 0,
            'garbage_removed': 0,
            'links_processed': 0,
            'files_categorized': 0
        }

    def clean_title(self, title: str) -> str:
        """Очищает название от мусора"""
        if not title:
            return title
            
        # Удаляем эмодзи в начале
        title = re.sub(r'^[📱📁🎯🔥⚡🧹🏷️💎🚀]+\s*', '', title)
        
        # Удаляем SaveAsBot спам
        title = re.sub(r'Спасибо, что пользуетесь.*?@SaveAsBot.*?\n*', '', title, flags=re.DOTALL)
        
        # Удаляем хэши и технические данные
        title = re.sub(r'[a-f0-9]{32,}', '', title)
        
        # Очищаем "📁 Файлы (N):" в начале
        title = re.sub(r'^📁\s*Файлы\s*\(\d+\):\s*', '', title)
        
        # Удаляем ссылки из названий
        if 'https://' in title and len(title) > 100:
            # Если название слишком длинное и содержит ссылки, берем часть до ссылки
            before_link = title.split('https://')[0].strip()
            if len(before_link) > 10:
                title = before_link
        
        # Обрезаем слишком длинные названия
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title.strip()

    def clean_description(self, description: str) -> str:
        """Очищает описание от мусора"""
        if not description:
            return description
            
        # Удаляем SaveAsBot спам
        description = re.sub(r'.*@SaveAsBot.*?\n?', '', description, flags=re.IGNORECASE)
        description = re.sub(r'Спасибо, что пользуетесь.*?ом\s*', '', description)
        
        # Удаляем технические списки файлов если они дублируют название
        if description.startswith('📁 Файлы'):
            lines = description.split('\n')
            clean_lines = []
            for line in lines:
                if not (line.startswith('•') and ('.jpg' in line or '.mp4' in line or '.pdf' in line)):
                    clean_lines.append(line)
            description = '\n'.join(clean_lines)
        
        # Удаляем хэши
        description = re.sub(r'[a-f0-9]{32,}', '', description)
        
        return description.strip()

    def extract_smart_tags(self, title: str, description: str, links: List[str]) -> List[str]:
        """Извлекает умные теги на основе контента"""
        tags = []
        content = f"{title} {description}".lower()
        
        # Теги по доменам
        for link in links:
            if 'instagram.com' in link:
                tags.extend(['Instagram', 'Социальные сети'])
                if 'reel' in link:
                    tags.append('Reels')
            elif 'youtube.com' in link or 'youtu.be' in link:
                tags.extend(['YouTube', 'Видео'])
            elif 'github.com' in link:
                tags.extend(['GitHub', 'Код'])
            elif 'figma.com' in link:
                tags.extend(['Figma', 'Дизайн'])
            elif 'yadi.sk' in link or 'yandex' in link:
                tags.append('Яндекс.Диск')
        
        # Теги по контенту
        if any(word in content for word in ['дизайн', 'ui', 'ux', 'figma', 'design']):
            tags.append('Дизайн')
        
        if any(word in content for word in ['код', 'программ', 'python', 'javascript', 'github']):
            tags.append('Код')
        
        if any(word in content for word in ['видео', 'youtube', 'смотреть', 'фильм']):
            tags.append('Видео')
        
        if any(word in content for word in ['фото', 'изображен', 'картинк', 'photo', 'image']):
            tags.append('Изображения')
        
        if any(word in content for word in ['аудио', 'музык', 'звук', 'голос', 'mp3']):
            tags.append('Аудио')
        
        if any(word in content for word in ['идея', 'мысль', 'концепт', 'план']):
            tags.append('Идеи')
        
        if any(word in content for word in ['бизнес', 'деньги', 'продаж', 'маркетинг']):
            tags.append('Бизнес')
        
        if any(word in content for word in ['обучен', 'урок', 'курс', 'learn']):
            tags.append('Обучение')
        
        # Удаляем дубликаты и возвращаем
        return list(set(tags))

    def is_garbage(self, analysis: Dict) -> bool:
        """Определяет является ли запись мусором"""
        title = analysis['current_title']
        description = analysis['current_description']
        
        # Слишком короткие названия
        if len(title.strip()) < 3:
            return True
        
        # Только хэши
        if re.match(r'^[a-f0-9\s\-_]+$', title):
            return True
        
        # Только SaveAsBot спам
        if 'SaveAsBot' in title and len(title.replace('SaveAsBot', '').strip()) < 10:
            return True
        
        # Битые символы
        if title.count('�') > 2:
            return True
        
        # Тестовые записи
        if any(word in title.lower() for word in ['test', 'тест', 'проверка']):
            return True
        
        return False

    async def process_single_record(self, page_id: str, analysis: Dict) -> bool:
        """Обрабатывает одну запись"""
        try:
            # Проверяем на мусор
            if self.is_garbage(analysis):
                print(f"🗑️ Удаляем мусор: {page_id}")
                await self.notion.pages.update(
                    page_id=page_id,
                    archived=True
                )
                self.stats['garbage_removed'] += 1
                return True
            
            # Очищаем данные
            original_title = analysis['current_title']
            original_desc = analysis['current_description']
            original_tags = analysis['current_tags']
            
            new_title = self.clean_title(original_title)
            new_desc = self.clean_description(original_desc)
            new_tags = self.extract_smart_tags(
                new_title, 
                new_desc, 
                analysis.get('extracted_links', [])
            )
            
            # Объединяем существующие и новые теги
            all_tags = list(set(original_tags + new_tags))
            
            # Проверяем нужны ли изменения
            needs_update = False
            properties = {}
            
            if new_title != original_title and new_title:
                properties['Name'] = {
                    'title': [{'text': {'content': new_title}}]
                }
                self.stats['titles_cleaned'] += 1
                needs_update = True
            
            if new_desc != original_desc and new_desc:
                properties['Описание'] = {
                    'rich_text': [{'text': {'content': new_desc}}]
                }
                self.stats['descriptions_cleaned'] += 1
                needs_update = True
            
            if len(all_tags) > len(original_tags):
                properties['Теги'] = {
                    'multi_select': [{'name': tag} for tag in all_tags]
                }
                self.stats['tags_added'] += len(all_tags) - len(original_tags)
                needs_update = True
            
            # Применяем изменения
            if needs_update:
                await self.notion.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                print(f"✅ Обновлено: {page_id[:8]}... ({len(properties)} изменений)")
            
            self.stats['processed'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обработки {page_id}: {e}")
            return False

    async def process_all_records(self):
        """Обрабатывает все записи"""
        print("🧹 АВТОМАТИЧЕСКАЯ ОЧИСТКА БАЗЫ ДАННЫХ")
        print("="*60)
        print(f"📊 Записей к обработке: {len(self.analysis_data)}")
        print()
        
        # Обрабатываем записи батчами
        batch_size = 10
        total_records = len(self.analysis_data)
        processed = 0
        
        for i in range(0, total_records, batch_size):
            batch_items = list(self.analysis_data.items())[i:i+batch_size]
            
            # Обрабатываем батч
            tasks = []
            for page_id, analysis in batch_items:
                task = self.process_single_record(page_id, analysis)
                tasks.append(task)
            
            # Ждем завершения батча
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            processed += len(batch_items)
            progress = (processed / total_records) * 100
            
            print(f"📊 Прогресс: {processed}/{total_records} ({progress:.1f}%)")
            
            # Небольшая пауза между батчами
            await asyncio.sleep(0.5)
        
        # Выводим финальную статистику
        self.print_final_stats()

    def print_final_stats(self):
        """Выводит финальную статистику"""
        print("\n" + "="*60)
        print("📊 ФИНАЛЬНАЯ СТАТИСТИКА ОЧИСТКИ")
        print("="*60)
        print(f"📄 Всего обработано: {self.stats['processed']}")
        print(f"🧹 Названий очищено: {self.stats['titles_cleaned']}")
        print(f"📝 Описаний очищено: {self.stats['descriptions_cleaned']}")
        print(f"🏷️ Тегов добавлено: {self.stats['tags_added']}")
        print(f"🗑️ Мусора удалено: {self.stats['garbage_removed']}")
        print()
        print("✅ АВТОМАТИЧЕСКАЯ ОЧИСТКА ЗАВЕРШЕНА!")
        
        # Сохраняем статистику
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats
        }
        
        with open('auto_cleanup_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        
        print("💾 Статистика сохранена в auto_cleanup_stats.json")

async def main():
    """Главная функция"""
    processor = AutoCleanupProcessor()
    if processor.analysis_data:
        await processor.process_all_records()
    else:
        print("❌ Нет данных для обработки")

if __name__ == "__main__":
    asyncio.run(main()) 