import pyaudio
import wave
import numpy as np
import time
from config import *
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)



record_secs = 3 # seconds to record
wav_output_filename = 'test1.wav' # name of .wav file

with noalsaerr():
    audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format=FORMAT, rate=SAMPLING_FREQ, channels=NUM_CHANNELS, \
                    input_device_index=DEVICE_INDEX, input=True, \
                    frames_per_buffer=CHUNK_SIZE)
print("recording")
frames = []

# loop through stream and append audio chunks to frame array
t = time.time()
count = 0
for ii in range(0,int((SAMPLING_FREQ/CHUNK_SIZE)*record_secs)):
    data = stream.read(CHUNK_SIZE)
    int_data = np.fromstring(data, dtype="int16")
    # frames.append(data)
    count += 1

print(1./((time.time() - t)/count))

print("finished recording")

# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()
