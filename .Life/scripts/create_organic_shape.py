#!/usr/bin/env python3
"""
Создание органической фигуры через Blender
"""

import subprocess
import tempfile
from pathlib import Path

def create_organic_script():
    """Создает скрипт для создания органической фигуры"""
    script = '''
import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_organic_flower():
    """Создает органический цветок"""
    
    # Параметры
    num_petals = 8
    base_radius = 3.0
    height_variation = 2.0
    
    vertices = []
    faces = []
    
    # Центр цветка
    center_vertices = []
    for i in range(16):
        angle = i * math.pi * 2 / 16
        x = 0.5 * math.cos(angle)
        y = 0.5 * math.sin(angle)
        z = 0.2 * math.sin(angle * 4)  # Волнистость центра
        center_vertices.append((x, y, z))
        vertices.append((x, y, z))
    
    # Создаем лепестки
    for petal in range(num_petals):
        petal_angle = petal * math.pi * 2 / num_petals
        
        # Базовые точки лепестка
        petal_vertices = []
        for i in range(20):
            t = i / 19.0  # Параметр от 0 до 1
            
            # Радиус лепестка (широкий у основания, узкий на конце)
            radius = base_radius * (1.0 - t * 0.7) * (1.0 + 0.3 * math.sin(t * math.pi))
            
            # Угол лепестка
            angle_offset = (t - 0.5) * 0.6  # Изгиб лепестка
            angle = petal_angle + angle_offset
            
            # Высота лепестка
            height = height_variation * t * (1.0 + 0.5 * math.sin(t * math.pi * 2))
            
            # Координаты
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = height
            
            vertices.append((x, y, z))
            petal_vertices.append(len(vertices) - 1)
        
        # Соединяем лепесток с центром
        center_start = 0
        petal_start = len(vertices) - 20
        
        # Создаем грани для лепестка
        for i in range(19):
            # Треугольники между центром и лепестком
            if i < 16:
                faces.append([center_start + i, center_start + ((i + 1) % 16), petal_start + i])
            
            # Треугольники вдоль лепестка
            if i < 19:
                faces.append([petal_start + i, petal_start + i + 1, petal_start + min(i + 2, 19)])
    
    # Создаем объект из вершин
    mesh = bpy.data.meshes.new("OrganicFlower")
    obj = bpy.data.objects.new("OrganicFlower", mesh)
    
    # Добавляем в сцену
    bpy.context.collection.objects.link(obj)
    
    # Заполняем меш данными
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    # Сглаживание
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Красивый материал
    mat = bpy.data.materials.new(name="FlowerMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.4, 0.6, 1.0)  # Розовый
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Subsurface'].default_value = 0.2  # Подповерхностное рассеивание
    bsdf.inputs['Subsurface Color'].default_value = (1.0, 0.8, 0.9, 1.0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Применяем материал
    obj.data.materials.append(mat)
    
    return obj

# Создаем органический цветок
flower = create_organic_flower()

# Освещение
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(-3, 3, 8))
area_light = bpy.context.active_object
area_light.data.energy = 2.0
area_light.data.color = (1.0, 0.9, 0.8)  # Теплый свет

# Камера
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Настройки рендера
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Сохраняем как blend файл
bpy.ops.wm.save_as_mainfile(filepath="output/blender/organic_flower.blend")

print("SUCCESS: Органический цветок создан!")
print("SUCCESS: Файл сохранен как: output/blender/organic_flower.blend")

# Можно открыть в Blender для просмотра
'''
    return script

def run_organic_script():
    """Запускает скрипт создания органической фигуры"""
    script_content = create_organic_script()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    # Путь к Blender
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🌸 Создание органического цветка...")
        print("🔄 Запуск Blender...")
        
        # Запускаем Blender
        result = subprocess.run([
            blender_path,
            "--background",
            "--python", script_path
        ], capture_output=True, text=True, timeout=60)
        
        print("📊 Результат:")
        if result.stdout:
            # Ищем наши SUCCESS сообщения
            for line in result.stdout.split('\n'):
                if 'SUCCESS:' in line:
                    print(f"✅ {line.replace('SUCCESS:', '').strip()}")
        
        if result.stderr and 'SUCCESS:' not in result.stderr:
            print("Предупреждения:", result.stderr.split('\n')[0])
        
        if result.returncode == 0:
            print("\n🎉 Органический цветок успешно создан!")
            print("📁 Файл сохранен: output/blender/organic_flower.blend")
            print("💡 Откройте файл в Blender для просмотра и рендеринга")
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
    print("🌺 Создание органического цветка через Blender")
    print("=" * 50)
    
    run_organic_script()
    
    print("\n🎨 Готово! Откройте output/blender/organic_flower.blend в Blender") 