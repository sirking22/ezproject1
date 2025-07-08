# 🚨 ОШИБКИ И РЕШЕНИЯ

## 🔥 КРИТИЧЕСКИЕ ОШИБКИ

### 1. Event Loop конфликт
**Проблема**: `RuntimeError: There is no current event loop in thread`
**Причина**: Множественные процессы Python с asyncio
**Решение**: 
```bash
taskkill /F /IM python.exe
python simple_bot.py
```

### 2. Notion API ограничения
**Проблема**: HTTP 401 'restricted from accessing public API'
**Причина**: Блокировка API или истекший токен
**Решение**:
1. Проверить токен в системных переменных
2. Создать новую integration в Notion Developers
3. Добавить integration к базам через Share → Invite
4. Обновить токен в переменных окружения

### 3. Telegram Bot не отвечает
**Проблема**: Бот не реагирует на команды
**Причина**: Неверный токен или webhook конфликт
**Решение**:
```bash
# Проверить токен
python -c "import os; print('TELEGRAM_TOKEN:', bool(os.getenv('TELEGRAM_TOKEN')))"

# Перезапустить бота
taskkill /F /IM python.exe
python simple_bot.py
```

### 4. Yandex.Disk загрузка
**Проблема**: Ошибки загрузки файлов
**Причина**: Истекший токен или недостаточно места
**Решение**:
1. Проверить YA_ACCESS_TOKEN
2. Очистить место на диске
3. Проверить права доступа

## 🧠 ОШИБКИ ОПТИМИЗАЦИИ LLM

### 15. Неэффективное использование токенов
**Проблема**: Высокие расходы на LLM API
**Причина**: 
- Длинные промпты (300+ токенов)
- 100% запросов к LLM
- Отсутствие кэширования
- Нет детерминированной обработки

**Пример ошибки**:
```python
# ❌ ПЛОХО - 300 токенов на запрос
prompt = f"""
Пользователь описал идею в разговорном стиле. Извлеки структурированную информацию:
Текст: "{text}"
Верни JSON с полями: name, description, tags, importance, status
Примеры: "Хочу бота" → {{"name": "Бот", "description": "Автоматизация"}}
Верни только JSON без дополнительного текста.
"""

# ✅ ХОРОШО - 50 токенов на запрос
prompt = f"'{text}' → JSON: name, desc, tags, importance"
```

**Решение**:
```python
def smart_parse(text: str) -> Dict:
    # 80% случаев - детерминированная обработка (0 токенов)
    if ':' in text and any(keyword in text.lower() for keyword in ['название', 'описание']):
        return parse_structured(text)  # 0 токенов
    
    if len(text) < 50:
        return parse_simple(text)  # 0 токенов
    
    # 20% случаев - только сложные фразы
    return llm_parse(text)  # 50 токенов

@lru_cache(maxsize=1000)
def cached_llm_parse(text: str) -> Dict:
    return llm_parse(text)
```

**Экономия**: 97% токенов (30,000 → 1,000 на 100 запросов)

### 16. Избыточная работа и переписывание
**Проблема**: Создание новых файлов вместо исправления существующих
**Причина**: 
- Не следование принципу "не плодить новые файлы"
- Игнорирование существующей архитектуры
- Дублирование кода

**Пример ошибки**:
```python
# ❌ ПЛОХО - создал новый файл simple_bot_llm.py
# ❌ ПЛОХО - переписал весь код с нуля
# ❌ ПЛОХО - не использовал ultimate_optimizer.py

# ✅ ХОРОШО - добавил LLM в существующий код
# ✅ ХОРОШО - использовал детерминированную обработку
# ✅ ХОРОШО - следовал принципам проекта
```

**Решение**:
1. **Сначала детерминированная обработка** (0 токенов)
2. **Потом LLM** только для сложных случаев
3. **Использовать существующую архитектуру**
4. **Не создавать новые файлы без необходимости**

