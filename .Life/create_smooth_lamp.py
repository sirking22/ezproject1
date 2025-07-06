import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def create_smooth_organic_lamp():
    """
    Создает гладкую органическую лампу без "ежистости"
    """
    # Увеличиваем разрешение для гладкости
    phi = np.linspace(0, np.pi, 100)  # вертикальный угол
    theta = np.linspace(0, 2*np.pi, 200)  # горизонтальный угол
    
    PHI, THETA = np.meshgrid(phi, theta)
    
    # Базовый радиус
    base_radius = 60.0  # мм
    
    # НОВЫЙ ПОДХОД: используем плавные волны без острых краев
    
    # Основные плавные волны - БЕЗ abs() для избежания острых краев
    primary_wave = (
        np.sin(THETA * 6 + PHI * 1.5) * 
        np.cos(PHI * 3 + THETA * 0.8) * 8.0
    )
    
    # Вторичные волны для сложности
    secondary_wave = (
        np.cos(THETA * 9 + PHI * 2.2) * 
        np.sin(PHI * 4 + THETA * 1.2) * 5.0
    )
    
    # Третичные волны для деталей
    tertiary_wave = (
        np.sin(THETA * 12 + PHI * 3.1) * 
        np.cos(PHI * 5 + THETA * 1.8) * 3.0
    )
    
    # Создаем плавные переходы между волнами
    flow_modulation = (
        np.sin(PHI * 2) * 0.3 + 0.7  # вертикальная модуляция
    ) * (
        np.cos(THETA * 2) * 0.2 + 0.8  # горизонтальная модуляция
    )
    
    # Комбинируем волны с плавными весами
    organic_deformation = (
        primary_wave * flow_modulation * 0.6 +
        secondary_wave * flow_modulation * 0.4 +
        tertiary_wave * flow_modulation * 0.2
    )
    
    # Добавляем очень мягкий шум
    np.random.seed(42)
    gentle_noise = np.random.normal(0, 0.8, organic_deformation.shape)
    
    # Сглаживаем шум простым усреднением
    kernel_size = 3
    smoothed_noise = np.zeros_like(gentle_noise)
    for i in range(kernel_size, gentle_noise.shape[0] - kernel_size):
        for j in range(kernel_size, gentle_noise.shape[1] - kernel_size):
            smoothed_noise[i, j] = np.mean(
                gentle_noise[i-kernel_size:i+kernel_size+1, 
                           j-kernel_size:j+kernel_size+1]
            )
    
    organic_deformation += smoothed_noise * 0.3
    
    # Применяем дополнительное сглаживание ко всей деформации
    smoothed_deformation = np.zeros_like(organic_deformation)
    for i in range(2, organic_deformation.shape[0] - 2):
        for j in range(2, organic_deformation.shape[1] - 2):
            smoothed_deformation[i, j] = np.mean(
                organic_deformation[i-2:i+3, j-2:j+3]
            )
    
    # Используем сглаженную версию
    organic_deformation = smoothed_deformation
    
    # Финальный радиус
    radius = base_radius + organic_deformation
    
    # Убеждаемся, что нет отрицательных радиусов
    radius = np.maximum(radius, base_radius * 0.3)
    
    # Преобразуем в декартовы координаты
    X = radius * np.sin(PHI) * np.cos(THETA)
    Y = radius * np.sin(PHI) * np.sin(THETA)
    Z = radius * np.cos(PHI)
    
    return X, Y, Z

def create_flowing_lamp():
    """
    Альтернативный алгоритм с "текучими" формами
    """
    phi = np.linspace(0, np.pi, 90)
    theta = np.linspace(0, 2*np.pi, 180)
    
    PHI, THETA = np.meshgrid(phi, theta)
    
    base_radius = 60.0
    
    # Используем только гладкие функции
    # Создаем "текучие" волны
    flow1 = np.sin(THETA * 4 + PHI * 2) * np.exp(-0.1 * PHI) * 10
    flow2 = np.cos(THETA * 7 + PHI * 1.5) * np.sin(PHI * 2) * 6
    flow3 = np.sin(THETA * 10 + PHI * 3) * np.cos(PHI * 1.5) * 4
    
    # Модуляция для плавности
    vertical_flow = np.sin(PHI * 1.5) * 0.4 + 0.6
    horizontal_flow = np.cos(THETA * 1.2) * 0.3 + 0.7
    
    # Комбинируем
    deformation = (flow1 + flow2 + flow3) * vertical_flow * horizontal_flow
    
    # Дополнительное сглаживание
    try:
        from scipy import ndimage
        kernel = np.ones((5, 5)) / 25
        deformation = ndimage.convolve(deformation, kernel, mode='wrap')
    except ImportError:
        # Если scipy нет, используем простое сглаживание
        smoothed = np.zeros_like(deformation)
        for i in range(2, deformation.shape[0] - 2):
            for j in range(2, deformation.shape[1] - 2):
                smoothed[i, j] = np.mean(deformation[i-2:i+3, j-2:j+3])
        deformation = smoothed
    
    radius = base_radius + deformation
    radius = np.maximum(radius, base_radius * 0.4)
    
    X = radius * np.sin(PHI) * np.cos(THETA)
    Y = radius * np.sin(PHI) * np.sin(THETA)
    Z = radius * np.cos(PHI)
    
    return X, Y, Z

