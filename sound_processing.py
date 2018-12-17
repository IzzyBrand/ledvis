import numpy as np
import time

###################################################################################################
# Normalizing
###################################################################################################

class Bounder:
    '''
    Used to estimate the upper and lower bounds on a stream of incoming
    data. Can handle scalar and vector data. Also facilitate contracting
    the bounds over time.
    '''
    def __init__(self, init_L=0.0, init_U=1.0, constrain_bounds=False):
        self.init_U = init_U
        self.init_L = init_L
        self.U = self.init_U
        self.L = self.init_L
        self.U_contraction_rate = 0.995
        self.L_contraction_rate = 0.995

        self.constrain_bounds = constrain_bounds

        self.dtype = type(self.init_U)
        assert(type(self.init_U) == type(self.init_L))

    def update(self, a):
        # contract the array size
        old_size = self.U - self.L
        self.U -= (1.-self.U_contraction_rate) * old_size
        self.L += (1.-self.L_contraction_rate) * old_size

        # and update the bounds
        if self.dtype == np.ndarray:
            self.U = np.max([self.U, a], axis=0)
            self.L = np.min([self.L, a], axis=0)
            if self.constrain_bounds:
                self.U = np.max([self.U, self.init_U], axis=0)
                self.L = np.min([self.L, self.init_L], axis=0)

        else:
            self.U = max(self.U, np.max(a))
            self.L = min(self.L, np.min(a))
            if self.constrain_bounds:
                self.U = max(self.U, self.init_U)
                self.L = min(self.L, self.init_L)

    def normalize(self, a):
        return (a - self.L)/(self.U - self.L)

    def update_and_normalize(self, a):
        self.update(a)
        return self.normalize(a)

def hertz_to_mel(freq):
    """Returns mel-frequency from linear frequency input.
    Parameter
    ---------
    freq : scalar or ndarray
        Frequency value or array in Hz.
    Returns
    -------
    mel : scalar or ndarray
        Mel-frequency value or ndarray in Mel
    """
    return 2595.0 * np.log10(1 + (freq / 700.0))

###################################################################################################
# Smoothing
###################################################################################################

class SmootherBase:
    def __init__(self):
        pass

    def smooth(self, x):
        return x

class ExponentialMovingAverage(SmootherBase):
    def __init__(self, alpha):
        self._s = 0
        self.alpha = np.clip(alpha, 0.0, 1.0)

    def smooth(self, x):
        self._s = (self.alpha * x) + ((1. - self.alpha) * self._s)
        return self._s

class SplitExponentialMovingAverage(SmootherBase):
    def __init__(self, alpha_down=0.5, alpha_up=0.5):
        self.alpha_down = alpha_down
        self.alpha_up = alpha_up
        self._s = 0

    def smooth(self, x):
        if isinstance(self._s, (list, np.ndarray, tuple)):
            alpha = x - self._s
            alpha[alpha > 0.0] = self.alpha_up
            alpha[alpha <= 0.0] = self.alpha_down
        else:
            alpha = self.alpha_up if x > self._s else self.alpha_down

        self._s = alpha * x + (1.0 - alpha) * self._s
        return self._s

class ExponentialMovingAverageSpikePass(SmootherBase):
    def __init__(self, alpha=0.1, pass_coeff=10):
        self._s = 0
        self._ss = 1
        self.alpha = np.clip(alpha, 0.0, 1.0)
        self.pass_coeff = pass_coeff

    def smooth(self, x):
        old_s = self._s
        self._s = (self.alpha * x) + ((1. - self.alpha) * self._s)
        self._ss = (self.alpha * x**2) + ((1. - self.alpha) * self._ss)
        var = np.abs(self._ss - self._s**2)

        if x > var*self.pass_coeff + old_s:
            self._s = x
        return self._s


class SpeedLimit(SmootherBase):
    def __init__(self, up=None, down=-1):
        self._s = 0
        self.up = up
        self.down = down

    def smooth(self, x):
        # calculate the delta
        d = x - self._s
        # bound the delta
        d = max(d, self.down)
        if self.up is not None: d = min(d, self.up)
        # and update the smoothed value
        self._s += d
        return self._s


class EMASpeedLimit(SmootherBase):
    def __init__(self, alpha=0.4, scale=.5):
        self._s = 0
        self._prev_x = 0
        self.ema = ExponentialMovingAverage(alpha)
        self.scale = scale

    def smooth(self, x):
        dx = x - self._prev_x
        self._prev_x = x

        sdx = abs(self.ema.smooth(dx) * self.scale)

        self._s += np.clip(x - self._s, -sdx, sdx)
        return self._s