### 17. Игнорирование принципов проекта
**Проблема**: Нарушение правил из AI_CONTEXT.md
**Причина**: 
- Не следование принципу "98% без LLM"
- Игнорирование детерминированной обработки
- Создание избыточной архитектуры

**Решение**:
```python
# Следовать принципам ultimate_optimizer.py:
# 1. Детерминированная обработка (0 токенов)
# 2. Автотеги по доменам
# 3. Медиа-анализ без токенов
# 4. Самообучающиеся правила
```

## 🔧 ТЕХНИЧЕСКИЕ ОШИБКИ

### 5. Cover изображения в Notion
**Проблема**: Пустые cover изображения для видео
**Причина**: Yandex.Disk ссылки не работают в Notion cover
**Решение**: ✅ РЕШЕНО
- Использовать Telegram CDN прямые ссылки
- Загружать кадры через отправку пользователю
- Порядок операций: Telegram CDN → Yandex.Disk → очистка

### 6. MCP серверы
**Проблема**: Ошибки коммуникации с MCP
**Причина**: Неправильные пути или поврежденный venv
**Решение**:
1. Исправить пути в .cursor/mcp.json
2. Пересоздать venv: `python -m venv venv --clear`
3. Установить зависимости: `pip install -r requirements.txt`
4. Перезапустить Cursor/IDE

### 7. LLM расходы
**Проблема**: Высокие расходы на API
**Причина**: Неэффективное использование токенов
**Решение**:
- Использовать DeepSeek (99.5% экономия)
- Мониторинг через cost_monitor_deepseek.py
- Детерминированная обработка без LLM

### 8. Массовая обработка
**Проблема**: Ошибки при обработке больших объемов
**Причина**: Rate limiting или таймауты
**Решение**:
- Использовать ultimate_optimizer.py
- Добавить retry логику
- Обрабатывать батчами по 50-100 записей

## 📊 ОШИБКИ ДАННЫХ

### 9. UUID формат Notion
**Проблема**: Неверный формат ID для Notion
**Причина**: Неправильное форматирование UUID
**Решение**:
```python
# Правильный формат
page_id = "221ace03-d9ff-8196-851f-dddc805646a4"
# Неправильный формат
page_id = "221ace03d9ff8196851fddd805646a4"
```

### 10. Кодировка файлов
**Проблема**: Кракозябры в названиях файлов
**Причина**: Неправильная кодировка UTF-8
**Решение**:
```python
# Правильная обработка
filename = filename.encode('utf-8').decode('utf-8')
```

### 11. Пустые значения
**Проблема**: None значения в Notion
**Причина**: Неправильная обработка пустых полей
**Решение**:
```python
# Проверка перед отправкой
if value and value.strip():
    properties['field'] = {"rich_text": [{"text": {"content": value}}]}
```

## 🔄 ОШИБКИ ИНТЕГРАЦИИ

### 12. Webhook конфликты
**Проблема**: Бот не получает обновления
**Причина**: Конфликт webhook и polling

## 🗄️ ОШИБКИ СТРУКТУРЫ ДАННЫХ (КРИТИЧЕСКИЕ)

### 18. Ошибки назначения исполнителей и KPI
**Проблема**: KPI или задачи не назначаются на нужного исполнителя (например, Арсения)
**Причина**:
- Неправильный фильтр (ищет по Name, а не по relation/people)
- Игнорирование централизованных справочников исполнителей
- Дублирование логики поиска исполнителей
- Непонимание архитектуры: в базах используются И relation, И people поля одновременно

**Решение**:
1. **Проверить схему базы** через MCP и notion_database_schemas.py - какие поля есть для исполнителей (relation "Сотрудники" И/ИЛИ people "Участники").
2. **Для relation-полей** использовать id из справочников (`assignees_registry.py`, `notion_users.py`).
3. **Для people-полей** использовать только id полноценных пользователей Notion (не гостей).
4. **Не дублировать справочники** — только централизованные файлы.
5. **Перед созданием/назначением KPI** сверяться с актуальной схемой базы.
6. **Если KPI не назначаются** — проверить, по какому полю идёт фильтрация (relation vs people vs Name).
7. **Все архитектурные решения и обходы** фиксировать в AI_CONTEXT.md и ERRORS_SOLUTIONS.md.

