#!/usr/bin/env python3
"""
Редактирование уже открытого Blender через Python API
"""

import socket
import json
import time
from pathlib import Path

def send_to_blender(script_content):
    """Отправляем скрипт в уже открытый Blender через socket"""
    
    # Создаем временный файл со скриптом
    script_path = Path("temp_blender_script.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📝 Скрипт сохранен: {script_path}")
    print("🎯 Теперь выполните в Blender:")
    print(f"   - Откройте Text Editor")
    print(f"   - Нажмите 'Open' и выберите: {script_path.absolute()}")
    print(f"   - Нажмите 'Run Script' (Alt+P)")
    print("")
    print("✨ Или скопируйте код ниже в Blender Python Console:")
    print("=" * 50)
    print(script_content)
    print("=" * 50)

def create_edit_script():
    """Создает скрипт для редактирования существующей сцены"""
    script = '''
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

print("🔮 Редактирование существующей сцены...")

# Получаем активный объект (если есть)
active_obj = bpy.context.active_object
if active_obj:
    print(f"📦 Активный объект: {active_obj.name}")
    
    # Если это кристалл - усложняем его
    if "crystal" in active_obj.name.lower() or "sphere" in active_obj.name.lower():
        print("💎 Усложняем кристалл...")
        
        # Переходим в режим редактирования
        bpy.context.view_layer.objects.active = active_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Получаем bmesh
        bm = bmesh.from_mesh(active_obj.data)
        
        # Добавляем детали
        for v in bm.verts:
            # Создаем выступы и впадины
            noise = random.uniform(-0.5, 0.5)
            v.co += v.normal * noise * 0.3
        
        # Обновляем mesh
        bmesh.update_edit_mesh(active_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Улучшаем материал
        if active_obj.data.materials:
            mat = active_obj.data.materials[0]
        else:
            mat = bpy.data.materials.new(name="EnhancedCrystal")
            active_obj.data.materials.append(mat)
        
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Очищаем существующие ноды
        nodes.clear()
        
        # Создаем сложный материал
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Noise texture
        noise_tex = nodes.new(type='ShaderNodeTexNoise')
        noise_tex.location = (-400, 200)
        noise_tex.inputs['Scale'].default_value = 15.0
        noise_tex.inputs['Detail'].default_value = 10.0
        
        # Color ramp
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 200)
        color_ramp.color_ramp.elements[0].position = 0.3
        color_ramp.color_ramp.elements[1].position = 0.7
        
        # Emission
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 200)
        emission.inputs['Color'].default_value = (0.6, 0.8, 1.0, 1.0)
        emission.inputs['Strength'].default_value = 2.5
        
        # Mix shader
        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (200, 0)
        mix_shader.inputs['Fac'].default_value = 0.4
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        # Соединяем
        links.new(noise_tex.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Roughness'])
        links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
        links.new(emission.outputs['Emission'], mix_shader.inputs[2])
        links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
        
        # Настройки
        bsdf.inputs['Base Color'].default_value = (0.7, 0.9, 1.0, 1.0)
        bsdf.inputs['Transmission'].default_value = 0.9
        bsdf.inputs['IOR'].default_value = 1.6
        
        print("✅ Кристалл усложнен!")

# Добавляем новые элементы в сцену
print("✨ Добавляем новые элементы...")

# Создаем плавающие частицы
for i in range(20):
    angle = i * 18 * math.pi / 180  # 18 градусов между частицами
    radius = 6.0 + random.uniform(-1, 1)
    height = random.uniform(-2, 4)
    
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = height
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=random.uniform(0.1, 0.3),
        location=(x, y, z)
    )
    particle = bpy.context.active_object
    particle.name = f"Particle_{i+1}"
    
    # Случайный масштаб
    scale = random.uniform(0.5, 1.5)
    particle.scale = (scale, scale, scale)
    
    # Светящийся материал
    mat = bpy.data.materials.new(name=f"ParticleMat_{i}")
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
    emission.inputs['Strength'].default_value = random.uniform(2.0, 6.0)
    
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    particle.data.materials.append(mat)

# Создаем энергетические кольца
for i in range(3):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=3.0 + i * 1.5,
        minor_radius=0.2,
        major_segments=48,
        minor_segments=12,
        location=(0, 0, 1 + i * 1.2)
    )
    ring = bpy.context.active_object
    ring.name = f"EnergyRing_{i+1}"
    
    # Наклон
    ring.rotation_euler = (math.radians(15 + i * 10), 0, math.radians(i * 30))
    
    # Металлический материал
    mat = bpy.data.materials.new(name=f"RingMat_{i}")
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
    ]
    
    bsdf.inputs['Base Color'].default_value = (*metals[i], 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.1
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    ring.data.materials.append(mat)

# Улучшаем освещение
print("💡 Улучшаем освещение...")

# Добавляем дополнительные источники света
light_positions = [
    (5, 5, 8),
    (-5, -5, 8),
    (8, 0, 5),
    (-8, 0, 5),
]

for i, pos in enumerate(light_positions):
    bpy.ops.object.light_add(type='POINT', location=pos)
    light = bpy.context.active_object
    light.name = f"ExtraLight_{i+1}"
    light.data.energy = 150.0
    light.data.color = (0.8, 0.9, 1.0)

# Настраиваем рендер
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True

print("✅ Сцена улучшена!")
print("🎨 Добавлено:")
print("   - 20 светящихся частиц")
print("   - 3 металлических кольца")
print("   - 4 дополнительных источника света")
print("   - Улучшенные материалы")
print("")
print("🎯 Готово к рендерингу! F12 для рендера.")
'''
    return script

