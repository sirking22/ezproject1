import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = "d09df250ce7e4e0d9fbe4e036d320def"  # База задач
SUBTASKS_DB_ID = "9c5f4269d61449b6a7485579a3c21da3"  # База подзадач

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def find_task_by_title(title):
    """Найти задачу по названию"""
    url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "property": "Задача",
            "title": {
                "contains": title
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка поиска задачи: {response.status_code}")
        return None
    
    data = response.json()
    results = data.get('results', [])
    
    if results:
        return results[0]
    return None

def create_subtask(task_id, title):
    """Создать подзадачу без исполнителя"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "parent": {"database_id": SUBTASKS_DB_ID},
        "properties": {
            "Подзадачи": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            " Статус": {
                "status": {
                    "name": "To do"
                }
            },
            "Задачи": {
                "relation": [
                    {
                        "id": task_id
                    }
                ]
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка создания подзадачи: {response.status_code}")
        print(f"Ответ: {response.text}")
        return None
    
    return response.json()

def update_task_status(task_id, status):
    """Обновить статус задачи"""
    url = f"https://api.notion.com/v1/pages/{task_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "properties": {
            "Статус": {
                "status": {
                    "name": status
                }
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка обновления статуса: {response.status_code}")
        return False
    
    return True

def main():
    print("🎯 ДОБАВЛЕНИЕ ПОДЗАДАЧИ ДЛЯ АРСЕНИЯ")
    print("=" * 50)
    
    # 1. Найти задачу "Иконки"
    print("🔍 Ищем задачу 'Иконки'...")
    task = find_task_by_title("Иконки")
    
    if not task:
        print("❌ Задача 'Иконки' не найдена")
        return
    
    task_id = task['id']
    task_title = task['properties']['Задача']['title'][0]['plain_text']
    print(f"✅ Найдена задача: {task_title} (ID: {task_id})")
    
    # 2. Создать подзадачу
    print("\n📝 Создаем подзадачу...")
    subtask_title = "Доделать логотип (30 минут)"
    subtask = create_subtask(task_id, subtask_title)
    
    if not subtask:
        print("❌ Не удалось создать подзадачу")
        return
    
    subtask_id = subtask['id']
    print(f"✅ Создана подзадача: {subtask_title}")
    print(f"   ID подзадачи: {subtask_id}")
    
    # 3. Обновить статус задачи на "In Progress"
    print("\n🔄 Обновляем статус задачи...")
    if update_task_status(task_id, "In Progress"):
        print("✅ Статус задачи обновлен на 'In Progress'")
    else:
        print("❌ Не удалось обновить статус задачи")
    
    # 4. Вывести ссылки
    print("\n🔗 ССЫЛКИ:")
    task_url = f"https://notion.so/{task_id.replace('-', '')}"
    subtask_url = f"https://notion.so/{subtask_id.replace('-', '')}"
    
    print(f"   📋 Задача: {task_url}")
    print(f"   📝 Подзадача: {subtask_url}")
    
    print("\n📝 ИНСТРУКЦИЯ:")
    print("   1. Откройте ссылку на подзадачу")
    print("   2. В поле 'Исполнитель' добавьте 'Arsentiy'")
    print("   3. Сохраните изменения")
    
    print("\n✅ Готово! Задача обновлена и подзадача создана.")

if __name__ == "__main__":
    main() 