import os
import asyncio
from datetime import datetime, timedelta
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

HABITS_DB = os.getenv('NOTION_DATABASE_ID_HABITS')
RITUALS_DB = os.getenv('NOTION_DATABASE_ID_RITUALS')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')

class WeeklyHabitGenerator:
    def __init__(self):
        self.client = AsyncClient(auth=NOTION_TOKEN)
    
    async def get_active_rituals(self):
        """Получает активные ритуалы (Сейчас в работ/ на паузе = True)"""
        print("=== Получение активных ритуалов ===")
        
        response = await self.client.databases.query(
            database_id=RITUALS_DB,
            filter={
                "property": "Сейчас в работ/ на паузе",
                "checkbox": {
                    "equals": True
                }
            }
        )
        
        rituals = response.get('results', [])
        print(f"Найдено активных ритуалов: {len(rituals)}")
        
        active_rituals = []
        for ritual in rituals:
            props = ritual['properties']
            name = props.get('Название', {}).get('title', [])
            name_text = name[0]['plain_text'] if name else 'Без названия'
            
            description = props.get('Описание', {}).get('rich_text', [])
            description_text = description[0]['text']['content'] if description else ''
            
            micro_step = props.get('Микрошаг', {}).get('rich_text', [])
            micro_step_text = micro_step[0]['text']['content'] if micro_step else ''
            
            category = props.get('Категория', {}).get('select', {}).get('name', '')
            
            active_rituals.append({
                'id': ritual['id'],
                'name': name_text,
                'description': description_text,
                'micro_step': micro_step_text,
                'category': category
            })
            print(f"- {name_text} ({category})")
        
        return active_rituals
    
    def get_schedule_for_ritual(self, ritual_name, start_date):
        """Определяет расписание для ритуала на неделю"""
        schedule = []
        
        # Расписание по дням недели (0=понедельник, 1=вторник, ..., 6=воскресенье)
        if 'бокс' in ritual_name.lower():
            # Бокс: вторник, четверг, суббота
            schedule_days = [1, 3, 5]  # вт, чт, сб
        elif 'шахматы' in ritual_name.lower():
            # Шахматы: 3 раза в неделю
            schedule_days = [1, 3, 5]  # вт, чт, сб
        elif 'чтение' in ritual_name.lower():
            # Чтение: ежедневно (объединяем "Чтение по расписанию" и "Интеллектуальное чтение")
            schedule_days = [0, 1, 2, 3, 4, 5, 6]  # все дни
        elif 'кино' in ritual_name.lower():
            # Гениальное кино: раз в 2 недели (пока раз в неделю)
            schedule_days = [5]  # суббота
        elif 'музыка' in ritual_name.lower():
            # Гениальная музыка: раз в неделю
            schedule_days = [4]  # пятница
        elif 'inbox' in ritual_name.lower():
            # Inbox Review: еженедельно
            schedule_days = [6]  # воскресенье
        else:
            # По умолчанию: 3 раза в неделю
            schedule_days = [1, 3, 5]  # вт, чт, сб
        
        # Генерируем даты на неделю вперёд
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            if current_date.weekday() in schedule_days:
                schedule.append(current_date)
        
        return schedule
    
    def get_time_of_day(self, ritual_name, weekday):
        """Определяет время дня для привычки"""
        if 'бокс' in ritual_name.lower():
            return 'Вечер'  # 18:30-20:00
        elif 'чтение' in ritual_name.lower():
            return 'Вечер'  # 5-10 минут вечером
        elif 'inbox' in ritual_name.lower():
            return 'Вечер'  # вечерний разбор
        elif 'кино' in ritual_name.lower():
            return 'Вечер'  # вечерний просмотр
        elif 'музыка' in ritual_name.lower():
            return 'День'   # днём для изучения
        else:
            return 'День'   # по умолчанию днём
    
    def get_habit_name(self, ritual_name):
        """Возвращает название привычки без даты"""
        # Объединяем чтение в одну привычку
        if 'чтение' in ritual_name.lower():
            return 'Чтение'
        elif 'бокс' in ritual_name.lower():
            return 'Бокс'
        elif 'шахматы' in ritual_name.lower():
            return 'Шахматы'
        elif 'кино' in ritual_name.lower():
            return 'Гениальное кино'
        elif 'музыка' in ritual_name.lower():
            return 'Гениальная музыка'
        elif 'inbox' in ritual_name.lower():
            return 'Inbox Review'
        elif 'пересказ' in ritual_name.lower():
            return 'Пересказ прочитанного'
        elif 'питание' in ritual_name.lower():
            return 'Питание на массу'
        elif 'тренировка' in ritual_name.lower():
            return 'Утренняя мини-тренировка'
        else:
            return ritual_name
    
    async def generate_weekly_habits(self, start_date=None):
        """Генерирует привычки на неделю вперёд"""
        if not start_date:
            start_date = datetime.now()
        
        print(f"\n=== Генерация привычек на неделю с {start_date.strftime('%Y-%m-%d')} ===")
        
        # Получаем активные ритуалы
        active_rituals = await self.get_active_rituals()
        
        if not active_rituals:
            print("Нет активных ритуалов для генерации привычек!")
            return
        
        # Проверяем существующие привычки на эту неделю
        week_end = start_date + timedelta(days=6)
        existing_habits = await self.get_existing_habits(start_date, week_end)
        
        generated_count = 0
        
        for ritual in active_rituals:
            # Получаем расписание для ритуала
            schedule = self.get_schedule_for_ritual(ritual['name'], start_date)
            
            for date in schedule:
                # Проверяем, не существует ли уже привычка на эту дату
                habit_name = self.get_habit_name(ritual['name'])
                date_str = date.strftime('%Y-%m-%d')
                
                # Проверяем существование по названию и дате
                habit_exists = False
                for existing_habit in existing_habits:
                    if existing_habit['name'] == habit_name and existing_habit['date'] == date_str:
                        habit_exists = True
                        break
                
                if habit_exists:
                    print(f"⏭️  Привычка уже существует: {habit_name} на {date_str}")
                    continue
                
                # Создаём привычку
                time_of_day = self.get_time_of_day(ritual['name'], date.weekday())
                habit_name = self.get_habit_name(ritual['name'])
                
                habit_props = {
                    'Привычка': {'title': [{'text': {'content': habit_name}}]},
                    'Комментарии': {'rich_text': [{'text': {'content': f"Автогенерировано из ритуала: {ritual['description']}\nМикрошаг: {ritual['micro_step']}"}}]},
                    'Дата': {'date': {'start': date.strftime('%Y-%m-%d')}},
                    'Время дня': {'select': {'name': time_of_day}},
                    'Выполнено': {'checkbox': False},
                    'Ритуалы': {'relation': [{'id': ritual['id']}]},
                }
                
                try:
                    new_habit = await self.client.pages.create(
                        parent={'database_id': HABITS_DB},
                        properties=habit_props
                    )
                    print(f"✅ Создана привычка: {habit_name} ({time_of_day})")
                    generated_count += 1
                    
                except Exception as e:
                    print(f"❌ Ошибка создания привычки {habit_name}: {e}")
        
        print(f"\n=== Генерация завершена ===")
        print(f"Создано новых привычек: {generated_count}")
        
        return generated_count
    
    async def get_existing_habits(self, start_date, end_date):
        """Получает существующие привычки в диапазоне дат"""
        response = await self.client.databases.query(
            database_id=HABITS_DB,
            filter={
                "and": [
                    {
                        "property": "Дата",
                        "date": {
                            "on_or_after": start_date.strftime('%Y-%m-%d')
                        }
                    },
                    {
                        "property": "Дата",
                        "date": {
                            "on_or_before": end_date.strftime('%Y-%m-%d')
                        }
                    }
                ]
            }
        )
        
        existing_habits = []
        for habit in response.get('results', []):
            name = habit['properties'].get('Привычка', {}).get('title', [])
            date = habit['properties'].get('Дата', {}).get('date', {})
            
            if name and date:
                existing_habits.append({
                    'name': name[0]['plain_text'],
                    'date': date.get('start', '')
                })
        
        return existing_habits
    
    async def cleanup_old_habits(self, days_to_keep=30):
        """Удаляет старые привычки (архивирует)"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        print(f"\n=== Очистка старых привычек (старше {days_to_keep} дней) ===")
        
        response = await self.client.databases.query(
            database_id=HABITS_DB,
            filter={
                "property": "Дата",
                "date": {
                    "before": cutoff_date.strftime('%Y-%m-%d')
                }
            }
        )
        
        old_habits = response.get('results', [])
        archived_count = 0
        
        for habit in old_habits:
            name = habit['properties'].get('Привычка', {}).get('title', [])
            name_text = name[0]['plain_text'] if name else 'Без названия'
            
            try:
                await self.client.pages.update(
                    page_id=habit['id'],
                    archived=True
                )
                print(f"🗑️  Архивирована старая привычка: {name_text}")
                archived_count += 1
            except Exception as e:
                print(f"❌ Ошибка архивирования {name_text}: {e}")
        
        print(f"Архивировано привычек: {archived_count}")

async def main():
    generator = WeeklyHabitGenerator()
    
    # Очищаем старые привычки (опционально)
    await generator.cleanup_old_habits(days_to_keep=30)
    
    # Генерируем привычки на неделю вперёд
    generated_count = await generator.generate_weekly_habits()
    
    print(f"\n🎯 Готово! Создано {generated_count} привычек на неделю.")
    print("Проверь в Notion созданные привычки и их связи с ритуалами.")

if __name__ == '__main__':
    asyncio.run(main()) 