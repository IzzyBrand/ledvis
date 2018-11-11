from multiprocessing import Process, Queue
import queue
import Adafruit_ADS1x15
import time

def sample(q):
    adc = Adafruit_ADS1x15.ADS1015()
    GAIN = 8
    adc.start_adc(0,gain=GAIN) # start continous sampling on pin 0
    while True:
        val = adc.get_last_result()
        print("Sending {}".format(val))
        q.put(val)

if __name__ == '__main__':
    q = Queue()
    s = Process(target=sample, args=(q,))
    s.start()

    start_time = time.time()
    while time.time() - start_time < 10:
        try:
            print("Recv {}".format(q.get(False)))
        except queue.Empty:
            print("Nothing to get")

    s.join()