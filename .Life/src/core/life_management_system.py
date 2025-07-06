#!/usr/bin/env python3
"""
Центральная система управления жизнью
Объединяет Todoist, Notion, Telegram и LLM
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ..integrations.todoist_integration import TodoistIntegration, TaskPriority as TodoistPriority
# from ..integrations.calendar_integration import GoogleCalendarIntegration  # Временно отключено
from ..notion.core import NotionService
from ..telegram.enhanced_bot import EnhancedTelegramBot
try:
    from ..agents.master_agent import MasterAgent
except ImportError:
    class MasterAgent:
        def __init__(self):
            pass
from ..config.environment import config

logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Заглушка для событий календаря"""
    id: str
    title: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class GoogleCalendarIntegration:
    """Заглушка для интеграции с календарем"""
    
    async def initialize(self):
        logger.info("Google Calendar интеграция отключена (заглушка)")
        return True
    
    async def create_event(self, title: str, **kwargs):
        logger.info(f"Создание события в календаре (заглушка): {title}")
        return CalendarEvent(id="stub", title=title)
    
    async def get_today_events(self):
        return []
    
    async def get_week_events(self):
        return []
    
    async def sync_with_todoist(self, todoist_integration):
        logger.info("Синхронизация с Todoist (заглушка)")
    
    async def cleanup(self):
        pass

@dataclass
class LifeMetrics:
    """Метрики жизни"""
    tasks_completed_today: int = 0
    tasks_overdue: int = 0
    habits_streak: int = 0
    reflections_count: int = 0
    productivity_score: float = 0.0
    mood_trend: str = "neutral"
    energy_level: int = 5
    focus_time: int = 0

