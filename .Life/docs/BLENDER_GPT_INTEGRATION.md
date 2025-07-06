# BlenderGPT Integration - Максимальная точность 3D генерации

## Обзор

BlenderGPT - это мощный инструмент, который использует LLM для управления Blender через естественный язык. Это решение превосходит нашу текущую систему валидации и предоставляет:

- ✅ **Полный доступ к API Blender**
- ✅ **Естественный язык для команд**
- ✅ **Автоматическая валидация и исправление**
- ✅ **Поддержка любых аддонов**
- ✅ **Максимальная точность через LLM**
- ✅ **Итеративное улучшение**

## Установка

### 1. Автоматическая установка

```bash
python scripts/install_blender_gpt.py
```

### 2. Ручная установка

```bash
pip install blender-gpt
```

### 3. Проверка установки

```bash
blender-gpt --version
```

## Использование

### Python API

```python
from src.integrations.blender_gpt_integration import BlenderGPTCLI

# Инициализация
cli = BlenderGPTCLI()

# Создание объекта с итеративным улучшением
prompt = "Create a perfect cube with dimensions 2x2x2 units, with clean geometry"
result = await cli.create_object(prompt, "precision_cube", iterations=3)

# Валидация существующей модели
validation = await cli.validate_model("path/to/model.stl")
```

### CLI Команды

```bash
# Создание объекта
blender-gpt --prompt "Create a sphere with radius 1" --output-dir output/

# Итеративное улучшение
blender-gpt --prompt "Improve this model" --input-model model.stl --iterations 3

# Валидация
blender-gpt --prompt "Validate this model" --input-model model.stl
```

## Преимущества BlenderGPT

### 1. Максимальная точность

```python
# Точные спецификации через естественный язык
prompt = """
Create a mechanical part with:
- Cylindrical base: diameter 50mm, height 20mm
- Central hole: diameter 10mm, through
- 4 mounting holes: diameter 5mm, positioned at corners
- Clean geometry, proper normals, manifold mesh
- Export as STL with high precision
"""
```

### 2. Автоматическая валидация

```python
# BlenderGPT автоматически проверяет:
validation_checks = [
    "geometry",      # Геометрическая корректность
    "manifold",      # Manifold mesh
    "overlapping",   # Перекрывающиеся грани
    "normals",       # Правильность нормалей
    "scaling",       # Масштабирование
    "positioning"    # Позиционирование
]
```

### 3. Итеративное улучшение

```python
# Автоматическое исправление проблем
iterative_prompt = """
Previous iteration had issues:
- Non-manifold edges detected
- Overlapping faces found

Fix these issues and improve:
- Ensure all edges are manifold
- Remove overlapping geometry
- Optimize mesh density
- Maintain original design intent
"""
```

## Интеграция с агентами

### Для оператора агента

```python
async def create_model_for_operator(prompt: str, target_score: float = 90.0):
    """Создание модели для оценки оператором"""
    
    cli = BlenderGPTCLI()
    
    # Итеративное создание с высокой точностью
    results = await cli.iterative.improve_model_iteratively(
        prompt,
        target_metrics={"quality_score": target_score},
        max_iterations=5
    )
    
    final_result = results[-1]
    
    # Проверка готовности для оператора
    if final_result.validation_score >= target_score:
        print("✅ Модель готова для оценки оператора")
        print(f"📁 Файл: {final_result.output_path}")
        print(f"📊 Score: {final_result.validation_score}/100")
        
        # Здесь можно интегрировать с Telegram ботом
        return final_result.output_path
    else:
        print("❌ Модель требует доработки")
        print(f"📊 Текущий score: {final_result.validation_score}/100")
        return None
```

### Автоматическое принятие решений

```python
async def auto_approval_system(prompt: str):
    """Система автоматического одобрения"""
    
    cli = BlenderGPTCLI()
    results = await cli.iterative.improve_model_iteratively(prompt)
    final_result = results[-1]
    
    if final_result.validation_score >= 95.0:
        print("🚀 Модель автоматически одобрена (высокое качество)")
        return final_result.output_path
    
    elif final_result.validation_score >= 85.0:
        print("👤 Требуется оценка оператора (среднее качество)")
        # Интеграция с Telegram ботом
        return final_result.output_path
    
    else:
        print("🔄 Требуется повторная попытка (низкое качество)")
        return None
```

