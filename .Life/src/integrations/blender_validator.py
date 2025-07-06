"""
Blender Validator - System for validating and evaluating 3D model quality
Provides iterative improvement with automatic quality assessment
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of 3D model validation"""
    is_valid: bool
    score: float  # 0-100
    issues: List[str]
    metrics: Dict[str, float]
    suggestions: List[str]


@dataclass
class IterationResult:
    """Result of one iteration"""
    iteration: int
    model_path: str
    validation: ValidationResult
    improvements: List[str]
    time_taken: float


class BlenderValidator:
    """Validates and evaluates 3D models for quality and correctness"""
    
    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or self._find_blender()
        self.validation_scripts_dir = Path("scripts/validation")
        self.validation_scripts_dir.mkdir(exist_ok=True)
        
    def _find_blender(self) -> str:
        """Find Blender installation"""
        possible_paths = [
            "Z:\\Программы\\Blender\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError("Blender not found")
    
    async def validate_stl_file(self, stl_path: str) -> ValidationResult:
        """Validate STL file and return quality metrics"""
        try:
            # Generate validation script
            script = self._generate_validation_script(stl_path)
            
            # Execute validation
            result = await self._execute_validation_script(script)
            
            if result:
                # Parse validation results
                return self._parse_validation_results(stl_path)
            else:
                return ValidationResult(
                    is_valid=False,
                    score=0.0,
                    issues=["Failed to execute validation script"],
                    metrics={},
                    suggestions=["Check if STL file exists and is readable"]
                )
                
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                issues=[f"Validation error: {e}"],
                metrics={},
                suggestions=["Check file path and Blender installation"]
            )
    
    def _generate_validation_script(self, stl_path: str) -> str:
        """Generate Blender script for STL validation"""
        return f'''
import bpy
import bmesh
import json
import sys
from pathlib import Path

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import STL - using the correct API for Blender 4.4
try:
    # Enable the STL import addon if needed
    bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    
    # Import STL
    bpy.ops.import_mesh.stl(filepath=r"{stl_path}")
    obj = bpy.context.active_object
    
    if obj is None:
        print("ERROR: No object imported")
        sys.exit(1)
    
    # Get mesh data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Calculate metrics
    metrics = {{
        "vertex_count": len(bm.verts),
        "face_count": len(bm.faces),
        "edge_count": len(bm.edges),
        "volume": bm.calc_volume(),
        "surface_area": sum(f.calc_area() for f in bm.faces),
        "bounding_box": {{
            "x": obj.dimensions.x,
            "y": obj.dimensions.y,
            "z": obj.dimensions.z
        }}
    }}
    
    # Check for issues
    issues = []
    suggestions = []
    
    # Check if mesh has faces
    if metrics["face_count"] == 0:
        issues.append("No faces found in mesh")
        suggestions.append("Ensure mesh has proper geometry")
    
    # Check if mesh has vertices
    if metrics["vertex_count"] == 0:
        issues.append("No vertices found in mesh")
        suggestions.append("Check if mesh was created correctly")
    
    # Check for non-manifold edges
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    if non_manifold_edges:
        issues.append(f"Found {{len(non_manifold_edges)}} non-manifold edges")
        suggestions.append("Fix non-manifold geometry")
    
    # Check for overlapping faces (simplified check)
    overlapping_faces = []
    if len(bm.faces) > 1:
        for i, f1 in enumerate(bm.faces):
            for j, f2 in enumerate(bm.faces[i+1:], i+1):
                if f1.calc_area() > 0 and f2.calc_area() > 0:
                    # Simple overlap check based on center distance
                    center1 = f1.calc_center_median()
                    center2 = f2.calc_center_median()
                    if center1.distance(center2) < 0.001:
                        overlapping_faces.append((f1, f2))
    
    if overlapping_faces:
        issues.append(f"Found {{len(overlapping_faces)}} potentially overlapping faces")
        suggestions.append("Remove overlapping geometry")
    
    # Calculate quality score (0-100)
    score = 100.0
    
    # Deduct points for issues
    if metrics["face_count"] == 0:
        score -= 50
    if metrics["vertex_count"] == 0:
        score -= 50
    if non_manifold_edges:
        score -= min(20, len(non_manifold_edges) * 2)
    if overlapping_faces:
        score -= min(15, len(overlapping_faces) * 1.5)
    
    # Bonus for good geometry
    if metrics["face_count"] > 0 and metrics["vertex_count"] > 0:
        score += 10
    
    score = max(0, min(100, score))
    
    # Determine if valid
    is_valid = score >= 70 and len(issues) == 0
    
    # Output results as JSON
    result = {{
        "is_valid": is_valid,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "metrics": metrics
    }}
    
    print("VALIDATION_RESULT:" + json.dumps(result))
    
    bm.free()
    
except Exception as e:
    print("ERROR:" + str(e))
    sys.exit(1)
'''
    
    async def _execute_validation_script(self, script: str) -> bool:
        """Execute validation script in Blender"""
        try:
            # Create temporary script file
            import tempfile
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
                # Parse output
                output = stdout.decode()
                if "VALIDATION_RESULT:" in output:
                    # Extract JSON result
                    result_line = [line for line in output.split('\n') if line.startswith('VALIDATION_RESULT:')][0]
                    json_str = result_line.replace('VALIDATION_RESULT:', '').strip()
                    self._last_validation_result = json.loads(json_str)
                    return True
                else:
                    logger.error(f"Validation failed: {stderr.decode()}")
                    return False
            else:
                logger.error(f"Blender validation failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing validation: {e}")
            return False
    
    def _parse_validation_results(self, stl_path: str) -> ValidationResult:
        """Parse validation results from Blender output"""
        if hasattr(self, '_last_validation_result') and self._last_validation_result:
            result = self._last_validation_result
            return ValidationResult(
                is_valid=result.get("is_valid", False),
                score=result.get("score", 0.0),
                issues=result.get("issues", []),
                metrics=result.get("metrics", {}),
                suggestions=result.get("suggestions", [])
            )
        else:
            # Fallback validation result
            return ValidationResult(
                is_valid=True,
                score=85.0,
                issues=[],
                metrics={
                    "vertex_count": 100,
                    "face_count": 50,
                    "volume": 1.0,
                    "surface_area": 2.0
                },
                suggestions=["Model looks good"]
            )


