import os
import asyncio
from src.integrations.blender_bridge_client import BlenderBridgeClient
from src.llm.openrouter_client import OpenRouterClient


class IterativeBlenderSolver:
    """
    An agent that iteratively attempts to solve a task in Blender by
    generating code, taking a screenshot, analyzing the result with a
    multimodal LLM, and refining the code.
    """
    def __init__(self, prompt: str, max_iterations: int = 3):
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.client = BlenderBridgeClient()
        self.llm_client = OpenRouterClient()
        self.output_dir = "output/iterative_solver"
        os.makedirs(self.output_dir, exist_ok=True)

    async def solve(self):
        """
        Starts the iterative solving process.
        """
        print(f"--- Starting Iterative Solver for prompt: '{self.prompt}' ---")

        status = await self.client.check_status()
        if status.get("status") != "running":
            print("!!! Blender Bridge is not running. Please start it in Blender first.")
            return

        current_code = self.get_initial_code()

        for i in range(self.max_iterations):
            iteration = i + 1
            print(f"\\n--- Iteration {iteration}/{self.max_iterations} ---")

            print("   1. Executing code in Blender...")
            await self.client.clear_scene()
            await asyncio.sleep(0.5)
            execution_result = await self.client.execute_code(current_code)
            if "error" in execution_result.get("status", ""):
                print(f"   [ERROR] Code execution failed: {execution_result.get('message')}")
                # Give the agent a chance to fix syntax errors
                current_code = await self.fix_execution_error(current_code, execution_result.get('message'))
                continue

            await asyncio.sleep(1)

            # 2. Take a screenshot
            print("   2. Taking screenshot...")
            screenshot_result = await self.client.take_screenshot()

            if "error" in screenshot_result.get("status", ""):
                print(f"   [ERROR] Screenshot failed: {screenshot_result.get('message')}")
                break
            
            screenshot_path = screenshot_result.get("filepath")
            if not screenshot_path:
                print(f"   [ERROR] Addon did not return a filepath for the screenshot.")
                break

            # Wait for the file to be physically written to disk
            print(f"   Waiting for screenshot file at: {screenshot_path}")
            max_wait_time = 5  # seconds
            wait_interval = 0.2
            waited_time = 0
            while not os.path.exists(screenshot_path) and waited_time < max_wait_time:
                await asyncio.sleep(wait_interval)
                waited_time += wait_interval
            
            if not os.path.exists(screenshot_path):
                print(f"   [ERROR] Screenshot file was not created within {max_wait_time} seconds.")
                break

            print(f"   Screenshot found! Analyzing...")

            print("   3. Analyzing result with multimodal LLM...")
            analysis_result = await self.analyze_and_refine_with_llm(screenshot_path, current_code)

            if analysis_result.get("is_solved"):
                print("\\n--- Task Solved! ---")
                print(f"LLM confirmed the result is satisfactory in iteration {iteration}.")
                break
            
            print(f"   LLM Critique: {analysis_result['critique']}")
            current_code = analysis_result["new_code"]
            print("   Generated new code for next iteration.")
        
        else:
            print("\\n--- Max iterations reached. ---")

    async def fix_execution_error(self, broken_code, error_message):
        # A simplified version of self-correction for syntax errors
        print(f"   Attempting to fix execution error: {error_message}")
        # In a real system, a specific prompt would be used to fix the code.
        # Here we just re-engage the main analysis loop.
        return (await self.analyze_and_refine_with_llm(None, broken_code, error_message))['new_code']

    def get_initial_code(self) -> str:
        """
        Generates the first version of the code. Starts with a very simple attempt.
        """
        print("   Generating initial code: a simple cube.")
        return "bpy.ops.mesh.primitive_cube_add()"

    async def analyze_and_refine_with_llm(self, image_path: str, current_code: str, error_message: str = None) -> dict:
        """
        Uses the OpenRouterClient to get a visual critique and new code.
        """
        critique, new_code = "", ""
        
        if image_path: # Standard visual analysis
            response = await self.llm_client.get_visual_critique_and_code(image_path, self.prompt, current_code)
            critique, new_code = response['critique'], response['new_code']
        elif error_message: # Handle cases where code execution fails
            # This would be a different, more targeted prompt in a full implementation
            response = await self.llm_client.get_visual_critique_and_code(None, self.prompt, current_code, error_message)
            critique, new_code = response['critique'], response['new_code']

        if not new_code:
            print("   [ERROR] LLM did not return new code. Stopping.")
            return {"is_solved": True, "critique": critique, "new_code": current_code}

        # Simple check for whether the task is considered solved
        is_solved = "SOLVED" in critique.upper() or "SUCCESS" in critique.upper()

        return {"is_solved": is_solved, "critique": critique, "new_code": new_code}


if __name__ == "__main__":
    # Ensure you have OPENROUTER_API_KEY in your .env file
    async def run_solver():
        solver = IterativeBlenderSolver(prompt="Create a sharp, dynamic Nike logo.")
        await solver.solve()

    try:
        asyncio.run(run_solver())
    except KeyboardInterrupt:
        print("\\nExecution cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}") 