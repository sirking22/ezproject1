# 📱 Руководство по установке на Xiaomi Watch S

## 🎯 Подготовка

### 1. Требования
- **Xiaomi Watch S** с Wear OS
- **Компьютер** с Android Studio
- **USB кабель** или **WiFi ADB**
- **Локальный LLM сервер** (Llama 70B)

### 2. Настройка ADB
```bash
# Установка ADB (если не установлен)
# Windows: скачай Android SDK Platform Tools
# macOS: brew install android-platform-tools
# Linux: sudo apt install adb

# Проверка подключения
adb devices

# Должно показать:
# List of devices attached
# 1234567890abcdef    device
```

### 3. Настройка WiFi ADB (опционально)
```bash
# Подключи часы по USB
adb tcpip 5555

# Отключи USB и подключись по WiFi
adb connect 192.168.1.100:5555

# Проверь подключение
adb devices
```

## 🚀 Установка

### 1. Сборка приложения
```bash
# Клонируй репозиторий
git clone <repository>
cd wear_app

# Сборка APK
./gradlew assembleDebug

# APK будет в:
# app/build/outputs/apk/debug/app-debug.apk
```

### 2. Установка на часы
```bash
# Установка через ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Или через Android Studio:
# 1. Открой проект в Android Studio
# 2. Подключи часы
# 3. Run -> Run 'app' -> Выбери часы
```

### 3. Первый запуск
1. **Найди приложение** на часах
2. **Открой** "Voice Assistant"
3. **Предоставь разрешения**:
   - Микрофон
   - Интернет
   - Уведомления

## ⚙️ Настройка

### 1. Конфигурация серверов
Отредактируй `app/src/main/AndroidManifest.xml`:
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

### 2. Пересборка и переустановка
```bash
# Пересборка с новыми настройками
./gradlew assembleDebug

# Переустановка
adb uninstall com.quickvoice.wear
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 🧪 Тестирование

### 1. Проверка подключения
```bash
# Проверь, что часы подключены
adb devices

# Проверь логи приложения
adb logcat | grep QuickVoice
```

### 2. Тест голосовых команд
1. **Открой приложение** на часах
2. **Нажми кнопку микрофона**
3. **Скажи**: "Добавить задачу купить продукты"
4. **Проверь результат**:
   - Уведомление на часах
   - Запись в Notion
   - Сообщение в Telegram

### 3. Тест интеграций
```bash
# Проверь LLM сервер
curl http://192.168.1.100:8000/health

# Проверь Notion API
curl -H "Authorization: Bearer your_token" \
     https://api.notion.com/v1/users/me

# Проверь Telegram бота
curl https://api.telegram.org/botyour_token/getMe
```

## 🔧 Устранение неполадок

### Проблемы с ADB
```bash
# Перезапуск ADB
adb kill-server
adb start-server

# Проверка устройств
adb devices

# Сброс настроек
adb shell settings reset-to-defaults
```

### Проблемы с микрофоном
1. **Проверь разрешения** в настройках часов
2. **Перезапусти приложение**
3. **Перезагрузи часы**
4. **Проверь другие приложения** с микрофоном

### Проблемы с сетью
1. **Проверь WiFi** на часах
2. **Проверь IP адрес** LLM сервера
3. **Проверь файрвол** на компьютере
4. **Проверь порты** (8000 для LLM)

### Проблемы с установкой
```bash
# Очистка и переустановка
adb uninstall com.quickvoice.wear
adb install app/build/outputs/apk/debug/app-debug.apk

# Принудительная остановка
adb shell am force-stop com.quickvoice.wear

# Очистка данных
adb shell pm clear com.quickvoice.wear
```

## 📱 Использование

### Быстрые команды
- **"Добавить задачу"** - создание задачи
- **"Записать мысль"** - сохранение рефлексии
- **"Отметить привычку"** - трекинг привычек

### Жесты (планируется)
- **Поднятие руки** - активация записи
- **Поворот запястья** - остановка записи
- **Двойное касание** - быстрый доступ

### Автоматизация (планируется)
- **Утренние напоминания** - 9:00
- **Обеденные подсказки** - 12:00
- **Вечерние рефлексии** - 18:00

## 🔄 Обновления

### Автоматические обновления
```bash
# Проверка обновлений
git pull origin main

# Пересборка
./gradlew assembleDebug

# Переустановка
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Ручные обновления
1. **Скачай новую версию**
2. **Пересобери проект**
3. **Переустанови приложение**

## 📊 Мониторинг

### Логи приложения
```bash
# Просмотр логов в реальном времени
adb logcat | grep QuickVoice

# Сохранение логов в файл
adb logcat | grep QuickVoice > voice_logs.txt
```

### Метрики использования
- **Количество команд** - в логах
- **Время ответа** - в логах
- **Ошибки** - в логах и уведомлениях

## 🎯 Оптимизация

### Батарея
- **Закрывай приложение** когда не используешь
- **Отключай WiFi** если не нужен
- **Используй энергосберегающий режим**

### Производительность
- **Перезагружай часы** раз в неделю
- **Очищай кэш** приложения
- **Обновляй прошивку** часов

---

*Готово! Твой голосовой ассистент работает на часах* 