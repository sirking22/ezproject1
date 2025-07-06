"""
Test BlenderGPT integration
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_blender_gpt():
    """Test BlenderGPT functionality"""
    print("=== Testing BlenderGPT Integration ===")
    
    try:
        from integrations.blender_gpt_integration import BlenderGPTCLI
        
        cli = BlenderGPTCLI()
        
        # Test simple cube creation
        prompt = "Create a simple cube with dimensions 1x1x1 units"
        result = await cli.create_object(prompt, "test_cube")
        
        if result:
            print(f"✅ Test successful: {result}")
            
            # Test validation
            validation = await cli.validate_model(result)
            print(f"📊 Validation score: {validation['score']}/100")
            
            return True
        else:
            print("❌ Test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_blender_gpt())
