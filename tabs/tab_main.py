# tabs/tab_main.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from models.hydraulic import HydraulicDrive
from widgets.sliders import MySlider


class TabMain:
    """Вкладка с тремя гидроприводами: график слева, выводы справа"""

    def __init__(self, fig, position, params_init):
        self.fig = fig
        self.position = position
        self.params_init = params_init
        
        self.ax_container = fig.add_axes(position)
        self.ax_container.axis('off')
        
        self.drives = []
        self.ax = None
        self.lines = []
        self.steady_lines = []
        self.sliders = {}
        self.texts = []
        self.animation = None
        
        self.info_ax = None
        self.info_table = None
        self.info_summary = None
        
        self.graph_width = 0.55
        self.info_width = 0.35
        self.gap = 0.05
        
        self._create_drives()
        self._create_plot()
        self._create_sliders()
        self._setup_animation()
        self._update_info()
    
    def _create_drives(self):
        """Создать три гидропривода"""
        self.drives = [
            HydraulicDrive('no_os', self.params_init['no_os'].copy()),
            HydraulicDrive('zhos', self.params_init['zhos'].copy()),
            HydraulicDrive('ios', self.params_init['ios'].copy())
        ]
    
    def _create_plot(self):
        """Создать график в левой части"""
        colors = ['#e74c3c', '#3498db', '#2ecc71']
        labels = ['Без ОС', 'С ЖОС', 'С ИОС']
        
        x_max = 0.8
        
        all_steady = [drive.steady for drive in self.drives]
        all_max = [drive.max_val for drive in self.drives]
        y_max = max(max(all_steady) * 1.4, max(all_max) * 1.2, 1.5)
        
        left_rel = 0.05
        bottom_rel = 0.45
        width_rel = self.graph_width
        height_rel = 0.4
        
        self.ax = self.fig.add_axes([
            self.position[0] + left_rel,
            self.position[1] + bottom_rel,
            width_rel, height_rel
        ])
        
        self.ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
        self.ax.set_xlim(0, x_max)
        self.ax.set_ylim(0, y_max)
        
        self.ax.axhline(y=1, color='gray', ls=':', lw=1, label='Задание', alpha=0.7)
        
        self.ax.set_title('Сравнение гидроприводов', pad=12, fontsize=11)
        self.ax.set_xlabel('Время, с', fontsize=9)
        self.ax.set_ylabel('Выход', fontsize=9)
        
        self.ax.tick_params(labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#cccccc')
            spine.set_linewidth(0.5)
        
        self.lines = []
        for i, drive in enumerate(self.drives):
            line, = self.ax.plot([], [], color=colors[i], lw=1.8, label=labels[i],
                                solid_capstyle='round', solid_joinstyle='round')
            self.lines.append(line)
        
        self.steady_lines = []
        for i, drive in enumerate(self.drives):
            steady_line = self.ax.axhline(y=drive.steady, color=colors[i], 
                                         ls='--', lw=1, alpha=0.6)
            self.steady_lines.append(steady_line)

        self.ax.legend(loc='lower right', framealpha=0.9, fontsize=8, frameon=True)
        
        # ===== ПРАВАЯ ЧАСТЬ: ИНФОРМАЦИОННАЯ ПАНЕЛЬ =====
        info_x = self.position[0] + left_rel + width_rel + self.gap
        info_y = self.position[1] + bottom_rel
        info_w = self.info_width
        info_h = height_rel
        
        self.info_ax = self.fig.add_axes([info_x, info_y, info_w, info_h])
        self.info_ax.axis('off')
        self.info_ax.set_facecolor('#ffffff')
        
        self.info_ax.text(0.385, 0.96, 'АНАЛИЗ ХАРАКТЕРИСТИК', 
                         fontsize=14, weight='bold', ha='center', va='top',
                         transform=self.info_ax.transAxes, color='#000000')
        
        self.info_ax.text(0.39, 0.91, 'Сравнение систем управления', 
                         fontsize=11, ha='center', va='top',
                         transform=self.info_ax.transAxes, color='#666666')
        
        self.info_table = self.info_ax.text(
            0.08, 0.80, '', fontsize=11, va='top', ha='left',
            transform=self.info_ax.transAxes, family='monospace',
            color='#000000'
        )
        
        self.info_ax.text(0.08, 0.51, '_' * 59, fontsize=10, va='top', ha='left',
                         transform=self.info_ax.transAxes, color='#999999')
        
        self.info_summary = self.info_ax.text(
            0.08, 0.45, '', fontsize=11, va='top', ha='left',
            transform=self.info_ax.transAxes, family='monospace',
            color='#000000'
        )
    
    def _calculate_metrics(self, drive):
        """Рассчитать метрики качества для привода"""
        t = drive.t
        y = drive.y
        
        steady_error = abs(drive.steady - 1.0) * 100
        overshoot = max(0, (drive.max_val - 1.0) / 1.0 * 100)
        
        rise_time = 0.0
        for i, val in enumerate(y):
            if val >= 0.9:
                rise_time = t[i]
                break
        
        settling_time = t[-1]
        tolerance = 0.05 * drive.steady
        for i in range(len(y) - 1, -1, -1):
            if abs(y[i] - drive.steady) > tolerance:
                if i < len(t) - 1:
                    settling_time = t[i + 1]
                break
        
        return {
            'steady': drive.steady,
            'steady_error': steady_error,
            'overshoot': overshoot,
            'rise_time': rise_time,
            'settling_time': settling_time,
            'max_val': drive.max_val
        }
    
    def _format_table(self, metrics):
        """Сформировать строгую таблицу без рамок"""
        lines = []
        lines.append(f"{'Параметр':<18} {'Без ОС':>8} {'ЖОС':>8} {'ИОС':>8}")
        lines.append(f"{'':<18} {'':->8} {'':->8} {'':->8}")
        
        lines.append(f"{'Уст. значение':<18} {metrics['no_os']['steady']:>8.3f} {metrics['zhos']['steady']:>8.3f} {metrics['ios']['steady']:>8.3f}")
        lines.append(f"{'Стат. ошибка, %':<18} {metrics['no_os']['steady_error']:>8.1f} {metrics['zhos']['steady_error']:>8.1f} {metrics['ios']['steady_error']:>8.1f}")
        lines.append(f"{'Перерегулир., %':<18} {metrics['no_os']['overshoot']:>8.1f} {metrics['zhos']['overshoot']:>8.1f} {metrics['ios']['overshoot']:>8.1f}")
        lines.append(f"{'t нарастания, с':<18} {metrics['no_os']['rise_time']:>8.3f} {metrics['zhos']['rise_time']:>8.3f} {metrics['ios']['rise_time']:>8.3f}")
        lines.append(f"{'t регулир., с':<18} {metrics['no_os']['settling_time']:>8.3f} {metrics['zhos']['settling_time']:>8.3f} {metrics['ios']['settling_time']:>8.3f}")
        
        return '\n'.join(lines)
    
    def _format_summary(self, metrics):
        """Сформировать строгие выводы без цветов"""
        names = {'no_os': 'Без ОС', 'zhos': 'С ЖОС', 'ios': 'С ИОС'}
        
        best_settling = min(self.drives, key=lambda d: self._calculate_metrics(d)['settling_time'])
        best_overshoot = min(self.drives, key=lambda d: self._calculate_metrics(d)['overshoot'])
        best_error = min(self.drives, key=lambda d: self._calculate_metrics(d)['steady_error'])
        
        lines = []
        lines.append('РЕЗУЛЬТАТЫ СРАВНЕНИЯ:')
        lines.append('')
        # ✅ ИСПРАВЛЕНО: drive.type вместо drive.model_type
        lines.append(f"1. Быстродействие:      {names[best_settling.type]:<8} (t = {metrics[best_settling.type]['settling_time']:.3f} с)")
        lines.append(f"2. Перерегулирование:   {names[best_overshoot.type]:<8} (σ = {metrics[best_overshoot.type]['overshoot']:.1f}%)")
        lines.append(f"3. Точность:            {names[best_error.type]:<8} (δ = {metrics[best_error.type]['steady_error']:.1f}%)")
        lines.append('')
        
        if best_error.type == 'ios' and best_settling.type == 'ios':
            rec = 'РЕКОМЕНДАЦИЯ: Система с ИОС показывает наилучшие'
            rec2 = 'характеристики по всем критериям.'
        elif best_overshoot.type == 'zhos':
            rec = 'РЕКОМЕНДАЦИЯ: Система с ЖОС обеспечивает работу'
            rec2 = 'без перерегулирования.'
        elif best_error.type == 'no_os':
            rec = 'РЕКОМЕНДАЦИЯ: Система без ОС применима для задач'
            rec2 = 'с низкими требованиями к точности.'
        else:
            rec = 'РЕКОМЕНДАЦИЯ: Выбор системы зависит от приоритета'
            rec2 = 'критериев качества.'
        
        lines.append(rec)
        lines.append(rec2)
        
        return '\n'.join(lines)
    
    def _update_info(self):
        """Обновить информационную панель"""
        metrics = {}
        
        for drive in self.drives:
            # ✅ ИСПРАВЛЕНО: drive.type вместо drive.model_type
            metrics[drive.type] = self._calculate_metrics(drive)
        
        if self.info_table:
            self.info_table.set_text(self._format_table(metrics))
        
        if self.info_summary:
            self.info_summary.set_text(self._format_summary(metrics))
    
    def _create_sliders(self):
        """Создать слайдеры"""
        colors = ['#e74c3c', '#3498db', '#2ecc71']
        titles = ['Без ОС', 'С ЖОС', 'С ИОС']
        sys_types = ['no_os', 'zhos', 'ios']  # ✅ Добавили список систем
        
        col_width = 0.15
        start_x = 0.05
        
        # Заголовки колонок
        for i, color in enumerate(colors):
            x_txt = start_x + i * (col_width+0.05) + col_width/ 2
            y_txt = self.position[1] + 0.35
            text = self.fig.text(x_txt, y_txt, titles[i], 
                        fontsize=9, weight='bold', color=color, ha='center')
            self.texts.append(text)
        
        dy = 0.04
        
        SLIDER_CONFIG = {
            'no_os': {
                'k': {'label': 'k', 'borders': (1, 100)},
                'zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
                'T': {'label': 'T', 'borders': (0.005, 1)}
            },
            'zhos': { 
                'k': {'label': 'k', 'borders': (1, 100)},
                'k_os': {'label': 'k_os', 'borders': (0.1, 5)},
                'zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
                'T': {'label': 'T', 'borders': (0.005, 1)}
            },
            'ios': {
                'k': {'label': 'k', 'borders': (1, 100)},
                'k_os': {'label': 'k_os', 'borders': (0.1, 5)},
                'zeta': {'label': 'ζ', 'borders': (0.1, 2.0)},
                'Ti': {'label': 'Ti', 'borders': (0.02, 0.5)},
                'T': {'label': 'T', 'borders': (0.005, 1)}
            }
        }
        
        # ✅ Создаём слайдеры с УНИКАЛЬНЫМИ ключами
        for i, (sys_type, params) in enumerate(SLIDER_CONFIG.items()):
            for j, (name, confs) in enumerate(params.items()):
                
                # ✅ Уникальный ключ: 'no_os_k', 'zhos_k', 'ios_k'
                slider_key = f"{sys_type}_{name}"
                
                slider_ax_pos = [
                    self.position[0] + 0.05 + (col_width+0.05)*i,
                    self.position[1] + 0.3 - dy * j,
                    col_width,
                    0.02
                ]
                slider = MySlider(slider_ax_pos, self.fig)
                slider._add_slider(
                    confs['label'],
                    *confs['borders'],
                    self.params_init[sys_type][name],  
                    colors[i]
                )
                slider.connect_slider(self.update)
                self.sliders[slider_key] = slider  # ✅ Сохраняем с уникальным ключом!
    
    def _setup_animation(self):
        """Настроить анимацию"""
        def init():
            for line in self.lines:
                line.set_data([], [])
            return self.lines

        def animate(frame):
            max_len = min([len(drive.t) for drive in self.drives if len(drive.t) > 0], default=0)
            if frame > max_len:
                frame = max_len
            for i, drive in enumerate(self.drives):
                self.lines[i].set_data(drive.t[:frame], drive.y[:frame])
            return self.lines
        
        self.animation = FuncAnimation(self.fig, animate, init_func=init,
                                       frames=1000, interval=30, blit=False)
    
    def update(self, val):
        """Обновить данные при изменении слайдеров"""
        params = self._get_params()
        
        try:
            for drive in self.drives:
                # ✅ ИСПРАВЛЕНО: drive.type вместо drive.model_type
                drive.params.update(params[drive.type])
                drive.calc()
            
            all_t = np.concatenate([drive.t for drive in self.drives])
            x_max = max(all_t) if len(all_t) > 0 else 10
            
            all_steady = [drive.steady for drive in self.drives]
            all_max = [drive.max_val for drive in self.drives]
            y_max = max(max(all_steady) * 1.4, max(all_max) * 1.2, 1.5)
            
            self.ax.set_xlim(0, x_max)
            self.ax.set_ylim(0, y_max)

                    # ✅ ДОБАВИТЬ: Обновление линий графика
            for i, drive in enumerate(self.drives):
                self.lines[i].set_data(drive.t, drive.y)
            
            for i, steady_line in enumerate(self.steady_lines):
                steady_line.set_ydata([self.drives[i].steady, self.drives[i].steady])
            
            self._update_info()
            self.fig.canvas.draw_idle()

            
        except Exception as e:
            print(f"Ошибка при обновлении: {e}")
    
    def _get_params(self):
        """Собрать параметры из слайдеров"""
        return {
            'no_os': {
                'k': self.sliders['no_os_k'].get_value(),
                'zeta': self.sliders['no_os_zeta'].get_value(),
                'T': self.sliders['no_os_T'].get_value()
            },
            'zhos': {
                'k': self.sliders['zhos_k'].get_value(),
                'k_os': self.sliders['zhos_k_os'].get_value(),  # ✅ Ключ с подчёркиванием
                'zeta': self.sliders['zhos_zeta'].get_value(),
                'T': self.sliders['zhos_T'].get_value()
            },
            'ios': {
                'k': self.sliders['ios_k'].get_value(),
                'k_os': self.sliders['ios_k_os'].get_value(),  # ✅ Ключ с подчёркиванием
                'zeta': self.sliders['ios_zeta'].get_value(),
                'Ti': self.sliders['ios_Ti'].get_value(),
                'T': self.sliders['ios_T'].get_value()
            }
        }
    
    def destroy(self):
        """Очистить ресурсы"""
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        
        for ax in [self.ax, self.info_ax, self.ax_container]:
            if ax:
                try:
                    ax.remove()
                except:
                    pass
        
        for slider in list(self.sliders.values()):
            try:
                if hasattr(slider, 'ax'):
                    slider.ax.remove()
            except:
                pass
        
        for text in self.texts:
            try:
                text.remove()
            except:
                pass
        
        self.lines.clear()
        self.steady_lines.clear()
        self.sliders.clear()
        self.texts.clear()
        self.drives.clear()