#!/usr/bin/env python3
import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

print(f"Текущая рабочая директория: {os.getcwd()}")
print(f"Путь к скрипту: {os.path.abspath(__file__)}")
print(f"Python: {sys.executable}")
print(f"Аргументы запуска: {sys.argv}")

# Логируем env
env_path = os.path.join(os.getcwd(), '.env')
print(f"Путь к .env: {env_path}")
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        print('Содержимое .env:')
        print(f.read())
else:
    print(".env не найден")

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
HABITS_DB_ID = "1fddb2b98a1b8053a54aedf250530798"

print(f"NOTION_TOKEN: {'есть' if NOTION_TOKEN else 'НЕТ'}")
print(f"HABITS_DB_ID: {HABITS_DB_ID}")

client = Client(auth=NOTION_TOKEN)
print(">>> Делаю запрос к Notion API...")

try:
    habits = client.databases.query(database_id=HABITS_DB_ID)
    print(f"RAW ответ от API (первые 1000 символов):\n{json.dumps(habits, ensure_ascii=False)[:1000]}\n")
    all_habits = habits['results']
    print(f"Всего habits['results']: {len(all_habits)}")
    print("ID всех привычек:")
    for h in all_habits:
        print(f"  - {h['id']}")
    print("\nRAW JSON каждой привычки:")
    for i, h in enumerate(all_habits, 1):
        print(f"\n--- Привычка {i} ---")
        print(json.dumps(h, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"❌ Ошибка: {e}") 