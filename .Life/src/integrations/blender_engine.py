"""
Blender Engine - High-performance 3D generation system
Provides declarative API for precise object creation and batch processing
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib
import pickle
from datetime import datetime
import bmesh
import struct

logger = logging.getLogger(__name__)


class ObjectType(Enum):
    """Supported 3D object types"""
    CUBE = "cube"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    PLANE = "plane"
    CONE = "cone"
    TORUS = "torus"
    LAMP = "lamp"
    NIKE_LOGO = "nike_logo"


class MaterialType(Enum):
    """Material types for objects"""
    METAL = "metal"
    PLASTIC = "plastic"
    GLASS = "glass"
    WOOD = "wood"
    CERAMIC = "ceramic"
    FABRIC = "fabric"


class ExportFormat(Enum):
    """Supported export formats"""
    STL = "stl"
    OBJ = "obj"
    FBX = "fbx"
    GLB = "glb"


@dataclass
class Vector3:
    """3D vector for positions, rotations, scales"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class ObjectSpec:
    """Specification for 3D object creation"""
    name: str
    object_type: ObjectType
    position: Vector3 = field(default_factory=Vector3)
    rotation: Vector3 = field(default_factory=Vector3)
    scale: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))
    
    # Object-specific parameters
    dimensions: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))
    radius: float = 0.5
    height: float = 1.0
    segments: int = 32
    rings: int = 16
    extrude_depth: float = 0.1  # For Nike logo extrusion
    
    # Material properties
    material_type: Optional[MaterialType] = None
    color: Vector3 = field(default_factory=lambda: Vector3(0.8, 0.8, 0.8))
    roughness: float = 0.5
    metallic: float = 0.0
    transparency: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "object_type": self.object_type.value,
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "scale": self.scale.to_dict(),
            "dimensions": self.dimensions.to_dict(),
            "radius": self.radius,
            "height": self.height,
            "segments": self.segments,
            "rings": self.rings,
            "extrude_depth": self.extrude_depth,
            "material_type": self.material_type.value if self.material_type else None,
            "color": self.color.to_dict(),
            "roughness": self.roughness,
            "metallic": self.metallic,
            "transparency": self.transparency
        }


@dataclass
class SceneSpec:
    """Complete scene specification"""
    name: str
    objects: List[ObjectSpec] = field(default_factory=list)
    camera_position: Vector3 = field(default_factory=lambda: Vector3(5.0, -5.0, 3.0))
    camera_target: Vector3 = field(default_factory=Vector3)
    lighting: str = "studio"  # studio, outdoor, indoor
    background_color: Vector3 = field(default_factory=lambda: Vector3(0.1, 0.1, 0.1))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "objects": [obj.to_dict() for obj in self.objects],
            "camera_position": self.camera_position.to_dict(),
            "camera_target": self.camera_target.to_dict(),
            "lighting": self.lighting,
            "background_color": self.background_color.to_dict()
        }


@dataclass
class RenderSpec:
    """Render settings"""
    resolution_x: int = 1920
    resolution_y: int = 1080
    samples: int = 128
    engine: str = "CYCLES"  # CYCLES, EEVEE
    file_format: str = "PNG"
    output_path: Optional[str] = None


@dataclass
class ExportSpec:
    """Export settings"""
    format: ExportFormat
    output_path: str
    scale: float = 1.0
    use_selection: bool = False
    apply_modifiers: bool = True


