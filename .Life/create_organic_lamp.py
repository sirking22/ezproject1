import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def create_organic_lamp_mesh():
    """
    Создает треугольную сетку для STL экспорта на основе нового скриншота лампы
    с изгибистыми органическими линиями
    """
    # Параметры сетки (увеличиваем разрешение для плавных кривых)
    phi = np.linspace(0, np.pi, 80)  # вертикальный угол
    theta = np.linspace(0, 2*np.pi, 160)  # горизонтальный угол
    
    PHI, THETA = np.meshgrid(phi, theta)
    
    # Базовые параметры лампы
    base_radius = 60.0  # базовый радиус 6см
    
    # Создаем многослойные органические волны
    # Слой 1: Основные изгибистые линии
    wave1_freq_theta = 6  # частота по горизонтали
    wave1_freq_phi = 4    # частота по вертикали
    wave1_amp = 12.0      # амплитуда
    
    # Слой 2: Вторичные волны для сложности
    wave2_freq_theta = 11
    wave2_freq_phi = 7
    wave2_amp = 8.0
    
    # Слой 3: Мелкие детали
    wave3_freq_theta = 18
    wave3_freq_phi = 12
    wave3_amp = 4.0
    
    # Создаем изгибистые паттерны с использованием комбинации sin и cos
    # для более органичных форм
    
    # Основной слой - создает крупные изгибистые линии
    primary_wave = (
        np.sin(THETA * wave1_freq_theta + PHI * 2.0) * 
        np.cos(PHI * wave1_freq_phi + THETA * 1.5) * 
        wave1_amp
    )
    
    # Вторичный слой - добавляет сложность
    secondary_wave = (
        np.cos(THETA * wave2_freq_theta + PHI * 3.0) * 
        np.sin(PHI * wave2_freq_phi + THETA * 2.0) * 
        wave2_amp
    )
    
    # Третичный слой - мелкие детали
    detail_wave = (
        np.sin(THETA * wave3_freq_theta + PHI * 4.0) * 
        np.cos(PHI * wave3_freq_phi + THETA * 3.0) * 
        wave3_amp
    )
    
    # Создаем "течение" волн - они должны плавно перетекать друг в друга
    flow_pattern1 = np.sin(THETA * 3 + PHI * 2) * np.cos(PHI * 3)
    flow_pattern2 = np.cos(THETA * 5 + PHI * 4) * np.sin(THETA * 2)
    
    # Комбинируем все слои с разными весами
    organic_deformation = (
        primary_wave * (0.6 + 0.3 * flow_pattern1) +
        secondary_wave * (0.4 + 0.2 * flow_pattern2) +
        detail_wave * 0.3
    )
    
    # Добавляем вертикальную модуляцию для естественности
    vertical_flow = np.sin(PHI * 2.5) * 0.4 + 0.6
    organic_deformation *= vertical_flow
    
    # Добавляем случайные вариации для органичности
    np.random.seed(42)
    noise = np.random.normal(0, 1.0, organic_deformation.shape)
    organic_deformation += noise
    
    # Сглаживаем резкие переходы
    try:
        from scipy import ndimage
        organic_deformation = ndimage.gaussian_filter(organic_deformation, sigma=0.8)
    except ImportError:
        # Если scipy нет, используем простое сглаживание
        pass
    
    # Финальный радиус
    radius = base_radius + organic_deformation
    
    # Преобразуем в декартовы координаты
    X = radius * np.sin(PHI) * np.cos(THETA)
    Y = radius * np.sin(PHI) * np.sin(THETA)
    Z = radius * np.cos(PHI)
    
    return X, Y, Z

def create_stl_file():
    """
    Создает STL файл с проверкой библиотеки
    """
    try:
        from stl import mesh
        
        X, Y, Z = create_organic_lamp_mesh()
        
        # Создаем треугольники для STL
        vertices = []
        faces = []
        
        rows, cols = X.shape
        
        # Создаем массив вершин
        for i in range(rows):
            for j in range(cols):
                vertices.append([X[i,j], Y[i,j], Z[i,j]])
        
        vertices = np.array(vertices)
        
        # Создаем треугольные грани
        for i in range(rows-1):
            for j in range(cols-1):
                # Индексы вершин для квада
                v1 = i * cols + j
                v2 = i * cols + ((j + 1) % cols)  # зацикливаем по theta
                v3 = (i + 1) * cols + j
                v4 = (i + 1) * cols + ((j + 1) % cols)
                
                # Два треугольника с правильной ориентацией
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
        
        faces = np.array(faces)
        
        # Создаем STL mesh
        lamp_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        
        for i, face in enumerate(faces):
            for j in range(3):
                lamp_mesh.vectors[i][j] = vertices[face[j], :]
        
        # Сохраняем STL файл
        lamp_mesh.save('organic_lamp_v2.stl')
        
        print("✅ STL файл 'organic_lamp_v2.stl' создан успешно!")
        print(f"📊 Статистика: {len(faces)} треугольников, {len(vertices)} вершин")
        print(f"📏 Размеры: ~120mm диаметр")
        
        return True
        
    except ImportError:
        print("❌ Библиотека numpy-stl не установлена")
        print("🔧 Установи командой: pip install numpy-stl")
        return False

