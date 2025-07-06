import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SUBTASK_ID = "224ace03-d9ff-81a6-81c6-d4c67a0b4898"  # ID ошибочной подзадачи

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def delete_subtask(subtask_id):
    """Удалить подзадачу"""
    url = f"https://api.notion.com/v1/pages/{subtask_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "archived": True
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка удаления подзадачи: {response.status_code}")
        print(f"Ответ: {response.text}")
        return False
    
    return True

def main():
    print("🗑️ УДАЛЕНИЕ ОШИБОЧНОЙ ПОДЗАДАЧИ")
    print("=" * 40)
    
    print(f"Удаляем подзадачу: {SUBTASK_ID}")
    
    if delete_subtask(SUBTASK_ID):
        print("✅ Подзадача успешно удалена (архивирована)")
    else:
        print("❌ Не удалось удалить подзадачу")

if __name__ == "__main__":
    main() 