# 🚀 Быстрый старт: Локальная Llama 70B

## ⚡ Установка за 15 минут

### 1. Установка зависимостей
```bash
# Основные пакеты
pip install llama-cpp-python fastapi uvicorn

# Для векторизации (опционально)
pip install sentence-transformers faiss-cpu

# Для работы с данными
pip install numpy pandas
```

### 2. Скачивание модели
```bash
# Создаем директорию
mkdir -p models

# Скачиваем квантованную Llama 70B (4-bit, ~40GB)
wget https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF/resolve/main/llama-2-70b-chat.Q4_K_M.gguf -O models/llama-2-70b-chat.Q4_K_M.gguf
```

### 3. Создание API сервера
```python
# src/llm/quick_server.py
from fastapi import FastAPI
from llama_cpp import Llama
from pydantic import BaseModel

app = FastAPI()
llm = Llama(
    model_path="models/llama-2-70b-chat.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8  # Настрой под свою систему
)

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/generate")
async def generate(request: GenerateRequest):
    response = llm(request.prompt, max_tokens=request.max_tokens)
    return {"response": response["choices"][0]["text"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 4. Запуск
```bash
# Запуск сервера
uvicorn src.llm.quick_server:app --host 0.0.0.0 --port 8000

# Тест
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Привет! Как дела?"}'
```

## 🔧 Настройка под твою систему

### Для мощной системы (32+ GB RAM, 16+ ядер):
```python
llm = Llama(
    model_path="models/llama-2-70b-chat.Q4_K_M.gguf",
    n_ctx=8192,
    n_threads=16,
    n_gpu_layers=35,  # Если есть GPU
    n_batch=512
)
```

### Для средней системы (16+ GB RAM, 8+ ядер):
```python
llm = Llama(
    model_path="models/llama-2-70b-chat.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0,
    n_batch=256
)
```

### Для слабой системы (8+ GB RAM, 4+ ядер):
```python
llm = Llama(
    model_path="models/llama-2-70b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,
    n_batch=128
)
```

## 🎯 Интеграция с существующей системой

### Замена OpenRouter на локальную LLM
```python
# В src/agents/agent_core.py
import aiohttp

class AgentCore:
    def __init__(self):
        self.local_llm_url = "http://localhost:8000"
    
    async def get_agent_response(self, role: str, context: str, user_input: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.local_llm_url}/generate",
                json={"prompt": user_input, "max_tokens": 512}
            ) as response:
                result = await response.json()
                return result["response"]
```

## 📊 Мониторинг производительности

### Проверка загрузки системы
```bash
# Мониторинг RAM
htop

# Мониторинг GPU (если используется)
nvidia-smi

# Проверка температуры CPU
sensors
```

### Оптимизация производительности
```python
# Настройки для разных сценариев
CONFIGS = {
    "fast": {"n_threads": 16, "n_ctx": 2048, "n_batch": 512},
    "balanced": {"n_threads": 8, "n_ctx": 4096, "n_batch": 256},
    "memory_safe": {"n_threads": 4, "n_ctx": 1024, "n_batch": 128}
}
```

## 🚀 Следующие шаги

1. **Протестируй базовую работу** - убедись, что модель отвечает
2. **Интегрируй с Telegram ботом** - замени OpenRouter
3. **Добавь контекстное управление** - рабочий/домашний режим
4. **Настрой векторизацию** - для семантического поиска

## ⚠️ Важные моменты

- **RAM**: Минимум 8GB, рекомендуется 16+ GB
- **CPU**: Минимум 4 ядра, рекомендуется 8+ ядер
- **Storage**: 50+ GB для модели и данных
- **GPU**: Опционально, но значительно ускоряет работу

## 🎉 Готово!

Теперь у тебя есть локальная Llama 70B, которая работает полностью на твоем компьютере. Никаких внешних API, полная приватность и контроль над данными. 