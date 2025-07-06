#!/usr/bin/env python3
"""
Пример использования Blender Engine в ручном режиме.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.blender_engine import (
    BlenderEngine, ObjectSpec, ObjectType, Dimensions, 
    MeshSettings, MaterialSettings, MaterialType
)
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Подготовка команды для ручной генерации объектов...")
    
    engine = BlenderEngine()
    
    if not engine.available:
        logger.error("❌ Blender недоступен. Проверьте путь в `blender_engine.py`.")
        return

    # 1. Опишите объекты, которые хотите сгенерировать
    specs = [
        ObjectSpec(
            name="Manual_Cube",
            object_type=ObjectType.CUBE,
            dimensions=Dimensions(width=50, height=80, depth=50),
            material_settings=MaterialSettings(
                material_type=MaterialType.PLASTIC,
                color=(0.1, 0.4, 0.8, 1.0)
            ),
            position=(-100, 0, 0)
        ),
        ObjectSpec(
            name="Manual_Organic_Lamp",
            object_type=ObjectType.ORGANIC_LAMP,
            dimensions=Dimensions(radius=40),
            mesh_settings=MeshSettings(subdivisions=2),
            material_settings=MaterialSettings(
                material_type=MaterialType.METAL,
                metallic=0.8,
                roughness=0.2,
                color=(0.9, 0.7, 0.2, 1.0)
            ),
            position=(0, 0, 0)
        ),
        ObjectSpec(
            name="Manual_Glass_Sphere",
            object_type=ObjectType.SPHERE,
            dimensions=Dimensions(radius=30),
            material_settings=MaterialSettings(
                material_type=MaterialType.GLASS,
                ior=1.52
            ),
            position=(100, 0, 0)
        )
    ]
    
    # 2. Получите команду для запуска
    try:
        command, script_path = engine.prepare_manual_run(specs)
        
        logger.info("✅ Команда готова!")
        logger.info("--------------------------------------------------------------------------")
        logger.info("👇 СКОПИРУЙТЕ И ВЫПОЛНИТЕ ЭТУ КОМАНДУ В ВАШЕМ ТЕРМИНАЛЕ (PowerShell):")
        print(f"\n{command}\n")
        logger.info("--------------------------------------------------------------------------")
        logger.info(f"⚙️  Используемый скрипт: {script_path}")
        logger.info("⏳ После выполнения команды Blender отработает в фоновом режиме.")
        logger.info(f"📂 Результаты (файлы .stl и .obj) появятся в папке: {engine.output_dir}")
        
    except Exception as e:
        logger.error(f"❌ Не удалось подготовить команду: {e}")

if __name__ == "__main__":
    main() 