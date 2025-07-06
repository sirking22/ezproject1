"""
Конфигурация сервера Quick Voice Assistant
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройки сервера
SERVER_CONFIG = {
    "host": os.getenv("SERVER_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVER_PORT", 8000)),
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "reload": os.getenv("RELOAD", "False").lower() == "true"
}

# Настройки LLM (если используешь локальную модель)
LLM_CONFIG = {
    "model_path": os.getenv("LLM_MODEL_PATH", ""),
    "model_type": os.getenv("LLM_MODEL_TYPE", "llama"),
    "context_length": int(os.getenv("LLM_CONTEXT_LENGTH", 4096)),
    "temperature": float(os.getenv("LLM_TEMPERATURE", 0.7)),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", 512)),
    "use_local": os.getenv("USE_LOCAL_LLM", "False").lower() == "true",
    "fallback_to_openai": os.getenv("FALLBACK_TO_OPENAI", "True").lower() == "true"
}

# Настройки Notion
NOTION_CONFIG = {
    "token": os.getenv("NOTION_TOKEN", ""),
    "databases": {
        "tasks": os.getenv("NOTION_TASKS_DB", ""),
        "reflections": os.getenv("NOTION_REFLECTIONS_DB", ""),
        "habits": os.getenv("NOTION_HABITS_DB", ""),
        "ideas": os.getenv("NOTION_IDEAS_DB", ""),
        "materials": os.getenv("NOTION_MATERIALS_DB", "")
    },
    "enabled": os.getenv("NOTION_ENABLED", "True").lower() == "true"
}

# Настройки Telegram
TELEGRAM_CONFIG = {
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "enabled": os.getenv("TELEGRAM_ENABLED", "True").lower() == "true"
}

# Настройки голосовой обработки
VOICE_CONFIG = {
    "sample_rate": int(os.getenv("VOICE_SAMPLE_RATE", 16000)),
    "chunk_size": int(os.getenv("VOICE_CHUNK_SIZE", 1024)),
    "max_duration": int(os.getenv("VOICE_MAX_DURATION", 30)),
    "language": os.getenv("VOICE_LANGUAGE", "ru"),
    "model": os.getenv("VOICE_MODEL", "whisper")
}

# Настройки производительности
PERFORMANCE_CONFIG = {
    "max_workers": int(os.getenv("MAX_WORKERS", 4)),
    "timeout": int(os.getenv("REQUEST_TIMEOUT", 30)),
    "cache_size": int(os.getenv("CACHE_SIZE", 1000)),
    "enable_compression": os.getenv("ENABLE_COMPRESSION", "True").lower() == "true",
    "enable_caching": os.getenv("ENABLE_CACHING", "True").lower() == "true"
}

# Настройки безопасности
SECURITY_CONFIG = {
    "allowed_hosts": os.getenv("ALLOWED_HOSTS", "192.168.1.0/24").split(","),
    "rate_limit": int(os.getenv("RATE_LIMIT", 100)),
    "enable_logging": os.getenv("ENABLE_LOGGING", "True").lower() == "true",
    "api_key": os.getenv("API_KEY", "")
}

# Настройки мониторинга
MONITORING_CONFIG = {
    "enable_metrics": os.getenv("ENABLE_METRICS", "True").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "save_logs": os.getenv("SAVE_LOGS", "True").lower() == "true",
    "log_file": os.getenv("LOG_FILE", "logs/server.log")
}

# Настройки кэширования
CACHE_CONFIG = {
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "ttl": int(os.getenv("CACHE_TTL", 3600)),
    "max_size": int(os.getenv("CACHE_MAX_SIZE", 1000))
}

# Команды для обработки
VOICE_COMMANDS = {
    "add_task": {
        "patterns": ["добавь задачу", "создай задачу", "задача"],
        "action": "create_task",
        "database": "tasks"
    },
    "save_thought": {
        "patterns": ["запиши мысль", "сохрани идею", "мысль"],
        "action": "save_reflection",
        "database": "reflections"
    },
    "create_habit": {
        "patterns": ["создай привычку", "новая привычка", "привычка"],
        "action": "create_habit",
        "database": "habits"
    },
    "show_progress": {
        "patterns": ["покажи прогресс", "статистика", "прогресс"],
        "action": "get_progress",
        "database": "all"
    },
    "health_check": {
        "patterns": ["как мое здоровье", "здоровье", "состояние"],
        "action": "health_analysis",
        "database": "biometrics"
    },
    "sync_data": {
        "patterns": ["синхронизируй", "синхронизация", "обнови"],
        "action": "sync_all",
        "database": "all"
    }
}

# Ответы по умолчанию
DEFAULT_RESPONSES = {
    "add_task": "Задача '{task}' добавлена в ваш список. Рекомендую выполнить в ближайшее время.",
    "save_thought": "Мысль '{thought}' сохранена. Рекомендую вернуться к ней позже.",
    "create_habit": "Привычка '{habit}' создана. Рекомендую начать с малого.",
    "show_progress": "Ваш прогресс: {progress}. Отличные результаты!",
    "health_check": "Ваше здоровье в отличном состоянии! {details}",
    "sync_data": "Данные синхронизированы. Все изменения сохранены.",
    "unknown": "Команда обработана. Что еще могу помочь?"
}

# Настройки логирования
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/server.log",
            "formatter": "default",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
}

def get_config() -> Dict[str, Any]:
    """Возвращает полную конфигурацию"""
    return {
        "server": SERVER_CONFIG,
        "llm": LLM_CONFIG,
        "notion": NOTION_CONFIG,
        "telegram": TELEGRAM_CONFIG,
        "voice": VOICE_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "security": SECURITY_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "cache": CACHE_CONFIG,
        "commands": VOICE_COMMANDS,
        "responses": DEFAULT_RESPONSES,
        "logging": LOGGING_CONFIG
    }

def validate_config() -> bool:
    """Проверяет корректность конфигурации"""
    errors = []
    
    # Проверка обязательных параметров
    if not NOTION_CONFIG["token"] and NOTION_CONFIG["enabled"]:
        errors.append("NOTION_TOKEN не установлен")
    
    if not TELEGRAM_CONFIG["bot_token"] and TELEGRAM_CONFIG["enabled"]:
        errors.append("TELEGRAM_BOT_TOKEN не установлен")
    
    if not LLM_CONFIG["model_path"] and LLM_CONFIG["use_local"]:
        errors.append("LLM_MODEL_PATH не установлен для локальной модели")
    
    if errors:
        print("❌ Ошибки конфигурации:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

if __name__ == "__main__":
    # Тестирование конфигурации
    print("🔧 Конфигурация сервера:")
    config = get_config()
    
    for section, settings in config.items():
        if isinstance(settings, dict):
            print(f"\n{section.upper()}:")
            for key, value in settings.items():
                if isinstance(value, dict):
                    print(f"  {key}: {len(value)} элементов")
                else:
                    print(f"  {key}: {value}")
    
    print(f"\n✅ Конфигурация валидна: {validate_config()}") 