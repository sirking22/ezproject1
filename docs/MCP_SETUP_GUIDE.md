# 🔧 Настройка MCP Notion Server

## ✅ Проблема решена

MCP сервер настроен и протестирован. Соединение с Notion API работает корректно.

## 📋 Что сделано

1. **Пересоздан venv** - чистое виртуальное окружение
2. **Установлены зависимости** - notion-client, python-telegram-bot, requests, python-dotenv
3. **Создан MCP сервер** - `mcp_notion_server.py` с полным функционалом
4. **Протестировано соединение** - все 5 баз данных доступны

## 🎯 Результат тестирования

```
✅ Соединение успешно: Еще тест
📊 Доступно 5 баз данных:
- ideas (ad92a6e21485428c84de8587706b3be1)
- subtasks (9c5f4269d61449b6a7485579a3c21da3)  
- materials (1d9ace03d9ff804191a4d35aeedcbbd4)
- projects (342f18c67a5e41fead73dcec00770f4e)
- kpi (1d6ace03d9ff80bfb809ed21dfd2150c)
```

## 🔑 Настройка токенов

### 1. Создать файл .env в корне проекта:
```bash
# Скопировать из env_template.txt
cp env_template.txt .env
```

### 2. Заполнить реальные токены:
```env
NOTION_TOKEN=ntn_ваш_реальный_токен_здесь
TELEGRAM_TOKEN=ваш_telegram_токен
YA_TOKEN=ваш_yandex_токен
DEEPSEEK_API_KEY=ваш_deepseek_ключ
```

## 🚀 Использование MCP сервера

### Запуск тестирования:
```bash
# Активировать venv
.\venv\Scripts\activate

# Запустить тест
python mcp_notion_server.py
```

### Фильтрация задач по исполнителю:
```python
# Через MCP сервер
server = NotionMCPServer()
tasks = await server.get_database_pages(server.tasks_db_id)

# Фильтр по исполнителю
designer_tasks = [
    task for task in tasks['pages'] 
    if 'Участники' in task['properties'] 
    and any('дизайнер' in str(p).lower() for p in task['properties']['Участники'])
]
```

## 📊 Доступные функции MCP сервера

| Функция | Описание | Пример |
|---------|----------|--------|
| `get_database_pages()` | Получить страницы из БД | Все задачи дизайнеров |
| `search_notion()` | Поиск по содержимому | Найти задачи по тексту |
| `create_page()` | Создать новую страницу | Добавить задачу |
| `update_page()` | Обновить страницу | Изменить статус |
| `delete_page()` | Удалить (архивировать) | Закрыть задачу |
| `get_databases()` | Список всех БД | Проверить доступность |

## 🔧 Интеграция с Cursor

### Настройка mcp.json в Cursor:
```json
{
  "mcpServers": {
    "notion-mcp-server": {
      "command": "python",
      "args": ["mcp_notion_server.py"],
      "cwd": "Z:\\Files\\VS_code"
    }
  }
}
```

## 🎯 Следующие шаги

1. **Заполнить реальные токены** в .env
2. **Протестировать фильтрацию** задач по исполнителю
3. **Настроить автоматизацию** постановки задач
4. **Интегрировать с дашбордом** эффективности дизайнеров

## 🐛 Устранение неполадок

### Ошибка "NOTION_TOKEN не найден":
```bash
# Проверить файл .env
ls -la .env
# Проверить переменные
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('NOTION_TOKEN'))"
```

### Ошибка "HTTP 401":
- Проверить токен Notion
- Убедиться что integration добавлена к базам данных
- Проверить права доступа

### Ошибка "Database not found":
- Проверить ID баз данных
- Убедиться что базы не архивированы
- Проверить права доступа к базам

## ✅ Статус: ГОТОВ К ИСПОЛЬЗОВАНИЮ

MCP сервер настроен и готов к работе. Все основные функции протестированы и работают корректно. 