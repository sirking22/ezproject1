# Руководство по универсальному репозиторию Notion

## Обзор

Универсальный репозиторий (`UniversalNotionRepository`) предоставляет единый интерфейс для работы со всеми 7 таблицами Notion:
- **rituals** - Ритуалы
- **habits** - Привычки  
- **reflections** - Размышления
- **guides** - Руководства
- **actions** - Действия/задачи
- **terms** - Термины
- **materials** - Материалы

## Основные возможности

### 1. CRUD операции
- **Create** - создание элементов
- **Read** - чтение элементов (по ID, список, поиск)
- **Update** - обновление элементов
- **Delete** - удаление элементов (архивирование)

### 2. Валидация
- Проверка структуры баз данных
- Валидация схемы свойств
- Обработка ошибок

### 3. Фильтрация и поиск
- Фильтрация по статусу, категории, тегам
- Полнотекстовый поиск
- Сортировка результатов

## Использование в коде

### Инициализация
```python
from src.core.config import Settings
from src.notion.universal_repository import UniversalNotionRepository

settings = Settings()
repo = UniversalNotionRepository(settings)
```

### Создание элементов
```python
# Создание ритуала
ritual_data = {
    'title': 'Утренняя медитация',
    'status': 'Active',
    'category': 'Health',
    'frequency': 'Daily',
    'description': 'Медитация каждое утро',
    'tags': ['health', 'meditation'],
    'created_date': datetime.now(UTC),
    'priority': 'High'
}

created_ritual = await repo.create_ritual(ritual_data)
```

### Получение элементов
```python
# Получение по ID
item = await repo.get_item('rituals', item_id)

# Список элементов
rituals = await repo.get_rituals()

# Список с фильтрацией
active_rituals = await repo.get_rituals({'status': 'Active'})

# Поиск
results = await repo.search_items('rituals', 'медитация')
```

### Обновление элементов
```python
update_data = {
    'description': 'Новое описание',
    'priority': 'Medium'
}

updated_item = await repo.update_item('rituals', item_id, update_data)
```

### Удаление элементов
```python
deleted = await repo.delete_item('rituals', item_id)
```

## Команды Telegram бота

### Проверка структуры
```
/validate all          # Проверка всех таблиц
/validate rituals      # Проверка конкретной таблицы
```

### Работа с данными
```
/list rituals 10       # Список 10 ритуалов
/create habits "Новая привычка" "Описание привычки"
/get rituals [ID]      # Получение элемента по ID
/search guides "продуктивность"  # Поиск
/update rituals [ID] description "Новое описание"
/delete rituals [ID]   # Удаление элемента
```

## Схемы таблиц

### Rituals (Ритуалы)
- `title` - Название
- `status` - Статус (Active/Inactive)
- `category` - Категория
- `frequency` - Частота
- `description` - Описание
- `tags` - Теги
- `created_date` - Дата создания
- `last_performed` - Последнее выполнение
- `streak` - Серия выполнений
- `priority` - Приоритет

### Habits (Привычки)
- `title` - Название
- `status` - Статус
- `category` - Категория
- `frequency` - Частота
- `description` - Описание
- `tags` - Теги
- `created_date` - Дата создания
- `last_performed` - Последнее выполнение
- `streak` - Серия выполнений
- `target_frequency` - Целевая частота
- `current_frequency` - Текущая частота

### Reflections (Размышления)
- `title` - Название
- `type` - Тип
- `mood` - Настроение
- `content` - Содержание
- `tags` - Теги
- `created_date` - Дата создания
- `related_activities` - Связанные активности
- `insights` - Инсайты
- `action_items` - Пункты действий

### Guides (Руководства)
- `title` - Название
- `category` - Категория
- `difficulty` - Сложность
- `content` - Содержание
- `tags` - Теги
- `created_date` - Дата создания
- `last_updated` - Последнее обновление
- `author` - Автор
- `status` - Статус
- `url` - Ссылка

### Actions (Действия)
- `title` - Название
- `status` - Статус
- `priority` - Приоритет
- `category` - Категория
- `description` - Описание
- `tags` - Теги
- `due_date` - Срок выполнения
- `created_date` - Дата создания
- `assigned_to` - Назначено
- `estimated_time` - Оценка времени
- `actual_time` - Фактическое время

### Terms (Термины)
- `title` - Название
- `category` - Категория
- `definition` - Определение
- `examples` - Примеры
- `tags` - Теги
- `created_date` - Дата создания
- `last_reviewed` - Последний обзор
- `mastery_level` - Уровень освоения
- `related_terms` - Связанные термины

### Materials (Материалы)
- `title` - Название
- `type` - Тип
- `category` - Категория
- `description` - Описание
- `tags` - Теги
- `url` - Ссылка
- `created_date` - Дата создания
- `last_accessed` - Последний доступ
- `status` - Статус
- `rating` - Рейтинг
- `notes` - Заметки

## Алиасы для удобства

Репозиторий предоставляет алиасы для каждой таблицы:

```python
# Создание
await repo.create_ritual(data)
await repo.create_habit(data)
await repo.create_reflection(data)
await repo.create_guide(data)
await repo.create_action(data)
await repo.create_term(data)
await repo.create_material(data)

# Получение списка
await repo.get_rituals()
await repo.get_habits()
await repo.get_reflections()
await repo.get_guides()
await repo.get_actions()
await repo.get_terms()
await repo.get_materials()
```

## Обработка ошибок

Все методы репозитория обрабатывают ошибки и возвращают:
- `None` для операций создания/обновления при ошибке
- `False` для операций удаления при ошибке
- Пустой список для операций получения списка при ошибке

Логирование ошибок происходит автоматически.

## Тестирование

Для тестирования используйте:
```bash
python test_universal_repository.py
python test_integration.py
```

## Следующие шаги

1. Векторизация данных для семантического поиска
2. Интеграция с LLM для анализа
3. Автоматизация процессов
4. Мониторинг и аналитика 