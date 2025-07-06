import os
import asyncio
import logging
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("notion_update.log", mode='w'),
        logging.StreamHandler()
    ]
)

# Получаем ID баз из env
DATABASES = {
    'yearly_goals': os.getenv('NOTION_DATABASE_ID_YEARLY_GOALS'),
    'genius_list': os.getenv('NOTION_DATABASE_ID_GENIUS_LIST'),
    'journal': os.getenv('NOTION_DATABASE_ID_JOURNAL'),
    'rituals': os.getenv('NOTION_DATABASE_ID_RITUALS'),
    'habits': os.getenv('NOTION_DATABASE_ID_HABITS'),
    'reflection': os.getenv('NOTION_DATABASE_ID_REFLECTION'),
    'guides': os.getenv('NOTION_DATABASE_ID_GUIDES'),
    'tasks': os.getenv('NOTION_TASKS_DB'),
    'terms': os.getenv('NOTION_DATABASE_ID_TERMS'),
    'materials': os.getenv('NOTION_DATABASE_ID_MATERIALS'),
    'agent_prompts': os.getenv('NOTION_DATABASE_ID_AGENT_PROMPTS'),
    'ideas': os.getenv('NOTION_DATABASE_ID_IDEAS'),
    'experience_hub': os.getenv('NOTION_DATABASE_ID_EXPERIENCE_HUB'),
}

NOTION_TOKEN = os.getenv('NOTION_TOKEN')

# Описания полей и тестовые строки для каждой базы
SCHEMAS = {
    'yearly_goals': {
        'properties': {
            'goal_name': {'title': {}},
            'description': {'rich_text': {}},
            'why': {'rich_text': {}},
            'status': {'select': {'options': [{'name': v} for v in ['active','paused','completed','archived']]}},
            'priority': {'select': {'options': [{'name': v} for v in ['low','medium','high','critical']]}},
            'key_results': {'rich_text': {}},
            'related_habits': {'rich_text': {}},
            'related_materials': {'rich_text': {}},
            'progress': {'number': {'format': 'percent'}},
            'progress_formula': {'rich_text': {}},
            'deadline': {'date': {}},
            'review_date': {'date': {}},
            'insights': {'rich_text': {}}
        },
        'sample': {
            'goal_name': {'title': [{'text': {'content': 'Прокачать английский до B2'}}]},
            'description': {'rich_text': [{'text': {'content': 'Читать книги, смотреть видео, общаться'}}]},
            'why': {'rich_text': [{'text': {'content': 'Для работы и путешествий'}}]},
            'status': {'select': {'name': 'active'}},
            'priority': {'select': {'name': 'high'}},
            'key_results': {'rich_text': [{'text': {'content': 'Сдать экзамен, Прочитать 5 книг (relation: Tasks)'}}]},
            'related_habits': {'rich_text': [{'text': {'content': 'Ежедневное чтение (relation: Habits)'}}]},
            'related_materials': {'rich_text': [{'text': {'content': 'English Book (relation: Materials)'}}]},
            'progress': {'number': 40},
            'progress_formula': {'rich_text': [{'text': {'content': '=completed_key_results / total_key_results * 100'}}]},
            'deadline': {'date': {'start': '2024-12-31'}},
            'review_date': {'date': {'start': '2024-09-01'}},
            'insights': {'rich_text': [{'text': {'content': 'Лучше всего заходит аудио'}}]}
        }
    },
    'genius_list': {
        'properties': {
            'idea': {'title': {}},
            'description': {'rich_text': {}},
            'status': {'select': {'options': [{'name': v} for v in ['raw','reviewed','implemented','archived']]}},
            'potential': {'select': {'options': [{'name': v} for v in ['low','medium','high','breakthrough']]}},
            'impact': {'select': {'options': [{'name': v} for v in ['low','medium','high']]}},
            'next_action': {'rich_text': {}},
            'related_projects': {'rich_text': {}},
            'tags': {'multi_select': {'options': [{'name': v} for v in ['habit','workflow','ai','automation']]}},
            'insights': {'rich_text': {}},
            'review_notes': {'rich_text': {}}
        },
        'sample': {
            'idea': {'title': [{'text': {'content': 'Гиперпростая система трекинга привычек'}}]},
            'description': {'rich_text': [{'text': {'content': 'Всё в одной таблице, минимум кликов'}}]},
            'status': {'select': {'name': 'raw'}},
            'potential': {'select': {'name': 'high'}},
            'impact': {'select': {'name': 'high'}},
            'next_action': {'rich_text': [{'text': {'content': 'Сделать шаблон для Notion'}}]},
            'related_projects': {'rich_text': [{'text': {'content': '.life (relation: Yearly Goals)'}}]},
            'tags': {'multi_select': [{'name': 'habit'}, {'name': 'workflow'}]},
            'insights': {'rich_text': [{'text': {'content': 'Можно сделать шаблон для Notion'}}]},
            'review_notes': {'rich_text': [{'text': {'content': 'Проверить через месяц'}}]}
        }
    },
    'journal': {
        'properties': {
            'date': {'date': {}},
            'entry': {'title': {}},
            'mood': {'select': {'options': [{'name': v} for v in ['great','good','neutral','bad','awful']]}},
            'energy_level': {'number': {'format': 'number'}},
            'focus_level': {'number': {'format': 'number'}},
            'related_habits': {'rich_text': {}},
            'insight': {'rich_text': {}},
            'tags': {'multi_select': {'options': [{'name': v} for v in ['focus','energy','habit','ritual']]}}
        },
        'sample': {
            'date': {'date': {'start': '2024-07-01'}},
            'entry': {'title': [{'text': {'content': 'Утро: фокус, вечер: усталость'}}]},
            'mood': {'select': {'name': 'good'}},
            'energy_level': {'number': 7},
            'focus_level': {'number': 6},
            'related_habits': {'rich_text': [{'text': {'content': 'Утренняя медитация (relation: Habits)'}}]},
            'insight': {'rich_text': [{'text': {'content': 'Лучше не читать новости утром'}}]},
            'tags': {'multi_select': [{'name': 'focus'}, {'name': 'energy'}]}
        }
    },
    # ... (аналогично для остальных баз: ритуалы, привычки, рефлексия, гайды, задачи, термины, материалы, промпты, идеи, experience_hub)
}

