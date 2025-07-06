"""
Blender API интеграция для генерации 3D объектов
Интеграция с системой управления жизнью
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import os
import sys

logger = logging.getLogger(__name__)

class BlenderGenerator:
    """
    Генератор 3D объектов через Blender API
    """
    
    def __init__(self):
        """Инициализация генератора"""
        self.setup_precise_environment()
        self.clear_scene()
        
    def setup_precise_environment(self):
        """Настройка точной рабочей среды"""
        try:
            import bpy
            
            # Единицы измерения - миллиметры
            bpy.context.scene.unit_settings.system = 'METRIC'
            bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
            bpy.context.scene.unit_settings.scale_length = 1.0
            
            # Точная привязка
            bpy.context.scene.tool_settings.use_snap = True
            bpy.context.scene.tool_settings.snap_elements = {'VERTEX', 'EDGE', 'FACE'}
            bpy.context.scene.tool_settings.use_snap_project = True
            bpy.context.scene.tool_settings.grid_scale = 0.1  # 0.1mm сетка
            
            # Рендер настройки для точности
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'GPU'
            
            logger.info("✅ Точная среда Blender настроена")
            
        except ImportError:
            logger.error("❌ Blender API недоступен")
            raise
        
    def clear_scene(self):
        """Очистка сцены"""
        try:
            import bpy
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            logger.info("🧹 Сцена очищена")
        except Exception as e:
            logger.error(f"❌ Ошибка очистки сцены: {e}")
    
    def create_precise_cube(self, 
                           width: float, 
                           height: float, 
                           depth: float,
                           location: Tuple[float, float, float] = (0, 0, 0),
                           name: str = "PreciseCube") -> Any:
        """
        Создание точного куба по размерам
        """
        try:
            import bpy
            from mathutils import Vector
            
            bpy.ops.mesh.primitive_cube_add(location=location)
            cube = bpy.context.active_object
            cube.name = name
            
            # Точное масштабирование
            cube.scale = (width/2, height/2, depth/2)
            bpy.ops.object.transform_apply(scale=True)
            
            logger.info(f"📦 Создан куб {name}: {width}x{height}x{depth}mm")
            return cube
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания куба: {e}")
            return None
    
    def create_precise_cylinder(self,
                               radius: float,
                               height: float,
                               segments: int = 32,
                               location: Tuple[float, float, float] = (0, 0, 0),
                               name: str = "PreciseCylinder") -> Any:
        """
        Создание точного цилиндра
        """
        try:
            import bpy
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=radius,
                depth=height,
                vertices=segments,
                location=location
            )
            cylinder = bpy.context.active_object
            cylinder.name = name
            
            logger.info(f"🔵 Создан цилиндр {name}: R={radius}, H={height}mm")
            return cylinder
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания цилиндра: {e}")
            return None
    
    def create_precise_sphere(self,
                             radius: float,
                             segments: int = 32,
                             rings: int = 16,
                             location: Tuple[float, float, float] = (0, 0, 0),
                             name: str = "PreciseSphere") -> Any:
        """
        Создание точной сферы
        """
        try:
            import bpy
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=radius,
                segments=segments,
                ring_count=rings,
                location=location
            )
            sphere = bpy.context.active_object
            sphere.name = name
            
            logger.info(f"⚪ Создана сфера {name}: R={radius}mm")
            return sphere
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сферы: {e}")
            return None
    
    def create_from_vertices(self,
                            vertices: List[Tuple[float, float, float]],
                            faces: List[List[int]],
                            name: str = "CustomMesh") -> Any:
        """
        Создание объекта из вершин и граней
        """
        try:
            import bpy
            from mathutils import Vector
            
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            
            # Добавляем в сцену
            bpy.context.collection.objects.link(obj)
            
            # Создаем меш
            mesh.from_pydata(vertices, [], faces)
            mesh.update()
            
            # Выбираем объект
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            logger.info(f"🎨 Создан объект {name}: {len(vertices)} вершин, {len(faces)} граней")
            return obj
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания объекта из вершин: {e}")
            return None
    
    def create_organic_lamp(self,
                           base_radius: float = 60.0,
                           complexity: float = 1.0,
                           name: str = "OrganicLamp") -> Any:
        """
        Создание органической лампы через Blender API
        """
        try:
            import numpy as np
            
            # Параметры сетки
            phi_res = int(40 * complexity)
            theta_res = int(80 * complexity)
            
            phi = np.linspace(0, np.pi, phi_res)
            theta = np.linspace(0, 2*np.pi, theta_res)
            PHI, THETA = np.meshgrid(phi, theta)
            
            # Органические волны
            wave1 = np.sin(THETA * 6 + PHI * 2) * np.cos(PHI * 4 + THETA * 1.5) * 12.0
            wave2 = np.cos(THETA * 11 + PHI * 3) * np.sin(PHI * 7 + THETA * 2) * 8.0
            wave3 = np.sin(THETA * 18 + PHI * 4) * np.cos(PHI * 12 + THETA * 3) * 4.0
            
            # Комбинируем волны
            organic_deformation = wave1 * 0.6 + wave2 * 0.3 + wave3 * 0.1
            
            # Вертикальная модуляция
            vertical_flow = np.sin(PHI * 2.5) * 0.4 + 0.6
            organic_deformation *= vertical_flow
            
            # Финальный радиус
            radius = base_radius + organic_deformation
            
            # Декартовы координаты
            X = radius * np.sin(PHI) * np.cos(THETA)
            Y = radius * np.sin(PHI) * np.sin(THETA)
            Z = radius * np.cos(PHI)
            
            # Создаем вершины и грани
            vertices = []
            faces = []
            
            rows, cols = X.shape
            
            # Вершины
            for i in range(rows):
                for j in range(cols):
                    vertices.append((X[i,j], Y[i,j], Z[i,j]))
            
            # Грани
            for i in range(rows-1):
                for j in range(cols-1):
                    v1 = i * cols + j
                    v2 = i * cols + ((j + 1) % cols)
                    v3 = (i + 1) * cols + j
                    v4 = (i + 1) * cols + ((j + 1) % cols)
                    
                    faces.append([v1, v3, v2])
                    faces.append([v2, v3, v4])
            
            # Создаем объект
            obj = self.create_from_vertices(vertices, faces, name)
            
            if obj:
                # Добавляем материал
                self.add_glass_material(obj)
            
            logger.info(f"💡 Создана органическая лампа {name}")
            return obj
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания органической лампы: {e}")
            return None
    
    def add_glass_material(self, obj: Any):
        """Добавление стеклянного материала"""
        try:
            import bpy
            
            material = bpy.data.materials.new(name="Glass")
            material.use_nodes = True
            nodes = material.node_tree.nodes
            
            # Очищаем ноды
            nodes.clear()
            
            # Создаем ноды
            output = nodes.new(type='ShaderNodeOutputMaterial')
            glass = nodes.new(type='ShaderNodeBsdfGlass')
            
            # Настройки стекла
            glass.inputs['Color'].default_value = (0.8, 0.9, 1.0, 1.0)
            glass.inputs['Roughness'].default_value = 0.0
            glass.inputs['IOR'].default_value = 1.45
            
            # Соединяем
            material.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])
            
            # Применяем к объекту
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления материала: {e}")
    
    def create_from_blueprint(self, blueprint_data: Dict[str, Any]) -> Any:
        """
        Создание объекта по чертежу
        """
        try:
            # Извлекаем размеры
            dimensions = blueprint_data.get('dimensions', {})
            width = dimensions.get('width', 100)
            height = dimensions.get('height', 100)
            depth = dimensions.get('depth', 100)
            
            # Тип объекта
            object_type = blueprint_data.get('type', 'cube')
            
            if object_type == 'cube':
                return self.create_precise_cube(width, height, depth)
            elif object_type == 'cylinder':
                radius = dimensions.get('radius', 50)
                return self.create_precise_cylinder(radius, height)
            elif object_type == 'sphere':
                radius = dimensions.get('radius', 50)
                return self.create_precise_sphere(radius)
            elif object_type == 'organic':
                return self.create_organic_lamp()
            else:
                raise ValueError(f"Неизвестный тип объекта: {object_type}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания по чертежу: {e}")
            return None
    
    def export_stl(self, obj: Any, filepath: str) -> bool:
        """Экспорт в STL"""
        try:
            import bpy
            
            # Выбираем объект
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Экспортируем
            bpy.ops.export_mesh.stl(
                filepath=filepath,
                use_selection=True,
                global_scale=1.0,
                use_scene_unit=True,
                ascii=False,
                use_mesh_edges=False,
                use_mesh_vertices=False
            )
            
            logger.info(f"💾 Экспортировано в STL: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка экспорта STL: {e}")
            return False
    
    def export_obj(self, obj: Any, filepath: str) -> bool:
        """Экспорт в OBJ"""
        try:
            import bpy
            
            # Выбираем объект
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Экспортируем
            bpy.ops.export_scene.obj(
                filepath=filepath,
                use_selection=True,
                use_materials=True,
                use_triangles=True,
                use_normals=True,
                use_uvs=True
            )
            
            logger.info(f"💾 Экспортировано в OBJ: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка экспорта OBJ: {e}")
            return False
    
    def render_preview(self, filepath: str, resolution: Tuple[int, int] = (1920, 1080)) -> bool:
        """Рендер превью"""
        try:
            import bpy
            
            # Настройки рендера
            bpy.context.scene.render.resolution_x = resolution[0]
            bpy.context.scene.render.resolution_y = resolution[1]
            bpy.context.scene.render.filepath = filepath
            
            # Рендерим
            bpy.ops.render.render(write_still=True)
            
            logger.info(f"📸 Рендер сохранен: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка рендера: {e}")
            return False
    
    def get_object_info(self, obj: Any) -> Dict[str, Any]:
        """Получение информации об объекте"""
        try:
            bbox = obj.bound_box
            dimensions = {
                'width': bbox[4][0] - bbox[0][0],
                'height': bbox[2][1] - bbox[0][1],
                'depth': bbox[1][2] - bbox[0][2]
            }
            
            return {
                'name': obj.name,
                'type': obj.type,
                'dimensions': dimensions,
                'vertex_count': len(obj.data.vertices),
                'face_count': len(obj.data.polygons),
                'location': tuple(obj.location),
                'rotation': tuple(obj.rotation_euler)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации об объекте: {e}")
            return {}


class BlenderIntegration:
    """
    Интеграция Blender API с системой управления жизнью
    """
    
    def __init__(self):
        """Инициализация интеграции"""
        self.generator = None
        self.available = False
        
        try:
            self.generator = BlenderGenerator()
            self.available = True
            logger.info("✅ Blender интеграция активна")
        except Exception as e:
            logger.warning(f"⚠️ Blender API недоступен: {e}")
    
    def is_available(self) -> bool:
        """Проверка доступности Blender API"""
        return self.available
    
    def generate_3d_object(self, 
                          request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Генерация 3D объекта по запросу
        
        Args:
            request_data: данные запроса
            
        Returns:
            Результат генерации
        """
        if not self.available or not self.generator:
            return {
                'success': False,
                'error': 'Blender API недоступен'
            }
        
        try:
            object_type = request_data.get('type', 'organic_lamp')
            
            if object_type == 'organic_lamp':
                obj = self.generator.create_organic_lamp(
                    base_radius=request_data.get('base_radius', 60.0),
                    complexity=request_data.get('complexity', 1.0)
                )
            else:
                obj = self.generator.create_precise_object(
                    object_type=object_type,
                    dimensions=request_data.get('dimensions', {}),
                    name=request_data.get('name', 'GeneratedObject')
                )
            
            if obj:
                # Экспортируем в STL
                filepath = f"generated_{object_type}_{obj.name}.stl"
                if self.generator.export_stl(obj, filepath):
                    # Рендерим превью
                    preview_path = f"preview_{object_type}_{obj.name}.png"
                    self.generator.render_preview(preview_path)
                    
                    return {
                        'success': True,
                        'filepath': filepath,
                        'preview_path': preview_path,
                        'object_type': object_type,
                        'object_info': self.generator.get_object_info(obj)
                    }
            
            return {
                'success': False,
                'error': 'Ошибка создания объекта'
            }
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации 3D объекта: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_precise_object(self, 
                             object_type: str,
                             dimensions: Dict[str, float],
                             name: str = "PreciseObject") -> Optional[Dict[str, Any]]:
        """
        Создание точного объекта
        
        Args:
            object_type: тип объекта (cube, cylinder, sphere)
            dimensions: размеры
            name: имя объекта
            
        Returns:
            Результат создания
        """
        if not self.available or not self.generator:
            return {
                'success': False,
                'error': 'Blender API недоступен'
            }
        
        try:
            blueprint_data = {
                'type': object_type,
                'dimensions': dimensions
            }
            
            obj = self.generator.create_from_blueprint(blueprint_data)
            if obj:
                obj.name = name
                
                # Экспортируем
                filepath = f"{name}.stl"
                if self.generator.export_stl(obj, filepath):
                    # Информация об объекте
                    info = self.generator.get_object_info(obj)
                    logger.info(f"📊 Информация об объекте: {info}")
                    
                    return {
                        'success': True,
                        'filepath': filepath,
                        'object_info': info
                    }
            
            return {
                'success': False,
                'error': 'Ошибка создания объекта'
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания точного объекта: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_generate(self, 
                      objects_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Пакетная генерация объектов
        
        Args:
            objects_data: список данных объектов
            
        Returns:
            Список результатов генерации
        """
        if not self.available or not self.generator:
            return [{'success': False, 'error': 'Blender API недоступен'}]
        
        results = []
        
        for i, obj_data in enumerate(objects_data):
            try:
                logger.info(f"🔄 Генерация объекта {i+1}/{len(objects_data)}")
                
                if obj_data.get('type') == 'organic_lamp':
                    result = self.generate_3d_object(obj_data)
                else:
                    result = self.create_precise_object(
                        obj_data.get('type', 'cube'),
                        obj_data.get('dimensions', {}),
                        obj_data.get('name', f"Object_{i+1}")
                    )
                
                results.append(result)
                    
            except Exception as e:
                logger.error(f"❌ Ошибка генерации объекта {i+1}: {e}")
                results.append({'success': False, 'error': str(e)})
        
        logger.info(f"✅ Пакетная генерация завершена: {len(results)} объектов")
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        return {
            'available': self.available,
            'blender_version': self._get_blender_version() if self.available else None
        }
    
    def _get_blender_version(self) -> str:
        """Получение версии Blender"""
        try:
            import bpy
            return bpy.app.version_string
        except:
            return "Unknown" 