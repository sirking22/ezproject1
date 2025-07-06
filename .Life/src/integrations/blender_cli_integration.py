"""
Blender CLI Integration - Command-line interface for Blender control
Provides high-level commands for object creation, scene management, and batch processing
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from .blender_engine import (
    BlenderEngine, ObjectSpec, SceneSpec, ObjectType, MaterialType,
    Vector3, RenderSpec, ExportSpec, ExportFormat
)

logger = logging.getLogger(__name__)


class BlenderCLI:
    """Command-line interface for Blender operations"""
    
    def __init__(self, blender_path: str = None):
        self.engine = BlenderEngine(blender_path)
    
    async def create_cube(self, name: str, size: float = 1.0, 
                         position: List[float] = None, material: str = None) -> str:
        """Create a cube with specified parameters"""
        spec = ObjectSpec(
            name=name,
            object_type=ObjectType.CUBE,
            position=Vector3(*(position or [0, 0, 0])),
            dimensions=Vector3(size, size, size),
            material_type=MaterialType(material) if material else None
        )
        
        return await self.engine.create_object(spec)
    
    async def create_cylinder(self, name: str, radius: float = 0.5, height: float = 1.0,
                            position: List[float] = None, segments: int = 32) -> str:
        """Create a cylinder with specified parameters"""
        spec = ObjectSpec(
            name=name,
            object_type=ObjectType.CYLINDER,
            position=Vector3(*(position or [0, 0, 0])),
            radius=radius,
            height=height,
            segments=segments
        )
        
        return await self.engine.create_object(spec)
    
    async def create_sphere(self, name: str, radius: float = 0.5,
                          position: List[float] = None, segments: int = 32) -> str:
        """Create a sphere with specified parameters"""
        spec = ObjectSpec(
            name=name,
            object_type=ObjectType.SPHERE,
            position=Vector3(*(position or [0, 0, 0])),
            radius=radius,
            segments=segments
        )
        
        return await self.engine.create_object(spec)
    
    async def batch_from_json(self, json_file: str, output_dir: str = "output/blender") -> List[str]:
        """Create objects from JSON specification file"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        specs = []
        for item in data:
            spec = ObjectSpec(
                name=item["name"],
                object_type=ObjectType(item["type"]),
                position=Vector3(**item.get("position", {})),
                rotation=Vector3(**item.get("rotation", {})),
                scale=Vector3(**item.get("scale", {"x": 1.0, "y": 1.0, "z": 1.0})),
                dimensions=Vector3(**item.get("dimensions", {"x": 1.0, "y": 1.0, "z": 1.0})),
                radius=item.get("radius", 0.5),
                height=item.get("height", 1.0),
                segments=item.get("segments", 32),
                material_type=MaterialType(item["material"]) if "material" in item else None
            )
            specs.append(spec)
        
        return await self.engine.batch_create(specs, output_dir)
    
    async def create_scene_from_blueprint(self, blueprint_file: str, 
                                        render: bool = False, export_format: str = None) -> Dict[str, str]:
        """Create scene from blueprint file"""
        with open(blueprint_file, 'r') as f:
            data = json.load(f)
        
        # Create scene specification
        scene_spec = SceneSpec(
            name=data["name"],
            camera_position=Vector3(**data.get("camera_position", {})),
            camera_target=Vector3(**data.get("camera_target", {})),
            lighting=data.get("lighting", "studio"),
            background_color=Vector3(**data.get("background_color", {}))
        )
        
        # Add objects
        for obj_data in data["objects"]:
            obj_spec = ObjectSpec(
                name=obj_data["name"],
                object_type=ObjectType(obj_data["type"]),
                position=Vector3(**obj_data.get("position", {})),
                rotation=Vector3(**obj_data.get("rotation", {})),
                scale=Vector3(**obj_data.get("scale", {"x": 1.0, "y": 1.0, "z": 1.0})),
                dimensions=Vector3(**obj_data.get("dimensions", {"x": 1.0, "y": 1.0, "z": 1.0})),
                radius=obj_data.get("radius", 0.5),
                height=obj_data.get("height", 1.0),
                segments=obj_data.get("segments", 32),
                material_type=MaterialType(obj_data["material"]) if "material" in obj_data else None
            )
            scene_spec.objects.append(obj_spec)
        
        # Setup render and export
        render_spec = None
        export_spec = None
        
        if render:
            render_spec = RenderSpec(
                resolution_x=1920,
                resolution_y=1080,
                samples=128,
                output_path=f"output/renders/{data['name']}.png"
            )
        
        if export_format:
            export_spec = ExportSpec(
                format=ExportFormat(export_format),
                output_path=f"output/exports/{data['name']}.{export_format}",
                scale=1.0
            )
        
        return await self.engine.create_scene(scene_spec, render_spec, export_spec)
    
    async def create_nike_logo(self, name: str, position: List[float] = None, 
                              extrude_depth: float = 0.1, scale: float = 1.0, 
                              material: str = None) -> str:
        """Create Nike logo (Swoosh) with specified parameters"""
        spec = ObjectSpec(
            name=name,
            object_type=ObjectType.NIKE_LOGO,
            position=Vector3(*(position or [0, 0, 0])),
            scale=Vector3(scale, scale, scale),
            extrude_depth=extrude_depth,
            material_type=MaterialType(material) if material else None
        )
        
        return await self.engine.create_object(spec)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return self.engine.get_stats()
    
    def clear_cache(self) -> None:
        """Clear engine cache"""
        self.engine.clear_cache()
    
    async def create_iterative_object(self, object_type: str, name: str, target_score: float = 80.0,
                                    max_iterations: int = 5, position: List[float] = None, 
                                    material: str = None) -> str:
        """Create object with iterative validation and improvement"""
        # Create spec based on object type
        if object_type == "cube":
            spec = ObjectSpec(
                name=name,
                object_type=ObjectType.CUBE,
                position=Vector3(*(position or [0, 0, 0])),
                material_type=MaterialType(material) if material else None
            )
        elif object_type == "cylinder":
            spec = ObjectSpec(
                name=name,
                object_type=ObjectType.CYLINDER,
                position=Vector3(*(position or [0, 0, 0])),
                material_type=MaterialType(material) if material else None
            )
        elif object_type == "sphere":
            spec = ObjectSpec(
                name=name,
                object_type=ObjectType.SPHERE,
                position=Vector3(*(position or [0, 0, 0])),
                material_type=MaterialType(material) if material else None
            )
        elif object_type == "nike_logo":
            spec = ObjectSpec(
                name=name,
                object_type=ObjectType.NIKE_LOGO,
                position=Vector3(*(position or [0, 0, 0])),
                material_type=MaterialType(material) if material else None
            )
        else:
            raise ValueError(f"Unsupported object type: {object_type}")
        
        # Create with validation
        final_path, validation_history = await self.engine.create_object_with_validation(
            spec, target_score, max_iterations
        )
        
        # Print validation summary
        print(f"\n=== Iterative Creation Summary ===")
        print(f"Final model: {final_path}")
        print(f"Total iterations: {len(validation_history)}")
        if validation_history:
            final_score = validation_history[-1]["score"]
            print(f"Final quality score: {final_score}/100")
            print(f"Status: {'✅ PASS' if validation_history[-1]['is_valid'] else '❌ FAIL'}")
        
        return final_path
    
    async def validate_stl_file(self, stl_file: str, output_report: str = None) -> Dict:
        """Validate existing STL file"""
        from .blender_validator import BlenderValidator, QualityReporter
        
        validator = BlenderValidator(self.engine.blender_path)
        validation = await validator.validate_stl_file(stl_file)
        
        # Generate report
        reporter = QualityReporter()
        report = f"""
# STL File Validation Report

## File: {stl_file}

## Results
- **Score**: {validation.score}/100
- **Valid**: {'✅ Yes' if validation.is_valid else '❌ No'}

## Issues
{chr(10).join(f"- {issue}" for issue in validation.issues) if validation.issues else "- No issues found"}

## Suggestions
{chr(10).join(f"- {suggestion}" for suggestion in validation.suggestions) if validation.suggestions else "- No suggestions"}

## Metrics
{chr(10).join(f"- **{key}**: {value}" for key, value in validation.metrics.items())}
"""
        
        # Save report if requested
        if output_report:
            with open(output_report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_report}")
        
        return {
            "score": validation.score,
            "is_valid": validation.is_valid,
            "issues": validation.issues,
            "suggestions": validation.suggestions,
            "metrics": validation.metrics
        }


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Blender CLI Integration")
    parser.add_argument("--blender-path", help="Path to Blender executable")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Cube command
    cube_parser = subparsers.add_parser("cube", help="Create a cube")
    cube_parser.add_argument("name", help="Object name")
    cube_parser.add_argument("--size", type=float, default=1.0, help="Cube size")
    cube_parser.add_argument("--position", nargs=3, type=float, help="Position (x y z)")
    cube_parser.add_argument("--material", help="Material type")
    
    # Cylinder command
    cylinder_parser = subparsers.add_parser("cylinder", help="Create a cylinder")
    cylinder_parser.add_argument("name", help="Object name")
    cylinder_parser.add_argument("--radius", type=float, default=0.5, help="Radius")
    cylinder_parser.add_argument("--height", type=float, default=1.0, help="Height")
    cylinder_parser.add_argument("--position", nargs=3, type=float, help="Position (x y z)")
    cylinder_parser.add_argument("--segments", type=int, default=32, help="Number of segments")
    
    # Sphere command
    sphere_parser = subparsers.add_parser("sphere", help="Create a sphere")
    sphere_parser.add_argument("name", help="Object name")
    sphere_parser.add_argument("--radius", type=float, default=0.5, help="Radius")
    sphere_parser.add_argument("--position", nargs=3, type=float, help="Position (x y z)")
    sphere_parser.add_argument("--segments", type=int, default=32, help="Number of segments")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch create objects from JSON")
    batch_parser.add_argument("json_file", help="JSON specification file")
    batch_parser.add_argument("--output-dir", default="output/blender", help="Output directory")
    
    # Scene command
    scene_parser = subparsers.add_parser("scene", help="Create scene from blueprint")
    scene_parser.add_argument("blueprint_file", help="Blueprint JSON file")
    scene_parser.add_argument("--render", action="store_true", help="Render scene")
    scene_parser.add_argument("--export", choices=["stl", "obj", "fbx", "glb"], help="Export format")
    
    # Nike logo command
    nike_parser = subparsers.add_parser("nike_logo", help="Create Nike logo (Swoosh)")
    nike_parser.add_argument("name", help="Object name")
    nike_parser.add_argument("--position", nargs=3, type=float, help="Position (x y z)")
    nike_parser.add_argument("--extrude", type=float, default=0.1, help="Extrusion depth")
    nike_parser.add_argument("--scale", type=float, default=1.0, help="Scale factor")
    nike_parser.add_argument("--material", help="Material type")
    
    # Iterative creation commands
    iterative_parser = subparsers.add_parser("iterative", help="Create object with iterative validation")
    iterative_parser.add_argument("object_type", choices=["cube", "cylinder", "sphere", "nike_logo"], help="Object type")
    iterative_parser.add_argument("name", help="Object name")
    iterative_parser.add_argument("--target-score", type=float, default=80.0, help="Target quality score (0-100)")
    iterative_parser.add_argument("--max-iterations", type=int, default=5, help="Maximum iterations")
    iterative_parser.add_argument("--position", nargs=3, type=float, help="Position (x y z)")
    iterative_parser.add_argument("--material", help="Material type")
    
    # Validation command
    validate_parser = subparsers.add_parser("validate", help="Validate existing STL file")
    validate_parser.add_argument("stl_file", help="Path to STL file")
    validate_parser.add_argument("--output-report", help="Output report file path")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show engine statistics")
    
    # Cache command
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_parser.add_argument("action", choices=["clear", "cleanup"], help="Cache action")
    cache_parser.add_argument("--max-age", type=int, default=24, help="Max age in hours for cleanup")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create CLI instance
    cli = BlenderCLI(args.blender_path)
    
    try:
        if args.command == "cube":
            result = await cli.create_cube(
                args.name, args.size, args.position, args.material
            )
            print(f"Created cube: {result}")
            
        elif args.command == "cylinder":
            result = await cli.create_cylinder(
                args.name, args.radius, args.height, args.position, args.segments
            )
            print(f"Created cylinder: {result}")
            
        elif args.command == "sphere":
            result = await cli.create_sphere(
                args.name, args.radius, args.position, args.segments
            )
            print(f"Created sphere: {result}")
            
        elif args.command == "batch":
            results = await cli.batch_from_json(args.json_file, args.output_dir)
            print(f"Created {len(results)} objects:")
            for result in results:
                print(f"  {result}")
                
        elif args.command == "scene":
            results = await cli.create_scene_from_blueprint(
                args.blueprint_file, args.render, args.export
            )
            print("Scene created:")
            for key, value in results.items():
                if value:
                    print(f"  {key}: {value}")
                    
        elif args.command == "stats":
            stats = cli.get_stats()
            print("Engine Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        elif args.command == "cache":
            if args.action == "clear":
                cli.clear_cache()
                print("Cache cleared")
            elif args.action == "cleanup":
                removed = cli.engine.cleanup_old_cache(args.max_age)
                print(f"Removed {removed} old cache files")
                
        elif args.command == "nike_logo":
            result = await cli.create_nike_logo(
                args.name, args.position, args.extrude, args.scale, args.material
            )
            print(f"Created Nike logo: {result}")
                
        elif args.command == "iterative":
            result = await cli.create_iterative_object(
                args.object_type, args.name, args.target_score, args.max_iterations, args.position, args.material
            )
            print(f"Created object: {result}")
            
        elif args.command == "validate":
            result = await cli.validate_stl_file(args.stl_file, args.output_report)
            print(f"Validation result: {result}")
                
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
