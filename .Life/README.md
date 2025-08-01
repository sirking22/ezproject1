# 🚀 Notion-Telegram-LLM: Система личностного развития с ИИ-командой

Персональная система развития с интеграцией Notion, Telegram и AI для управления привычками, задачами, знаниями и рефлексиями. **Теперь с полноценной ИИ-командой разработчиков под управлением мастер-агента!**

## 🎯 Что это

Система, которая помогает:
- 📝 **Управлять задачами** через Telegram бота
- 🔄 **Отслеживать привычки** и их прогресс
- 💭 **Вести рефлексии** и анализировать настроение
- 📚 **Накопливать знания** и опыт
- 🎯 **Планировать цели** и отслеживать прогресс
- 🤖 **Получать AI-рекомендации** на основе данных
- 👥 **Работать с ИИ-командой** разработчиков под управлением мастер-агента

## 🚀 Быстрый старт

### 1. Установка
```bash
git clone <repository>
cd .Life
pip install -r requirements.txt
```

### 2. Настройка
Скопируйте `env_example.txt` в `.env` и заполните:
```
NOTION_TOKEN=your_notion_token
TELEGRAM_BOT_TOKEN=your_telegram_token
NOTION_RITUALS_DATABASE_ID=your_database_id
# ... остальные настройки
```

### 3. Запуск
```bash
# Основной бот для личностного развития
python run_admin_bot.py

# Тест ИИ-команды разработчиков
python test_master_agent.py
```

### 4. Первые команды
```
/validate all                    # Проверить систему
/todo "Купить продукты"          # Добавить задачу
/habit "Медитация"              # Добавить привычку
/morning                         # Создать утренний ритуал
/progress                        # Посмотреть прогресс
```

## 🤖 ИИ-команда разработчиков

### Мастер-агент
Центральный координатор, который:
- 🎯 **Автоматически назначает** задачи подходящим агентам
- 📊 **Отслеживает производительность** каждого агента
- 🔄 **Оптимизирует работу команды** на основе метрик
- 💡 **Генерирует рекомендации** по улучшению
- ⚡ **Перераспределяет задачи** при перегрузке

### Специалисты команды
- **Product Manager** - приоритизация, планирование, анализ требований
- **Developer** - кодирование, архитектура, рефакторинг
- **LLM Researcher** - оптимизация промптов, исследование моделей
- **DevOps** - CI/CD, инфраструктура, автоматизация
- **QA/Tester** - тестирование, качество, автоматизация
- **Support/Helpdesk** - поддержка пользователей, документация
- **Growth/Marketing** - аналитика, эксперименты, рост
- **Meta-Agent** - координация, оптимизация, стратегия

### Как это работает
1. **Создание задачи** → Мастер-агент анализирует требования
2. **Выбор агента** → Автоматическое назначение на основе специализаций
3. **Выполнение** → Агент работает с улучшенным промптом
4. **Анализ** → Мастер-агент оценивает качество и производительность
5. **Оптимизация** → Автоматические улучшения и перераспределение

## 📱 Основные команды

### Быстрые действия
- `/todo [задача]` - добавить задачу
- `/habit [название]` - добавить привычку
- `/reflection [текст]` - добавить рефлексию
- `/idea [идея]` - сохранить идею
- `/morning` - утренний ритуал
- `/evening` - вечерняя рефлексия

### Аналитика
- `/progress` - отчет о прогрессе
- `/mood` - анализ настроения
- `/insights` - персональные инсайты
- `/recommendations` - рекомендации

### Управление данными
- `/validate [table]` - проверка структуры
- `/list [table] [limit]` - список элементов
- `/search [table] [query]` - поиск
- `/create [table] [data]` - создание
- `/update [table] [id] [data]` - обновление
- `/delete [table] [id]` - удаление

## 🗄️ Базы данных Notion

Система работает с 7 базами данных:
- **Rituals** - ритуалы и рутины
- **Habits** - привычки и трекинг
- **Reflections** - размышления и инсайты
- **Guides** - руководства и знания
- **Actions** - задачи и проекты
- **Terms** - термины и понятия
- **Materials** - материалы и ресурсы

