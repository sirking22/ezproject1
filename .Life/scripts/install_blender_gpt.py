"""
Install and setup BlenderGPT for advanced 3D generation
"""

import subprocess
import sys
import os
from pathlib import Path

def install_blender_gpt():
    """Install BlenderGPT"""
    print("=== Installing BlenderGPT ===")
    
    try:
        # Install via pip
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "blender-gpt"
        ])
        print("✅ BlenderGPT installed successfully")
        
        # Test installation
        result = subprocess.run([
            "blender-gpt", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ BlenderGPT version: {result.stdout.strip()}")
        else:
            print("⚠️  BlenderGPT installed but version check failed")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    
    return True

def setup_blender_integration():
    """Setup Blender integration"""
    print("\n=== Setting up Blender Integration ===")
    
    # Check if Blender is available
    blender_paths = [
        "Z:\\Программы\\Blender\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]
    
    blender_found = False
    for path in blender_paths:
        if Path(path).exists():
            print(f"✅ Found Blender at: {path}")
            blender_found = True
            break
    
    if not blender_found:
        print("❌ Blender not found. Please install Blender first.")
        return False
    
    return True

def test_blender_gpt():
    """Test BlenderGPT functionality"""
    print("\n=== Testing BlenderGPT ===")
    
    try:
        # Simple test command
        result = subprocess.run([
            "blender-gpt", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ BlenderGPT is working correctly")
            return True
        else:
            print(f"❌ BlenderGPT test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ BlenderGPT test timed out")
        return False
    except Exception as e:
        print(f"❌ BlenderGPT test error: {e}")
        return False

def create_test_script():
    """Create a test script for BlenderGPT"""
    print("\n=== Creating Test Script ===")
    
    test_script = '''"""
Test BlenderGPT integration
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_gpt_integration import BlenderGPTCLI

async def test_blender_gpt():
    """Test BlenderGPT functionality"""
    print("=== Testing BlenderGPT Integration ===")
    
    try:
        cli = BlenderGPTCLI()
        
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
    asyncio.run(test_blender_gpt())
'''
    
    with open("scripts/test_blender_gpt_integration.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: scripts/test_blender_gpt_integration.py")

def main():
    """Main installation process"""
    print("BlenderGPT Installation and Setup")
    print("=" * 40)
    
    # Install BlenderGPT
    if not install_blender_gpt():
        print("❌ Installation failed. Exiting.")
        return
    
    # Setup Blender integration
    if not setup_blender_integration():
        print("❌ Blender setup failed. Exiting.")
        return
    
    # Test functionality
    if not test_blender_gpt():
        print("❌ Test failed. Please check installation.")
        return
    
    # Create test script
    create_test_script()
    
    print("\n" + "=" * 40)
    print("✅ BlenderGPT setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python scripts/test_blender_gpt_integration.py")
    print("2. Use BlenderGPT in your projects:")
    print("   from src.integrations.blender_gpt_integration import BlenderGPTCLI")
    print("3. Check documentation: docs/BLENDER_GPT_INTEGRATION.md")

if __name__ == "__main__":
    main() 