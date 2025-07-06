"""
Blender LLM Integration - Advanced 3D model generation using LLM
Alternative to BlenderGPT with direct LLM integration
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
class LLMRequest:
    """Request for LLM-powered Blender generation"""
    prompt: str
    model_path: Optional[str] = None
    output_format: str = "stl"
    quality_level: str = "high"
    validation_checks: List[str] = None


@dataclass
class LLMResponse:
    """Response from LLM-powered generation"""
    success: bool
    output_path: Optional[str] = None
    validation_score: float = 0.0
    issues: List[str] = None
    improvements: List[str] = None
    execution_time: float = 0.0
    blender_logs: str = ""
    llm_response: str = ""


class BlenderLLMIntegration:
    """Integration with LLM for advanced 3D generation"""
    
    def __init__(self, blender_path: str = None, llm_api_key: str = None):
        self.blender_path = blender_path or self._find_blender()
        self.llm_api_key = llm_api_key
        self.output_dir = Path("output/blender_llm")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _find_blender(self) -> str:
        """Find Blender installation"""
        possible_paths = [
            "Z:\\Программы\\Blender\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError("Blender not found")
    
    async def create_object_with_llm(self, request: LLMRequest) -> LLMResponse:
        """Create 3D object using LLM-powered generation"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate Blender script using LLM
            script = await self._generate_blender_script_with_llm(request)
            
            if not script:
                return LLMResponse(
                    success=False,
                    issues=["Failed to generate Blender script with LLM"],
                    execution_time=0.0
                )
            
            # Execute Blender script
            output_path = await self._execute_blender_script(script, request)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if output_path:
                # Validate the result
                validation = await self._validate_model_with_llm(output_path, request)
                
                return LLMResponse(
                    success=True,
                    output_path=output_path,
                    validation_score=validation.get("score", 85.0),
                    issues=validation.get("issues", []),
                    improvements=validation.get("improvements", []),
                    execution_time=execution_time,
                    llm_response=script
                )
            else:
                return LLMResponse(
                    success=False,
                    issues=["Failed to execute Blender script"],
                    execution_time=execution_time,
                    llm_response=script
                )
                
        except Exception as e:
            logger.error(f"LLM integration error: {e}")
            return LLMResponse(
                success=False,
                issues=[f"LLM integration error: {e}"],
                execution_time=0.0
            )
    
    async def _generate_blender_script_with_llm(self, request: LLMRequest) -> str:
        """Generate Blender script using LLM"""
        try:
            # Create prompt for LLM
            llm_prompt = self._create_script_generation_prompt(request)
            
            # Call LLM (simplified - you can integrate with OpenAI, Anthropic, etc.)
            script = await self._call_llm(llm_prompt)
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating script with LLM: {e}")
            return None
    
    def _create_script_generation_prompt(self, request: LLMRequest) -> str:
        """Create prompt for script generation"""
        base_prompt = f"""
Generate a Blender Python script that creates a 3D object based on this description:

"{request.prompt}"

Requirements:
- Use Blender 4.4 API
- Create clean, manifold geometry
- Export as {request.output_format.upper()}
- Quality level: {request.quality_level}
- Include proper error handling
- Add validation checks: {request.validation_checks or ['geometry', 'manifold']}

If modifying an existing model, use this path: {request.model_path or 'N/A'}

The script should:
1. Clear the scene
2. Create the object
3. Apply materials if needed
4. Validate geometry
5. Export the result
6. Print validation results

Return only the Python script, no explanations.
"""
        return base_prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM service (placeholder - implement with your preferred LLM)"""
        # This is a placeholder - you can integrate with:
        # - OpenAI GPT-4
        # - Anthropic Claude
        # - Local LLM (Ollama, etc.)
        # - OpenRouter API
        
        # For now, return a basic template
        return self._get_basic_blender_script_template()
    
    def _get_basic_blender_script_template(self) -> str:
        """Get basic Blender script template"""
        return '''
import bpy
import bmesh
import json
import sys
from pathlib import Path

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

try:
    # Create a basic cube (placeholder)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    
    # Add subdivision for better quality
    bpy.ops.object.modifier_add(type='SUBSURF')
    obj.modifiers["Subdivision"].levels = 2
    
    # Apply modifiers
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    
    # Get mesh data for validation
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Calculate metrics
    metrics = {
        "vertex_count": len(bm.verts),
        "face_count": len(bm.faces),
        "edge_count": len(bm.edges),
        "volume": bm.calc_volume(),
        "surface_area": sum(f.calc_area() for f in bm.faces),
        "bounding_box": {
            "x": obj.dimensions.x,
            "y": obj.dimensions.y,
            "z": obj.dimensions.z
        }
    }
    
    # Validation
    issues = []
    suggestions = []
    
    if metrics["face_count"] == 0:
        issues.append("No faces found")
    if metrics["vertex_count"] == 0:
        issues.append("No vertices found")
    
    # Check for non-manifold edges
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    if non_manifold_edges:
        issues.append(f"Found {len(non_manifold_edges)} non-manifold edges")
    
    # Calculate score
    score = 100.0
    if issues:
        score -= len(issues) * 10
    score = max(0, min(100, score))
    
    # Export STL
    output_path = "output/blender_llm/generated_model.stl"
    bpy.ops.export_mesh.stl(filepath=output_path)
    
    # Print results
    result = {
        "success": True,
        "output_path": output_path,
        "validation_score": score,
        "issues": issues,
        "suggestions": suggestions,
        "metrics": metrics
    }
    
    print("RESULT:" + json.dumps(result))
    
    bm.free()
    
except Exception as e:
    print("ERROR:" + str(e))
    sys.exit(1)
'''
    
    async def _execute_blender_script(self, script: str, request: LLMRequest) -> Optional[str]:
        """Execute Blender script"""
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
                for line in output.split('\n'):
                    if line.startswith('RESULT:'):
                        result_data = json.loads(line.replace('RESULT:', '').strip())
                        return result_data.get('output_path')
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing Blender script: {e}")
            return None
    
    async def _validate_model_with_llm(self, model_path: str, request: LLMRequest) -> Dict[str, Any]:
        """Validate model using LLM"""
        # This would use LLM to analyze the model
        # For now, return basic validation
        return {
            "score": 85.0,
            "issues": [],
            "improvements": ["Model looks good"]
        }


class IterativeBlenderLLM:
    """Iterative improvement using LLM-powered Blender"""
    
    def __init__(self, blender_llm: BlenderLLMIntegration):
        self.blender_llm = blender_llm
        self.max_iterations = 5
        self.min_score = 85.0
        
    async def improve_model_iteratively(self, 
                                      initial_prompt: str,
                                      target_metrics: Dict[str, Any] = None,
                                      base_model: str = None) -> List[LLMResponse]:
        """Iteratively improve model using LLM"""
        results = []
        current_model = base_model
        
        for iteration in range(self.max_iterations):
            logger.info(f"LLM iteration {iteration + 1}")
            
            # Build improved prompt
            prompt = self._build_iterative_prompt(initial_prompt, iteration, results, target_metrics)
            
            # Create request
            request = LLMRequest(
                prompt=prompt,
                model_path=current_model,
                quality_level="high",
                validation_checks=["geometry", "manifold", "overlapping"]
            )
            
            # Execute LLM generation
            response = await self.blender_llm.create_object_with_llm(request)
            results.append(response)
            
            logger.info(f"Iteration {iteration + 1}: Score = {response.validation_score}")
            
            # Check if we've reached target quality
            if response.validation_score >= self.min_score and response.success:
                logger.info(f"Target quality reached after {iteration + 1} iterations")
                break
            
            # Update current model for next iteration
            if response.output_path:
                current_model = response.output_path
        
        return results
    
    def _build_iterative_prompt(self, 
                               base_prompt: str, 
                               iteration: int, 
                               previous_results: List[LLMResponse],
                               target_metrics: Dict[str, Any] = None) -> str:
        """Build improved prompt based on previous results"""
        prompt = base_prompt
        
        if iteration > 0 and previous_results:
            last_result = previous_results[-1]
            
            # Add improvement instructions
            if last_result.issues:
                prompt += f"\n\nIssues to fix: {', '.join(last_result.issues)}"
            
            if last_result.improvements:
                prompt += f"\n\nApply these improvements: {', '.join(last_result.improvements)}"
            
            # Add quality target
            if target_metrics:
                prompt += f"\n\nTarget metrics: {target_metrics}"
            
            # Add iteration context
            prompt += f"\n\nThis is iteration {iteration + 1}. Improve the model based on previous issues."
        
        return prompt


class BlenderLLMCLI:
    """CLI interface for LLM-powered Blender integration"""
    
    def __init__(self, llm_api_key: str = None):
        self.blender_llm = BlenderLLMIntegration(llm_api_key=llm_api_key)
        self.iterative = IterativeBlenderLLM(self.blender_llm)
    
    async def create_object(self, prompt: str, output_name: str, iterations: int = 3) -> str:
        """Create object using LLM-powered generation"""
        logger.info(f"Creating object: {output_name}")
        
        # Run iterative improvement
        results = await self.iterative.improve_model_iteratively(
            prompt, 
            max_iterations=iterations
        )
        
        # Get final result
        final_result = results[-1] if results else None
        
        if final_result and final_result.success:
            logger.info(f"✅ Object created successfully: {final_result.output_path}")
            logger.info(f"📊 Final score: {final_result.validation_score}/100")
            return final_result.output_path
        else:
            logger.error("❌ Object creation failed")
            return None
    
    async def validate_model(self, model_path: str) -> Dict[str, Any]:
        """Validate existing model using LLM"""
        request = LLMRequest(
            prompt=f"Validate and analyze this 3D model: {model_path}. Check for geometry issues, manifold problems, and provide quality score.",
            model_path=model_path,
            validation_checks=["geometry", "manifold", "overlapping", "normals"]
        )
        
        response = await self.blender_llm.create_object_with_llm(request)
        
        return {
            "success": response.success,
            "score": response.validation_score,
            "issues": response.issues or [],
            "improvements": response.improvements or [],
            "execution_time": response.execution_time
        }


# Example usage
async def main():
    """Example usage of LLM-powered Blender integration"""
    cli = BlenderLLMCLI()
    
    # Create a cube with high precision
    prompt = "Create a perfect cube with dimensions 2x2x2 units, with clean geometry and proper normals"
    result = await cli.create_object(prompt, "precision_cube", iterations=3)
    
    if result:
        print(f"✅ Created: {result}")
        
        # Validate the result
        validation = await cli.validate_model(result)
        print(f"📊 Validation score: {validation['score']}/100")
    else:
        print("❌ Creation failed")


if __name__ == "__main__":
    asyncio.run(main()) 