def create_animation_script():
    """Создает скрипт для добавления анимации"""
    script = '''
import bpy
import math

print("🎬 Добавляем анимацию...")

# Устанавливаем длительность анимации
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120  # 5 секунд при 24 fps

# Анимация вращения кристалла
crystal = None
for obj in bpy.data.objects:
    if "crystal" in obj.name.lower() or "sphere" in obj.name.lower():
        crystal = obj
        break

if crystal:
    print(f"🎭 Анимируем кристалл: {crystal.name}")
    
    # Вращение по Z
    crystal.rotation_euler = (0, 0, 0)
    crystal.keyframe_insert(data_path="rotation_euler", frame=1)
    
    crystal.rotation_euler = (0, 0, 2 * math.pi)
    crystal.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # Плавная интерполяция
    for fcurve in crystal.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

# Анимация частиц
particles = [obj for obj in bpy.data.objects if "particle" in obj.name.lower()]
for i, particle in enumerate(particles):
    print(f"✨ Анимируем частицу {i+1}")
    
    # Плавающее движение
    start_pos = particle.location.copy()
    
    # Ключевые кадры
    particle.keyframe_insert(data_path="location", frame=1)
    
    # Случайное движение
    import random
    random.seed(i)  # Для воспроизводимости
    
    for frame in range(30, 121, 30):
        offset = Vector((
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-0.5, 0.5)
        ))
        particle.location = start_pos + offset
        particle.keyframe_insert(data_path="location", frame=frame)
    
    # Возврат в исходную позицию
    particle.location = start_pos
    particle.keyframe_insert(data_path="location", frame=120)
    
    # Плавная интерполяция
    if particle.animation_data and particle.animation_data.action:
        for fcurve in particle.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'

# Анимация колец
rings = [obj for obj in bpy.data.objects if "ring" in obj.name.lower()]
for i, ring in enumerate(rings):
    print(f"🔄 Анимируем кольцо {i+1}")
    
    # Вращение с разной скоростью
    speed = 1 + i * 0.5  # Разная скорость для каждого кольца
    
    ring.rotation_euler = (0, 0, 0)
    ring.keyframe_insert(data_path="rotation_euler", frame=1)
    
    ring.rotation_euler = (0, 0, 2 * math.pi * speed)
    ring.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # Плавная интерполяция
    if ring.animation_data and ring.animation_data.action:
        for fcurve in ring.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

# Анимация интенсивности света
lights = [obj for obj in bpy.data.objects if "light" in obj.name.lower()]
for i, light in enumerate(lights):
    if light.type == 'LIGHT':
        print(f"💡 Анимируем свет {i+1}")
        
        # Пульсация
        light.data.energy = 100
        light.data.keyframe_insert(data_path="energy", frame=1)
        
        light.data.energy = 200
        light.data.keyframe_insert(data_path="energy", frame=60)
        
        light.data.energy = 100
        light.data.keyframe_insert(data_path="energy", frame=120)
        
        # Плавная интерполяция
        if light.data.animation_data and light.data.animation_data.action:
            for fcurve in light.data.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'BEZIER'

print("✅ Анимация добавлена!")
print("🎬 120 кадров (5 секунд)")
print("🎯 Нажмите пробел для воспроизведения")
print("📹 Нажмите Ctrl+F12 для рендера анимации")
'''
    return script

def main():
    """Главная функция"""
    print("🔮 Редактирование существующего Blender")
    print("=" * 50)
    
    print("🎯 Выберите действие:")
    print("1. Улучшить существующую сцену")
    print("2. Добавить анимацию")
    print("3. Оба варианта")
    
    choice = input("Введите номер (1-3): ").strip()
    
    if choice == "1":
        script = create_edit_script()
        send_to_blender(script)
    elif choice == "2":
        script = create_animation_script()
        send_to_blender(script)
    elif choice == "3":
        script = create_edit_script() + "\n\n" + create_animation_script()
        send_to_blender(script)
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    main() 