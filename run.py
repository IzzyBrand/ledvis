from multiprocessing import Process, Array
import Adafruit_ADS1x15
import numpy as np
import time
import requests
from config import *
from visualizer import vis_list
from strips import Strips


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

    # here I was saving some sample data for testing offline
    # a = np.array(samples)
    # print 'Saving', a.shape, 'samples'
    # np.save("sample_30s_3.txt", np.array(samples), allow_pickle=True)


def visualizer(sample_array, settings_array):
    '''
    Create an array of colors to be displayed on the LED strips given an array of audio samples
    '''

    strips = Strips()
    voo_index = -1
    new_voo_index = 0

    while True:
        # get the current selected mode
        if settings_array.acquire():
            new_voo_index = settings_array[0]
            settings_array.release()

        # if the selected mode has changed, instantiate the new visualizer
        if voo_index != new_voo_index:
            voo_index = new_voo_index
            vis = vis_list[voo_index]()
            print('Mode changed to {}'.format(vis.name))

        # get the newest sample array
        sample_array.acquire()
        a = np.array(sample_array)
        sample_array.release()

        # unwrap the circular buffer
        a_start = (a[-1] + 1) % (a.size - 1)
        a = np.concatenate([a[a_start:-1], a[:a_start]])

        # create a color array
        color_array = vis.visualize(a)

        # send the color array to the strips
        strips.write(color_array)


def settings_getter(settings_array):
    '''
    Make get requests to the server to get the most recent user input
    '''
    while True:
        # do a get request to the server
        url = 'http://ledvis.local:5000/get_settings'

        try:
            response = requests.get(url)
        except requests.ConnectionError:
            print('Request failed.')
            continue

        if response.ok:
            data = response.json()
            voo_index = int(data['voo_index'])
            settings_array.acquire()
            settings_array[0] = voo_index
            settings_array.release()
        else:
            print('Status Code {}'.format(response.status_code))

        time.sleep(0.1)


if __name__ == '__main__':
    sample_array    = Array('i', np.zeros(SAMPLE_ARRAY_SIZE + 1, dtype=int))
    settings_array  = Array('i', np.zeros(1, dtype=int))

    sampler_process    = Process(target=sampler,         name='Sampler',         args=(sample_array,))
    visualizer_process = Process(target=visualizer,      name='Visualizer',      args=(sample_array, settings_array))
    settings_process   = Process(target=settings_getter, name='Settings Getter', args=(settings_array,))

    processes = [sampler_process,  visualizer_process, settings_process]

    for p in processes: p.start()
    for p in processes: print("Started {} on PID {}".format(p.name, p.pid))
    for p in processes: p.join()
    