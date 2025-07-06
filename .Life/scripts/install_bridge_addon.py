import shutil
from pathlib import Path
import os

def install_bridge_addon():
    """
    Copies the cursor_blender_bridge addon to the user's Blender scripts directory.
    """
    print("--- Installing Cursor-Blender Bridge Addon to User Directory ---")

    # 1. Find Blender user scripts path in AppData
    appdata_path = os.getenv('APPDATA')
    if not appdata_path:
        print("Error: APPDATA environment variable not found.")
        return

    addons_path = Path(appdata_path) / "Blender Foundation" / "Blender" / "4.4" / "scripts" / "addons"
    
    if not addons_path.exists():
        print(f"Warning: Blender addons path not found at '{addons_path}'. Creating it.")
        addons_path.mkdir(parents=True, exist_ok=True)

    # 2. Define source and destination
    source_dir = Path("src/addons/cursor_blender_bridge")
    if not source_dir.exists():
        print(f"Error: Source addon directory not found at '{source_dir}'")
        return

    destination_dir = addons_path / "cursor_blender_bridge"

    # 3. Copy the addon
    print(f"Copying addon from '{source_dir}' to '{destination_dir}'...")
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    
    shutil.copytree(source_dir, destination_dir)

    print("\n--- Installation Complete! ---")
    print(f"Addon installed to user directory: {destination_dir}")
    print("\nNext Steps:")
    print("1. RESTART Blender.")
    print("2. Go to Edit > Preferences > Add-ons.")
    print("3. Search for 'Cursor-Blender Bridge' and enable it (It should be under the 'Community' tab).")
    print("4. In the 3D Viewport, press 'N' to open the sidebar.")
    print("5. Find the 'Cursor Bridge' tab and click 'Start Bridge'.")

if __name__ == "__main__":
    install_bridge_addon() 