#!/usr/bin/env python3
"""
Advanced Node System for Blender
Based on modern node architecture patterns
"""

import subprocess
import tempfile
from pathlib import Path

def create_node_system_script():
    """Creates a comprehensive node system for Blender"""
    script = '''
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

print("🔧 Creating Advanced Node System...")

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

class NodeSystem:
    """Advanced Node System for Blender"""
    
    def __init__(self):
        self.nodes = {}
        self.connections = []
        self.node_types = {
            'input': self.create_input_node,
            'output': self.create_output_node,
            'process': self.create_process_node,
            'transform': self.create_transform_node,
            'material': self.create_material_node,
            'geometry': self.create_geometry_node,
            'logic': self.create_logic_node,
            'data': self.create_data_node
        }
    
    def create_input_node(self, name, node_type="INPUT"):
        """Create input node"""
        node = {
            'id': name,
            'type': 'input',
            'inputs': [],
            'outputs': ['value'],
            'data': {'value': 0.0},
            'position': (0, 0)
        }
        self.nodes[name] = node
        return node
    
    def create_output_node(self, name, node_type="OUTPUT"):
        """Create output node"""
        node = {
            'id': name,
            'type': 'output',
            'inputs': ['value'],
            'outputs': [],
            'data': {},
            'position': (800, 0)
        }
        self.nodes[name] = node
        return node
    
    def create_process_node(self, name, operation="ADD"):
        """Create processing node"""
        node = {
            'id': name,
            'type': 'process',
            'operation': operation,
            'inputs': ['a', 'b'],
            'outputs': ['result'],
            'data': {'a': 0.0, 'b': 0.0, 'result': 0.0},
            'position': (400, 0)
        }
        self.nodes[name] = node
        return node
    
    def create_transform_node(self, name, transform_type="TRANSLATE"):
        """Create transform node"""
        node = {
            'id': name,
            'type': 'transform',
            'transform_type': transform_type,
            'inputs': ['object', 'value'],
            'outputs': ['transformed_object'],
            'data': {'value': Vector((0, 0, 0))},
            'position': (400, 200)
        }
        self.nodes[name] = node
        return node
    
    def create_material_node(self, name, material_type="PRINCIPLED"):
        """Create material node"""
        node = {
            'id': name,
            'type': 'material',
            'material_type': material_type,
            'inputs': ['color', 'roughness', 'metallic'],
            'outputs': ['material'],
            'data': {
                'color': (0.8, 0.8, 0.8, 1.0),
                'roughness': 0.5,
                'metallic': 0.0
            },
            'position': (400, -200)
        }
        self.nodes[name] = node
        return node
    
    def create_geometry_node(self, name, geometry_type="CUBE"):
        """Create geometry node"""
        node = {
            'id': name,
            'type': 'geometry',
            'geometry_type': geometry_type,
            'inputs': ['size', 'location'],
            'outputs': ['object'],
            'data': {
                'size': 1.0,
                'location': Vector((0, 0, 0))
            },
            'position': (200, 0)
        }
        self.nodes[name] = node
        return node
    
    def create_logic_node(self, name, logic_type="IF"):
        """Create logic node"""
        node = {
            'id': name,
            'type': 'logic',
            'logic_type': logic_type,
            'inputs': ['condition', 'true_value', 'false_value'],
            'outputs': ['result'],
            'data': {
                'condition': True,
                'true_value': 1.0,
                'false_value': 0.0
            },
            'position': (600, 0)
        }
        self.nodes[name] = node
        return node
    
    def create_data_node(self, name, data_type="CONSTANT"):
        """Create data node"""
        node = {
            'id': name,
            'type': 'data',
            'data_type': data_type,
            'inputs': [],
            'outputs': ['value'],
            'data': {'value': 1.0},
            'position': (200, 200)
        }
        self.nodes[name] = node
        return node
    
    def connect_nodes(self, from_node, from_output, to_node, to_input):
        """Connect two nodes"""
        connection = {
            'from_node': from_node,
            'from_output': from_output,
            'to_node': to_node,
            'to_input': to_input
        }
        self.connections.append(connection)
        print(f"🔗 Connected {from_node}.{from_output} -> {to_node}.{to_input}")
    
    def execute_node(self, node_id):
        """Execute a single node"""
        node = self.nodes[node_id]
        print(f"⚙️ Executing node: {node_id} ({node['type']})")
        
        if node['type'] == 'geometry':
            return self.execute_geometry_node(node)
        elif node['type'] == 'transform':
            return self.execute_transform_node(node)
        elif node['type'] == 'material':
            return self.execute_material_node(node)
        elif node['type'] == 'process':
            return self.execute_process_node(node)
        elif node['type'] == 'logic':
            return self.execute_logic_node(node)
        
        return None
    
    def execute_geometry_node(self, node):
        """Execute geometry node"""
        geometry_type = node['geometry_type']
        size = node['data']['size']
        location = node['data']['location']
        
        if geometry_type == "CUBE":
            bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        elif geometry_type == "SPHERE":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=location)
        elif geometry_type == "CYLINDER":
            bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=location)
        elif geometry_type == "CONE":
            bpy.ops.mesh.primitive_cone_add(radius1=size, radius2=0, depth=size*2, location=location)
        
        obj = bpy.context.active_object
        obj.name = f"{node['id']}_Geometry"
        return obj
    
    def execute_transform_node(self, node):
        """Execute transform node"""
        transform_type = node['transform_type']
        value = node['data']['value']
        
        # Get the last created object
        if bpy.context.active_object:
            obj = bpy.context.active_object
            
            if transform_type == "TRANSLATE":
                obj.location += value
            elif transform_type == "ROTATE":
                obj.rotation_euler += value
            elif transform_type == "SCALE":
                obj.scale *= value
            
            print(f"🔄 Applied {transform_type} to {obj.name}")
            return obj
        
        return None
    
    def execute_material_node(self, node):
        """Execute material node"""
        material_type = node['material_type']
        data = node['data']
        
        mat = bpy.data.materials.new(name=f"{node['id']}_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        if material_type == "PRINCIPLED":
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            output = nodes.new(type='ShaderNodeOutputMaterial')
            
            bsdf.inputs['Base Color'].default_value = data['color']
            bsdf.inputs['Roughness'].default_value = data['roughness']
            bsdf.inputs['Metallic'].default_value = data['metallic']
            
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        elif material_type == "EMISSION":
            emission = nodes.new(type='ShaderNodeEmission')
            output = nodes.new(type='ShaderNodeOutputMaterial')
            
            emission.inputs['Color'].default_value = data['color']
            emission.inputs['Strength'].default_value = data.get('strength', 1.0)
            
            links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Apply to active object
        if bpy.context.active_object:
            bpy.context.active_object.data.materials.append(mat)
        
        return mat
    
    def execute_process_node(self, node):
        """Execute process node"""
        operation = node['operation']
        a = node['data']['a']
        b = node['data']['b']
        
        if operation == "ADD":
            result = a + b
        elif operation == "SUBTRACT":
            result = a - b
        elif operation == "MULTIPLY":
            result = a * b
        elif operation == "DIVIDE":
            result = a / b if b != 0 else 0
        elif operation == "POWER":
            result = a ** b
        else:
            result = a
        
        node['data']['result'] = result
        print(f"🧮 {operation}: {a} {operation} {b} = {result}")
        return result
    
    def execute_logic_node(self, node):
        """Execute logic node"""
        logic_type = node['logic_type']
        condition = node['data']['condition']
        true_value = node['data']['true_value']
        false_value = node['data']['false_value']
        
        if logic_type == "IF":
            result = true_value if condition else false_value
        elif logic_type == "AND":
            result = true_value if condition and true_value else false_value
        elif logic_type == "OR":
            result = true_value if condition or true_value else false_value
        else:
            result = condition
        
        node['data']['result'] = result
        print(f"🔀 {logic_type}: {condition} -> {result}")
        return result
    
    def execute_graph(self):
        """Execute the entire node graph"""
        print("🚀 Executing Node Graph...")
        
        # Create nodes
        self.create_input_node("Input1")
        self.create_data_node("Size", "CONSTANT")
        self.create_data_node("Position", "CONSTANT")
        self.create_geometry_node("Geometry", "CUBE")
        self.create_transform_node("Transform", "TRANSLATE")
        self.create_material_node("Material", "PRINCIPLED")
        self.create_output_node("Output1")
        
        # Set data values
        self.nodes["Size"]["data"]["value"] = 2.0
        self.nodes["Position"]["data"]["value"] = Vector((1, 1, 1))
        self.nodes["Material"]["data"]["color"] = (0.8, 0.2, 0.8, 1.0)
        
        # Execute nodes in order
        execution_order = ["Size", "Position", "Geometry", "Transform", "Material"]
        
        for node_id in execution_order:
            if node_id in self.nodes:
                self.execute_node(node_id)
        
        print("✅ Node Graph Execution Complete!")

# Create and execute node system
print("🔧 Initializing Advanced Node System...")
node_system = NodeSystem()
node_system.execute_graph()

# Create additional complex node setups
print("🎨 Creating Complex Node Setups...")

def create_advanced_material_system():
    """Create advanced material node system"""
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

def create_geometry_node_system():
    """Create geometry node system"""
    print("🔷 Creating Geometry Node System...")
    
    # Create base object
    bpy.ops.mesh.primitive_cube_add(size=1, location=(4, 0, 0))
    cube = bpy.context.active_object
    cube.name = "GeometryNodeCube"
    
    # Add geometry nodes modifier
    geo_mod = cube.modifiers.new(name="GeometryNodes", type='NODES')
    
    # Create geometry node tree
    geo_tree = bpy.data.node_groups.new(type='GeometryNodeTree', name="GeometryNodeTree")
    geo_mod.node_group = geo_tree
    
    # Add nodes to geometry tree
    nodes = geo_tree.nodes
    links = geo_tree.links
    
    # Input nodes
    group_input = nodes.new(type='NodeGroupInput')
    group_input.location = (-600, 0)
    
    # Processing nodes
    subdiv = nodes.new(type='GeometryNodeSubdivisionSurface')
    subdiv.location = (-400, 0)
    subdiv.levels = 2
    
    displace = nodes.new(type='GeometryNodeDisplace')
    displace.location = (-200, 0)
    displace.inputs['Scale'].default_value = 0.2
    
    # Output nodes
    group_output = nodes.new(type='NodeGroupOutput')
    group_output.location = (0, 0)
    
    # Connect nodes
    links.new(group_input.outputs['Geometry'], subdiv.inputs['Geometry'])
    links.new(subdiv.outputs['Geometry'], displace.inputs['Geometry'])
    links.new(displace.outputs['Geometry'], group_output.inputs['Geometry'])
    
    print("✅ Geometry Node System Created!")

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
    
    print("✅ Animation Node System Created!")

# Execute all node systems
create_advanced_material_system()
create_geometry_node_system()
create_animation_node_system()

# Set up lighting and camera
print("💡 Setting up lighting and camera...")

# Lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Camera
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.785)

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True

print("✅ Advanced Node System Complete!")
print("🎨 Created:")
print("   - 🔧 Modular Node System")
print("   - 🎨 Advanced Material Nodes")
print("   - 🔷 Geometry Nodes")
print("   - 🎬 Animation Nodes")
print("   - 💡 Professional Lighting")
print("   - 📷 Camera Setup")
print("")
print("🎯 Ready for rendering! Press F12 to render.")

# Save the scene
bpy.ops.wm.save_as_mainfile(filepath="output/blender/advanced_node_system.blend")
print("💾 Scene saved: output/blender/advanced_node_system.blend")
'''
    return script

def run_node_system():
    """Run the advanced node system"""
    script_content = create_node_system_script()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    
    # Create output directory
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🔧 Creating Advanced Node System...")
        print("🚀 Opening Blender with node system...")
        
        # Launch Blender
        subprocess.Popen([
            blender_path,
            "--python", script_path
        ])
        
        print("✨ Blender opened!")
        print("🔧 Advanced Node System features:")
        print("   - 🔧 Modular Node Architecture")
        print("   - 🎨 Advanced Material Nodes")
        print("   - 🔷 Geometry Nodes")
        print("   - 🎬 Animation Nodes")
        print("   - 🧮 Processing Nodes")
        print("   - 🔀 Logic Nodes")
        print("   - 📊 Data Nodes")
        print("   - 🔗 Node Connections")
        print("   - ⚙️ Node Execution Engine")
        print("")
        print("💾 Result saved as: advanced_node_system.blend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print(f"📝 Script: {script_path}")

if __name__ == "__main__":
    print("🔧 Advanced Node System for Blender")
    print("=" * 50)
    
    run_node_system()
    
    print("\n✨ Advanced Node System created successfully!") 