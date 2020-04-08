from multiprocessing import Process, Array
import pyaudio
import numpy as np
import time
import requests
from config import *
from visualizer import vis_list
from strips import Strips
from util import FrequencyPrinter, CircularBuffer


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

    fp = FrequencyPrinter('Sampler')
    while True:
        if PRINT_LOOP_FREQUENCY: fp.tick()

        try:
            data = stream.read(CHUNK_SIZE,False)
        except IOError as e:
            print(e)
            stream.close()
            stream = audio.open(format=FORMAT, rate=SAMPLING_FREQ, channels=NUM_CHANNELS, \
                        input_device_index=DEVICE_INDEX, input=True, \
                        frames_per_buffer=CHUNK_SIZE)
        int_data = np.fromstring(data, dtype="int16")
        # print stream.get_read_available()

        # attempts a non-blocking write to the sample array
        if sample_array.acquire(False):
            sample_start = sample_array[-1]
            sample_end = sample_start + CHUNK_SIZE

            if sample_end < SAMPLE_ARRAY_SIZE - 1:
                sample_array[sample_start:sample_end] = int_data # write the newest sample to the array
                sample_array[-1] = sample_end # store the most recent index last in the array
            # else:
            #     print 'dropped'

            sample_array.release()

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
            circ_buffer = CircularBuffer(vis.required_samples)
            print('Mode changed to {}'.format(vis.name))

        # get the newest sample array
        sample_array.acquire()
        a = np.array(sample_array[:sample_array[-1]])
        sample_array[-1] = 0 # indicate that you have read the sample
        sample_array.release()

        # add the array to the buffer
        circ_buffer.push(a)

        # run the visualizer on the contents of the buffer
        color_array = vis.visualize(circ_buffer.get())

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
        url = 'http://127.0.0.1:5000/get_settings'

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
    