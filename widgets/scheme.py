import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.animation import FuncAnimation
import math

class SchemeManager:
    SCHEME_FOLDER = None
    TOTAL_FRAMES = None  # ✅ Для анимации

    def __init__(self, fig, position):
        self.fig = fig
        self.position = position
        self.scheme_images = {}
        self.scheme_patches = {}
        self.animation = None  # ✅ Защита от GC

        self._load_scheme_images()
        self._create_scheme()
        self._create_scheme_components()

    def _load_scheme_images(self):
        if not self.SCHEME_FOLDER:
            return 
        images_path = Path(__file__).parent.parent / 'images' / self.SCHEME_FOLDER
        if not images_path.exists():
            print(f"⚠️ Папка не найдена: {images_path}")
            return
        for img_path in images_path.glob('*.png'):
            try:
                name = img_path.stem
                self.scheme_images[name] = plt.imread(img_path)
                print(f"✅ {self.SCHEME_FOLDER}: {img_path.name}")
            except Exception as e:
                print(f"❌ {img_path.name}: {e}")

    def _create_scheme(self):
        """Создать оси для схемы"""
        width = 0.35
        height = width * 1.5  # ✅ ИЗМЕНИТЬ: было 1.5 → стало 1.0 (квадрат)
        
        if not self.SCHEME_FOLDER:
            return
        
        self.scheme_ax = self.fig.add_axes([
            self.position[0] + 0.55,
            self.position[1] + 0.35,
            width,
            height
        ])
        self.scheme_ax.set_xlim(-2, 2)
        self.scheme_ax.set_ylim(-2, 2)
        self.scheme_ax.axis('off') 
        self.scheme_ax.set_aspect('auto')  # ✅ ИЗМЕНИТЬ: было 'auto' → стало 'equal'

    def _create_scheme_components(self):
        """Создать элементы схемы (переопределяется в дочерних классах)"""
        # ✅ Пустая реализация — дочерние классы сами решают
        pass
    
    def _setup_animation(self):
        """Настроить анимацию (переопределяется в дочерних классах)"""
        pass


# ============================================================
# ✅ ДОЧЕРНИЕ КЛАССЫ
# ============================================================

class NOOSScheme(SchemeManager):
    SCHEME_FOLDER = 'NOS'
    # Статичная схема, без анимации
    pass


class ZHOSScheme(SchemeManager):
    SCHEME_FOLDER = 'ZHOS'
    TOTAL_FRAMES = 240  # ✅ Количество кадров анимации
    prev_frame_num = None
    is_increasing = None
    
    def __init__(self, fig, position):
        # ✅ Вызов родителя без лишних аргументов
        super().__init__(fig, position)
        # ✅ Анимацию настраиваем отдельно, после создания компонентов
        self._setup_animation()
    
    def _create_scheme_components(self):
        """Создать элементы схемы с анимацией"""
        ax = self.scheme_ax
        
        # ✅ Создаём изображение только если есть кадр
        if 'frame_1' in self.scheme_images:
            self.scheme_patches['frame_1'] = ax.imshow(
                self.scheme_images['frame_1'],
                extent=[-2, 2, -2, 2],
                aspect='auto',
                animated=True
            )
            print("✅ ZHOS: схема создана")
        else:
            print("⚠️ ZHOS: frame_1 не найден!")
    
    def _setup_animation(self):
        """Настроить анимацию готовых кадров"""
        def animate(t):
            amplitude = 20
            period = 60
            center = 23 
            decay_rate = 0.01    

            frame_num = int(amplitude * math.exp(-decay_rate * t) * math.sin(2 * math.pi * t / period)) + center
            
            img_key = f'frame_{frame_num}'

            patch = self.scheme_patches['frame_1']
            patch.set_data(self.scheme_images[img_key])
            # if prev_frame_num is not None:
            #     if frame_num > prev_frame_num:
            #         self.is_increasing = True    # 📈 Кадры увеличиваются
            #     elif frame_num < prev_frame_num:
            #         self.is_increasing = False   # 📉 Кадры уменьшаются
            # Если равны — направление не меняем
            prev_frame_num = frame_num
            
            return patch  # ✅ Для blit
        
        self.animation = FuncAnimation(
            self.fig,
            animate,
            frames=self.TOTAL_FRAMES,
            interval=1,
            blit=False,
            repeat=False,
            cache_frame_data=False
        )



class IOSScheme(SchemeManager):
    SCHEME_FOLDER = 'IOS'
    # Статичная схема
    pass