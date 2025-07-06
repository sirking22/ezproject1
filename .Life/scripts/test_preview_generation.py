#!/usr/bin/env python3
"""
Тест системы генерации превью для Blender Engine
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.blender_engine import (
    BlenderEngine, ObjectSpec, ObjectType, Dimensions, 
    MeshSettings, MaterialSettings, MaterialType, RenderSettings
)
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_preview():
    """Тест базового превью"""
    logger.info("🎬 Тестирование базового превью...")
    
    engine = BlenderEngine()
    
    # Создаем простой куб
    spec = ObjectSpec(
        name="test_cube",
        object_type=ObjectType.CUBE,
        dimensions=Dimensions(width=50, height=50, depth=50),
        material_settings=MaterialSettings(
            material_type=MaterialType.PLASTIC,
            color=(0.8, 0.2, 0.2, 1.0)  # Красный
        )
    )
    
    # Настройки рендера для быстрого превью
    render_settings = RenderSettings(
        resolution_x=800,
        resolution_y=600,
        engine="BLENDER_EEVEE_NEXT",
        samples=32,
        preview_type="perspective",
        lighting_type="studio",
        preview_format="PNG"
    )
    
    result = engine.generate_preview(spec, render_settings)
    
    if result.success:
        logger.info(f"✅ Превью создано: {result.preview_file}")
        logger.info(f"⏱️ Время выполнения: {result.execution_time:.2f}с")
    else:
        logger.error(f"❌ Ошибка: {result.error_message}")
    
    return result.success

def test_multiple_preview_types():
    """Тест различных типов превью"""
    logger.info("🎬 Тестирование различных типов превью...")
    
    engine = BlenderEngine()
    
    # Создаем сферу
    spec = ObjectSpec(
        name="test_sphere",
        object_type=ObjectType.SPHERE,
        dimensions=Dimensions(radius=30),
        material_settings=MaterialSettings(
            material_type=MaterialType.GLASS,
            color=(0.2, 0.8, 0.8, 0.8),
            ior=1.5
        )
    )
    
    # Тестируем разные типы превью
    preview_types = ["front", "side", "top", "perspective", "wireframe"]
    
    for preview_type in preview_types:
        logger.info(f"📸 Генерация превью типа: {preview_type}")
        
        render_settings = RenderSettings(
            resolution_x=600,
            resolution_y=600,
            engine="CYCLES",
            samples=64,
            preview_type=preview_type,
            lighting_type="studio",
            preview_format="PNG"
        )
        
        result = engine.generate_preview(spec, render_settings)
        
        if result.success:
            logger.info(f"✅ {preview_type}: {result.preview_file}")
        else:
            logger.error(f"❌ {preview_type}: {result.error_message}")

def test_lighting_setups():
    """Тест различных настроек освещения"""
    logger.info("💡 Тестирование различных настроек освещения...")
    
    engine = BlenderEngine()
    
    # Создаем органическую лампу
    spec = ObjectSpec(
        name="test_organic_lamp",
        object_type=ObjectType.ORGANIC_LAMP,
        dimensions=Dimensions(radius=40),
        mesh_settings=MeshSettings(subdivisions=2),
        material_settings=MaterialSettings(
            material_type=MaterialType.METAL,
            color=(0.8, 0.8, 0.9, 1.0),
            metallic=0.9,
            roughness=0.1
        )
    )
    
    # Тестируем разные типы освещения
    lighting_types = ["studio", "natural", "dramatic", "product"]
    
    for lighting_type in lighting_types:
        logger.info(f"💡 Генерация с освещением: {lighting_type}")
        
        render_settings = RenderSettings(
            resolution_x=800,
            resolution_y=600,
            engine="CYCLES",
            samples=128,
            preview_type="perspective",
            lighting_type=lighting_type,
            enable_ao=True,
            preview_format="PNG"
        )
        
        result = engine.generate_preview(spec, render_settings)
        
        if result.success:
            logger.info(f"✅ {lighting_type}: {result.preview_file}")
        else:
            logger.error(f"❌ {lighting_type}: {result.error_message}")

def test_material_previews():
    """Тест превью различных материалов"""
    logger.info("🎨 Тестирование превью различных материалов...")
    
    engine = BlenderEngine()
    
    # Создаем цилиндр для демонстрации материалов
    spec = ObjectSpec(
        name="test_materials",
        object_type=ObjectType.CYLINDER,
        dimensions=Dimensions(radius=25, height=80),
        material_settings=MaterialSettings(
            material_type=MaterialType.PLASTIC,
            color=(0.2, 0.6, 0.8, 1.0),
            roughness=0.3
        )
    )
    
    # Тестируем разные материалы
    materials = [
        ("plastic_blue", MaterialType.PLASTIC, (0.2, 0.6, 0.8, 1.0), 0.3, 0.0),
        ("metal_gold", MaterialType.METAL, (1.0, 0.8, 0.2, 1.0), 0.1, 0.9),
        ("glass_clear", MaterialType.GLASS, (0.9, 0.9, 0.9, 0.3), 0.0, 0.0),
        ("plastic_red", MaterialType.PLASTIC, (0.8, 0.2, 0.2, 1.0), 0.5, 0.0),
    ]
    
    for mat_name, mat_type, color, roughness, metallic in materials:
        logger.info(f"🎨 Генерация материала: {mat_name}")
        
        spec.material_settings = MaterialSettings(
            material_type=mat_type,
            color=color,
            roughness=roughness,
            metallic=metallic
        )
        spec.name = f"test_{mat_name}"
        
        render_settings = RenderSettings(
            resolution_x=600,
            resolution_y=600,
            engine="CYCLES",
            samples=128,
            preview_type="perspective",
            lighting_type="studio",
            preview_format="PNG"
        )
        
        result = engine.generate_preview(spec, render_settings)
        
        if result.success:
            logger.info(f"✅ {mat_name}: {result.preview_file}")
        else:
            logger.error(f"❌ {mat_name}: {result.error_message}")

def test_high_quality_preview():
    """Тест высококачественного превью"""
    logger.info("🌟 Тестирование высококачественного превью...")
    
    engine = BlenderEngine()
    
    # Создаем сложный объект
    spec = ObjectSpec(
        name="high_quality_test",
        object_type=ObjectType.ORGANIC_LAMP,
        dimensions=Dimensions(radius=50),
        mesh_settings=MeshSettings(subdivisions=3, segments=64),
        material_settings=MaterialSettings(
            material_type=MaterialType.GLASS,
            color=(0.9, 0.9, 1.0, 0.7),
            ior=1.52,
            transmission=0.95
        )
    )
    
    # Высококачественные настройки
    render_settings = RenderSettings(
        resolution_x=1920,
        resolution_y=1080,
        engine="CYCLES",
        samples=512,
        preview_type="perspective",
        lighting_type="studio",
        enable_ao=True,
        enable_bloom=True,
        preview_format="PNG"
    )
    
    start_time = time.time()
    result = engine.generate_preview(spec, render_settings)
    execution_time = time.time() - start_time
    
    if result.success:
        logger.info(f"✅ Высококачественное превью: {result.preview_file}")
        logger.info(f"⏱️ Время выполнения: {execution_time:.2f}с")
    else:
        logger.error(f"❌ Ошибка: {result.error_message}")

def test_preview_caching():
    """Тест кэширования превью"""
    logger.info("💾 Тестирование кэширования превью...")
    
    engine = BlenderEngine()
    
    spec = ObjectSpec(
        name="cache_test",
        object_type=ObjectType.SPHERE,
        dimensions=Dimensions(radius=30),
        material_settings=MaterialSettings(
            material_type=MaterialType.PLASTIC,
            color=(0.8, 0.4, 0.2, 1.0)
        )
    )
    
    render_settings = RenderSettings(
        resolution_x=400,
        resolution_y=400,
        engine="BLENDER_EEVEE_NEXT",
        samples=16,
        preview_type="perspective",
        lighting_type="studio"
    )
    
    # Первый запуск
    logger.info("🔄 Первый запуск...")
    start_time = time.time()
    result1 = engine.generate_preview(spec, render_settings)
    time1 = time.time() - start_time
    
    # Второй запуск (должен использовать кэш)
    logger.info("🔄 Второй запуск (кэш)...")
    start_time = time.time()
    result2 = engine.generate_preview(spec, render_settings)
    time2 = time.time() - start_time
    
    if result1.success and result2.success:
        logger.info(f"✅ Первый запуск: {time1:.2f}с")
        logger.info(f"✅ Второй запуск: {time2:.2f}с")
        logger.info(f"🚀 Ускорение: {time1/time2:.1f}x")
    else:
        logger.error("❌ Ошибка в тесте кэширования")

def main():
    """Основная функция тестирования"""
    logger.info("🚀 Запуск тестов системы генерации превью")
    
    # Проверяем доступность Blender
    engine = BlenderEngine()
    if not engine.available:
        logger.error("❌ Blender недоступен. Убедитесь, что Blender установлен и путь указан правильно.")
        return False
    
    logger.info(f"✅ Blender найден: {engine.blender_path}")
    
    # Запускаем тесты
    tests = [
        ("Базовое превью", test_basic_preview),
        ("Типы превью", test_multiple_preview_types),
        ("Освещение", test_lighting_setups),
        ("Материалы", test_material_previews),
        ("Высокое качество", test_high_quality_preview),
        ("Кэширование", test_preview_caching),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Тест: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    logger.info(f"\n{'='*50}")
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n📈 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        logger.info("🎉 Все тесты пройдены успешно!")
    else:
        logger.warning("⚠️ Некоторые тесты не пройдены")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 