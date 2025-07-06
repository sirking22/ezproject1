#!/usr/bin/env python3
"""
Создание сложной магической сцены с продвинутыми текстурами
"""

import subprocess
import tempfile
from pathlib import Path

def create_complex_script():
    """Создает скрипт для сложной магической сцены"""
    script = '''
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# Очищаем сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_complex_crystal():
    """Создаем сложный кристалл с множественными гранями"""
    
    # Создаем базовый кристалл
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=3,
        radius=2.0,
        location=(0, 0, 0)
    )
    crystal = bpy.context.active_object
    crystal.name = "ComplexCrystal"
    
    # Переходим в режим редактирования
    bpy.context.view_layer.objects.active = crystal
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Получаем bmesh
    bm = bmesh.from_mesh(crystal.data)
    
    # Создаем случайные выступы и впадины
    for v in bm.verts:
        # Добавляем шум к позиции
        noise = random.uniform(-0.3, 0.3)
        v.co += v.normal * noise
    
    # Обновляем mesh
    bmesh.update_edit_mesh(crystal.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Создаем сложный материал с шейдерами
    mat = bpy.data.materials.new(name="ComplexCrystal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Noise texture для поверхности
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    noise_tex.location = (-400, 200)
    noise_tex.inputs['Scale'].default_value = 10.0
    noise_tex.inputs['Detail'].default_value = 8.0
    
    # Color ramp для контроля шума
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 200)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # Musgrave texture для внутренней структуры
    musgrave = nodes.new(type='ShaderNodeTexMusgrave')
    musgrave.location = (-400, 0)
    musgrave.inputs['Scale'].default_value = 5.0
    musgrave.inputs['Detail'].default_value = 10.0
    
    # Mix RGB для комбинирования текстур
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (-200, 0)
    mix_rgb.blend_type = 'MULTIPLY'
    
    # Gradient texture для цветового перехода
    gradient = nodes.new(type='ShaderNodeTexGradient')
    gradient.location = (-400, -200)
    
    # Color ramp для градиента
    gradient_ramp = nodes.new(type='ShaderNodeValToRGB')
    gradient_ramp.location = (-200, -200)
    gradient_ramp.color_ramp.elements[0].color = (0.1, 0.3, 0.8, 1.0)  # Темно-синий
    gradient_ramp.color_ramp.elements[1].color = (0.8, 0.9, 1.0, 1.0)  # Светло-голубой
    
    # Emission для внутреннего свечения
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 200)
    emission.inputs['Color'].default_value = (0.5, 0.8, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 2.0
    
    # Mix shader для комбинирования BSDF и emission
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    mix_shader.location = (200, 0)
    mix_shader.inputs['Fac'].default_value = 0.3
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Соединяем ноды
    links.new(noise_tex.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(musgrave.outputs['Fac'], mix_rgb.inputs[1])
    links.new(color_ramp.outputs['Color'], mix_rgb.inputs[2])
    links.new(gradient.outputs['Color'], gradient_ramp.inputs['Fac'])
    links.new(gradient_ramp.outputs['Color'], mix_rgb.inputs[1])
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    # Настройки материала
    bsdf.inputs['Transmission'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.5
    bsdf.inputs['Metallic'].default_value = 0.1
    
    crystal.data.materials.append(mat)
    return crystal

def create_organic_base():
    """Создаем органическое основание"""
    
    # Создаем базовую форму
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=8.0,
        depth=2.0,
        location=(0, 0, -3)
    )
    base = bpy.context.active_object
    base.name = "OrganicBase"
    
    # Добавляем модификатор subdivision surface
    subsurf = base.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Добавляем displacement
    displace = base.modifiers.new(name="Displacement", type='DISPLACE')
    
    # Создаем текстуру для displacement
    tex = bpy.data.textures.new("BaseDisplacement", type='VORONOI')
    tex.noise_scale = 2.0
    tex.contrast = 1.5
    displace.texture = tex
    displace.strength = 0.5
    
    # Материал для основания
    mat = bpy.data.materials.new(name="OrganicBase")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Voronoi texture для органической текстуры
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (-400, 200)
    voronoi.inputs['Scale'].default_value = 8.0
    
    # Noise texture для деталей
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 12.0
    
    # Mix RGB
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (-200, 100)
    mix_rgb.blend_type = 'MULTIPLY'
    
    # Color ramp
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, -100)
    color_ramp.color_ramp.elements[0].color = (0.1, 0.05, 0.02, 1.0)  # Темно-коричневый
    color_ramp.color_ramp.elements[1].color = (0.3, 0.2, 0.1, 1.0)    # Светло-коричневый
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Соединяем
    links.new(voronoi.outputs['Distance'], mix_rgb.inputs[1])
    links.new(noise.outputs['Color'], mix_rgb.inputs[2])
    links.new(mix_rgb.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    base.data.materials.append(mat)
    return base

def create_floating_particles():
    """Создаем систему плавающих частиц"""
    particles = []
    
    for i in range(50):
        # Случайная позиция в сфере
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = random.uniform(0, math.pi)
        radius = random.uniform(3, 12)
        
        x = radius * math.sin(angle2) * math.cos(angle1)
        y = radius * math.sin(angle2) * math.sin(angle1)
        z = radius * math.cos(angle2)
        
        # Создаем маленькую сферу
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=random.uniform(0.05, 0.2),
            location=(x, y, z)
        )
        particle = bpy.context.active_object
        particle.name = f"Particle_{i+1}"
        
        # Случайный размер
        scale = random.uniform(0.5, 2.0)
        particle.scale = (scale, scale, scale)
        
        # Материал для частицы
        mat = bpy.data.materials.new(name=f"ParticleMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Emission
        emission = nodes.new(type='ShaderNodeEmission')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Случайный цвет
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
        
        color = random.choice(colors)
        emission.inputs['Color'].default_value = (*color, 1.0)
        emission.inputs['Strength'].default_value = random.uniform(1.0, 5.0)
        
        nodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        particle.data.materials.append(mat)
        
        particles.append(particle)
    
    return particles

def create_energy_rings():
    """Создаем сложные энергетические кольца"""
    rings = []
    
    for i in range(6):
        # Создаем тор
        bpy.ops.mesh.primitive_torus_add(
            major_radius=4.0 + i * 1.5,
            minor_radius=0.3,
            major_segments=64,
            minor_segments=16,
            location=(0, 0, 2 + i * 0.8)
        )
        ring = bpy.context.active_object
        ring.name = f"EnergyRing_{i+1}"
        
        # Наклон и поворот
        ring.rotation_euler = (
            math.radians(15 + i * 10),
            math.radians(i * 30),
            math.radians(i * 45)
        )
        
        # Сложный материал
        mat = bpy.data.materials.new(name=f"RingMaterial_{i}")
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
        wave.inputs['Scale'].default_value = 20.0
        wave.inputs['Distortion'].default_value = 2.0
        
        # Color ramp для волн
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
        emission.inputs['Strength'].default_value = 3.0
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.1
        
        # Разные цвета для колец
        colors = [
            (1.0, 0.8, 0.2),  # Золото
            (0.9, 0.9, 0.9),  # Серебро
            (0.8, 0.4, 0.1),  # Медь
            (0.6, 0.3, 0.8),  # Фиолетовый
            (0.2, 0.8, 0.8),  # Бирюзовый
            (0.8, 0.2, 0.8),  # Розовый
        ]
        
        emission.inputs['Color'].default_value = (*colors[i], 1.0)
        bsdf.inputs['Base Color'].default_value = (*colors[i], 1.0)
        
        ring.data.materials.append(mat)
        rings.append(ring)
    
    return rings

def create_lighting_setup():
    """Создаем сложную систему освещения"""
    
    # Удаляем стандартный свет
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Основной свет
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.95, 0.8)
    
    # Дополнительные источники света
    light_positions = [
        (5, -5, 8),
        (-5, 5, 8),
        (0, 10, 5),
        (10, 0, 5),
        (-10, 0, 5),
        (0, -10, 5)
    ]
    
    light_colors = [
        (1.0, 0.5, 0.3),  # Теплый
        (0.3, 0.5, 1.0),  # Холодный
        (0.5, 1.0, 0.3),  # Зеленый
        (1.0, 0.3, 0.8),  # Розовый
        (0.8, 0.8, 0.3),  # Желтый
        (0.3, 0.8, 0.8),  # Голубой
    ]
    
    for i, (pos, color) in enumerate(zip(light_positions, light_colors)):
        bpy.ops.object.light_add(type='POINT', location=pos)
        light = bpy.context.active_object
        light.name = f"PointLight_{i+1}"
        light.data.energy = 100.0
        light.data.color = color
        light.data.shadow_soft_size = 2.0

def setup_camera_and_render():
    """Настраиваем камеру и рендер"""
    
    # Камера
    if "Camera" in bpy.data.objects:
        camera = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
    
    camera.location = (12, -12, 8)
    camera.rotation_euler = (1.0, 0, 0.785)
    
    # Настройки рендера
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True
    
    # Дополнительные настройки Cycles
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.use_motion_blur = True
    scene.view_settings.look = 'Medium High Contrast'
    
    # World settings
    world = scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes
    world_nodes.clear()
    
    # Environment texture
    env_tex = world_nodes.new(type='ShaderNodeTexEnvironment')
    world_bg = world_nodes.new(type='ShaderNodeBackground')
    world_output = world_nodes.new(type='ShaderNodeOutputWorld')
    
    world_bg.inputs['Strength'].default_value = 0.3
    world.node_tree.links.new(env_tex.outputs['Color'], world_bg.inputs['Color'])
    world.node_tree.links.new(world_bg.outputs['Background'], world_output.inputs['Surface'])

# Создаем всю сцену
print("Создание сложного кристалла...")
crystal = create_complex_crystal()

print("Создание органического основания...")
base = create_organic_base()

print("Создание плавающих частиц...")
particles = create_floating_particles()

print("Создание энергетических колец...")
rings = create_energy_rings()

print("Настройка освещения...")
create_lighting_setup()

print("Настройка камеры и рендера...")
setup_camera_and_render()

# Сохраняем сцену
bpy.ops.wm.save_as_mainfile(filepath="output/blender/complex_magical_scene.blend")

print("✨ Сложная магическая сцена создана!")
print("🎨 Сцена содержит:")
print("   - 💎 Сложный кристалл с шумовыми текстурами")
print("   - 🌱 Органическое основание с displacement")
print("   - ✨ 50 плавающих частиц")
print("   - 🔄 6 анимированных энергетических колец")
print("   - 💡 7 источников света")
print("   - 📷 Профессиональные настройки рендера")

print("🎯 Готово к рендерингу! Нажмите F12 для рендера.")
'''
    return script

def run_complex_scene():
    """Запускаем создание сложной сцены"""
    script_content = create_complex_script()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Создаем output директорию
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🎇 Создание сложной магической сцены...")
        print("🚀 Открытие Blender с продвинутыми текстурами...")
        
        # Запускаем Blender
        subprocess.Popen([
            blender_path,
            "--python", script_path
        ])
        
        print("✨ Blender открыт!")
        print("🎨 Создается эпичная сцена с:")
        print("   - 🔮 Сложный кристалл с шумовыми текстурами")
        print("   - 🌱 Органическое основание с displacement")
        print("   - ✨ 50 светящихся частиц")
        print("   - 🔄 6 анимированных колец")
        print("   - 💡 Профессиональное освещение")
        print("   - 🎭 Cycles рендер с denoising")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print(f"📝 Скрипт: {script_path}")

if __name__ == "__main__":
    print("🔮 Сложная магическая сцена")
    print("=" * 50)
    
    run_complex_scene()
    
    print("\n✨ Наслаждайтесь эпичной сценой!") 