#!/usr/bin/env python3
"""
🚀 PRODUCT SYSTEM
Превращение обработки данных в регулярный продукт

КОНЦЕПЦИЯ ПРОДУКТА:
1. Автоматический мониторинг новых записей
2. Умная обработка с минимальными токенами
3. Веб-интерфейс для управления правилами
4. API для интеграции с другими системами
5. Аналитика и отчеты

КОМПОНЕНТЫ:
- Scheduler (планировщик обработки)
- Rules Engine (движок правил)
- Web Interface (веб-интерфейс)
- Analytics (аналитика)
- API Gateway (API шлюз)
"""

import os
import json
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from notion_client import AsyncClient

@dataclass
class ProcessingRule:
    """Правило обработки"""
    id: str
    name: str
    description: str
    pattern: str
    action: str
    enabled: bool = True
    priority: int = 1
    created_at: str = ""
    last_used: str = ""
    usage_count: int = 0

@dataclass
class ProcessingJob:
    """Задача обработки"""
    id: str
    type: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    records_processed: int = 0
    errors: List[str] = None
    results: Dict = None

class ProductSystem:
    """Система продукта для автоматической обработки"""
    
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = "ad92a6e21485428c84de8587706b3be1"
        
        # Состояние системы
        self.rules: List[ProcessingRule] = []
        self.jobs: List[ProcessingJob] = []
        self.analytics = {}
        
        # Конфигурация
        self.config = {
            'auto_processing': True,
            'schedule_interval': 60,  # минут
            'max_llm_tokens_per_day': 10000,
            'quality_threshold': 0.85,
            'backup_enabled': True
        }
        
        self._load_system_state()
        self._init_default_rules()

    def _load_system_state(self):
        """Загружает состояние системы"""
        try:
            with open('product_state.json', 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # Загружаем правила
            if 'rules' in state:
                self.rules = [ProcessingRule(**rule) for rule in state['rules']]
            
            # Загружаем задачи
            if 'jobs' in state:
                self.jobs = [ProcessingJob(**job) for job in state['jobs']]
            
            # Загружаем конфигурацию
            if 'config' in state:
                self.config.update(state['config'])
                
        except FileNotFoundError:
            print("ℹ️ Создается новое состояние системы")

    def _save_system_state(self):
        """Сохраняет состояние системы"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'rules': [asdict(rule) for rule in self.rules],
            'jobs': [asdict(job) for job in self.jobs],
            'config': self.config,
            'analytics': self.analytics
        }
        
        with open('product_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _init_default_rules(self):
        """Инициализирует правила по умолчанию"""
        if not self.rules:
            default_rules = [
                ProcessingRule(
                    id="remove_telegram_emoji",
                    name="Удаление 📱 эмодзи",
                    description="Удаляет 📱 из начала названий",
                    pattern="^📱\\s*",
                    action="replace:",
                    priority=1
                ),
                ProcessingRule(
                    id="clean_savebot_spam",
                    name="Очистка SaveAsBot",
                    description="Удаляет спам от SaveAsBot",
                    pattern=".*@SaveAsBot.*",
                    action="delete",
                    priority=2
                ),
                ProcessingRule(
                    id="extract_instagram_info",
                    name="Instagram контент",
                    description="Обрабатывает ссылки Instagram",
                    pattern="instagram\\.com",
                    action="tag:Instagram,Контент",
                    priority=3
                ),
                ProcessingRule(
                    id="extract_youtube_info", 
                    name="YouTube контент",
                    description="Обрабатывает ссылки YouTube",
                    pattern="youtube\\.com|youtu\\.be",
                    action="tag:YouTube,Видео",
                    priority=3
                ),
                ProcessingRule(
                    id="delete_low_weight",
                    name="Удаление мусора",
                    description="Удаляет записи с низкой весомостью",
                    pattern="weight<15",
                    action="delete",
                    priority=5
                )
            ]
            
            self.rules.extend(default_rules)
            self._save_system_state()

    async def start_scheduler(self):
        """Запускает планировщик автоматической обработки"""
        print("🕐 ЗАПУСК ПЛАНИРОВЩИКА АВТОМАТИЧЕСКОЙ ОБРАБОТКИ")
        print("="*60)
        
        # Настройка расписания
        schedule.every(self.config['schedule_interval']).minutes.do(
            lambda: asyncio.create_task(self.auto_process())
        )
        
        # Ежедневная аналитика
        schedule.every().day.at("09:00").do(
            lambda: asyncio.create_task(self.generate_daily_report())
        )
        
        # Еженедельная оптимизация правил
        schedule.every().sunday.at("02:00").do(
            lambda: asyncio.create_task(self.optimize_rules())
        )
        
        print(f"✅ Планировщик настроен:")
        print(f"   📊 Автообработка каждые {self.config['schedule_interval']} минут")
        print(f"   📈 Ежедневные отчеты в 09:00")
        print(f"   🔧 Оптимизация правил по воскресеньям")
        
        # Основной цикл
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)

    async def auto_process(self):
        """Автоматическая обработка новых записей"""
        job_id = f"auto_{int(time.time())}"
        job = ProcessingJob(
            id=job_id,
            type="auto_processing",
            status="running",
            created_at=datetime.now().isoformat(),
            started_at=datetime.now().isoformat(),
            errors=[]
        )
        
        self.jobs.append(job)
        
        try:
            print(f"\n🔄 АВТОМАТИЧЕСКАЯ ОБРАБОТКА - {datetime.now().strftime('%H:%M:%S')}")
            
            # Получаем новые записи
            new_records = await self._get_new_records()
            
            if not new_records:
                job.status = "completed"
                job.completed_at = datetime.now().isoformat()
                job.records_processed = 0
                print("ℹ️ Новых записей для обработки нет")
                return
            
            print(f"📥 Найдено новых записей: {len(new_records)}")
            
            # Применяем правила
            processed = await self._apply_rules_to_records(new_records)
            
            # Обновляем статистику
            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
            job.records_processed = processed
            job.results = {
                'processed': processed,
                'rules_applied': len([r for r in self.rules if r.enabled])
            }
            
            # Обновляем аналитику
            self._update_analytics(processed)
            
            print(f"✅ Обработано записей: {processed}")
            
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now().isoformat()
            job.errors.append(str(e))
            print(f"❌ Ошибка автообработки: {e}")
        
        finally:
            self._save_system_state()

    async def _get_new_records(self) -> List[Dict]:
        """Получает новые записи для обработки"""
        # Определяем время последней обработки
        last_job = None
        for job in reversed(self.jobs):
            if job.status == "completed" and job.type == "auto_processing":
                last_job = job
                break
        
        # Если это первый запуск, берем записи за последний час
        if not last_job:
            cutoff_time = datetime.now() - timedelta(hours=1)
        else:
            cutoff_time = datetime.fromisoformat(last_job.completed_at)
        
        # Здесь будет запрос к Notion API для получения новых записей
        # Пока возвращаем заглушку
        return []

    async def _apply_rules_to_records(self, records: List[Dict]) -> int:
        """Применяет правила к записям"""
        processed = 0
        
        for record in records:
            changes = {}
            
            # Применяем активные правила по приоритету
            for rule in sorted(self.rules, key=lambda r: r.priority):
                if not rule.enabled:
                    continue
                
                change = await self._apply_single_rule(rule, record)
                if change:
                    changes.update(change)
                    rule.usage_count += 1
                    rule.last_used = datetime.now().isoformat()
            
            # Применяем изменения к записи
            if changes:
                await self._update_notion_record(record['id'], changes)
                processed += 1
        
        return processed

    async def _apply_single_rule(self, rule: ProcessingRule, record: Dict) -> Optional[Dict]:
        """Применяет одно правило к записи"""
        import re
        
        content = f"{record.get('title', '')} {record.get('description', '')}"
        
        # Проверяем паттерн
        if re.search(rule.pattern, content, re.IGNORECASE):
            
            if rule.action.startswith("replace:"):
                replacement = rule.action.split(":", 1)[1]
                new_content = re.sub(rule.pattern, replacement, content)
                return {"title": new_content}
            
            elif rule.action == "delete":
                return {"delete": True}
            
            elif rule.action.startswith("tag:"):
                tags = rule.action.split(":", 1)[1].split(",")
                return {"tags": [tag.strip() for tag in tags]}
        
        return None

    async def _update_notion_record(self, page_id: str, changes: Dict):
        """Обновляет запись в Notion"""
        properties = {}
        
        if "title" in changes:
            properties["Name"] = {"title": [{"text": {"content": changes["title"]}}]}
        
        if "description" in changes:
            properties["Описание"] = {"rich_text": [{"text": {"content": changes["description"]}}]}
        
        if "tags" in changes:
            properties["Теги"] = {"multi_select": [{"name": tag} for tag in changes["tags"]]}
        
        if "delete" in changes:
            await self.notion.pages.update(page_id=page_id, archived=True)
        elif properties:
            await self.notion.pages.update(page_id=page_id, properties=properties)

    def _update_analytics(self, processed_count: int):
        """Обновляет аналитику"""
        today = datetime.now().date().isoformat()
        
        if 'daily_stats' not in self.analytics:
            self.analytics['daily_stats'] = {}
        
        if today not in self.analytics['daily_stats']:
            self.analytics['daily_stats'][today] = {
                'processed': 0,
                'rules_triggered': 0,
                'tokens_used': 0
            }
        
        self.analytics['daily_stats'][today]['processed'] += processed_count

    async def generate_daily_report(self):
        """Генерирует ежедневный отчет"""
        print("\n📊 ГЕНЕРАЦИЯ ЕЖЕДНЕВНОГО ОТЧЕТА")
        
        today = datetime.now().date().isoformat()
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
        
        today_stats = self.analytics.get('daily_stats', {}).get(today, {})
        yesterday_stats = self.analytics.get('daily_stats', {}).get(yesterday, {})
        
        report = {
            'date': today,
            'processed_today': today_stats.get('processed', 0),
            'processed_yesterday': yesterday_stats.get('processed', 0),
            'active_rules': len([r for r in self.rules if r.enabled]),
            'total_jobs': len(self.jobs),
            'failed_jobs': len([j for j in self.jobs if j.status == 'failed']),
            'top_rules': self._get_top_rules()
        }
        
        # Сохраняем отчет
        with open(f'daily_report_{today}.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Отчет сохранен: daily_report_{today}.json")

    def _get_top_rules(self) -> List[Dict]:
        """Получает топ правил по использованию"""
        return [
            {
                'name': rule.name,
                'usage_count': rule.usage_count,
                'last_used': rule.last_used
            }
            for rule in sorted(self.rules, key=lambda r: r.usage_count, reverse=True)[:5]
        ]

    async def optimize_rules(self):
        """Оптимизирует правила на основе статистики"""
        print("\n🔧 ОПТИМИЗАЦИЯ ПРАВИЛ")
        
        # Отключаем неиспользуемые правила
        for rule in self.rules:
            if rule.usage_count == 0 and rule.enabled:
                rule.enabled = False
                print(f"⚠️ Отключено неиспользуемое правило: {rule.name}")
        
        # Повышаем приоритет часто используемых правил
        for rule in sorted(self.rules, key=lambda r: r.usage_count, reverse=True)[:3]:
            if rule.priority > 1:
                rule.priority = max(1, rule.priority - 1)
                print(f"⬆️ Повышен приоритет правила: {rule.name}")
        
        self._save_system_state()
        print("✅ Оптимизация завершена")

    def create_web_interface(self):
        """Создает веб-интерфейс для управления"""
        web_config = {
            'title': 'Smart Content Processor',
            'description': 'Автоматическая обработка контента с ИИ',
            'features': [
                'Управление правилами обработки',
                'Мониторинг задач в реальном времени',
                'Аналитика и отчеты',
                'API для интеграции'
            ],
            'endpoints': {
                '/': 'Главная панель',
                '/rules': 'Управление правилами',
                '/jobs': 'Мониторинг задач',
                '/analytics': 'Аналитика',
                '/api/process': 'API обработки',
                '/api/rules': 'API правил'
            }
        }
        
        # Сохраняем конфигурацию веб-интерфейса
        with open('web_config.json', 'w', encoding='utf-8') as f:
            json.dump(web_config, f, ensure_ascii=False, indent=2)
        
        print("🌐 Конфигурация веб-интерфейса создана: web_config.json")

    def export_for_deployment(self):
        """Экспортирует систему для развертывания"""
        deployment_config = {
            'name': 'smart-content-processor',
            'version': '1.0.0',
            'description': 'Автоматическая обработка контента Telegram → Notion',
            'requirements': [
                'notion-client>=2.0.0',
                'schedule>=1.2.0',
                'fastapi>=0.100.0',
                'uvicorn>=0.20.0'
            ],
            'environment': {
                'NOTION_TOKEN': 'required',
                'DATABASE_ID': 'required',
                'DEEPSEEK_API_KEY': 'optional'
            },
            'docker': {
                'image': 'python:3.11-slim',
                'ports': ['8000:8000'],
                'volumes': ['./data:/app/data']
            },
            'scaling': {
                'min_instances': 1,
                'max_instances': 5,
                'cpu_threshold': 70,
                'memory_limit': '512MB'
            }
        }
        
        with open('deployment_config.json', 'w', encoding='utf-8') as f:
            json.dump(deployment_config, f, ensure_ascii=False, indent=2)
        
        print("🚀 Конфигурация развертывания создана: deployment_config.json")

async def main():
    """Главная функция"""
    system = ProductSystem()
    
    print("🚀 SMART CONTENT PROCESSOR - ПРОДУКТОВАЯ СИСТЕМА")
    print("="*60)
    
    # Создаем конфигурации
    system.create_web_interface()
    system.export_for_deployment()
    
    # Запускаем планировщик
    await system.start_scheduler()

if __name__ == "__main__":
    asyncio.run(main()) 