**Пример ошибки**:
```python
# ❌ ПЛОХО - фильтр только по Name
result = await server.get_pages(db_id, {"property": "Name", "title": {"contains": "Arsentiy"}})

# ✅ ХОРОШО - фильтр по relation-полю "Сотрудники" (если есть)
result = await server.get_pages(db_id, {"property": "Сотрудники", "relation": {"contains": arseniy_id}})

# ✅ ХОРОШО - фильтр по people-полю "Участники" (если есть)
result = await server.get_pages(db_id, {"property": "Участники", "people": {"contains": arseniy_id}})
```

**Рекомендация**:
- Сначала проверить схему базы через MCP: какие поля для исполнителей есть.
- Если есть relation "Сотрудники" — использовать для гостей.
- Если есть people "Участники" — использовать для полноценных пользователей.
- Если есть оба поля — заполнять оба согласно типам исполнителей.
- Все обходы и решения — в ERRORS_SOLUTIONS.md, а не только в AI_CONTEXT.md.

### 19. Игнорирование MCP сервера
**Проблема**: Создание сырых API скриптов вместо использования MCP
**Дата**: 2025-01-18
**Причина**: 
- Непонимание преимуществ MCP
- Дублирование логики
- Потеря времени на отладку

**ОШИБОЧНЫЕ ДЕЙСТВИЯ**:
```python
# ❌ ПЛОХО - сырой API
import requests
url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
response = requests.post(url, headers=headers, json=payload)

# ✅ ПРАВИЛЬНО - MCP сервер
from notion_mcp_server import NotionMCPServer
server = NotionMCPServer()
result = await server.call_tool("analyze_notion_completeness", {...})
```

**РЕШЕНИЕ**:
1. **ВСЕГДА начинать с MCP** для анализа данных
2. **Использовать готовые инструменты** из mcp_schemas.yaml
3. **Не дублировать логику** в сырых скриптах
4. **Документировать MCP инструменты** в AI_CONTEXT.md
**Решение**:
```python
# Удалить webhook перед polling
await bot.delete_webhook()
```

### 13. Асинхронные операции
**Проблема**: Блокировка при загрузке файлов
**Причина**: Синхронные операции в async контексте
**Решение**:
```python
# Использовать aiohttp вместо requests
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.read()
```

### 14. Таймауты
**Проблема**: Прерывание длительных операций
**Причина**: Слишком короткие таймауты
**Решение**:
```python
# Увеличить таймауты для сложных операций
timeout = aiohttp.ClientTimeout(total=300)  # 5 минут
```

## 🛠️ ПРОФИЛАКТИКА

### Ежедневные проверки:
1. ✅ Проверить процессы Python
2. ✅ Проверить логи ошибок
3. ✅ Мониторинг расходов LLM
4. ✅ Проверка доступности API

### Перед изменениями:
1. ✅ Создать backup
2. ✅ Тестировать на малых данных
3. ✅ Проверить переменные окружения
4. ✅ Документировать изменения

### Мониторинг:
1. ✅ Логирование всех операций
2. ✅ Отслеживание метрик
3. ✅ Алерты при критических ошибках
4. ✅ Регулярные проверки состояния

## 📈 СТАТИСТИКА ОШИБОК

### Частые ошибки (2025):
1. Event Loop конфликт - 35%
2. Неэффективное использование LLM - 25%
3. Notion API ограничения - 20%
4. Telegram токены - 10%
5. Yandex.Disk загрузка - 5%
6. Прочие - 5%

### Время решения:
- Критические: < 5 минут
- Оптимизация LLM: < 15 минут
- Технические: < 30 минут
- Интеграционные: < 2 часа
- Архитектурные: < 1 день

