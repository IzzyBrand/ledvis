# ledvis
Raspberry Pi LED music visualizer

## Requirments

 * pyzmq
 * rpi_ws281x
 * adafruit-ads1x15

I followed [this tutorial to install pyzmq on the Pi](https://github.com/MonsieurV/ZeroMQ-RPi). Took about 15 mins to compile everything.

Run this to install the rpi_ws281x (LED) driver library
```
cd ~
git clone https://github.com/jgarff/rpi_ws281x.git
sudo apt install scons
cd rpi_ws281x
scons
cd python
python setup.py build
python setup.py install
```

And run this to install the ADS1015 (ADC) i2c library
```
pip install adafruit-ads1x15
```