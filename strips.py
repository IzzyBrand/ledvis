from neopixel import *
from config import *
import numpy as np
import time


class Strips:
    def __init__(self):
        self.strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL)
        self.strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL) # IZZY: strip2 disabled
        self.strip1.begin()
        self.strip2.begin() # IZZY: strip2 disabled

        self.prev_write_time = time.time()

    def set_brightness(self, brightness):
        self.strip1.setBrightness(brightness)
        self.strip2.setBrightness(brightness) # IZZY: strip2 disabled

    def write(self, colors):
        # set the LED self.strips to those colors
        for i, c in enumerate(colors.astype(int)):
            color = Color(*c)
            self.strip1.setPixelColor(i, color)
            self.strip2.setPixelColor(i, color) # IZZY: strip2 disabled

        # we require a sleep after each each write for the strips to finish updating
        # make sure we've slept enough since the last write
        sleep_time = LED_WRITE_DELAY - (time.time() - self.prev_write_time)
        if sleep_time > 0: time.sleep(sleep_time)

        # write to the LED strips (with GPIO)
        self.strip1.show()

        time.sleep(LED_WRITE_DELAY) # IZZY: strip2 disabled
        self.strip2.show() # IZZY: strip2 disabled

        self.prev_write_time = time.time() # save for the next loop
