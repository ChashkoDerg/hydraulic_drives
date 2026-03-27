import numpy as np
from scipy import signal

class HydraulicDrive:
    """Универсальный класс гидропривода"""
    
    FORMULAS = {
        # W(p) = K / (T²p² + 2ζTp + 1)
        'no_os': {
            'num': lambda p: [p['k']],
            'den': lambda p: [p['T']**2, 2 * p['zeta'] * p['T'], 1],
            'steady': lambda p: p['k'],
        },
        # W(p) = K / (T²p² + 2ζ√(1+K·K_oc)·Tp + (1+K·K_oc))
        'zhos': {
            'num': lambda p: [p['k']],
            'den': lambda p: [p['T']**2, 2 * p['zeta'] * np.sqrt(1 + p['k'] * p['k_os']) * p['T'], 1 + p['k'] * p['k_os']],
            'steady': lambda p: p['k'] / (1 + p['k'] * p['k_os']),
        },
        # W(p) = (K·Ti·p + K) / (T²p³ + 2ζTp² + p + K·K_oc)
        'ios': {
            'num': lambda p: [p['k'] * p.get('Ti', 0.03), p['k']],
            'den': lambda p: [p['T']**2, 2 * p['zeta'] * p['T'], 1, p['k'] * p['k_os']],
            'steady': lambda p: 1.0 / p['k_os'],
        }
    }
    
    def __init__(self, system_type, params):
        self.type = system_type
        self.f = self.FORMULAS[system_type]
        self.params = params.copy()
        self.t = None
        self.y = None
        self.steady = None
        self.calc()
    
    def calc(self):
        num = self.f['num'](self.params)
        den = self.f['den'](self.params)
        
        sys = signal.TransferFunction(num, den)
        
        t_max = 0.8
        self.t = np.linspace(0, t_max, 400)
        _, self.y = signal.step(sys, T=self.t)
        
        self.steady = self.f['steady'](self.params)
        self.max_val = np.max(self.y)