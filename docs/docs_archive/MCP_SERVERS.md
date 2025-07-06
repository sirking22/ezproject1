# MCP Servers Documentation

## Обзор

Проект использует Model Context Protocol (MCP) для интеграции с различными сервисами. Реализованы 4 основных MCP сервера:

1. **Notion MCP Server** - работа с Notion API
2. **Telegram MCP Server** - интеграция с Telegram Bot API
3. **LLM MCP Server** - работа с языковыми моделями
4. **Analytics MCP Server** - аналитика и отчеты

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Manager   │    │  Notion Client  │    │ Telegram Client │
│                 │    │                 │    │                 │
│  - Start/Stop   │    │  - Get Pages    │    │  - Send Message │
│  - Test Status  │    │  - Create Page  │    │  - Get Updates  │
│  - Integration  │    │  - Search       │    │  - Webhook      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   LLM Client    │    │ Analytics Client│
                    │                 │    │                 │
                    │  - Generate     │    │  - Reports      │
                    │  - Analyze      │    │  - KPI          │
                    │  - Translate    │    │  - Trends       │
                    └─────────────────┘    └─────────────────┘
```

## Конфигурация

### Файл конфигурации: `.cursor/mcp.json`

```json
{
    "mcpServers": {
        "notion-mcp-server": {
            "type": "command",
            "command": "python",
            "args": ["notion_mcp_server.py"],
            "env": {
                "NOTION_TOKEN": "${NOTION_TOKEN}",
                "NOTION_DATABASE_ID": "${NOTION_IDEAS_DB_ID}"
            }
        },
        "telegram-mcp-server": {
            "type": "command",
            "command": "python",
            "args": ["telegram_mcp_server.py"],
            "env": {
                "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
                "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID}"
            }
        },
        "llm-mcp-server": {
            "type": "command",
            "command": "python",
            "args": ["llm_mcp_server.py"],
            "env": {
                "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
            }
        },
        "analytics-mcp-server": {
            "type": "command",
            "command": "python",
            "args": ["analytics_mcp_server.py"],
            "env": {
                "NOTION_TOKEN": "${NOTION_TOKEN}",
                "NOTION_DATABASE_ID": "${NOTION_IDEAS_DB_ID}"
            }
        }
    }
}
```

## Серверы

### 1. Notion MCP Server

**Файл:** `notion_mcp_server.py`

**Инструменты:**
- `notion_get_pages` - получить страницы из базы данных
- `notion_create_page` - создать новую страницу
- `notion_update_page` - обновить существующую страницу
- `notion_search_pages` - поиск страниц по тексту
- `notion_get_database_info` - получить информацию о базе данных
- `notion_bulk_update` - массовое обновление страниц

**Пример использования:**
```python
from notion_mcp_client import NotionMCPClient

client = NotionMCPClient()
await client.start_server()

# Получить страницы
pages = await client.get_pages("database_id", limit=10)

# Создать страницу
result = await client.create_page(
    "database_id",
    "Название",
    description="Описание",
    tags=["тег1", "тег2"],
    importance=8
)
```

### 2. Telegram MCP Server

**Файл:** `telegram_mcp_server.py`

**Инструменты:**
- `telegram_send_message` - отправить сообщение
- `telegram_send_photo` - отправить фото
- `telegram_send_document` - отправить документ
- `telegram_get_updates` - получить обновления
- `telegram_create_task` - создать задачу из сообщения
- `telegram_process_learning` - обработать обучающее сообщение
- `telegram_get_chat_info` - получить информацию о чате
- `telegram_set_webhook` - установить webhook

**Пример использования:**
```python
from telegram_mcp_client import TelegramMCPClient

client = TelegramMCPClient()
await client.start_server()

# Отправить сообщение
result = await client.send_message(
    "chat_id",
    "Привет! 👋",
    "HTML"
)

