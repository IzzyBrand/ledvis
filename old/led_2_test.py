import time
from neopixel import *
from config import *


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=5.0):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


if __name__ == "__main__":
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL)
	# Intialize the library (must be called once before other functions).
	strip.begin()
	colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
	while True:
		for color in colors:
			colorWipe(strip, color, wait_ms=5.0)