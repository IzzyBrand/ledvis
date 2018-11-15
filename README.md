# ledvis
Raspberry Pi LED music visualizer. Use `sudo python run.py` to run.

`sudo` is needed because this we are interfacing with the GPIO and PWM through the rpi_ws281x library.

## Requirments

This is meant to run on a Raspberry Pi. I used a Model 3 B+.

 * rpi_ws281x
 * adafruit-ads1x15

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

## Repo Organization

 * **run.py** contains execture three processes: one to sample the ADC, one to process the data, and one to write to the LEDs
 * **visualizer.py** contains classes the define how to process a sample array into color values to be displayed
 * **smoother.py** contains functions for smoothing the incoming audio signal
 * **masker.py** contains functions for create a color mask given an amplitude (used in `VooMeter` in `visualizer.py`)
 * **config.py** does what is sounds like it does
 * **strips_off.py** turns off the LED strips. Run it with `sudo python strips_off.py`

