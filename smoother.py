import numpy as np

class ExponentialMovingAverageSmoother:
	def __init__(self, alpha):
		self._s = 0
		self.alpha = np.clip(alpha, 0.0, 1.0)

	def smooth(self, x):
		self._s = (self.alpha * x) + ((1. - self.alpha) * self._s)
		return self._s


class ExponentialMovingAverageSpikePassSmoother:
	def __init__(self, alpha):
		self._s = 0
		self._ss = 1
		self.alpha = np.clip(alpha, 0.0, 1.0)

	def smooth(self, x):
		old_s = self._s
		self._s = (self.alpha * x) + ((1. - self.alpha) * self._s)
		self._ss = (self.alpha * x**2) + ((1. - self.alpha) * self._ss)
		var = np.abs(self._ss - self._s**2)

		if x > var*5. + old_s:
			self._s = x
			print('SpikePass', (x - old_s)/var)
		return self._s