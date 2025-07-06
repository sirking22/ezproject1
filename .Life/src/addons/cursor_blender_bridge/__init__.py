bl_info = {
    "name": "Cursor-Blender Bridge",
    "author": "AI Assistant & User",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Cursor Bridge",
    "description": "Control Blender from Cursor.",
    "category": "Development",
}

import bpy
import threading
import json
import os
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from bpy.app.handlers import persistent

# --- Globals for server management ---
SERVER_THREAD = None
HTTP_SERVER = None
HOST = 'localhost'
PORT = 8008

# --- API Logic ---
class BlenderApiRequestHandler(BaseHTTPRequestHandler):
    """
    Handles HTTP requests for the Blender Bridge.
    """
    def do_POST(self):
        if self.path == '/execute':
            self.handle_execute()
        elif self.path == '/screenshot':
            self.handle_screenshot()
        else:
            self._send_error(404, "Endpoint not found.")

    def handle_execute(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            code_to_execute = data.get('code')
            
            if code_to_execute:
                bpy.app.timers.register(lambda: self.execute_in_main_thread(code_to_execute))
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Command deferred for execution."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self._send_error(400, "Missing 'code' in request body.")
        except Exception as e:
            self._send_error(500, f"Error processing request: {e}")

    def handle_screenshot(self):
        try:
            # Path is now predefined for reliability
            home_dir = os.path.expanduser('~')
            filepath = os.path.join(home_dir, 'blender_screenshot.png')

            bpy.app.timers.register(lambda: self.take_screenshot_in_main_thread(filepath))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "success", "message": f"Screenshot deferred to be saved at {filepath}", "filepath": filepath}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self._send_error(500, f"Error processing screenshot request: {e}")

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "running", "blender_version": bpy.app.version_string}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/scene_info':
            try:
                # Defer to main thread to ensure context access
                bpy.app.timers.register(self.get_scene_info_in_main_thread)
                # For now, just send a deferred response. The real data would need a more complex async mechanism.
                # A simple implementation is to write to a global and fetch on another request, but let's keep it simple.
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Scene info retrieval deferred. Not yet implemented for direct response."}
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                self._send_error(500, f"Error getting scene info: {e}")
        else:
            self._send_error(404, "Endpoint not found.")

    def execute_in_main_thread(self, code):
        """
        Executes the provided Python code string within Blender's main thread.
        """
        try:
            # Using a restricted globals dict for some safety
            exec(code, {'bpy': bpy})
            print(f"[Cursor Bridge] Executed: {code}")
        except Exception as e:
            print(f"[Cursor Bridge] Error executing code: {e}")
        return None # Returning None cancels the timer

    def take_screenshot_in_main_thread(self, filepath):
        """Saves a screenshot of the 3D Viewport."""
        try:
            # Ensure the directory exists
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Find the 3D View area to screenshot
            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            
            # Temporarily override context for the screenshot operator
            with bpy.context.temp_override(
                window=bpy.context.window,
                area=area,
                region=next(region for region in area.regions if region.type == 'WINDOW'),
                screen=bpy.context.screen
            ):
                bpy.ops.screen.screenshot(filepath=filepath, full=False)

            print(f"[Cursor Bridge] Screenshot saved to {filepath}")
        except Exception as e:
            print(f"[Cursor Bridge] Error taking screenshot: {e}")
        return None

    def get_scene_info_in_main_thread(self):
        try:
            object_names = [obj.name for obj in bpy.data.objects]
            # The challenge is getting this data *back* to the HTTP response.
            # For now, we just print it.
            print(f"[Cursor Bridge] Scene Objects: {object_names}")
        except Exception as e:
            print(f"[Cursor Bridge] Error getting scene info: {e}")
        return None

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"status": "error", "message": message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def log_message(self, format, *args):
        # Quiet the server logging to the console
        return

# --- Server Control ---
def start_server():
    global HTTP_SERVER, SERVER_THREAD
    if SERVER_THREAD is not None and SERVER_THREAD.is_alive():
        print("[Cursor Bridge] Server is already running.")
        return

    try:
        HTTP_SERVER = HTTPServer((HOST, PORT), BlenderApiRequestHandler)
        print(f"[Cursor Bridge] Starting server on http://{HOST}:{PORT}")
        SERVER_THREAD = threading.Thread(target=HTTP_SERVER.serve_forever)
        SERVER_THREAD.daemon = True
        SERVER_THREAD.start()
    except Exception as e:
        print(f"[Cursor Bridge] Could not start server: {e}")
        HTTP_SERVER = None


def stop_server():
    global HTTP_SERVER, SERVER_THREAD
    if HTTP_SERVER is not None:
        print("[Cursor Bridge] Stopping server...")
        HTTP_SERVER.shutdown()
        HTTP_SERVER.server_close()
        SERVER_THREAD.join()
        HTTP_SERVER = None
        SERVER_THREAD = None
        print("[Cursor Bridge] Server stopped.")

# --- Blender UI Panel ---
class CURSORBRIDGE_PT_Panel(bpy.types.Panel):
    bl_label = "Cursor Bridge"
    bl_idname = "OBJECT_PT_cursor_bridge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cursor Bridge'

    def draw(self, context):
        layout = self.layout
        if HTTP_SERVER is None:
            layout.operator("cursor_bridge.start_operator", text="Start Bridge", icon='PLAY')
        else:
            layout.operator("cursor_bridge.stop_operator", text="Stop Bridge", icon='PAUSE')
        
        col = layout.column()
        col.label(text="Status:")
        if HTTP_SERVER is not None:
             col.label(text=f"Running on http://{HOST}:{PORT}", icon='WORLD_DATA')
        else:
             col.label(text="Stopped", icon='CANCEL')


# --- Operators ---
class CURSORBRIDGE_OT_StartOperator(bpy.types.Operator):
    bl_idname = "cursor_bridge.start_operator"
    bl_label = "Start Cursor Bridge"
    
    def execute(self, context):
        start_server()
        return {'FINISHED'}

class CURSORBRIDGE_OT_StopOperator(bpy.types.Operator):
    bl_idname = "cursor_bridge.stop_operator"
    bl_label = "Stop Cursor Bridge"

    def execute(self, context):
        stop_server()
        return {'FINISHED'}

# --- Addon Registration ---
classes = (
    CURSORBRIDGE_PT_Panel,
    CURSORBRIDGE_OT_StartOperator,
    CURSORBRIDGE_OT_StopOperator,
)

@persistent
def load_handler(dummy):
    # This function is called on file load.
    # You could potentially auto-start the server here if desired.
    print("[Cursor Bridge] Blender file loaded.")
    # start_server() # Uncomment to autostart on file load

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    # Ensure server is stopped when addon is disabled
    stop_server()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(load_handler)

if __name__ == "__main__":
    register()
    # To test running the server directly from Blender's text editor
    # start_server() 