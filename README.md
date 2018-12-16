# ledvis
Raspberry Pi LED music visualizer. Use `screen -c pi.screenrc` to run.

`sudo` is needed because this we are interfacing with the GPIO and PWM through the rpi_ws281x library.

## Requirments

This is meant to run on a Raspberry Pi. I used a Model 3 B+.

 * rpi_ws281x
 * adafruit-ads1x15
 * screen
 * Flask

Run this to install the rpi_ws281x (LED) driver library
```
cd ~
git clone https://github.com/jgarff/rpi_ws281x.git
sudo apt install scons swig
cd rpi_ws281x
scons
cd python
sudo -H python setup.py build
sudo -H python setup.py install
```

And run this to install the other dependencies
```
pip install adafruit-ads1x15	# install the ADS1015 i2c library
pip3 install Flask				# get Flask (best to use python3)
sudo apt install screen 		# get screen
```

## Repo Organization

 * **run.py** contains execture three processes: one to sample the ADC, one to process the data, and one to write to the LEDs
 * **visualizer.py** contains classes the define how to process a sample array into color values to be displayed
 * **sound_processing.py** contains functions for normalizing and smoothing the incoming audio signal
 * **masker.py** contains functions for create a color mask given an amplitude (used in `VooMeter` in `visualizer.py`)
 * **config.py** does what is sounds like it does

## To get it to run automatically on the Pi

Install screen by `sudo apt install screen`. dd the following to `/etc/rc.local` right above the `exit 0` line

```
su - pi -c "screen -dm -S ledvis -c /home/pi/ledvis/pi.screenrc"
```
