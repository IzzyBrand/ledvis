import pyaudio
import time
import numpy as np
from matplotlib import pyplot as plt
from config import *

RECORD_SECONDS = 10
freqs = np.fft.fftfreq(CHUNK_SIZE)*float(SAMPLING_FREQ)

def get_freq_for_sample(sample):
    return np.abs(freqs[np.argmax(np.abs(np.fft.fft(sample)))])

def get_val_for_freq(freq):
    min_freq = 100
    max_freq = 4000
    n_steps  = 10
    log_min_freq = np.log(min_freq)
    log_max_freq = np.log(max_freq)
    return int((np.log(np.clip(freq, min_freq, max_freq)) - log_min_freq)/log_max_freq * n_steps)

def get_val_for_sample(sample):
    return get_val_for_freq(get_freq_for_sample(sample))


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
    vals = []
    print("* recording")
    for i in range(0, int(SAMPLING_FREQ / CHUNK_SIZE * RECORD_SECONDS)):
        start = time.time()
        string_data = stream.read(CHUNK_SIZE)
        print time.time() - start, '\t',
        int_data = np.fromstring(string_data, dtype="int16")
        l_data, r_data = int_data.reshape((-1,2)).T
        # ffts.append(np.abs(freqs[np.argmax(np.abs(np.fft.fft(l_data)))]))
        # vols.append(np.mean(np.abs(l_data)))
        vals.append(get_val_for_sample(l_data))
        print time.time() - start
        
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # plt.semilogy(ffts, label="FFT")
    # plt.plot(vols, label="Vol")
    plt.plot(vals, label="Val")
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