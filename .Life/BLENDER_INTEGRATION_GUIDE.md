# Blender Integration Guide

Высокопроизводительная система управления Blender для точной 3D генерации через API.

## Возможности

- ✅ **Декларативный API** - создание объектов через спецификации
- ✅ **Batch processing** - массовое создание объектов
- ✅ **Кэширование** - автоматическое кэширование результатов
- ✅ **Материалы** - поддержка различных типов материалов
- ✅ **Экспорт** - STL, OBJ, FBX, GLB форматы
- ✅ **Рендеринг** - создание превью изображений
- ✅ **CLI интерфейс** - командная строка для управления
- ✅ **Blueprint система** - создание сложных сцен из JSON

## Быстрый старт

### 1. Создание простого объекта

```python
from src.integrations import BlenderEngine, ObjectSpec, ObjectType, MaterialType, Vector3

# Создаем движок
engine = BlenderEngine()

# Спецификация куба
cube_spec = ObjectSpec(
    name="my_cube",
    object_type=ObjectType.CUBE,
    position=Vector3(0, 0, 0),
    dimensions=Vector3(2, 2, 2),
    material_type=MaterialType.METAL,
    color=Vector3(0.8, 0.2, 0.2)
)

# Создаем объект
result = await engine.create_object(cube_spec)
print(f"Создан: {result}")
```

### 2. CLI команды

```bash
# Создать куб
python -m src.integrations.blender_cli_integration cube my_cube --size 2.0 --material metal

# Создать цилиндр
python -m src.integrations.blender_cli_integration cylinder my_cylinder --radius 1.0 --height 3.0

# Создать сферу
python -m src.integrations.blender_cli_integration sphere my_sphere --radius 1.5 --segments 48

# Batch создание из JSON
python -m src.integrations.blender_cli_integration batch objects.json --output-dir output/

# Создание сцены из blueprint
python -m src.integrations.blender_cli_integration scene blueprint.json --render --export stl
```

## API Reference

### ObjectSpec

Спецификация для создания 3D объекта:

```python
@dataclass
class ObjectSpec:
    name: str                           # Имя объекта
    object_type: ObjectType             # Тип объекта (CUBE, CYLINDER, SPHERE, etc.)
    position: Vector3                   # Позиция в пространстве
    rotation: Vector3                   # Поворот (в радианах)
    scale: Vector3                      # Масштаб
    dimensions: Vector3                 # Размеры (для куба)
    radius: float                       # Радиус (для цилиндра/сферы)
    height: float                       # Высота (для цилиндра)
    segments: int                       # Количество сегментов
    rings: int                          # Количество колец (для сферы)
    material_type: Optional[MaterialType]  # Тип материала
    color: Vector3                      # Цвет (RGB)
    roughness: float                    # Шероховатость (0-1)
    metallic: float                     # Металличность (0-1)
    transparency: float                 # Прозрачность (0-1)
```

### SceneSpec

Спецификация для создания сцены:

```python
@dataclass
class SceneSpec:
    name: str                           # Имя сцены
    objects: List[ObjectSpec]           # Список объектов
    camera_position: Vector3            # Позиция камеры
    camera_target: Vector3              # Точка фокуса камеры
    lighting: str                       # Тип освещения (studio, outdoor, indoor)
    background_color: Vector3           # Цвет фона
```

### Поддерживаемые типы объектов

- `ObjectType.CUBE` - куб
- `ObjectType.CYLINDER` - цилиндр
- `ObjectType.SPHERE` - сфера
- `ObjectType.PLANE` - плоскость
- `ObjectType.CONE` - конус
- `ObjectType.TORUS` - тор
- `ObjectType.LAMP` - лампа

### Поддерживаемые материалы

- `MaterialType.METAL` - металл
- `MaterialType.PLASTIC` - пластик
- `MaterialType.GLASS` - стекло
- `MaterialType.WOOD` - дерево
- `MaterialType.CERAMIC` - керамика
- `MaterialType.FABRIC` - ткань

## Примеры использования

### Создание сложной сцены

