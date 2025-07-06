"""
Test script for iterative 3D model creation with validation
Demonstrates the complete workflow with quality assessment
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_engine import BlenderEngine, ObjectSpec, ObjectType, MaterialType, Vector3
from integrations.blender_validator import BlenderValidator, IterativeImprover, QualityReporter

async def test_iterative_cube():
    """Test iterative cube creation with validation"""
    print("=== Testing Iterative Cube Creation ===")
    
    # Initialize components
    engine = BlenderEngine()
    validator = BlenderValidator()
    improver = IterativeImprover(engine, validator)
    
    # Create initial specification
    spec = ObjectSpec(
        name="iterative_test_cube",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, 0),
        dimensions=Vector3(2, 2, 2),
        material_type=MaterialType.METAL
    )
    
    # Run iterative improvement
    print("Starting iterative improvement process...")
    results = await improver.improve_model(spec, target_metrics={"face_count": 50})
    
    # Generate and display report
    reporter = QualityReporter()
    report = reporter.generate_report(results)
    
    print("\n" + "="*50)
    print("QUALITY REPORT")
    print("="*50)
    print(report)
    
    # Save report
    report_path = Path("output/quality_reports")
    report_path.mkdir(parents=True, exist_ok=True)
    
    with open(report_path / "iterative_test_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path / 'iterative_test_report.md'}")
    
    return results

async def test_nike_logo_validation():
    """Test validation of existing Nike logo"""
    print("\n=== Testing Nike Logo Validation ===")
    
    # Create a simple Nike logo first
    engine = BlenderEngine()
    spec = ObjectSpec(
        name="validation_test_nike",
        object_type=ObjectType.NIKE_LOGO,
        extrude_depth=0.1
    )
    
    model_path = await engine.create_object(spec)
    print(f"Created Nike logo: {model_path}")
    
    # Validate it
    validator = BlenderValidator()
    validation = await validator.validate_stl_file(model_path)
    
    print(f"Validation Score: {validation.score}/100")
    print(f"Valid: {'✅ Yes' if validation.is_valid else '❌ No'}")
    print(f"Issues: {len(validation.issues)}")
    print(f"Suggestions: {len(validation.suggestions)}")
    
    if validation.issues:
        print("\nIssues found:")
        for issue in validation.issues:
            print(f"  - {issue}")
    
    if validation.suggestions:
        print("\nSuggestions:")
        for suggestion in validation.suggestions:
            print(f"  - {suggestion}")
    
    return validation

async def test_cli_commands():
    """Test CLI commands for iterative creation"""
    print("\n=== Testing CLI Commands ===")
    
    # This would test the CLI commands we added
    print("CLI commands available:")
    print("  python -m src.integrations.blender_cli_integration iterative cube test_cube --target-score 85 --max-iterations 3")
    print("  python -m src.integrations.blender_cli_integration validate cache/blender/test.stl --output-report validation_report.md")

async def main():
    """Run all tests"""
    print("Starting Iterative 3D Model Creation Tests\n")
    
    try:
        # Test iterative cube creation
        cube_results = await test_iterative_cube()
        
        # Test Nike logo validation
        nike_validation = await test_nike_logo_validation()
        
        # Test CLI commands info
        await test_cli_commands()
        
        print("\n=== All Tests Completed Successfully ===")
        
        # Summary
        print(f"\nSummary:")
        print(f"- Iterative cube: {len(cube_results)} iterations")
        print(f"- Nike logo validation score: {nike_validation.score}/100")
        print(f"- Quality reports saved to: output/quality_reports/")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 