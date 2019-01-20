from multiprocessing import Process, Array
import pyaudio
import numpy as np
import time
import requests
from config import *
from visualizer import vis_list
from strips import Strips
from util import FrequencyPrinter


def sampler(sample_array):
    '''
    Sample the ADC as in continous mode and write into the shared array as a circular buffer.
    The index that has been most recently written is stored in the last slot in the array
    '''

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format=FORMAT, rate=SAMPLING_FREQ, channels=NUM_CHANNELS, \
                        input_device_index=DEVICE_INDEX, input=True, \
                        frames_per_buffer=CHUNK_SIZE)
    sample_index = 0

    fp = FrequencyPrinter('Sampler')
    while True:
        if PRINT_LOOP_FREQUENCY: fp.tick()

        try:
            data = stream.read(CHUNK_SIZE)
        except IOError:
            print 'Stream overflow!'
            stream.close()
            stream = audio.open(format=FORMAT, rate=SAMPLING_FREQ, channels=NUM_CHANNELS, \
                        input_device_index=DEVICE_INDEX, input=True, \
                        frames_per_buffer=CHUNK_SIZE)
        int_data = np.fromstring(data, dtype="int16")
        # print stream.get_read_available()

        # attempts a non-blocking write to the sample array
        if sample_array.acquire(False):
            sample_array[sample_index:sample_index + CHUNK_SIZE] = int_data # write the newest sample to the array
            sample_array[-1] = sample_index # store the most recent index last in the array
            sample_array.release()

            sample_index += CHUNK_SIZE
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
    vis_index = -1
    new_vis_index = 0

    fp = FrequencyPrinter('Visualizer')
    while True:
        if PRINT_LOOP_FREQUENCY: fp.tick()

        # get the current selected mode
        if settings_array.acquire():
            new_vis_index = settings_array[0]
            settings_array.release()

        # if the selected mode has changed, instantiate the new visualizer
        if vis_index != new_vis_index:
            vis_index = new_vis_index
            vis = vis_list[vis_index]()
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
    fp = FrequencyPrinter('Settings Getter')
    while True:
        if PRINT_LOOP_FREQUENCY: fp.tick()

        # do a get request to the server
        url = 'http://ledvis.local:5000/get_settings'

        try:
            response = requests.get(url)
        except requests.ConnectionError:
            print('Request failed.')
            continue

        if response.ok:
            data = response.json()
            vis_index = int(data['vis_index'])
            settings_array.acquire()
            settings_array[0] = vis_index
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
    