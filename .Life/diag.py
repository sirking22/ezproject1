import bpy
import traceback

print("--- BLENDER DIRECT DIAGNOSTIC SCRIPT (RESTORED) ---")
try:
    print("--> Clearing scene...")
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    if bpy.context.selected_objects:
        bpy.ops.object.delete(use_global=False)
    print("--> Scene cleared.")
    
    print("--> Adding Suzanne (monkey)...")
    bpy.ops.mesh.primitive_monkey_add(size=3, location=(0,0,0))
    print("--> Suzanne added.")
    
except Exception:
    print("\\n--- !!! ERROR IN BLENDER SCRIPT !!! ---")
    print(traceback.format_exc())

print("--- SCRIPT FINISHED. You can close Blender. ---") 