# Привычки, которые нужно удалить
DELETE_HABITS = [
    'Трекер привычек',
    'Путешествия — планирование и отчёты',
]

# Новые/оптимизированные привычки (пример)
NEW_HABITS = [
    {
        'Привычка': 'Фильмы для развития',
        'Комментарий': 'Гениальное кино раз в 2 недели, с рефлексией',
        'Ритуал': 'Гениальное кино',
        'Частота': 'Раз в 2 недели',
    },
    {
        'Привычка': 'Чтение по расписанию',
        'Комментарий': 'Каждый день 5-10 минут',
        'Ритуал': 'Чтение',
        'Частота': 'Ежедневно',
    },
    {
        'Привычка': 'Музыкальные открытия',
        'Комментарий': 'Изучать новые жанры, исполнителей, закреплять материал через опросы/нейросети',
        'Ритуал': 'Гениальная музыка',
        'Частота': 'Раз в неделю',
    },
    {
        'Привычка': 'Бокс по расписанию',
        'Комментарий': 'Вторник, четверг, суббота 18:30-20:00',
        'Ритуал': 'Бокс',
        'Частота': '3 раза в неделю',
    },
    {
        'Привычка': 'Разбор inbox',
        'Комментарий': 'Регулярно разбирать задачи, картинки, ссылки, видео. Рабочий и личный inbox.',
        'Ритуал': 'Inbox Review',
        'Частота': 'Еженедельно',
    },
]

