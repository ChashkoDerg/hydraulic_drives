import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.animation import FuncAnimation

class SchemeManager:
    SCHEME_FOLDER = None

    def __init__(self, fig, position):
        self.fig = fig
        self.position = position
        self.scheme_images = {}
        self.scheme_patches = {}

        self._load_scheme_images()
        self._create_scheme()
        self._create_scheme_components()


    def _load_scheme_images(self):
        if not self.SCHEME_FOLDER:
            return 
        images_path = Path(__file__).parent.parent/'images'/self.SCHEME_FOLDER
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
        if not self.SCHEME_FOLDER:
            return
        
        # ✅ ОДНА ось для всей схемы
        self.scheme_ax = self.fig.add_axes([
            self.position[0] + 0.65,  # Справа
            self.position[1] + 0.50,  # По центру
            0.25,                       # Ширина
            0.25                        # Высота
        ])
        self.scheme_ax.set_xlim(-2, 2)
        self.scheme_ax.set_ylim(-2, 2)
        self.scheme_ax.axis('off')
        self.scheme_ax.set_aspect('equal')

    def _create_scheme_components(self):
        """Создать элементы схемы"""
        ax = self.scheme_ax
        
        # ✅ КОРПУС (статичный)
        if 'housing' in self.scheme_images:
            self.scheme_patches['housing'] = ax.imshow(
                self.scheme_images['housing'],
                extent=[-1.5, 1.5, -1.5, 1.5]
            )
        
        # ✅ ПОРШЕНЬ (движется по Y)
        if 'piston' in self.scheme_images:
            self.scheme_patches['piston'] = ax.imshow(
                self.scheme_images['piston'],
                extent=[-0.8, 0.8, -0.5, -0.2]
            )
        
        # ✅ РЫЧАГ (движется по Y)
        if 'lever' in self.scheme_images:
            self.scheme_patches['lever'] = ax.imshow(
                self.scheme_images['lever'],
                extent=[-0.8, 0.8, -0.5, -0.2]
            )
        
        # ✅ ГИЛЬЗА (движется по Y)
        if 'sleeve' in self.scheme_images:
            self.scheme_patches['sleeve'] = ax.imshow(
                self.scheme_images['sleeve'],
                extent=[0.7, 1.1, -0.2, 0.2]
            )
        
        # ✅ ЗОЛОТНИК (движется по X)
        if 'spool' in self.scheme_images:
            self.scheme_patches['spool'] = ax.imshow(
                self.scheme_images['spool'],
                extent=[0.8, 1.1, -0.1, 0.1]
            )

    

class NOOSScheme(SchemeManager):
    pass
class ZHOSScheme(SchemeManager):
    pass
class IOSScheme(SchemeManager):
    SCHEME_FOLDER = 'IOS'