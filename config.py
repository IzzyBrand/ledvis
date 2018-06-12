import pyaudio

# PYAUDIO CONFIGURATION
CHUNK_SIZE 		= 441
FORMAT 			= pyaudio.paInt16
NUM_CHANNELS 	= 2
SAMPLING_FREQ	= 44100
DEVICE_INDEX 	= 2

# LED CONFIGURATION
LED_COUNT      = 20      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53