## Примеры использования

### 1. Создание точного куба

```python
prompt = """
Create a perfect cube with:
- Dimensions: 2x2x2 units
- Clean geometry with proper normals
- No overlapping faces
- Manifold mesh
- Export as STL
"""

result = await cli.create_object(prompt, "perfect_cube", iterations=3)
```

### 2. Создание Nike логотипа

```python
prompt = """
Create a Nike Swoosh logo with:
- Smooth curved shape
- Extrusion depth: 2mm
- Clean edges and surfaces
- Proper scaling
- Export as STL
"""

result = await cli.create_object(prompt, "nike_swoosh", iterations=4)
```

### 3. Создание сложной детали

```python
prompt = """
Create a mechanical bracket with:
- Base plate: 100x80x10mm
- Two mounting holes: diameter 8mm
- Reinforcing ribs: 5mm thick
- Rounded corners: radius 5mm
- Clean geometry for 3D printing
- Export as STL
"""

result = await cli.create_object(prompt, "mechanical_bracket", iterations=5)
```

## Конфигурация

### Настройки качества

```python
request = BlenderGPTRequest(
    prompt="Create a sphere",
    quality_level="ultra_high",  # ultra_high, high, medium, low
    validation_checks=["geometry", "manifold", "overlapping", "normals"],
    output_format="stl"  # stl, obj, fbx, gltf
)
```

### Настройки итераций

```python
iterative = IterativeBlenderGPT(blender_gpt)
iterative.max_iterations = 5
iterative.min_score = 90.0  # Минимальный score для успеха
```

## Сравнение с текущей системой

| Функция | Текущая система | BlenderGPT |
|---------|----------------|------------|
| Валидация | Простые метрики | Полная валидация |
| Исправление | Ограниченное | Автоматическое |
| Точность | Средняя | Максимальная |
| Язык команд | Python API | Естественный язык |
| Аддоны | Проблемы | Полная поддержка |
| Итерации | Простые | Умные |

## Миграция с текущей системы

### 1. Замена валидатора

```python
# Старый код
from src.integrations.blender_validator import BlenderValidator
validator = BlenderValidator()
validation = await validator.validate_stl_file("model.stl")

# Новый код
from src.integrations.blender_gpt_integration import BlenderGPTCLI
cli = BlenderGPTCLI()
validation = await cli.validate_model("model.stl")
```

### 2. Замена итеративного улучшения

```python
# Старый код
from src.integrations.blender_validator import IterativeImprover
improver = IterativeImprover(engine, validator)
results = await improver.improve_model(spec)

# Новый код
from src.integrations.blender_gpt_integration import IterativeBlenderGPT
iterative = IterativeBlenderGPT(blender_gpt)
results = await iterative.improve_model_iteratively(prompt)
```

## Тестирование

### Запуск тестов

```bash
# Установка и настройка
python scripts/install_blender_gpt.py

# Тест интеграции
python scripts/test_blender_gpt_integration.py

# Тест CLI
blender-gpt --help
```

### Тестовые сценарии

1. **Создание простых объектов**
2. **Сложные геометрические формы**
3. **Валидация существующих моделей**
4. **Итеративное улучшение**
5. **Интеграция с агентами**

## Устранение неполадок

### Частые проблемы

1. **BlenderGPT не найден**
   ```bash
   pip install blender-gpt --upgrade
   ```

2. **Blender не найден**
   - Проверьте путь в настройках
   - Установите Blender в стандартную директорию

3. **Ошибки валидации**
   - Проверьте права доступа
   - Убедитесь в корректности STL файла

### Логирование

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Заключение

BlenderGPT предоставляет максимальную точность и функциональность для 3D генерации:

- **Естественный язык** для описания задач
- **Автоматическая валидация** и исправление
- **Итеративное улучшение** с умными подсказками
- **Полная интеграция** с Blender API
- **Готовность для оператора** с высоким качеством

Это решение превосходит нашу текущую систему и обеспечивает профессиональное качество 3D моделей. 