import numpy as np
from matplotlib import pyplot as plt
from smoother import *

input_freq = 44100
sample_freq = 3000

raw = np.loadtxt(open("testing/sample.csv", "rb"), delimiter=",")

num_sub_samples = int(float(sample_freq)/input_freq * raw.shape[0]) 
sub_sample_rescale = int(float(input_freq)/sample_freq)

L, R = raw[np.arange(num_sub_samples) * sub_sample_rescale, :].T
L_sampled = np.array([np.max(np.abs(L[10*i:10*i+10])) for i in range(int(np.floor(num_sub_samples/10 - 1)))])
L_sampled = L_sampled/np.max(L_sampled)

ema = ExponentialMovingAverageSmoother(0.1)
ema_sp = ExponentialMovingAverageSpikePassSmoother(0.1)
L_smoothed = np.array([ema.smooth(l) for l in L_sampled])
L_smoothed_sp = np.array([ema_sp.smooth(l) for l in L_sampled])

plt.plot(L_sampled, label='Original')
plt.plot(L_smoothed, label='EMA')
plt.plot(L_smoothed_sp, label='EMA_SP')
plt.legend()
plt.show()

