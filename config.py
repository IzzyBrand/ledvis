import numpy as np

# PYAUDIO CONFIGURATION
CHUNK_SIZE 		=  2**8	 # How many audio samples to read in per step
FORMAT 			= 8
NUM_CHANNELS 	= 1	      # Number of audio channels
SAMPLING_FREQ	= 48000  # Sampling frequency of incoming audio
DEVICE_INDEX 	= 2      # Which audio device to read from (listed in pyaudio_test.py)

# RUN CONFIGURATION
PRINT_LOOP_FREQUENCY = True
SAMPLE_ARRAY_SIZE = 4 * CHUNK_SIZE
DEFAULT_REQUIRED_SAMPLES = SAMPLE_ARRAY_SIZE

# LED STRIPS CONFIGURATION
LED_1_COUNT      = 30     # Number of LED pixels.
LED_1_PIN        = 18      # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3).
LED_1_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_1_DMA        = 10      # DMA channel to use for generating signal (Between 1 and 14)
LED_1_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_1_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL    = 0       # 0 or 1

LED_2_COUNT      = 30     # Number of LED pixels.
LED_2_PIN        = 13      # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA        = 9      # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_2_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL    = 1       # 0 or 1

LED_WRITE_DELAY  = 0.005   # wait (in seconds) after writing to each LED strip

# ADC CONFIGURATION
ADC_GAIN = 4
ADC_CHANNEL = 0
ADC_MIN = -2048
ADC_MAX = 2048

# SERVER CONFIGURATION
SERVER_ADDRESS = 'pi-visualizer'
SERVER_PORT    = 5000

