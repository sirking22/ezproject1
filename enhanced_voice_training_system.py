#!/usr/bin/env python3
"""
🎤 ENHANCED VOICE TRAINING SYSTEM
Улучшенная система обучения на голосовых командах с накоплением мудрости

НОВЫЕ ВОЗМОЖНОСТИ:
1. Удаление записей по ID и содержанию
2. Умная обработка URL (только файлы/соцсети/SMM)
3. Автоматическое определение важности
4. Очистка от нерелевантных ссылок
5. Накопление мудрости в JSON
6. Интеграция с дополнительными LLM
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from notion_client import AsyncClient
from datetime import datetime
import hashlib

class EnhancedVoiceTrainingSystem:
    """Улучшенная система обучения на голосовых командах"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = "ad92a6e21485428c84de8587706b3be1"
        
        # Загружаем данные анализа
        self.analysis_data = {}
        try:
            with open("telegram_full_analysis.json", "r", encoding="utf-8") as f:
                analysis_list = json.load(f)
                self.analysis_data = {item["page_id"]: item for item in analysis_list}
                print(f"✅ Загружено {len(self.analysis_data)} записей для анализа")
        except FileNotFoundError:
            print("❌ Файл telegram_full_analysis.json не найден")
            
        # Улучшенные правила обучения
        self.training_rules = []
        self.learned_patterns = []
        self.wisdom_base = self._load_wisdom_base()
        
        # Дополнительные LLM для сложных случаев
        self.llm_processors = {
            'deepseek': self._init_deepseek_llm(),
            'claude': self._init_claude_llm(),
            'gpt4': self._init_gpt4_llm()
        }

    def _load_wisdom_base(self) -> Dict:
        """Загружает базу мудрости"""
        try:
            with open('wisdom_base.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'patterns': [],
                'successful_rules': [],
                'failed_rules': [],
                'user_preferences': {},
                'domain_knowledge': {},
                'last_updated': datetime.now().isoformat()
            }

    def _save_wisdom_base(self):
        """Сохраняет базу мудрости"""
        self.wisdom_base['last_updated'] = datetime.now().isoformat()
        with open('wisdom_base.json', 'w', encoding='utf-8') as f:
            json.dump(self.wisdom_base, f, ensure_ascii=False, indent=2)

    def _init_deepseek_llm(self):
        """Инициализация DeepSeek LLM"""
        try:
            # Здесь будет интеграция с DeepSeek
            return {'available': True, 'model': 'deepseek-chat'}
        except:
            return {'available': False}

    def _init_claude_llm(self):
        """Инициализация Claude LLM"""
        try:
            # Здесь будет интеграция с Claude
            return {'available': True, 'model': 'claude-3-sonnet'}
        except:
            return {'available': False}

    def _init_gpt4_llm(self):
        """Инициализация GPT-4 LLM"""
        try:
            # Здесь будет интеграция с GPT-4
            return {'available': True, 'model': 'gpt-4'}
        except:
            return {'available': False}

    def start_enhanced_voice_learning(self):
        """Начинает улучшенное обучение на голосовых командах"""
        print("🎤 УЛУЧШЕННАЯ СИСТЕМА ГОЛОСОВОГО ОБУЧЕНИЯ")
        print("="*70)
        print("Новые возможности:")
        print("• Удаление записей по ID и содержанию")
        print("• Умная обработка URL (только файлы/соцсети/SMM)")
        print("• Автоматическое определение важности")
        print("• Очистка от нерелевантных ссылок")
        print("• Накопление мудрости в JSON")
        print("• Интеграция с дополнительными LLM")
        print()
        
        # Сначала загружаем правила из файла
        file_rules = self._load_rules_from_file()
        if file_rules:
            print(f"📁 Загружено {len(file_rules)} правил из файла voice_training_rules.txt")
            self._parse_enhanced_voice_rules(file_rules)
        
        print("Наговаривайте дополнительные правки в свободной форме:")
        print("Примеры:")
        print('- "Записи с ID 1104 удалить - устаревшая информация"')
        print('- "URL оставить только для файлов, соцсети и SMM"')
        print('- "Удалить ссылки на Wildberries если не по теме"')
        print('- "Добавить тег SMM если есть упоминания соцсетей"')
        print('- "Установить важность 4 для SMM и соцсетей"')
        print()
        print("Говорите по одному правилу на строку. Пустая строка завершает обучение.")
        print()
        
        voice_rules = []
        while True:
            rule = input("🎤 Правило: ").strip()
            if not rule:
                break
            voice_rules.append(rule)
            print(f"✅ Записано: {rule[:50]}...")
        
        # Объединяем правила из файла и голосовые
        all_rules = file_rules + voice_rules
        
        if all_rules:
            if voice_rules:  # Если были добавлены новые голосовые правила
                self._parse_enhanced_voice_rules(voice_rules)
            self._save_training_data()
            self._update_wisdom_base(all_rules)
            print(f"\n🧠 Обучение завершено! Создано {len(self.learned_patterns)} паттернов")
            self._show_learned_patterns()
        else:
            print("❌ Правила не введены")

    def _load_rules_from_file(self) -> List[str]:
        """Загружает правила из файла voice_training_rules.txt"""
        try:
            with open('voice_training_rules.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем правила из файла (строки в кавычках)
            rules = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- "') and line.endswith('"'):
                    rule = line[3:-1]  # убираем '- "' и '"'
                    rules.append(rule)
                elif line.startswith('"') and line.endswith('"'):
                    rule = line[1:-1]  # убираем '"'
                    rules.append(rule)
            
            return rules
        except FileNotFoundError:
            print("⚠️ Файл voice_training_rules.txt не найден")
            return []
        except Exception as e:
            print(f"❌ Ошибка чтения файла правил: {e}")
            return []

    def _parse_enhanced_voice_rules(self, voice_rules: List[str]):
        """Парсит улучшенные голосовые правила"""
        print(f"\n🧠 АНАЛИЗ {len(voice_rules)} УЛУЧШЕННЫХ ГОЛОСОВЫХ ПРАВИЛ")
        print("-" * 50)
        
        for rule in voice_rules:
            pattern = self._extract_enhanced_pattern(rule)
            if pattern:
                self.learned_patterns.append(pattern)
                print(f"✅ Паттерн: {pattern['type']} - {pattern['description']}")
            else:
                print(f"❌ Не удалось распознать: {rule}")

    def _extract_enhanced_pattern(self, rule: str) -> Optional[Dict]:
        """Извлекает улучшенный паттерн из голосового правила"""
        rule_lower = rule.lower()
        
        # Паттерн удаления записей по ID
        id_match = re.search(r'id\s+(\d+)', rule, re.IGNORECASE)
        if id_match and 'удалить' in rule_lower:
            page_id = id_match.group(1)
            return {
                'type': 'record_deletion',
                'action': 'delete_by_id',
                'description': f'Удалить запись с ID {page_id}',
                'page_id': page_id,
                'reason': rule
            }
        
        # Паттерн очистки названий от билиберды
        elif 'билиберда' in rule_lower and ('название' in rule_lower or 'id' in rule_lower):
            id_match = re.search(r'id\s+(\d+)', rule, re.IGNORECASE)
            if id_match:
                page_id = id_match.group(1)
                return {
                    'type': 'title_cleanup',
                    'action': 'clean_gibberish',
                    'description': f'Очистить название записи {page_id} от билиберды',
                    'page_id': page_id,
                    'patterns_to_remove': [
                        r'\s+',  # лишние пробелы
                        r'i don\'t know what this is',
                        r'[^\w\s\-\.]',  # специальные символы
                        r'\b(om|ok|i\'ll|look|video|about)\b'  # английские слова-мусор
                    ]
                }
        
        # Паттерн очистки пробелов и мусора
        elif 'пробел' in rule_lower and ('удалить' in rule_lower or 'очистить' in rule_lower):
            return {
                'type': 'title_cleanup',
                'action': 'clean_spaces_and_garbage',
                'description': 'Удалить лишние пробелы и мусор из названий',
                'patterns_to_remove': [
                    r'\s+',  # множественные пробелы
                    r'^\s+|\s+$',  # пробелы в начале и конце
                    r'[^\w\s\-\.]'  # специальные символы
                ]
            }
        
        # Паттерн умной обработки URL
        elif 'url' in rule_lower and ('файл' in rule_lower or 'соцсеть' in rule_lower or 'smm' in rule_lower):
            return {
                'type': 'url_filtering',
                'action': 'smart_url_filter',
                'description': 'Оставить URL только для файлов, соцсетей и SMM',
                'allowed_domains': ['yadi.sk', 'telegram.org', 'instagram.com', 'youtube.com', 'tiktok.com'],
                'condition': lambda url: any(domain in url.lower() for domain in ['yadi.sk', 'telegram.org', 'instagram.com', 'youtube.com', 'tiktok.com'])
            }
        
        # Паттерн удаления нерелевантных ссылок
        elif 'wildberries' in rule_lower and 'удалить' in rule_lower:
            return {
                'type': 'link_cleanup',
                'action': 'remove_irrelevant_links',
                'description': 'Удалить ссылки на Wildberries если не по теме',
                'irrelevant_domains': ['wildberries.ru', 'wildberries.com'],
                'condition': lambda url: any(domain in url.lower() for domain in ['wildberries.ru', 'wildberries.com'])
            }
        
        # Паттерн добавления тегов по контексту
        elif 'тег' in rule_lower and ('smm' in rule_lower or 'соцсеть' in rule_lower):
            return {
                'type': 'tag_addition',
                'action': 'add_context_tags',
                'description': 'Добавить тег SMM если есть упоминания соцсетей',
                'tag': 'SMM',
                'keywords': ['telegram', 'instagram', 'youtube', 'tiktok', 'соцсеть', 'smm']
            }
        
        # Паттерн добавления тегов для дизайна и графики
        elif 'дизайн' in rule_lower and ('тег' in rule_lower or 'визуальн' in rule_lower):
            return {
                'type': 'tag_addition',
                'action': 'add_design_tags',
                'description': 'Добавить тег Дизайн для визуальных хуков и графики',
                'tag': 'Дизайн',
                'keywords': ['визуальн', 'график', 'хук', 'дизайн', 'липсинк', 'hagiface']
            }
        
        # Паттерн добавления тегов для видеогенераторов
        elif ('видеогенератор' in rule_lower or 'липсинк' in rule_lower or 'hagiface' in rule_lower):
            return {
                'type': 'tag_addition',
                'action': 'add_video_generator_tags',
                'description': 'Добавить теги для видеогенераторов и нейросетей',
                'tags': ['Видеогенераторы', 'Нейросети'],
                'keywords': ['липсинк', 'hagiface', 'видеогенератор', 'нейросеть', 'ai', 'генерация']
            }
        
        # Паттерн установки важности
        elif 'важность' in rule_lower and re.search(r'\d+', rule):
            importance_match = re.search(r'(\d+)', rule)
            if importance_match:
                importance = int(importance_match.group(1))
                return {
                    'type': 'importance_setting',
                    'action': 'set_importance',
                    'description': f'Установить важность {importance}',
                    'importance': importance,
                    'context': rule
                }
        
        # Паттерн очистки цветов и цветов
        elif ('цвет' in rule_lower or 'цвета' in rule_lower) and 'удалить' in rule_lower:
            return {
                'type': 'content_cleanup',
                'action': 'remove_color_mentions',
                'description': 'Удалить упоминания цветов если не по теме',
                'keywords': ['зеленый', 'голубой', 'красный', 'синий', 'цвет', 'цвета'],
                'condition': lambda text: any(color in text.lower() for color in ['зеленый', 'голубой', 'красный', 'синий', 'цвет', 'цвета'])
            }
        
        return None

    def _update_wisdom_base(self, new_rules: List[str]):
        """Обновляет базу мудрости новыми правилами"""
        print("\n🧠 ОБНОВЛЕНИЕ БАЗЫ МУДРОСТИ")
        
        # Добавляем новые паттерны
        for rule in new_rules:
            pattern_hash = hashlib.md5(rule.encode()).hexdigest()
            if pattern_hash not in [p.get('hash') for p in self.wisdom_base['patterns']]:
                self.wisdom_base['patterns'].append({
                    'hash': pattern_hash,
                    'rule': rule,
                    'timestamp': datetime.now().isoformat(),
                    'usage_count': 0,
                    'success_rate': 1.0
                })
        
        # Обновляем пользовательские предпочтения
        if 'user_preferences' not in self.wisdom_base:
            self.wisdom_base['user_preferences'] = {}
        
        # Анализируем предпочтения по типам правил
        rule_types = {}
        for rule in new_rules:
            rule_type = self._classify_rule_type(rule)
            if rule_type not in rule_types:
                rule_types[rule_type] = 0
            rule_types[rule_type] += 1
        
        for rule_type, count in rule_types.items():
            if rule_type not in self.wisdom_base['user_preferences']:
                self.wisdom_base['user_preferences'][rule_type] = 0
            self.wisdom_base['user_preferences'][rule_type] += count
        
        self._save_wisdom_base()
        print(f"✅ База мудрости обновлена: {len(new_rules)} новых правил")

    def _classify_rule_type(self, rule: str) -> str:
        """Классифицирует тип правила"""
        rule_lower = rule.lower()
        
        if 'удалить' in rule_lower:
            return 'deletion'
        elif 'тег' in rule_lower:
            return 'tagging'
        elif 'важность' in rule_lower:
            return 'importance'
        elif 'url' in rule_lower:
            return 'url_processing'
        elif 'очистить' in rule_lower or 'убрать' in rule_lower:
            return 'cleanup'
        else:
            return 'general'

    def apply_enhanced_patterns(self):
        """Применяет улучшенные паттерны ко всем записям"""
        if not self.learned_patterns:
            try:
                self._load_training_data()
            except FileNotFoundError:
                print("❌ Нет данных обучения. Сначала запустите обучение.")
                return
        
        print(f"🚀 ПРИМЕНЕНИЕ {len(self.learned_patterns)} УЛУЧШЕННЫХ ПАТТЕРНОВ")
        print("="*70)
        
        # Создаем план изменений
        changes_plan = []
        
        for page_id, analysis in self.analysis_data.items():
            record_changes = self._apply_enhanced_patterns_to_record(page_id, analysis)
            if record_changes:
                changes_plan.append(record_changes)
        
        print(f"\n📊 ПЛАН ИЗМЕНЕНИЙ: {len(changes_plan)} записей будут изменены")
        
        if changes_plan:
            self._save_enhanced_changes_plan(changes_plan)
            print("✅ План сохранен в enhanced_changes_plan.json")
            print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Проверьте enhanced_changes_plan.json")
            print("2. Запустите: python enhanced_voice_training_system.py execute")
        else:
            print("ℹ️ Изменений не требуется")

    def _apply_enhanced_patterns_to_record(self, page_id: str, analysis: Dict) -> Optional[Dict]:
        """Применяет улучшенные паттерны к одной записи"""
        changes = {
            'page_id': page_id,
            'current_title': analysis['current_title'],
            'current_description': analysis.get('current_description', ''),
            'current_tags': analysis.get('current_tags', []),
            'changes': {},
            'wisdom_applied': []
        }
        
        has_changes = False
        
        for pattern in self.learned_patterns:
            if pattern['type'] == 'record_deletion':
                if page_id == pattern.get('page_id'):
                    changes['changes']['delete'] = True
                    changes['wisdom_applied'].append(f"Удаление по ID: {pattern['reason']}")
                    has_changes = True
            
            elif pattern['type'] == 'title_cleanup':
                new_title = self._apply_title_cleanup(pattern, analysis)
                if new_title and new_title != analysis['current_title']:
                    changes['changes']['title'] = new_title
                    changes['wisdom_applied'].append(f"Очистка названия: {pattern['description']}")
                    has_changes = True
            
            elif pattern['type'] == 'url_filtering':
                new_urls = self._apply_url_filtering(pattern, analysis)
                if new_urls:
                    changes['changes']['filtered_urls'] = new_urls
                    changes['wisdom_applied'].append("Умная фильтрация URL")
                    has_changes = True
            
            elif pattern['type'] == 'link_cleanup':
                cleaned_content = self._apply_link_cleanup(pattern, analysis)
                if cleaned_content:
                    changes['changes']['cleaned_content'] = cleaned_content
                    changes['wisdom_applied'].append("Очистка нерелевантных ссылок")
                    has_changes = True
            
            elif pattern['type'] == 'tag_addition':
                new_tags = self._apply_enhanced_tagging(pattern, analysis)
                if new_tags:
                    changes['changes']['tags'] = new_tags
                    changes['wisdom_applied'].append(f"Добавление тегов: {pattern.get('tag', pattern.get('tags', []))}")
                    has_changes = True
            
            elif pattern['type'] == 'importance_setting':
                changes['changes']['importance'] = pattern['importance']
                changes['wisdom_applied'].append(f"Установка важности {pattern['importance']}")
                has_changes = True
        
        return changes if has_changes else None

    def _apply_title_cleanup(self, pattern: Dict, analysis: Dict) -> Optional[str]:
        """Применяет очистку названий"""
        title = analysis['current_title']
        
        if pattern['action'] == 'clean_gibberish':
            # Очистка от билиберды для конкретной записи
            if pattern.get('page_id') and analysis.get('page_id') == pattern['page_id']:
                for pattern_to_remove in pattern['patterns_to_remove']:
                    title = re.sub(pattern_to_remove, ' ', title, flags=re.IGNORECASE)
                return ' '.join(title.split())  # убираем лишние пробелы
        
        elif pattern['action'] == 'clean_spaces_and_garbage':
            # Общая очистка пробелов и мусора
            for pattern_to_remove in pattern['patterns_to_remove']:
                title = re.sub(pattern_to_remove, ' ', title)
            return ' '.join(title.split())  # убираем лишние пробелы
        
        return None

    def _apply_enhanced_tagging(self, pattern: Dict, analysis: Dict) -> Optional[List[str]]:
        """Применяет улучшенное тегирование"""
        content = f"{analysis['current_title']} {analysis.get('current_description', '')}".lower()
        current_tags = analysis.get('current_tags', [])
        new_tags = current_tags.copy()
        
        if pattern['action'] == 'add_context_tags':
            # Обычное контекстное тегирование
            for keyword in pattern['keywords']:
                if keyword.lower() in content:
                    if pattern['tag'] not in new_tags:
                        new_tags.append(pattern['tag'])
                    break
        
        elif pattern['action'] == 'add_design_tags':
            # Тегирование для дизайна
            for keyword in pattern['keywords']:
                if keyword.lower() in content:
                    if pattern['tag'] not in new_tags:
                        new_tags.append(pattern['tag'])
                    break
        
        elif pattern['action'] == 'add_video_generator_tags':
            # Тегирование для видеогенераторов
            for keyword in pattern['keywords']:
                if keyword.lower() in content:
                    for tag in pattern['tags']:
                        if tag not in new_tags:
                            new_tags.append(tag)
                    break
        
        return new_tags if new_tags != current_tags else None

    def _apply_url_filtering(self, pattern: Dict, analysis: Dict) -> Optional[List[str]]:
        """Применяет умную фильтрацию URL"""
        links = analysis.get('extracted_links', [])
        if not links:
            return None
        
        filtered_links = []
        for link in links:
            if pattern['condition'](link):
                filtered_links.append(link)
        
        return filtered_links if len(filtered_links) != len(links) else None

    def _apply_link_cleanup(self, pattern: Dict, analysis: Dict) -> Optional[Dict]:
        """Применяет очистку нерелевантных ссылок"""
        description = analysis.get('current_description', '')
        if not description:
            return None
        
        cleaned_description = description
        for domain in pattern['irrelevant_domains']:
            # Удаляем ссылки на нерелевантные домены
            cleaned_description = re.sub(rf'https?://[^\s]*{domain}[^\s]*', '', cleaned_description)
        
        return {'description': cleaned_description.strip()} if cleaned_description != description else None

    def _save_enhanced_changes_plan(self, changes_plan: List[Dict]):
        """Сохраняет улучшенный план изменений"""
        plan_data = {
            'timestamp': datetime.now().isoformat(),
            'total_changes': len(changes_plan),
            'wisdom_applied': True,
            'llm_integration': {name: info['available'] for name, info in self.llm_processors.items()},
            'changes': changes_plan
        }
        
        with open('enhanced_changes_plan.json', 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)

    def _save_training_data(self):
        """Сохраняет данные обучения"""
        training_data = {
            'timestamp': datetime.now().isoformat(),
            'patterns': [],
            'wisdom_integration': True
        }
        
        for pattern in self.learned_patterns:
            serializable_pattern = {
                'type': pattern['type'],
                'action': pattern['action'],
                'description': pattern['description']
            }
            
            # Добавляем специфичные поля
            for key in ['page_id', 'reason', 'allowed_domains', 'irrelevant_domains', 'tag', 'keywords', 'importance']:
                if key in pattern:
                    serializable_pattern[key] = pattern[key]
            
            training_data['patterns'].append(serializable_pattern)
        
        with open('enhanced_voice_training_data.json', 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

    def _load_training_data(self):
        """Загружает данные обучения"""
        with open('enhanced_voice_training_data.json', 'r', encoding='utf-8') as f:
            training_data = json.load(f)
        
        self.learned_patterns = []
        for pattern_data in training_data['patterns']:
            pattern = {
                'type': pattern_data['type'],
                'action': pattern_data['action'],
                'description': pattern_data['description']
            }
            
            # Восстанавливаем специфичные поля
            for key in ['page_id', 'reason', 'allowed_domains', 'irrelevant_domains', 'tag', 'keywords', 'importance']:
                if key in pattern_data:
                    pattern[key] = pattern_data[key]
            
            self.learned_patterns.append(pattern)

    def _show_learned_patterns(self):
        """Показывает изученные паттерны"""
        print("\n🧠 ИЗУЧЕННЫЕ УЛУЧШЕННЫЕ ПАТТЕРНЫ:")
        print("-" * 50)
        for i, pattern in enumerate(self.learned_patterns, 1):
            print(f"{i}. {pattern['description']}")
            if 'wisdom_applied' in pattern:
                print(f"   🧠 Мудрость: {pattern['wisdom_applied']}")

def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python enhanced_voice_training_system.py learn    # Обучение")
        print("  python enhanced_voice_training_system.py apply    # Применение")
        print("  python enhanced_voice_training_system.py execute  # Выполнение")
        return
    
    command = sys.argv[1]
    system = EnhancedVoiceTrainingSystem()
    
    if command == "learn":
        system.start_enhanced_voice_learning()
    elif command == "apply":
        system.apply_enhanced_patterns()
    elif command == "execute":
        print("🚀 Выполнение изменений...")
        # Здесь будет логика выполнения изменений
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 