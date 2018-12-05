from __future__ import division

import numpy as np
from matplotlib import pyplot as plt
from smoother import *

files = ['data/sample_30s_1.npy', 'data/sample_30s_2.npy', 'data/sample_30s_3.npy']
durations = [30, 30, 30]

fileno = 2
file = files[fileno]
raw_data = np.log(np.load(file))
duration = durations[fileno]
sample_rate = raw_data.shape[0]/duration

vis_rate = 200
samples_per_vis = int(sample_rate/vis_rate)

print('[{}]\t\t{} seconds at {} Hz.\t{} samples per vis'.format(file, duration, sample_rate, samples_per_vis))

# resample the data as the visualizer would
reshaped_data = (raw_data[:-(raw_data.shape[0] % samples_per_vis)]).reshape([-1, samples_per_vis])
sampled_data = np.max(reshaped_data, axis=1)

ema = ExponentialMovingAverageSmoother(0.1)
sl = SpeedLimit()

def smooth(data, smoother):
	return np.array([smoother.smooth(d) for d in data])


plt.plot(np.exp(sampled_data), color=(0,0.5,0,0.5), label='Max')
plt.plot(np.exp(reshaped_data)[:,-1], color=(0,0.5,0,0.2), label='Last')
# plt.plot(np.exp(smooth(sampled_data, sl)), color=(0,0,1,1), label='Speed Limit Smoothed')
plt.plot(np.exp(smooth(sampled_data, ema)), color=(1,0,0,1), label='EMA 0.1 Smoothed')
plt.legend()
plt.show()

