import numpy as np
from scipy import signal

class HydraulicDrive:
    """Универсальный класс гидропривода"""
    
    FORMULAS = {
        # W(p) = K / (T²p² + 2ζTp + 1)
        'no_os': {
            'num': lambda p: [p['no_os_k']],
            'den': lambda p: [p['no_os_T']**2, 2 * p['no_os_zeta'] * p['no_os_T'], 1],
            'steady': lambda p: p['no_os_k'],
        },
        # W(p) = K / (T²p² + 2ζ√(1+K·K_oc)·Tp + (1+K·K_oc))
        'zhos': {
            'num': lambda p: [p['zhos_k']],
            'den': lambda p: [p['zhos_T']**2, 2 * p['zhos_zeta'] * np.sqrt(1 + p['zhos_k'] * p['zhos_k_os']) * p['zhos_T'], 1 + p['zhos_k'] * p['zhos_k_os']],
            'steady': lambda p: p['zhos_k'] / (1 + p['zhos_k'] * p['zhos_k_os']),
        },
        # W(p) = (K·Ti·p + K) / (T²p³ + 2ζTp² + p + K·K_oc)
        'ios': {
            'num': lambda p: [p['ios_k'] * p.get('ios_Ti', 0.03), p['ios_k']],
            'den': lambda p: [p['ios_T']**2, 2 * p['ios_zeta'] * p['ios_T'], 1, p['ios_k'] * p['ios_k_os']],
            'steady': lambda p: 1.0 / p['ios_k_os'],
        }
    }
    
    def __init__(self, system_type, params):
        self.type = system_type
        self.f = self.FORMULAS[system_type]
        self.params = params.copy()
        self.t = None
        self.y = None
        self.steady = None
        self.settling_time = None
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

        self.settling_time = self.t[-1]
        tolerance = 0.05 * self.steady
        for i in range(len(self.y) - 1, -1, -1):
            if abs(self.y[i] - self.steady) > tolerance:
                if i < len(self.t) - 1:
                    self.settling_time = self.t[i + 1]
                break