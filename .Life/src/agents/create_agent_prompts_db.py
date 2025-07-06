import os
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")  # ID страницы, где создавать базу

async def create_agent_prompts_db():
    """Создаёт новую базу agent_prompts с правильной структурой"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    try:
        print("Создание новой базы agent_prompts...")
        
        # Создаём новую базу данных
        new_db = await client.databases.create(
            parent={"page_id": PARENT_PAGE_ID},
            title=[{"text": {"content": "Промпты агентов"}}],
            properties={
                "Название": {
                    "title": {}
                },
                "Роль": {
                    "select": {
                        "options": [
                            {"name": "Product Manager", "color": "blue"},
                            {"name": "Developer", "color": "green"},
                            {"name": "LLM Researcher", "color": "purple"},
                            {"name": "DevOps", "color": "orange"},
                            {"name": "QA", "color": "red"},
                            {"name": "Support", "color": "yellow"},
                            {"name": "Growth/Marketing", "color": "pink"},
                            {"name": "Meta-Agent", "color": "gray"}
                        ]
                    }
                },
                "Промпт": {
                    "rich_text": {}
                },
                "Миссия": {
                    "rich_text": {}
                },
                "Статус": {
                    "select": {
                        "options": [
                            {"name": "Активный", "color": "green"},
                            {"name": "Черновик", "color": "yellow"},
                            {"name": "Архив", "color": "gray"}
                        ]
                    }
                },
                "Версия": {
                    "number": {
                        "format": "number"
                    }
                },
                "Дата создания": {
                    "date": {}
                },
                "Последнее обновление": {
                    "date": {}
                }
            }
        )
        
        print(f"✓ База создана с ID: {new_db['id']}")
        print(f"Название: {new_db['title'][0]['plain_text']}")
        
        # Обновляем .env файл
        env_file_path = ".env"
        if os.path.exists(env_file_path):
            with open(env_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Заменяем или добавляем переменную
            if "NOTION_DATABASE_ID_AGENT_PROMPTS=" in content:
                content = content.replace(
                    "NOTION_DATABASE_ID_AGENT_PROMPTS=",
                    f"NOTION_DATABASE_ID_AGENT_PROMPTS={new_db['id']}"
                )
            else:
                content += f"\nNOTION_DATABASE_ID_AGENT_PROMPTS={new_db['id']}"
            
            with open(env_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✓ .env файл обновлен")
        
        return new_db['id']
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    db_id = await create_agent_prompts_db()
    if db_id:
        print(f"\nНовая база agent_prompts создана!")
        print(f"ID: {db_id}")
        print("Теперь можно запустить создание промптов агентов.")

if __name__ == "__main__":
    asyncio.run(main()) 