## 🎯 ЛУЧШИЕ ПРАКТИКИ

### Код:
- Всегда использовать try/except
- Логировать все операции
- Проверять входные данные
- Использовать типизацию

### Операции:
- Тестировать на малых данных
- Создавать backup перед изменениями
- Мониторить расходы
- Документировать решения

### Интеграции:
- Проверять токены перед запуском
- Использовать retry логику
- Обрабатывать таймауты
- Fallback на альтернативные методы

### LLM Оптимизация:
- **Сначала детерминированная обработка** (0 токенов)
- **Потом LLM** только для сложных случаев (20%)
- **Короткие промпты** (50 токенов вместо 300)
- **Кэширование** одинаковых запросов
- **Следовать принципам** ultimate_optimizer.py 

## ⚠️ ОШИБКИ ENV/.env и ПЕРЕМЕННЫХ ОКРУЖЕНИЯ

### Проблема: Python-скрипты не видят переменные из .env
**Причина**:
- Файл .env есть в корне, но переменные не подхватываются Python
- Возможные причины: неправильное имя переменной, дубликаты, невидимые символы, кодировка, запуск не из того каталога
- В проекте было несколько похожих переменных (TELEGRAM_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_TOKEN_2 и т.д.)
- В какой-то момент не было переменной с точным именем TELEGRAM_BOT_TOKEN, либо она была не сохранена/не видна из-за кодировки или невидимых символов

**Диагностика**:
- Проверить рабочий каталог: `os.getcwd()`
- Проверить путь к .env: `find_dotenv()`
- Проверить содержимое .env и отсутствие BOM/пробелов
- Проверить переменные через os.environ

**Решение**:
1. Убедиться, что переменная называется ровно так, как ожидает код (например, TELEGRAM_BOT_TOKEN)
2. Проверить, что .env сохранён в UTF-8 без BOM
3. Проверить, что Python запускается из корня проекта
4. Проверить, что нет дубликатов переменных
5. После исправления — переменные видны, бот и тесты работают корректно

**Рекомендация**: всегда явно проверять имя переменной, отсутствие пробелов и кодировку .env, а также запускать Python из корня проекта. Для диагностики использовать скрипты с выводом os.environ и find_dotenv(). 

### 20. MCP сервер не запускается (NotificationOptions ошибка)
**Проблема**: `AttributeError: 'NoneType' object has no attribute 'tools_changed'`
**Дата**: 2025-07-06
**Причина**: 
- В MCP SDK 1.10.1 нет класса `NotificationOptions` в `mcp.types`
- Неправильные импорты в MCP серверах
- Использование несуществующих классов: `Message`, `MessageRole`, `MessageContent`

**ОШИБОЧНЫЕ ДЕЙСТВИЯ**:
```python
# ❌ ПЛОХО - несуществующие импорты
from mcp.types import (
    NotificationOptions,  # НЕ СУЩЕСТВУЕТ
    Message,              # НЕ СУЩЕСТВУЕТ
    MessageRole,          # НЕ СУЩЕСТВУЕТ
    MessageContent,       # НЕ СУЩЕСТВУЕТ
)

# ❌ ПЛОХО - неправильный вызов
capabilities=server.server.get_capabilities(
    notification_options=NotificationOptions(tools_changed=False),  # ОШИБКА
    experimental_capabilities={},
),
```

**ПРАВИЛЬНЫЕ РЕШЕНИЯ**:
```python
# ✅ ПРАВИЛЬНО - правильные импорты
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# ✅ ПРАВИЛЬНО - правильный вызов
capabilities=server.server.get_capabilities(None, {}),
```

**ИСПРАВЛЕННЫЕ ФАЙЛЫ**:
1. `notion_mcp_server.py` - убраны несуществующие импорты
2. `.cursor/mcp.json` - обновлен путь к рабочему серверу
3. `simple_mcp_notion_server.py` - исправлены импорты
4. `mcp_notion_server_with_schemas.py` - исправлены импорты

