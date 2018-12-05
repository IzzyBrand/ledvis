import numpy as np

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


class ExponentialMovingAverageSpikePass(SmootherBase):
	def __init__(self, alpha=0.1):
		self._s = 0
		self._ss = 1
		self.alpha = np.clip(alpha, 0.0, 1.0)

	def smooth(self, x):
		old_s = self._s
		self._s = (self.alpha * x) + ((1. - self.alpha) * self._s)
		self._ss = (self.alpha * x**2) + ((1. - self.alpha) * self._ss)
		var = np.abs(self._ss - self._s**2)

		if x > var*5 + old_s:
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