## 📊 Ежедневный workflow

### Утром
1. `/morning` - создать утренний ритуал
2. `/todo "важные задачи"` - добавить задачи дня
3. `/habit "название"` - добавить новую привычку

### В течение дня
1. `/reflection "мысли и инсайты"` - записывать идеи
2. `/idea "новая идея"` - сохранять идеи
3. `/progress` - проверять прогресс

### Вечером
1. `/evening` - создать вечернюю рефлексию
2. `/reflection "размышления о дне"` - анализировать день
3. `/mood` - проверить настроение

## 🛠 Техническая информация

### Архитектура
- **Telegram Bot** - интерфейс пользователя
- **Notion API** - хранение данных
- **Universal Repository** - единый интерфейс для всех таблиц
- **AI Integration** - аналитика и рекомендации
- **Master Agent** - управление ИИ-командой
- **Enhanced Prompts** - улучшенные промпты агентов

### Структура проекта
```
src/
├── telegram/          # Telegram бот
├── notion/           # Работа с Notion
├── agents/           # ИИ-агенты и мастер-агент
│   ├── master_agent.py      # Мастер-агент
│   ├── enhanced_prompts.py  # Улучшенные промпты
│   └── agent_core.py        # Ядро агентов
├── utils/            # Утилиты
└── core/             # Основные компоненты
```

## 📚 Документация

- **[PERSONAL_DEVELOPMENT_STRATEGY.md](PERSONAL_DEVELOPMENT_STRATEGY.md)** - главная стратегия проекта
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - подробная настройка
- **[UNIVERSAL_REPOSITORY_GUIDE.md](UNIVERSAL_REPOSITORY_GUIDE.md)** - техническая документация

## 🧪 Тестирование

```bash
# Тест универсального репозитория
python test_universal_repository.py

# Тест быстрых команд
python test_quick_commands.py

# Тест интеграции
python test_integration.py

# Тест ИИ-команды разработчиков
python test_master_agent.py
```

## 🎯 Критерии успеха

Система работает, если:
- ✅ Используешь её каждый день
- ✅ Чувствуешь, что она помогает принимать решения
- ✅ Видишь прогресс в привычках и целях
- ✅ Получаешь полезные инсайты и рекомендации
- ✅ ИИ-команда эффективно решает задачи
- ✅ Мастер-агент оптимизирует процессы

## 🚀 Следующие шаги

1. **Протестируй систему** - запусти бота и попробуй команды
2. **Добавь первые данные** - задачи, привычки, рефлексии
3. **Используй аналитику** - смотри отчеты и рекомендации
4. **Запусти ИИ-команду** - протестируй мастер-агента
5. **Развивай дальше** - добавляй новые потребности

## 🤖 Особенности ИИ-команды

### Автоматическое назначение задач
- Анализ требований через LLM
- Выбор агента на основе специализаций
- Учет текущей загрузки и производительности

### Оптимизация производительности
- Отслеживание метрик каждого агента
- Автоматическое перераспределение задач
- Рекомендации по улучшению промптов

### Улучшенные промпты
- Детальные инструкции для каждого агента
- Специализации и технологии
- Структурированные ответы

### Координация команды
- Единый интерфейс через мастер-агента
- Автоматические отчеты и аналитика
- Проактивная оптимизация процессов

## 🧠 Новые возможности мастер-агента

- **Автоматическая генерация и обновление промптов** для агентов на основе истории задач и качества
- **Автоматические ретроспективы**: мастер-агент сам пишет summary по команде, ошибкам, инсайтам
- **Логирование истории решений**: все ключевые решения и ретроспективы сохраняются в Notion или локально

---

**Главное**: Система должна помогать тебе развиваться, а не отнимать время. Адаптируй под себя!

**ИИ-команда**: Автоматизирует рутину и фокусирует на важном, а мастер-агент обеспечивает эффективность! 