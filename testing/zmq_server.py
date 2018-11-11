import zmq
import random
import sys
import time
import Adafruit_ADS1x15
import numpy as np

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

adc = Adafruit_ADS1x15.ADS1015()
GAIN = 8
adc.start_adc(0,gain=GAIN) # start continous sampling on pin 0


while True:
    start = time.time()
    val = adc.get_last_result()
    read_time = time.time() - start

    last = time.time()
    socket.send_string(str(val))
    send_time = time.time() - last

    print("Val {}\tFreq {}\tRead {}\tSend {}".format(val, 1/(time.time() -start),read_time, send_time))