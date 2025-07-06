# 🧠 Руководство по настройке локальной Llama 70B

## 🎯 Обзор

Это руководство поможет настроить локальную Llama 70B квантованную модель для персональной AI-экосистемы. Локальная модель обеспечивает:

- **Приватность** - все данные остаются на твоем компьютере
- **Персонализацию** - модель адаптируется под твои данные
- **Контекстность** - переключение между рабочим и домашним контекстами
- **Независимость** - работа без интернета

---

## 🖥️ Системные требования

### Минимальные требования:
- **RAM**: 16 GB (для 4-bit квантования)
- **GPU**: NVIDIA GPU с 8GB VRAM (опционально, но рекомендуется)
- **CPU**: 8+ ядер
- **Диск**: 50 GB свободного места

### Рекомендуемые требования:
- **RAM**: 32 GB
- **GPU**: NVIDIA RTX 4090 или аналогичная
- **CPU**: 16+ ядер
- **Диск**: 100 GB SSD

---

## 📦 Установка

### 1. Установка llama-cpp-python

```bash
# Базовая установка
pip install llama-cpp-python

# С поддержкой CUDA (если есть NVIDIA GPU)
pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu118

# С поддержкой Metal (для Mac с Apple Silicon)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### 2. Скачивание модели

```bash
# Создаем директорию для моделей
mkdir -p models
cd models

# Скачиваем Llama 70B квантованную (4-bit)
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q4_K_M.gguf

# Альтернативно, для более быстрой работы (7B модель)
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
```

### 3. Установка дополнительных зависимостей

```bash
pip install fastapi uvicorn aiohttp
```

---

## ⚙️ Настройка

### 1. Создание конфигурационного файла

Создай файл `llm_config.json`:

```json
{
  "models": {
    "fast": {
      "path": "models/llama-2-7b-chat.Q4_K_M.gguf",
      "n_ctx": 4096,
      "n_threads": 8,
      "n_gpu_layers": 0
    },
    "default": {
      "path": "models/llama-2-70b-chat.Q4_K_M.gguf", 
      "n_ctx": 4096,
      "n_threads": 12,
      "n_gpu_layers": 0
    },
    "advanced": {
      "path": "models/llama-2-70b-chat.Q4_K_M.gguf",
      "n_ctx": 8192,
      "n_threads": 16,
      "n_gpu_layers": 0
    }
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "max_concurrent_requests": 5
  }
}
```

### 2. Настройка переменных окружения

Добавь в `.env`:

```env
# LLM настройки
LLM_USE_LOCAL=true
LLM_LOCAL_URL=http://localhost:8000
LLM_FALLBACK_TO_OPENROUTER=true

# OpenRouter (как fallback)
OPENROUTER_API_KEY=your_openrouter_key
```

---

## 🚀 Запуск

### 1. Запуск LLM сервера

```bash
# Запуск локального LLM сервера
python src/llm/local_server.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

### 2. Тестирование сервера

```bash
# Тест здоровья сервера
curl http://localhost:8000/health

# Тест генерации
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет! Как дела?",
    "context": "home",
    "model_type": "default"
  }'
```

### 3. Запуск расширенного бота

```bash
# Запуск бота с локальной LLM
python run_enhanced_bot.py
```

---

## 🧪 Тестирование

### 1. Базовые тесты

```bash
# Тест интеграции
python test_local_llm_integration.py
```

### 2. Тест производительности

```python
import asyncio
import time
from src.llm.client import LocalLLMClient

async def test_performance():
    async with LocalLLMClient() as client:
        start_time = time.time()
        
        response = await client.generate(
            prompt="Напиши эссе о важности личного развития",
            context="home"
        )
        
        end_time = time.time()
        print(f"Время генерации: {end_time - start_time:.2f} секунд")
        print(f"Длина ответа: {len(response.text)} символов")
        print(f"Токены: {response.tokens}")

asyncio.run(test_performance())
```

---

## 🔧 Оптимизация

### 1. Оптимизация для CPU

