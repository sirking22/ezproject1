# 🔗 НАСТРОЙКА РЕАЛЬНЫХ СЕРВИСОВ

## 🎯 ИНТЕГРАЦИЯ С NOTION И TELEGRAM

### 1. **Настройка Notion Integration**

#### 1.1 Создание интеграции
1. **Перейди на:** https://www.notion.so/my-integrations
2. **Нажми:** "New integration"
3. **Заполни:**
   - Name: `Quick Voice Assistant`
   - Associated workspace: выбери свой workspace
   - Capabilities: Read content, Update content, Insert content
4. **Скопируй:** Internal Integration Token

#### 1.2 Создание баз данных
Создай базы данных для каждого типа контента:

**Tasks (Задачи):**
```
Name: Tasks
Properties:
- Name (Title) - название задачи
- Status (Select) - To Do, In Progress, Done
- Priority (Select) - Low, Medium, High
- Created (Date) - дата создания
- Tags (Multi-select) - теги
```

**Reflections (Рефлексии):**
```
Name: Reflections
Properties:
- Name (Title) - заголовок рефлексии
- Content (Text) - содержание
- Mood (Select) - Happy, Neutral, Sad, Stressed
- Date (Date) - дата
- Type (Select) - voice, manual, ai
```

**Habits (Привычки):**
```
Name: Habits
Properties:
- Name (Title) - название привычки
- Status (Select) - Active, Paused, Completed
- Frequency (Select) - Daily, Weekly, Monthly
- Streak (Number) - текущая серия
- Created (Date) - дата создания
```

#### 1.3 Получение Database IDs
1. **Открой каждую базу данных**
2. **Скопируй ID из URL:**
   ```
   https://notion.so/workspace/DATABASE_ID?v=...
   ```
3. **Добавь интеграцию к каждой базе:**
   - Нажми "Share" в правом верхнем углу
   - Добавь созданную интеграцию
   - Дай права "Can edit"

### 2. **Настройка Telegram Bot**

#### 2.1 Создание бота
1. **Найди @BotFather в Telegram**
2. **Отправь команду:** `/newbot`
3. **Следуй инструкциям:**
   - Bot name: `Quick Voice Assistant`
   - Username: `your_voice_assistant_bot`
4. **Скопируй токен:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### 2.2 Получение Chat ID
1. **Найди созданного бота в Telegram**
2. **Отправь любое сообщение**
3. **Перейди по ссылке:**
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
4. **Найди в ответе:**
   ```json
   "chat": {
     "id": 123456789,
     "type": "private"
   }
   ```
5. **Скопируй ID** (это число)

### 3. **Обновление конфигурации**

#### 3.1 Редактирование .env
```bash
nano .env
```

Замени значения:
```env
# Notion
NOTION_TOKEN=secret_your_actual_notion_token_here
NOTION_TASKS_DB=your_tasks_database_id
NOTION_REFLECTIONS_DB=your_reflections_database_id
NOTION_HABITS_DB=your_habits_database_id

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### 3.2 Проверка конфигурации
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Notion Token:', '✅' if os.getenv('NOTION_TOKEN') else '❌')
print('Telegram Token:', '✅' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌')
print('Chat ID:', '✅' if os.getenv('TELEGRAM_CHAT_ID') else '❌')
"
```

### 4. **Тестирование интеграций**

#### 4.1 Тест Notion
```bash
python -c "
import asyncio
import sys
sys.path.append('integration')
from notion_integration import NotionIntegration
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    notion = NotionIntegration(
        token=os.getenv('NOTION_TOKEN'),
        databases={'tasks': os.getenv('NOTION_TASKS_DB')}
    )
    await notion.initialize()
    result = await notion.create_task('Тестовая задача')
    print('Notion test:', '✅' if result else '❌')

asyncio.run(test())
"
```

#### 4.2 Тест Telegram
```bash
python -c "
import asyncio
import sys
sys.path.append('integration')
from telegram_integration import TelegramIntegration
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    telegram = TelegramIntegration(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        chat_id=os.getenv('TELEGRAM_CHAT_ID')
    )
    await telegram.initialize()
    result = await telegram.send_message('🧪 Тестовое сообщение от Quick Voice Assistant')
    print('Telegram test:', '✅' if result else '❌')

asyncio.run(test())
"
```

### 5. **Запуск полной системы**

#### 5.1 Запуск сервера
```bash
python start_quick_voice_assistant.py
```

#### 5.2 Тестирование API
```bash
# В новом терминале
python scripts/test_system.py
```

#### 5.3 Тест голосовой команды
```bash
curl -X POST http://localhost:8000/watch/voice \
  -H "Content-Type: application/json" \
  -d '{
    "query": "добавь задачу протестировать интеграции",
    "context": "test",
    "timestamp": 1234567890,
    "user_id": "test_user"
  }'
```

### 6. **Проверка результатов**

#### 6.1 Notion
- Открой базу данных Tasks
- Найди созданную задачу "протестировать интеграции"

#### 6.2 Telegram
- Проверь сообщения от бота
- Должно прийти уведомление о созданной задаче

#### 6.3 Часы
- Установи приложение на часы
- Протестируй голосовую команду
- Проверь ответ на экране

### 7. **Устранение неполадок**

#### 7.1 Notion ошибки
- **401 Unauthorized:** проверь токен и права доступа
- **404 Not Found:** проверь Database ID
- **403 Forbidden:** добавь интеграцию к базе данных

#### 7.2 Telegram ошибки
- **401 Unauthorized:** проверь токен бота
- **400 Bad Request:** проверь Chat ID
- **403 Forbidden:** убедись, что бот не заблокирован

#### 7.3 Сетевые ошибки
- **Connection refused:** проверь, что сервер запущен
- **Timeout:** проверь скорость интернета
- **DNS error:** проверь доступность сервисов

### 8. **Мониторинг и логи**

#### 8.1 Просмотр логов
```bash
# Логи сервера
tail -f logs/server.log

# Логи ошибок
tail -f logs/error.log

# Лог развертывания
tail -f deployment_log.jsonl
```

#### 8.2 Метрики
```bash
# Статус сервера
curl http://localhost:8000/health

# Метрики
curl http://localhost:8000/metrics
```

---

## 🎯 РЕЗУЛЬТАТ

После настройки у тебя будет:

✅ **Работающая интеграция с Notion** - автоматическое создание задач/рефлексий/привычек  
✅ **Работающая интеграция с Telegram** - уведомления о каждом действии  
✅ **Полное тестирование** - все компоненты проверены  
✅ **Готовность к использованию** - система работает с реальными данными  

**Система готова к продуктивному использованию!** 🚀 