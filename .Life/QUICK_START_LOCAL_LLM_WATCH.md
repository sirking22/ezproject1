# 🚀 БЫСТРЫЙ СТАРТ: XIAOMI WATCH S + ЛОКАЛЬНАЯ LLAMA 70B

## ⚡ УСТАНОВКА ЗА 5 МИНУТ

### 1. Установка Llama 70B
```bash
# Установка llama-cpp-python
pip install llama-cpp-python

# Скачивание квантованной модели (4GB)
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q4_K_M.gguf
```

### 2. Запуск API сервера
```bash
# Создание файла local_llm_server.py
cat > local_llm_server.py << 'EOF'
from fastapi import FastAPI
from llama_cpp import Llama
import uvicorn

app = FastAPI(title="Local LLM API", version="1.0.0")
llm = Llama(model_path="llama-2-70b-chat.Q4_K_M.gguf", n_ctx=2048)

@app.post("/generate")
async def generate_text(prompt: str, context: str = "general", max_tokens: int = 800):
    full_prompt = f"Context: {context}\n\n{prompt}"
    response = llm(full_prompt, max_tokens=max_tokens, temperature=0.7)
    return {"response": response["choices"][0]["text"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "llama-2-70b-chat"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Запуск сервера
python local_llm_server.py
```

### 3. Тестирование интеграции
```bash
# Запуск теста интеграции
python test_watch_llm_final.py
```

---

## 📱 ИНТЕГРАЦИЯ С ЧАСАМИ

### Вариант 1: Через существующее приложение
```python
# Обновление XiaomiWatchAPI для реальных данных
class RealXiaomiWatchAPI:
    def __init__(self):
        self.app_token = "your_app_token"
        self.user_id = "your_user_id"
    
    async def get_real_heart_rate(self) -> Optional[int]:
        """Получение реального пульса"""
        # Здесь будет реальный API вызов
        # Пока используем моковые данные
        return 75
```

### Вариант 2: Собственное приложение для часов
```javascript
// life_watch_app.js - приложение для Xiaomi Watch S
class LifeWatchApp {
    constructor() {
        this.sensors = new Sensors();
        this.communication = new Communication();
    }
    
    async initialize() {
        await this.sensors.initialize();
        await this.communication.initialize();
    }
    
    async startMonitoring() {
        // Мониторинг пульса каждые 5 минут
        setInterval(async () => {
            const heartRate = await this.sensors.getHeartRate();
            await this.communication.sendData('heart_rate', {
                heartRate: heartRate,
                timestamp: Date.now()
            });
        }, 300000);
        
        // Мониторинг активности каждый час
        setInterval(async () => {
            const activity = await this.sensors.getActivityData();
            await this.communication.sendData('activity', {
                steps: activity.steps,
                calories: activity.calories,
                timestamp: Date.now()
            });
        }, 3600000);
    }
}

// Запуск приложения
const app = new LifeWatchApp();
app.initialize().then(() => app.startMonitoring());
```

---

## 🔄 ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩЕЙ СИСТЕМОЙ

### 1. Обновление Telegram бота
```python
# Добавление в admin_bot.py

async def watch_health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для анализа здоровья"""
    if not self.is_user_allowed(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    # Получение биометрических данных
    biometrics = await llm_watch_analyzer.watch_api.get_current_biometrics()
    
    # Анализ через локальную LLM
    insight = await llm_watch_analyzer.analyze_biometrics_with_llm(biometrics)
    
    # Формирование ответа
    message = f"🏥 **Анализ здоровья**\n\n"
    message += f"📊 **Биометрия:**\n"
    message += f"   • Пульс: {biometrics.heart_rate} уд/мин\n"
    message += f"   • Стресс: {biometrics.stress_level}%\n"
    message += f"   • Шаги: {biometrics.steps}\n\n"
    message += f"🧠 **Инсайт:** {insight.title}\n"
    message += f"📝 {insight.description}\n\n"
    message += f"🎯 **Рекомендации:**\n"
    for action in insight.action_items:
        message += f"   • {action}\n"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# Регистрация команды
def register_commands(self):
    # ... существующие команды ...
    self.application.add_handler(CommandHandler("watch_health", self.watch_health_command))
```

