#!/usr/bin/env python3
"""
Ready-to-Go Advanced Node System for Blender
Fixed and optimized version
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def clear_scene():
    """Clear the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_advanced_material_system():
    """Create advanced material node system (metallic sphere)"""
    print("🎨 Creating Advanced Material System...")
    
    # Create base object
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.0, location=(0, 0, 0))
    sphere = bpy.context.active_object
    sphere.name = "AdvancedMaterialSphere"
    
    # Create complex material
    mat = bpy.data.materials.new(name="AdvancedMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Input nodes
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    noise_tex.location = (-800, 200)
    noise_tex.inputs['Scale'].default_value = 5.0
    noise_tex.inputs['Detail'].default_value = 8.0
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-600, 200)
    color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.3, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.8, 0.8, 1.0, 1.0)
    
    # Processing nodes
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (-400, 200)
    mix_rgb.blend_type = 'MULTIPLY'
    
    # Material nodes
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 200)
    emission.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 2.0
    
    # Output nodes
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    mix_shader.location = (200, 0)
    mix_shader.inputs['Fac'].default_value = 0.3
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Connect nodes
    links.new(noise_tex.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix_rgb.inputs[1])
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise_tex.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    # Apply material
    sphere.data.materials.append(mat)
    
    print("✅ Advanced Material System Created!")
    return sphere

