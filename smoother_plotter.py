from __future__ import division

import numpy as np
from matplotlib import pyplot as plt
from sound_processing import *

files = ['data/sample_30s_1.npy', 'data/sample_30s_2.npy', 'data/sample_30s_3.npy']
durations = [30, 30, 30]

fileno = 2
file = files[fileno]
raw_data = np.load(file)
duration = durations[fileno]
sample_rate = raw_data.shape[0]/duration

vis_rate = 50
samples_per_vis = int(sample_rate/vis_rate)

print('[{}]\t\t{} seconds at {} Hz.\t{} samples per vis'.format(file, duration, sample_rate, samples_per_vis))

# resample the data as the visualizer would
reshaped_data = (raw_data[:-(raw_data.shape[0] % samples_per_vis)]).reshape([-1, samples_per_vis])

###################################################################################################
# Make sure Bounder works as expected
###################################################################################################

# maxed_data = np.max(reshaped_data, axis=1)/float(np.max(reshaped_data))
# sampled_data = np.max(reshaped_data[:,-8:], axis=1)


# bounder = Bounder(100, 500, constrain_bounds=True)
# def u(x):
# 	bounder.update(x)
# 	return bounder.U

# bounder = Bounder(100, 500, constrain_bounds=True)
# def l(x):
# 	bounder.update(x)
# 	return bounder.L

# # bounded_data = np.array([bounder.update_and_normalize(np.max(d[-8:])) for d in reshaped_data])
# upper_bound = np.array([u(d) for d in sampled_data])
# lower_bound = np.array([l(d) for d in sampled_data])

# plt.plot(sampled_data, color=(0,0.5,0,0.5), label='Max')
# plt.plot(upper_bound, color=(0,0,1,1), label='upper')
# plt.plot(lower_bound, color=(1,0,0,1), label='lower')
# plt.legend()
# plt.show()

###################################################################################################
# Testing out some smoothers
###################################################################################################

bounder = Bounder()
sampled_data = np.max(reshaped_data[:,-8:], axis=1)
normalized_data = [bounder.update_and_normalize(d) for d in sampled_data]

ema = ExponentialMovingAverage(0.1)
ema_data = [ema.smooth(d) for d in sampled_data]

exp_ema_data = np.log(np.array([ema.smooth(d) for d in np.exp(sampled_data/np.max(sampled_data))])+1) * np.max(sampled_data)
log_ema_data = np.exp(np.array([ema.smooth(d) for d in np.log(sampled_data+1)]))


plt.plot(sampled_data, color=(0,0.5,0,0.5), label='raw')
plt.plot(ema_data, color=(0,0,1,1), label='ema')
plt.plot(exp_ema_data, color=(1,0,0,1), label='exp')
plt.plot(log_ema_data, color=(0,1,0,1), label='log')
# plt.plot(reshaped_data[:,-1], color=(0,0.5,0,0.2), label='Last')
# plt.plot(np.exp(smooth(sampled_data, sl)), color=(0,0,1,1), label='Speed Limit Smoothed')
# plt.plot(smooth(sampled_data, ema), color=(1,0,0,1), label='EMA 0.1 Smoothed')
plt.legend()
plt.show()

