from notion_client import Client
from typing import Optional, Dict, List, Any
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

load_dotenv()

class NotionPage:
    """Класс для представления страницы Notion"""
    def __init__(self, page_data: Dict[str, Any]):
        self.id = page_data.get("id", "")
        self.title = self._extract_title(page_data)
        self.description = self._extract_description(page_data)
        self.tags = self._extract_tags(page_data)
        self.importance = self._extract_importance(page_data)
        self.status = self._extract_status(page_data)
        self.due_date = self._extract_due_date(page_data)
        self.url = page_data.get("url", "")
        self.created_time = page_data.get("created_time", "")
        self.last_edited_time = page_data.get("last_edited_time", "")
    
    def _extract_title(self, page_data: Dict[str, Any]) -> str:
        """Извлекает заголовок из свойств страницы"""
        properties = page_data.get("properties", {})
        title_prop = properties.get("Name")
        if title_prop and "title" in title_prop:
            title_array = title_prop["title"]
            if title_array:
                return title_array[0].get("plain_text", "")
        return "Без названия"
    
    def _extract_description(self, page_data: Dict[str, Any]) -> str:
        """Извлекает описание из свойств страницы"""
        properties = page_data.get("properties", {})
        desc_prop = properties.get("Описание")
        if desc_prop and "rich_text" in desc_prop:
            desc_array = desc_prop["rich_text"]
            if desc_array:
                return desc_array[0].get("plain_text", "")
        return ""
    
    def _extract_tags(self, page_data: Dict[str, Any]) -> List[str]:
        """Извлекает теги из свойств страницы"""
        properties = page_data.get("properties", {})
        tags_prop = properties.get("Теги")
        if tags_prop and "multi_select" in tags_prop:
            return [tag["name"] for tag in tags_prop["multi_select"]]
        return []
    
    def _extract_importance(self, page_data: Dict[str, Any]) -> int:
        """Извлекает важность из свойств страницы"""
        properties = page_data.get("properties", {})
        importance_prop = properties.get("~Весомость?")
        if importance_prop and "number" in importance_prop:
            return importance_prop["number"] or 5
        return 5
    
    def _extract_status(self, page_data: Dict[str, Any]) -> str:
        """Извлекает статус из свойств страницы"""
        properties = page_data.get("properties", {})
        status_prop = properties.get("Статус")
        if status_prop and "status" in status_prop:
            return status_prop["status"]["name"] if status_prop["status"] else "Not Started"
        return "Not Started"
    
    def _extract_due_date(self, page_data: Dict[str, Any]) -> str:
        """Извлекает дату выполнения из свойств страницы"""
        properties = page_data.get("properties", {})
        due_prop = properties.get("Due Date") or properties.get("Date")
        if due_prop and "date" in due_prop:
            return due_prop["date"]["start"] if due_prop["date"] else ""
        return ""