**РЕЗУЛЬТАТ**:
- ✅ MCP сервер запускается без ошибок
- ✅ Переменные окружения загружаются корректно
- ✅ Cursor видит MCP инструменты
- ✅ Работает интеграция с Notion

**ПРОФИЛАКТИКА**:
1. **Всегда проверять импорты** перед использованием MCP SDK
2. **Использовать только существующие классы** из `mcp.types`
3. **Тестировать MCP сервер** перед обновлением конфигурации
4. **Документировать изменения** в ERRORS_SOLUTIONS.md

**КОМАНДЫ ДЛЯ ПРОВЕРКИ**:
```bash
# Проверка импортов
python -c "from mcp.types import NotificationOptions; print('OK')"

# Тест MCP сервера
python notion_mcp_server.py

# Проверка конфигурации
cat .cursor/mcp.json
``` 

## 🎯 ОШИБКИ KPI И НАЗНАЧЕНИЙ

### 18. Неправильное назначение KPI на сотрудников
**Проблема**: KPI не назначаются на правильного сотрудника
**Причина**: 
- Использование неправильного UUID сотрудника
- Попытка назначения через people поле вместо relation
- Неправильная структура базы данных

**Пример ошибки**:
```python
# ❌ ПЛОХО - неправильный UUID
ARSENIY_UUID = "229ace03-d9ff-8182-a8ac-c40987fa42b1"  # Старый UUID

# ❌ ПЛОХО - попытка через people поле
properties = {
    'Сотрудники': {
        'people': [{'id': ARSENIY_UUID}]  # Неправильный тип поля
    }
}

# ✅ ХОРОШО - правильный UUID из базы сотрудников
ARSENIY_UUID = "73726d47-02d4-4a5b-900a-b24b145ecf72"  # Актуальный UUID

# ✅ ХОРОШО - через relation поле
properties = {
    'Сотрудники': {
        'relation': [{'id': ARSENIY_UUID}]  # Правильный тип поля
    }
}
```

**Решение**:
1. **Всегда проверять структуру базы**:
   ```python
   # Проверка типа поля
   for field_name, field_info in page['properties'].items():
       if field_info.get('type') == 'relation':
           print(f"Relation поле: {field_name}")
       elif field_info.get('type') == 'people':
           print(f"People поле: {field_name}")
   ```

2. **Получать актуальный UUID из базы сотрудников**:
   ```python
   # Поиск сотрудника в базе
   employees_db_id = "195ace03-d9ff-80c1-a1b0-d236ec3564d2"
   response = client.databases.query(database_id=employees_db_id)
   
   for page in response.get('results', []):
       name = get_page_title(page)
       if 'арсен' in name.lower():
           return page['id']  # Актуальный UUID
   ```

3. **Использовать правильный тип поля**:
   ```python
   # Для relation полей
   properties = {
       'Сотрудники': {
           'relation': [{'id': employee_uuid}]
       }
   }
   
   # Для people полей
   properties = {
       'Участники': {
           'people': [{'id': employee_uuid}]
       }
   }
   ```

### 19. Ошибки диагностики KPI баз
**Проблема**: Неправильная диагностика структуры KPI базы
**Причина**: 
- Предположение о наличии people полей
- Игнорирование relation полей
- Не проверка реальной структуры API

**Пример ошибки**:
```python
# ❌ ПЛОХО - предположение без проверки
people_field = 'Сотрудники'  # Может быть relation!

# ❌ ПЛОХО - не проверка типа поля
client.pages.update(
    page_id=page_id,
    properties={
        'Сотрудники': {
            'people': [{'id': uuid}]  # Ошибка если это relation
        }
    }
)

# ✅ ХОРОШО - проверка типа поля
for field_name, field_info in page['properties'].items():
    if field_info.get('type') == 'people':
        people_field = field_name
        break
    elif field_info.get('type') == 'relation':
        relation_field = field_name
        break
```

