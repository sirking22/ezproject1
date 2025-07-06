import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def get_users():
    """Получить всех пользователей"""
    url = "https://api.notion.com/v1/users"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка получения пользователей: {response.status_code}")
        return None
    
    return response.json()

def main():
    print("👥 ПОЛЬЗОВАТЕЛИ NOTION")
    print("=" * 30)
    
    users_data = get_users()
    if not users_data:
        return
    
    users = users_data.get('results', [])
    
    print(f"Всего пользователей: {len(users)}")
    print()
    
    for i, user in enumerate(users, 1):
        user_id = user.get('id', 'N/A')
        name = user.get('name', 'Без имени')
        email = user.get('person', {}).get('email', 'N/A') if user.get('person') else 'N/A'
        
        print(f"{i}. {name}")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print()

if __name__ == "__main__":
    main() 