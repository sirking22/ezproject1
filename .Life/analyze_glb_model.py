import numpy as np
import json
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def read_glb_file(filename):
    """
    Читает GLB файл и извлекает геометрию
    """
    print(f"🔍 Анализ GLB файла: {filename}")
    
    with open(filename, 'rb') as f:
        # Читаем заголовок GLB
        magic = f.read(4)
        if magic != b'glTF':
            print("❌ Не GLB файл!")
            return None
            
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        print(f"📊 GLB версия: {version}, размер: {length} байт")
        
        # Читаем JSON chunk
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = f.read(4)
        
        if json_chunk_type != b'JSON':
            print("❌ Неверный формат JSON chunk")
            return None
            
        json_data = f.read(json_chunk_length).decode('utf-8')
        gltf = json.loads(json_data)
        
        print("✅ JSON данные загружены")
        
        # Читаем бинарные данные
        binary_chunk_length = struct.unpack('<I', f.read(4))[0]
        binary_chunk_type = f.read(4)
        
        if binary_chunk_type != b'BIN\x00':
            print("❌ Неверный формат BIN chunk")
            return None
            
        binary_data = f.read(binary_chunk_length)
        
        print(f"✅ Бинарные данные загружены: {len(binary_data)} байт")
        
        return gltf, binary_data

def extract_geometry(gltf, binary_data):
    """
    Извлекает геометрию из GLB данных
    """
    print("\n🔧 Извлечение геометрии...")
    
    vertices = []
    indices = []
    
    # Анализируем структуру
    print(f"📋 Meshes: {len(gltf.get('meshes', []))}")
    print(f"📋 Accessors: {len(gltf.get('accessors', []))}")
    print(f"📋 BufferViews: {len(gltf.get('bufferViews', []))}")
    
    if 'meshes' not in gltf:
        print("❌ Нет мешей в файле")
        return None, None
        
    # Берем первый меш
    mesh = gltf['meshes'][0]
    primitive = mesh['primitives'][0]
    
    # Получаем позиции вершин
    position_accessor_idx = primitive['attributes']['POSITION']
    position_accessor = gltf['accessors'][position_accessor_idx]
    position_buffer_view = gltf['bufferViews'][position_accessor['bufferView']]
    
    # Извлекаем вершины
    offset = position_buffer_view['byteOffset']
    length = position_buffer_view['byteLength']
    vertex_data = binary_data[offset:offset+length]
    
    # Конвертируем в массив numpy
    vertex_count = position_accessor['count']
    vertices = np.frombuffer(vertex_data, dtype=np.float32).reshape(vertex_count, 3)
    
    print(f"✅ Извлечено {len(vertices)} вершин")
    
    # Получаем индексы (если есть)
    if 'indices' in primitive:
        indices_accessor_idx = primitive['indices']
        indices_accessor = gltf['accessors'][indices_accessor_idx]
        indices_buffer_view = gltf['bufferViews'][indices_accessor['bufferView']]
        
        offset = indices_buffer_view['byteOffset']
        length = indices_buffer_view['byteLength']
        indices_data = binary_data[offset:offset+length]
        
        # Определяем тип индексов
        component_type = indices_accessor['componentType']
        if component_type == 5123:  # UNSIGNED_SHORT
            indices = np.frombuffer(indices_data, dtype=np.uint16)
        elif component_type == 5125:  # UNSIGNED_INT
            indices = np.frombuffer(indices_data, dtype=np.uint32)
        
        print(f"✅ Извлечено {len(indices)} индексов")
    
    return vertices, indices

