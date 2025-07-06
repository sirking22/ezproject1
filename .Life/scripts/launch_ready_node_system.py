#!/usr/bin/env python3
"""
Launcher for Ready-to-Go Advanced Node System
Opens Blender and runs the node system script
"""

import subprocess
import sys
import os
from pathlib import Path

def find_blender():
    """Find Blender executable"""
    possible_paths = [
        "blender",  # If in PATH
        "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.6/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.5/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.4/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.3/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.1/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.0/blender.exe",
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def main():
    """Main launcher function"""
    print("🚀 Ready-to-Go Node System Launcher")
    print("=" * 40)
    
    # Find Blender
    blender_path = find_blender()
    if not blender_path:
        print("❌ Blender not found!")
        print("Please install Blender or add it to PATH")
        return
    
    print(f"✅ Found Blender: {blender_path}")
    
    # Get script path
    script_dir = Path(__file__).parent
    node_script = script_dir / "ready_node_system.py"
    
    if not node_script.exists():
        print(f"❌ Script not found: {node_script}")
        return
    
    print(f"✅ Found script: {node_script}")
    
    # Create output directory
    output_dir = Path("output/blender")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Launch Blender with script
    print("🚀 Launching Blender with node system...")
    
    cmd = [
        blender_path,
        "--background",  # Run in background
        "--python", str(node_script),
        "--render-output", str(output_dir / "render_"),
        "--render-format", "PNG",
        "--render-frame", "1"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Node system created successfully!")
            print(f"💾 Scene saved: {output_dir}/ready_node_system.blend")
            print("🎯 Ready for rendering!")
        else:
            print("❌ Error running script:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Script timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 