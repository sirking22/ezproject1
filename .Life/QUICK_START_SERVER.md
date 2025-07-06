# 🚀 Быстрый старт - Локальный LLM сервер

## ⚡ Установка за 5 минут

### 1. Скачай файлы
```bash
# Создай папку
mkdir llm_server
cd llm_server

# Скопируй файлы:
# - simple_llm_server.py
# - requirements.txt
# - start_server.py
```

### 2. Установи Python зависимости
```bash
pip install requests python-dotenv colorlog
```

### 3. Запусти сервер
```bash
python simple_llm_server.py
```

### 4. Проверь работу
```bash
# В новом терминале
curl http://localhost:8000/health
```

## 🎯 Что получится

Сервер будет доступен по адресу:
- **Локально**: `http://localhost:8000`
- **В сети**: `http://192.168.1.100:8000` (твой IP)

## 📱 Для Android и часов

Обнови IP адрес в приложениях:
```xml
<meta-data
    android:name="com.quickvoice.LLM_SERVER_URL"
    android:value="http://192.168.1.100:8000" />
```

## 🧪 Тестирование

```bash
# Проверь здоровье
curl http://localhost:8000/health

# Тестовый запрос
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Добавить задачу купить продукты","context":"home"}'
```

## 🛑 Остановка

Нажми `Ctrl+C` в терминале с сервером.

---

*Готово! Сервер работает и готов принимать запросы от приложений!* 