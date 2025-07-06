import httpx
import json
import asyncio
import math

class BlenderBridgeClient:
    """
    An async client to interact with the Cursor-Blender Bridge API.
    """
    def __init__(self, host: str = 'localhost', port: int = 8008):
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def check_status(self) -> dict:
        """
        Checks if the Blender Bridge server is running.
        """
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Connection failed: {e}"}

    async def execute_code(self, code: str) -> dict:
        """
        Sends a string of Python code to be executed in Blender.
        """
        try:
            payload = {"code": code}
            response = await self.client.post(f"{self.base_url}/execute", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Request failed: {e}"}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"Blender API returned an error: {e.response.text}"}

    async def clear_scene(self):
        """Deletes all objects in the scene."""
        code = "bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)"
        return await self.execute_code(code)

    async def create_nike_logo(self):
        """
        Creates a final, correct Nike logo using a single, non-twisted, 
        closed Bezier curve.
        """
        code = """
import bpy
import math

# The key is to define the points sequentially around the perimeter
# of the shape, so the cyclic spline doesn't twist.

curve_data = bpy.data.curves.new('NikeLogoShape', type='CURVE')
curve_data.dimensions = '2D'
curve_data.fill_mode = 'BOTH'

spline = curve_data.splines.new('BEZIER')
spline.use_cyclic_u = True # Connect last point to first
spline.bezier_points.add(3) # 4 points total

# Points are defined in order around the shape's perimeter
points = [
    # 1. Tail Tip (most negative X)
    {'co': (-4.2, 0.9, 0), 'h_l': (-4.8, 0.4, 0), 'h_r': (-3.5, 1.4, 0)},
    # 2. Top-Right Point
    {'co': (4.5, 1.4, 0), 'h_l': (2.0, -0.5, 0), 'h_r': (5.0, 1.8, 0)},
    # 3. Inner-Right Corner (the "point" of the swoosh)
    {'co': (2.0, 0.4, 0), 'h_l': (3.0, 0.8, 0), 'h_r': (1.0, 0.0, 0)},
    # 4. Bottom-Middle Point
    {'co': (0.0, -0.8, 0), 'h_l': (1.5, -1.2, 0), 'h_r': (-1.5, -0.4, 0)},
]

for i, p_data in enumerate(points):
    p = spline.bezier_points[i]
    p.co = p_data['co']
    p.handle_left = p_data['h_l']
    p.handle_right = p_data['h_r']
    p.handle_left_type = 'AUTO'
    p.handle_right_type = 'AUTO'

logo_obj = bpy.data.objects.new('NikeLogo', curve_data)
bpy.context.collection.objects.link(logo_obj)
bpy.context.view_layer.objects.active = logo_obj
logo_obj.select_set(True)

solidify = logo_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.2
solidify.offset = 0

logo_obj.rotation_euler[0] = math.radians(90)
logo_obj.location = (0, 0, 0) # Center the object

bpy.ops.object.convert(target='MESH')
"""
        return await self.execute_code(code)

    async def take_screenshot(self):
        """
        Requests the Blender Bridge to take a screenshot.
        The path is determined by the addon for reliability.
        """
        try:
            # No payload is needed, just a POST request to trigger the screenshot
            response = await self.client.post(f"{self.base_url}/screenshot", json={})
            response.raise_for_status()
            return response.json() # Response now contains the filepath
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Screenshot request failed: {e}"}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"Blender screenshot API returned an error: {e.response.text}"}


async def main():
    """
    An example of how to use the BlenderBridgeClient.
    """
    print("--- Blender Bridge Client Example ---")
    client = BlenderBridgeClient()

    print("\n1. Checking bridge status...")
    status = await client.check_status()
    print(f"   Status: {status}")

    if status.get("status") != "running":
        print("!!! Blender Bridge is not running. Please start it in Blender first.")
        return

    print("\n2. Clearing the scene...")
    result = await client.clear_scene()
    print(f"   Result: {result}")
    
    print("\n3. Creating Nike Logo...")
    result = await client.create_nike_logo()
    print(f"   Result: {result}")

    print("\n--- Example finished ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution cancelled by user.") 