```python
# В llm_config.json
{
  "models": {
    "default": {
      "n_threads": 16,  # Количество CPU ядер
      "n_batch": 512,   # Размер батча
      "n_ctx": 2048     # Уменьшенный контекст
    }
  }
}
```

### 2. Оптимизация для GPU

```python
# В llm_config.json
{
  "models": {
    "default": {
      "n_gpu_layers": 35,  # Количество слоев на GPU
      "n_batch": 1024,     # Увеличенный батч
      "n_ctx": 4096        # Полный контекст
    }
  }
}
```

### 3. Мониторинг ресурсов

```bash
# Мониторинг использования памяти
htop

# Мониторинг GPU (если используется)
nvidia-smi
```

---

## 🎯 Контекстное переключение

### 1. Рабочий контекст

```python
# Переключение на рабочий контекст
await client.set_session_context("session_123", "work")

response = await client.generate(
    prompt="Планирование проекта",
    context="work"
)
```

### 2. Домашний контекст

```python
# Переключение на домашний контекст
await client.set_session_context("session_123", "home")

response = await client.generate(
    prompt="Личное развитие",
    context="home"
)
```

### 3. Общий контекст

```python
# Общий контекст для универсальных задач
response = await client.generate(
    prompt="Общие советы",
    context="general"
)
```

---

## 🔍 Устранение неполадок

### 1. Проблемы с памятью

**Симптомы**: Ошибки "Out of memory"

**Решения**:
```python
# Уменьшить размер модели
"n_ctx": 1024,  # Вместо 4096
"n_batch": 256, # Вместо 512

# Использовать более агрессивное квантование
# Скачать Q2_K вместо Q4_K_M
```

### 2. Медленная генерация

**Симптомы**: Долгое время ответа

**Решения**:
```python
# Увеличить количество потоков
"n_threads": 16,  # Вместо 8

# Использовать GPU
"n_gpu_layers": 35,

# Уменьшить контекст
"n_ctx": 2048,  # Вместо 4096
```

### 3. Ошибки загрузки модели

**Симптомы**: "Model not found"

**Решения**:
```bash
# Проверить путь к модели
ls -la models/

# Перескачать модель
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q4_K_M.gguf
```

---

## 📊 Мониторинг и логирование

### 1. Настройка логирования

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_server.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Метрики производительности

```python
# В LLM сервисе
async def log_metrics(self, response: LLMResponse):
    logger.info(f"Generation metrics: {response.processing_time:.2f}s, "
                f"{response.tokens} tokens, confidence: {response.confidence:.2f}")
```

---

## 🔮 Следующие шаги

### 1. Fine-tuning

После настройки базовой модели:

1. **Сбор данных**: Экспорт из Notion
2. **Подготовка датасета**: Форматирование для обучения
3. **LoRA адаптеры**: Эффективное дообучение
4. **Валидация**: Проверка качества

### 2. Семантический поиск

1. **Векторизация**: Создание эмбеддингов
2. **Векторная база**: ChromaDB или FAISS
3. **Поиск**: RAG (Retrieval-Augmented Generation)

### 3. Автоматизация

1. **Ежедневные отчеты**: Автоматическая аналитика
2. **Умные напоминания**: Контекстные уведомления
3. **Автоматические действия**: Триггеры и реакции

---

## 📚 Полезные ссылки

- [llama-cpp-python документация](https://github.com/abetlen/llama-cpp-python)
- [GGUF модели на Hugging Face](https://huggingface.co/TheBloke)
- [Llama 2 модель](https://huggingface.co/meta-llama/Llama-2-70b-chat-hf)
- [Квантование моделей](https://github.com/ggerganov/llama.cpp)

---

## 🎯 Чек-лист настройки

- [ ] Установлен llama-cpp-python
- [ ] Скачана модель Llama 70B
- [ ] Настроен конфигурационный файл
- [ ] Запущен LLM сервер
- [ ] Протестирована генерация
- [ ] Настроено контекстное переключение
- [ ] Интегрирован с Telegram ботом
- [ ] Протестирована полная система

---

*Этот гайд поможет настроить локальную LLM для максимальной пользы в твоей персональной AI-экосистеме!* 