class BlenderEngine:
    """High-performance Blender control engine"""
    
    def __init__(self, blender_path: str = None, cache_dir: str = "cache/blender"):
        self.blender_path = blender_path or self._find_blender()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.stats = {
            "objects_created": 0,
            "scenes_rendered": 0,
            "exports_completed": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info(f"Blender Engine initialized with path: {self.blender_path}")
    
    def _find_blender(self) -> str:
        """Find Blender installation"""
        possible_paths = [
            "Z:\\Программы\\Blender\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
            "/usr/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Blender not found. Please specify blender_path manually.")
    
    def _generate_cache_key(self, spec: Union[ObjectSpec, SceneSpec]) -> str:
        """Generate cache key for specification"""
        spec_dict = spec.to_dict()
        spec_json = json.dumps(spec_dict, sort_keys=True)
        return hashlib.md5(spec_json.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, extension: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.{extension}"
    
    async def create_object(self, spec: ObjectSpec, use_cache: bool = True) -> str:
        """Create single object and return output path"""
        cache_key = self._generate_cache_key(spec)
        output_path = self._get_cache_path(cache_key, "stl")
        
        if use_cache and output_path.exists():
            self.stats["cache_hits"] += 1
            logger.info(f"Cache hit for object: {spec.name}")
            return str(output_path)
        
        self.stats["cache_misses"] += 1
        
        # Generate Blender script
        script = self._generate_object_script(spec, str(output_path))
        
        # Execute Blender
        result = await self._execute_blender_script(script, output_path)
        
        if result:
            self.stats["objects_created"] += 1
            logger.info(f"Created object: {spec.name} -> {output_path}")
            return str(output_path)
        else:
            raise RuntimeError(f"Failed to create object: {spec.name}")
    
    async def create_scene(self, spec: SceneSpec, render_spec: RenderSpec = None, 
                          export_spec: ExportSpec = None) -> Dict[str, str]:
        """Create complete scene with optional render and export"""
        cache_key = self._generate_cache_key(spec)
        
        results = {
            "scene_file": str(self._get_cache_path(cache_key, "blend")),
            "render": None,
            "export": None
        }
        
        # Generate scene script
        script = self._generate_scene_script(spec, render_spec, export_spec)
        
        # Execute Blender
        success = await self._execute_blender_script(script, results["scene_file"])
        
        if success:
            self.stats["scenes_rendered"] += 1
            
            if render_spec:
                render_path = self._get_cache_path(cache_key, render_spec.file_format.lower())
                if render_path.exists():
                    results["render"] = str(render_path)
            
            if export_spec:
                export_path = Path(export_spec.output_path)
                if export_path.exists():
                    results["export"] = str(export_path)
            
            logger.info(f"Created scene: {spec.name}")
            return results
        else:
            raise RuntimeError(f"Failed to create scene: {spec.name}")
    
    async def batch_create(self, specs: List[ObjectSpec], 
                          output_dir: str = "output/blender") -> List[str]:
        """Batch create multiple objects"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        tasks = []
        
        for spec in specs:
            task = self.create_object(spec)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful = [r for r in results if isinstance(r, str)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        if failed:
            logger.warning(f"Failed to create {len(failed)} objects")
            for error in failed:
                logger.error(f"Batch creation error: {error}")
        
        logger.info(f"Batch created {len(successful)} objects")
        return successful
    
    def _generate_object_script(self, spec: ObjectSpec, output_path: str = None) -> str:
        """Generate Blender Python script for object creation"""
        if output_path is None:
            output_path = str(self.cache_dir / f"{spec.name}.stl")
            
        return f'''
import bpy
import bmesh
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create object
if "{spec.object_type.value}" == "cube":
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=({spec.position.x}, {spec.position.y}, {spec.position.z})
    )
    obj = bpy.context.active_object
    obj.scale = ({spec.scale.x}, {spec.scale.y}, {spec.scale.z})
    
elif "{spec.object_type.value}" == "cylinder":
    bpy.ops.mesh.primitive_cylinder_add(
        radius={spec.radius},
        depth={spec.height},
        location=({spec.position.x}, {spec.position.y}, {spec.position.z}),
        vertices={spec.segments}
    )
    obj = bpy.context.active_object
    obj.scale = ({spec.scale.x}, {spec.scale.y}, {spec.scale.z})
    
elif "{spec.object_type.value}" == "sphere":
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius={spec.radius},
        location=({spec.position.x}, {spec.position.y}, {spec.position.z}),
        segments={spec.segments},
        rings={spec.rings}
    )
    obj = bpy.context.active_object
    obj.scale = ({spec.scale.x}, {spec.scale.y}, {spec.scale.z})

elif "{spec.object_type.value}" == "nike_logo":
    # Create Nike Swoosh using simple primitives (more compatible)
    # Create base plane
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=({spec.position.x}, {spec.position.y}, {spec.position.z})
    )
    obj = bpy.context.active_object
    
    # Enter edit mode to shape the plane
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Scale to make it wider
    bpy.ops.transform.resize(value=(2, 0.3, 1))
    
    # Add more vertices for better control
    bpy.ops.mesh.subdivide(number_cuts=3)
    
    # Move vertices to create swoosh curve
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get mesh data
    mesh = obj.data
    for i, vert in enumerate(mesh.vertices):
        if i < len(mesh.vertices) // 2:
            # First half - curve up
            progress = i / (len(mesh.vertices) // 2)
            vert.co.y += 0.3 * progress
        else:
            # Second half - curve down
            progress = (i - len(mesh.vertices) // 2) / (len(mesh.vertices) // 2)
            vert.co.y += 0.3 * (1 - progress)
    
    # Add thickness
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region()
    bpy.ops.transform.translate(value=(0, 0, {spec.extrude_depth}))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply scale
    obj.scale = ({spec.scale.x}, {spec.scale.y}, {spec.scale.z})

# Apply rotation
obj.rotation_euler = ({spec.rotation.x}, {spec.rotation.y}, {spec.rotation.z})

# Create material
if {spec.material_type is not None}:
    mat = bpy.data.materials.new(name="{spec.name}_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Clear default nodes
    nodes.clear()
    
    # Create principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = ({spec.color.x}, {spec.color.y}, {spec.color.z}, 1.0)
    principled.inputs['Roughness'].default_value = {spec.roughness}
    principled.inputs['Metallic'].default_value = {spec.metallic}
    principled.inputs['Alpha'].default_value = {1.0 - spec.transparency}
    
    # Create output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Export to STL using bmesh (works in Blender 4.4)
import bmesh
import struct

# Get the mesh data
mesh = obj.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Ensure mesh has faces
if len(bm.faces) == 0:
    # If no faces, create a simple plane
    bm.faces.new(bm.verts[:3]) if len(bm.verts) >= 3 else None

# Create STL file
with open(r"{output_path}".replace('\\\\', '/'), "wb") as f:
    # Write STL header (80 bytes)
    header = "STL file generated by Blender".encode('ascii')
    f.write(header + b'\\x00' * (80 - len(header)))
    
    # Write triangle count
    f.write(struct.pack("<I", len(bm.faces)))
    
    # Write each face
    for face in bm.faces:
        if len(face.verts) >= 3:
            # Calculate normal
            normal = face.normal
            f.write(struct.pack("<3f", normal.x, normal.y, normal.z))
            
            # Write vertices (triangulate if needed)
            if len(face.verts) == 3:
                for vert in face.verts:
                    f.write(struct.pack("<3f", vert.co.x, vert.co.y, vert.co.z))
            else:
                # Triangulate polygon
                for i in range(1, len(face.verts) - 1):
                    v0 = face.verts[0]
                    v1 = face.verts[i]
                    v2 = face.verts[i + 1]
                    f.write(struct.pack("<3f", v0.co.x, v0.co.y, v0.co.z))
                    f.write(struct.pack("<3f", v1.co.x, v1.co.y, v1.co.z))
                    f.write(struct.pack("<3f", v2.co.x, v2.co.y, v2.co.z))
            
            # Write attribute byte count (0)
            f.write(struct.pack("<H", 0))

bm.free()
'''
    
    def _generate_scene_script(self, spec: SceneSpec, render_spec: RenderSpec = None, 
                              export_spec: ExportSpec = None) -> str:
        """Generate Blender Python script for scene creation"""
        script = '''
import bpy
import bmesh
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Setup scene
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 128

# Setup camera
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
scene.camera = camera

# Setup lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 5.0

# Create objects
'''
        
        # Add object creation for each object in scene
        for obj_spec in spec.objects:
            script += self._generate_object_script(obj_spec)
        
        # Add render settings if specified
        if render_spec:
            script += f'''
# Render settings
scene.render.resolution_x = {render_spec.resolution_x}
scene.render.resolution_y = {render_spec.resolution_y}
scene.cycles.samples = {render_spec.samples}
scene.render.engine = "{render_spec.engine}"

# Render
scene.render.filepath = "{render_spec.output_path or "//render.png"}"
bpy.ops.render.render(write_still=True)
'''
        
        # Add export settings if specified
        if export_spec:
            if export_spec.format == ExportFormat.STL:
                script += f'''
# Export STL
bpy.ops.export_mesh.stl(
    filepath="{export_spec.output_path}",
    use_selection={str(export_spec.use_selection).lower()},
    global_scale={export_spec.scale},
    use_scene_unit=False,
    ascii=False,
    use_mesh_edges=False,
    use_mesh_vertices=False
)
'''
            elif export_spec.format == ExportFormat.OBJ:
                script += f'''
# Export OBJ
bpy.ops.export_scene.obj(
    filepath="{export_spec.output_path}",
    use_selection={str(export_spec.use_selection).lower()},
    use_mesh_edges=True,
    use_mesh_vertices=True,
    global_scale={export_spec.scale}
)
'''
        
        return script
    
    async def _execute_blender_script(self, script: str, output_path: Path) -> bool:
        """Execute Blender script and return success status"""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script)
                script_path = f.name
            
            logger.info(f"Created temporary script: {script_path}")
            logger.info(f"Output path: {output_path}")
            
            # Execute Blender
            cmd = [
                self.blender_path,
                "--background",
                "--python", script_path,
                "--", str(output_path)
            ]
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temporary script
            os.unlink(script_path)
            
            logger.info(f"Blender stdout: {stdout.decode()}")
            if stderr:
                logger.warning(f"Blender stderr: {stderr.decode()}")
            
            if process.returncode == 0:
                logger.info(f"Blender executed successfully, return code: {process.returncode}")
                return True
            else:
                logger.error(f"Blender execution failed, return code: {process.returncode}")
                logger.error(f"Blender stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing Blender script: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.stats,
            "cache_dir": str(self.cache_dir),
            "cache_size_mb": self._get_cache_size()
        }
    
    def _get_cache_size(self) -> float:
        """Get cache directory size in MB"""
        total_size = 0
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def clear_cache(self) -> None:
        """Clear all cached files"""
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                file_path.unlink()
        logger.info("Cache cleared")
    
    def cleanup_old_cache(self, max_age_hours: int = 24) -> int:
        """Remove cache files older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        removed_count = 0
        
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                removed_count += 1
        
        logger.info(f"Removed {removed_count} old cache files")
        return removed_count
    
    async def create_object_with_validation(self, spec: ObjectSpec, target_score: float = 80.0, 
                                          max_iterations: int = 5) -> Tuple[str, List[Dict]]:
        """Create object with iterative validation and improvement"""
        from .blender_validator import BlenderValidator, IterativeImprover, QualityReporter
        
        validator = BlenderValidator(self.blender_path)
        improver = IterativeImprover(self, validator)
        improver.max_iterations = max_iterations
        improver.min_score = target_score
        
        # Run iterative improvement
        results = await improver.improve_model(spec)
        
        # Generate report
        reporter = QualityReporter()
        report = reporter.generate_report(results)
        
        # Save report
        report_path = Path("output/quality_reports")
        report_path.mkdir(parents=True, exist_ok=True)
        
        report_file = report_path / f"{spec.name}_quality_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Return final model path and validation history
        final_result = results[-1] if results else None
        final_path = final_result.model_path if final_result else None
        
        validation_history = []
        for result in results:
            validation_history.append({
                "iteration": result.iteration,
                "score": result.validation.score,
                "is_valid": result.validation.is_valid,
                "issues": result.validation.issues,
                "improvements": result.improvements,
                "time_taken": result.time_taken
            })
        
        return final_path, validation_history 