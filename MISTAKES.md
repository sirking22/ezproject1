# 🚨 MISTAKES.md - ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

## 📋 СОДЕРЖАНИЕ
1. [Notion API Ошибки](#notion-api-ошибки)
2. [Telegram Bot Ошибки](#telegram-bot-ошибки)
3. [LLM/API Ошибки](#llmapi-ошибки)
4. [MCP Серверы](#mcp-серверы)
5. [Переменные окружения](#переменные-окружения)
6. [Структурные ошибки](#структурные-ошибки)
7. [Код ошибки](#код-ошибки)
8. [Система подзадач Notion](#система-подзадач-notion)
9. [Формулы Notion API](#формулы-notion-api)
10. [Быстрые решения](#быстрые-решения)

---

## 🔥 NOTION API ОШИБКИ

### HTTP 401 'restricted from accessing public API'
**Проблема**: Notion API возвращает ошибку доступа
**Решение**:
1. Проверить токен в `.env` файле
2. Убедиться в правах доступа к базе данных
3. Пересоздать интеграцию в Notion если нужно
4. Проверить ID баз данных в настройках

### Ошибки создания страниц
**Проблема**: Не удается создать страницы в Notion
**Решение**:
1. Проверить схему базы данных (должны быть поля: Description, Tags, Importance, Status)
2. Убедиться в правильности ID базы данных
3. Проверить права интеграции на запись

### Ошибки чтения данных
**Проблема**: Не удается прочитать данные из Notion
**Решение**:
1. Проверить валидность токена
2. Убедиться в существовании страниц/баз
3. Проверить права доступа интеграции

---

## 🤖 TELEGRAM BOT ОШИБКИ

### Event loop errors
**Проблема**: Бот падает с ошибками event loop
**Решение**:
1. `taskkill /F /IM python.exe` - убить все процессы Python
2. Запустить `enhanced_materials_bot_v3.py`
3. Проверить логи: `Get-Content bot.log -Tail 10`

### Бот не отвечает
**Проблема**: Telegram бот не реагирует на команды
**Решение**:
1. Проверить токен бота в `.env`
2. Убедиться что бот запущен
3. Проверить логи на ошибки
4. Перезапустить бота

### Ошибки обработки сообщений
**Проблема**: Бот не может обработать сообщения
**Решение**:
1. Проверить права бота в группе
2. Убедиться в правильности обработчиков
3. Проверить логи ошибок

---

## 🧠 LLM/API ОШИБКИ

### Высокие расходы на Claude
**Проблема**: Слишком много тратится на LLM
**Решение**:
1. Использовать DeepSeek (99.5% экономия)
2. Настроить `DEEPSEEK_API_KEY`
3. Убрать Claude из fallback
4. Мониторить расходы через `cost_monitor_deepseek.py`

### DeepSeek API ошибки
**Проблема**: Ошибки при работе с DeepSeek
**Решение**:
1. Добавить rate limiting
2. Добавить retry логику
3. Проверить валидность API ключа
4. Использовать fallback на другие модели

### LLM анализ ошибка
**Проблема**: LLM не может проанализировать контент
**Решение**:
1. Использовать fallback анализ без LLM
2. Проверить формат входных данных
3. Добавить валидацию контента

---

## 🔌 MCP СЕРВЕРЫ

### Ошибки коммуникации
**Проблема**: MCP серверы не отвечают
**Решение**:
1. Проверить порты и настройки
2. Перезапустить серверы
3. Проверить логи MCP
4. Убедиться в правильности конфигурации

### Notion MCP Server ошибки
**Проблема**: Notion MCP сервер не работает
**Решение**:
1. Проверить `notification_options` в Server.get_capabilities()
2. Убедиться в правильности схемы базы данных
3. Проверить токен и права доступа

---

## 🔧 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

### Переменная не загружается
**Проблема**: `Telegram=False` в логах
**Решение**:
1. Проверить наличие `.env` файла
2. Добавить `from dotenv import load_dotenv; load_dotenv()`
3. Проверить переменные: `echo $env:TELEGRAM_BOT_TOKEN`

### Неправильные имена переменных
**Проблема**: `TELEGRAM_TOKEN` vs `TELEGRAM_BOT_TOKEN`
**Решение**: Использовать единообразные имена во всех файлах

### Отсутствие валидации
**Проблема**: Бот падает при отсутствии токенов
**Решение**: Добавить проверку в начале приложения

### Массовый импорт ошибка
**Проблема**: Ошибки при массовом импорте
**Решение**: Использовать `ultimate_optimizer.py`

---

## 📁 СТРУКТУРНЫЕ ОШИБКИ

### Неправильная структура проекта
**Проблема**: Все в одном файле
**Решение**:
```
✅ Правильно:
project/
    src/
        main.py
        services/
        models/
    tests/
    docs/
```

### Отсутствие модульности
**Проблема**: Код не разделен на модули
**Решение**:
1. Разделить на сервисы
2. Создать модели данных
3. Вынести утилиты
4. Добавить тесты

---

## 💻 КОД ОШИБКИ

### Глобальные переменные
**Проблема**: Использование глобальных переменных
```python
# ❌ Неправильно
token = "secret_token"
def process_data():
    global token
    # использование глобальной переменной

# ✅ Правильно
def process_data(token: str):
    # использование параметра
```

### Отсутствие обработки ошибок
**Проблема**: Нет try-catch блоков
```python
# ❌ Неправильно
def get_data():
    response = requests.get(url)
    return response.json()

# ✅ Правильно
def get_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        raise
```

### Неправильное именование
**Проблема**: Непонятные имена функций
```python
# ❌ Неправильно
def do_stuff():
    pass

# ✅ Правильно
def process_user_data():
    pass
```

### HTTP запросы без обработки ошибок
**Проблема**: 20+ файлов с небезопасными HTTP запросами
```python
# ❌ Неправильно (найдено в 15+ файлах)
response = requests.get(url, headers=headers)
return response.json()

# ✅ Правильно
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
except requests.RequestException as e:
    logger.error(f"Error in GET request: {e}")
    raise
```

**Файлы с ошибками**:
- `universal_social_metrics.py`
- `telegram_analytics_framework.py`
- `setup_templates_chain.py`
- `setup_kpi_relations.py`
- `setup_business_chains.py`
- `optimize_existing_kpi.py`
- `notion_universal_fields.py`
- `notion_fields_setup.py`
- `link_guides_to_templates.py`
- `kpi_migration_full.py`
- `kpi_simple_migration.py`
- `fix_kpi_relations.py`
- `fix_kpi_api.py`
- `dual_level_analytics.py`
- `daily_telegram_monitor.py`

### MCP Server ошибки
**Проблема**: Неправильные параметры в get_capabilities()
```python
# ❌ Неправильно
capabilities=server.server.get_capabilities(
    experimental_capabilities={},
    notification_options={},  # Неправильный параметр
)

# ✅ Правильно
capabilities=server.server.get_capabilities(
    experimental_capabilities={},
    notification_options=NotificationOptions(notifications=[]),
)
```

### Неправильные имена переменных окружения
**Проблема**: Несоответствие имен переменных
```python
# ❌ Неправильно
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# ✅ Правильно
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```

---

## 🔗 СИСТЕМА ПОДЗАДАЧ NOTION

### ❌ КРИТИЧЕСКАЯ ОШИБКА: Неправильное создание подзадач
**Проблема**: Подзадачи создавались в неправильной базе данных и не связывались с задачей
**Что происходило**:
1. Подзадачи создавались в базе "Гайды" (47c6086858d442ebaeceb4fad1b23ba3) вместо "Дизайн" (9c5f4269-d614-49b6-a748-5579a3c21da3)
2. В поле "📬 Гайды" задачи попадали подзадачи вместо гайдов
3. Поле "Под задачи" оставалось пустым
4. Использовались неправильные имена полей (Name вместо Подзадачи)

**✅ ИСПРАВЛЕНИЕ**:
```python
# Правильная схема создания подзадач:
# 1. Найти подзадачи в гайде через поле "Дизайн подзадачи"
# 2. Создать копии в базе "Дизайн" (9c5f4269-d614-49b6-a748-5579a3c21da3)
# 3. Использовать поле "Подзадачи" (title) для названия
# 4. Связать с задачей через поле "Задачи" (relation)
# 5. В задаче обновить поле "Под задачи" (relation)
```

**🔧 ПРАВИЛЬНЫЙ АЛГОРИТМ**:
```python
async def create_task_with_subtasks(guide_id: str, task_title: str):
    # 1. Создать задачу
    task = await client.pages.create(
        parent={"database_id": "d09df250ce7e4e0d9fbe4e036d320def"},
        properties={
            "Задача": {"title": [{"text": {"content": task_title}}]},
            "📬 Гайды": {"relation": [{"id": guide_id}]}
        }
    )
    
    # 2. Получить подзадачи из гайда
    guide = await client.pages.retrieve(page_id=guide_id)
    subtasks_relation = guide['properties'].get('Дизайн подзадачи', {}).get('relation', [])
    
    # 3. Создать копии подзадач в правильной базе
    for subtask_ref in subtasks_relation:
        original_subtask = await client.pages.retrieve(page_id=subtask_ref['id'])
        subtask_title = original_subtask['properties'].get('Подзадачи', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        
        new_subtask = await client.pages.create(
            parent={"database_id": "9c5f4269-d614-49b6-a748-5579a3c21da3"},  # Дизайн
            properties={
                "Подзадачи": {"title": [{"text": {"content": subtask_title}}]},
                "Задачи": {"relation": [{"id": task['id']}]}
            }
        )
    
    # 4. Обновить задачу с подзадачами
    await client.pages.update(
        page_id=task['id'],
        properties={
            "Под задачи": {"relation": [{"id": subtask_id} for subtask_id in created_subtask_ids]}
        }
    )
```

**📋 ВЫВОДЫ**:
1. **Всегда проверять схему базы данных** перед созданием объектов
2. **Не терять имена полей** - использовать точные названия из Notion
3. **Не создавать дублирующие объекты** в неправильных базах
4. **Использовать централизованный сервер** (notion_mcp_server_fixed.py) для всех операций
5. **Проверять связи** после создания объектов

**🔍 ДИАГНОСТИКА**:
```python
# Проверить схему базы
database = await client.databases.retrieve(database_id="database_id")
for prop_name, prop_config in database['properties'].items():
    print(f"- {prop_name}: {prop_config.get('type')}")

# Проверить связи в объекте
object = await client.pages.retrieve(page_id="object_id")
for prop_name, prop_config in object['properties'].items():
    if prop_config.get('type') == 'relation':
        print(f"- {prop_name}: {len(prop_config.get('relation', []))} связей")
```

**📁 ФАЙЛЫ ДЛЯ ИСПОЛЬЗОВАНИЯ**:
- `notion_mcp_server_fixed.py` - исправленный MCP сервер
- `test_fixed_system_v4.py` - тест правильной системы
- `check_task_subtasks_field.py` - диагностика связей

---

## 📊 ФОРМУЛЫ NOTION API

### ❌ КРИТИЧЕСКАЯ ОШИБКА: Сложные формулы с relation полями
**Проблема**: API Notion не принимает сложные формулы с relation полями
**Что происходило**:
1. Попытки создать формулы типа `prop("Проекты").filter(current.prop("Статус") == "Done")`
2. API возвращает "Type error with formula"
3. Простые формулы работают, сложные - нет

**✅ ИСПРАВЛЕНИЕ**:
```python
# ❌ НЕ РАБОТАЕТ В API:
formula = """if(
  prop("Проекты").filter(current.prop("Статус") == "Done").length() > 0,
  prop("Проекты").filter(current.prop("Статус") == "Done").map(current.prop("Общее время")).average(),
  0
)"""

# ✅ РАБОТАЕТ В API:
formula = "1 + 1"  # Простые математические операции
formula = "now()"  # Простые функции
formula = "length(prop(\"Name\"))"  # Простые операции с полями
```

**🔧 ПРАВИЛЬНЫЙ ПОДХОД**:
1. **Создавать простые формулы через API** - только базовые операции
2. **Сложные формулы создавать вручную** в интерфейсе Notion
3. **Использовать rollup поля** для агрегации данных
4. **Комбинировать простые формулы** для сложной логики

**📝 ПРИМЕР ФОРМУЛЫ ДЛЯ ТИПОВЫХ ПРОЕКТОВ**:
```notion
// Формула для среднего времени выполненных проектов (создавать вручную в Notion):
if(
  prop("Проекты").filter(current.prop("Статус") == "Done").length() > 0,
  prop("Среднее время") * 
  (prop("Проекты").filter(current.prop("Статус") == "Done").length() / prop("Проекты").length()),
  0
)
```

**📋 ВЫВОДЫ**:
1. **API Notion ограничен** - принимает только простые формулы
2. **Сложные формулы создавать вручную** в интерфейсе Notion
3. **Использовать rollup поля** для агрегации данных
4. **Комбинировать простые формулы** для сложной логики
5. **Всегда тестировать формулы** перед массовым применением

**🔍 ДИАГНОСТИКА**:
```python
# Проверить работает ли формула в API
test_formula = "1 + 1"
try:
    await client.databases.update(
        database_id=database_id,
        properties={"Test": {"type": "formula", "formula": {"expression": test_formula}}}
    )
    print("✅ Простая формула работает")
except Exception as e:
    print(f"❌ Ошибка: {e}")
```

**📁 ФАЙЛЫ ДЛЯ ИСПОЛЬЗОВАНИЯ**:
- `create_basic_formula.py` - тестирование простых формул
- `analyze_typical_projects_database.py` - анализ схемы базы
- `update_existing_formula_field.py` - обновление полей формул

---

## ⚡ БЫСТРЫЕ РЕШЕНИЯ

### Проверка статуса ботов
```bash
# Проверить запущенные процессы
tasklist | findstr python

# Убить все процессы Python
taskkill /F /IM python.exe

# Запустить бота
python enhanced_materials_bot_v3.py
```

### Проверка переменных окружения
```bash
# Проверить переменные
echo $env:TELEGRAM_BOT_TOKEN
echo $env:NOTION_TOKEN

# Загрузить .env
python -c "from dotenv import load_dotenv; load_dotenv()"
```

### Проверка логов
```bash
# Последние 10 строк лога
Get-Content bot.log -Tail 10

# Поиск ошибок
Get-Content bot.log | Select-String "ERROR"
```

### Исправление Notion API
1. Проверить токен в `.env`
2. Пересоздать интеграцию в Notion
3. Обновить ID баз данных
4. Проверить права доступа

### Экономия на LLM
1. Настроить `DEEPSEEK_API_KEY`
2. Убрать Claude из fallback
3. Использовать `cost_monitor_deepseek.py`
4. Мониторить расходы

### Диагностика подзадач
```bash
# Проверить схему базы
python check_subtasks_database.py

# Тест правильной системы
python test_fixed_system_v4.py

# Проверить связи в задаче
python check_task_subtasks_field.py
```

### Создание формул Notion
```bash
# Тест простых формул
python create_basic_formula.py

# Анализ схемы базы
python analyze_typical_projects_database.py

# Сложные формулы создавать вручную в Notion
```

---

## 📞 КОГДА ОБРАЩАТЬСЯ К ДОКУМЕНТАЦИИ

### Если проблема не решена:
1. Проверить `docs/DAILY_WORKFLOW.md` - текущие проблемы
2. Посмотреть `docs/ENV_MANAGEMENT.md` - настройки окружения
3. Изучить `docs/PROJECT_STRUCTURE.md` - архитектура
4. Проверить `docs/AI_CONTEXT.md` - общий контекст

### Команды для диагностики:
```bash
# Контекст менеджер
python context_manager.py --problem [тип_проблемы]

# Проверка окружения
python -c "import os; print([k for k in os.environ.keys() if 'TOKEN' in k])"

# Тест Notion API
python test_notion_api.py
```

---

## 🔄 ОБНОВЛЕНИЕ ДОКУМЕНТА

При добавлении новых ошибок:
1. Добавить в `MISTAKES.md`
2. Обновить `docs/DAILY_WORKFLOW.md`
3. Документировать в `docs/AI_CONTEXT.md`
4. Создать тест если нужно

**Последнее обновление**: 2025-01-18
**Версия**: 4.0

## ✅ ИСПРАВЛЕННЫЕ ОШИБКИ (2025-01-18)

### HTTP запросы без обработки ошибок
**Статус**: ✅ ИСПРАВЛЕНО
**Файлы исправлены**:
- `universal_social_metrics.py` - добавлены try-catch блоки
- `setup_templates_chain.py` - исправлены все HTTP запросы
- `setup_kpi_relations.py` - исправлены GET запросы
- `notion_universal_fields.py` - исправлен GET запрос
- `notion_fields_setup.py` - исправлены GET и POST запросы
- `link_guides_to_templates.py` - автоматически исправлен
- `kpi_migration_full.py` - автоматически исправлен
- `kpi_simple_migration.py` - автоматически исправлен
- `fix_kpi_relations.py` - автоматически исправлен
- `fix_kpi_api.py` - автоматически исправлен
- `dual_level_analytics.py` - автоматически исправлен
- `daily_telegram_monitor.py` - автоматически исправлен

### Переменные окружения
**Статус**: ✅ ИСПРАВЛЕНО
- `enhanced_materials_bot_v3.py` - исправлено `TELEGRAM_TOKEN` → `TELEGRAM_BOT_TOKEN`
- `.env` файл уже содержит правильное имя переменной

### Система подзадач Notion
**Статус**: ✅ ИСПРАВЛЕНО
- Создание подзадач в правильной базе "Дизайн" (9c5f4269-d614-49b6-a748-5579a3c21da3)
- Правильное связывание через поля "Задачи" и "Под задачи"
- Использование корректных имен полей из схемы
- Создан `notion_mcp_server_fixed.py` для централизованного управления

### Формулы Notion API
**Статус**: ✅ ИСПРАВЛЕНО
- Выявлено ограничение API: сложные формулы с relation полями не работают
- Простые формулы (математика, функции) работают через API
- Сложные формулы нужно создавать вручную в интерфейсе Notion
- Создана формула для типовых проектов: среднее время выполненных проектов

### Созданные утилиты
- `utils/http_error_fixer.py` - утилита для поиска небезопасных HTTP запросов
- `utils/quick_fix_http.py` - быстрый скрипт для автоматического исправления
- `notion_mcp_server_fixed.py` - исправленный MCP сервер для работы с подзадачами
- `test_fixed_system_v4.py` - тест правильной системы подзадач
- `check_task_subtasks_field.py` - диагностика связей в задачах
- `check_subtasks_database.py` - проверка схемы баз данных
- `create_basic_formula.py` - тестирование простых формул Notion
- `analyze_typical_projects_database.py` - анализ схемы базы типовых проектов
- `update_existing_formula_field.py` - обновление полей формул

### Остается исправить
- **MCP Server** - требует изучения API документации для правильных параметров 

## MCP-АНАЛИТИКА НЕ СТАРТУЕТ (ПУТАЕМ СЕРВЕР И ИНСТРУМЕНТ)

**Симптомы**
- Запускаем `python notion_mcp_server.py analyze_notion_completeness ...` – в консоли одни ENV-переменные, дальше тишина.
- `notion_progress.log` пустой.
- Кажется, что «сервер завис», запросов к Notion нет.

**Причина**
- Этот скрипт *только инициализирует* сервер MCP и ждёт JSON-RPC-вызовов. Он **не** вызывает инструмент.

**Фикс**
1. Запускать инструмент через клиента: `python test_notion_mcp_final.py` или новый `analyze_ideas_via_mcp.py`.
2. Все прогресс-логи пишутся в `notion_progress.log`.
3. Для live-tail: `chcp 65001 ; Get-Content notion_progress.log -Wait`.

**Правило**
> Никогда не ждём прогресса, пока не увидим строку `LOAD:` в `notion_progress.log`. Если её нет – инструмент не вызван.

--- 