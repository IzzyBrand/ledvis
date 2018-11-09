import time
from neopixel import *
from config import *
import Adafruit_ADS1x15

GAIN = 8
NUM_SAMPLES = 5
MAX_DROP = 1
VOO_DROP = 30
assert(LED_1_COUNT == LED_2_COUNT)

# Create an ADC object
adc = Adafruit_ADS1x15.ADS1015()
adc.start_adc(0, gain=GAIN)
# Create NeoPixel object with appropriate configuration.
strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL)
strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL)

# Intialize the library (must be called once before other functions).
strip1.begin()
strip2.begin()


off = Color(0,0,0)

val = 0
max_val = 0
while True:
    for i in range(NUM_SAMPLES):
        val = max(val, abs(adc.get_last_result()))

    max_val = max(max_val, val)


    num_leds_on = LED_1_COUNT/2 * val/max_val
    for i in range(LED_1_COUNT):
        strip1.setPixelColor(i, Color(80, val/5, max_val/8) if abs(i - LED_1_COUNT/2) < num_leds_on else off)
        strip2.setPixelColor(i, Color(80, val/5, max_val/8) if abs(i - LED_1_COUNT/2) < num_leds_on else off)

    strip1.show()
    time.sleep(0.005)
    strip2.show()
    time.sleep(0.005)

    val -= VOO_DROP
    max_val -= MAX_DROP