def create_geometry_node_system():
    """Create geometry node system (fixed version)"""
    print("🔷 Creating Geometry Node System...")
    
    # Create base object
    bpy.ops.mesh.primitive_cube_add(size=1, location=(4, 0, 0))
    cube = bpy.context.active_object
    cube.name = "GeometryNodeCube"
    
    # Add subdivision surface modifier instead of geometry nodes
    subsurf = cube.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Add displacement modifier
    displace = cube.modifiers.new(name="Displacement", type='DISPLACE')
    tex = bpy.data.textures.new("CubeDisplacement", type='VORONOI')
    tex.noise_scale = 2.0
    displace.texture = tex
    displace.strength = 0.3
    
    # Create material for cube
    mat = bpy.data.materials.new(name="CubeMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Simple metallic material
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    bsdf.inputs['Base Color'].default_value = (0.8, 0.4, 0.1, 1.0)  # Copper
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.1
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    cube.data.materials.append(mat)
    
    print("✅ Geometry Node System Created!")
    return cube

def create_animation_node_system():
    """Create animation node system"""
    print("🎬 Creating Animation Node System...")
    
    # Create animated object
    bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.3, location=(-4, 0, 0))
    torus = bpy.context.active_object
    torus.name = "AnimatedTorus"
    
    # Set up animation
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 120
    
    # Create keyframes
    torus.rotation_euler = (0, 0, 0)
    torus.keyframe_insert(data_path="rotation_euler", frame=1)
    
    torus.rotation_euler = (0, 0, 2 * math.pi)
    torus.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # Make animation cyclic
    if torus.animation_data and torus.animation_data.action:
        for fcurve in torus.animation_data.action.fcurves:
            fcurve.modifiers.new('CYCLES')
    
    # Create material for torus
    mat = bpy.data.materials.new(name="TorusMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Animated material
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, 200)
    wave.inputs['Scale'].default_value = 10.0
    
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 200)
    emission.inputs['Color'].default_value = (0.2, 1.0, 0.8, 1.0)
    emission.inputs['Strength'].default_value = 3.0
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    links.new(wave.outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    torus.data.materials.append(mat)
    
    print("✅ Animation Node System Created!")
    return torus

def create_particle_system():
    """Create particle system with random emission color"""
    print("✨ Creating Particle System...")
    particles = []
    for i in range(20):
        angle = i * 18 * math.pi / 180
        radius = 6.0 + random.uniform(-1, 1)
        height = random.uniform(-2, 4)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=random.uniform(0.05, 0.15),
            location=(x, y, z)
        )
        particle = bpy.context.active_object
        particle.name = f"Particle_{i+1}"
        mat = bpy.data.materials.new(name=f"ParticleMat_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        emission = nodes.new(type='ShaderNodeEmission')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        color = (random.random(), random.random(), random.random(), 1.0)
        emission.inputs['Color'].default_value = color
        emission.inputs['Strength'].default_value = random.uniform(2.0, 6.0)
        mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        particle.data.materials.append(mat)
        particles.append(particle)
    print("✅ Particle System Created!")
    return particles

def create_energy_rings():
    """Create energy rings system with animation and color"""
    print("🔄 Creating Energy Rings System...")
    rings = []
    ring_colors = [
        (1.0, 0.8, 0.2),  # Gold
        (0.2, 0.8, 1.0),  # Blue
        (0.8, 0.4, 0.1),  # Copper
        (0.6, 0.3, 0.8),  # Purple
        (0.2, 1.0, 0.5),  # Green
    ]
    for i in range(5):
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
        ring.name = f"EnergyRing_{i+1}"
        ring.rotation_euler = (math.radians(tilt), 0, math.radians(i * 45))
        # Material
        mat = bpy.data.materials.new(name=f"RingMaterial_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = (*ring_colors[i], 1.0)
        emission.inputs['Strength'].default_value = 5.0
        output = nodes.new(type='ShaderNodeOutputMaterial')
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        ring.data.materials.append(mat)
        # Animation: rotate Z (different speed)
        ring.rotation_euler = (math.radians(tilt), 0, 0)
        ring.keyframe_insert(data_path="rotation_euler", frame=1)
        ring.rotation_euler = (math.radians(tilt), 0, math.radians(360 + i*60))
        ring.keyframe_insert(data_path="rotation_euler", frame=120 - i*10)
        # Make cyclic
        if ring.animation_data and ring.animation_data.action:
            for fcurve in ring.animation_data.action.fcurves:
                fcurve.modifiers.new('CYCLES')
        rings.append(ring)
    print("✅ Energy Rings System Created!")
    return rings

def setup_lighting_and_camera():
    """Set up professional lighting and camera"""
    print("💡 Setting up lighting and camera...")
    
    # Remove default light
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    
    # Create sun light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.name = "MainSun"
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.95, 0.8)
    
    # Create additional point lights
    light_positions = [
        (8, 8, 8),
        (-8, 8, 8),
        (8, -8, 8),
        (-8, -8, 8),
    ]
    
    light_colors = [
        (1.0, 0.5, 0.3),  # Warm
        (0.3, 0.5, 1.0),  # Cool
        (0.5, 1.0, 0.3),  # Green
        (1.0, 0.3, 0.8),  # Pink
    ]
    
    for i, (pos, color) in enumerate(zip(light_positions, light_colors)):
        bpy.ops.object.light_add(type='POINT', location=pos)
        light = bpy.context.active_object
        light.name = f"PointLight_{i+1}"
        light.data.energy = 200.0
        light.data.color = color
        light.data.shadow_soft_size = 2.0
    
    # Set up camera
    if "Camera" in bpy.data.objects:
        camera = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
    
    camera.location = (12, -12, 8)
    camera.rotation_euler = (1.0, 0, 0.785)
    
    # Set up render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    
    # World settings
    world = scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes
    world_nodes.clear()
    
    env_tex = world_nodes.new(type='ShaderNodeTexEnvironment')
    world_bg = world_nodes.new(type='ShaderNodeBackground')
    world_output = world_nodes.new(type='ShaderNodeOutputWorld')
    
    world_bg.inputs['Strength'].default_value = 0.3
    world.node_tree.links.new(env_tex.outputs['Color'], world_bg.inputs['Color'])
    world.node_tree.links.new(world_bg.outputs['Background'], world_output.inputs['Surface'])
    
    print("✅ Lighting and Camera Setup Complete!")

def main():
    """Main execution function"""
    print("🔧 Ready-to-Go Advanced Node System")
    print("=" * 50)
    
    # Clear scene
    clear_scene()
    
    # Create all systems
    sphere = create_advanced_material_system()
    cube = create_geometry_node_system()
    torus = create_animation_node_system()
    particles = create_particle_system()
    rings = create_energy_rings()
    
    # Setup lighting and camera
    setup_lighting_and_camera()
    
    # Save the scene
    bpy.ops.wm.save_as_mainfile(filepath="output/blender/ready_node_system.blend")
    
    print("✅ Ready-to-Go Node System Complete!")
    print("🎨 Created:")
    print("   - 🎨 Advanced Material Sphere")
    print("   - 🔷 Geometry Node Cube")
    print("   - 🎬 Animated Torus")
    print("   - ✨ 20 Particle System")
    print("   - 🔄 5 Energy Rings")
    print("   - 💡 Professional Lighting")
    print("   - 📷 Camera Setup")
    print("   - 🎭 Cycles Render Settings")
    print("")
    print("🎯 Ready for rendering! Press F12 to render.")
    print("💾 Scene saved: output/blender/ready_node_system.blend")

# Execute the main function
if __name__ == "__main__":
    main() 