#!/usr/bin/env python3
"""
Демонстрация BlenderGPT плагина - создание сложного объекта
"""

import subprocess
import tempfile
import json
from pathlib import Path

def create_blender_gpt_script():
    """Создает скрипт для выполнения через BlenderGPT"""
    script = '''
import bpy
import bmesh
import math
from mathutils import Vector

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Создаем красивую спиральную башню
def create_spiral_tower():
    # Создаем основание
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3,
        depth=1,
        location=(0, 0, 0)
    )
    base = bpy.context.active_object
    base.name = "SpiralTower_Base"
    
    # Создаем спираль из кубов
    num_cubes = 20
    height_step = 0.5
    angle_step = math.pi * 2 / 8  # 8 кубов на виток
    
    for i in range(num_cubes):
        height = i * height_step + 1
        angle = i * angle_step
        radius = 2.5 - (i * 0.05)  # Сужение к верху
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height
        
        # Создаем куб
        bpy.ops.mesh.primitive_cube_add(
            size=0.4,
            location=(x, y, z)
        )
        cube = bpy.context.active_object
        cube.name = f"SpiralCube_{i+1}"
        
        # Поворачиваем куб
        cube.rotation_euler = (0, 0, angle)
        
        # Добавляем материал
        if i % 3 == 0:
            color = (1.0, 0.3, 0.3)  # Красный
        elif i % 3 == 1:
            color = (0.3, 1.0, 0.3)  # Зеленый
        else:
            color = (0.3, 0.3, 1.0)  # Синий
            
        mat = bpy.data.materials.new(name=f"Material_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*color, 1.0)
        cube.data.materials.append(mat)
    
    # Создаем вершину башни
    bpy.ops.mesh.primitive_cone_add(
        radius1=1.0,
        radius2=0.1,
        depth=2.0,
        location=(0, 0, num_cubes * height_step + 2)
    )
    top = bpy.context.active_object
    top.name = "SpiralTower_Top"
    
    # Материал для вершины (золотой)
    gold_mat = bpy.data.materials.new(name="Gold")
    gold_mat.use_nodes = True
    bsdf = gold_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (1.0, 0.8, 0.2, 1.0)  # Золотой цвет
    bsdf.inputs[4].default_value = 1.0  # Metallic
    bsdf.inputs[7].default_value = 0.1  # Roughness
    top.data.materials.append(gold_mat)

# Создаем башню
create_spiral_tower()

# Добавляем освещение
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Настройки рендера
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Добавляем камеру
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
scene.camera = camera

# Экспортируем в STL
output_path = "output/blender/spiral_tower.stl"
bpy.ops.export_mesh.stl(
    filepath=output_path,
    use_selection=False,
    global_scale=1.0
)

print("SUCCESS: Спиральная башня создана и экспортирована в:", output_path)

# Рендерим превью
scene.render.filepath = "output/blender/spiral_tower_render.png"
bpy.ops.render.render(write_still=True)

print("SUCCESS: Рендер сохранен в: output/blender/spiral_tower_render.png")
'''
    return script

def run_blender_script():
    """Запускает скрипт в Blender"""
    script_content = create_blender_gpt_script()
    
    # Создаем временный файл со скриптом
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    # Путь к Blender
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🎨 Создание спиральной башни через Blender...")
        print("🔄 Запуск Blender...")
        
        # Запускаем Blender с нашим скриптом
        result = subprocess.run([
            blender_path,
            "--background",
            "--python", script_path
        ], capture_output=True, text=True, timeout=60)
        
        print("📊 Результат выполнения:")
        if result.stdout:
            print("Blender Output:")
            print(result.stdout)
        
        if result.stderr:
            print("Blender Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Спиральная башня успешно создана!")
            print("📁 Проверьте папку output/blender/")
            print("   - spiral_tower.stl (3D модель)")
            print("   - spiral_tower_render.png (рендер)")
        else:
            print(f"❌ Ошибка выполнения (код: {result.returncode})")
            
    except subprocess.TimeoutExpired:
        print("⏰ Время выполнения истекло")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Удаляем временный файл
        Path(script_path).unlink(missing_ok=True)

if __name__ == "__main__":
    print("🏗️ Создание спиральной башни через Blender")
    print("=" * 50)
    
    run_blender_script()
    
    print("\n🎉 Готово! Проверьте результаты в output/blender/") 