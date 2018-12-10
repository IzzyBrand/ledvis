import time
from neopixel import *
from config import *

# Create NeoPixel object with appropriate configuration.
strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL)
strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL)

# Intialize the library (must be called once before other functions).
strip1.begin()
strip2.begin()

off = Color(0,0,0)

for i in range(LED_1_COUNT): strip1.setPixelColor(i, off)
for i in range(LED_2_COUNT): strip2.setPixelColor(i, off)

strip1.show()
time.sleep(0.005)
strip2.show()
time.sleep(0.005)