```python
from src.integrations import *

# Создаем сцену
scene_spec = SceneSpec(
    name="assembly",
    camera_position=Vector3(10, -10, 8),
    lighting="studio"
)

# Добавляем объекты
scene_spec.objects.extend([
    # Основание
    ObjectSpec(
        name="base",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, -0.5),
        dimensions=Vector3(10, 10, 1),
        material_type=MaterialType.WOOD
    ),
    # Центральная колонна
    ObjectSpec(
        name="pillar",
        object_type=ObjectType.CYLINDER,
        position=Vector3(0, 0, 1),
        radius=0.8,
        height=2,
        material_type=MaterialType.METAL
    ),
    # Верхняя сфера
    ObjectSpec(
        name="top",
        object_type=ObjectType.SPHERE,
        position=Vector3(0, 0, 3),
        radius=1.2,
        material_type=MaterialType.GLASS,
        transparency=0.3
    )
])

# Создаем сцену с рендером и экспортом
render_spec = RenderSpec(
    resolution_x=1920,
    resolution_y=1080,
    samples=128,
    output_path="output/assembly_render.png"
)

export_spec = ExportSpec(
    format=ExportFormat.STL,
    output_path="output/assembly.stl"
)

results = await engine.create_scene(scene_spec, render_spec, export_spec)
```

### Batch создание объектов

```python
# Создаем список спецификаций
specs = []
for i in range(10):
    spec = ObjectSpec(
        name=f"object_{i}",
        object_type=ObjectType.CUBE,
        position=Vector3(i * 2 - 9, 0, 0),
        dimensions=Vector3(1, 1, 1),
        material_type=MaterialType.PLASTIC,
        color=Vector3(0.2 + i * 0.08, 0.5, 0.8)
    )
    specs.append(spec)

# Batch создание
results = await engine.batch_create(specs, "output/batch")
```

### JSON Blueprint

Создайте файл `blueprint.json`:

```json
{
  "name": "my_assembly",
  "camera_position": {"x": 10, "y": -10, "z": 8},
  "lighting": "studio",
  "objects": [
    {
      "name": "base",
      "type": "cube",
      "position": {"x": 0, "y": 0, "z": -0.5},
      "dimensions": {"x": 10, "y": 10, "z": 1},
      "material": "wood"
    },
    {
      "name": "pillar",
      "type": "cylinder",
      "position": {"x": 0, "y": 0, "z": 1},
      "radius": 0.8,
      "height": 2,
      "material": "metal"
    }
  ]
}
```

Затем создайте сцену:

```bash
python -m src.integrations.blender_cli_integration scene blueprint.json --render --export stl
```

## Управление кэшем

```python
# Получить статистику
stats = engine.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Cache size: {stats['cache_size_mb']:.2f} MB")

# Очистить кэш
engine.clear_cache()

# Очистить старые файлы (старше 24 часов)
removed = engine.cleanup_old_cache(24)
print(f"Removed {removed} old files")
```

## Просмотр результатов

```bash
# Просмотреть все созданные STL файлы
python scripts/quick_viewer.py

# Открыть конкретный файл
python scripts/quick_viewer.py cache/blender/my_object.stl
```

## Производительность

- **Кэширование**: Повторные запросы выполняются мгновенно
- **Batch processing**: Параллельное создание множества объектов
- **Async/await**: Неблокирующие операции
- **Оптимизированные скрипты**: Минимальное время выполнения Blender

## Требования

- Blender 3.0+ (установлен и доступен в PATH)
- Python 3.8+
- Зависимости: `asyncio`, `pathlib`, `tempfile`

## Структура файлов

```
src/integrations/
├── blender_engine.py          # Основной движок
├── blender_cli_integration.py # CLI интерфейс
└── __init__.py               # Экспорты

scripts/
├── test_blender_integration.py # Тесты
├── quick_viewer.py            # Просмотрщик
├── blueprint_example.json     # Пример blueprint
└── batch_objects_example.json # Пример batch

cache/blender/                 # Кэш файлов
output/                        # Результаты
```

## Troubleshooting

### Blender не найден
```python
# Укажите путь вручную
engine = BlenderEngine(blender_path="C:/Program Files/Blender/blender.exe")
```

### Ошибки экспорта
- Убедитесь, что Blender поддерживает нужный формат
- Проверьте права доступа к папке вывода

### Проблемы с материалами
- Используйте только поддерживаемые типы материалов
- Проверьте корректность значений (0-1 для цветов, шероховатости и т.д.)

## Расширение функциональности

### Добавление нового типа объекта

1. Добавьте новый тип в `ObjectType` enum
2. Обновите `_generate_object_script()` для поддержки нового типа
3. Добавьте соответствующие параметры в `ObjectSpec`

### Добавление нового материала

1. Добавьте новый тип в `MaterialType` enum
2. Обновите логику создания материалов в скриптах Blender

### Кастомные скрипты

Вы можете передавать собственные скрипты Blender:

```python
custom_script = """
import bpy
# Ваш код Blender
"""

success = await engine._execute_blender_script(custom_script, output_path)
``` 