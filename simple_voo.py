import time
from neopixel import *
from config import *
import Adafruit_ADS1x15

GAIN = 8
NUM_SAMPLES = 5

# Create an ADC object
adc = Adafruit_ADS1x15.ADS1015()
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

color = Color(50, 100, 200)
off = Color(0,0,0)

max_val = 0
while True:
    abs_val = 0
    for i in range(NUM_SAMPLES):
        abs_val += abs(adc.read_adc_difference(0, gain=GAIN))
    abs_val = abs_val/NUM_SAMPLES

    max_val = max(max_val, abs_val)

    num_leds_on = LED_COUNT * abs_val/max_val

    for i in range(LED_COUNT):
        strip.setPixelColor(i, color if i < num_leds_on else off)

    strip.show()

