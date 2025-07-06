"""
Quick viewer for STL files
Simple script to view generated STL files
"""

import os
import sys
import subprocess
from pathlib import Path

def open_stl_file(file_path: str):
    """Open STL file with default application"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    try:
        if sys.platform == "win32":
            os.startfile(str(file_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(file_path)])
        else:
            subprocess.run(["xdg-open", str(file_path)])
        
        print(f"Opened: {file_path}")
    except Exception as e:
        print(f"Error opening file: {e}")

def list_stl_files(directory: str = "cache/blender"):
    """List all STL files in directory"""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Directory not found: {dir_path}")
        return []
    
    stl_files = list(dir_path.glob("*.stl"))
    
    if not stl_files:
        print(f"No STL files found in {dir_path}")
        return []
    
    print(f"Found {len(stl_files)} STL files:")
    for i, file_path in enumerate(stl_files, 1):
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  {i}. {file_path.name} ({size_mb:.2f} MB)")
    
    return stl_files

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Open specific file
        file_path = sys.argv[1]
        open_stl_file(file_path)
    else:
        # List and let user choose
        stl_files = list_stl_files()
        
        if stl_files:
            try:
                choice = input("\nEnter file number to open (or 'q' to quit): ")
                if choice.lower() != 'q':
                    index = int(choice) - 1
                    if 0 <= index < len(stl_files):
                        open_stl_file(stl_files[index])
                    else:
                        print("Invalid file number")
            except (ValueError, KeyboardInterrupt):
                print("\nExiting...")

if __name__ == "__main__":
    main() 