# 🚀 Полное руководство по установке AI-экосистемы

## 🎯 Что устанавливаем

1. **Локальный LLM сервер** - на компьютере
2. **Android приложение** - на телефоне
3. **Wear OS приложение** - на часах
4. **Интеграции** - Notion + Telegram

## 📋 Требования

### Компьютер (сервер)
- **Python 3.8+**
- **Интернет соединение**
- **Статический IP** (желательно)
- **8GB RAM** (минимум)

### Телефон
- **Android 8.0+**
- **Интернет соединение**
- **Разрешения**: микрофон, интернет

### Часы
- **Wear OS 2.0+**
- **Xiaomi Watch S** (рекомендуется)
- **Подключение к телефону**

## 🖥️ Шаг 1: Установка локального сервера

### 1.1 Подготовка компьютера
```bash
# Проверь Python
python --version  # Должно быть 3.8+

# Создай папку для проекта
mkdir ai_ecosystem
cd ai_ecosystem

# Клонируй или скачай файлы
# (скопируй все файлы из wear_app/server/ в эту папку)
```

### 1.2 Установка зависимостей
```bash
# Установи зависимости
pip install -r requirements.txt

# Или установи вручную
pip install requests python-dotenv colorlog
```

### 1.3 Запуск сервера
```bash
# Простой запуск
python simple_llm_server.py

# Или с проверками
python start_server.py
```

### 1.4 Проверка работы
```bash
# Проверь здоровье сервера
curl http://localhost:8000/health

# Проверь статус
curl http://localhost:8000/status

# Тестовый запрос
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Добавить задачу купить продукты","context":"home"}'
```

### 1.5 Настройка автозапуска (опционально)
```bash
# Windows: создай .bat файл
echo @echo off > start_server.bat
echo cd /d "%~dp0" >> start_server.bat
echo python simple_llm_server.py >> start_server.bat
echo pause >> start_server.bat

# Добавь в автозагрузку Windows
# Win+R → shell:startup → скопируй start_server.bat
```

## 📱 Шаг 2: Установка Android приложения

### 2.1 Подготовка
```bash
# Убедись, что телефон подключен
adb devices

# Должно показать:
# List of devices attached
# 1234567890abcdef    device
```

### 2.2 Настройка конфигурации
Отредактируй `android_app/app/src/main/AndroidManifest.xml`:
```xml
<meta-data
    android:name="com.quickvoice.LLM_SERVER_URL"
    android:value="http://192.168.1.100:8000" />
<meta-data
    android:name="com.quickvoice.NOTION_TOKEN"
    android:value="your_notion_token" />
<meta-data
    android:name="com.quickvoice.TELEGRAM_BOT_TOKEN"
    android:value="your_telegram_bot_token" />
```

### 2.3 Сборка и установка
```bash
cd android_app

# Сборка
./gradlew assembleDebug

# Установка
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 2.4 Настройка на телефоне
1. **Открой приложение** "Quick Voice Assistant"
2. **Предоставь разрешения**:
   - Микрофон
   - Интернет
   - Уведомления
3. **Протестируй**: нажми кнопку и скажи "Добавить задачу купить продукты"

## ⌚ Шаг 3: Установка Wear OS приложения

### 3.1 Подготовка часов
```bash
# Проверь подключение часов
adb devices

# Должно показать и телефон, и часы:
# List of devices attached
# 1234567890abcdef    device
# 9876543210fedcba    device
```

### 3.2 Настройка конфигурации
Отредактируй `wear_app/app/src/main/AndroidManifest.xml`:
```xml
<meta-data
    android:name="com.quickvoice.wear.LLM_SERVER_URL"
    android:value="http://192.168.1.100:8000" />
<meta-data
    android:name="com.quickvoice.wear.NOTION_TOKEN"
    android:value="your_notion_token" />
<meta-data
    android:name="com.quickvoice.wear.TELEGRAM_BOT_TOKEN"
    android:value="your_telegram_bot_token" />
```

### 3.3 Сборка и установка
```bash
cd wear_app

# Сборка
./gradlew assembleDebug

# Установка на часы
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 3.4 Настройка на часах
1. **Найди приложение** "Voice Assistant" на часах
2. **Открой приложение**
3. **Предоставь разрешения**: микрофон
4. **Протестируй**: нажми кнопку и скажи "Добавить задачу"

## 🔗 Шаг 4: Настройка интеграций

### 4.1 Notion интеграция
1. **Создай интеграцию** в Notion:
   - Settings → Integrations → Develop your own integrations
   - Создай новую интеграцию
   - Скопируй Internal Integration Token

