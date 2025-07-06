# Итеративная Валидация и Улучшение 3D Моделей

## Обзор

Система итеративной валидации позволяет автоматически создавать и улучшать 3D модели с оценкой качества на каждом этапе. Это обеспечивает высокое качество финальных моделей без необходимости ручного вмешательства.

## Архитектура

### Компоненты

1. **BlenderValidator** - Валидация STL файлов и оценка качества
2. **IterativeImprover** - Итеративное улучшение моделей
3. **QualityReporter** - Генерация отчетов о качестве
4. **BlenderEngine** - Создание моделей с валидацией

### Процесс работы

```
1. Создание начальной модели
   ↓
2. Валидация качества
   ↓
3. Анализ проблем
   ↓
4. Применение улучшений
   ↓
5. Повтор до достижения цели
   ↓
6. Генерация отчета
```

## Использование

### Python API

```python
from src.integrations.blender_engine import BlenderEngine, ObjectSpec, ObjectType
from src.integrations.blender_validator import BlenderValidator, IterativeImprover

# Инициализация
engine = BlenderEngine()
validator = BlenderValidator()
improver = IterativeImprover(engine, validator)

# Создание спецификации
spec = ObjectSpec(
    name="test_cube",
    object_type=ObjectType.CUBE,
    dimensions=Vector3(2, 2, 2)
)

# Итеративное создание с валидацией
results = await improver.improve_model(spec, target_metrics={"face_count": 50})

# Анализ результатов
for result in results:
    print(f"Iteration {result.iteration}: Score = {result.validation.score}")
```

### CLI Команды

#### Итеративное создание объекта

```bash
# Создать куб с итеративной валидацией
python -m src.integrations.blender_cli_integration iterative cube test_cube --target-score 85 --max-iterations 3

# Создать цилиндр с позиционированием
python -m src.integrations.blender_cli_integration iterative cylinder test_cylinder --position 1 2 3 --material metal

# Создать Nike логотип
python -m src.integrations.blender_cli_integration iterative nike_logo test_nike --target-score 90
```

#### Валидация существующих файлов

```bash
# Валидировать STL файл
python -m src.integrations.blender_cli_integration validate output/blender/test.stl

# Валидировать с сохранением отчета
python -m src.integrations.blender_cli_integration validate output/blender/test.stl --output-report validation_report.md
```

## Метрики качества

### Основные метрики

- **vertex_count** - Количество вершин
- **face_count** - Количество граней
- **edge_count** - Количество ребер
- **volume** - Объем модели
- **surface_area** - Площадь поверхности
- **bounding_box** - Размеры ограничивающего бокса

### Критерии валидации

- **Минимальный score**: 70/100
- **Наличие граней**: > 0
- **Наличие вершин**: > 0
- **Отсутствие non-manifold ребер**
- **Отсутствие перекрывающихся граней**

### Система оценки (0-100)

```
Базовый score: 100
- Отсутствие граней: -50
- Отсутствие вершин: -50
- Non-manifold ребра: -2 за каждое (макс -20)
- Перекрывающиеся грани: -1.5 за каждую (макс -15)
- Бонус за хорошую геометрию: +10
```

## Автоматические улучшения

### Типы улучшений

1. **Исправление non-manifold геометрии**
2. **Удаление перекрывающихся граней**
3. **Увеличение плотности сетки**
4. **Обеспечение правильного создания геометрии**

### Применение улучшений

```python
# Генерация предложений по улучшению
improvements = improver._generate_improvements(validation_result, target_metrics)

# Применение улучшений к спецификации
updated_spec = improver._apply_improvements(original_spec, improvements)
```

## Отчеты о качестве

### Структура отчета

```markdown
# 3D Model Quality Report

## Summary
- Total Iterations: 3
- Final Score: 85/100
- Status: ✅ PASS
- Total Time: 12.34s

## Iteration Details
### Iteration 1
- Score: 75/100
- Time: 4.12s
- Issues: 1
- Improvements: 2

### Iteration 2
- Score: 82/100
- Time: 4.05s
- Issues: 0
- Improvements: 1

### Iteration 3
- Score: 85/100
- Time: 4.17s
- Issues: 0
- Improvements: 0

## Recommendations
- Model meets quality standards

## Metrics Comparison
- vertex_count: 24.00 → 24.00 (+0.00)
- face_count: 12.00 → 12.00 (+0.00)
```

### Сохранение отчетов

Отчеты автоматически сохраняются в:
- `output/quality_reports/{model_name}_quality_report.md`
- `validation_report.md` (при использовании CLI)

## Конфигурация

### Настройки итераций

```python
improver.max_iterations = 5      # Максимум итераций
improver.min_score = 80.0        # Минимальный score для успеха
```

### Целевые метрики

```python
target_metrics = {
    "face_count": 50,           # Минимум граней
    "vertex_count": 100,        # Минимум вершин
    "volume": 1.0,              # Минимальный объем
    "surface_area": 2.0         # Минимальная площадь
}
```

## Интеграция с агентами

### Для оператора агента

```python
# Создание модели с валидацией
final_path, validation_history = await engine.create_object_with_validation(
    spec, target_score=85.0, max_iterations=5
)

# Проверка готовности для оператора
if validation_history[-1]["score"] >= 85.0:
    print("✅ Модель готова для оценки оператором")
    print(f"📁 Файл: {final_path}")
    print(f"📊 Score: {validation_history[-1]['score']}/100")
else:
    print("❌ Модель требует доработки")
    print(f"📊 Текущий score: {validation_history[-1]['score']}/100")
```

### Автоматическое принятие решений

```python
# Автоматическое принятие при высоком качестве
if validation_history[-1]["score"] >= 95.0:
    print("🚀 Модель автоматически одобрена")
    return final_path

# Запрос оценки оператора при среднем качестве
elif validation_history[-1]["score"] >= 80.0:
    print("👤 Требуется оценка оператора")
    # Здесь можно интегрировать с Telegram ботом
    return final_path

# Повторная попытка при низком качестве
else:
    print("🔄 Требуется повторная попытка")
    return None
```

## Тестирование

### Запуск тестов

```bash
python scripts/test_iterative_creation.py
```

### Тестовые сценарии

1. **Итеративное создание куба**
2. **Валидация Nike логотипа**
3. **Проверка CLI команд**
4. **Генерация отчетов**

## Устранение неполадок

### Частые проблемы

1. **Blender не найден**
   - Проверьте путь в `_find_blender()`
   - Установите Blender в стандартную директорию

2. **Ошибки валидации**
   - Проверьте права доступа к файлам
   - Убедитесь в корректности STL файла

3. **Низкий score качества**
   - Увеличьте количество итераций
   - Настройте целевые метрики
   - Проверьте спецификацию объекта

### Логирование

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Расширение функциональности

### Добавление новых метрик

```python
# В BlenderValidator._generate_validation_script()
metrics["new_metric"] = calculate_new_metric(bm)
```

### Новые типы улучшений

```python
# В IterativeImprover._generate_improvements()
if "specific_issue" in issue.lower():
    improvements.append("Specific improvement action")
```

### Кастомные критерии валидации

```python
# В BlenderValidator
def custom_validation_criteria(self, mesh_data):
    # Ваша логика валидации
    pass
``` 