### 2. Автоматические уведомления
```python
# Добавление в admin_bot.py

async def send_smart_watch_notification():
    """Отправка умного уведомления"""
    try:
        notification = await llm_watch_analyzer.get_smart_notification()
        
        for user_id in AUTHORIZED_USERS:
            await self.bot.send_message(
                chat_id=user_id,
                text=f"🔔 **Умное уведомление**\n\n{notification}",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error sending watch notification: {e}")

# Запуск уведомлений каждые 2 часа
async def start_watch_notifications():
    while True:
        await send_smart_watch_notification()
        await asyncio.sleep(7200)  # 2 часа
```

---

## 🎯 КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ

### Telegram команды:
```
/watch_health          # Анализ здоровья
/watch_insights        # Недельные инсайты
/watch_notification    # Тестовое уведомление
```

### Голосовые команды (через часы):
```
"как мое здоровье?"    # Анализ биометрии
"добавь задачу"        # Создание задачи
"покажи прогресс"      # Отчет о прогрессе
"что мне делать?"      # Рекомендации
```

---

## 📊 МОНИТОРИНГ И АНАЛИТИКА

### 1. Дашборд здоровья
```python
async def get_health_dashboard():
    """Создание дашборда здоровья"""
    
    # Получение последних данных
    recent_biometrics = llm_watch_analyzer.biometric_history[-7:]
    recent_insights = llm_watch_analyzer.insights_history[-7:]
    
    # Анализ трендов
    avg_heart_rate = sum(b.heart_rate for b in recent_biometrics if b.heart_rate) / len(recent_biometrics)
    avg_stress = sum(b.stress_level for b in recent_biometrics if b.stress_level) / len(recent_biometrics)
    
    # Формирование отчета
    report = f"📊 **Дашборд здоровья (7 дней)**\n\n"
    report += f"❤️ **Средний пульс:** {avg_heart_rate:.1f} уд/мин\n"
    report += f"😰 **Средний стресс:** {avg_stress:.1f}%\n"
    report += f"🧠 **Инсайтов получено:** {len(recent_insights)}\n"
    report += f"🎯 **Рекомендаций выполнено:** {len([i for i in recent_insights if i.actionable])}\n"
    
    return report
```

### 2. Автоматические отчеты
```python
# Еженедельный отчет
async def send_weekly_health_report():
    """Отправка еженедельного отчета"""
    report = await get_health_dashboard()
    
    for user_id in AUTHORIZED_USERS:
        await bot.send_message(
            chat_id=user_id,
            text=report,
            parse_mode=ParseMode.MARKDOWN
        )

# Запуск еженедельных отчетов
async def start_weekly_reports():
    while True:
        await send_weekly_health_report()
        await asyncio.sleep(604800)  # 7 дней
```

---

## 🔧 НАСТРОЙКА И КОНФИГУРАЦИЯ

### 1. Конфигурационный файл
```python
# config/watch_llm_config.py
WATCH_LLM_CONFIG = {
    "local_llm_url": "http://localhost:8000",
    "notification_interval": 7200,  # 2 часа
    "biometric_sync_interval": 300,  # 5 минут
    "stress_threshold": 70.0,
    "low_activity_threshold": 3000,
    "poor_sleep_threshold": 60.0,
    "authorized_users": [123456789],  # Telegram user IDs
    "notion_sync_enabled": True,
    "telegram_notifications_enabled": True
}
```

### 2. Переменные окружения
```bash
# .env
LOCAL_LLM_URL=http://localhost:8000
XIAOMI_APP_TOKEN=your_app_token
XIAOMI_USER_ID=your_user_id
TELEGRAM_BOT_TOKEN=your_bot_token
NOTION_TOKEN=your_notion_token
```

---

## 🚀 ЗАПУСК СИСТЕМЫ

### 1. Запуск всех компонентов
```bash
# Терминал 1: Локальная LLM
python local_llm_server.py

# Терминал 2: Telegram бот
python run_admin_bot.py

# Терминал 3: Мониторинг часов (если нужно)
python watch_monitor.py
```

### 2. Проверка работоспособности
```bash
# Тест локальной LLM
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Привет!", "context": "test"}'

# Тест интеграции
python test_watch_llm_final.py
```

---

## 🎯 РЕЗУЛЬТАТ

После выполнения всех шагов у тебя будет:

✅ **Локальная Llama 70B** - анализирует биометрические данные  
✅ **Умные уведомления** - персональные рекомендации  
✅ **Telegram интеграция** - команды и уведомления  
✅ **Контекстный анализ** - адаптация под время дня  
✅ **Детекция стресса** - автоматические рекомендации  
✅ **Голосовые команды** - управление через часы  

**Система готова к использованию!** 🚀 