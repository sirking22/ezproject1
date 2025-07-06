# Документация API Notion-Telegram-LLM интеграции

## Обзор

Эта документация покрывает все публичные API, функции и компоненты системы интеграции Notion-Telegram-LLM. Система предоставляет автоматизированное управление задачами, генерацию контента, обработку файлов и интеллектуальную обработку данных.

## Содержание

1. [Основные сервисы](#основные-сервисы)
2. [Модели данных](#модели-данных)
3. [Репозитории](#репозитории)
4. [Обработчики Telegram](#обработчики-telegram)
5. [Утилиты](#утилиты)
6. [Схемы баз данных](#схемы-баз-данных)
7. [Конфигурация](#конфигурация)
8. [Примеры использования](#примеры-использования)

---

## Основные сервисы

### Продвинутый LLM сервис

**Расположение**: `services/llm_service.py`

Продвинутый LLM сервис предоставляет возможности интеллектуальной обработки с использованием больших языковых моделей для операций с Notion.

#### `AdvancedLLMService`

**Конструктор**
```python
def __init__(self):
    """Инициализация LLM сервиса с конфигурацией OpenRouter API."""
```

**Методы**

##### `analyze_database_with_llm(db_name, analysis_type="comprehensive", limit=None)`
Анализирует базу данных Notion с использованием ИИ.

**Параметры:**
- `db_name` (str): Название базы данных для анализа
- `analysis_type` (str): Тип анализа ("comprehensive", "summary", "detailed")
- `limit` (int, optional): Максимальное количество записей для анализа

**Возвращает:** `Dict[str, Any]` - Результаты анализа с выводами и рекомендациями

**Пример:**
```python
llm_service = AdvancedLLMService()
analysis = await llm_service.analyze_database_with_llm(
    db_name="tasks",
    analysis_type="comprehensive",
    limit=50
)
print(f"Анализ: {analysis['llm_analysis']}")
```

##### `bulk_categorize_pages(db_name, category_property, criteria, limit=None)`
Выполняет массовую категоризацию страниц с помощью LLM.

**Параметры:**
- `db_name` (str): Название базы данных
- `category_property` (str): Свойство для обновления категориями
- `criteria` (str): Критерии категоризации
- `limit` (int, optional): Максимальное количество страниц для обработки

**Возвращает:** `Dict[str, Any]` - Результаты с количеством успешных/неудачных операций

**Пример:**
```python
result = await llm_service.bulk_categorize_pages(
    db_name="ideas",
    category_property="Категория",
    criteria="Категоризировать по типу технологии",
    limit=100
)
print(f"Категоризировано {result['categorized_pages']} страниц")
```

##### `intelligent_data_extraction(source_text, target_db, extraction_schema)`
Извлекает структурированные данные из текста и создает записи в Notion.

**Параметры:**
- `source_text` (str): Исходный текст для извлечения
- `target_db` (str): Название целевой базы данных
- `extraction_schema` (Dict[str, str]): Схема для извлечения

**Возвращает:** `Dict[str, Any]` - Результаты извлечения

**Пример:**
```python
result = await llm_service.intelligent_data_extraction(
    source_text="Заметки со встречи: Обсудить сроки нового проекта...",
    target_db="tasks",
    extraction_schema={"title": "task_name", "description": "details"}
)
```

##### `smart_relation_builder(source_db, target_db, relation_criteria)`
Интеллектуально создает связи между записями баз данных.

**Параметры:**
- `source_db` (str): Название исходной базы данных
- `target_db` (str): Название целевой базы данных
- `relation_criteria` (str): Критерии для создания связей

**Возвращает:** `Dict[str, Any]` - Результаты создания связей

**Пример:**
```python
result = await llm_service.smart_relation_builder(
    source_db="tasks",
    target_db="projects",
    relation_criteria="Связать задачи с соответствующими проектами"
)
```

##### `bulk_content_generation(db_name, template_field, target_field, generation_prompt, limit=None)`
Генерирует контент для множественных записей базы данных.

**Параметры:**
- `db_name` (str): Название базы данных
- `template_field` (str): Поле с шаблонными данными
- `target_field` (str): Поле для обновления сгенерированным контентом
- `generation_prompt` (str): Промпт для генерации контента
- `limit` (int, optional): Максимальное количество записей для обработки

**Возвращает:** `Dict[str, Any]` - Результаты генерации

**Пример:**
```python
result = await llm_service.bulk_content_generation(
    db_name="ideas",
    template_field="Name",
    target_field="Описание",
    generation_prompt="Создать подробное описание на основе названия идеи",
    limit=50
)
```

---

### Продвинутый Notion сервис

**Расположение**: `services/advanced_notion_service.py`

Предоставляет продвинутые операции Notion с массовым редактированием и групповыми операциями.

#### `AdvancedNotionService`

**Конструктор**
```python
def __init__(self):
    """Инициализация с токеном Notion и конфигурацией базы данных."""
```

**Методы**

##### `get_database_schema(db_id)`
Получает информацию о схеме базы данных.

**Параметры:**
- `db_id` (str): ID базы данных

**Возвращает:** `Dict[str, Any]` - Схема базы данных

**Пример:**
```python
notion_service = AdvancedNotionService()
schema = await notion_service.get_database_schema("database_id")
```

##### `query_database_bulk(db_id, filters=None, sorts=None, limit=None)`
Выполняет массовые запросы к базе данных с фильтрацией и сортировкой.

**Параметры:**
- `db_id` (str): ID базы данных
- `filters` (List[NotionFilter], optional): Фильтры запроса
- `sorts` (List[Dict], optional): Параметры сортировки
- `limit` (int, optional): Лимит результатов

**Возвращает:** `List[Dict]` - Результаты запроса

**Пример:**
```python
from services.advanced_notion_service import NotionFilter

filters = [
    NotionFilter("Status", "select", {"equals": "In Progress"})
]
results = await notion_service.query_database_bulk(
    db_id="database_id",
    filters=filters,
    limit=100
)
```

##### `update_pages_bulk(page_updates)`
Выполняет массовые обновления страниц.

**Параметры:**
- `page_updates` (List[Tuple[str, List[NotionUpdate]]]): Список обновлений страниц

**Возвращает:** `List[Dict]` - Результаты обновлений

**Пример:**
```python
from services.advanced_notion_service import NotionUpdate

updates = [
    ("page_id_1", [NotionUpdate("Status", "Done", "select")]),
    ("page_id_2", [NotionUpdate("Priority", "High", "select")])
]
results = await notion_service.update_pages_bulk(updates)
```

---

### Базовый Notion сервис

**Расположение**: `src/services/notion_service.py`

Основной Notion сервис для стандартных операций.

#### `NotionService`

**Конструктор**
```python
def __init__(self):
    """Инициализация с настройками и Notion клиентом."""
```

**Методы**

##### `initialize()`
Инициализирует сессию Notion клиента.

**Возвращает:** `None`

**Пример:**
```python
notion_service = NotionService()
await notion_service.initialize()
```

##### `query_database(database_id, filter_conditions=None, sorts=None)`
Запрашивает базу данных с опциональными фильтрами и сортировкой.

**Параметры:**
- `database_id` (str): ID базы данных
- `filter_conditions` (Dict, optional): Условия фильтрации
- `sorts` (List[Dict], optional): Параметры сортировки

**Возвращает:** `List[NotionPage]` - Результаты запроса

**Пример:**
```python
pages = await notion_service.query_database(
    database_id="database_id",
    filter_conditions={
        "property": "Status",
        "select": {"equals": "In Progress"}
    }
)
```

##### `create_page(database_id, properties, content=None)`
Создает новую страницу в указанной базе данных.

**Параметры:**
- `database_id` (str): ID базы данных
- `properties` (Dict[str, Any]): Свойства страницы
- `content` (List[Dict], optional): Блоки контента страницы

**Возвращает:** `NotionPage` - Созданная страница

**Пример:**
```python
properties = {
    "Name": {"title": [{"text": {"content": "Новая задача"}}]},
    "Status": {"select": {"name": "To Do"}}
}
page = await notion_service.create_page("database_id", properties)
```

---

## Модели данных

### Notion модели

**Расположение**: `src/models/notion_models.py`

#### `NotionPage`
Представляет страницу Notion.

**Поля:**
- `id` (str): ID страницы
- `created_time` (datetime): Временная метка создания
- `last_edited_time` (datetime): Временная метка последнего редактирования
- `archived` (bool): Статус архивации
- `properties` (Dict): Свойства страницы

**Пример:**
```python
page = NotionPage(
    id="page_id",
    created_time=datetime.now(),
    last_edited_time=datetime.now(),
    properties={"Name": {"title": [{"text": {"content": "Название задачи"}}]}}
)
```

#### `Task`
Модель данных задачи.

**Поля:**
- `id` (str): ID задачи
- `title` (str): Название задачи
- `description` (str): Описание задачи
- `status` (str): Статус задачи
- `priority` (str): Приоритет задачи
- `tags` (List[str]): Теги задачи
- `due_date` (datetime): Срок выполнения
- `created_at` (datetime): Временная метка создания
- `updated_at` (datetime): Временная метка обновления

**Пример:**
```python
task = Task(
    id="task_id",
    title="Завершить документацию",
    description="Написать полную документацию API",
    status="In Progress",
    priority="High",
    tags=["документация", "api"],
    due_date=datetime.now() + timedelta(days=7)
)
```

---

## Репозитории

### Notion репозиторий

**Расположение**: `src/repositories/notion_repository.py`

#### `NotionTaskRepository`
Репозиторий для операций с задачами.

**Конструктор**
```python
def __init__(self, client: AsyncClient, database_id: str):
    """Инициализация с Notion клиентом и ID базы данных."""
```

**Методы**

##### `validate_database()`
Проверяет подключение к базе данных и структуру.

**Возвращает:** `Tuple[bool, str]` - Статус успеха и сообщение

**Пример:**
```python
repo = NotionTaskRepository(client, "database_id")
is_valid, message = await repo.validate_database()
```

##### `create(task)`
Создает новую задачу.

**Параметры:**
- `task` (TaskDTO): Данные задачи

**Возвращает:** `TaskDTO` - Созданная задача

**Пример:**
```python
task_data = TaskDTO(title="Новая задача", status="To Do")
created_task = await repo.create(task_data)
```

##### `list(params=None)`
Список задач с опциональной фильтрацией.

**Параметры:**
- `params` (Dict, optional): Параметры фильтрации

**Возвращает:** `List[TaskDTO]` - Список задач

**Пример:**
```python
# Получить все активные задачи
tasks = await repo.list({
    "status": {"not_equals": "Completed"}
})

# Получить высокоприоритетные задачи
high_priority_tasks = await repo.list({
    "priority": "High"
})
```

---

## Обработчики Telegram

### Обработчик задач

**Расположение**: `src/services/telegram/handlers/tasks.py`

#### `TaskHandler`
Обрабатывает команды Telegram, связанные с задачами.

**Конструктор**
```python
def __init__(self, task_repository: NotionTaskRepository):
    """Инициализация с репозиторием задач."""
```

**Методы**

##### `task_command(update, context)`
Обрабатывает команду /task.

**Параметры:**
- `update` (Update): Обновление Telegram
- `context` (ContextTypes.DEFAULT_TYPE): Контекст бота

**Возвращает:** `None`

**Пример:**
```python
handler = TaskHandler(task_repository)
await handler.task_command(update, context)
```

##### `list_tasks(update, context)`
Отображает список задач пользователя.

**Параметры:**
- `update` (Update): Обновление Telegram
- `context` (ContextTypes.DEFAULT_TYPE): Контекст бота

**Возвращает:** `None`

**Пример:**
```python
await handler.list_tasks(update, context)
```

---

### Основной бот

**Расположение**: `simple_bot.py`

#### `LLMProcessor`
Обрабатывает естественный язык с помощью LLM.

**Конструктор**
```python
def __init__(self):
    """Инициализация с конфигурацией LLM."""
```

**Методы**

##### `parse_natural_language(text)`
Парсит текст на естественном языке в структурированные данные.

**Параметры:**
- `text` (str): Текст на естественном языке

**Возвращает:** `Dict[str, Any]` - Распарсенные данные

**Пример:**
```python
processor = LLMProcessor()
result = await processor.parse_natural_language(
    "Создать высокоприоритетную задачу для дизайна нового сайта"
)
```

#### `YandexUploader`
Обрабатывает загрузку файлов в Yandex.Disk.

**Конструктор**
```python
def __init__(self):
    """Инициализация с конфигурацией Yandex.Disk."""
```

**Методы**

##### `upload_file(file_url, filename)`
Загружает файл в Yandex.Disk.

**Параметры:**
- `file_url` (str): URL исходного файла
- `filename` (str): Целевое имя файла

**Возвращает:** `Dict[str, Any]` - Результаты загрузки

**Пример:**
```python
uploader = YandexUploader()
result = await uploader.upload_file(
    file_url="https://telegram.org/file.jpg",
    filename="uploaded_image.jpg"
)
```

---

## Утилиты

### Консольные помощники

**Расположение**: `utils/console_helpers.py`

#### `setup_logging(level=logging.INFO, log_file=None)`
Настраивает логирование с цветным форматированием.

**Параметры:**
- `level` (int): Уровень логирования
- `log_file` (str, optional): Путь к файлу логов

**Возвращает:** `logging.Logger` - Настроенный логгер

**Пример:**
```python
from utils.console_helpers import setup_logging
logger = setup_logging(level=logging.INFO, log_file="app.log")
```

#### `Timer`
Контекстный менеджер для измерения времени выполнения.

**Конструктор**
```python
def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
    """Инициализация с названием операции и логгером."""
```

**Пример:**
```python
with Timer("Вызов API"):
    response = await make_api_call()
```

---

## Схемы баз данных

### Управление схемами баз данных

**Расположение**: `notion_database_schemas.py`

#### `DatabaseSchema`
Определение схемы базы данных.

**Поля:**
- `name` (str): Название базы данных
- `database_id` (str): ID базы данных Notion
- `description` (str): Описание базы данных
- `properties` (Dict): Определения свойств
- `status_options` (Dict): Опции полей статуса
- `select_options` (Dict): Опции полей выбора
- `multi_select_options` (Dict): Опции полей множественного выбора
- `relations` (Dict): Определения связей

**Пример:**
```python
schema = DatabaseSchema(
    name="Задачи",
    database_id="database_id",
    description="База данных задач проекта",
    properties={
        "Name": {"type": "title"},
        "Status": {"type": "status"},
        "Priority": {"type": "select"}
    },
    status_options={
        "Status": ["To Do", "In Progress", "Done"]
    }
)
```

#### Функции схем

##### `get_database_schema(db_name)`
Получает схему базы данных по названию.

**Параметры:**
- `db_name` (str): Название базы данных

**Возвращает:** `Optional[DatabaseSchema]` - Схема базы данных

**Пример:**
```python
schema = get_database_schema("tasks")
```

##### `validate_property_value(db_name, property_name, value)`
Проверяет значение свойства против схемы.

**Параметры:**
- `db_name` (str): Название базы данных
- `property_name` (str): Название свойства
- `value` (str): Значение для проверки

**Возвращает:** `bool` - Результат проверки

**Пример:**
```python
is_valid = validate_property_value("tasks", "Status", "In Progress")
```

---

## Примеры использования

### Полный рабочий процесс управления задачами

```python
import asyncio
from src.services.notion_service import NotionService
from src.repositories.notion_repository import NotionTaskRepository
from notion_client import AsyncClient

async def main():
    # Инициализация сервисов
    notion_service = NotionService()
    await notion_service.initialize()
    
    # Создание репозитория задач
    client = AsyncClient(auth="your_token")
    task_repo = NotionTaskRepository(client, "database_id")
    
    # Проверка базы данных
    is_valid, message = await task_repo.validate_database()
    if not is_valid:
        print(f"Ошибка проверки базы данных: {message}")
        return
    
    # Создание новой задачи
    from src.models.base import TaskDTO
    task_data = TaskDTO(
        title="Завершить документацию API",
        description="Написать полную документацию",
        status="In Progress",
        priority="High"
    )
    
    # Сохранение в Notion
    created_task = await task_repo.create(task_data)
    print(f"Создана задача: {created_task.id}")
    
    # Список всех задач
    tasks = await task_repo.list()
    print(f"Всего задач: {len(tasks)}")
    
    # Обновление статуса задачи
    task_data.status = "Done"
    updated_task = await task_repo.update(created_task.id, task_data)
    print(f"Обновлен статус задачи: {updated_task.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Анализ базы данных с помощью LLM

```python
from services.llm_service import AdvancedLLMService

async def analyze_projects():
    llm_service = AdvancedLLMService()
    
    # Анализ содержимого базы данных
    analysis = await llm_service.analyze_database_with_llm(
        db_name="projects",
        analysis_type="comprehensive",
        limit=100
    )
    
    print("Результаты анализа базы данных:")
    print(f"Всего страниц: {analysis['data_summary']['total_pages']}")
    print(f"Выводы LLM: {analysis['llm_analysis']}")
    
    # Категоризация проектов
    categorization = await llm_service.bulk_categorize_pages(
        db_name="projects",
        category_property="Category",
        criteria="Категоризировать по типу и сложности проекта",
        limit=50
    )
    
    print(f"Категоризировано {categorization['categorized_pages']} проектов")

# Запуск анализа
asyncio.run(analyze_projects())
```

### Загрузка и обработка файлов

```python
from simple_bot import YandexUploader, LLMProcessor, NotionManager

async def process_uploaded_file():
    # Инициализация компонентов
    uploader = YandexUploader()
    processor = LLMProcessor()
    notion_manager = NotionManager()
    
    # Загрузка файла
    file_url = "https://example.com/document.pdf"
    filename = "project_document.pdf"
    
    upload_result = await uploader.upload_file(file_url, filename)
    
    if upload_result['success']:
        # Обработка с помощью LLM
        analysis = await processor.parse_natural_language(
            "Это проектный документ, содержащий технические спецификации дизайна"
        )
        
        # Создание записи в Notion
        material = await notion_manager.create_material(
            fields={
                "name": analysis['name'],
                "description": analysis['description'],
                "tags": analysis.get('tags', [])
            },
            file_url=upload_result['url'],
            file_name=filename
        )
        
        print(f"Создан материал: {material['id']}")

# Запуск обработки
asyncio.run(process_uploaded_file())
```

---

## Обработка ошибок

### Типичные паттерны ошибок

```python
from src.services.notion_service import NotionService, NotionError

async def handle_notion_operations():
    notion_service = NotionService()
    
    try:
        await notion_service.initialize()
        
        # Выполнение операций
        pages = await notion_service.query_database("database_id")
        
    except NotionError as e:
        print(f"Ошибка Notion API: {e}")
        
    except Exception as e:
        print(f"Общая ошибка: {e}")
        
    finally:
        await notion_service.cleanup()
```

---

## Лучшие практики

### 1. Всегда инициализируйте сервисы
```python
# Хорошо
notion_service = NotionService()
await notion_service.initialize()

# Использование сервиса
await notion_service.query_database("db_id")

# Очистка
await notion_service.cleanup()
```

### 2. Проверяйте подключения к базам данных
```python
repo = NotionTaskRepository(client, database_id)
is_valid, message = await repo.validate_database()
if not is_valid:
    raise ValueError(f"Ошибка проверки базы данных: {message}")
```

### 3. Используйте проверку схем
```python
from notion_database_schemas import validate_property_value

# Проверка перед созданием/обновлением
if not validate_property_value("tasks", "Status", status_value):
    raise ValueError(f"Недопустимый статус: {status_value}")
```

### 4. Эффективно обрабатывайте массовые операции
```python
# Обработка пакетами
batch_size = 10
for i in range(0, len(items), batch_size):
    batch = items[i:i + batch_size]
    await process_batch(batch)
    await asyncio.sleep(0.1)  # Ограничение скорости
```

---

Эта документация предоставляет полное покрытие всех публичных API, функций и компонентов системы. Для дополнительной помощи или уточнений по конкретным компонентам, обращайтесь к исходному коду или команде разработки.