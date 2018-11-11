from multiprocessing import Process, Queue, Array
import Queue as queue
import Adafruit_ADS1x15
import numpy as np
import time
from neopixel import *
from config import *


def sampler(q):
    adc = Adafruit_ADS1x15.ADS1015()
    GAIN = 4
    adc.start_adc(0,gain=GAIN) # start continous sampling on pin 0
    while True:
        val = adc.get_last_result()
        try:
            q.put(val, False)
        except queue.Full:
            pass


def leds(a):
    # Create NeoPixel object with appropriate configuration.
    strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL)
    strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL)

    # Intialize the library (must be called once before other functions).
    strip1.begin()
    strip2.begin()

    while True:
        start_time = time.time()

        a.acquire()
        np_a = np.array(a)
        a.release()

        for i, c in enumerate(np_a.reshape(3, -1).T):
            strip1.setPixelColor(i, Color(*c))
            strip2.setPixelColor(i, Color(*c))

        # write to the LED strips
        # we require a sleep after each each write for the strips to update
        sleep_time = LED_WRITE_DELAY - (time.time() - start_time)
        if sleep_time > 0: time.sleep(sleep_time)
        strip1.show()
        time.sleep(LED_WRITE_DELAY)
        strip2.show()


if __name__ == '__main__':


    q = Queue(5)
    a = Array('i', np.zeros([LED_1_COUNT * 3], dtype=int))

    sampler_process = Process(target=sampler, args=(q,))
    leds_process = Process(target=leds, args=(a,))

    # sampler_process.start()
    leds_process.start()

    start_time = time.time()

    max_max = 0

    offset = 0
    while True:
        offset += 1
        offset = offset % LED_1_COUNT

        # num_samples = 0
        # max_sample = 0
        # while num_samples < 5:
        #     try:
        #         max_sample = max(max_sample, abs(q.get(False)))
        #         num_samples += 1
        #     except queue.Empty:
        #         print("Queue Empty!")

        # max_max = max(max_max, max_sample)

        # led_array = (np.arange(LED_1_COUNT * 3) < float(max_sample)/max_max * LED_1_COUNT * 3) * 80

        pi_range = (np.arange(LED_1_COUNT, dtype=float) + offset)/float(LED_1_COUNT)* np.pi *2.0

        cut = int(LED_1_COUNT / 3)
        r = (np.sin(pi_range) + 1.0) * 100.
        g = np.concatenate([r[cut:],r[:cut]])
        b = np.concatenate([r[2*cut:],r[:2*cut]])

        led_array = np.concatenate([g,r,b])
        a.acquire()
        a[:] = led_array.astype(int)
        a.release()
        time.sleep(0.004)


    sampler_process.join()
    leds_1_process.join()
    leds_2_process.join()