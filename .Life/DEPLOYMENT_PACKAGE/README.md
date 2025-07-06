# 🚀 ПАКЕТ РАЗВЕРТЫВАНИЯ: QUICK VOICE ASSISTANT

## 📦 СОДЕРЖИМОЕ ПАКЕТА

```
DEPLOYMENT_PACKAGE/
├── README.md                    # Этот файл
├── INSTALLATION_GUIDE.md        # Пошаговая инструкция установки
├── 
├── server/
│   ├── llm_api_server.py        # FastAPI сервер для LLM
│   ├── requirements.txt         # Python зависимости
│   └── config.py               # Конфигурация сервера
├── 
├── watch_app/
│   ├── xiaomi_watch_app.js      # Приложение для часов
│   ├── app_config.json          # Конфигурация приложения
│   └── quick_voice_assistant.js # Упрощенный ассистент
├── 
├── integration/
│   ├── notion_integration.py    # Интеграция с Notion
│   ├── telegram_integration.py  # Интеграция с Telegram
│   └── voice_processor.py       # Обработка голоса
├── 
└── scripts/
    ├── install.sh              # Скрипт автоматической установки
    ├── start_server.sh         # Запуск сервера
    └── test_system.py          # Тестирование системы
```

## 🎯 БЫСТРЫЙ СТАРТ

### 1. Автоматическая установка (рекомендуется)
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Ручная установка
Следуй инструкции в `INSTALLATION_GUIDE.md`

## 📋 ТРЕБОВАНИЯ

- **Python 3.8+**
- **Node.js 16+**
- **Xiaomi Watch S** (или совместимые часы)
- **WiFi сеть** для связи часов с компьютером
- **Локальная Llama 70B** (опционально)

## 🔧 КОНФИГУРАЦИЯ

1. **Настрой IP адрес** в `watch_app/app_config.json`
2. **Добавь токены** в `server/config.py`
3. **Проверь пути** к LLM модели

## 🚀 ЗАПУСК

```bash
# Запуск сервера
./scripts/start_server.sh

# Тестирование
python scripts/test_system.py
```

## 📞 ПОДДЕРЖКА

При проблемах:
1. Проверь логи в `logs/`
2. Запусти тесты: `python scripts/test_system.py`
3. Обратись к `INSTALLATION_GUIDE.md`

---

**Готов к развертыванию!** 🚀 