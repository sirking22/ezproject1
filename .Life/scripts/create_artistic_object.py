#!/usr/bin/env python3
"""
Создание художественного объекта через Blender
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.blender_engine import (
    BlenderEngine, ObjectSpec, SceneSpec, ObjectType, MaterialType,
    Vector3, RenderSpec, ExportSpec, ExportFormat
)

async def create_artistic_scene():
    """Создание художественной сцены"""
    print("🎨 Создание художественного объекта...")
    
    engine = BlenderEngine()
    
    # Создаем сцену с несколькими объектами
    scene_spec = SceneSpec(
        name="artistic_composition",
        camera_position=Vector3(10, -10, 8),
        camera_target=Vector3(0, 0, 0),
        lighting="studio",
        background_color=Vector3(0.1, 0.1, 0.15)
    )
    
    # Центральная сфера из стекла
    glass_sphere = ObjectSpec(
        name="glass_sphere",
        object_type=ObjectType.SPHERE,
        position=Vector3(0, 0, 2),
        radius=2.0,
        segments=64,
        material_type=MaterialType.GLASS,
        color=Vector3(0.9, 0.95, 1.0),
        transparency=0.2,
        roughness=0.1
    )
    scene_spec.objects.append(glass_sphere)
    
    # Металлические кольца вокруг
    for i in range(3):
        angle = i * 120  # 120 градусов между кольцами
        x = 4 * (1 if i == 0 else 0.5 if i == 1 else -0.5)
        y = 4 * (0 if i == 0 else 0.866 if i == 1 else -0.866)
        
        ring = ObjectSpec(
            name=f"metal_ring_{i+1}",
            object_type=ObjectType.TORUS,
            position=Vector3(x, y, 1.5 + i * 0.5),
            radius=1.5,
            material_type=MaterialType.METAL,
            color=Vector3(0.8, 0.6, 0.2),  # Золотистый
            metallic=0.9,
            roughness=0.2
        )
        scene_spec.objects.append(ring)
    
    # Основание из дерева
    base = ObjectSpec(
        name="wooden_base",
        object_type=ObjectType.CUBE,
        position=Vector3(0, 0, -1),
        dimensions=Vector3(12, 12, 1),
        material_type=MaterialType.WOOD,
        color=Vector3(0.6, 0.4, 0.2),
        roughness=0.8
    )
    scene_spec.objects.append(base)
    
    # Настройки рендера
    render_spec = RenderSpec(
        resolution_x=1920,
        resolution_y=1080,
        samples=128,
        engine="CYCLES",
        output_path="output/artistic_composition_render.png"
    )
    
    # Настройки экспорта
    export_spec = ExportSpec(
        format=ExportFormat.STL,
        output_path="output/artistic_composition.stl",
        scale=1.0
    )
    
    print("🔄 Создание сцены...")
    results = await engine.create_scene(scene_spec, render_spec, export_spec)
    
    print("✅ Художественная композиция создана!")
    print(f"📁 Файлы сохранены в: output/")
    print(f"🖼️ Рендер: {render_spec.output_path}")
    print(f"📦 STL: {export_spec.output_path}")
    
    return results

async def create_organic_lamp():
    """Создание органической лампы через специальный генератор"""
    print("💡 Создание органической лампы...")
    
    try:
        from integrations.blender_integration import BlenderIntegration
        
        integration = BlenderIntegration()
        
        if not integration.is_available():
            print("❌ Blender API недоступен")
            return
        
        # Создаем органическую лампу
        request_data = {
            'type': 'organic_lamp',
            'base_radius': 80.0,
            'complexity': 1.5,
            'name': 'ArtisticLamp'
        }
        
        result = integration.generate_3d_object(request_data)
        
        if result['success']:
            print(f"✅ Органическая лампа создана!")
            print(f"📁 Файл: {result['filepath']}")
            print(f"🖼️ Превью: {result['preview_path']}")
            print(f"📊 Информация: {result['object_info']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
            
    except Exception as e:
        print(f"❌ Ошибка создания органической лампы: {e}")

if __name__ == "__main__":
    print("🎨 Художественная мастерская Blender")
    print("=" * 50)
    
    # Создаем художественную сцену
    asyncio.run(create_artistic_scene())
    
    print("\n" + "=" * 50)
    
    # Создаем органическую лампу
    asyncio.run(create_organic_lamp())
    
    print("\n🎉 Все объекты созданы!") 