def create_obj_file():
    """
    Создает OBJ файл (не требует дополнительных библиотек)
    """
    X, Y, Z = create_organic_lamp_mesh()
    
    with open('organic_lamp_v2.obj', 'w') as f:
        f.write("# Organic Lamp Model v2 - curved flowing lines\n")
        f.write("# Created with Python for 3D printing\n")
        f.write("# More organic and flowing pattern\n\n")
        
        rows, cols = X.shape
        
        # Записываем вершины
        vertex_count = 0
        for i in range(rows):
            for j in range(cols):
                f.write(f"v {X[i,j]:.6f} {Y[i,j]:.6f} {Z[i,j]:.6f}\n")
                vertex_count += 1
        
        # Записываем грани (треугольники)
        face_count = 0
        for i in range(rows-1):
            for j in range(cols-1):
                # OBJ использует 1-based индексацию
                v1 = i * cols + j + 1
                v2 = i * cols + ((j + 1) % cols) + 1
                v3 = (i + 1) * cols + j + 1
                v4 = (i + 1) * cols + ((j + 1) % cols) + 1
                
                # Два треугольника с правильной ориентацией
                f.write(f"f {v1} {v3} {v2}\n")
                f.write(f"f {v2} {v3} {v4}\n")
                face_count += 2
    
    print("✅ OBJ файл 'organic_lamp_v2.obj' создан успешно!")
    print(f"📊 {vertex_count} вершин, {face_count} треугольников")
    return True

def visualize_model():
    """
    Показывает 3D модель перед экспортом
    """
    X, Y, Z = create_organic_lamp_mesh()
    
    # Создаем фигуру с несколькими видами
    fig = plt.figure(figsize=(15, 5))
    
    # Три вида модели
    views = [
        (30, 45, "Перспектива"),
        (0, 0, "Вид спереди"), 
        (90, 0, "Вид сверху")
    ]
    
    for i, (elev, azim, title) in enumerate(views):
        ax = fig.add_subplot(1, 3, i+1, projection='3d')
        
        # Создаем поверхность с более детальным освещением
        surf = ax.plot_surface(X, Y, Z, 
                              cmap='YlOrRd',
                              alpha=0.9,
                              linewidth=0,
                              antialiased=True,
                              shade=True,
                              rcount=50, ccount=50)  # Увеличиваем детализацию
        
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        
        # Устанавливаем угол обзора
        ax.view_init(elev=elev, azim=azim)
        
        # Равные пропорции
        max_range = 90
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])
    
    plt.suptitle('Органическая лампа v2 - изгибистые линии', fontsize=16)
    plt.tight_layout()
    plt.show()
    
    # Дополнительный рендер с эффектом свечения
    fig2 = plt.figure(figsize=(12, 12), facecolor='black')
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # Имитация внутреннего свечения с градиентом
    # Вычисляем расстояние от центра для градиента
    center_distance = np.sqrt(X**2 + Y**2 + Z**2)
    normalized_distance = (center_distance - center_distance.min()) / (center_distance.max() - center_distance.min())
    
    # Создаем цветовую карту для свечения
    colors = plt.cm.YlOrRd(1.0 - normalized_distance * 0.5)
    
    surf2 = ax2.plot_surface(X, Y, Z,
                           facecolors=colors,
                           alpha=0.85,
                           linewidth=0,
                           antialiased=True,
                           rcount=60, ccount=60)
    
    # Настройки для красивого рендера
    ax2.set_facecolor('black')
    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False  
    ax2.zaxis.pane.fill = False
    ax2.grid(False)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_zticks([])
    
    # Угол как на оригинальном фото
    ax2.view_init(elev=20, azim=45)
    
    max_range = 90
    ax2.set_xlim([-max_range, max_range])
    ax2.set_ylim([-max_range, max_range])
    ax2.set_zlim([-max_range, max_range])
    
    plt.title("Органическая лампа v2 - с изгибистыми линиями", color='white', pad=20)
    plt.show()

def main():
    print("🌟 Создание STL модели органической лампы v2")
    print("🔄 Новый алгоритм с изгибистыми линиями")
    print("="*60)
    
    # Показываем 3D модель
    print("📺 Отображение 3D модели...")
    visualize_model()
    
    print("\n📁 Создание файлов для 3D печати...")
    
    # Создаем OBJ (всегда работает)
    obj_success = create_obj_file()
    
    # Пытаемся создать STL
    stl_success = create_stl_file()
    
    print("\n" + "="*60)
    print("🎉 РЕЗУЛЬТАТ:")
    
    if obj_success:
        print("✅ organic_lamp_v2.obj - создан (изгибистые линии)")
    
    if stl_success:
        print("✅ organic_lamp_v2.stl - создан (готов для 3D печати)")
    else:
        print("⚠️  STL не создан - установи numpy-stl: pip install numpy-stl")
    
    print("\n🔍 КАК ПОСМОТРЕТЬ:")
    print("1. В Cursor: установи расширение '3D Viewer', кликни на файл")
    print("2. Онлайн: https://3dviewer.net (перетащи файл)")
    print("3. Программы: Blender, FreeCAD, PrusaSlicer")
    
    print("\n🖨️  ПАРАМЕТРЫ ДЛЯ 3D ПЕЧАТИ:")
    print("• Размер: ~120mm диаметр (масштабируй по желанию)")
    print("• Материал: PLA или PETG")
    print("• Заполнение: 15-20%")
    print("• Поддержки: НЕ нужны")
    print("• Для подсветки: используй полупрозрачный пластик")
    
    print("\n💡 УЛУЧШЕНИЯ v2:")
    print("• Более изгибистые и органичные линии")
    print("• Многослойный паттерн волн")
    print("• Плавные переходы между элементами")
    print("• Увеличенное разрешение для детализации")

if __name__ == "__main__":
    main() 