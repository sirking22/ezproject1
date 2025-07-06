"""
Simple test for Blender integration
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_engine import BlenderEngine, ObjectSpec, ObjectType, Vector3

async def test_simple_cube():
    """Test simple cube creation"""
    print("Testing simple cube creation...")
    
    engine = BlenderEngine()
    
    # Simple cube spec
    spec = ObjectSpec(
        name="simple_test",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, 0),
        dimensions=Vector3(1, 1, 1)
    )
    
    try:
        result = await engine.create_object(spec)
        print(f"✓ Success: {result}")
        
        # Check if file exists
        file_path = Path(result)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ File exists, size: {size} bytes")
        else:
            print("✗ File does not exist!")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_cube()) 