def analyze_geometry(vertices, indices):
    """
    Анализирует геометрию и выводит статистику
    """
    print("\n📊 АНАЛИЗ ГЕОМЕТРИИ:")
    print(f"• Количество вершин: {len(vertices)}")
    if indices is not None:
        print(f"• Количество индексов: {len(indices)}")
        print(f"• Количество треугольников: {len(indices) // 3}")
    
    # Размеры модели
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    size = max_coords - min_coords
    
    print(f"• Размеры модели:")
    print(f"  X: {min_coords[0]:.3f} - {max_coords[0]:.3f} (размер: {size[0]:.3f})")
    print(f"  Y: {min_coords[1]:.3f} - {max_coords[1]:.3f} (размер: {size[1]:.3f})")
    print(f"  Z: {min_coords[2]:.3f} - {max_coords[2]:.3f} (размер: {size[2]:.3f})")
    
    # Центр модели
    center = (min_coords + max_coords) / 2
    print(f"• Центр модели: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
    
    return min_coords, max_coords, center, size

def visualize_reference_model(vertices, indices):
    """
    Визуализирует референсную модель
    """
    print("\n📺 Визуализация референсной модели...")
    
    fig = plt.figure(figsize=(15, 5))
    
    # Три вида
    views = [
        (30, 45, "Перспектива"),
        (0, 0, "Вид спереди"), 
        (90, 0, "Вид сверху")
    ]
    
    for i, (elev, azim, title) in enumerate(views):
        ax = fig.add_subplot(1, 3, i+1, projection='3d')
        
        # Отображаем как точечное облако для скорости
        sample_indices = np.random.choice(len(vertices), min(5000, len(vertices)), replace=False)
        sample_vertices = vertices[sample_indices]
        
        ax.scatter(sample_vertices[:, 0], sample_vertices[:, 1], sample_vertices[:, 2], 
                  c='orange', alpha=0.6, s=0.5)
        
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.view_init(elev=elev, azim=azim)
    
    plt.suptitle('Референсная модель из GLB файла', fontsize=16)
    plt.tight_layout()
    plt.show()

def create_lamp_from_reference(vertices, indices):
    """
    Создает новую модель лампы на основе анализа референса
    """
    print("\n🎨 Создание новой модели на основе референса...")
    
    # Анализируем паттерн вершин
    min_coords, max_coords, center, size = analyze_geometry(vertices, indices)
    
    # Нормализуем вершины к единичной сфере для анализа
    normalized_vertices = vertices - center
    max_radius = np.max(np.linalg.norm(normalized_vertices, axis=1))
    normalized_vertices /= max_radius
    
    # Конвертируем в сферические координаты для анализа паттерна
    x, y, z = normalized_vertices[:, 0], normalized_vertices[:, 1], normalized_vertices[:, 2]
    
    # Сферические координаты
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y, x)  # азимутальный угол
    phi = np.arccos(z / r)    # полярный угол
    
    # Анализируем вариации радиуса
    radius_variations = r - 1.0  # отклонения от единичной сферы
    
    print(f"📊 Анализ паттерна:")
    print(f"• Средняя вариация радиуса: {np.mean(np.abs(radius_variations)):.3f}")
    print(f"• Максимальная вариация: {np.max(np.abs(radius_variations)):.3f}")
    print(f"• Стандартное отклонение: {np.std(radius_variations):.3f}")
    
    # Создаем новую модель с похожими характеристиками
    phi_new = np.linspace(0, np.pi, 80)
    theta_new = np.linspace(0, 2*np.pi, 160)
    PHI, THETA = np.meshgrid(phi_new, theta_new)
    
    # Базовый радиус
    base_radius = 60.0  # мм
    
    # Пытаемся воспроизвести паттерн из референса
    # Используем статистику вариаций для настройки амплитуды
    amplitude_scale = np.max(np.abs(radius_variations)) * base_radius
    
    # Создаем органический паттерн
    organic_pattern = (
        np.sin(THETA * 8 + PHI * 3) * np.cos(PHI * 6 + THETA * 2) * 0.4 +
        np.cos(THETA * 12 + PHI * 4) * np.sin(PHI * 8 + THETA * 3) * 0.3 +
        np.sin(THETA * 16 + PHI * 6) * np.cos(PHI * 10 + THETA * 4) * 0.2
    )
    
    # Применяем вертикальную модуляцию
    vertical_mod = np.sin(PHI * 2.5) * 0.4 + 0.6
    organic_pattern *= vertical_mod
    
    # Масштабируем по анализу референса
    organic_pattern *= amplitude_scale
    
    # Добавляем шум для органичности
    np.random.seed(42)
    noise = np.random.normal(0, amplitude_scale * 0.1, organic_pattern.shape)
    organic_pattern += noise
    
    # Финальный радиус
    radius_new = base_radius + organic_pattern
    
    # Конвертируем в декартовы координаты
    X = radius_new * np.sin(PHI) * np.cos(THETA)
    Y = radius_new * np.sin(PHI) * np.sin(THETA)
    Z = radius_new * np.cos(PHI)
    
    return X, Y, Z

def save_improved_model(X, Y, Z):
    """
    Сохраняет улучшенную модель в STL
    """
    print("\n💾 Сохранение улучшенной модели...")
    
    try:
        from stl import mesh
        
        # Создаем треугольники
        vertices = []
        faces = []
        
        rows, cols = X.shape
        
        for i in range(rows):
            for j in range(cols):
                vertices.append([X[i,j], Y[i,j], Z[i,j]])
        
        vertices = np.array(vertices)
        
        for i in range(rows-1):
            for j in range(cols-1):
                v1 = i * cols + j
                v2 = i * cols + ((j + 1) % cols)
                v3 = (i + 1) * cols + j
                v4 = (i + 1) * cols + ((j + 1) % cols)
                
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
        
        faces = np.array(faces)
        
        # Создаем STL mesh
        lamp_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        
        for i, face in enumerate(faces):
            for j in range(3):
                lamp_mesh.vectors[i][j] = vertices[face[j], :]
        
        # Сохраняем
        lamp_mesh.save('organic_lamp_from_reference.stl')
        
        print("✅ STL файл 'organic_lamp_from_reference.stl' создан!")
        print(f"📊 {len(faces)} треугольников, {len(vertices)} вершин")
        
        return True
        
    except ImportError:
        print("❌ numpy-stl не установлен")
        return False

def main():
    print("🔍 АНАЛИЗ РЕФЕРЕНСНОЙ МОДЕЛИ GLB")
    print("="*50)
    
    filename = "12528bbab42cceba1447a4db3e8e5562.glb"
    
    # Читаем GLB файл
    result = read_glb_file(filename)
    if result is None:
        return
    
    gltf, binary_data = result
    
    # Извлекаем геометрию
    vertices, indices = extract_geometry(gltf, binary_data)
    if vertices is None:
        return
    
    # Анализируем
    analyze_geometry(vertices, indices)
    
    # Визуализируем референс
    visualize_reference_model(vertices, indices)
    
    # Создаем новую модель на основе анализа
    X, Y, Z = create_lamp_from_reference(vertices, indices)
    
    # Показываем новую модель
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, 
                          cmap='YlOrRd',
                          alpha=0.9,
                          linewidth=0,
                          antialiased=True)
    
    ax.set_title('Новая модель на основе референса', fontsize=16)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    
    plt.show()
    
    # Сохраняем
    save_improved_model(X, Y, Z)
    
    print("\n🎉 ГОТОВО! Модель создана на основе анализа референса!")

if __name__ == "__main__":
    main() 