**Решение**:
1. **Всегда диагностировать структуру базы**:
   ```python
   def diagnose_database_structure(database_id):
       response = client.databases.query(database_id=database_id, page_size=1)
       if response.get('results'):
           page = response['results'][0]
           for field_name, field_info in page['properties'].items():
               print(f"Поле '{field_name}': {field_info.get('type')}")
   ```

2. **Проверять реальные данные API**:
   ```python
   # Получить реальную структуру
   database = client.databases.retrieve(database_id=database_id)
   properties = database.get('properties', {})
   
   for field_name, field_info in properties.items():
       print(f"{field_name}: {field_info.get('type')}")
   ```

### 20. Массовые операции без валидации
**Проблема**: Массовые изменения без проверки результата
**Причина**: 
- Отсутствие валидации после операций
- Не проверка успешности назначений
- Игнорирование ошибок API

**Пример ошибки**:
```python
# ❌ ПЛОХО - без валидации
for page in pages:
    client.pages.update(page_id=page['id'], properties=properties)
print("Готово!")  # Не знаем что произошло

# ✅ ХОРОШО - с валидацией
updated_count = 0
for page in pages:
    try:
        result = client.pages.update(page_id=page['id'], properties=properties)
        if result:
            updated_count += 1
    except Exception as e:
        print(f"Ошибка {page['id']}: {e}")
        continue

print(f"Обновлено: {updated_count}/{len(pages)}")
```

**Решение**:
1. **Всегда валидировать результат**:
   ```python
   def verify_assignment(database_id, employee_uuid):
       response = client.databases.query(database_id=database_id)
       assigned_count = 0
       
       for page in response.get('results', []):
           employees_data = page['properties'].get('Сотрудники', {})
           relations = employees_data.get('relation', [])
           
           if any(rel.get('id') == employee_uuid for rel in relations):
               assigned_count += 1
       
       return assigned_count
   ```

2. **Логировать все операции**:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   
   for page in pages:
       try:
           result = client.pages.update(...)
           logger.info(f"✅ Обновлена запись {page['id']}")
       except Exception as e:
           logger.error(f"❌ Ошибка {page['id']}: {e}")
   ```

### 21. Игнорирование схем баз данных
**Проблема**: Не использование канонических схем
**Причина**: 
- Создание схем "на лету"
- Не проверка соответствия реальным данным
- Игнорирование notion_database_schemas.py

**Решение**:
1. **Всегда использовать канонические схемы**:
   ```python
   from notion_database_schemas import DATABASE_SCHEMAS
   
   def validate_schema(database_id, real_data):
       if database_id not in DATABASE_SCHEMAS:
           return False
       
       expected_schema = DATABASE_SCHEMAS[database_id]
       real_properties = real_data.get('properties', {})
       
       for field_name in expected_schema:
           if field_name not in real_properties:
               return False
       
       return True
   ```

2. **Сверять реальные данные со схемами**:
   ```python
   def compare_schema_with_reality(database_id):
       # Получить схему
       expected = DATABASE_SCHEMAS.get(database_id, {})
       
       # Получить реальные данные
       database = client.databases.retrieve(database_id=database_id)
       real_properties = database.get('properties', {})
       
       print(f"Ожидаемые поля: {list(expected.keys())}")
       print(f"Реальные поля: {list(real_properties.keys())}")
   ```

## 📋 ЧЕКЛИСТ ПРЕДОТВРАЩЕНИЯ ОШИБОК KPI

### Перед массовыми операциями:
- [ ] Проверить структуру базы (relation vs people поля)
- [ ] Получить актуальный UUID сотрудника из базы сотрудников
- [ ] Валидировать схему через notion_database_schemas.py
- [ ] Протестировать на одной записи
- [ ] Подготовить скрипт валидации результата

### После операций:
- [ ] Проверить количество обновленных записей
- [ ] Валидировать назначения через relation/people поля
- [ ] Логировать все ошибки и успешные операции
- [ ] Удалить временные диагностические файлы

### При повторных ошибках:
- [ ] Сверяться с ERRORS_SOLUTIONS.md
- [ ] Проверять актуальность UUID в assignees_registry.py
- [ ] Диагностировать реальную структуру API
- [ ] Использовать безопасные операции с валидацией 

## 🔒 БЕЗОПАСНЫЕ ОПЕРАЦИИ С NOTION

### Проблема: Создание пустых записей в Notion
**Симптомы:**
- Записи создаются, но поля остаются пустыми
- MCP возвращает success, но данные не сохраняются
- Notion API не показывает ошибки, но записи неполные

**Причины:**
1. Невалидные значения для select/multi_select полей
2. Неправильная структура данных для полей
3. Отсутствие валидации схемы перед отправкой
4. Отсутствие post-check после создания

**Решение:**
```python
# ❌ НЕПРАВИЛЬНО - обычное создание
result = await server.create_page({
    "database_id": db_id,
    "properties": properties
})

