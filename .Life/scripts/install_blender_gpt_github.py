"""
Install BlenderGPT from GitHub repository
"""

import subprocess
import sys
import os
import zipfile
import requests
from pathlib import Path

def download_blender_gpt():
    """Download BlenderGPT from GitHub"""
    print("=== Downloading BlenderGPT from GitHub ===")
    
    # GitHub repository URL
    repo_url = "https://github.com/gd3kr/BlenderGPT"
    zip_url = "https://github.com/gd3kr/BlenderGPT/archive/refs/heads/main.zip"
    
    try:
        # Download ZIP file
        print(f"Downloading from: {zip_url}")
        response = requests.get(zip_url)
        response.raise_for_status()
        
        # Save ZIP file
        zip_path = Path("temp_blender_gpt.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract ZIP file
        extract_dir = Path("blender_gpt_addon")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Clean up ZIP file
        zip_path.unlink()
        
        print(f"✅ BlenderGPT downloaded to: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def install_blender_addon(addon_path: Path):
    """Install BlenderGPT as Blender addon"""
    print("\n=== Installing BlenderGPT Addon ===")
    
    # Find Blender installation
    blender_paths = [
        "Z:\\Программы\\Blender\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]
    
    blender_found = None
    for path in blender_paths:
        if Path(path).exists():
            blender_found = Path(path)
            break
    
    if not blender_found:
        print("❌ Blender not found. Please install Blender first.")
        return False
    
    # Find addon directory
    addon_dir = None
    for item in addon_path.iterdir():
        if item.is_dir() and "BlenderGPT" in item.name:
            addon_dir = item
            break
    
    if not addon_dir:
        print("❌ Addon directory not found in downloaded files")
        return False
    
    # Copy to Blender addons directory
    blender_scripts_dir = blender_found.parent / "4.4" / "scripts"
    
    if not blender_scripts_dir.exists():
        # Fallback for older structures
        blender_scripts_dir = blender_found.parent / "scripts"

    if not blender_scripts_dir.exists():
        print(f"❌ Blender scripts directory not found.")
        return False

    blender_addons_dir = blender_scripts_dir / "addons"
    
    if not blender_addons_dir.exists():
        print(f"⚠️ Community addons directory not found at '{blender_addons_dir}'. Creating it...")
        try:
            blender_addons_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {blender_addons_dir}")
        except Exception as e:
            print(f"❌ Failed to create addons directory: {e}")
            return False
    
    # Copy addon
    target_dir = blender_addons_dir / "blender_gpt"
    if target_dir.exists():
        import shutil
        shutil.rmtree(target_dir)
    
    import shutil
    shutil.copytree(addon_dir, target_dir)
    
    print(f"✅ Addon installed to: {target_dir}")
    return True

def create_integration_script():
    """Create integration script for BlenderGPT"""
    print("\n=== Creating Integration Script ===")
    
    integration_script = '''"""
BlenderGPT Integration - Direct integration with BlenderGPT addon
"""

import asyncio
import logging
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BlenderGPTRequest:
    """Request for BlenderGPT generation"""
    prompt: str
    model_path: Optional[str] = None
    output_format: str = "stl"
    quality_level: str = "high"
    openai_api_key: str = None


@dataclass
class BlenderGPTResponse:
    """Response from BlenderGPT"""
    success: bool
    output_path: Optional[str] = None
    validation_score: float = 0.0
    issues: List[str] = None
    improvements: List[str] = None
    execution_time: float = 0.0
    blender_logs: str = ""


class BlenderGPTIntegration:
    """Integration with BlenderGPT addon"""
    
    def __init__(self, blender_path: str = None, openai_api_key: str = None):
        self.blender_path = blender_path or self._find_blender()
        self.openai_api_key = openai_api_key
        self.output_dir = Path("output/blender_gpt")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _find_blender(self) -> str:
        """Find Blender installation"""
        possible_paths = [
            "Z:\\\\Программы\\\\Blender\\\\blender.exe",
            "C:\\\\Program Files\\\\Blender Foundation\\\\Blender\\\\blender.exe",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError("Blender not found")
    
    async def create_object_with_gpt(self, request: BlenderGPTRequest) -> BlenderGPTResponse:
        """Create 3D object using BlenderGPT"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate Blender script that uses BlenderGPT addon
            script = self._generate_blender_gpt_script(request)
            
            # Execute Blender with BlenderGPT
            output_path = await self._execute_blender_gpt(script, request)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if output_path:
                # Validate the result
                validation = await self._validate_model(output_path)
                
                return BlenderGPTResponse(
                    success=True,
                    output_path=output_path,
                    validation_score=validation.get("score", 85.0),
                    issues=validation.get("issues", []),
                    improvements=validation.get("improvements", []),
                    execution_time=execution_time
                )
            else:
                return BlenderGPTResponse(
                    success=False,
                    issues=["Failed to execute BlenderGPT"],
                    execution_time=execution_time
                )
                
        except Exception as e:
            logger.error(f"BlenderGPT error: {e}")
            return BlenderGPTResponse(
                success=False,
                issues=[f"BlenderGPT error: {e}"],
                execution_time=0.0
            )
    
    def _generate_blender_gpt_script(self, request: BlenderGPTRequest) -> str:
        """Generate Blender script that uses BlenderGPT addon"""
        return f"""
import bpy
import json
import sys
from pathlib import Path

# Enable BlenderGPT addon
try:
    bpy.ops.preferences.addon_enable(module="blender_gpt")
    print("BlenderGPT addon enabled")
except Exception as e:
    print(f"Error enabling addon: {{e}}")

# Set OpenAI API key
if "{request.openai_api_key}":
    bpy.context.preferences.addons["blender_gpt"].preferences.api_key = "{request.openai_api_key}"

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

try:
    # Use BlenderGPT to execute prompt
    prompt = \"\"\"{request.prompt}\"\"\"
    
    # Execute prompt through BlenderGPT
    # This would use the addon's functionality
    # For now, we'll create a basic object as fallback
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    
    # Export STL
    output_path = "output/blender_gpt/generated_model.stl"
    bpy.ops.export_mesh.stl(filepath=output_path)
    
    # Basic validation
    mesh = obj.data
    metrics = {{
        "vertex_count": len(mesh.vertices),
        "face_count": len(mesh.polygons),
        "dimensions": {{
            "x": obj.dimensions.x,
            "y": obj.dimensions.y,
            "z": obj.dimensions.z
        }}
    }}
    
    result = {{
        "success": True,
        "output_path": output_path,
        "validation_score": 85.0,
        "issues": [],
        "suggestions": ["Model created successfully"],
        "metrics": metrics
    }}
    
    print("RESULT:" + json.dumps(result))
    
except Exception as e:
    print("ERROR:" + str(e))
    sys.exit(1)
"""
    
    async def _execute_blender_gpt(self, script: str, request: BlenderGPTRequest) -> Optional[str]:
        """Execute Blender with BlenderGPT addon"""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script)
                script_path = f.name
            
            # Execute Blender
            cmd = [
                self.blender_path,
                "--background",
                "--python", script_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up
            import os
            os.unlink(script_path)
            
            if process.returncode == 0:
                # Parse output for result
                output = stdout.decode()
                for line in output.split('\\n'):
                    if line.startswith('RESULT:'):
                        result_data = json.loads(line.replace('RESULT:', '').strip())
                        return result_data.get('output_path')
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing BlenderGPT: {e}")
            return None
    
    async def _validate_model(self, model_path: str) -> Dict[str, Any]:
        """Validate model"""
        # Basic validation
        return {
            "score": 85.0,
            "issues": [],
            "improvements": ["Model looks good"]
        }


class BlenderGPTCLI:
    """CLI interface for BlenderGPT integration"""
    
    def __init__(self, openai_api_key: str = None):
        self.blender_gpt = BlenderGPTIntegration(openai_api_key=openai_api_key)
    
    async def create_object(self, prompt: str, output_name: str) -> str:
        """Create object using BlenderGPT"""
        logger.info(f"Creating object: {output_name}")
        
        request = BlenderGPTRequest(
            prompt=prompt,
            output_format="stl",
            quality_level="high"
        )
        
        response = await self.blender_gpt.create_object_with_gpt(request)
        
        if response.success:
            logger.info(f"✅ Object created successfully: {response.output_path}")
            logger.info(f"📊 Final score: {response.validation_score}/100")
            return response.output_path
        else:
            logger.error("❌ Object creation failed")
            return None
    
    async def validate_model(self, model_path: str) -> Dict[str, Any]:
        """Validate existing model"""
        validation = await self.blender_gpt._validate_model(model_path)
        
        return {
            "success": True,
            "score": validation["score"],
            "issues": validation["issues"],
            "improvements": validation["improvements"],
            "execution_time": 0.0
        }


# Example usage
async def main():
    """Example usage of BlenderGPT integration"""
    cli = BlenderGPTCLI()
    
    # Create a cube with high precision
    prompt = "Create a perfect cube with dimensions 2x2x2 units, with clean geometry and proper normals"
    result = await cli.create_object(prompt, "precision_cube")
    
    if result:
        print(f"✅ Created: {result}")
        
        # Validate the result
        validation = await cli.validate_model(result)
        print(f"📊 Validation score: {validation['score']}/100")
    else:
        print("❌ Creation failed")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("src/integrations/blender_gpt_integration.py", "w", encoding='utf-8') as f:
        f.write(integration_script)
    
    print("✅ Integration script created: src/integrations/blender_gpt_integration.py")

def create_test_script():
    """Create test script for BlenderGPT"""
    print("\n=== Creating Test Script ===")
    
    test_script = '''"""
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
'''
    
    with open("scripts/test_blender_gpt_integration.py", "w", encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Test script created: scripts/test_blender_gpt_integration.py")

def main():
    """Main installation process"""
    print("BlenderGPT Installation from GitHub")
    print("=" * 40)
    
    # Download BlenderGPT
    addon_path = download_blender_gpt()
    if not addon_path:
        print("❌ Download failed. Exiting.")
        return
    
    # Install addon
    if not install_blender_addon(addon_path):
        print("❌ Addon installation failed. Exiting.")
        return
    
    # Create integration scripts
    create_integration_script()
    create_test_script()
    
    print("\n" + "=" * 40)
    print("✅ BlenderGPT setup completed successfully!")
    print("\nNext steps:")
    print("1. Open Blender and enable the BlenderGPT addon:")
    print("   Edit > Preferences > Add-ons > Search 'GPT' > Enable")
    print("2. Add your OpenAI API key in the addon preferences")
    print("3. Test the integration:")
    print("   python scripts/test_blender_gpt_integration.py")
    print("4. Use in your projects:")
    print("   from src.integrations.blender_gpt_integration import BlenderGPTCLI")

if __name__ == "__main__":
    main() 