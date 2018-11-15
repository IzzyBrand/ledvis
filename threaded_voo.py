from multiprocessing import Process, Array
import Adafruit_ADS1x15
import numpy as np
import time
from neopixel import *
from config import *
from smoother import *

SAMPLE_ARRAY_SIZE = 50
SAMPLE_FREQUENCY = 3000

def sampler(sample_array):
    '''
    Sample the ADC as in continous mode and write into the shared array as a circular buffer.
    The index that has been most recently written is stored in the last slot in the array
    '''
    adc = Adafruit_ADS1x15.ADS1015() # instantiate the ADC object
    adc.start_adc(ADC_CHANNEL, gain=ADC_GAIN) # start continous sampling

    sample_index = 0
    while True:
        # TODO(izzy): get the upper and lower bounds on the ADC so we can
        # handle negative numbers properly and not crop the sample range
        val = abs(adc.get_last_result()) # sample the ADC

        # attempts a non-blocking write to the sample array
        if sample_array.acquire(False):
            sample_array[sample_index] = val # write the newest sample to the array
            sample_array[-1] = sample_index # store the most recent index last in the array
            sample_array.release()

            sample_index += 1
            sample_index = sample_index % SAMPLE_ARRAY_SIZE
        # else:
        #     print("We dropped a sample")


def led_writer(led_array):
    '''
    Write to the LED strips as fast as possible, publishing the newest value from the led_array.
    The led_array is the individual colors for each for each of the pixels concatenated
    '''
    # Create NeoPixel object with appropriate configuration.
    strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL)
    strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip1.begin()
    strip2.begin()

    while True:
        start_time = time.time()

        led_array.acquire()
        np_a = np.array(led_array)
        led_array.release()

        # convert the led_array to a list of colors
        colors = [Color(*c) for c in np_a.reshape(-1,3)]
        # and set the LED strips to those colors
        for i, c in enumerate(colors):
            strip1.setPixelColor(i, c)
            strip2.setPixelColor(i, c)

        # write to the LED strips (with GPIO)
        # we require a sleep after each each write for the strips to finish updating
        sleep_time = LED_WRITE_DELAY - (time.time() - start_time)
        if sleep_time > 0: time.sleep(sleep_time)
        strip1.show()
        time.sleep(LED_WRITE_DELAY)
        strip2.show()


def unloop(a):
    a_start = (a[-1] + 1) % (a.size - 1)
    return np.concatenate([a[a_start:-1], a[:a_start]])

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

def visualizer(sample_array, led_array):
    max_amplitude = 0
    min_amplitude = 0
    max_amplitude_contraction_rate = 0.01
    min_amplitude_contraction_rate = 0.01
    voo_smoother = ExponentialMovingAverageSpikePassSmoother(0.1)

    while True:
        sample_array.acquire()
        a = np.array(sample_array)
        sample_array.release()

        a = unloop(a) # unwrap the circular buffer
        f = get_max_freq(a) # get the maximum frequency
        m = np.max(a[-10:]) # and the maximum amplitude

        # update the max and min bounds on the amplitude
        max_amplitude -= max_amplitude_contraction_rate
        max_amplitude = max(max_amplitude, m)
        min_amplitude += min_amplitude_contraction_rate
        min_amplitude = min(min_amplitude, max_amplitude - 1) # make sure the min doesn't exceed the max
        min_amplitude = min(min_amplitude, np.min(a))

        m = float(m - min_amplitude)/float(max_amplitude-min_amplitude) # normalize the amplitude to [0,1]
        m = voo_smoother(m) # and smooth it

        num_leds_on = m * LED_1_COUNT # create a mask of which LEDS to turn on
        color_mask = np.tile(np.arange(LED_1_COUNT) < num_leds_on, (3,1)).T

        # freq_color = sample_color(f)
        freq_color = [100, 150, 200]

        # create a linear color array to be sent to the LED_writer
        color_array = np.ravel(color_mask * freq_color).astype(int)

        # send the color array to the LED_writer
        led_array.acquire()
        led_array[:] = color_array
        led_array.release()


if __name__ == '__main__':
    led_array = Array('i', np.zeros(LED_1_COUNT * 3, dtype=int))
    sample_array = Array('i', np.zeros(SAMPLE_ARRAY_SIZE + 1, dtype=int))

    sampler_process    = Process(target=sampler,    name='Sampler',    args=(sample_array,))
    led_writer_process = Process(target=led_writer, name='LED Writer', args=(led_array,))
    visualizer_process = Process(target=visualizer, name='Visualizer', args=(sample_array, led_array))

    processes = [sampler_process, led_writer_process, visualizer_process]

    for p in processes: p.start()

    for p in processes:
        print("Started {} on PID {}".format(p.name, p.pid))

    for p in processes: p.join()