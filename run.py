from multiprocessing import Process, Array
import Adafruit_ADS1x15
import numpy as np
import time
import masker
from neopixel import *
from config import *
from smoother import *
from visualizer import *


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


def visualizer(sample_array, led_array, settings_array):
    '''
    Create an array of colors to be displayed on the LED strips given an array of audio samples
    '''

    voos = [BlobSlider(), FFTGauss(), VooMeter()]
    voo_index = 0

    while True:
        
        if settings_array.acquire():
            voo_index = settings_array[0]
            settings_array.release()

        voo = voos[voo_index]

        # get the newest sample array
        sample_array.acquire()
        a = np.array(sample_array)
        sample_array.release()

        # unwrap the circular buffer
        a_start = (a[-1] + 1) % (a.size - 1)
        a = np.concatenate([a[a_start:-1], a[:a_start]])

        color_array = voo.visualize(a) # create a linear color array to be sent to the LED_writer

        # send the color array to the LED_writer
        led_array.acquire()
        led_array[:] = color_array
        led_array.release()


def settings_getter(settings_array):
    while True:
        # do a get request to the server
        url = 'localhost:5000/get_settings'
        data = requests.get(url).json()
        settings_array.acquire()
        settings_array[0] = data['voo_index']
        settings_array.release()
        pass

if __name__ == '__main__':
    led_array = Array('i', np.zeros(LED_1_COUNT * 3, dtype=int))
    sample_array = Array('i', np.zeros(SAMPLE_ARRAY_SIZE + 1, dtype=int))
    settings_array = Array('i', np.zeros(1), dtype=int)

    sampler_process    = Process(target=sampler,    name='Sampler',    args=(sample_array,))
    led_writer_process = Process(target=led_writer, name='LED Writer', args=(led_array,))
    visualizer_process = Process(target=visualizer, name='Visualizer', args=(sample_array, led_array, settings_array))
    settings_process   = Process(target=visualizer, name='Settings Getter', args=(settings_array))

    processes = [sampler_process, led_writer_process, visualizer_process, settings_getter]

    for p in processes: p.start()

    for p in processes:
        print("Started {} on PID {}".format(p.name, p.pid))

    for p in processes: p.join()