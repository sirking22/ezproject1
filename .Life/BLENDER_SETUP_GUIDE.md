# 🎨 Руководство по настройке Blender API

## 📋 Что нужно сделать

### 1. Установка Blender

1. **Скачайте Blender** с официального сайта: https://www.blender.org/download/
2. **Выберите версию**: рекомендуется LTS (Long Term Support)
3. **Установите** в стандартную директорию:
   - Windows: `C:\Program Files\Blender Foundation\Blender\`
   - Или в `C:\Users\YourName\AppData\Local\Programs\Blender Foundation\Blender\`

### 2. Проверка установки

После установки Blender должен быть доступен в командной строке:

```bash
blender --version
```

Если команда не работает, добавьте Blender в PATH или укажите путь вручную.

### 3. Запуск теста

Запустите тест для проверки интеграции:

```bash
python scripts/test_blender_cli.py
```

Тест автоматически:
- 🔍 Найдет Blender
- 🧪 Создаст тестовые объекты
- 📁 Сохранит STL файлы
- 📸 Сгенерирует превью

## 🚀 Как использовать

### Простое создание объекта

```python
from src.integrations.blender_cli_integration import BlenderCLIIntegration

# Создаем интеграцию
blender = BlenderCLIIntegration()

# Создаем куб
result = blender.create_precise_object(
    object_type='cube',
    dimensions={'width': 100, 'height': 100, 'depth': 100},
    name='MyCube',
    output_dir='output'
)

if result['success']:
    print(f"✅ Куб создан: {result['stl_file']}")
    print(f"📸 Превью: {result['preview_file']}")
```

### Создание органической лампы

```python
# Создаем органическую лампу
result = blender.create_organic_lamp(
    base_radius=80.0,
    complexity=1.5,
    output_dir='output'
)

if result['success']:
    print(f"✅ Лампа создана: {result['stl_file']}")
```

### Пакетная генерация

```python
# Создаем несколько объектов
objects_data = [
    {
        'type': 'cube',
        'dimensions': {'width': 50, 'height': 50, 'depth': 50},
        'name': 'SmallCube'
    },
    {
        'type': 'sphere',
        'dimensions': {'radius': 30},
        'name': 'TestSphere'
    },
    {
        'type': 'organic_lamp',
        'base_radius': 40.0,
        'complexity': 0.8
    }
]

results = blender.batch_generate(objects_data, output_dir='output')
```

## 🔧 Возможности системы

### Поддерживаемые типы объектов

1. **Куб** (`cube`)
   - Параметры: `width`, `height`, `depth`
   - Точные размеры в миллиметрах

2. **Цилиндр** (`cylinder`)
   - Параметры: `radius`, `height`
   - Настраиваемое количество сегментов

3. **Сфера** (`sphere`)
   - Параметры: `radius`
   - Настраиваемое разрешение

4. **Органическая лампа** (`organic_lamp`)
   - Параметры: `base_radius`, `complexity`
   - Сложные органические формы

### Экспорт форматов

- **STL** - для 3D печати
- **PNG** - превью изображения
- **OBJ** - для других 3D программ

### Точность

- Единицы измерения: миллиметры
- Точность позиционирования: ±0.001mm
- Поддержка точных размеров по чертежам

## 🛠️ Устранение проблем

### Blender не найден

1. **Проверьте установку**:
   ```bash
   # Windows
   dir "C:\Program Files\Blender Foundation\Blender\blender.exe"
   ```

2. **Добавьте в PATH**:
   - Откройте "Система" → "Дополнительные параметры системы"
   - "Переменные среды" → "Path" → "Изменить"
   - Добавьте путь к папке с blender.exe

3. **Укажите путь вручную**:
   ```python
   blender = BlenderCLIIntegration(r"C:\path\to\blender.exe")
   ```

### Ошибки создания объектов

1. **Проверьте права доступа** к папке output
2. **Убедитесь**, что Blender может запуститься в headless режиме
3. **Проверьте логи** в выводе ошибок

### Медленная генерация

1. **Уменьшите сложность** органических объектов
2. **Используйте меньше сегментов** для простых форм
3. **Закройте другие программы** для освобождения ресурсов

## 📁 Структура файлов

```
output/
├── TestCube.stl          # STL файл куба
├── preview_TestCube.png  # Превью куба
├── organic_lamp.stl      # STL файл лампы
└── preview.png           # Превью лампы
```

## 🔗 Интеграция с основной системой

После настройки Blender, система автоматически интегрируется с твоей Life Management System:

```python
from src.core.life_management_system import LifeManagementSystem

lms = LifeManagementSystem()

# Создание 3D объекта через основную систему
result = lms.generate_3d_object({
    'type': 'organic_lamp',
    'base_radius': 60.0,
    'complexity': 1.0
})
```

## 🎯 Следующие шаги

1. ✅ Установите Blender
2. ✅ Запустите тест: `python scripts/test_blender_cli.py`
3. ✅ Проверьте созданные файлы в папке `test_output/`
4. ✅ Интегрируйте с основной системой
5. 🚀 Создавайте точные 3D объекты!

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи в консоли
2. Убедитесь, что Blender установлен корректно
3. Проверьте права доступа к папкам
4. Попробуйте запустить Blender вручную

---

**Удачи в создании 3D объектов! 🎨✨** 