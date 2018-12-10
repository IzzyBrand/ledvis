import numpy as np
import masker
import time
from config import *
from sound_processing import *


class VisualizerBase:
    '''
    Base class for the visualizer. This structure takes in incoming audio data and generates
    output colors for the LED strips
    '''
    def __init__(self):
        self.name = self.__class__.__name__

    def visualize(self, sample_array):
        return np.zeros([LED_1_COUNT, 3], dtype=int)


class ExampleVisualizer(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.bounder = Bounder()

    def visualize(self, sample_array):
        self.bounder.update(sample_array) # update the max and min observed sample
        m = sample_array[-1] # pull out the most recent sample
        m = self.bounder.normalize(most_recent_sample) # normalize it to be from 0 to 1

        # make an array with LED_1_COUNT elements, where one entry is 255 and the rest are zeros.
        color_channel = 255 * (np.arrange(LED_1_COUNT) == int(m * LED_1_COUNT))

        # there are three color channels. repeating the same array three times yields white
        return np.vstack([color_channel, color_channel, color_channel]).T


class StripsOff(VisualizerBase):
    def visualize(self, sample_array):
        color_array = np.zeros([LED_1_COUNT,3], dtype=int)
        return color_array


class VooMeter(VisualizerBase):
    def __init__(self, color=np.array([120, 200, 100]), mask_maker=masker.middle_out):
        VisualizerBase.__init__(self)
        self.color = color
        self.mask_maker = mask_maker
        self.smoother = ExponentialMovingAverageSpikePass(0.1)
        self.bounder = Bounder()

    def visualize(self, sample_array):
            self.bounder.update(sample_array)

            m = np.max(sample_array[-8:]) # get the maximum amplitude
            m = self.bounder.normalize(m) # normalize the amplitude to [0,1]
            m = self.smoother.smooth(m) # and smooth it

            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on

            # create a color array to be sent to the LED_writer
            return color_mask * self.color


class FFTGauss(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.hex_colors = ["7B00FF", "5255EE", "29AADD", "00FFCC", "4EFF88", "9CFF44", "EAFF00", "F1AA00", "F85500", "FF0000"]
        self.colors = np.array([hex_to_rgb(h) for h in self.hex_colors])[:,[1,0,2]]
        self.num_bins = self.colors.shape[0]
        self.bin_size = float(LED_1_COUNT)/self.num_bins
        self.centers = (np.arange(self.num_bins) + 0.5) * self.bin_size
        self.gaussians = np.vstack([gaussian(np.arange(LED_1_COUNT), mu, self.bin_size) for mu in self.centers])
        self.color_gaussians = np.multiply(self.colors.T[:,:,None], self.gaussians)
        self.bounder = Bounder()

    def visualize(self, sample_array):
        fft = np.abs(np.fft.rfft(sample_array))
        n = fft.shape[0]
        n -= n % self.num_bins # make n divisible by the number of bins
        fft = fft[:n] # take the first n elements of the fft

        bin_activations = np.sum(fft.reshape([self.num_bins,-1]), axis=1) # how much in each frequency bin

        # normalize the bin_activations
        self.bounder.update(bin_activations)
        bin_activations = self.bounder.normalize(bin_activations)

        # multiple the each bin by its gaussian
        color_array = np.max(self.color_gaussians *  bin_activations[None, :, None], axis=1)

        return color_array.T


class FFTGaussBeads(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.hex_colors = ["7B00FF", "5255EE", "29AADD", "00FFCC", "4EFF88", "9CFF44", "EAFF00", "F1AA00", "F85500", "FF0000"]
        self.colors = np.array([hex_to_rgb(h) for h in self.hex_colors])[:,[1,0,2]]
        self.num_bins = self.colors.shape[0]
        self.bin_size = float(LED_1_COUNT)/self.num_bins
        self.centers = (np.arange(self.num_bins) + 0.5) * self.bin_size
        self.gaussians = np.vstack([gaussian(np.arange(LED_1_COUNT), mu, self.bin_size/4) for mu in self.centers])
        self.color_gaussians = np.multiply(self.colors.T[:,:,None], self.gaussians)
        self.bounder = Bounder()
        self.bounder.U_contraction_rate = 0.99

    def visualize(self, sample_array):
        fft = np.abs(np.fft.rfft(sample_array))
        n = fft.shape[0]
        n -= n % self.num_bins # make n divisible by the number of bins
        fft = fft[:n] # take the first n elements of the fft

        bin_activations = np.sum(fft.reshape([self.num_bins,-1]), axis=1) # how much in each frequency bin
        bin_activations = bin_activations**2

        # normalize the bin_activations
        bin_activations = self.bounder.update_and_normalize(bin_activations)

        # multiple the each bin by its gaussian
        color_array = np.max(self.color_gaussians *  bin_activations[None, :, None], axis=1)

        return color_array.T


class BlobSlider(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.blob_list = []
        self.max_blob_count = 15
        self.blob_prob = 0.02
        self.prev_time = time.time()
        self.blob_buffer = 10
        self.bounder = Bounder(constrain_bounds=True)
        self.smoother = ExponentialMovingAverageSpikePass(0.05)
        self.init_max_amp = 100

    def visualize(self, sample_array):  
        m = self.bounder.update_and_normalize(np.max(sample_array[-10]))
        m = self.smoother.smooth(m)

        new_time = time.time()
        dt = new_time - self.prev_time
        self.prev_time = new_time


        blob_count = len(self.blob_list)
        if blob_count < self.max_blob_count and np.random.rand() < self.blob_prob/(blob_count + 1):
            new_blob = {
                'color': [np.random.randint(10,100), np.random.randint(150,255), np.random.randint(10,120)],
                'speed': np.clip(np.random.normal(7,3), 2, 10),
                'pos': -self.blob_buffer
            }
            self.blob_list.append(new_blob)

        # remove blobs that have gone off the end of the strip
        self.blob_list = [b for b in self.blob_list if b['pos'] < LED_1_COUNT + self.blob_buffer]

        color_array = np.zeros([LED_1_COUNT, 3])
        x = np.arange(LED_1_COUNT)
        for blob in self.blob_list:
            blob['pos'] += dt * blob['speed']**(2*m + 0.5) # move the blobs
            color_array = np.maximum(color_array, np.outer(gaussian(x, blob['pos'], 2.5), blob['color']))

        return np.clip(color_array, 0, 255)


class Zoom(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.bounder = Bounder()
        self.stripe_list = []
        self.prev_time = time.time()
        self.zoom_rate = 1.
        self.curr_color = 0

        new_stripe = {
            'color': np.random.randint(0,255,3),
            'width': 1
        }
        self.stripe_list.append(new_stripe)

    def visualize(self, sample_array):
        m = self.bounder.update_and_normalize(np.max(sample_array[-10]))

        new_time = time.time()
        dt = new_time - self.prev_time
        self.prev_time = new_time

        colors = np.zeros([LED_1_COUNT, 3], dtype=int)

        i = 0
        count = 0
        center = int(np.ceil(LED_1_COUNT/2))
        top = LED_1_COUNT - center
        for stripe in self.stripe_list:
            stripe['width'] += self.zoom_rate * stripe['width'] * dt

            w = int(stripe['width'])
            j = min(top, w + i)
            colors[center + i: center + j, :] = stripe['color']
            colors[center - j: center - i, :] = stripe['color']

            if j == top:
                break
            else:
                i = j
                count += 1

        self.stripe_list = self.stripe_list[:count + 1]

        if int(self.stripe_list[0]['width']) > 1:
            new_stripe = {
                'color': [np.random.randint(10,100), np.random.randint(150,255), np.random.randint(10,120)],
                'width': 1
            }
            new_stripe['color'][self.curr_color] *= 0.2
            self.curr_color = (self.curr_color + 1) % 3
            self.stripe_list.insert(0, new_stripe)

        return colors


class Sparkle(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.bounder = Bounder()

    def visualize(self, sample_array):
        a = sample_array[-8:]
        m = np.max(a) # get the maximum amplitude
        m = self.bounder.update_and_normalize(m) # normalize the amplitude to [0,1]
        m = max(m**3 * 0.5, - 0.05, 0.01)
        mask = np.random.rand(LED_1_COUNT) < m
        colors = np.random.randint(0,255, [LED_1_COUNT, 3])
        return mask[:, None] * colors


class Retro(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.color = np.array([75, 75, 10])
        self.floater_color = np.array([40, 160, 230])
        self.mask_maker = masker.bottom_up
        self.bounder = Bounder()
        self.smoother = ExponentialMovingAverage(0.2)

        self.descent_rate = 0.008
        self.fade_size = 20
        self.fade = (np.arange(self.fade_size, dtype=float)/self.fade_size)[:,None]
        self.floater = 0
        self.max_maker = masker.bottom_up

    def visualize(self, sample_array):
            m = np.max(sample_array[-8:]) # get the maximum amplitude
            m = self.bounder.update_and_normalize(m) # normalize the amplitude to [0,1]
            m = np.log(self.smoother.smooth(np.exp(m+2)))-2 # and smooth it

            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on
            color_array = color_mask * self.color

            self.floater = max(self.floater - self.descent_rate, m) # get the position of the floater
            floater_index = max(int((LED_1_COUNT-1) * self.floater), self.fade_size) # make it an index

            # and replace a stripe of colors below that index
            i = floater_index - self.fade_size + 1
            j = floater_index + 1
            part_1 = (1 - self.fade) * color_array[i:j, :]
            part_2 = self.fade * self.floater_color
            color_array[i:j, :] =  part_1 + part_2
            
            return color_array


class SamMode(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.counter = 0
        self.t = time.time()

    def visualize(self, sample_array):
        tt = time.time()
        dt = tt - self.t
        self.t = tt
        self.counter += dt * 3.
        color_array = np.zeros([LED_1_COUNT,3], dtype=int)

        half_way = int(np.floor(LED_1_COUNT/2.0))
        indices = np.arange(half_way)/4. + self.counter
        b = np.zeros(LED_1_COUNT)
        b[:half_way] = indices
        b[-half_way:] = np.flipud(indices)

        color_array[:,2] = (np.sin(b) + 1) * 50.

        return color_array


class Pancakes(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.pancake_color = np.array([100, 50, 160])
        self.color = np.array([50, 80, 0])

        self.mask_maker = masker.bottom_up
        self.smoother = ExponentialMovingAverageSpikePass(0.1, pass_coeff=20)
        self.bounder = Bounder()

        self.num_cakes = 10
        self.positions = np.arange(self.num_cakes)
        self.velocities = np.linspace(2, 0.1, self.num_cakes)

        lam = (np.arange(self.num_cakes)/float(self.num_cakes))[:,None]

        self.pancakes_colors = (1-lam) * self.color + lam * self.pancake_color

    def visualize(self, sample_array):
            m = np.max(sample_array[-8:]) # get the maximum amplitude
            m = self.bounder.update_and_normalize(m) # normalize the amplitude to [0,1]
            m = self.smoother.smooth(m) # and smooth it

            new_pos = self.positions - self.velocities
            lower_bound = np.arange(self.num_cakes)
            level = int((LED_1_COUNT - self.num_cakes) * m)
            levels = level + np.arange(self.num_cakes)

            self.positions = np.max([new_pos, levels, lower_bound], axis=0)

            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on
            color_array = color_mask * self.color
            color_array[self.positions.astype(int),:] = self.pancakes_colors

            # create a color array to be sent to the LED_writer
            return color_array

class Stones(VisualizerBase):
    def __init__(self):
        VisualizerBase.__init__(self)
        self.stone_color = np.array([150, 50, 50])
        self.color = np.array([20, 20, 30])

        self.mask_maker = masker.bottom_up
        self.smoother = ExponentialMovingAverage(0.4)
        self.bounder = Bounder()

        self.num_stones = 5
        self.positions = np.ones(self.num_stones)
        self.velocities = np.zeros(self.num_stones)
        self.accelerations = np.linspace(0.2, 0.8, self.num_stones)

        self.prev_t = time.time()
        self.prev_m = 0

    def visualize(self, sample_array):
            # update the time
            t = time.time()
            dt = t - self.prev_t
            self.prev_t = t
            sample_array = np.log(sample_array+1)
            m = np.max(sample_array[-8:]) # get the maximum amplitude
            m = self.bounder.update_and_normalize(m) # normalize the amplitude to [0,1]
            m = self.smoother.smooth(m) # and smooth it
            m = (10**m - 1)/20.

            dm = m - self.prev_m
            self.prev_m = m

            new_vel = self.velocities - self.accelerations * dt # update the velocity
            new_vel[(0 > self.positions)] = 0 # set to zero at the bottom
            new_vel[(1 <= self.positions)] = -1e-3 # set to zero at the top
            new_vel[(m > self.positions)] = max(0,dm/dt) * 0.3
            self.velocities = new_vel

            new_pos = self.positions + self.velocities * dt
            self.positions = np.max([np.zeros(self.num_stones), m * np.ones(self.num_stones)+1e-3, new_pos], axis=0)
            self.positions = np.min([np.ones(self.num_stones), self.positions], axis=0)


            color_mask = self.mask_maker(m) # create a mask of which LEDS to turn on
            color_array = color_mask * self.color
            color_array[((LED_1_COUNT - 1) * self.positions).astype(int),:] = self.stone_color

            # create a color array to be sent to the LED_writer
            return color_array


# this is the list of visualizers to be used by run.py and the web page
vis_list = [StripsOff,
            VooMeter,
            FFTGauss,
            FFTGaussBeads,
            BlobSlider,
            Zoom,
            Sparkle,
            Retro,
            Pancakes,
            SamMode,
            Stones]

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

