# 🛠️ ПОЛНОЕ РУКОВОДСТВО ПО НАСТРОЙКЕ

## 📋 ПРЕДВАРИТЕЛЬНАЯ ПОДГОТОВКА

### 1. Telegram Bot Setup
1. Откройте @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
4. Добавьте бота в нужные каналы (если требуется)

### 2. Notion Integration Setup
1. Перейдите на https://www.notion.so/my-integrations
2. Создайте новую интеграцию
3. Получите Internal Integration Token
4. Добавьте интеграцию в нужные страницы/базы данных

### 3. Базы данных Notion
Создайте или подготовьте базы данных:
- **PLATFORMS** - для статистики платформ
- **CONTENT_PLAN** - для контент-плана
- **TASKS** - для задач (опционально)
- **EMPLOYEES** - для сотрудников (опционально)

## 🔧 НАСТРОЙКА ПРОЕКТА

### 1. Установка зависимостей
```bash
cd .Life
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
```bash
# Скопируйте пример
cp env_example.txt .env

# Отредактируйте .env файл
nano .env
```

### 3. Минимальная конфигурация .env
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
NOTION_TOKEN=your_notion_token_here
NOTION_PLATFORMS_DB_ID=your_platforms_db_id
NOTION_CONTENT_PLAN_DB_ID=your_content_db_id
```

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Тестирование компонентов
```bash
python quick_start.py
```

### 2. Базовое использование
```python
from src.telegram.core import TelegramAnalytics
from src.notion.core import NotionService
from src.integrations.telegram_notion import TelegramNotionIntegration

# Инициализация
telegram = TelegramAnalytics()
notion = NotionService()
integration = TelegramNotionIntegration()

# Синхронизация канала
integration.run_full_integration()
```

## 📊 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Telegram Analytics
```python
from src.telegram.core import TelegramAnalytics

# Создание экземпляра
analytics = TelegramAnalytics()

# Тест подключения
if analytics.test_bot_connection():
    print("✅ Бот подключен!")
    
    # Анализ канала
    results = analytics.analyze_channel_statistics()
    print(f"Подписчики: {results['member_count']}")
```

### Notion Operations
```python
from src.notion.core import NotionService
import asyncio

async def notion_example():
    notion = NotionService()
    await notion.initialize()
    
    # Создание страницы
    page = await notion.create_page(
        database_id="your_db_id",
        properties={
            "Name": {"title": [{"text": {"content": "Test Page"}}]},
            "Status": {"select": {"name": "Active"}}
        }
    )
    
    await notion.cleanup()

# Запуск
asyncio.run(notion_example())
```

### Integration Example
```python
from src.integrations.telegram_notion import TelegramNotionIntegration

# Полная интеграция
integration = TelegramNotionIntegration()
success = integration.run_full_integration()

if success:
    print("✅ Данные синхронизированы!")
else:
    print("❌ Ошибка синхронизации")
```

## 🔍 РЕШЕНИЕ ПРОБЛЕМ

### Telegram API Errors
- **401 Unauthorized**: Проверьте TELEGRAM_BOT_TOKEN
- **403 Forbidden**: Бот не добавлен в канал
- **400 Bad Request**: Неверный chat_id

### Notion API Errors
- **401 Unauthorized**: Проверьте NOTION_TOKEN
- **403 Forbidden**: Интеграция не добавлена в базу данных
- **404 Not Found**: Неверный database_id

### Common Issues
1. **Import Errors**: Установите зависимости `pip install -r requirements.txt`
2. **Environment Variables**: Проверьте .env файл
3. **Database Permissions**: Добавьте интеграцию в базы данных Notion

## 📈 РАСШИРЕННЫЕ ВОЗМОЖНОСТИ

### Enhanced Scraper
```python
from src.telegram.enhanced_scraper import TelegramEnhancedScraper

scraper = TelegramEnhancedScraper("channel_name")
data = scraper.scrape_all_data()
```

### Analytics Framework
```python
from src.telegram.analytics import TelegramAnalyticsFramework

framework = TelegramAnalyticsFramework()
metrics = framework.get_channel_metrics("@channel")
```

### LLM Integration
```python
from src.notion.llm_service import NotionLLMService

llm_service = NotionLLMService()
await llm_service.initialize()

# Генерация контента
content = await llm_service.generate_content_idea("topic")
```

## 🔄 АВТОМАТИЗАЦИЯ

### Cron Job (Linux/Mac)
```bash
# Добавьте в crontab
0 */6 * * * cd /path/to/.Life && python main.py
```

### Windows Task Scheduler
1. Откройте Task Scheduler
2. Создайте Basic Task
3. Укажите путь к Python и скрипту
4. Настройте расписание

### Docker (опционально)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 📝 ЛОГИРОВАНИЕ

### Настройка логов
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration.log'),
        logging.StreamHandler()
    ]
)
```

### Мониторинг
- Проверяйте логи регулярно
- Настройте алерты на ошибки
- Мониторьте использование API лимитов

## 🚀 ГОТОВО!

Теперь у вас есть полностью настроенная система интеграции Telegram + Notion. Используйте компоненты в своих проектах! 