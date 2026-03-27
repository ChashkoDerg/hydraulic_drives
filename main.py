import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from tabs.tab_main import TabMain
from tabs.tab_selfs import TabNoOs, TabZhOs, TabIOs




class TabManager:
    """Управляет вкладками и их переключением"""
    
    def __init__(self, fig, params_init):
        self.fig = fig
        self.params_init = params_init
        self.current_tab = None
        self.tabs = []  # Список вкладок для итерации
        
        # Определяем структуру вкладок (легко расширять)
        self.tab_configs = [
            {"name": "Гидроприводы", "class": TabMain},
            {"name": "ГП без ОС", "class": TabNoOs},
            {"name": "ГП с ЖОС", "class": TabZhOs},
            {"name": "ГП с ИОС", "class": TabIOs},
        ]
        
        self._create_buttons()
        self._show_first_tab()
    
    def _create_buttons(self):
        """Создает кнопки для всех вкладок динамически"""
        self.buttons = []
        button_width = 0.1
        start_x = 0.0
        button_height = 0.03
        y_position = 0.97
        
        for i, config in enumerate(self.tab_configs):
            # Позиция кнопки: [x, y, width, height]
            ax = plt.axes([start_x + i * button_width, y_position, button_width, button_height])
            btn = Button(ax, config["name"])
            # Привязываем конкретный tab_class через замыкание
            btn.on_clicked(lambda event, tab_class=config["class"]: self.switch_to_tab(tab_class))
            self.buttons.append(btn)
    
    def switch_to_tab(self, tab_class):
        """Переключается на указанную вкладку"""
        if self.current_tab:
            try:
                self.current_tab.destroy()
            except Exception:
                pass
        
        self.current_tab = tab_class(self.fig, [0.0, 0.03, 0.9, 0.85], self.params_init)
        self.fig.canvas.draw_idle()
    
    def _show_first_tab(self):
        """Показывает первую вкладку при запуске"""
        if self.tab_configs:
            self.switch_to_tab(self.tab_configs[0]["class"])


class PlotWindow:
    """Главное окно приложения"""
    
    def __init__(self, params_init):
        self.fig = plt.figure(figsize=(20, 10))
        self.tab_manager = TabManager(self.fig, params_init)
    
    def show(self):
        plt.show()


# Использование
if __name__ == "__main__":
    params_init = {
        'no_os': {'k': 25, 'zeta': 0.3, 'T': 0.025},
        'zhos': {'k': 25, 'k_os': 1, 'zeta': 0.65, 'T': 0.025},
        'ios': {'k': 22, 'k_os': 1, 'zeta': 0.8, 'Ti': 0.015, 'T': 0.024}
    }
    
    app = PlotWindow(params_init)
    app.show()