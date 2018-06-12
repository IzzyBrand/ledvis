import pyaudio
import wave
import numpy as np
from matplotlib import pyplot as plt

CHUNK_SIZE = 441
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

frames = []
print("* recording")
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
plt.show()
