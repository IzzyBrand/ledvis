import socket
import sys
from config import *

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        message = raw_input()
        print('sending "{}"'.format(message))
        sent = sock.sendto(message, (SERVER_ADDRESS, SERVER_PORT))
finally:
    print('closing socket')
    sock.close()