def create_stl_file(X, Y, Z, filename):
    """
    Создает STL файл
    """
    try:
        from stl import mesh
        
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
        
        lamp_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        
        for i, face in enumerate(faces):
            for j in range(3):
                lamp_mesh.vectors[i][j] = vertices[face[j], :]
        
        lamp_mesh.save(filename)
        
        print(f"✅ STL файл '{filename}' создан!")
        print(f"📊 {len(faces)} треугольников, {len(vertices)} вершин")
        
        return True
        
    except ImportError:
        print("❌ numpy-stl не установлен")
        return False

def visualize_comparison():
    """
    Показывает сравнение разных алгоритмов
    """
    print("🎨 Создание гладких вариантов...")
    
    # Создаем три варианта
    X1, Y1, Z1 = create_smooth_organic_lamp()
    X2, Y2, Z2 = create_flowing_lamp()
    
    fig = plt.figure(figsize=(15, 10))
    
    # Показываем оба варианта
    algorithms = [
        (X1, Y1, Z1, "Гладкая органическая лампа"),
        (X2, Y2, Z2, "Текучая лампа")
    ]
    
    for idx, (X, Y, Z, title) in enumerate(algorithms):
        # Три вида для каждого алгоритма
        for i, (elev, azim, view_name) in enumerate([(30, 45, "Перспектива"), (0, 0, "Спереди"), (90, 0, "Сверху")]):
            ax = fig.add_subplot(2, 3, idx*3 + i + 1, projection='3d')
            
            surf = ax.plot_surface(X, Y, Z, 
                                 cmap='YlOrRd',
                                 alpha=0.9,
                                 linewidth=0,
                                 antialiased=True,
                                 rcount=40, ccount=40)
            
            ax.set_title(f"{title}\n{view_name}", fontsize=10)
            ax.view_init(elev=elev, azim=azim)
            
            max_range = 90
            ax.set_xlim([-max_range, max_range])
            ax.set_ylim([-max_range, max_range])
            ax.set_zlim([-max_range, max_range])
            
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
    
    plt.suptitle('Сравнение гладких алгоритмов (без "ежистости")', fontsize=16)
    plt.tight_layout()
    plt.show()
    
    return X1, Y1, Z1, X2, Y2, Z2

def main():
    print("🌟 СОЗДАНИЕ ГЛАДКОЙ ОРГАНИЧЕСКОЙ ЛАМПЫ")
    print("🚫 Исправляем 'ежистость' предыдущих версий")
    print("="*60)
    
    # Показываем варианты
    X1, Y1, Z1, X2, Y2, Z2 = visualize_comparison()
    
    print("\n📁 Создание STL файлов...")
    
    # Сохраняем оба варианта
    create_stl_file(X1, Y1, Z1, 'smooth_organic_lamp.stl')
    create_stl_file(X2, Y2, Z2, 'flowing_lamp.stl')
    
    print("\n" + "="*60)
    print("🎉 РЕЗУЛЬТАТ:")
    print("✅ smooth_organic_lamp.stl - гладкая органическая версия")
    print("✅ flowing_lamp.stl - текучая версия")
    
    print("\n💡 КЛЮЧЕВЫЕ УЛУЧШЕНИЯ:")
    print("• Убрал abs() - нет острых краев")
    print("• Добавил сглаживание - нет 'ежистости'")
    print("• Увеличил разрешение - более гладкая поверхность")
    print("• Использую только плавные функции")
    print("• Контроль минимального радиуса - нет инверсий")
    
    print("\n🔍 КАК ПОСМОТРЕТЬ:")
    print("1. В Cursor: установи '3D Viewer', кликни на STL")
    print("2. Онлайн: https://3dviewer.net")
    print("3. Сравни с предыдущими версиями")

if __name__ == "__main__":
    main() 