2. **Добавь базы данных**:
   - Создай базы: Tasks, Reflections, Habits
   - Поделись с интеграцией
   - Скопируй ID баз данных

3. **Обнови токены** в приложениях:
   - Замени `your_notion_token` на реальный токен
   - Обнови ID баз данных в коде
   - Пересобери и переустанови приложения

### 4.2 Telegram интеграция
1. **Создай бота**:
   - Напиши @BotFather в Telegram
   - `/newbot` → выбери имя и username
   - Скопируй токен бота

2. **Получи chat_id**:
   - Напиши боту любое сообщение
   - Открой: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Скопируй chat_id

3. **Обнови токены** в приложениях:
   - Замени `your_telegram_bot_token` на реальный токен
   - Обнови chat_id в коде
   - Пересобери и переустанови приложения

## 🧪 Шаг 5: Тестирование системы

### 5.1 Проверка сервера
```bash
# Проверь, что сервер работает
curl http://192.168.1.100:8000/health

# Должен вернуть:
# {"status": "healthy", "timestamp": "...", "uptime": 123.45}
```

### 5.2 Тест Android приложения
1. **Открой приложение** на телефоне
2. **Нажми кнопку микрофона**
3. **Скажи**: "Добавить задачу купить продукты"
4. **Проверь**:
   - Уведомление в приложении
   - Запись в Notion
   - Сообщение в Telegram

### 5.3 Тест Wear OS приложения
1. **Открой приложение** на часах
2. **Нажми кнопку микрофона**
3. **Скажи**: "Добавить задачу купить продукты"
4. **Проверь**:
   - Уведомление на часах
   - Запись в Notion
   - Сообщение в Telegram

## 🔧 Устранение неполадок

### Проблемы с сервером
```bash
# Проверь, что сервер запущен
netstat -an | grep 8000

# Проверь логи
tail -f llm_server.log

# Перезапусти сервер
pkill -f simple_llm_server.py
python simple_llm_server.py
```

### Проблемы с Android
```bash
# Проверь подключение
adb devices

# Переустанови приложение
adb uninstall com.quickvoice
adb install app/build/outputs/apk/debug/app-debug.apk

# Проверь логи
adb logcat | grep QuickVoice
```

### Проблемы с часами
```bash
# Проверь подключение часов
adb devices

# Переустанови приложение
adb uninstall com.quickvoice.wear
adb install app/build/outputs/apk/debug/app-debug.apk

# Проверь логи
adb logcat | grep QuickVoice
```

### Проблемы с сетью
1. **Проверь IP адрес** компьютера
2. **Проверь файрвол** Windows
3. **Проверь роутер** - открой порт 8000
4. **Проверь подключение**:
   ```bash
   ping 192.168.1.100
   telnet 192.168.1.100 8000
   ```

## 📊 Мониторинг

### Логи сервера
```bash
# Просмотр логов в реальном времени
tail -f llm_server.log

# Поиск ошибок
grep ERROR llm_server.log
```

### Статистика использования
- **Количество запросов** - в логах сервера
- **Время ответа** - в логах приложений
- **Ошибки** - в логах и уведомлениях

## 🚀 Автоматизация

### Автозапуск сервера
```bash
# Windows: создай задачу в Планировщике
# Linux: добавь в crontab
# macOS: добавь в LaunchAgents
```

### Мониторинг здоровья
```bash
# Скрипт проверки
curl -f http://localhost:8000/health || echo "Сервер не отвечает"
```

## 🎯 Результат

После установки у тебя будет:

✅ **Локальный LLM сервер** - работает на компьютере  
✅ **Android приложение** - голосовые команды с телефона  
✅ **Wear OS приложение** - голосовые команды с часов  
✅ **Notion интеграция** - автоматическое сохранение данных  
✅ **Telegram уведомления** - быстрые ответы в мессенджере  
✅ **Полная экосистема** - все компоненты работают вместе  

## 📞 Поддержка

### Полезные команды
```bash
# Проверка всей системы
curl http://192.168.1.100:8000/health
adb devices
adb logcat | grep QuickVoice

# Перезапуск сервера
pkill -f simple_llm_server.py
python simple_llm_server.py

# Переустановка приложений
adb uninstall com.quickvoice
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Логи и отладка
- **Сервер**: `llm_server.log`
- **Android**: `adb logcat | grep QuickVoice`
- **Часы**: `adb logcat | grep QuickVoice`

---

*Готово! Твоя персональная AI-экосистема работает!* 