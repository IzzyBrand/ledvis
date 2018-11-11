import zmq
import random
import sys
import time
import numpy as np


port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

while True:
    msg = socket.recv()
    print(msg)