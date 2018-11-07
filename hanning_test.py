from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

duration = .1  # Duration in seconds
signal_frequency = 100
sample_frequency = 1000

# timesteps
t = np.arange(0, duration*sample_frequency)/sample_frequency
# the signal
x = np.sin(2*np.pi*signal_frequency*t)
# number of samples
n = x.size
# hanning window
h = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n)/(n-1))
# h = 1 - np.abs(n/2 - np.arange(n))/(n/2)

# DFT
X = np.fft.fft(x)
X_db = 20 * np.log10(2 * np.abs(X)/n)
# DFT with hanning window
Xh = np.fft.fft(x *h)
Xh_db = 20 * np.log10(2 * np.abs(Xh/n))

# create the x axis of frequencies
f = np.arange(0, n) * sample_frequency/n

plt.subplot(2,1,1)
plt.plot(t, x, label='signal')
plt.plot(t, x * h, label='signal * hanning')
plt.legend()

plt.subplot(2,1,2)
plt.plot(f, X_db, label='fft')
plt.plot(f, Xh_db, label='fft w/ hanning')
plt.legend()
# plt.grid()
plt.show()