# 🤖 Notion-Telegram-LLM Integration

**Система управления задачами и обучением** через интеграцию Notion, Telegram и LLM.

## 🎯 ЦЕЛИ ПРОЕКТА

- **Управление задачами**: Создание, назначение, отслеживание через Telegram
- **KPI система**: Централизованные метрики для Арсения и команды
- **LLM интеграция**: AI-помощь в анализе и принятии решений
- **Автоматизация**: Синхронизация между Notion, Telegram, внешними системами

## 🏗️ АРХИТЕКТУРА

### Основные компоненты:
- **Telegram боты** (2): corporate_bot + life_bot
- **Notion API**: 7+ баз данных (проекты, задачи, KPI, материалы)
- **LLM системы**: DeepSeek, Claude, GPT-4 через OpenRouter
- **MCP сервер**: Централизованное управление схемами и операциями

### Ключевые технологии:
- Python 3.9+
- Telegram Bot API
- Notion API
- DeepSeek (экономичная LLM)
- Yandex.Disk API

## 📚 ДОКУМЕНТАЦИЯ

### 🎯 Основные документы:
- **[AI_CONTEXT.md](AI_CONTEXT.md)** - Архитектура, правила, контекст системы
- **[FEATURES.md](FEATURES.md)** - Описание функционала и возможностей
- **[DAILY_WORKFLOW.md](DAILY_WORKFLOW.md)** - Ежедневные процессы и чек-листы
- **[DECISION_EFFICIENCY_DASHBOARD_PLAN.md](DECISION_EFFICIENCY_DASHBOARD_PLAN.md)** - KPI система и метрики

### 🔧 Технические гайды:
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Быстрый старт (15 минут)
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Разработка и расширение
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API и интеграции
- **[MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md)** - Настройка MCP сервера

### 🛠️ Troubleshooting:
- **[ERRORS_SOLUTIONS.md](ERRORS_SOLUTIONS.md)** - Решения ошибок
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Диагностика проблем
- **[ERRORS_SPEECHKIT_STT.md](ERRORS_SPEECHKIT_STT.md)** - Проблемы с распознаванием речи

### 📊 Структура данных:
- **[DATA_STRUCTURE_GUIDE.md](DATA_STRUCTURE_GUIDE.md)** - Схемы и связи
- **[CI_SETUP.md](CI_SETUP.md)** - Настройка CI/CD

## 🚀 БЫСТРЫЙ СТАРТ

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка .env (см. env.example)
cp env.example .env
# Заполнить API ключи и ID баз

# 3. Запуск MCP сервера
python notion_mcp_server.py

# 4. Запуск Telegram бота
python designer_report_bot.py
```

## 📋 КРИТИЧЕСКИЕ ПРАВИЛА

### 🔄 Всегда используй:
- **MCP сервер** для операций с Notion
- **Централизованные схемы** (notion_database_schemas.py)
- **Регистры исполнителей** (assignees_registry.py, notion_users.py)
- **Документирование ошибок** в ERRORS_SOLUTIONS.md

### ⚠️ Никогда не делай:
- Прямые вызовы Notion API без MCP
- Дублирование схем в разных местах
- Создание новых файлов без базовой инфраструктуры
- Изменения без тестирования

## 📁 СТРУКТУРА ПРОЕКТА

```
├── docs/                    # Документация
├── services/                # Бизнес-логика
├── utils/                   # Утилиты и хелперы
├── config/                  # Конфигурация
├── shared_code/             # Общий код
├── tests/                   # Тесты
├── reports/                 # Отчёты и аналитика
└── docs_archive/           # Архив устаревших документов
```

## 🎯 ТЕКУЩИЕ ПРИОРИТЕТЫ

1. **KPI система для Арсения** - назначение и отслеживание метрик
2. **Автоматизация процессов** - синхронизация и уведомления
3. **LLM интеграция** - AI-помощь в анализе и принятии решений
4. **Масштабирование** - поддержка новых баз и пользователей

---

**📞 Поддержка**: Все вопросы и проблемы документируются в ERRORS_SOLUTIONS.md
**🔄 Обновления**: Архив устаревших документов в docs_archive/
**🎯 Фокус**: Максимальная автоматизация и AI-помощь в управлении задачами 