# 🚀 РУКОВОДСТВО ПО ДЕПЛОЮ НА RAILWAY

## 📋 ОБЗОР

Это руководство поможет развернуть твою систему Life System Bots на Railway с поддержкой DeepSea LLM, чтобы боты работали 24/7 без зависимости от ноутбука.

## 🎯 ЧТО БУДЕТ РАЗВЕРНУТО

- **Admin Bot** - админские функции управления
- **Enhanced Bot** - расширенный функционал с AI
- **Agent Team** - команда специализированных агентов
- **LLM API Server** - сервер для обработки запросов
- **DeepSea LLM Integration** - интеграция с твоей LLM

---

## 🚀 БЫСТРЫЙ СТАРТ (5 минут)

### 1. Подготовка

```bash
# Клонируй репозиторий (если еще не сделал)
git clone <your-repo>
cd .Life

# Создай конфигурационные файлы
python scripts/deploy_to_railway.py
```

### 2. Создание ботов в Telegram

Создай **3 разных бота** через @BotFather:

1. **Admin Bot** - для админских функций
2. **Enhanced Bot** - для расширенного функционала  
3. **Agent Bot** - для команды агентов

Сохрани токены для каждого бота.

### 3. Настройка переменных окружения

Создай файл `.env` на основе `.env.template`:

```bash
# Telegram Bot Tokens
TELEGRAM_BOT_TOKEN=your_admin_bot_token
TELEGRAM_ENHANCED_BOT_TOKEN=your_enhanced_bot_token
TELEGRAM_AGENT_BOT_TOKEN=your_agent_bot_token

# Telegram Users (твой ID)
TELEGRAM_ALLOWED_USERS=your_telegram_id
TELEGRAM_ADMIN_USERS=your_telegram_id

# Notion Configuration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASES={"tasks":"db_id","habits":"db_id","rituals":"db_id","reflections":"db_id","ideas":"db_id","materials":"db_id","agent_prompts":"db_id"}

# DeepSea LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 4. Деплой на Railway

```bash
# Установи Railway CLI
npm install -g @railway/cli

# Войди в Railway
railway login

# Создай проект
railway init

# Деплой
railway up
```

---

## 🔧 ПОДРОБНАЯ НАСТРОЙКА

### Шаг 1: Создание Telegram ботов

#### Admin Bot
```
1. Напиши @BotFather: /newbot
2. Название: Life System Admin
3. Username: your_life_admin_bot
4. Сохрани токен
```

#### Enhanced Bot
```
1. Напиши @BotFather: /newbot
2. Название: Life System Enhanced
3. Username: your_life_enhanced_bot
4. Сохрани токен
```

#### Agent Bot
```
1. Напиши @BotFather: /newbot
2. Название: Life System Agents
3. Username: your_life_agents_bot
4. Сохрани токен
```

### Шаг 2: Получение Telegram ID

```bash
# Напиши любому из ботов: /start
# Затем отправь: /my_id
# Сохрани полученный ID
```

### Шаг 3: Настройка Notion

1. **Создай интеграцию** в [Notion Developers](https://developers.notion.com)
2. **Получи токен** интеграции
3. **Добавь интеграцию** ко всем базам данных
4. **Скопируй ID** всех баз данных

### Шаг 4: Настройка DeepSea LLM

1. **Получи API ключ** OpenRouter
2. **Настрой модель** DeepSea в OpenRouter
3. **Проверь доступность** модели

---

## 🚀 ДЕПЛОЙ НА RAILWAY

### Вариант 1: Автоматический деплой

```bash
# Запусти автоматический скрипт
./scripts/quick_deploy.sh
```

### Вариант 2: Ручной деплой

```bash
# 1. Установи Railway CLI
npm install -g @railway/cli

# 2. Войди в Railway
railway login

# 3. Создай проект
railway init

# 4. Настрой переменные окружения
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set NOTION_TOKEN=your_token
railway variables set OPENROUTER_API_KEY=your_key

# 5. Деплой
railway up
```

### Вариант 3: GitHub Actions (автодеплой)

1. **Добавь RAILWAY_TOKEN в GitHub Secrets**
2. **Запушь код в main ветку**
3. **Railway автоматически задеплоит изменения**

---

## 🔍 ПРОВЕРКА РАБОТЫ

### 1. Проверка сервера

```bash
# Получи URL приложения
railway status

# Проверь health check
curl https://your-app.railway.app/health