class LifeManagementSystem:
    """Центральная система управления жизнью"""
    
    def __init__(self):
        # Инициализация всех интеграций
        self.todoist = TodoistIntegration(config.TODOIST_API_TOKEN)
        self.calendar = GoogleCalendarIntegration()
        self.notion = NotionService()
        self.telegram_bot = EnhancedTelegramBot()
        self.master_agent = MasterAgent()
        
        # Состояние системы
        self.is_initialized = False
        self.metrics = LifeMetrics()
        self.user_preferences = {}
        
    async def initialize(self):
        """Инициализация всей системы"""
        try:
            logger.info("🚀 Инициализация Life Management System...")
            
            # Инициализируем все компоненты
            await self.todoist.initialize()
            await self.calendar.initialize()
            await self.notion.initialize()
            await self.telegram_bot.initialize()
            
            # Загружаем пользовательские настройки
            await self._load_user_preferences()
            
            # Первоначальная синхронизация
            await self._initial_sync()
            
            self.is_initialized = True
            logger.info("✅ Life Management System инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации системы: {e}")
            raise
    
    async def _load_user_preferences(self):
        """Загрузка пользовательских настроек"""
        try:
            # Пока используем базовые настройки
            self.user_preferences = {
                "morning_routine": ["meditation", "planning", "exercise"],
                "evening_routine": ["reflection", "planning_next_day", "reading"],
                "productivity_focus": ["deep_work", "breaks", "review"],
                "health_goals": ["sleep", "exercise", "nutrition"],
                "learning_goals": ["reading", "courses", "projects"]
            }
            logger.info("Пользовательские настройки загружены")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
    
    async def _initial_sync(self):
        """Первоначальная синхронизация всех систем"""
        try:
            logger.info("🔄 Начинаю первоначальную синхронизацию...")
            
            # Синхронизация Todoist ↔ Calendar
            await self.calendar.sync_with_todoist(self.todoist)
            
            # Синхронизация с Notion
            await self._sync_with_notion()
            
            logger.info("✅ Синхронизация завершена")
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации: {e}")
    
    async def _sync_with_notion(self):
        """Синхронизация с Notion"""
        try:
            # Получаем задачи из Todoist
            todoist_tasks = await self.todoist.get_tasks()
            
            # Синхронизируем с Notion
            for task in todoist_tasks:
                # Проверяем, есть ли уже в Notion
                # Если нет - создаем
                pass
                
        except Exception as e:
            logger.error(f"Ошибка синхронизации с Notion: {e}")
    
    async def create_quick_task(self, task_text: str, priority: str = "normal",
                               due_date: Optional[datetime] = None,
                               sync_all: bool = True) -> Dict[str, Any]:
        """Быстрое создание задачи во всех системах"""
        try:
            result = {
                "todoist": None,
                "notion": None,
                "calendar": None,
                "success": False
            }
            
            # Создаем в Todoist
            todoist_priority = getattr(TodoistPriority, priority.upper(), TodoistPriority.NORMAL)
            todoist_task = await self.todoist.create_task(
                content=task_text,
                priority=todoist_priority,
                due_date=due_date
            )
            
            if todoist_task:
                result["todoist"] = todoist_task
                
                # Синхронизируем с другими системами
                if sync_all:
                    # Создаем в Notion
                    try:
                        notion_task = await self.notion.create_task({
                            "name": task_text,
                            "status": "To Do",
                            "priority": priority,
                            "due_date": due_date.isoformat() if due_date else None
                        })
                        result["notion"] = notion_task
                    except Exception as e:
                        logger.error(f"Ошибка создания в Notion: {e}")
                    
                    # Создаем в календаре (если есть дедлайн)
                    if due_date:
                        try:
                            calendar_event = await self.calendar.create_event(
                                title=f"Задача: {task_text}",
                                description="Создано через Life Management System",
                                start_time=due_date,
                                end_time=due_date + timedelta(hours=1)
                            )
                            result["calendar"] = calendar_event
                        except Exception as e:
                            logger.error(f"Ошибка создания в календаре: {e}")
                
                result["success"] = True
                logger.info(f"Задача создана: {task_text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_daily_overview(self) -> Dict[str, Any]:
        """Получение обзора дня"""
        try:
            # Получаем данные из всех систем
            today_tasks = await self.todoist.get_daily_tasks()
            overdue_tasks = await self.todoist.get_overdue_tasks()
            today_events = await self.calendar.get_today_events()
            
            # Обновляем метрики
            self.metrics.tasks_completed_today = len([t for t in today_tasks if t.completed_at])
            self.metrics.tasks_overdue = len(overdue_tasks)
            
            overview = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tasks": {
                    "today": len(today_tasks),
                    "completed": self.metrics.tasks_completed_today,
                    "overdue": self.metrics.tasks_overdue,
                    "pending": len(today_tasks) - self.metrics.tasks_completed_today
                },
                "events": {
                    "today": len(today_events),
                    "upcoming": [e for e in today_events if e.start_time > datetime.now()]
                },
                "metrics": self.metrics,
                "recommendations": await self._generate_recommendations()
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Ошибка получения обзора дня: {e}")
            return {"error": str(e)}
    
    async def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций на основе данных"""
        recommendations = []
        
        # Анализируем метрики
        if self.metrics.tasks_overdue > 3:
            recommendations.append("⚠️ Много просроченных задач. Рекомендуется пересмотр приоритетов.")
        
        if self.metrics.tasks_completed_today < 2:
            recommendations.append("📝 Мало выполненных задач. Попробуйте разбить большие задачи на мелкие.")
        
        if self.metrics.energy_level < 4:
            recommendations.append("🔋 Низкий уровень энергии. Рекомендуется перерыв или легкая активность.")
        
        if not recommendations:
            recommendations.append("🎉 Отличный день! Продолжайте в том же духе.")
        
        return recommendations
    
    async def create_morning_routine(self) -> Dict[str, Any]:
        """Создание утреннего ритуала"""
        try:
            routine_tasks = []
            
            # Создаем задачи утреннего ритуала
            morning_tasks = [
                "🧘 Медитация (10 минут)",
                "📝 Планирование дня",
                "💪 Легкая зарядка",
                "📖 Чтение (15 минут)"
            ]
            
            for task in morning_tasks:
                result = await self.create_quick_task(
                    task_text=task,
                    priority="high",
                    due_date=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                )
                routine_tasks.append(result)
            
            # Создаем событие в календаре
            calendar_event = await self.calendar.create_event(
                title="🌅 Утренний ритуал",
                description="Время для себя и планирования дня",
                start_time=datetime.now().replace(hour=7, minute=30, second=0, microsecond=0),
                end_time=datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
            )
            
            return {
                "success": True,
                "tasks_created": len(routine_tasks),
                "calendar_event": calendar_event,
                "message": "🌅 Утренний ритуал создан! Начните день с позитива."
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания утреннего ритуала: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_evening_routine(self) -> Dict[str, Any]:
        """Создание вечернего ритуала"""
        try:
            routine_tasks = []
            
            # Создаем задачи вечернего ритуала
            evening_tasks = [
                "📝 Рефлексия дня",
                "📅 Планирование завтра",
                "📖 Чтение перед сном",
                "😴 Подготовка ко сну"
            ]
            
            for task in evening_tasks:
                result = await self.create_quick_task(
                    task_text=task,
                    priority="medium",
                    due_date=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)
                )
                routine_tasks.append(result)
            
            # Создаем событие в календаре
            calendar_event = await self.calendar.create_event(
                title="🌙 Вечерний ритуал",
                description="Время для рефлексии и подготовки к завтрашнему дню",
                start_time=datetime.now().replace(hour=20, minute=30, second=0, microsecond=0),
                end_time=datetime.now().replace(hour=21, minute=30, second=0, microsecond=0)
            )
            
            return {
                "success": True,
                "tasks_created": len(routine_tasks),
                "calendar_event": calendar_event,
                "message": "🌙 Вечерний ритуал создан! Завершите день с пользой."
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания вечернего ритуала: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_productivity_insights(self) -> Dict[str, Any]:
        """Получение инсайтов по продуктивности"""
        try:
            # Анализируем данные за неделю
            week_tasks = await self.todoist.get_tasks()
            week_events = await self.calendar.get_week_events()
            
            # Вычисляем метрики
            completed_tasks = len([t for t in week_tasks if t.completed_at])
            total_tasks = len(week_tasks)
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Определяем паттерны
            patterns = []
            if completion_rate > 80:
                patterns.append("Высокая продуктивность")
            elif completion_rate > 60:
                patterns.append("Хорошая продуктивность")
            else:
                patterns.append("Есть возможности для улучшения")
            
            insights = {
                "completion_rate": completion_rate,
                "tasks_completed": completed_tasks,
                "total_tasks": total_tasks,
                "patterns": patterns,
                "recommendations": await self._generate_productivity_recommendations(completion_rate)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Ошибка получения инсайтов: {e}")
            return {"error": str(e)}
    
    async def _generate_productivity_recommendations(self, completion_rate: float) -> List[str]:
        """Генерация рекомендаций по продуктивности"""
        recommendations = []
        
        if completion_rate < 50:
            recommendations.extend([
                "🎯 Уменьшите количество задач в день",
                "⏰ Используйте технику Pomodoro",
                "📝 Разбивайте большие задачи на мелкие"
            ])
        elif completion_rate < 80:
            recommendations.extend([
                "📊 Анализируйте, какие задачи отнимают больше времени",
                "🔄 Оптимизируйте рабочий процесс",
                "🎯 Фокусируйтесь на приоритетных задачах"
            ])
        else:
            recommendations.extend([
                "🚀 Отличная работа! Попробуйте более сложные цели",
                "📈 Рассмотрите возможность делегирования",
                "🎯 Ставьте более амбициозные цели"
            ])
        
        return recommendations
    
    async def run_telegram_bot(self):
        """Запуск Telegram бота"""
        try:
            logger.info("🤖 Запуск Telegram бота...")
            await self.telegram_bot.run()
        except Exception as e:
            logger.error(f"Ошибка запуска Telegram бота: {e}")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            await self.todoist.cleanup()
            await self.calendar.cleanup()
            await self.notion.cleanup()
            logger.info("Очистка ресурсов завершена")
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")

# Глобальный экземпляр системы
life_system = LifeManagementSystem() 