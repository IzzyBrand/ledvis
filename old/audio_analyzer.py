import numpy as np
import pyaudio
import socket
import time
from config import *

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


def get_message_for_sample(sample):
    vols = np.log(np.abs(np.mean(sample.reshape((-1,2)).T,axis=1))+1)
    l_vol, r_vol = np.clip(vols*1,0,LED_COUNT).astype(np.uint8)
    freq = 0
    return "{},{},{}".format(l_vol, r_vol, freq)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    p = pyaudio.PyAudio()
    stream = p.open(input_device_index=DEVICE_INDEX,
                    format=FORMAT,
                    channels=NUM_CHANNELS,
                    rate=SAMPLING_FREQ,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)


    prev_message = ""
    print("* recording")
    try:
        while True:
            string_data = stream.read(CHUNK_SIZE)
            int_data = np.fromstring(string_data, dtype="int16")
            message = get_message_for_sample(int_data)
            if message != prev_message:
                print(message)
                sent = sock.sendto(message, (SERVER_ADDRESS, SERVER_PORT))
                prev_message = message

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("* done recording")
        sock.close()


if __name__ == '__main__':
    main()