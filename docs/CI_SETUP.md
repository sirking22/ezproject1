# 🚀 CI/CD Setup - Notion-Telegram-LLM Integration

## 📋 Что делает CI

### Schema Validation Pipeline
- **Автоматическая проверка** схем баз данных при каждом коммите
- **Валидация консистентности** — проверка дубликатов ID, обязательных полей
- **Генерация документации** — автообновление notion_schemas_documentation.json
- **Уведомления об ошибках** — если схема сломана, CI не пропустит коммит

### Code Quality Pipeline
- **Форматирование кода** — проверка black форматирования
- **Линтинг** — flake8 для стиля и ошибок
- **Проверка типов** — mypy для type hints
- **Тесты** — автоматический запуск pytest
- **TODO/FIXME** — поиск незавершённых задач

## 🔧 Настройка

### 1. GitHub Actions
CI уже настроен в `.github/workflows/`:
- `schema-validation.yml` — проверка схем
- `code-quality.yml` — качество кода

### 2. Локальная проверка
```bash
# Установка зависимостей
pip install -r requirements.txt

# Проверка схем
python test_schemas_integration.py

# Форматирование кода
black .

# Линтинг
flake8 .

# Проверка типов
mypy notion_database_schemas.py
```

### 3. Pre-commit hooks (опционально)
```bash
# Установка pre-commit
pip install pre-commit

# Создание .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Установка hooks
pre-commit install
```

## 📊 Что проверяется

### Schema Validation
- ✅ Все схемы загружаются без ошибок
- ✅ ID баз данных уникальны
- ✅ Обязательные поля заполнены
- ✅ Валидация значений работает
- ✅ Связи между базами корректны
- ✅ Документация генерируется

### Code Quality
- ✅ Код отформатирован black
- ✅ Нет критических ошибок flake8
- ✅ Type hints корректны
- ✅ Тесты проходят
- ✅ Нет незавершённых TODO

## 🚨 При ошибках

### Schema Validation Failed
1. Проверь `notion_database_schemas.py` на синтаксис
2. Убедись, что все DatabaseSchema имеют все поля
3. Проверь уникальность database_id
4. Запусти локально: `python test_schemas_integration.py`

### Code Quality Failed
1. Запусти `black .` для форматирования
2. Исправь ошибки flake8
3. Добавь type hints где нужно
4. Исправь тесты

## 📈 Мониторинг

### GitHub Actions Dashboard
- Переходи в Actions → Schema Validation
- Смотри логи для деталей ошибок
- Скачивай артефакты (документацию)

### Локальные проверки
```bash
# Быстрая проверка схем
python -c "from notion_database_schemas import get_all_schemas; print('✅ Schemas OK')"

# Проверка конкретной схемы
python -c "from notion_database_schemas import get_database_schema; print(get_database_schema('tasks').name)"
```

## 🔄 Автоматизация

### При коммите в main/develop:
1. Запускается schema-validation.yml
2. Проверяется качество кода
3. Генерируется документация
4. Если ошибки — коммит отклоняется

### При PR:
1. Те же проверки
2. Дополнительно проверяется конфликт с main
3. Можно настроить авто-merge при успехе

## 🎯 Best Practices

### Для разработки:
- Всегда запускай тесты локально перед коммитом
- Используй pre-commit hooks
- Следи за качеством кода
- Обновляй документацию при изменении схем

### Для команды:
- Не коммить сломанные схемы
- Используй feature branches
- Пиши понятные commit messages
- Регулярно обновляй зависимости

## 📝 Настройка уведомлений

### Slack/Discord интеграция (опционально)
```yaml
# В .github/workflows/schema-validation.yml добавить:
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email уведомления
Настрой в GitHub Settings → Notifications → Email

## 🔧 Расширение CI

### Добавление новых проверок:
1. Создай новый job в .github/workflows/
2. Добавь зависимости в requirements.txt
3. Напиши тесты в tests/
4. Обнови документацию

### Интеграция с другими сервисами:
- **Docker** — для контейнеризации
- **AWS/GCP** — для деплоя
- **Slack** — для уведомлений
- **Jira** — для тикетов

---

**Результат:** Полная автоматизация проверки качества и актуальности схем баз данных Notion. 