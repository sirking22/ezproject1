import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = "d09df250ce7e4e0d9fbe4e036d320def"  # База задач
SUBTASKS_DB_ID = "9c5f4269d61449b6a7485579a3c21da3"  # База подзадач

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def find_task_by_title_and_status(title, status):
    """Найти задачу по названию и статусу"""
    url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Задача",
                    "title": {
                        "contains": title
                    }
                },
                {
                    "property": "Статус",
                    "status": {
                        "equals": status
                    }
                }
            ]
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

def create_subtask_with_hours(task_id, title, hours):
    """Создать подзадачу с указанием часов"""
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
    
    # Добавляем поле часов, если оно есть в схеме
    # Попробуем разные варианты названий поля
    hours_field_names = ["Часы", "Время", "Hours", "Time", "Ориентир"]
    
    # Сначала проверим схему базы подзадач
    schema_url = f"https://api.notion.com/v1/databases/{SUBTASKS_DB_ID}"
    schema_response = requests.get(schema_url, headers=headers)
    
    if schema_response.status_code == 200:
        schema = schema_response.json()
        properties = schema.get('properties', {})
        
        # Ищем поле для часов
        hours_field = None
        for field_name, field_info in properties.items():
            if field_info.get('type') == 'number':
                hours_field = field_name
                break
        
        if hours_field:
            payload["properties"][hours_field] = {
                "number": hours
            }
            print(f"✅ Добавлено поле '{hours_field}' со значением {hours}")
        else:
            print("⚠️ Поле для часов не найдено в схеме")
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка создания подзадачи: {response.status_code}")
        print(f"Ответ: {response.text}")
        return None
    
    return response.json()

def main():
    print("🎯 СОЗДАНИЕ ПРАВИЛЬНОЙ ПОДЗАДАЧИ")
    print("=" * 50)
    
    # 1. Найти задачу "Лого и иконка" в статусе In Progress
    print("🔍 Ищем задачу 'Лого и иконка' в статусе In Progress...")
    task = find_task_by_title_and_status("Лого и иконка", "In Progress")
    
    if not task:
        print("❌ Задача 'Лого и иконка' в статусе In Progress не найдена")
        print("🔍 Попробуем найти по части названия...")
        task = find_task_by_title_and_status("Лого", "In Progress")
        
        if not task:
            print("❌ Задача не найдена")
            return
    
    task_id = task['id']
    task_title = task['properties']['Задача']['title'][0]['plain_text']
    print(f"✅ Найдена задача: {task_title} (ID: {task_id})")
    
    # 2. Создать подзадачу
    print("\n📝 Создаем подзадачу...")
    subtask_title = "Доделать логотип"
    hours = 0.5  # 30 минут = 0.5 часа
    
    subtask = create_subtask_with_hours(task_id, subtask_title, hours)
    
    if not subtask:
        print("❌ Не удалось создать подзадачу")
        return
    
    subtask_id = subtask['id']
    print(f"✅ Создана подзадача: {subtask_title}")
    print(f"   ID подзадачи: {subtask_id}")
    print(f"   Часы: {hours}")
    
    # 3. Вывести ссылки
    print("\n🔗 ССЫЛКИ:")
    task_url = f"https://notion.so/{task_id.replace('-', '')}"
    subtask_url = f"https://notion.so/{subtask_id.replace('-', '')}"
    
    print(f"   📋 Задача: {task_url}")
    print(f"   📝 Подзадача: {subtask_url}")
    
    print("\n📝 ИНСТРУКЦИЯ:")
    print("   1. Откройте ссылку на подзадачу")
    print("   2. В поле 'Исполнитель' добавьте 'Arsentiy'")
    print("   3. Проверьте, что в поле 'Часы' указано 0.5")
    print("   4. Сохраните изменения")
    
    print("\n✅ Готово! Подзадача создана с правильными параметрами.")

if __name__ == "__main__":
    main() 