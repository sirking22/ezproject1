"""
Test script for Blender integration
Tests object creation, scene management, and batch processing
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_engine import (
    BlenderEngine, ObjectSpec, SceneSpec, ObjectType, MaterialType,
    Vector3, RenderSpec, ExportSpec, ExportFormat
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_objects():
    """Test basic object creation"""
    print("=== Testing Basic Object Creation ===")
    
    engine = BlenderEngine()
    
    # Test cube
    cube_spec = ObjectSpec(
        name="test_cube",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, 0),
        dimensions=Vector3(2, 2, 2),
        material_type=MaterialType.METAL,
        color=Vector3(0.8, 0.2, 0.2)
    )
    
    result = await engine.create_object(cube_spec)
    print(f"✓ Cube created: {result}")
    
    # Test cylinder
    cylinder_spec = ObjectSpec(
        name="test_cylinder",
        object_type=ObjectType.CYLINDER,
        position=Vector3(3, 0, 0),
        radius=1.0,
        height=2.0,
        material_type=MaterialType.PLASTIC,
        color=Vector3(0.2, 0.8, 0.2)
    )
    
    result = await engine.create_object(cylinder_spec)
    print(f"✓ Cylinder created: {result}")
    
    # Test sphere
    sphere_spec = ObjectSpec(
        name="test_sphere",
        object_type=ObjectType.SPHERE,
        position=Vector3(-3, 0, 0),
        radius=1.5,
        material_type=MaterialType.GLASS,
        color=Vector3(0.2, 0.2, 0.8),
        transparency=0.3
    )
    
    result = await engine.create_object(sphere_spec)
    print(f"✓ Sphere created: {result}")


async def test_scene_creation():
    """Test complete scene creation"""
    print("\n=== Testing Scene Creation ===")
    
    engine = BlenderEngine()
    
    # Create scene specification
    scene_spec = SceneSpec(
        name="test_scene",
        camera_position=Vector3(8, -8, 5),
        camera_target=Vector3(0, 0, 0),
        lighting="studio"
    )
    
    # Add objects to scene
    scene_spec.objects.extend([
        ObjectSpec(
            name="base_plate",
            object_type=ObjectType.CUBE,
            position=Vector3(0, 0, -0.5),
            dimensions=Vector3(10, 10, 1),
            material_type=MaterialType.WOOD,
            color=Vector3(0.6, 0.4, 0.2)
        ),
        ObjectSpec(
            name="center_pillar",
            object_type=ObjectType.CYLINDER,
            position=Vector3(0, 0, 1),
            radius=0.5,
            height=2,
            material_type=MaterialType.METAL,
            color=Vector3(0.7, 0.7, 0.7)
        ),
        ObjectSpec(
            name="top_sphere",
            object_type=ObjectType.SPHERE,
            position=Vector3(0, 0, 3),
            radius=0.8,
            material_type=MaterialType.GLASS,
            color=Vector3(0.9, 0.9, 1.0),
            transparency=0.2
        )
    ])
    
    # Create render specification
    render_spec = RenderSpec(
        resolution_x=1280,
        resolution_y=720,
        samples=64,
        engine="CYCLES",
        output_path="output/test_scene_render.png"
    )
    
    # Create export specification
    export_spec = ExportSpec(
        format=ExportFormat.STL,
        output_path="output/test_scene.stl",
        scale=1.0
    )
    
    # Create scene
    results = await engine.create_scene(scene_spec, render_spec, export_spec)
    
    print("✓ Scene created successfully:")
    for key, value in results.items():
        if value:
            print(f"  {key}: {value}")


async def test_batch_processing():
    """Test batch object creation"""
    print("\n=== Testing Batch Processing ===")
    
    engine = BlenderEngine()
    
    # Create multiple object specifications
    specs = []
    
    for i in range(5):
        spec = ObjectSpec(
            name=f"batch_object_{i}",
            object_type=ObjectType.CUBE,
            position=Vector3(i * 2 - 4, 0, 0),
            dimensions=Vector3(1, 1, 1),
            material_type=MaterialType.PLASTIC,
            color=Vector3(0.2 + i * 0.15, 0.5, 0.8)
        )
        specs.append(spec)
    
    # Batch create objects
    results = await engine.batch_create(specs, "output/batch_test")
    
    print(f"✓ Batch created {len(results)} objects:")
    for result in results:
        print(f"  {result}")


async def test_cache_functionality():
    """Test caching functionality"""
    print("\n=== Testing Cache Functionality ===")
    
    engine = BlenderEngine()
    
    # Create object specification
    spec = ObjectSpec(
        name="cache_test",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, 0),
        dimensions=Vector3(1, 1, 1)
    )
    
    # Create object first time (cache miss)
    start_time = asyncio.get_event_loop().time()
    result1 = await engine.create_object(spec)
    time1 = asyncio.get_event_loop().time() - start_time
    
    # Create same object second time (cache hit)
    start_time = asyncio.get_event_loop().time()
    result2 = await engine.create_object(spec)
    time2 = asyncio.get_event_loop().time() - start_time
    
    print(f"✓ First creation (cache miss): {time1:.3f}s")
    print(f"✓ Second creation (cache hit): {time2:.3f}s")
    print(f"✓ Speedup: {time1/time2:.1f}x")
    
    # Show cache statistics
    stats = engine.get_stats()
    print(f"✓ Cache hits: {stats['cache_hits']}")
    print(f"✓ Cache misses: {stats['cache_misses']}")


async def test_material_variations():
    """Test different material types"""
    print("\n=== Testing Material Variations ===")
    
    engine = BlenderEngine()
    
    materials = [
        (MaterialType.METAL, Vector3(0.8, 0.8, 0.8), 0.1, 1.0),
        (MaterialType.PLASTIC, Vector3(0.2, 0.8, 0.2), 0.8, 0.0),
        (MaterialType.GLASS, Vector3(0.9, 0.9, 1.0), 0.0, 0.0),
        (MaterialType.WOOD, Vector3(0.6, 0.4, 0.2), 0.9, 0.0),
        (MaterialType.CERAMIC, Vector3(1.0, 1.0, 1.0), 0.3, 0.0)
    ]
    
    for i, (material_type, color, roughness, metallic) in enumerate(materials):
        spec = ObjectSpec(
            name=f"material_test_{material_type.value}",
            object_type=ObjectType.SPHERE,
            position=Vector3(i * 2 - 4, 0, 0),
            radius=0.8,
            material_type=material_type,
            color=color,
            roughness=roughness,
            metallic=metallic
        )
        
        result = await engine.create_object(spec)
        print(f"✓ {material_type.value} material: {result}")


async def main():
    """Run all tests"""
    print("Starting Blender Integration Tests\n")
    
    try:
        await test_basic_objects()
        await test_scene_creation()
        await test_batch_processing()
        await test_cache_functionality()
        await test_material_variations()
        
        print("\n=== All Tests Completed Successfully ===")
        
        # Show final statistics
        engine = BlenderEngine()
        stats = engine.get_stats()
        print("\nFinal Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 