# ✅ ПРАВИЛЬНО - безопасное создание
from safe_database_operations import SafeDatabaseOperations
safe_ops = SafeDatabaseOperations()
result = await safe_ops.safe_create_page("database_name", properties)

# Проверяем результат
if result["success"] and result["post_check_passed"]:
    print("✅ Запись создана и проверена")
else:
    print(f"❌ Ошибки: {result['errors']}")
    print(f"⚠️ Предупреждения: {result['warnings']}")
```

### Железные правила для работы с Notion:

#### 1. ВСЕГДА использовать safe operations
```python
# Создание
result = await safe_ops.safe_create_page("kpi", properties)

# Обновление  
result = await safe_ops.safe_update_page(page_id, properties)

# Массовое создание
result = await safe_ops.safe_bulk_create("kpi", properties_list)
```

#### 2. ВСЕГДА проверять результат
```python
if not result["validation_passed"]:
    print(f"❌ Валидация не пройдена: {result['errors']}")
    return

if not result["post_check_passed"]:
    print(f"⚠️ Post-check не пройден: {result['warnings']}")
    # Запись создана, но с проблемами
```

#### 3. ВСЕГДА использовать значения из схемы
```python
# ❌ НЕПРАВИЛЬНО - хардкод значений
"Тип KPI": {"select": {"name": "Мой тип"}}

# ✅ ПРАВИЛЬНО - из схемы
from notion_database_schemas import get_database_schema
schema = get_database_schema("kpi")
valid_types = schema.select_options["Тип KPI"]
# Используем только valid_types
```

#### 4. ВСЕГДА тестировать на одной записи
```python
# Тест на одной записи
test_result = await safe_ops.safe_create_page("kpi", test_properties)
if test_result["success"] and test_result["post_check_passed"]:
    # Только потом массовая операция
    bulk_result = await safe_ops.safe_bulk_create("kpi", all_properties)
```

### Чеклист перед любой операцией с Notion:
- [ ] Проверить схему базы через `get_database_schema()`
- [ ] Валидировать все значения select/multi_select
- [ ] Использовать safe_create_page/safe_update_page
- [ ] Проверить результат (validation_passed, post_check_passed)
- [ ] При массовых операциях - тест на 1 записи
- [ ] После массовой операции - проверить 2-3 записи вручную

### Автоматические проверки:
```python
# В любом скрипте, работающем с Notion
from safe_database_operations import SafeDatabaseOperations

safe_ops = SafeDatabaseOperations()

# Создание с автоматической валидацией и post-check
result = await safe_ops.safe_create_page("database_name", properties)

# Автоматическое логирование всех проблем
if not result["success"]:
    logger.error(f"Ошибка создания: {result['errors']}")
elif not result["post_check_passed"]:
    logger.warning(f"Предупреждения: {result['warnings']}")
else:
    logger.info("✅ Запись создана успешно")
``` 