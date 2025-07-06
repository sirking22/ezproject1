#!/usr/bin/env python3
"""
Создание простого художественного объекта через Blender
"""

import subprocess
import tempfile
from pathlib import Path

def create_art_script():
    """Создает скрипт для художественного объекта"""
    script = '''
import bpy
import bmesh
import math

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Создаем красивую художественную композицию
def create_art_composition():
    objects_created = []
    
    # 1. Центральная сфера
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=2.0,
        location=(0, 0, 2)
    )
    sphere = bpy.context.active_object
    sphere.name = "CentralSphere"
    objects_created.append(sphere)
    
    # Материал для сферы - стекло
    mat_glass = bpy.data.materials.new(name="Glass")
    mat_glass.use_nodes = True
    nodes = mat_glass.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1.0)
    bsdf.inputs['Transmission'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.1
    sphere.data.materials.append(mat_glass)
    
    # 2. Кольца вокруг сферы
    for i in range(3):
        angle = i * 120 * math.pi / 180  # 120 градусов
        radius = 5.0
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 2.5 + i * 0.5
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=1.5,
            minor_radius=0.3,
            location=(x, y, z)
        )
        ring = bpy.context.active_object
        ring.name = f"Ring_{i+1}"
        ring.rotation_euler = (math.pi/2, 0, angle)
        objects_created.append(ring)
        
        # Материал - металл
        mat_metal = bpy.data.materials.new(name=f"Metal_{i}")
        mat_metal.use_nodes = True
        bsdf_metal = mat_metal.node_tree.nodes["Principled BSDF"]
        colors = [(0.8, 0.6, 0.2, 1.0), (0.7, 0.7, 0.7, 1.0), (0.9, 0.4, 0.2, 1.0)]
        bsdf_metal.inputs['Base Color'].default_value = colors[i]
        bsdf_metal.inputs['Metallic'].default_value = 0.9
        bsdf_metal.inputs['Roughness'].default_value = 0.2
        ring.data.materials.append(mat_metal)
    
    # 3. Основание
    bpy.ops.mesh.primitive_cylinder_add(
        radius=8.0,
        depth=0.5,
        location=(0, 0, -0.25)
    )
    base = bpy.context.active_object
    base.name = "Base"
    objects_created.append(base)
    
    # Материал - дерево
    mat_wood = bpy.data.materials.new(name="Wood")
    mat_wood.use_nodes = True
    bsdf_wood = mat_wood.node_tree.nodes["Principled BSDF"]
    bsdf_wood.inputs['Base Color'].default_value = (0.6, 0.4, 0.2, 1.0)
    bsdf_wood.inputs['Roughness'].default_value = 0.8
    base.data.materials.append(mat_wood)
    
    # 4. Декоративные элементы
    for i in range(6):
        angle = i * 60 * math.pi / 180
        radius = 3.5
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0.5
        
        bpy.ops.mesh.primitive_cube_add(
            size=0.5,
            location=(x, y, z)
        )
        cube = bpy.context.active_object
        cube.name = f"DecorCube_{i+1}"
        cube.rotation_euler = (0, 0, angle)
        objects_created.append(cube)
        
        # Яркий материал
        mat_bright = bpy.data.materials.new(name=f"Bright_{i}")
        mat_bright.use_nodes = True
        bsdf_bright = mat_bright.node_tree.nodes["Principled BSDF"]
        # Разные яркие цвета
        bright_colors = [
            (1.0, 0.2, 0.2, 1.0),  # Красный
            (0.2, 1.0, 0.2, 1.0),  # Зеленый
            (0.2, 0.2, 1.0, 1.0),  # Синий
            (1.0, 1.0, 0.2, 1.0),  # Желтый
            (1.0, 0.2, 1.0, 1.0),  # Магента
            (0.2, 1.0, 1.0, 1.0),  # Голубой
        ]
        bsdf_bright.inputs['Base Color'].default_value = bright_colors[i]
        bsdf_bright.inputs['Emission'].default_value = bright_colors[i]
        bsdf_bright.inputs['Emission Strength'].default_value = 0.5
        cube.data.materials.append(mat_bright)
    
    return objects_created

# Создаем композицию
objects = create_art_composition()

# Освещение
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Дополнительное освещение
bpy.ops.object.light_add(type='AREA', location=(-5, 5, 8))
area = bpy.context.active_object
area.data.energy = 2.0
area.data.color = (1.0, 0.9, 0.8)

# Камера
bpy.ops.object.camera_add(location=(12, -12, 8))
camera = bpy.context.active_object
# Направляем камеру на центр
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Настройки сцены
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32  # Быстрый рендер
scene.render.resolution_x = 1080
scene.render.resolution_y = 1080

# Экспортируем все объекты в один STL
output_stl = "output/blender/art_composition.stl"

# Выделяем все наши объекты
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    obj.select_set(True)

# Объединяем в один объект для экспорта
bpy.ops.object.join()
combined = bpy.context.active_object
combined.name = "ArtComposition"

# Ручной экспорт STL
import bmesh

# Получаем mesh данные
bm = bmesh.new()
bm.from_mesh(combined.data)

# Применяем трансформации
bmesh.ops.transform(bm, matrix=combined.matrix_world, verts=bm.verts)

# Треугулируем
bmesh.ops.triangulate(bm, faces=bm.faces)

# Создаем STL данные
stl_data = []
for face in bm.faces:
    # Нормаль грани
    normal = face.normal
    stl_data.append(f"facet normal {normal.x} {normal.y} {normal.z}")
    stl_data.append("  outer loop")
    for vert in face.verts:
        v = vert.co
        stl_data.append(f"    vertex {v.x} {v.y} {v.z}")
    stl_data.append("  endloop")
    stl_data.append("endfacet")

# Записываем ASCII STL
import os
os.makedirs("output/blender", exist_ok=True)

with open(output_stl, 'w') as f:
    f.write("solid ArtComposition\\n")
    for line in stl_data:
        f.write(line + "\\n")
    f.write("endsolid ArtComposition\\n")

bm.free()

print("SUCCESS: Художественная композиция создана!")
print(f"SUCCESS: STL экспортирован в: {output_stl}")
print(f"SUCCESS: Объектов в композиции: {len(objects)}")

# Рендерим превью
scene.render.filepath = "output/blender/art_composition_render"
bpy.ops.render.render(write_still=True)
print("SUCCESS: Рендер сохранен: output/blender/art_composition_render.png")
'''
    return script

def run_art_script():
    """Запускает создание художественного объекта"""
    script_content = create_art_script()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🎨 Создание художественной композиции...")
        print("🔄 Запуск Blender...")
        
        result = subprocess.run([
            blender_path,
            "--background",
            "--python", script_path
        ], capture_output=True, text=True, timeout=90)
        
        print("📊 Результат:")
        if result.stdout:
            for line in result.stdout.split('\n'):
                if 'SUCCESS:' in line:
                    print(f"✅ {line.replace('SUCCESS:', '').strip()}")
        
        if result.returncode == 0:
            print("\n🎉 Художественная композиция создана!")
            print("📁 Файлы в output/blender/:")
            print("   - art_composition.stl (3D модель)")
            print("   - art_composition_render.png (рендер)")
        else:
            print(f"❌ Код ошибки: {result.returncode}")
            if result.stderr:
                print("Ошибки:", result.stderr[:500])
                
    except subprocess.TimeoutExpired:
        print("⏰ Время выполнения истекло")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        Path(script_path).unlink(missing_ok=True)

if __name__ == "__main__":
    print("🎭 Создание художественной композиции")
    print("=" * 50)
    
    run_art_script()
    
    print("\n🌟 Готово! Проверьте output/blender/") 