class NotionManager:
    def __init__(self):
        self.client = Client(auth=os.getenv("NOTION_TOKEN"))
        
    async def sync_database(self, database_id: str) -> List[Dict]:
        """Получает данные из базы данных Notion"""
        try:
            response = self.client.databases.query(database_id=database_id)
            return response["results"]
        except Exception as e:
            print(f"Ошибка при синхронизации с Notion: {e}")
            return []
    
    async def get_pages(self, database_id: str, filter_params=None, limit=50, sort=None) -> List[NotionPage]:
        """Получает страницы из базы данных"""
        try:
            query_params = {
                "database_id": database_id,
                "page_size": min(limit, 100)
            }
            
            if filter_params:
                query_params["filter"] = filter_params
            
            if sort:
                query_params["sorts"] = [sort]
            
            response = self.client.databases.query(**query_params)
            pages = []
            
            for page_data in response["results"]:
                pages.append(NotionPage(page_data))
            
            return pages
        except Exception as e:
            print(f"Ошибка при получении страниц: {e}")
            return []

    async def create_page(self, page_data: dict) -> NotionPage:
        """Создает новую страницу"""
        try:
            database_id = page_data["database_id"]
            
            # Подготавливаем свойства страницы с правильными именами
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": page_data["title"]
                            }
                        }
                    ]
                }
            }
            
            # Добавляем описание (используем правильное имя свойства)
            if page_data.get("description"):
                properties["Описание"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": page_data["description"]
                            }
                        }
                    ]
                }
            
            # Добавляем теги (используем правильное имя свойства)
            if page_data.get("tags"):
                properties["Теги"] = {
                    "multi_select": [
                        {"name": tag} for tag in page_data["tags"]
                    ]
                }
            
            # Добавляем важность/вес (используем правильное имя свойства в зависимости от базы)
            if page_data.get("importance"):
                # Определяем базу по ID
                ideas_db_id = os.getenv("NOTION_IDEAS_DB_ID")
                if database_id == ideas_db_id:
                    # База идей - используем "Вес"
                    properties["Вес"] = {
                        "number": page_data["importance"]
                    }
                else:
                    # Другие базы - используем "~Весомость?"
                    properties["~Весомость?"] = {
                        "number": page_data["importance"]
                    }
            
            # Добавляем статус (используем правильное имя свойства и значения)
            if page_data.get("status"):
                # Маппинг статусов на реальные значения из базы
                status_mapping = {
                    "Not Started": "To do",
                    "In Progress": "In progress", 
                    "Done": "Ок",
                    "Archive": "Архив",
                    "Discuss": "Обсудить"
                }
                actual_status = status_mapping.get(page_data["status"], page_data["status"])
                properties["Статус"] = {
                    "status": {
                        "name": actual_status
                    }
                }
            
            # Добавляем дату выполнения (если есть)
            if page_data.get("due_date"):
                properties["Date"] = {
                    "date": {
                        "start": page_data["due_date"]
                    }
                }
            
            # Создаем страницу
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            return NotionPage(response)
        except Exception as e:
            print(f"Ошибка при создании страницы: {e}")
            # Пробрасываем исключение вместо возврата заглушки
            raise

    async def update_page(self, page_id: str, update_data: dict) -> NotionPage:
        """Обновляет существующую страницу"""
        try:
            properties = {}
            
            # Обновляем заголовок
            if "title" in update_data:
                properties["Name"] = {
                    "title": [
                        {
                            "text": {
                                "content": update_data["title"]
                            }
                        }
                    ]
                }
            
            # Обновляем описание (используем правильное имя свойства)
            if "description" in update_data:
                properties["Описание"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": update_data["description"]
                            }
                        }
                    ]
                }
            
            # Обновляем теги (используем правильное имя свойства)
            if "tags" in update_data:
                properties["Теги"] = {
                    "multi_select": [
                        {"name": tag} for tag in update_data["tags"]
                    ]
                }
            
            # Обновляем важность (используем правильное имя свойства)
            if "importance" in update_data:
                properties["~Весомость?"] = {
                    "number": update_data["importance"]
                }
            
            # Обновляем статус (используем правильное имя свойства и значения)
            if "status" in update_data:
                # Маппинг статусов на реальные значения из базы
                status_mapping = {
                    "Not Started": "To do",
                    "In Progress": "In progress", 
                    "Done": "Ок",
                    "Archive": "Архив",
                    "Discuss": "Обсудить"
                }
                actual_status = status_mapping.get(update_data["status"], update_data["status"])
                properties["Статус"] = {
                    "status": {
                        "name": actual_status
                    }
                }
            
            # Обновляем дату выполнения
            if "due_date" in update_data:
                properties["Due Date"] = {
                    "date": {
                        "start": update_data["due_date"]
                    }
                }
            
            # Обновляем страницу
            response = self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return NotionPage(response)
        except Exception as e:
            print(f"Ошибка при обновлении страницы: {e}")
            return NotionPage({"id": page_id, "properties": {}})

    async def search_pages(self, query: str, database_id=None, limit=20, filter_params=None) -> List[NotionPage]:
        """Ищет страницы по тексту"""
        try:
            search_params = {
                "query": query,
                "page_size": min(limit, 100)
            }
            
            if database_id:
                search_params["filter"] = {
                    "property": "object",
                    "value": "page"
                }
            
            if filter_params:
                search_params["filter"] = filter_params
            
            response = self.client.search(**search_params)
            pages = []
            
            for page_data in response["results"]:
                # Проверяем, что это страница из нужной базы данных
                if database_id:
                    parent = page_data.get("parent", {})
                    if parent.get("database_id") != database_id:
                        continue
                
                pages.append(NotionPage(page_data))
            
            return pages
        except Exception as e:
            print(f"Ошибка при поиске страниц: {e}")
        return []

    async def get_database_info(self, database_id: str) -> Dict[str, Any]:
        """Получает информацию о базе данных"""
        try:
            response = self.client.databases.retrieve(database_id=database_id)
            return {
                "id": response["id"],
                "title": response["title"][0]["plain_text"] if response["title"] else "Без названия",
                "created_time": response["created_time"],
                "last_edited_time": response["last_edited_time"],
                "properties": response["properties"]
            }
        except Exception as e:
            print(f"Ошибка при получении информации о базе данных: {e}")
            return {
                "title": "Error",
                "created_time": "N/A",
                "last_edited_time": "N/A",
                "properties": {}
            }

    async def delete_page(self, page_id: str) -> bool:
        """Удаляет страницу"""
        try:
            self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            return True
        except Exception as e:
            print(f"Ошибка при удалении страницы: {e}")
            return False

    async def get_page_content(self, page_id: str, include_blocks=True) -> str:
        """Получает содержимое страницы"""
        try:
            if include_blocks:
                blocks = self.client.blocks.children.list(page_id)
                content = ""
                for block in blocks["results"]:
                    if block["type"] == "paragraph":
                        for text in block["paragraph"]["rich_text"]:
                            content += text["plain_text"] + "\n"
                    elif block["type"] == "heading_1":
                        for text in block["heading_1"]["rich_text"]:
                            content += "# " + text["plain_text"] + "\n"
                    elif block["type"] == "heading_2":
                        for text in block["heading_2"]["rich_text"]:
                            content += "## " + text["plain_text"] + "\n"
                return content
            else:
                page = self.client.pages.retrieve(page_id)
                return page.get("url", "")
        except Exception as e:
            print(f"Ошибка при получении содержимого: {e}")
            return ""

    async def add_page_content(self, page_id: str, content: str, content_type="paragraph") -> bool:
        """Добавляет содержимое на страницу"""
        try:
            block_data = {
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
            
            if content_type == "heading":
                block_data = {
                    "heading_2": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            elif content_type == "list":
                block_data = {
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            elif content_type == "quote":
                block_data = {
                    "quote": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            
            self.client.blocks.children.append(
                page_id=page_id,
                children=[block_data]
            )
            return True
        except Exception as e:
            print(f"Ошибка при добавлении содержимого: {e}")
            return False

    async def get_databases(self, limit=20) -> List[Dict[str, Any]]:
        """Получает список всех баз данных"""
        try:
            response = self.client.search(
                filter={"property": "object", "value": "database"},
                page_size=limit
            )
            databases = []
            for db in response["results"]:
                databases.append({
                    "id": db["id"],
                    "title": db["title"][0]["plain_text"] if db["title"] else "Без названия",
                    "created_time": db["created_time"]
                })
            return databases
        except Exception as e:
            print(f"Ошибка при получении списка баз данных: {e}")
        return []

    async def create_database(self, parent_page_id: str, title: str, description: str = "", properties: Dict = None) -> Dict[str, Any]:
        """Создает новую базу данных"""
        try:
            if properties is None:
                properties = {
                    "Name": {"title": {}},
                    "Теги": {"multi_select": {}},
                    "~Весомость?": {"number": {}},
                    "Статус": {"status": {"options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "blue"},
                        {"name": "Done", "color": "green"}
                    ]}},
                    "Описание": {"rich_text": {}},
                    "Due Date": {"date": {}}
                }
            
            response = self.client.databases.create(
                parent={"page_id": parent_page_id},
                title=[{"text": {"content": title}}],
                properties=properties
            )
            
            return {
                "id": response["id"],
                "title": title,
                "description": description
            }
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            return {"id": "error", "title": title, "description": description}

def test_notion_connection():
    from notion_client import Client
    import os
    token = os.getenv("NOTION_TOKEN")
    print(f"[TEST] NOTION_TOKEN: {token[:8]}..." if token else "[TEST] NOTION_TOKEN: None")
    try:
        client = Client(auth=token)
        user = client.users.list()
        print(f"[TEST] Notion API доступен. Пользователи: {user['results'][0]['name'] if user['results'] else 'нет пользователей'}")
    except Exception as e:
        print(f"[TEST] Ошибка подключения к Notion API: {e}")

if __name__ == "__main__":
    test_notion_connection()

notion_manager = NotionManager() 