# Создать задачу из сообщения
task = await client.create_task(
    "Нужно обновить документацию",
    "user_id",
    "chat_id"
)
```

### 3. LLM MCP Server

**Файл:** `llm_mcp_server.py`

**Инструменты:**
- `llm_generate_response` - сгенерировать ответ
- `llm_analyze_text` - анализировать текст
- `llm_extract_entities` - извлечь сущности
- `llm_classify_content` - классифицировать контент
- `llm_generate_title` - сгенерировать заголовок
- `llm_translate_text` - перевести текст
- `llm_generate_tags` - сгенерировать теги
- `llm_improve_text` - улучшить текст

**Пример использования:**
```python
from llm_mcp_client import LLMMCPClient

client = LLMMCPClient()
await client.start_server()

# Сгенерировать ответ
response = await client.generate_response(
    "Объясни квантовую физику простыми словами",
    model="gpt-4",
    max_tokens=300
)

# Анализировать настроение
sentiment = await client.analyze_text(
    "Этот продукт отлично работает!",
    "sentiment"
)

# Сгенерировать заголовок
title = await client.generate_title(
    "Статья о новых технологиях",
    style="professional"
)
```

### 4. Analytics MCP Server

**Файл:** `analytics_mcp_server.py`

**Инструменты:**
- `analytics_generate_report` - сгенерировать отчет
- `analytics_get_kpi` - получить KPI метрики
- `analytics_trend_analysis` - анализ трендов
- `analytics_compare_periods` - сравнение периодов
- `analytics_export_data` - экспорт данных
- `analytics_predict_trends` - прогнозирование трендов
- `analytics_anomaly_detection` - обнаружение аномалий
- `analytics_create_dashboard` - создать дашборд

**Пример использования:**
```python
from analytics_mcp_client import AnalyticsMCPClient

client = AnalyticsMCPClient()
await client.start_server()

# Сгенерировать отчет
report = await client.generate_report(
    "database_id",
    "weekly",
    metrics=["completion", "productivity"]
)

# Получить KPI
kpi = await client.get_kpi(
    "database_id",
    "completion_rate",
    "week"
)

# Анализ трендов
trends = await client.trend_analysis(
    "database_id",
    "productivity",
    "30d"
)
```

## MCP Manager

**Файл:** `mcp_manager.py`

Централизованное управление всеми MCP серверами.

**Основные функции:**
- `start_all_servers()` - запуск всех серверов
- `stop_all_servers()` - остановка всех серверов
- `test_all_servers()` - тестирование всех серверов
- `create_task_with_llm()` - создание задачи с помощью LLM
- `generate_weekly_report()` - генерация еженедельного отчета

**Пример использования:**
```python
from mcp_manager import MCPManager

manager = MCPManager()

# Запустить все серверы
await manager.start_all_servers()

# Проверить статус
status = manager.get_servers_status()
print(status)

# Создать задачу с помощью LLM
task = await manager.create_task_with_llm(
    "Нужно обновить документацию",
    "user_id",
    "chat_id"
)

# Сгенерировать отчет
report = await manager.generate_weekly_report()

# Остановить все серверы
await manager.stop_all_servers()
```

## Переменные окружения

Необходимые переменные в `.env`:

```env
# Notion
NOTION_TOKEN=your_notion_token
NOTION_IDEAS_DB_ID=your_database_id

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# LLM
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Запуск и тестирование

### Запуск всех серверов:
```bash
python mcp_manager.py
```

### Тестирование отдельных клиентов:
```bash
python notion_mcp_client.py
python telegram_mcp_client.py
python llm_mcp_client.py
python analytics_mcp_client.py
```

### Тестирование серверов:
```bash
python notion_mcp_server.py
python telegram_mcp_server.py
python llm_mcp_server.py
python analytics_mcp_server.py
```

## Логирование

Все MCP серверы и клиенты используют централизованное логирование:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Сервер запущен")
logger.error("❌ Ошибка: {error}")
logger.warning("⚠️ Предупреждение")
```

## Обработка ошибок

Все клиенты включают обработку ошибок:

- Автоматический перезапуск серверов при сбоях
- Graceful shutdown при остановке
- Логирование всех ошибок
- Fallback механизмы для критических операций

## Производительность

- Асинхронная обработка всех операций
- Параллельный запуск серверов
- Кэширование результатов
- Оптимизированные запросы к API

## Безопасность

- Все токены хранятся в переменных окружения
- Валидация входных данных
- Rate limiting для API запросов
- Безопасная передача данных через MCP протокол 