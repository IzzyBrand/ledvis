import numpy as np
import masker
import time
from config import *
from smoother import *

class Visualizer:
    def __init__(self):
        self.init_max_amplitude = 1
        self.init_min_amplitude = 0
        self.max_amplitude = self.init_max_amplitude
        self.min_amplitude = self.init_min_amplitude
        self.max_amplitude_contraction_rate = 0.01
        self.min_amplitude_contraction_rate = 0.01

    def update_bounds(self, sample_array):
        if np.isinf(np.sum(sample_array)): return
        self.max_amplitude -= self.max_amplitude_contraction_rate
        self.max_amplitude = max(self.max_amplitude, np.max(sample_array), self.init_max_amplitude)
        self.min_amplitude += self.min_amplitude_contraction_rate
        self.min_amplitude = min(self.min_amplitude, np.min(sample_array), self.init_min_amplitude)

    def normalize(self, m):
        return (m - self.min_amplitude)/(self.max_amplitude-self.min_amplitude)

    def visualize(self, sample_array):
        self.update_bounds(sample_array) # update the max and min observed sample
        m = sample_array[-1] # pull out the most recent sample
        m = self.normalize(most_recent_sample) # normalize it to be from 0 to 1

        # make an array with LED_1_COUNT elements, where one entry is 255 and the rest are zeros.
        color_channel = 255 * (np.arrange(LED_1_COUNT) == int(m * LED_1_COUNT))

        # there are three color channels. repeating the same array three times yields white
        return np.concatenate([color_channel, color_channel, color_channel])


class VooMeter(Visualizer):
    def __init__(self, color=np.array([120, 200, 100]), mask_maker=masker.middle_out):
        Visualizer.__init__(self)
        self.color = color
        self.mask_maker = mask_maker
        self.smoother = ExponentialMovingAverageSpikePassSmoother(0.1)

    def visualize(self, sample_array):
            self.update_bounds(sample_array)

            m = np.max(sample_array[-8:]) # get the maximum amplitude
            m = self.normalize(m) # normalize the amplitude to [0,1]
            m = self.smoother.smooth(m) # and smooth it

            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on

            # create a linear color array to be sent to the LED_writer
            return np.ravel(color_mask * self.color).astype(int)


class FFTGauss(Visualizer):
    def __init__(self):
        Visualizer.__init__(self)
        self.hex_colors = ["7B00FF", "5255EE", "29AADD", "00FFCC", "4EFF88", "9CFF44", "EAFF00", "F1AA00", "F85500", "FF0000"]
        self.colors = np.array([hex_to_rgb(h) for h in self.hex_colors])[:,[1,0,2]]
        self.num_bins = self.colors.shape[0]
        self.bin_size = float(LED_1_COUNT)/self.num_bins
        self.centers = (np.arange(self.num_bins) + 0.5) * self.bin_size
        self.gaussians = np.vstack([gaussian(np.arange(LED_1_COUNT), mu, self.bin_size/6) for mu in self.centers])
        self.color_gaussians = np.multiply(self.colors.T[:,:,None], self.gaussians)

    def visualize(self, sample_array):
        # decide how many elements from the FFT to use
        n = int(sample_array.shape[0]/2.0) 
        n -= n % self.num_bins # make n divisible by the number of bins

        f = (np.abs(np.fft.fft(sample_array)[1:n+1])) # take the first n elements of the fft
        bin_activations = np.sum(f.reshape([self.num_bins,-1]), axis=1) # how much in each frequency bin

        # normalize the bin_activations
        self.update_bounds(bin_activations)
        bin_activations = self.normalize(bin_activations)

        # multiple the each bin by its gaussian
        color_array = np.max(self.color_gaussians *  bin_activations[None, :, None], axis=1)

        return np.ravel(color_array.T.astype(int))


class BlobSlider(Visualizer):
    def __init__(self):
        Visualizer.__init__(self)
        self.blob_list = []
        self.max_blob_count = 15
        self.blob_prob = 0.01
        self.prev_time = time.time()
        self.blob_buffer = 10
        self.smoother = ExponentialMovingAverageSpikePassSmoother(0.05)
        self.init_max_amplitude = 100

    def visualize(self, sample_array):
        self.update_bounds(sample_array)
        m = self.normalize(np.max(sample_array[-10]))
        m = self.smoother.smooth(m)

        new_time = time.time()
        dt = new_time - self.prev_time
        self.prev_time = new_time


        if len(self.blob_list) < self.max_blob_count and np.random.rand() < self.blob_prob:
            new_blob = {
                'color': [np.random.randint(10,100), np.random.randint(150,255), np.random.randint(10,120)],
                'speed': np.clip(np.random.normal(8,6), 2, 10),
                'pos': -self.blob_buffer
            }
            self.blob_list.append(new_blob)

        # remove blobs that have gone off the end of the strip
        self.blob_list = [b for b in self.blob_list if b['pos'] < LED_1_COUNT + self.blob_buffer]
        
        colors = np.zeros([LED_1_COUNT, 3])
        x = np.arange(LED_1_COUNT)
        for blob in self.blob_list:
            blob['pos'] += dt * blob['speed']**(2*m + 0.5) # move the blobs
            colors = np.maximum(colors, np.outer(gaussian(x, blob['pos'], 2.5), blob['color']))

        colors = np.clip(colors, 0, 255).astype(int)
        return np.ravel(colors)

###################################################################################################
# Experimental stuff
###################################################################################################

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

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

