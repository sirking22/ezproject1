import os
from dotenv import load_dotenv

print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("=" * 50)

# Загружаем .env
load_dotenv()

# Проверяем все Notion переменные
notion_vars = {
    "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
    "NOTION_TASKS_DB_ID": os.getenv("NOTION_TASKS_DB_ID"),
    "NOTION_TEAMS_DB_ID": os.getenv("NOTION_TEAMS_DB_ID"),
    "NOTION_KPI_DB_ID": os.getenv("NOTION_KPI_DB_ID"),
    "NOTION_MATERIALS_DB_ID": os.getenv("NOTION_MATERIALS_DB_ID"),
    "NOTION_IDEAS_DB_ID": os.getenv("NOTION_IDEAS_DB_ID"),
}

print("\n📋 NOTION ПЕРЕМЕННЫЕ:")
for var, value in notion_vars.items():
    status = "✅ УСТАНОВЛЕНА" if value else "❌ ОТСУТСТВУЕТ"
    print(f"   {var}: {status}")
    if value:
        print(f"      Значение: {value[:20]}..." if len(value) > 20 else f"      Значение: {value}")

# Проверяем другие важные переменные
other_vars = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "YA_ACCESS_TOKEN": os.getenv("YA_ACCESS_TOKEN"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}

print("\n📋 ДРУГИЕ ПЕРЕМЕННЫЕ:")
for var, value in other_vars.items():
    status = "✅ УСТАНОВЛЕНА" if value else "❌ ОТСУТСТВУЕТ"
    print(f"   {var}: {status}")

print(f"\n💡 РЕКОМЕНДАЦИИ:")
missing = [var for var, value in notion_vars.items() if not value]
if missing:
    print(f"   ❌ Отсутствуют: {', '.join(missing)}")
    print("   📝 Добавьте их в .env файл в корне проекта")
else:
    print("   ✅ Все Notion переменные настроены!")

print(f"\n🎯 ГОТОВ К РАБОТЕ: {'Да' if notion_vars['NOTION_TOKEN'] and notion_vars['NOTION_TASKS_DB_ID'] else 'Нет'}") 