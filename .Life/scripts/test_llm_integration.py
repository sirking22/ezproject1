"""
Test LLM-powered Blender integration
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_llm_integration():
    """Test LLM integration with Blender"""
    print("=== Testing LLM-Powered Blender Integration ===")
    
    try:
        # Import the LLM integration
        from integrations.blender_llm_integration import BlenderLLMCLI
        
        cli = BlenderLLMCLI()
        
        # Test simple cube creation
        prompt = "Create a simple cube with dimensions 1x1x1 units"
        result = await cli.create_object(prompt, "test_cube", iterations=2)
        
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
    asyncio.run(test_llm_integration()) 