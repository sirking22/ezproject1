# Управление переменными окружения

## 1. Проблема 🤔

В нашем проекте есть несколько проблем с управлением переменными окружения:

1. **Разбросанность**: Переменные используются в разных местах кода напрямую
2. **Отсутствие валидации**: Нет проверки наличия всех необходимых переменных
3. **Нет типизации**: Значения берутся как строки, без преобразования в нужный тип
4. **Сложность тестирования**: Тяжело подменять значения при тестировании

## 2. Решение 💡

### 2.1. Централизованное управление

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    """
    Централизованное управление настройками приложения.
    Автоматически загружает значения из .env файла.
    """
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    ADMIN_USER_IDS: List[int]
    
    # Notion
    NOTION_TOKEN: str
    NOTION_MATERIALS_DB_ID: str
    NOTION_IDEAS_DB_ID: str
    
    # Yandex Disk
    YA_ACCESS_TOKEN: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def validate(self) -> bool:
        """Проверка валидности всех настроек"""
        return all([
            self.validate_telegram_token(),
            self.validate_notion_token(),
            self.validate_yandex_token(),
            self.validate_database_ids()
        ])
```

### 2.2. Использование в коде

```python
# Плохо ❌
import os
token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_TASKS_DB_ID")

# Хорошо ✅
from config.settings import settings
token = settings.NOTION_TOKEN
db_id = settings.NOTION_MATERIALS_DB_ID
```

### 2.3. Пример .env файла

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_IDS=123456789,987654321

# Notion
NOTION_TOKEN=your_notion_token
NOTION_MATERIALS_DB_ID=your_materials_db_id
NOTION_IDEAS_DB_ID=your_ideas_db_id

# Yandex Disk
YA_ACCESS_TOKEN=your_yandex_token
```

## 3. Преимущества 🌟

1. **Безопасность**:
   - Централизованная проверка наличия всех переменных
   - Валидация значений при запуске
   - Типизация предотвращает ошибки

2. **Удобство**:
   - Все настройки в одном месте
   - Автоподсказки в IDE
   - Документация рядом с кодом

3. **Тестируемость**:
   - Легко подменять значения в тестах
   - Моки и фикстуры
   - Изоляция тестов

## 4. Использование 📝

### 4.1. Добавление новой переменной

1. Добавить в класс Settings:
```python
NEW_VARIABLE: str
```

2. Добавить в .env:
```env
NEW_VARIABLE=value
```

3. Использовать в коде:
```python
value = settings.NEW_VARIABLE
```

### 4.2. Валидация

```python
def validate_notion_token(self) -> bool:
    """Проверка валидности токена Notion"""
    try:
        # Пробуем выполнить тестовый запрос
        client = Client(auth=self.NOTION_TOKEN)
        client.users.me()
        return True
    except Exception as e:
        logger.error(f"Invalid Notion token: {e}")
        return False
```

### 4.3. Тестирование

```python
def test_with_custom_settings():
    test_settings = Settings(
        NOTION_TOKEN="test_token",
        NOTION_MATERIALS_DB_ID="test_id"
    )
    assert test_settings.validate()
```

## 5. Безопасность 🔒

1. **Не коммитить .env**:
   - Добавить в .gitignore
   - Использовать .env.example как шаблон

2. **Разные окружения**:
   - .env.development
   - .env.testing
   - .env.production

3. **Шифрование**:
   - Использовать системы управления секретами
   - Шифровать чувствительные данные
   - Регулярно обновлять токены

## 6. Чек-лист 📋

При работе с переменными окружения:

- [ ] Все переменные описаны в Settings
- [ ] Есть валидация значений
- [ ] Есть типизация
- [ ] Есть документация
- [ ] Настроено тестирование
- [ ] Обеспечена безопасность

## 7. Частые ошибки и решения 🐛

### 7.1. Переменная не загружается
**Проблема:** `Telegram=False` в логах
**Решение:**
1. Проверить наличие .env файла
2. Добавить `from dotenv import load_dotenv; load_dotenv()`
3. Проверить переменные: `echo $env:TELEGRAM_BOT_TOKEN`

### 7.2. Неправильные имена переменных
**Проблема:** `TELEGRAM_TOKEN` vs `TELEGRAM_BOT_TOKEN`
**Решение:** Использовать единообразные имена во всех файлах

### 7.3. Отсутствие валидации
**Проблема:** Бот падает при отсутствии токенов
**Решение:** Добавить проверку в начале приложения

## 8. Best Practices ⭐

### 8.1. Структура .env файла
```env
# =============================================================================
# TELEGRAM CONFIGURATION
# =============================================================================
TELEGRAM_BOT_TOKEN=your_bot_token

# =============================================================================
# NOTION CONFIGURATION
# =============================================================================
NOTION_TOKEN=your_notion_token
NOTION_MATERIALS_DB_ID=your_materials_db_id
NOTION_IDEAS_DB_ID=your_ideas_db_id

# =============================================================================
# YANDEX DISK CONFIGURATION
# =============================================================================
YA_ACCESS_TOKEN=your_yandex_token
```

### 8.2. Проверка при запуске
```python
def check_environment():
    """Проверка всех необходимых переменных"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'NOTION_TOKEN',
        'YA_ACCESS_TOKEN',
        'NOTION_MATERIALS_DB_ID',
        'NOTION_IDEAS_DB_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
    
    logger.info("✅ All environment variables loaded successfully")
```

### 8.3. Логирование (безопасно)
```python
def log_environment_status():
    """Логирует статус переменных без показа значений"""
    vars_status = {
        'TELEGRAM_BOT_TOKEN': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
        'NOTION_TOKEN': bool(os.getenv('NOTION_TOKEN')),
        'YA_ACCESS_TOKEN': bool(os.getenv('YA_ACCESS_TOKEN')),
        'NOTION_MATERIALS_DB_ID': bool(os.getenv('NOTION_MATERIALS_DB_ID')),
        'NOTION_IDEAS_DB_ID': bool(os.getenv('NOTION_IDEAS_DB_ID'))
    }
    
    logger.info(f"Environment variables status: {vars_status}")
```

## 9. Автоматизация 🔧

### 9.1. Скрипт проверки
```python
# daily_setup.py
def check_env_vars():
    """Проверяет критические переменные окружения"""
    critical_vars = ['TELEGRAM_BOT_TOKEN', 'NOTION_TOKEN', 'YA_ACCESS_TOKEN']
    missing = []
    
    for var in critical_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return missing
```

### 9.2. Автоматическая загрузка
```python
# В начале каждого файла бота
from dotenv import load_dotenv
load_dotenv()

# Проверка переменных
check_environment()
``` 