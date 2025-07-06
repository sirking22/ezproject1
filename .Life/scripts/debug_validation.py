"""
Debug validation script execution
"""

import asyncio
import subprocess
import tempfile
import os
from pathlib import Path

async def debug_validation():
    """Debug validation script execution"""
    print("=== Debug Validation Script ===")
    
    # Find Blender
    blender_path = "Z:\\Программы\\Blender\\blender.exe"
    if not Path(blender_path).exists():
        print(f"Blender not found at: {blender_path}")
        return
    
    # Find a test STL file
    stl_files = list(Path("cache/blender").glob("*.stl"))
    if not stl_files:
        print("No STL files found")
        return
    
    test_stl = str(stl_files[0])
    print(f"Testing with: {test_stl}")
    
    # Create a simple validation script
    script = f'''
import bpy
import json
import sys

print("Script started")

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

print("Scene cleared")

# Import STL
try:
    bpy.ops.import_mesh.stl(filepath=r"{test_stl}")
    obj = bpy.context.active_object
    
    print(f"Object imported: {{obj.name if obj else 'None'}}")
    
    if obj is None:
        print("ERROR: No object imported")
        sys.exit(1)
    
    # Simple metrics
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
    
    print(f"Metrics calculated: {{metrics}}")
    
    # Simple validation
    score = 100.0
    issues = []
    suggestions = []
    
    if metrics["face_count"] == 0:
        score -= 50
        issues.append("No faces found")
    
    if metrics["vertex_count"] == 0:
        score -= 50
        issues.append("No vertices found")
    
    is_valid = score >= 70 and len(issues) == 0
    
    result = {{
        "is_valid": is_valid,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "metrics": metrics
    }}
    
    print("VALIDATION_RESULT:" + json.dumps(result))
    print("Script completed successfully")
    
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Create temporary script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    print(f"Created script: {script_path}")
    
    # Execute Blender
    cmd = [
        blender_path,
        "--background",
        "--python", script_path
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        print(f"Return code: {process.returncode}")
        print(f"Stdout: {stdout.decode()}")
        print(f"Stderr: {stderr.decode()}")
        
        # Clean up
        os.unlink(script_path)
        
    except Exception as e:
        print(f"Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_validation()) 