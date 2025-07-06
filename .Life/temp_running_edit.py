
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

print("🔧 Редактирование запущенного Blender...")

# Получаем все объекты в сцене
all_objects = list(bpy.data.objects)
print(f"📦 Найдено объектов: {len(all_objects)}")

# Анализируем что у нас есть
crystals = [obj for obj in all_objects if "crystal" in obj.name.lower()]
spheres = [obj for obj in all_objects if "sphere" in obj.name.lower()]
rings = [obj for obj in all_objects if "ring" in obj.name.lower()]
lights = [obj for obj in all_objects if obj.type == 'LIGHT']

print(f"💎 Кристаллов: {len(crystals)}")
print(f"⚡ Сфер: {len(spheres)}")
print(f"🔄 Колец: {len(rings)}")
print(f"💡 Источников света: {len(lights)}")

# Улучшаем существующие объекты
def enhance_crystal(crystal):
    """Улучшаем кристалл"""
    print(f"✨ Улучшаем кристалл: {crystal.name}")
    
    # Добавляем subdivision surface если нет
    if "Subdivision" not in [mod.name for mod in crystal.modifiers]:
        subsurf = crystal.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 3
    
    # Добавляем displacement
    if "Displacement" not in [mod.name for mod in crystal.modifiers]:
        displace = crystal.modifiers.new(name="Displacement", type='DISPLACE')
        tex = bpy.data.textures.new(f"{crystal.name}_Displacement", type='VORONOI')
        tex.noise_scale = 2.0
        displace.texture = tex
        displace.strength = 0.2
    
    # Улучшаем материал
    if crystal.data.materials:
        mat = crystal.data.materials[0]
    else:
        mat = bpy.data.materials.new(name=f"{crystal.name}_Enhanced")
        crystal.data.materials.append(mat)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Очищаем и создаем новый материал
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Noise texture
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 200)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 8.0
    
    # Color ramp
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 200)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # Emission
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 200)
    emission.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 2.0
    
    # Mix shader
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    mix_shader.location = (200, 0)
    mix_shader.inputs['Fac'].default_value = 0.3
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Соединяем
    links.new(noise.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    # Настройки
    bsdf.inputs['Base Color'].default_value = (0.6, 0.8, 1.0, 1.0)
    bsdf.inputs['Transmission'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.5

def enhance_sphere(sphere):
    """Улучшаем сферу"""
    print(f"⚡ Улучшаем сферу: {sphere.name}")
    
    # Улучшаем материал
    if sphere.data.materials:
        mat = sphere.data.materials[0]
    else:
        mat = bpy.data.materials.new(name=f"{sphere.name}_Enhanced")
        sphere.data.materials.append(mat)
    
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
    emission.inputs['Strength'].default_value = 5.0
    bsdf.inputs['Transmission'].default_value = 0.9
    bsdf.inputs['IOR'].default_value = 1.4

def enhance_ring(ring):
    """Улучшаем кольцо"""
    print(f"🔄 Улучшаем кольцо: {ring.name}")
    
    # Добавляем subdivision surface
    if "Subdivision" not in [mod.name for mod in ring.modifiers]:
        subsurf = ring.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 1
        subsurf.render_levels = 2
    
    # Улучшаем материал
    if ring.data.materials:
        mat = ring.data.materials[0]
    else:
        mat = bpy.data.materials.new(name=f"{ring.name}_Enhanced")
        ring.data.materials.append(mat)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Улучшенные металлические настройки
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Clearcoat'].default_value = 1.0
    bsdf.inputs['Clearcoat Roughness'].default_value = 0.1
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Применяем улучшения
print("🔧 Применяем улучшения...")

for crystal in crystals:
    enhance_crystal(crystal)

for sphere in spheres:
    enhance_sphere(sphere)

for ring in rings:
    enhance_ring(ring)

# Добавляем новые элементы
print("✨ Добавляем новые элементы...")

# Создаем дополнительные частицы
for i in range(15):
    angle = i * 24 * math.pi / 180
    radius = 8.0 + random.uniform(-2, 2)
    height = random.uniform(-3, 5)
    
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = height
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=random.uniform(0.05, 0.15),
        location=(x, y, z)
    )
    particle = bpy.context.active_object
    particle.name = f"ExtraParticle_{i+1}"
    
    # Светящийся материал
    mat = bpy.data.materials.new(name=f"ParticleMat_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
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
    ]
    
    color = random.choice(colors)
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = random.uniform(1.0, 3.0)
    
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    particle.data.materials.append(mat)

# Создаем энергетические лучи
for i in range(8):
    angle = i * 45 * math.pi / 180
    radius = 6.0
    
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=4.0,
        location=(x, y, 0)
    )
    ray = bpy.context.active_object
    ray.name = f"EnergyRay_{i+1}"
    
    # Поворачиваем к центру
    direction = Vector((-x, -y, 0)).normalized()
    ray.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Светящийся материал
    mat = bpy.data.materials.new(name=f"RayMat_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    emission = nodes.new(type='ShaderNodeEmission')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    emission.inputs['Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 3.0
    
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    ray.data.materials.append(mat)

# Улучшаем освещение
print("💡 Улучшаем освещение...")

# Добавляем дополнительные источники света
extra_lights = [
    (6, 6, 6),
    (-6, 6, 6),
    (6, -6, 6),
    (-6, -6, 6),
]

for i, pos in enumerate(extra_lights):
    bpy.ops.object.light_add(type='POINT', location=pos)
    light = bpy.context.active_object
    light.name = f"ExtraLight_{i+1}"
    light.data.energy = 100.0
    light.data.color = (0.8, 0.9, 1.0)

# Настраиваем рендер
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512  # Увеличиваем качество
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'

print("✅ Редактирование завершено!")
print("🎨 Улучшения:")
print("   - 💎 Кристаллы получили displacement и subdivision")
print("   - ⚡ Сферы получили анимированные wave текстуры")
print("   - 🔄 Кольца получили subdivision и clearcoat")
print("   - ✨ Добавлено 15 новых частиц")
print("   - 🌟 Добавлено 8 энергетических лучей")
print("   - 💡 Добавлено 4 дополнительных источника света")
print("   - 🎭 Улучшены настройки рендера (512 сэмплов)")
print("")
print("🎯 Готово к рендерингу! F12 для рендера.")

# Сохраняем отредактированную сцену
bpy.ops.wm.save_as_mainfile(filepath="output/blender/edited_running_scene.blend")
print("💾 Отредактированная сцена сохранена: output/blender/edited_running_scene.blend")
