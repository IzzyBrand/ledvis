# PYAUDIO CONFIGURATION
CHUNK_SIZE 		= 882 	 # How many audio samples to read in per step
FORMAT 			= 8
NUM_CHANNELS 	= 2      # Number of audio channels
SAMPLING_FREQ	= 44100  # Sampling frequency of incoming audio
DEVICE_INDEX 	= 2      # Which audio device to read from (listed in pyaudio_test.py)

# LED CONFIGURATION
LED_COUNT      = 10      # Number of LED pixels per column
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# SERVER CONFIGURATION
SERVER_ADDRESS = 'izzypi.local'
SERVER_PORT    = 10000
