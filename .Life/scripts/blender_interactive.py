#!/usr/bin/env python3
"""
Интерактивное создание фигуры в Blender
"""

import subprocess
import tempfile
from pathlib import Path

def create_interactive_script():
    """Создает скрипт для интерактивной работы в Blender"""
    script = '''
import bpy
import bmesh
import math
from mathutils import Vector

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_magic_crystal():
    """Создаем магический кристалл"""
    
    # 1. Центральный кристалл (октаэдр)
    vertices = [
        (0, 0, 2),      # Верх
        (1, 1, 0),      # Северо-восток
        (-1, 1, 0),     # Северо-запад  
        (-1, -1, 0),    # Юго-запад
        (1, -1, 0),     # Юго-восток
        (0, 0, -2)      # Низ
    ]
    
    faces = [
        [0, 1, 2],  # Верхняя грань 1
        [0, 2, 3],  # Верхняя грань 2
        [0, 3, 4],  # Верхняя грань 3
        [0, 4, 1],  # Верхняя грань 4
        [5, 2, 1],  # Нижняя грань 1
        [5, 3, 2],  # Нижняя грань 2
        [5, 4, 3],  # Нижняя грань 3
        [5, 1, 4]   # Нижняя грань 4
    ]
    
    # Создаем основной кристалл
    mesh = bpy.data.meshes.new("MagicCrystal")
    obj = bpy.data.objects.new("MagicCrystal", mesh)
    bpy.context.collection.objects.link(obj)
    
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    # Масштабируем кристалл
    obj.scale = (2.0, 2.0, 1.5)
    
    # Создаем красивый кристальный материал
    mat = bpy.data.materials.new(name="Crystal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF для кристалла
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.7, 0.9, 1.0, 1.0)  # Голубой
    bsdf.inputs['Transmission'].default_value = 0.95  # Прозрачность
    bsdf.inputs['Roughness'].default_value = 0.05     # Очень гладкий
    bsdf.inputs['IOR'].default_value = 1.45           # Показатель преломления
    
    # Добавляем эмиссию для свечения
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = (0.5, 0.8, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 0.3
    
    # Смешиваем BSDF и эмиссию
    mix = nodes.new(type='ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = 0.1
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Соединяем ноды
    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emission.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    obj.data.materials.append(mat)
    
    return obj

def create_floating_rings():
    """Создаем плавающие кольца вокруг кристалла"""
    rings = []
    
    for i in range(4):
        # Разные радиусы и высоты
        angle = i * 90  # 90 градусов между кольцами
        radius = 6.0 + i * 0.5
        height = 1.0 + i * 0.8
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=1.2,
            minor_radius=0.2,
            location=(0, 0, height)
        )
        ring = bpy.context.active_object
        ring.name = f"FloatingRing_{i+1}"
        
        # Наклоняем кольцо
        ring.rotation_euler = (math.radians(20 + i * 10), 0, math.radians(angle))
        
        # Анимированное вращение
        ring.rotation_euler = (0, 0, math.radians(angle))
        
        # Материал для колец
        ring_mat = bpy.data.materials.new(name=f"RingMaterial_{i}")
        ring_mat.use_nodes = True
        ring_bsdf = ring_mat.node_tree.nodes["Principled BSDF"]
        
        # Разные металлические цвета
        colors = [
            (1.0, 0.8, 0.2, 1.0),  # Золото
            (0.9, 0.9, 0.9, 1.0),  # Серебро
            (0.8, 0.4, 0.1, 1.0),  # Медь
            (0.6, 0.3, 0.8, 1.0),  # Фиолетовый металл
        ]
        
        ring_bsdf.inputs['Base Color'].default_value = colors[i]
        ring_bsdf.inputs['Metallic'].default_value = 1.0
        ring_bsdf.inputs['Roughness'].default_value = 0.1
        
        ring.data.materials.append(ring_mat)
        rings.append(ring)
    
    return rings

def create_energy_orbs():
    """Создаем энергетические сферы"""
    orbs = []
    
    for i in range(6):
        angle = i * 60 * math.pi / 180  # 60 градусов
        radius = 4.5
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0.5 + (i % 2) * 2.0  # Разная высота
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.3,
            location=(x, y, z)
        )
        orb = bpy.context.active_object
        orb.name = f"EnergyOrb_{i+1}"
        
        # Светящийся материал
        orb_mat = bpy.data.materials.new(name=f"OrbMaterial_{i}")
        orb_mat.use_nodes = True
        orb_nodes = orb_mat.node_tree.nodes
        orb_nodes.clear()
        
        # Только эмиссия для свечения
        emission = orb_nodes.new(type='ShaderNodeEmission')
        output = orb_nodes.new(type='ShaderNodeOutputMaterial')
        
        # Разные цвета энергии
        energy_colors = [
            (1.0, 0.3, 0.3),  # Красный
            (0.3, 1.0, 0.3),  # Зеленый
            (0.3, 0.3, 1.0),  # Синий
            (1.0, 1.0, 0.3),  # Желтый
            (1.0, 0.3, 1.0),  # Магента
            (0.3, 1.0, 1.0),  # Циан
        ]
        
        emission.inputs['Color'].default_value = (*energy_colors[i], 1.0)
        emission.inputs['Strength'].default_value = 3.0
        
        orb_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        orb.data.materials.append(orb_mat)
        orbs.append(orb)
    
    return orbs

# Создаем всю композицию
print("Создание магического кристалла...")
crystal = create_magic_crystal()

print("Создание плавающих колец...")
rings = create_floating_rings()

print("Создание энергетических сфер...")
orbs = create_energy_orbs()

# Настраиваем освещение
print("Настройка освещения...")

# Удаляем стандартный свет
if "Light" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)

# HDRI освещение для красивых отражений
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes.clear()

# Environment texture
env_tex = world_nodes.new(type='ShaderNodeTexEnvironment')
world_bg = world_nodes.new(type='ShaderNodeBackground')
world_output = world_nodes.new(type='ShaderNodeOutputWorld')

world_bg.inputs['Strength'].default_value = 0.5
world.node_tree.links.new(env_tex.outputs['Color'], world_bg.inputs['Color'])
world.node_tree.links.new(world_bg.outputs['Background'], world_output.inputs['Surface'])

# Дополнительное освещение
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0
sun.data.color = (1.0, 0.95, 0.8)

# Настраиваем камеру
print("Настройка камеры...")
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects["Camera"]
else:
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object

camera.location = (8, -8, 6)
camera.rotation_euler = (1.1, 0, 0.785)

# Настройки рендера для красивого результата
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Включаем дополнительные фичи Cycles
scene.cycles.use_denoising = True
scene.view_settings.look = 'Medium High Contrast'

print("✨ Магический кристалл создан!")
print("🎨 Сцена готова для рендеринга!")
print("📷 Нажмите F12 для рендера или пробел для воспроизведения анимации")

# Сохраняем сцену
bpy.ops.wm.save_as_mainfile(filepath="output/blender/magic_crystal_scene.blend")
print("💾 Сцена сохранена: output/blender/magic_crystal_scene.blend")
'''
    return script

