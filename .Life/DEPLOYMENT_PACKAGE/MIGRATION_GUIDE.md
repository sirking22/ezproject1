# 🚀 РУКОВОДСТВО ПО ПЕРЕНОСУ И РАЗВЕРТЫВАНИЮ

## 📦 ПОДГОТОВКА К ПЕРЕНОСУ

### Что включено в пакет:

```
DEPLOYMENT_PACKAGE/
├── README.md                    # Обзор пакета
├── INSTALLATION_GUIDE.md        # Пошаговая установка
├── MIGRATION_GUIDE.md          # Это руководство
├── 
├── server/                      # Серверная часть
│   ├── llm_api_server.py        # FastAPI сервер
│   ├── requirements.txt         # Python зависимости
│   └── config.py               # Конфигурация
├── 
├── watch_app/                   # Приложение для часов
│   ├── xiaomi_watch_app.js      # Основное приложение
│   ├── app_config.json          # Конфигурация часов
│   └── quick_voice_assistant.js # Упрощенный ассистент
├── 
├── integration/                 # Интеграции
│   ├── notion_integration.py    # Notion интеграция
│   ├── telegram_integration.py  # Telegram интеграция
│   └── voice_processor.py       # Обработка голоса
└── 
└── scripts/                     # Скрипты
    ├── install.sh              # Автоматическая установка
    ├── start_server.sh         # Запуск сервера
    └── test_system.py          # Тестирование
```

---

## 🎯 БЫСТРЫЙ СТАРТ (5 минут)

### 1. Копирование файлов
```bash
# Создай папку для проекта
mkdir ~/quick-voice-assistant
cd ~/quick-voice-assistant

# Скопируй все файлы из пакета
cp -r DEPLOYMENT_PACKAGE/* .
```

### 2. Автоматическая установка
```bash
# Сделай скрипт исполняемым
chmod +x scripts/install.sh

# Запусти установку
./scripts/install.sh
```

### 3. Настройка конфигурации
```bash
# Отредактируй .env файл
nano .env

# Добавь свои токены:
# NOTION_TOKEN=your_notion_token
# TELEGRAM_BOT_TOKEN=your_telegram_token
# TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Запуск системы
```bash
# Запусти сервер
./scripts/start_server.sh

# В новом терминале протестируй
./scripts/test_system.sh
```

---

## 🔧 ПОДРОБНАЯ ИНСТРУКЦИЯ

### Этап 1: Подготовка системы

#### 1.1 Проверка требований
```bash
# Python 3.8+
python3 --version

# Node.js 16+ (опционально)
node --version

# Git
git --version
```

#### 1.2 Создание рабочей директории
```bash
# Создай папку проекта
mkdir ~/quick-voice-assistant
cd ~/quick-voice-assistant

