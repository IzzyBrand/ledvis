import time
import Adafruit_ADS1x15
from sys import stdout

# Or create an ADS1015 ADC (12-bit) instance.
adc = Adafruit_ADS1x15.ADS1015()

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 8
# adc.start_adc(0,gain=GAIN) # start continous sampling on pin 0

print('Reading ADS1x15 values, press Ctrl-C to quit...')
# Main loop
full = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
blank = "                                           "
while True:
    start = time.time()
    val = adc.read_adc_difference(0, gain=GAIN) # comparison of pins 0 and 1
    # val = adc.read_adc(0, gain=GAIN) # individual read
    # val = adc.get_last_result() # continuous mode
    
    
    print "Freq {}\tVal {}".format(1/(time.time() -start), val)
    
    count = abs(int(val/10))
    out = '\r' + full[:count] + blank[count:]
    #stdout.write(out)
