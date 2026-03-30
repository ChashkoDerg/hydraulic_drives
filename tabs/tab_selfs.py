import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from models.hydraulic import HydraulicDrive
from widgets.sliders import MySlider
from widgets.scheme import NOOSScheme, ZHOSScheme, IOSScheme

class Base:
    """Базовый класс для всех вкладок гидропривода"""
    MODEL_TYPE = None
    SLIDER_CONFIG = {}
    PLOT_TITLE = None
    PARAMS_KEY = None
    

    def __init__(self, fig, position, params_init):
        """
        Parameters
        ----------
        fig : plt.Figure
            Фигура matplotlib
        position : list
            Позиция контейнера вкладки [left, bottom, width, height]
        params_init : dict
            Словарь начальных параметров 
        """
        # ✅ snake_case для атрибутов экземпляра
        self.fig = fig
        self.position = position
        self.params_init = params_init
        self.drive = HydraulicDrive(self.MODEL_TYPE, self.params_init[self.PARAMS_KEY])

        
        # Контейнер вкладки
        self.ax_container = plt.axes(self.position)
        self.ax_container.axis('off')
        
        # Динамические атрибуты
        self.ax = None
        self.line = None
        self.sliders = {}
        self.texts = []
        self.animation = None
        
        
        # Создание компонентов
        self._create_plot()
        self._create_sliders()
        self._setup_animation()
        
    def y_lim(self):
        dy_lim_max = self.drive.max_val - self.drive.steady
        dy_lim_min = abs(self.drive.min_val)

        if dy_lim_max > self.drive.steady or dy_lim_min > self.drive.steady:
            if dy_lim_max > dy_lim_min:
                dy_lim = dy_lim_max
            else:
                dy_lim = dy_lim_min
        else:
            dy_lim = self.drive.steady
        return (self.drive.steady - dy_lim)*1.1, (self.drive.steady + dy_lim)*1.1
    

    def _create_plot(self):
        """Создать график переходного процесса"""
        left = 0.1
        bottom = 0.45
        width = 0.35
        height = 0.4



        self.ax = self.fig.add_axes([
            self.position[0] + left,
            self.position[1] + bottom,
            width,
            height
        ])
        
        self.ax.grid(True)
        self.ax.set_xlim(0, self.drive.settling_time*1.5)
        self.ax.set_ylim(*self.y_lim())
        self.ax.axhline(y=self.drive.steady, color='red', ls='--', label='Установившееся')
        self.ax.axhline(y= self.drive.params['no_os_k'] if self.drive.type == 'no_os' else 1 , color='gray', ls=':', label='Задание')
        self.ax.set_title(self.PLOT_TITLE)
        self.ax.set_xlabel('Время, с')
        self.ax.set_ylabel('Выход')
        self.ax.legend()
        
        self.line, = self.ax.plot([], [], '#e74c3c', lw=2)
    
    def _create_sliders(self):
        """Создать слайдеры для настройки параметров"""
        x = self.position[0] + 0.2
        y = self.position[1] + 0.35
        text = self.fig.text(
            x, y,
            f'Параметры: {self.PLOT_TITLE}',
            ha='center'
        )
        self.texts.append(text)
        
        color = '#e74c3c'
        y_interval = 0.04
        
        for i, (name, confs) in enumerate(self.SLIDER_CONFIG.items()):
            slider_ax_pos = [
                self.position[0] + 0.1,
                self.position[1] + 0.3 - y_interval * i,
                0.35,
                0.02
            ]
            
            slider = MySlider(slider_ax_pos, self.fig)
            slider._add_slider(
                confs['label'],
                *confs['borders'],
                self.params_init[self.PARAMS_KEY][name],  
                color
            )
            slider.connect_slider(self.update)
            self.sliders[name] = slider
    
    def _setup_animation(self):
        """Настроить анимацию графика"""
        def animate(frame):
            self.line.set_data(self.drive.t[:frame], self.drive.y[:frame])
            return [self.line]
        
        self.animation = FuncAnimation(
            self.fig,
            animate,
            frames=len(self.drive.t),
            interval=30,      # ✅ 30ms = ~33 FPS (вместо 1ms)
            blit=False,       # ✅ False для совместимости со слайдерами
            repeat=False
        )
    
    def update(self, _):
        """Обновить данные при изменении слайдеров"""
        params = {key: self.sliders[key].get_value() for key in self.sliders}
        
        self.drive.params.update(params)
        self.drive.calc()
        
        self.ax.set_xlim(0, self.drive.settling_time*1.5)
        self.ax.set_ylim(*self.y_lim())
        
        for line in self.ax.get_lines():
            if line.get_linestyle() == '--' and line.get_color() == 'red':
                line.set_ydata([self.drive.steady, self.drive.steady])
        
        self.line.set_data(self.drive.t, self.drive.y)
        self.fig.canvas.draw_idle()
    
    def destroy(self):
        """Очистить ресурсы вкладки"""
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        
        if self.ax:
            try:
                self.ax.remove()
            except:
                pass
            self.ax = None
        
        for slider in list(self.sliders.values()):
            try:
                slider.destroy()
            except:
                pass
        self.sliders.clear()
        
        for text in self.texts:
            try:
                text.remove()
            except:
                pass
        self.texts.clear()
        
        try:
            self.ax_container.remove()
        except:
            pass
        
        self.drive = None


class TabNoOs(Base):
    MODEL_TYPE = 'no_os'
    SLIDER_CONFIG = {
            'no_os_k': {'label': 'k', 'borders': (1, 100)},
            'no_os_zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
            'no_os_T': {'label': 'T', 'borders': (0.005, 1)}
        }
    PLOT_TITLE = 'Гидропривод без ОС'
    PARAMS_KEY = "no_os"


class TabZhOs(Base):
    MODEL_TYPE = 'zhos'
    SLIDER_CONFIG = {
            'zhos_k': {'label': 'k', 'borders': (1, 100)},
            'zhos_k_os': {'label': 'k_os', 'borders': (0.1, 5)},
            'zhos_zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
            'zhos_T': {'label': 'T', 'borders': (0.005, 1)}
        }
    PLOT_TITLE = 'Гидропривод с ЖОС'
    PARAMS_KEY = "zhos"

class TabIOs(Base):

    def __init__(self, fig, position, params_init):
        self.scheme = IOSScheme(fig, position)  # ✅ Создаём схему здесь
        super().__init__(fig, position, params_init)  # ✅ Передаём в Base 

    MODEL_TYPE = 'ios'
    SLIDER_CONFIG = {
            'ios_k': {'label': 'k', 'borders': (1, 100)},
            'ios_k_os': {'label': 'k_os', 'borders': (0.1, 5)},
            'ios_zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
            'ios_Ti': {'label': 'Ti', 'borders': (0.02, 0.5)},
            'ios_T': {'label': 'T', 'borders': (0.005, 1)}
        }
    PLOT_TITLE = 'Гидропривод с ИОС'
    PARAMS_KEY = 'ios'


    

    
