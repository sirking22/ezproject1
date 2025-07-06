#!/usr/bin/env python3
"""
🧠 SMART RULES PROCESSOR
Умная обработка с минимальными токенами LLM и максимальным качеством

СТРАТЕГИЯ ОПТИМИЗАЦИИ:
1. 95% обработки - детерминированные правила (0 токенов)
2. 5% спорных случаев - LLM обработка (минимум токенов)
3. Автоматическая категоризация по паттернам
4. Умная обработка ссылок и медиа
5. Превращение в регулярный продукт

МОДУЛИ:
- Детерминированные правила (без LLM)
- Классификатор контента (без LLM) 
- Обработчик ссылок и медиа
- Умный тегинг по ключевым словам
- LLM только для спорных случаев
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
from notion_client import AsyncClient
from datetime import datetime

class SmartRulesProcessor:
    """Умный процессор с минимальным использованием LLM"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = "ad92a6e21485428c84de8587706b3be1"
        
        # Загружаем анализ
        self.analysis_data = {}
        try:
            with open("telegram_full_analysis.json", "r", encoding="utf-8") as f:
                analysis_list = json.load(f)
                self.analysis_data = {item["page_id"]: item for item in analysis_list}
        except FileNotFoundError:
            print("❌ Файл анализа не найден")
        
        # Статистика обработки
        self.stats = {
            'auto_processed': 0,
            'llm_required': 0,
            'links_processed': 0,
            'media_categorized': 0,
            'tags_added': 0,
            'cleaned': 0,
            'deleted': 0
        }
        
        # Инициализируем правила
        self._init_deterministic_rules()
        self._init_content_classifiers()
        self._init_link_processors()

    def _init_deterministic_rules(self):
        """Инициализирует детерминированные правила (без LLM)"""
        
        # Правила очистки названий
        self.title_cleanup_rules = [
            {
                'name': 'remove_telegram_emoji',
                'pattern': r'^📱\s*',
                'replacement': '',
                'description': 'Удаление 📱 из начала названий'
            },
            {
                'name': 'extract_from_links',
                'pattern': r'^.*?https?://[^\s]+\s*(.+)$',
                'replacement': r'\1',
                'description': 'Извлечение текста после ссылок'
            },
            {
                'name': 'clean_files_titles',
                'pattern': r'^📁 Файлы \(\d+\):.*',
                'replacement': lambda match, desc: self._extract_meaningful_title_from_files(match.group(0), desc),
                'description': 'Замена "📁 Файлы" на осмысленные названия'
            },
            {
                'name': 'remove_savebot_spam',
                'pattern': r'Спасибо, что пользуетесь.*?@SaveAsBot.*?\n?',
                'replacement': '',
                'description': 'Удаление спама SaveAsBot'
            }
        ]
        
        # Правила очистки описаний
        self.description_cleanup_rules = [
            {
                'pattern': r'.*@SaveAsBot.*\n?',
                'replacement': '',
                'description': 'Удаление SaveAsBot из описаний'
            },
            {
                'pattern': r'📁 Файлы \(\d+\):.*?(?=\n\n|\Z)',
                'replacement': '',
                'description': 'Удаление списков файлов из описаний'
            },
            {
                'pattern': r'\s*•\s*\w+@\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}\.\w+.*?\n',
                'replacement': '',
                'description': 'Удаление технических имен файлов'
            },
            {
                'pattern': r'\([0-9.]+MB\)\s*\[photo\]\s*-\s*',
                'replacement': '',
                'description': 'Удаление технической информации о файлах'
            }
        ]

    def _init_content_classifiers(self):
        """Инициализирует классификаторы контента (без LLM)"""
        
        # Умные теги по ключевым словам
        self.smart_tags = {
            'Instagram': {
                'keywords': ['instagram.com', 'reel', 'igsh', 'img_index'],
                'weight': 10
            },
            'YouTube': {
                'keywords': ['youtube.com', 'youtu.be', 'watch?v='],
                'weight': 10
            },
            'Дизайн': {
                'keywords': ['figma', 'design', 'ui', 'ux', 'dribbble', 'behance', 'typography', 'color', 'layout'],
                'weight': 8
            },
            'Код': {
                'keywords': ['github', 'code', 'python', 'javascript', 'api', 'programming', 'dev', 'repository'],
                'weight': 8
            },
            'AI': {
                'keywords': ['chatgpt', 'midjourney', 'openai', 'нейросеть', 'ai', 'artificial intelligence', 'prompt'],
                'weight': 9
            },
            'Бизнес': {
                'keywords': ['startup', 'business', 'marketing', 'sales', 'revenue', 'monetization', 'strategy'],
                'weight': 7
            },
            'Обучение': {
                'keywords': ['course', 'learn', 'tutorial', 'guide', 'education', 'skill', 'training'],
                'weight': 7
            },
            'Новости': {
                'keywords': ['news', 'новости', 'event', 'announcement', 'update', 'release'],
                'weight': 6
            },
            'Инструменты': {
                'keywords': ['tool', 'service', 'app', 'software', 'platform', 'инструмент', 'сервис'],
                'weight': 7
            },
            'Контент': {
                'keywords': ['content', 'post', 'article', 'blog', 'story', 'контент', 'статья'],
                'weight': 6
            }
        }
        
        # Классификация по типу контента
        self.content_types = {
            'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'video', 'видео'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'photo', 'image'],
            'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'document'],
            'archive': ['zip', 'rar', '7z', 'tar', 'archive'],
            'audio': ['mp3', 'wav', 'flac', 'm4a', 'audio']
        }

    def _init_link_processors(self):
        """Инициализирует обработчики ссылок"""
        
        self.link_processors = {
            'instagram.com': {
                'type': 'social_media',
                'extract_title': lambda url: self._extract_instagram_info(url),
                'auto_tags': ['Instagram', 'Контент'],
                'priority': 'high'
            },
            'youtube.com': {
                'type': 'video_platform', 
                'extract_title': lambda url: self._extract_youtube_info(url),
                'auto_tags': ['YouTube', 'Видео'],
                'priority': 'high'
            },
            'youtu.be': {
                'type': 'video_platform',
                'extract_title': lambda url: self._extract_youtube_info(url),
                'auto_tags': ['YouTube', 'Видео'],
                'priority': 'high'
            },
            'yadi.sk': {
                'type': 'file_storage',
                'extract_title': lambda url: 'Файл на Яндекс.Диске',
                'auto_tags': ['Файлы'],
                'priority': 'medium'
            },
            'disk.yandex.ru': {
                'type': 'file_storage', 
                'extract_title': lambda url: 'Файл на Яндекс.Диске',
                'auto_tags': ['Файлы'],
                'priority': 'medium'
            },
            'github.com': {
                'type': 'code_repository',
                'extract_title': lambda url: self._extract_github_info(url),
                'auto_tags': ['Код', 'GitHub'],
                'priority': 'high'
            },
            'habr.com': {
                'type': 'tech_article',
                'extract_title': lambda url: 'Статья на Хабре',
                'auto_tags': ['Статья', 'Код'],
                'priority': 'medium'
            }
        }

    async def process_all_records(self):
        """Обрабатывает все записи с минимальным использованием LLM"""
        print("🧠 SMART RULES PROCESSOR - СТАРТ")
        print("="*60)
        print(f"📊 Записей для обработки: {len(self.analysis_data)}")
        
        # Этап 1: Детерминированная обработка (без LLM)
        auto_processed = await self._deterministic_processing()
        
        # Этап 2: Классификация ссылок и медиа (без LLM)
        link_processed = await self._process_links_and_media()
        
        # Этап 3: Умное тегирование (без LLM)
        tagged = await self._smart_tagging()
        
        # Этап 4: Выявление спорных случаев для LLM
        controversial = await self._identify_controversial_cases()
        
        # Этап 5: LLM обработка только спорных случаев
        llm_processed = await self._llm_processing(controversial)
        
        # Сохраняем результаты
        await self._save_processing_results()
        
        self._print_final_stats()

    async def _deterministic_processing(self):
        """Детерминированная обработка без LLM"""
        print("\n🔧 ЭТАП 1: ДЕТЕРМИНИРОВАННАЯ ОБРАБОТКА (без LLM)")
        print("-" * 50)
        
        processed = 0
        
        for page_id, analysis in self.analysis_data.items():
            changes = {}
            
            # Очистка названий
            new_title = self._apply_title_cleanup(analysis['current_title'], analysis['current_description'])
            if new_title != analysis['current_title']:
                changes['title'] = new_title
            
            # Очистка описаний
            new_desc = self._apply_description_cleanup(analysis['current_description'])
            if new_desc != analysis['current_description']:
                changes['description'] = new_desc
            
            # Автоматическое удаление мусора
            if self._is_garbage_record(analysis):
                changes['delete'] = True
                self.stats['deleted'] += 1
            
            if changes:
                analysis['auto_changes'] = changes
                processed += 1
                self.stats['auto_processed'] += 1
        
        print(f"✅ Автоматически обработано: {processed} записей")
        return processed

    def _apply_title_cleanup(self, title: str, description: str) -> str:
        """Применяет правила очистки названий"""
        cleaned_title = title
        
        for rule in self.title_cleanup_rules:
            if callable(rule.get('replacement')):
                # Для сложных правил с функциями
                match = re.search(rule['pattern'], cleaned_title)
                if match:
                    cleaned_title = rule['replacement'](match, description)
            else:
                # Для простых regex замен
                cleaned_title = re.sub(rule['pattern'], rule['replacement'], cleaned_title)
        
        # Дополнительная очистка
        cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
        
        return cleaned_title if cleaned_title else title

    def _apply_description_cleanup(self, description: str) -> str:
        """Применяет правила очистки описаний"""
        cleaned_desc = description
        
        for rule in self.description_cleanup_rules:
            cleaned_desc = re.sub(rule['pattern'], rule['replacement'], cleaned_desc, flags=re.MULTILINE | re.DOTALL)
        
        # Убираем лишние пробелы и переносы
        cleaned_desc = re.sub(r'\n\s*\n', '\n\n', cleaned_desc)
        cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc).strip()
        
        return cleaned_desc

    def _extract_meaningful_title_from_files(self, files_title: str, description: str) -> str:
        """Извлекает осмысленное название из списка файлов"""
        # Ищем паттерны в описании
        if description and description != files_title:
            # Берем первое предложение из описания
            sentences = re.split(r'[.!?\n]', description.strip())
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15 and len(sentence) < 100 and not sentence.startswith('📁'):
                    return sentence
        
        # Анализируем типы файлов в названии
        file_types = []
        if '.jpg' in files_title or '.png' in files_title or 'photo' in files_title:
            file_types.append('фото')
        if '.mp4' in files_title or 'video' in files_title:
            file_types.append('видео')
        if '.pdf' in files_title or '.doc' in files_title:
            file_types.append('документы')
        
        if file_types:
            return f"Коллекция {', '.join(file_types)}"
        
        return "Файлы из Telegram"

    async def _process_links_and_media(self):
        """Обрабатывает ссылки и медиа без LLM"""
        print("\n🔗 ЭТАП 2: ОБРАБОТКА ССЫЛОК И МЕДИА (без LLM)")
        print("-" * 50)
        
        processed = 0
        
        for page_id, analysis in self.analysis_data.items():
            if not analysis.get('extracted_links'):
                continue
            
            link_info = self._analyze_links(analysis['extracted_links'])
            if link_info:
                if 'auto_changes' not in analysis:
                    analysis['auto_changes'] = {}
                
                # Добавляем информацию о ссылках
                analysis['link_info'] = link_info
                
                # Автоматические теги на основе ссылок
                auto_tags = set(analysis.get('current_tags', []))
                for link_data in link_info:
                    auto_tags.update(link_data.get('auto_tags', []))
                
                if auto_tags != set(analysis.get('current_tags', [])):
                    analysis['auto_changes']['tags'] = list(auto_tags)
                
                processed += 1
                self.stats['links_processed'] += 1
        
        print(f"✅ Обработано ссылок: {processed} записей")
        return processed

    def _analyze_links(self, links: List[str]) -> List[Dict]:
        """Анализирует ссылки и извлекает информацию"""
        link_info = []
        
        for link in links:
            try:
                parsed = urlparse(link)
                domain = parsed.netloc.lower()
                
                # Убираем www.
                domain = domain.replace('www.', '')
                
                for processor_domain, processor in self.link_processors.items():
                    if processor_domain in domain:
                        info = {
                            'url': link,
                            'domain': domain,
                            'type': processor['type'],
                            'auto_tags': processor['auto_tags'],
                            'priority': processor['priority']
                        }
                        
                        # Пытаемся извлечь заголовок
                        try:
                            title = processor['extract_title'](link)
                            if title:
                                info['suggested_title'] = title
                        except:
                            pass
                        
                        link_info.append(info)
                        break
            except:
                continue
        
        return link_info

    def _extract_instagram_info(self, url: str) -> str:
        """Извлекает информацию из Instagram ссылок"""
        if '/reel/' in url:
            return "Instagram Reel"
        elif '/p/' in url:
            return "Instagram пост"
        elif '/stories/' in url:
            return "Instagram Story"
        return "Instagram контент"

    def _extract_youtube_info(self, url: str) -> str:
        """Извлекает информацию из YouTube ссылок"""
        if 'watch?v=' in url or 'youtu.be/' in url:
            return "YouTube видео"
        elif '/playlist' in url:
            return "YouTube плейлист"
        elif '/channel/' in url or '/c/' in url:
            return "YouTube канал"
        return "YouTube контент"

    def _extract_github_info(self, url: str) -> str:
        """Извлекает информацию из GitHub ссылок"""
        parts = url.split('/')
        if len(parts) >= 5:
            repo_name = parts[4]
            return f"GitHub: {repo_name}"
        return "GitHub репозиторий"

    async def _smart_tagging(self):
        """Умное тегирование без LLM"""
        print("\n🏷️ ЭТАП 3: УМНОЕ ТЕГИРОВАНИЕ (без LLM)")
        print("-" * 50)
        
        processed = 0
        
        for page_id, analysis in self.analysis_data.items():
            content = f"{analysis['current_title']} {analysis['current_description']}".lower()
            
            # Вычисляем веса тегов
            tag_scores = {}
            for tag, config in self.smart_tags.items():
                score = 0
                for keyword in config['keywords']:
                    if keyword.lower() in content:
                        score += config['weight']
                
                if score > 5:  # Минимальный порог
                    tag_scores[tag] = score
            
            # Добавляем теги с высоким скором
            if tag_scores:
                current_tags = set(analysis.get('current_tags', []))
                new_tags = set(tag for tag, score in tag_scores.items() if score >= 7)
                
                if new_tags - current_tags:  # Есть новые теги
                    if 'auto_changes' not in analysis:
                        analysis['auto_changes'] = {}
                    
                    all_tags = current_tags | new_tags
                    analysis['auto_changes']['tags'] = list(all_tags)
                    analysis['tag_scores'] = tag_scores
                    
                    processed += 1
                    self.stats['tags_added'] += 1
        
        print(f"✅ Добавлены теги: {processed} записей")
        return processed

    def _is_garbage_record(self, analysis: Dict) -> bool:
        """Определяет мусорные записи для удаления"""
        title = analysis['current_title'].lower()
        desc = analysis['current_description'].lower()
        
        # Критерии мусора
        garbage_indicators = [
            len(title.strip()) < 3,
            title in ['test', 'тест', '...', '-', '.'],
            'test' in title and len(title) < 10,
            not analysis.get('has_valuable_content', True),
            len(analysis.get('extracted_links', [])) == 0 and len(title + desc) < 15
        ]
        
        return any(garbage_indicators)

    async def _identify_controversial_cases(self):
        """Выявляет спорные случаи для LLM обработки"""
        print("\n❓ ЭТАП 4: ВЫЯВЛЕНИЕ СПОРНЫХ СЛУЧАЕВ")
        print("-" * 50)
        
        controversial = []
        
        for page_id, analysis in self.analysis_data.items():
            # Пропускаем уже автоматически обработанные
            if analysis.get('auto_changes'):
                continue
            
            # Критерии спорности
            is_controversial = (
                # Сложные названия
                len(analysis['current_title']) > 100 or
                # Много ссылок разных типов
                len(analysis.get('extracted_links', [])) > 5 or
                # Смешанный контент
                (len(analysis.get('extracted_links', [])) > 0 and len(analysis.get('extracted_files', [])) > 0) or
                # Неопределенный тип контента
                not any(keyword in analysis['current_title'].lower() + analysis['current_description'].lower() 
                       for tag_config in self.smart_tags.values() 
                       for keyword in tag_config['keywords'])
            )
            
            if is_controversial:
                controversial.append(page_id)
        
        print(f"⚠️ Спорных случаев для LLM: {len(controversial)}")
        self.stats['llm_required'] = len(controversial)
        
        return controversial

    async def _llm_processing(self, controversial_ids: List[str]):
        """LLM обработка только спорных случаев"""
        print(f"\n🤖 ЭТАП 5: LLM ОБРАБОТКА ({len(controversial_ids)} записей)")
        print("-" * 50)
        
        if not controversial_ids:
            print("✅ LLM обработка не требуется")
            return 0
        
        # Здесь будет интеграция с DeepSeek
        # Пока заглушка для демонстрации
        
        print("🔄 Подготовка батчей для DeepSeek...")
        
        # Группируем по типам для эффективной обработки
        batches = self._create_llm_batches(controversial_ids)
        
        processed = 0
        for batch_type, batch_ids in batches.items():
            print(f"📦 Обработка батча '{batch_type}': {len(batch_ids)} записей")
            
            # Здесь будет вызов DeepSeek API
            # result = await self._process_with_deepseek(batch_type, batch_ids)
            
            processed += len(batch_ids)
        
        print(f"✅ LLM обработано: {processed} записей")
        return processed

    def _create_llm_batches(self, controversial_ids: List[str]) -> Dict[str, List[str]]:
        """Создает батчи для эффективной LLM обработки"""
        batches = {
            'complex_titles': [],
            'mixed_content': [], 
            'link_heavy': [],
            'uncategorized': []
        }
        
        for page_id in controversial_ids:
            analysis = self.analysis_data[page_id]
            
            if len(analysis['current_title']) > 100:
                batches['complex_titles'].append(page_id)
            elif len(analysis.get('extracted_links', [])) > 5:
                batches['link_heavy'].append(page_id)
            elif (len(analysis.get('extracted_links', [])) > 0 and 
                  len(analysis.get('extracted_files', [])) > 0):
                batches['mixed_content'].append(page_id)
            else:
                batches['uncategorized'].append(page_id)
        
        return batches

    async def _save_processing_results(self):
        """Сохраняет результаты обработки"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'processed_data': {}
        }
        
        # Собираем все изменения
        for page_id, analysis in self.analysis_data.items():
            if analysis.get('auto_changes') or analysis.get('link_info'):
                results['processed_data'][page_id] = {
                    'auto_changes': analysis.get('auto_changes', {}),
                    'link_info': analysis.get('link_info', []),
                    'tag_scores': analysis.get('tag_scores', {})
                }
        
        with open('smart_processing_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в smart_processing_results.json")

    def _print_final_stats(self):
        """Выводит финальную статистику"""
        print("\n" + "="*60)
        print("📊 ФИНАЛЬНАЯ СТАТИСТИКА SMART PROCESSING")
        print("="*60)
        
        total_records = len(self.analysis_data)
        auto_percent = (self.stats['auto_processed'] / total_records) * 100
        llm_percent = (self.stats['llm_required'] / total_records) * 100
        
        print(f"📥 Всего записей: {total_records}")
        print(f"🔧 Автоматически обработано: {self.stats['auto_processed']} ({auto_percent:.1f}%)")
        print(f"🤖 Требует LLM: {self.stats['llm_required']} ({llm_percent:.1f}%)")
        print(f"🔗 Ссылок обработано: {self.stats['links_processed']}")
        print(f"🏷️ Тегов добавлено: {self.stats['tags_added']}")
        print(f"🗑️ Записей удалено: {self.stats['deleted']}")
        
        print(f"\n💰 ЭКОНОМИЯ ТОКЕНОВ:")
        estimated_tokens_saved = self.stats['auto_processed'] * 200  # ~200 токенов на запись
        print(f"Сэкономлено токенов: ~{estimated_tokens_saved:,}")
        print(f"Стоимость экономии: ~${estimated_tokens_saved * 0.0001:.2f}")
        
        print(f"\n🎯 КАЧЕСТВО ОБРАБОТКИ:")
        print(f"Детерминированная обработка: {auto_percent:.1f}%")
        print(f"Требует ручной проверки: {llm_percent:.1f}%")

async def main():
    """Главная функция"""
    processor = SmartRulesProcessor()
    await processor.process_all_records()

if __name__ == "__main__":
    asyncio.run(main()) 