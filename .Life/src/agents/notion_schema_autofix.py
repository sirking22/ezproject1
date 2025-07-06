import os
import sys
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

# Добавляем корень в sys.path для импорта шаблонов
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.activity_autocreate import DBS, DB_FIELDS

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

FIELD_TYPE_MAP = {
    "title": {"type": "title", "title": [{}]},
    "select": {"type": "select", "select": {"options": []}},
}

def guess_field_type(field_name):
    # Примитивная эвристика: если поле называется "Категория" — select, если "Название"/"Name"/"Задача"/"Привычка" — title
    if field_name.lower() in ["категория"]:
        return "select"
    if field_name.lower() in ["название", "name", "задача", "привычка"]:
        return "title"
    return "title"  # fallback

async def validate_and_fix_schema():
    client = AsyncClient(auth=NOTION_TOKEN)
    any_errors = False
    for db_name, db_id in DBS.items():
        print(f"\n=== Проверка базы {db_name.upper()} ===")
        if not db_id:
            print(f"  ❌ Нет ID базы {db_name} в переменных окружения")
            any_errors = True
            continue
        try:
            db = await client.databases.retrieve(database_id=db_id)
            existing_fields = db["properties"].keys()
            required_fields = [f for f in DB_FIELDS[db_name] if f]
            missing = [f for f in required_fields if f not in existing_fields]
            if not missing:
                print(f"  ✅ Все нужные поля присутствуют: {required_fields}")
            else:
                print(f"  ⚠️ Не хватает полей: {missing}")
                for field in missing:
                    field_type = guess_field_type(field)
                    print(f"    ➕ Добавляю поле '{field}' типа '{field_type}'...")
                    try:
                        await client.databases.update(
                            database_id=db_id,
                            properties={
                                field: FIELD_TYPE_MAP[field_type]
                            }
                        )
                        print(f"      ✅ Поле '{field}' добавлено!")
                    except Exception as e:
                        print(f"      ❌ Ошибка добавления поля '{field}': {e}")
                        any_errors = True
        except Exception as e:
            print(f"  ❌ Ошибка доступа к базе {db_name}: {e}")
            any_errors = True
    if any_errors:
        print("\n❗ Были ошибки при валидации/создании полей. Проверьте вывод выше.")
    else:
        print("\n✅ Все базы и поля соответствуют требованиям!")

if __name__ == "__main__":
    asyncio.run(validate_and_fix_schema()) 