"""
Simple validation test for debugging
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_validator import BlenderValidator

async def test_simple_validation():
    """Test simple validation of an existing STL file"""
    print("=== Simple Validation Test ===")
    
    # Find an existing STL file
    stl_files = list(Path("cache/blender").glob("*.stl"))
    if not stl_files:
        print("No STL files found in cache/blender/")
        return
    
    test_file = str(stl_files[0])
    print(f"Testing validation of: {test_file}")
    
    # Initialize validator
    validator = BlenderValidator()
    
    # Test validation
    try:
        validation = await validator.validate_stl_file(test_file)
        
        print(f"Validation completed:")
        print(f"  Score: {validation.score}/100")
        print(f"  Valid: {validation.is_valid}")
        print(f"  Issues: {len(validation.issues)}")
        print(f"  Metrics: {validation.metrics}")
        
        if validation.issues:
            print("Issues found:")
            for issue in validation.issues:
                print(f"  - {issue}")
                
    except Exception as e:
        print(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_validation()) 