# Проверь API docs
curl https://your-app.railway.app/docs
```

### 2. Проверка ботов

Отправь команды каждому боту:

```
/admin - Admin Bot
/help - Enhanced Bot  
/agents - Agent Bot
```

### 3. Проверка интеграций

```bash
# Проверь логи
railway logs

# Проверь переменные окружения
railway variables
```

---

## 📊 МОНИТОРИНГ И ЛОГИ

### Просмотр логов

```bash
# Все логи
railway logs

# Логи конкретного сервиса
railway logs --service admin-bot

# Логи в реальном времени
railway logs --follow
```

### Метрики производительности

```bash
# Статус приложения
railway status

# Использование ресурсов
railway metrics
```

### Уведомления

Настрой уведомления в Railway Dashboard:
- **Discord** - для уведомлений о деплоях
- **Email** - для критических ошибок
- **Slack** - для команды (если есть)

---

## 🔧 НАСТРОЙКА АВТОДЕПЛОЯ

### GitHub Actions

1. **Создай файл** `.github/workflows/railway-deploy.yml`
2. **Добавь секреты** в GitHub:
   - `RAILWAY_TOKEN`
   - `TELEGRAM_BOT_TOKEN`
   - `NOTION_TOKEN`
   - `OPENROUTER_API_KEY`

3. **Настрой триггеры**:
   - Push в main ветку
   - Pull Request в main ветку
   - Ручной запуск

### Автоматические обновления

```bash
# Обновление кода
git add .
git commit -m "Update bots"
git push origin main

# Railway автоматически задеплоит изменения
```

---

## 🛠️ УСТРАНЕНИЕ НЕПОЛАДОК

### Проблема: Бот не отвечает

**Решение:**
```bash
# Проверь логи
railway logs --service admin-bot

# Проверь переменные окружения
railway variables

# Перезапусти сервис
railway service restart admin-bot
```

### Проблема: Ошибки подключения к Notion

**Решение:**
1. Проверь токен Notion
2. Убедись, что интеграция добавлена к базам
3. Проверь права доступа

### Проблема: Ошибки DeepSea LLM

**Решение:**
1. Проверь API ключ OpenRouter
2. Убедись, что модель доступна
3. Проверь лимиты использования

### Проблема: Высокое потребление ресурсов

**Решение:**
```bash
# Оптимизируй настройки
railway variables set MAX_WORKERS=2
railway variables set CACHE_SIZE=500

# Перезапусти сервисы
railway service restart
```

---

## 💰 СТОИМОСТЬ И ЛИМИТЫ

### Railway Pricing

- **Free Tier**: $5 кредитов/месяц
- **Pro Plan**: $20/месяц
- **Team Plan**: $50/месяц

### Оценка стоимости

**Для твоей системы (4 сервиса):**
- **Admin Bot**: ~$2/месяц
- **Enhanced Bot**: ~$3/месяц  
- **Agent Bot**: ~$3/месяц
- **LLM Server**: ~$5/месяц

**Итого: ~$13/месяц**

### Оптимизация затрат

```bash
# Уменьши количество воркеров
railway variables set MAX_WORKERS=2

# Включи кэширование
railway variables set ENABLE_CACHING=True

# Оптимизируй логирование
railway variables set LOG_LEVEL=WARNING
```

---

## 🎯 РЕЗУЛЬТАТ

**После успешного деплоя ты получишь:**

✅ **Работающие боты 24/7** без зависимости от ноутбука  
✅ **Автоматические обновления** через GitHub  
✅ **Мониторинг и логи** в реальном времени  
✅ **Интеграцию с DeepSea LLM** через OpenRouter  
✅ **Масштабируемость** под нагрузку  
✅ **Резервное копирование** данных  

### Тестирование workflow:

1. **Отправь команду** любому боту в Telegram
2. **Получи ответ** с DeepSea LLM
3. **Проверь создание** записи в Notion
4. **Мониторь логи** в Railway Dashboard

**Система готова к продуктивному использованию!** 🚀

---

## 📞 ПОДДЕРЖКА

### Полезные команды:

```bash
# Статус всех сервисов
railway status

# Логи в реальном времени
railway logs --follow

# Переменные окружения
railway variables

# Перезапуск сервиса
railway service restart <service-name>

# Открыть в браузере
railway open
```

### Документация:

- [Railway Docs](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Notion API](https://developers.notion.com/)
- [OpenRouter API](https://openrouter.ai/docs)

### При проблемах:

1. **Проверь логи**: `railway logs`
2. **Проверь переменные**: `railway variables`
3. **Перезапусти сервисы**: `railway service restart`
4. **Обратись в поддержку**: Railway Discord 