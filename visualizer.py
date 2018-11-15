import numpy as np
import masker
from config import *
from smoother import *


class Visualizer:
    def __init__(self):
        pass

    def visualize(self, sample_array):
        return np.zeros(LED_1_COUNT*3)


class VooMeter:
    def __init__(self, color=np.array([100, 150, 200]), mask_maker=masker.middle_out):
        self.color = color
        self.mask_maker = mask_maker
        self.max_amplitude = 0
        self.min_amplitude = 0
        self.max_amplitude_contraction_rate = 0.01
        self.min_amplitude_contraction_rate = 0.01
        self.voo_smoother = ExponentialMovingAverageSpikePassSmoother(0.05)

    def visualize(self, sample_array):
            m = np.max(sample_array[-10:]) # get the maximum amplitude

            # update the max and min bounds on the amplitude
            self.max_amplitude -= self.max_amplitude_contraction_rate
            self.max_amplitude = max(self.max_amplitude, m)
            self.min_amplitude += self.min_amplitude_contraction_rate
            self.min_amplitude = min(self.min_amplitude, self.max_amplitude - 1) # make sure the min doesn't exceed the max
            self.min_amplitude = min(self.min_amplitude, np.min(sample_array))

            m = float(m - self.min_amplitude)/float(self.max_amplitude-self.min_amplitude) # normalize the amplitude to [0,1]
            m = self.voo_smoother.smooth(m) # and smooth it

            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on

            # create a linear color array to be sent to the LED_writer
            return np.ravel(color_mask * self.color).astype(int)


class BlobSlider(Visualizer):
    def __init__(self):
        pass

    def visualize(sample_array):
        pass

###################################################################################################
# Experimental stuff
###################################################################################################

SAMPLE_FREQUENCY = 3000

def get_max_freq(a):
    '''
    Returns a value from [0,1] indicating the frequency ouf of the maximum
    measurable frequency
    ''' 
    A = abs(np.fft.fft(a))
    # the fourier transform is symmetric, so we can only use the first half
    return np.argmax(A[1:int(SAMPLE_ARRAY_SIZE/2)])/(SAMPLE_ARRAY_SIZE/2.0)
    # freqs = np.arange(SAMPLE_ARRAY_SIZE) * SAMPLE_FREQUENCY/SAMPLE_ARRAY_SIZE
    # max_freq_index = np.argmax(A[1:int(SAMPLE_ARRAY_SIZE/2)])
    # return freqs[max_freq_index]

def sample_color(x):
    # an RGB color whipe from purple to yellow
    color_array = np.array([
        [86,  26,  68],
        [142, 17,  63],
        [197, 10,  60],
        [252, 88,  60],
        [254, 194, 45]
    ], dtype=float)
    # reorder the columns to GRB
    color_array = color_array[[1,0,2], :]

    xs = np.arange(color_array.shape[0],dtype=float)/color_array.shape[0]
    return np.array([np.interp(x, xs, channel) for channel in color_array.T])

