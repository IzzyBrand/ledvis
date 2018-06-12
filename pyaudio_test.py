import pyaudio
import numpy as np
from matplotlib import pyplot as plt
from config import *

RECORD_SECONDS = 5

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
	info = p.get_device_info_by_index(i)
	print info['index'], info['name']

stream = p.open(input_device_index=DEVICE_INDEX,
				format=FORMAT,
                channels=NUM_CHANNELS,
                rate=SAMPLING_FREQ,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

frames = []
print("* recording {} seconds on {}".format(RECORD_SECONDS, 
	p.get_device_info_by_index(DEVICE_INDEX)['name']))
for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
    frames.append(stream.read(CHUNK_SIZE))
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

string_data = b''.join(frames)
int_data = np.fromstring(string_data, dtype="int16")
l_data, r_data = int_data.reshape((-1,2)).T
plt.plot(l_data)
plt.plot(r_data)
plt.show()
