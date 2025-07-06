#!/usr/bin/env python3
"""
Создание сложного объекта с множественными фигурами
"""

import subprocess
import tempfile
from pathlib import Path

def create_complex_object_script():
    """Создает скрипт для сложного объекта"""
    script = '''
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_central_core():
    """Создаем центральное ядро"""
    print("🔮 Создание центрального ядра...")
    
    # Создаем икосаэдр
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=2.0,
        location=(0, 0, 0)
    )
    core = bpy.context.active_object
    core.name = "CentralCore"
    
    # Добавляем детали через displacement
    displace = core.modifiers.new(name="Displacement", type='DISPLACE')
    tex = bpy.data.textures.new("CoreDisplacement", type='VORONOI')
    tex.noise_scale = 1.5
    displace.texture = tex
    displace.strength = 0.3
    
    # Материал для ядра
    mat = bpy.data.materials.new(name="CoreMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Noise texture
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 200)
    noise.inputs['Scale'].default_value = 8.0
    
    # Color ramp
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 200)
    color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.3, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.3, 0.5, 0.8, 1.0)
    
    # Emission
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 200)
    emission.inputs['Color'].default_value = (0.2, 0.4, 0.8, 1.0)
    emission.inputs['Strength'].default_value = 1.5
    
    # Mix shader
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    mix_shader.location = (200, 0)
    mix_shader.inputs['Fac'].default_value = 0.3
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Соединяем
    links.new(noise.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Transmission'].default_value = 0.2
    
    core.data.materials.append(mat)
    return core

def create_orbital_rings():
    """Создаем орбитальные кольца"""
    print("🔄 Создание орбитальных колец...")
    rings = []
    
    for i in range(5):
        # Разные радиусы и наклоны
        radius = 4.0 + i * 1.2
        height = i * 0.8
        tilt = i * 15
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius,
            minor_radius=0.15,
            major_segments=64,
            minor_segments=16,
            location=(0, 0, height)
        )
        ring = bpy.context.active_object
        ring.name = f"OrbitalRing_{i+1}"
        
        # Наклон
        ring.rotation_euler = (math.radians(tilt), 0, math.radians(i * 45))
        
        # Материал
        mat = bpy.data.materials.new(name=f"RingMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Разные металлы
        metals = [
            (1.0, 0.8, 0.2),  # Золото
            (0.9, 0.9, 0.9),  # Серебро
            (0.8, 0.4, 0.1),  # Медь
            (0.6, 0.3, 0.8),  # Фиолетовый
            (0.2, 0.8, 0.8),  # Бирюзовый
        ]
        
        bsdf.inputs['Base Color'].default_value = (*metals[i], 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.1
        
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        ring.data.materials.append(mat)
        rings.append(ring)
    
    return rings

def create_floating_crystals():
    """Создаем плавающие кристаллы"""
    print("💎 Создание плавающих кристаллов...")
    crystals = []
    
    for i in range(12):
        # Случайная позиция на сфере
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = random.uniform(0, math.pi)
        radius = random.uniform(6, 10)
        
        x = radius * math.sin(angle2) * math.cos(angle1)
        y = radius * math.sin(angle2) * math.sin(angle1)
        z = radius * math.cos(angle2)
        
        # Создаем октаэдр
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.3, 0.8),
            location=(x, y, z)
        )
        crystal = bpy.context.active_object
        crystal.name = f"FloatingCrystal_{i+1}"
        
        # Случайный поворот
        crystal.rotation_euler = (
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi),
            random.uniform(0, 2 * math.pi)
        )
        
        # Материал
        mat = bpy.data.materials.new(name=f"CrystalMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        emission = nodes.new(type='ShaderNodeEmission')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Случайный цвет
        colors = [
            (1.0, 0.3, 0.3),  # Красный
            (0.3, 1.0, 0.3),  # Зеленый
            (0.3, 0.3, 1.0),  # Синий
            (1.0, 1.0, 0.3),  # Желтый
            (1.0, 0.3, 1.0),  # Магента
            (0.3, 1.0, 1.0),  # Циан
        ]
        
        color = random.choice(colors)
        emission.inputs['Color'].default_value = (*color, 1.0)
        emission.inputs['Strength'].default_value = random.uniform(2.0, 5.0)
        
        mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        crystal.data.materials.append(mat)
        crystals.append(crystal)
    
    return crystals

def create_energy_spheres():
    """Создаем энергетические сферы"""
    print("⚡ Создание энергетических сфер...")
    spheres = []
    
    for i in range(8):
        # Расположение по кругу
        angle = i * 45 * math.pi / 180
        radius = 7.0
        height = random.uniform(-1, 3)
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=random.uniform(0.4, 0.8),
            location=(x, y, z)
        )
        sphere = bpy.context.active_object
        sphere.name = f"EnergySphere_{i+1}"
        
        # Материал с анимированной текстурой
        mat = bpy.data.materials.new(name=f"SphereMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Wave texture для анимации
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-400, 200)
        wave.inputs['Scale'].default_value = 15.0
        wave.inputs['Distortion'].default_value = 1.5
        
        # Color ramp
        wave_ramp = nodes.new(type='ShaderNodeValToRGB')
        wave_ramp.location = (-200, 200)
        wave_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        wave_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        
        # Emission
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 200)
        
        # Mix shader
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (200, 0)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        # Соединяем
        links.new(wave.outputs['Color'], wave_ramp.inputs['Fac'])
        links.new(wave_ramp.outputs['Color'], emission.inputs['Color'])
        links.new(wave_ramp.outputs['Color'], mix_shader.inputs['Fac'])
        links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
        links.new(emission.outputs['Emission'], mix_shader.inputs[2])
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        # Настройки
        emission.inputs['Strength'].default_value = 4.0
        bsdf.inputs['Transmission'].default_value = 0.8
        bsdf.inputs['IOR'].default_value = 1.4
        
        # Разные цвета
        colors = [
            (1.0, 0.2, 0.2),  # Красный
            (0.2, 1.0, 0.2),  # Зеленый
            (0.2, 0.2, 1.0),  # Синий
            (1.0, 1.0, 0.2),  # Желтый
            (1.0, 0.2, 1.0),  # Магента
            (0.2, 1.0, 1.0),  # Циан
            (1.0, 0.5, 0.2),  # Оранжевый
            (0.5, 0.2, 1.0),  # Фиолетовый
        ]
        
        emission.inputs['Color'].default_value = (*colors[i], 1.0)
        bsdf.inputs['Base Color'].default_value = (*colors[i], 1.0)
        
        sphere.data.materials.append(mat)
        spheres.append(sphere)
    
    return spheres

def create_geometric_structures():
    """Создаем геометрические структуры"""
    print("🔷 Создание геометрических структур...")
    structures = []
    
    # Куб
    bpy.ops.mesh.primitive_cube_add(
        size=1.5,
        location=(3, 3, 2)
    )
    cube = bpy.context.active_object
    cube.name = "GeometricCube"
    
    # Цилиндр
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.8,
        depth=3.0,
        location=(-3, 3, 1.5)
    )
    cylinder = bpy.context.active_object
    cylinder.name = "GeometricCylinder"
    
    # Конус
    bpy.ops.mesh.primitive_cone_add(
        radius1=1.0,
        radius2=0.0,
        depth=2.5,
        location=(3, -3, 1.25)
    )
    cone = bpy.context.active_object
    cone.name = "GeometricCone"
    
    # Тор
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.2,
        minor_radius=0.3,
        location=(-3, -3, 1.2)
    )
    torus = bpy.context.active_object
    torus.name = "GeometricTorus"
    
    # Материалы для геометрических фигур
    geometric_objects = [cube, cylinder, cone, torus]
    geometric_colors = [
        (0.8, 0.2, 0.8),  # Фиолетовый
        (0.2, 0.8, 0.8),  # Бирюзовый
        (0.8, 0.8, 0.2),  # Желтый
        (0.8, 0.4, 0.2),  # Оранжевый
    ]
    
    for i, obj in enumerate(geometric_objects):
        mat = bpy.data.materials.new(name=f"GeometricMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        
        bsdf.inputs['Base Color'].default_value = (*geometric_colors[i], 1.0)
        bsdf.inputs['Metallic'].default_value = 0.7
        bsdf.inputs['Roughness'].default_value = 0.2
        
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        obj.data.materials.append(mat)
        structures.append(obj)
    
    return structures

def create_lighting_system():
    """Создаем систему освещения"""
    print("💡 Создание системы освещения...")
    
    # Основной свет
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    sun = bpy.context.active_object
    sun.name = "MainSun"
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.95, 0.8)
    
    # Точечные источники света
    light_positions = [
        (8, 8, 8),
        (-8, 8, 8),
        (8, -8, 8),
        (-8, -8, 8),
        (0, 0, 12),
    ]
    
    light_colors = [
        (1.0, 0.5, 0.3),  # Теплый
        (0.3, 0.5, 1.0),  # Холодный
        (0.5, 1.0, 0.3),  # Зеленый
        (1.0, 0.3, 0.8),  # Розовый
        (1.0, 1.0, 0.5),  # Желтый
    ]
    
    for i, (pos, color) in enumerate(zip(light_positions, light_colors)):
        bpy.ops.object.light_add(type='POINT', location=pos)
        light = bpy.context.active_object
        light.name = f"PointLight_{i+1}"
        light.data.energy = 200.0
        light.data.color = color
        light.data.shadow_soft_size = 2.0

def setup_camera_and_render():
    """Настраиваем камеру и рендер"""
    print("📷 Настройка камеры и рендера...")
    
    # Камера
    if "Camera" in bpy.data.objects:
        camera = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
    
    camera.location = (15, -15, 10)
    camera.rotation_euler = (1.0, 0, 0.785)
    
    # Настройки рендера
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True
    
    # Дополнительные настройки
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.view_settings.look = 'Medium High Contrast'
    
    # World settings
    world = scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes
    world_nodes.clear()
    
    env_tex = world_nodes.new(type='ShaderNodeTexEnvironment')
    world_bg = world_nodes.new(type='ShaderNodeBackground')
    world_output = world_nodes.new(type='ShaderNodeOutputWorld')
    
    world_bg.inputs['Strength'].default_value = 0.2
    world.node_tree.links.new(env_tex.outputs['Color'], world_bg.inputs['Color'])
    world.node_tree.links.new(world_bg.outputs['Background'], world_output.inputs['Surface'])

# Создаем всю композицию
print("🎨 Создание сложного объекта...")

core = create_central_core()
rings = create_orbital_rings()
crystals = create_floating_crystals()
spheres = create_energy_spheres()
structures = create_geometric_structures()

create_lighting_system()
setup_camera_and_render()

# Сохраняем сцену
bpy.ops.wm.save_as_mainfile(filepath="output/blender/complex_object_scene.blend")

print("✨ Сложный объект создан!")
print("🎨 Композиция содержит:")
print("   - 🔮 Центральное ядро (икосаэдр)")
print("   - 🔄 5 орбитальных металлических колец")
print("   - 💎 12 плавающих светящихся кристаллов")
print("   - ⚡ 8 энергетических сфер с анимированными текстурами")
print("   - 🔷 4 геометрические фигуры (куб, цилиндр, конус, тор)")
print("   - 💡 6 источников света")
print("   - 📷 Профессиональные настройки рендера")

print("🎯 Готово к рендерингу! F12 для рендера.")
'''
    return script

def run_complex_object():
    """Запускаем создание сложного объекта"""
    script_content = create_complex_object_script()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🎨 Создание сложного объекта с множественными фигурами...")
        print("🚀 Открытие Blender...")
        
        # Запускаем Blender
        subprocess.Popen([
            blender_path,
            "--python", script_path
        ])
        
        print("✨ Blender открыт!")
        print("🎨 Создается эпичная композиция:")
        print("   - 🔮 Центральное ядро с displacement")
        print("   - 🔄 5 орбитальных колец разных металлов")
        print("   - 💎 12 светящихся кристаллов")
        print("   - ⚡ 8 энергетических сфер с волновыми текстурами")
        print("   - 🔷 4 геометрические фигуры")
        print("   - 💡 6 источников света")
        print("   - 🎭 Cycles рендер с denoising")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print(f"📝 Скрипт: {script_path}")

if __name__ == "__main__":
    print("🔮 Сложный объект с множественными фигурами")
    print("=" * 50)
    
    run_complex_object()
    
    print("\n✨ Наслаждайтесь эпичной композицией!") 