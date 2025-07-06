# Быстрый старт

## Обзор

Это руководство поможет запустить систему интеграции Notion-Telegram-LLM менее чем за 15 минут.

## Требования

- Python 3.8 или выше
- Аккаунт Notion с доступом к API
- Токен Telegram бота
- API ключ OpenRouter для LLM функций
- Аккаунт Yandex.Disk (для загрузки файлов)

## Установка

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd notion-telegram-llm
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env` в корне проекта:

```bash
# Основные API ключи
NOTION_TOKEN=secret_xxxxxxxxxxxx
TELEGRAM_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
YA_ACCESS_TOKEN=y0_xxxxxxxxxxxx

# ID баз данных (получить из URL Notion)
NOTION_TASKS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_IDEAS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_MATERIALS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_PROJECTS_DB_ID=12345678-1234-1234-1234-123456789abc

# Опционально: Конфигурация LLM
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 3. Настройка Notion

#### Создание необходимых баз данных

1. **База данных задач**
   - Создайте новую базу в Notion
   - Добавьте свойства:
     - `Задача` (Title)
     - `Статус` (Status: To do, In Progress, Done)
     - `Участники` (People)
     - `Проект` (Relation к проектам)
     - `Категория` (Multi-select)
     - `Приоритет` (Select: High, Medium, Low)
   - Скопируйте ID базы данных из URL

2. **База данных идей**
   - Создайте базу со свойствами:
     - `Name` (Title)
     - `Статус` (Status)
     - `Теги` (Multi-select)
     - `Описание` (Rich text)
     - `URL` (URL)

3. **База данных материалов**
   - Создайте базу со свойствами:
     - `Name` (Title)
     - `Статус` (Status)
     - `URL` (URL)
     - `Описание` (Rich text)

#### Настройка интеграции Notion

1. Перейдите на https://www.notion.so/my-integrations
2. Создайте новую интеграцию
3. Скопируйте токен интеграции
4. Поделитесь вашими базами данных с интеграцией

## Основное использование

### 1. Запуск Telegram бота

```bash
python simple_bot.py
```

### 2. Тестирование базовых команд

Отправьте эти команды вашему боту:

- `/start` - Инициализация бота
- `/task` - Меню управления задачами
- `/stats` - Просмотр статистики использования
- Отправка файла - Автозагрузка в Yandex.Disk + создание записи в Notion

### 3. Тестирование основных сервисов

```python
# Тестирование Notion сервиса
from src.services.notion_service import NotionService

async def test_notion():
    service = NotionService()
    await service.initialize()
    
    # Список задач
    tasks = await service.query_database("your_tasks_db_id")
    print(f"Найдено {len(tasks)} задач")
    
    await service.cleanup()

# Запуск теста
import asyncio
asyncio.run(test_notion())
```

### 4. Тестирование LLM сервиса

```python
# Тестирование LLM анализа
from services.llm_service import AdvancedLLMService

async def test_llm():
    llm_service = AdvancedLLMService()
    
    # Анализ базы данных
    analysis = await llm_service.analyze_database_with_llm(
        db_name="tasks",
        analysis_type="summary",
        limit=10
    )
    
    print(f"Анализ: {analysis}")

asyncio.run(test_llm())
```

## Основные операции

### Создание задачи

```python
from src.repositories.notion_repository import NotionTaskRepository
from src.models.base import TaskDTO
from notion_client import AsyncClient

async def create_task():
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    repo = NotionTaskRepository(client, os.getenv("NOTION_TASKS_DB_ID"))
    
    task = TaskDTO(
        title="Тестовая задача",
        description="Тестирование API",
        status="To Do",
        priority="High"
    )
    
    created = await repo.create(task)
    print(f"Создана задача: {created.id}")

asyncio.run(create_task())
```

### Загрузка файла и создание материала

```python
from simple_bot import YandexUploader, NotionManager

async def upload_and_save():
    uploader = YandexUploader()
    notion_manager = NotionManager()
    
    # Загрузка файла
    result = await uploader.upload_file(
        "https://example.com/document.pdf",
        "test_document.pdf"
    )
    
    if result['success']:
        # Создание записи материала
        material = await notion_manager.create_material(
            fields={
                "name": "Тестовый документ",
                "description": "Пример загрузки документа"
            },
            file_url=result['url'],
            file_name="test_document.pdf"
        )
        print(f"Создан материал: {material}")

asyncio.run(upload_and_save())
```

## Решение проблем

### Типичные проблемы

1. **База данных не найдена**
   - Проверьте ID базы в .env
   - Убедитесь, что интеграция имеет доступ к базе
   - Проверьте, что база существует и не архивирована

2. **Ошибки аутентификации**
   - Проверьте правильность API токенов
   - Убедитесь, что токены имеют необходимые разрешения
   - Проверьте срок действия токенов

3. **Ограничения скорости**
   - Notion API: 3 запроса/секунду
   - Добавьте задержки между запросами
   - Используйте массовые операции когда возможно

### Проверка работоспособности

```python
async def health_check():
    """Проверка работы всех сервисов"""
    
    # Тестирование подключения к Notion
    try:
        from src.services.notion_service import NotionService
        service = NotionService()
        await service.initialize()
        databases = await service.query_database("your_db_id")
        print(f"✅ Notion: {len(databases)} записей")
        await service.cleanup()
    except Exception as e:
        print(f"❌ Notion: {e}")
    
    # Тестирование LLM сервиса
    try:
        from services.llm_service import AdvancedLLMService
        llm = AdvancedLLMService()
        result = await llm._call_llm("Тестовое сообщение", "general")
        print(f"✅ LLM: Ответ получен")
    except Exception as e:
        print(f"❌ LLM: {e}")

asyncio.run(health_check())
```

## Следующие шаги

1. **Прочитайте полную документацию API** - `docs/API_DOCUMENTATION_RU.md`
2. **Изучите примеры** - Проверьте директорию `examples/`
3. **Настройте среду разработки** - См. `docs/DEVELOPMENT_GUIDE.md`
4. **Настройте продвинутые функции** - Схемы баз данных, кастомные LLM промпты

## Получение помощи

- **Документация**: Полный справочник API в `docs/`
- **Проблемы**: Проверьте существующие проблемы и частые вопросы
- **Примеры кода**: Изучите кодовую базу для примеров
- **Справочник схем**: Проверьте `notion_database_schemas.py` для структуры базы данных

---

Теперь вы готовы начать работу с системой интеграции Notion-Telegram-LLM! 🚀