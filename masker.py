import numpy as np
from config import *

def bottom_up(m):
    '''
    Creates a mask of which leds to turn on given an amplitude.
    This mask lights a strip of LEDs starting at the bottom and reaching higher
    with increasing amplitude

    Arguments:
        m (float): The amplitude in 0 to 1

    Returns:
        A [LED_1_COUNT x 3] array of zeros and ones
    '''
    num_leds_on = m * LED_1_COUNT
    return np.tile(np.arange(LED_1_COUNT) < num_leds_on, (3,1)).T

def bottom_upV(m):
    '''
    Creates a mask of which leds to turn on given an amplitude.
    This mask lights a strip of LEDs starting at the bottom and reaching higher
    with increasing amplitude

    Arguments:
        m (float): The amplitude in 0 to 1

    Returns:
        A [LED_1_COUNT] array of zeros and ones
    '''
    num_leds_on = m * LED_1_COUNT
    return np.tile(np.abs(np.arange(LED_1_COUNT/3)) < num_leds_on/3-0.01, (3,1)).T


def top_down(m):
    '''
    Creates a mask of which leds to turn on given an amplitude.
    This mask lights a strip of LEDs starting at the top and reaching lower
    with increasing amplitude

    Arguments:
        m (float): The amplitude in 0 to 1

    Returns:
        A [LED_1_COUNT x 3] array of zeros and ones
    '''
    num_leds_on = m * LED_1_COUNT
    return np.tile(LED_1_COUNT - np.arange(LED_1_COUNT) < num_leds_on, (3,1)).T

def middle_out(m):
    '''
    Creates a mask of which leds to turn on given an amplitude.
    This mask lights a strip of LEDs starting at the middle and reaching out
    with increasing amplitude

    Arguments:
        m (float): The amplitude in 0 to 1

    Returns:
        A [LED_1_COUNT x 3] array of zeros and ones
    '''
    num_leds_on = m * LED_1_COUNT
    return np.tile(np.abs(LED_1_COUNT/2.0 - np.arange(LED_1_COUNT)) < num_leds_on/2., (3,1)).T

def clamp(m):
    '''
    Creates a mask of which leds to turn on given an amplitude.
    This mask lights a strip of LEDs starting at the top and bottom and reaching towards
    the middle with increasing amplitude

    Arguments:
        m (float): The amplitude in 0 to 1

    Returns:
        A [LED_1_COUNT x 3] array of zeros and ones
    '''
    num_leds_on = (1. - m) * LED_1_COUNT
    return 1 - np.tile(np.abs(LED_1_COUNT/2.0 - np.arange(LED_1_COUNT)) < num_leds_on/2., (3,1)).T