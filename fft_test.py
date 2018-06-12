import pyaudio
import time
import numpy as np
from matplotlib import pyplot as plt
from config import *

RECORD_SECONDS = 5

def main():
    p = pyaudio.PyAudio()

    stream = p.open(input_device_index=DEVICE_INDEX,
                    format=FORMAT,
                    channels=NUM_CHANNELS,
                    rate=SAMPLING_FREQ,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    ffts = []
    vols = []
    print("* recording")
    for i in range(0, int(SAMPLING_FREQ / CHUNK_SIZE * RECORD_SECONDS)):
        start = time.time()
        string_data = stream.read(CHUNK_SIZE)
        print time.time() - start, '\t',
        int_data    = np.fromstring(string_data, dtype="int16")
        ffts.append(np.mean(np.abs(np.fft.fft(int_data)[:int(CHUNK_SIZE/2)])))
        vols.append(np.mean(np.abs(int_data)))
        print time.time() - start
        
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    plt.plot(ffts, label="FFT")
    plt.plot(vols, label="Vol")
    plt.legend()
    plt.show()
    # string_data = b''.join(frames)
    # int_data = np.fromstring(string_data, dtype="int16")
    # l_data, r_data = int_data.reshape((-1,2)).T
    # plt.plot(l_data)
    # plt.plot(r_data)
    # plt.show()

if __name__ == '__main__':
    main()