from matplotlib.widgets import Slider


class MySlider:
    """Обёртка над matplotlib Slider для удобного управления"""
    
    def __init__(self, slider_ax_pos, fig):
        self.position = slider_ax_pos
        self.fig = fig
        
        # Создание осей для слайдера
        self.ax = self.fig.add_axes([
            self.position[0],
            self.position[1],
            self.position[2],
            self.position[3],
        ])
        
        self.slider = None
    
    def _add_slider(self, label, vmin, vmax, valinit, color='#3498db'):

        self.slider = Slider(
            ax=self.ax,
            label=label,
            valmin=vmin,
            valmax=vmax,
            valinit=valinit,
            facecolor=color  # ✅ facecolor, не color!
        )
    
    def connect_slider(self, update):
        """Подключить обработчик изменения значения"""
        if self.slider:
            self.slider.on_changed(update)
    
    def get_value(self):
        """Получить текущее значение слайдера"""
        return self.slider.val
    
    def set_value(self, value):
        """Установить значение слайдера программно"""
        
        self.slider.set_val(value)
    
    def destroy(self):
        """Удалить слайдер и оси"""
        if self.slider:
            self.slider.ax.remove()
            self.slider = None
        if self.ax:
            self.ax.remove()
            self.ax = None