import numpy as np
import socket
import sys
from config import *
from neopixel import *



def message_to_color_array(msg):
    try:
        v_left, v_right, freq = [int(x) for x in msg.split(',')]
    except Exception as e:
        print(e)
        return None

    left_on  = np.arange(LED_COUNT-1, -1, -1) < v_left
    right_on = np.arange(LED_COUNT) < v_right
    on = np.append(left_on, right_on)
    return np.vstack([np.zeros(LED_COUNT*2), np.zeros(LED_COUNT*2), on]).T.astype(np.int8)*100

def write_pixels(strip, color_array):
    for i, c in enumerate(color_array):
        r, g, b = c
        strip.setPixelColorRGB(i, r, g, b)
    strip.show()   


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT*NUM_CHANNELS, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = ('0.0.0.0', SERVER_PORT)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    data, address = sock.recvfrom(4096)
    print('Received {} from {}'.format(data, address))

    color_array = message_to_color_array(data)
    if color_array is None:
        print('Failed to parse {}'.format(data))
    else:
        write_pixels(strip, color_array)