def run_blender_with_script():
    """Открываем Blender со скриптом"""
    script_content = create_interactive_script()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🎇 Создание магического кристалла в Blender...")
        print("🚀 Открытие Blender с интерактивной сценой...")
        
        # Запускаем Blender с GUI и выполняем скрипт
        subprocess.Popen([
            blender_path,
            "--python", script_path
        ])
        
        print("✨ Blender открыт!")
        print("🎨 Магический кристалл создается...")
        print("🎬 В Blender вы увидите:")
        print("   - 💎 Центральный кристалл с прозрачностью")
        print("   - 🔄 4 плавающих металлических кольца") 
        print("   - ⚡ 6 светящихся энергетических сфер")
        print("   - 🌅 Профессиональное освещение")
        print("")
        print("🎯 Что можно делать:")
        print("   - F12 - рендер сцены")
        print("   - Пробел - воспроизведение анимации")
        print("   - Tab - режим редактирования")
        print("   - Ctrl+S - сохранить проект")
        
    except Exception as e:
        print(f"❌ Ошибка запуска Blender: {e}")
    finally:
        # Не удаляем файл сразу, Blender может его использовать
        print(f"📝 Скрипт: {script_path}")

if __name__ == "__main__":
    print("🔮 Интерактивное создание в Blender")
    print("=" * 50)
    
    run_blender_with_script()
    
    print("\n✨ Наслаждайтесь созданием в Blender!") 