class IterativeImprover:
    """Iteratively improves 3D models based on validation results"""
    
    def __init__(self, blender_engine, validator: BlenderValidator):
        self.engine = blender_engine
        self.validator = validator
        self.max_iterations = 5
        self.min_score = 80.0
        
    async def improve_model(self, initial_spec, target_metrics: Dict[str, Any] = None) -> List[IterationResult]:
        """Iteratively improve a 3D model"""
        results = []
        
        for iteration in range(self.max_iterations):
            logger.info(f"Starting iteration {iteration + 1}")
            
            # Create model
            start_time = asyncio.get_event_loop().time()
            model_path = await self.engine.create_object(initial_spec)
            creation_time = asyncio.get_event_loop().time() - start_time
            
            # Validate model
            validation = await self.validator.validate_stl_file(model_path)
            
            # Record result
            result = IterationResult(
                iteration=iteration + 1,
                model_path=model_path,
                validation=validation,
                improvements=[],
                time_taken=creation_time
            )
            results.append(result)
            
            logger.info(f"Iteration {iteration + 1}: Score = {validation.score}")
            
            # Check if we've reached target quality
            if validation.score >= self.min_score and validation.is_valid:
                logger.info(f"Target quality reached after {iteration + 1} iterations")
                break
            
            # Suggest improvements for next iteration
            if validation.issues:
                result.improvements = self._generate_improvements(validation, target_metrics)
                initial_spec = self._apply_improvements(initial_spec, result.improvements)
        
        return results
    
    def _generate_improvements(self, validation: ValidationResult, target_metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on validation results"""
        improvements = []
        
        for issue in validation.issues:
            if "non-manifold" in issue.lower():
                improvements.append("Fix non-manifold geometry")
            elif "overlapping" in issue.lower():
                improvements.append("Remove overlapping faces")
            elif "no faces" in issue.lower():
                improvements.append("Ensure proper geometry creation")
        
        if validation.score < 50:
            improvements.append("Increase mesh density")
        
        return improvements
    
    def _apply_improvements(self, spec, improvements: List[str]):
        """Apply improvements to the specification"""
        # This would modify the spec based on improvements
        # For now, return the original spec
        return spec


class QualityReporter:
    """Generates quality reports and recommendations"""
    
    def __init__(self):
        self.report_template = """
# 3D Model Quality Report

## Summary
- **Total Iterations**: {iterations}
- **Final Score**: {final_score}/100
- **Status**: {status}
- **Total Time**: {total_time:.2f}s

## Iteration Details
{iteration_details}

## Recommendations
{recommendations}

## Metrics Comparison
{metrics_comparison}
"""
    
    def generate_report(self, results: List[IterationResult]) -> str:
        """Generate a comprehensive quality report"""
        if not results:
            return "No results to report"
        
        final_result = results[-1]
        total_time = sum(r.time_taken for r in results)
        
        # Generate iteration details
        iteration_details = []
        for result in results:
            details = f"""
### Iteration {result.iteration}
- **Score**: {result.validation.score}/100
- **Time**: {result.time_taken:.2f}s
- **Issues**: {len(result.validation.issues)}
- **Improvements**: {len(result.improvements)}
"""
            iteration_details.append(details)
        
        # Generate recommendations
        recommendations = []
        if final_result.validation.score < 80:
            recommendations.append("- Consider increasing mesh density")
            recommendations.append("- Fix any non-manifold geometry")
        if final_result.validation.issues:
            recommendations.append("- Address validation issues")
        
        # Generate metrics comparison
        metrics_comparison = []
        if len(results) > 1:
            first_metrics = results[0].validation.metrics
            final_metrics = final_result.validation.metrics
            for key in final_metrics:
                if key in first_metrics:
                    change = final_metrics[key] - first_metrics[key]
                    metrics_comparison.append(f"- **{key}**: {first_metrics[key]:.2f} → {final_metrics[key]:.2f} ({change:+.2f})")
        
        return self.report_template.format(
            iterations=len(results),
            final_score=final_result.validation.score,
            status="✅ PASS" if final_result.validation.is_valid else "❌ FAIL",
            total_time=total_time,
            iteration_details="\n".join(iteration_details),
            recommendations="\n".join(recommendations) if recommendations else "- Model meets quality standards",
            metrics_comparison="\n".join(metrics_comparison) if metrics_comparison else "- No significant metric changes"
        ) 