# Скопируй файлы
cp -r /path/to/DEPLOYMENT_PACKAGE/* .
```

### Этап 2: Установка зависимостей

#### 2.1 Python окружение
```bash
# Создай виртуальное окружение
python3 -m venv venv

# Активируй
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установи зависимости
pip install -r server/requirements.txt
```

#### 2.2 Настройка конфигурации
```bash
# Отредактируй .env файл
nano .env

# Основные настройки:
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# Токены (обязательно):
NOTION_TOKEN=your_notion_token_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# LLM (опционально):
USE_LOCAL_LLM=False
LLM_MODEL_PATH=/path/to/llama-70b.gguf
```

### Этап 3: Настройка интеграций

#### 3.1 Notion интеграция
1. **Получи токен Notion:**
   - Зайди на https://www.notion.so/my-integrations
   - Создай новую интеграцию
   - Скопируй Internal Integration Token

2. **Настрой базы данных:**
   - Создай базы данных для задач, рефлексий, привычек
   - Скопируй ID баз данных из URL
   - Добавь интеграцию к каждой базе данных

3. **Обнови .env:**
```bash
NOTION_TOKEN=secret_your_token_here
NOTION_TASKS_DB=database_id_for_tasks
NOTION_REFLECTIONS_DB=database_id_for_reflections
NOTION_HABITS_DB=database_id_for_habits
```

#### 3.2 Telegram интеграция
1. **Создай бота:**
   - Напиши @BotFather в Telegram
   - Команда: `/newbot`
   - Следуй инструкциям
   - Скопируй токен бота

2. **Получи chat_id:**
   - Напиши боту любое сообщение
   - Перейди на: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Найди "chat":{"id": число}

3. **Обнови .env:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### 3.3 Локальная LLM (опционально)
1. **Скачай модель:**
```bash
# Создай папку для моделей
mkdir models
cd models

# Скачай Llama 70B (выбери одну):
# 4-bit (быстрее, меньше памяти):
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q4_K_M.gguf

# 8-bit (лучше качество, больше памяти):
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q8_0.gguf
```

2. **Обнови .env:**
```bash
USE_LOCAL_LLM=True
LLM_MODEL_PATH=/path/to/models/llama-2-70b-chat.Q4_K_M.gguf
```

### Этап 4: Настройка часов

#### 4.1 Получение IP адреса
```bash
# Linux/macOS:
hostname -I

# Windows:
ipconfig
# Найди IPv4 Address
```

#### 4.2 Обновление конфигурации часов
```bash
# Отредактируй app_config.json
nano watch_app/app_config.json

# Замени IP адрес:
{
  "server": {
    "url": "http://YOUR_IP_ADDRESS:8000",
    "timeout": 10000
  }
}
```

#### 4.3 Установка на часы
1. **Подключи часы** к компьютеру через USB
2. **Открой Xiaomi Wear** приложение
3. **Перейди в "Приложения"**
4. **Нажми "Установить приложение"**
5. **Выбери файл** `watch_app/xiaomi_watch_app.js`

### Этап 5: Запуск и тестирование

#### 5.1 Запуск сервера
```bash
# Запусти сервер
./scripts/start_server.sh

# Или вручную:
cd server
python llm_api_server.py
```

#### 5.2 Тестирование
```bash
# В новом терминале
./scripts/test_system.sh

# Или вручную:
cd scripts
python test_system.py
```

#### 5.3 Проверка работы
1. **Открой браузер:** `http://localhost:8000/docs`
2. **Протестируй эндпоинт:** `/ping`
3. **Проверь часы:** подними руку → говори команду
4. **Проверь Telegram:** должно прийти уведомление

---

## 🔄 ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩЕЙ СИСТЕМОЙ

### Если у тебя уже есть Notion-Telegram-LLM система:

#### 1. Копирование конфигурации
```bash
# Скопируй токены из существующей системы
cp /path/to/existing/.env .env

# Обнови пути к базам данных если нужно
nano .env
```

#### 2. Интеграция с существующими базами
```python
# В server/config.py обнови database IDs:
NOTION_CONFIG = {
    "databases": {
        "tasks": "your_existing_tasks_db_id",
        "reflections": "your_existing_reflections_db_id",
        "habits": "your_existing_habits_db_id"
    }
}
```

#### 3. Интеграция с локальной LLM
```python
# Если у тебя уже есть Llama 70B:
LLM_CONFIG = {
    "model_path": "/path/to/your/existing/llama-70b.gguf",
    "use_local": True
}
```

---

## 🚀 АВТОЗАПУСК

### Linux/macOS (systemd)
```bash
# Создай сервис
sudo nano /etc/systemd/system/quick-voice-assistant.service
```

Содержимое:
```ini
[Unit]
Description=Quick Voice Assistant
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/quick-voice-assistant
Environment=PATH=/home/your_username/quick-voice-assistant/venv/bin
ExecStart=/home/your_username/quick-voice-assistant/venv/bin/python server/llm_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируй:
```bash
sudo systemctl enable quick-voice-assistant
sudo systemctl start quick-voice-assistant
sudo systemctl status quick-voice-assistant
```

### Windows (Task Scheduler)
1. **Открой Task Scheduler**
2. **Создай Basic Task**
3. **Назови:** "Quick Voice Assistant"
4. **Триггер:** At startup
5. **Действие:** Start a program
6. **Программа:** `C:\path\to\quick-voice-assistant\venv\Scripts\python.exe`
7. **Аргументы:** `server\llm_api_server.py`
8. **Рабочая папка:** `C:\path\to\quick-voice-assistant`

---

## 🛠️ УСТРАНЕНИЕ НЕПОЛАДОК

### Проблема: Сервер не запускается
```bash
# Проверь зависимости
pip list | grep fastapi

# Проверь порт
netstat -an | grep 8000

# Запусти с отладкой
python -u server/llm_api_server.py
```

### Проблема: Часы не подключаются
1. **Проверь IP адрес** в `watch_app/app_config.json`
2. **Убедись, что часы в той же WiFi сети**
3. **Проверь firewall** на компьютере
4. **Перезапусти приложение** на часах

### Проблема: Не работает Notion
1. **Проверь токен** в `.env`
2. **Убедись, что интеграция добавлена** к базам данных
3. **Проверь права доступа** к базам

### Проблема: Не работает Telegram
1. **Проверь токен бота** в `.env`
2. **Проверь chat_id** (должно быть число)
3. **Убедись, что бот запущен** и отвечает

### Проблема: Медленные ответы
1. **Проверь скорость WiFi**
2. **Оптимизируй настройки LLM**
3. **Увеличь количество воркеров** в конфигурации
4. **Включи кэширование**

---

## 📊 МОНИТОРИНГ

### Просмотр логов
```bash
# Логи сервера
tail -f logs/server.log

# Логи ошибок
tail -f logs/error.log

# Логи доступа
tail -f logs/access.log
```

### Метрики производительности
```bash
# Статус сервера
curl http://localhost:8000/health

# Метрики
curl http://localhost:8000/metrics
```

### Тестирование системы
```bash
# Полный тест
./scripts/test_system.sh

# Отдельные тесты
python scripts/test_system.py
```

---

## 🎯 РЕЗУЛЬТАТ

**После успешного развертывания ты получишь:**

✅ **Работающий сервер** на порту 8000  
✅ **Интеграцию с Notion** для автоматического создания элементов  
✅ **Интеграцию с Telegram** для уведомлений  
✅ **Приложение на часах** с голосовым управлением  
✅ **Систему мониторинга** и логирования  
✅ **Автозапуск** при загрузке системы  

### Тестирование workflow:

1. **Подними руку** → экран часов включается
2. **Говори** → "добавь задачу медитация"
3. **Получи ответ** на часах
4. **Проверь Telegram** → уведомление пришло
5. **Проверь Notion** → задача создана

**Система готова к использованию!** 🚀

---

## 📞 ПОДДЕРЖКА

### При проблемах:

1. **Проверь логи:** `tail -f logs/server.log`
2. **Запусти тесты:** `./scripts/test_system.sh`
3. **Проверь конфигурацию:** `nano .env`
4. **Перезапусти сервер:** `./scripts/start_server.sh`

### Полезные команды:

```bash
# Статус сервера
curl http://localhost:8000/health

# Тест голосовой команды
curl -X POST http://localhost:8000/watch/voice \
  -H "Content-Type: application/json" \
  -d '{"query": "добавь задачу тест", "context": "test"}'

# Отправка в Telegram
curl -X POST http://localhost:8000/telegram/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Тестовое сообщение", "source": "test"}'
```

**Удачи с использованием Quick Voice Assistant!** 🎤 