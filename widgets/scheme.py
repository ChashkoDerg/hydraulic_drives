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
        width = 0.35
        height = width * 1.5  # Прямоугольная область
        
        if not self.SCHEME_FOLDER:
            return
        
        self.scheme_ax = self.fig.add_axes([
            self.position[0]+0.55,
            self.position[1]+0.35,
            width,
            height
        ])
        self.scheme_ax.set_xlim(-2, 2)
        self.scheme_ax.set_ylim(-2, 2)
        self.scheme_ax.axis('off') 
        self.scheme_ax.set_aspect('auto')

    def _create_scheme_components(self):
        """Создать элементы схемы"""
        ax = self.scheme_ax
        
        self.scheme_patches['frame_1'] = ax.imshow(
            self.scheme_images['frame_1'],
            extent=[-2, 2, -2, 2],
            aspect='auto' 
        )
    
    

class NOOSScheme(SchemeManager):
    pass
class ZHOSScheme(SchemeManager):
    SCHEME_FOLDER = 'ZHOS'
class IOSScheme(SchemeManager):
    SCHEME_FOLDER = 'IOS'