async def update_db_and_add_sample():
    if not NOTION_TOKEN:
        logging.error("NOTION_TOKEN не найден в env!")
        return
    client = AsyncClient(auth=NOTION_TOKEN)
    summary = {}
    for db_key, db_id in DATABASES.items():
        if not db_id:
            logging.warning(f"Пропускаю {db_key}: нет ID в env")
            summary[db_key] = 'NO_ID'
            continue
        if db_key not in SCHEMAS:
            logging.warning(f"Пропускаю {db_key}: нет схемы в SCHEMAS")
            summary[db_key] = 'NO_SCHEMA'
            continue
        logging.info(f"Пробую соединиться с базой {db_key} ({db_id})...")
        try:
            db_meta = await client.databases.retrieve(database_id=db_id)
            logging.info(f"✓ База {db_key} найдена: {db_meta['title'][0]['plain_text'] if db_meta['title'] else db_key}")
        except Exception as e:
            logging.error(f"Ошибка соединения с базой {db_key}: {e}")
            summary[db_key] = f'CONNECT_ERROR: {e}'
            continue
        try:
            logging.info(f"Обновляю структуру базы {db_key}...")
            await client.databases.update(database_id=db_id, properties=SCHEMAS[db_key]['properties'])
            logging.info(f"✓ Структура {db_key} обновлена")
        except Exception as e:
            logging.error(f"Ошибка обновления структуры {db_key}: {e}")
            summary[db_key] = f'SCHEMA_ERROR: {e}'
            continue
        try:
            logging.info(f"Добавляю тестовую строку в {db_key}...")
            await client.pages.create(parent={"database_id": db_id}, properties=SCHEMAS[db_key]['sample'])
            logging.info(f"✓ Тестовая строка добавлена в {db_key}")
            summary[db_key] = 'OK'
        except Exception as e:
            logging.error(f"Ошибка добавления тестовой строки в {db_key}: {e}")
            summary[db_key] = f'SAMPLE_ERROR: {e}'
    logging.info("\n=== ОТЧЁТ ===")
    for db_key, status in summary.items():
        logging.info(f"{db_key}: {status}")
    logging.info("Готово. Подробности смотри в notion_update.log")

async def main():
    if not NOTION_TOKEN or not DATABASES['habits']:
        print('NOTION_TOKEN или NOTION_DATABASE_ID_HABITS не найден!')
        return
    client = AsyncClient(auth=NOTION_TOKEN)
    # Получаем все привычки
    response = await client.databases.query(database_id=DATABASES['habits'])
    pages = response.get('results', [])
    # Удаляем лишние привычки
    for page in pages:
        name = page['properties']['Привычка'].get('title', [])
        if name:
            title = name[0]['plain_text']
            if title in DELETE_HABITS:
                await client.pages.update(page_id=page['id'], archived=True)
                print(f'Удалена привычка: {title}')
    # Добавляем/обновляем шаблонные привычки
    for habit in NEW_HABITS:
        # Проверяем, есть ли уже такая привычка
        exists = False
        for page in pages:
            name = page['properties']['Привычка'].get('title', [])
            if name and name[0]['plain_text'] == habit['Привычка']:
                exists = True
                # Обновляем комментарий и частоту
                props = {}
                if 'Комментарий' in page['properties']:
                    props['Комментарии'] = {'rich_text': [{'text': {'content': habit['Комментарий']}}]}
                if 'Частота' in page['properties']:
                    props['Частота'] = {'rich_text': [{'text': {'content': habit['Частота']}}]}
                await client.pages.update(page_id=page['id'], properties=props)
                print(f"Обновлена привычка: {habit['Привычка']}")
        if not exists:
            # Создаём новую привычку
            props = {
                'Привычка': {'title': [{'text': {'content': habit['Привычка']}}]},
                'Комментарии': {'rich_text': [{'text': {'content': habit['Комментарий']}}]},
                'Частота': {'rich_text': [{'text': {'content': habit['Частота']}}]},
            }
            await client.pages.create(parent={'database_id': DATABASES['habits']}, properties=props)
            print(f"Создана привычка: {habit['Привычка']}")

if __name__ == "__main__":
    asyncio.run(update_db_and_add_sample())
    asyncio.run(main()) 