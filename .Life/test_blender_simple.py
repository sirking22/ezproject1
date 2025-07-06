#!/usr/bin/env python3
"""
Простой тест Blender CLI
"""

import subprocess
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blender_path():
    """Тест пути к Blender"""
    blender_path = r"Z:\Программы\Blender\blender.exe"
    
    if os.path.exists(blender_path):
        logger.info(f"✅ Blender найден: {blender_path}")
        return blender_path
    else:
        logger.error(f"❌ Blender не найден: {blender_path}")
        return None

def create_simple_cube_script():
    """Создание простого скрипта для куба"""
    script_content = '''
import bpy
import os

# Очистка сцены
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Создание куба
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"

# Выбираем объект
bpy.context.view_layer.objects.active = cube
cube.select_set(True)

# Настройка единиц измерения
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

# Экспорт в STL
output_dir = r"test_output"
os.makedirs(output_dir, exist_ok=True)

stl_path = os.path.join(output_dir, "test_cube.stl")

# Включаем аддон для экспорта STL
bpy.ops.preferences.addon_enable(module="io_mesh_stl")

# Экспортируем
bpy.ops.export_mesh.stl(
    filepath=stl_path,
    use_selection=True,
    global_scale=1.0,
    use_scene_unit=True,
    ascii=False
)

print("SUCCESS: Cube created and exported")
'''
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        return f.name

def test_blender_execution():
    """Тест выполнения Blender"""
    blender_path = test_blender_path()
    if not blender_path:
        return False
    
    # Создаем директорию для вывода
    os.makedirs('test_output', exist_ok=True)
    
    # Создаем скрипт
    script_path = create_simple_cube_script()
    
    try:
        logger.info("🚀 Запуск Blender...")
        
        # Запускаем Blender
        cmd = [
            blender_path,
            '--background',
            '--python', script_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        logger.info(f"📊 Код возврата: {result.returncode}")
        logger.info(f"📤 STDOUT: {result.stdout}")
        if result.stderr:
            logger.info(f"📥 STDERR: {result.stderr}")
        
        if result.returncode == 0:
            logger.info("✅ Blender выполнился успешно")
            
            # Проверяем созданный файл
            stl_file = "test_output/test_cube.stl"
            if os.path.exists(stl_file):
                logger.info(f"✅ STL файл создан: {stl_file}")
                return True
            else:
                logger.error(f"❌ STL файл не найден: {stl_file}")
                return False
        else:
            logger.error("❌ Blender завершился с ошибкой")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Таймаут выполнения Blender")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False
    finally:
        # Удаляем временный скрипт
        if os.path.exists(script_path):
            os.unlink(script_path)

def main():
    """Основная функция"""
    logger.info("🧪 Тестирование Blender CLI")
    logger.info("=" * 50)
    
    success = test_blender_execution()
    
    if success:
        logger.info("🎉 ТЕСТ ПРОЙДЕН! Blender работает корректно")
    else:
        logger.error("❌ ТЕСТ ПРОВАЛЕН! Проверьте настройки Blender")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 