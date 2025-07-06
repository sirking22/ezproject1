import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
from notion_client import AsyncClient
from src.agents.agent_core import agent_core

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DailyAutomation:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_client = AsyncClient(auth=self.notion_token)
        
        # Notion базы
        self.dbs = {
            "rituals": os.getenv("NOTION_DATABASE_ID_RITUALS"),
            "habits": os.getenv("NOTION_DATABASE_ID_HABITS"),
            "reflection": os.getenv("NOTION_DATABASE_ID_REFLECTION"),
            "guides": os.getenv("NOTION_DATABASE_ID_GUIDES"),
            "actions": os.getenv("NOTION_DATABASE_ID_ACTIONS"),
            "terms": os.getenv("NOTION_DATABASE_ID_TERMS"),
            "materials": os.getenv("NOTION_DATABASE_ID_MATERIALS"),
            "agent_prompts": os.getenv("NOTION_DATABASE_ID_AGENT_PROMPTS"),
        }
        
        # Поля для каждой базы
        self.db_fields = {
            "rituals": ("Название", "Категория"),
            "habits": ("Привычка", None),
            "reflection": ("Дата", "Тип"),
            "guides": ("Name", None),
            "actions": ("Задача", "Категория"),
            "terms": ("Термин", "Категория"),
            "materials": ("Название", "Категория"),
            "agent_prompts": ("Name", "Роль"),
        }

    async def create_daily_reflection(self):
        """Создаёт ежедневную рефлексию"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Получаем активные привычки
            habits = await self.get_notion_records("habits")
            
            # Формируем контекст для рефлексии
            context = f"Дата: {today}\nАктивные привычки: {len(habits)}"
            
            # Получаем рекомендации от Meta-Agent
            reflection_prompt = f"""
            Создай ежедневную рефлексию для {today}.
            
            Контекст:
            - Активных привычек: {len(habits)}
            - День недели: {datetime.now().strftime('%A')}
            
            Структура рефлексии:
            1. Общее настроение и энергия
            2. Прогресс по привычкам
            3. Ключевые достижения
            4. Вызовы и сложности
            5. Планы на завтра
            6. Благодарность
            
            Сделай рефлексию конкретной, честной и мотивирующей.
            """
            
            reflection_content = await agent_core.get_agent_response(
                "Meta-Agent", 
                context, 
                reflection_prompt
            )
            
            # Создаём запись в базе reflection
            await self.create_notion_record(
                "reflection",
                f"Рефлексия {today}",
                "Ежедневная",
                {
                    "Дата": {"date": {"start": today}},
                    "Тип": {"select": {"name": "Ежедневная"}},
                    "Содержание": {"rich_text": [{"text": {"content": reflection_content}}]}
                }
            )
            
            logger.info(f"Создана ежедневная рефлексия для {today}")
            return reflection_content
            
        except Exception as e:
            logger.error(f"Ошибка создания ежедневной рефлексии: {e}")
            return None

    async def check_habits_completion(self):
        """Проверяет выполнение привычек и создаёт напоминания"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Получаем все привычки
            habits = await self.get_notion_records("habits")
            
            incomplete_habits = []
            for habit in habits:
                # Проверяем, выполнена ли привычка сегодня
                # Здесь можно добавить логику проверки статуса
                habit_name = habit["properties"].get("Привычка", {}).get("title", [{}])[0].get("plain_text", "")
                if habit_name:
                    incomplete_habits.append(habit_name)
            
            if incomplete_habits:
                # Создаём напоминание о невыполненных привычках
                reminder_content = f"""
                📋 **Напоминание о привычках - {today}**
                
                Не выполненные привычки:
                {chr(10).join(f"• {habit}" for habit in incomplete_habits)}
                
                Время ещё есть! Выполните хотя бы одну привычку сегодня.
                """
                
                # Создаём запись в actions как напоминание
                await self.create_notion_record(
                    "actions",
                    f"Напоминание о привычках {today}",
                    "Автоматизация",
                    {
                        "Задача": {"title": [{"text": {"content": f"Выполнить привычки: {', '.join(incomplete_habits[:3])}"}}]},
                        "Категория": {"select": {"name": "Автоматизация"}},
                        "Приоритет": {"select": {"name": "Средний"}},
                        "Статус": {"select": {"name": "К выполнению"}}
                    }
                )
                
                logger.info(f"Создано напоминание о {len(incomplete_habits)} привычках")
                return reminder_content
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка проверки привычек: {e}")
            return None

    async def generate_weekly_insights(self):
        """Генерирует еженедельные инсайты на основе данных"""
        try:
            # Проверяем, нужно ли создавать еженедельную рефлексию
            today = datetime.now()
            if today.weekday() != 6:  # Только по воскресеньям
                return None
            
            # Получаем данные за неделю
            week_start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
            week_end = today.strftime("%Y-%m-%d")
            
            # Получаем рефлексии за неделю
            reflections = await self.get_notion_records("reflection")
            
            # Получаем выполненные задачи
            actions = await self.get_notion_records("actions")
            
            # Формируем контекст для анализа
            context = f"""
            Анализ недели: {week_start} - {week_end}
            Рефлексий: {len(reflections)}
            Задач: {len(actions)}
            """
            
            # Получаем еженедельные инсайты от Meta-Agent
            insights_prompt = f"""
            Проанализируй неделю {week_start} - {week_end} и создай еженедельные инсайты.
            
            Структура анализа:
            1. Общие достижения недели
            2. Паттерны в привычках
            3. Ключевые уроки
            4. Области для улучшения
            5. Цели на следующую неделю
            6. Благодарность за неделю
            
            Сделай анализ глубоким, честным и мотивирующим для роста.
            """
            
            insights_content = await agent_core.get_agent_response(
                "Meta-Agent",
                context,
                insights_prompt
            )
            
            # Создаём запись в reflection
            await self.create_notion_record(
                "reflection",
                f"Еженедельные инсайты {week_start}-{week_end}",
                "Еженедельная",
                {
                    "Дата": {"date": {"start": today.strftime("%Y-%m-%d")}},
                    "Тип": {"select": {"name": "Еженедельная"}},
                    "Содержание": {"rich_text": [{"text": {"content": insights_content}}]}
                }
            )
            
            logger.info(f"Созданы еженедельные инсайты для {week_start}-{week_end}")
            return insights_content
            
        except Exception as e:
            logger.error(f"Ошибка генерации еженедельных инсайтов: {e}")
            return None

    async def create_notion_record(self, db_name: str, title: str, category: str = None, 
                                 additional_props: Dict = None) -> bool:
        """Создаёт запись в указанной Notion базе"""
        try:
            db_id = self.dbs[db_name]
            title_field = self.db_fields[db_name][0]
            category_field = self.db_fields[db_name][1]
            
            properties = {
                title_field: {"title": [{"text": {"content": title}}]}
            }
            
            if category_field and category:
                properties[category_field] = {"select": {"name": category}}
            
            if additional_props:
                properties.update(additional_props)
            
            await self.notion_client.pages.create(
                parent={"database_id": db_id},
                properties=properties
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания записи в {db_name}: {e}")
            return False

    async def get_notion_records(self, db_name: str, filter_params: Dict = None) -> List[Dict]:
        """Получает записи из Notion базы с фильтрацией"""
        try:
            db_id = self.dbs[db_name]
            
            query_params = {"database_id": db_id}
            if filter_params:
                query_params["filter"] = filter_params
            
            response = await self.notion_client.databases.query(**query_params)
            return response["results"]
            
        except Exception as e:
            logger.error(f"Ошибка получения записей из {db_name}: {e}")
            return []

    async def run_daily_automation(self):
        """Запускает все ежедневные автоматизации"""
        logger.info("Запуск ежедневной автоматизации...")
        
        results = {}
        
        # 1. Создание ежедневной рефлексии
        reflection = await self.create_daily_reflection()
        results["reflection"] = reflection
        
        # 2. Проверка привычек
        habits_reminder = await self.check_habits_completion()
        results["habits_reminder"] = habits_reminder
        
        # 3. Еженедельные инсайты (только по воскресеньям)
        weekly_insights = await self.generate_weekly_insights()
        results["weekly_insights"] = weekly_insights
        
        logger.info("Ежедневная автоматизация завершена")
        return results

async def main():
    """Главная функция для запуска автоматизации"""
    automation = DailyAutomation()
    results = await automation.run_daily_automation()
    
    print("=== РЕЗУЛЬТАТЫ АВТОМАТИЗАЦИИ ===")
    for key, value in results.items():
        if value:
            print(f"✓ {key}: {len(str(value))} символов")
        else:
            print(f"- {key}: не выполнено")

if __name__ == "__main__":
    asyncio.run(main()) 