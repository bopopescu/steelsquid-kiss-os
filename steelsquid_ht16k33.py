#!/usr/bin/python -OO


'''
Controll the I2C 8X8 LED Matrix HT16K33 
https://www.adafruit.com/product/870

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-11-09 Created
'''


import steelsquid_i2c
import sys
import steelsquid_utils

DISPLAY_ADDRESS=0x80
BRIGHTNESS_ADDRESS=0xE0
OSCILLATOR=0x21
ROW_ADDRESS = [0x00, 0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0E]
COLUMN_VALUES = [0x80, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40]

empty = [[ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0],
         [ 0,0,0,0,0,0,0,0]]


address_setup = []

def _setup(address=0x70, brightness=15):
    '''
    Setup the LED matrix
    brightness: 0 to 15
    '''
    # Clear
    clear()
    # OSCILLATOR
    steelsquid_i2c.write_8_bit_raw(address, OSCILLATOR)
    # Display
    blink_rate = int(0) % 0x04
    on = int(True) % 0x02
    steelsquid_i2c.write_8_bit_raw(address, DISPLAY_ADDRESS | (blink_rate << 0x01) | on )
    # Brightness
    brightness = int(brightness) % 0x10
    steelsquid_i2c.write_8_bit_raw(address, BRIGHTNESS_ADDRESS | brightness )


def clear(address=0x70):
    '''
    Clear all leds
    '''
    for i in range(0x10):
        steelsquid_i2c.write_8_bit(address, i, 0x00)    

def get_matrix():
    '''
    Get matrix to use in paint
    '''
    return [[0 for x in range(8)] for y in range(8)] 


def paint_flash(matrix, rotate=0, address=0x70, seconds=1):
    '''
    Light a pattern
    matrix= two dimensinal array 8*8  [ROW, COLUMN]
    rotate: rotate the array clockwise this number of times
    '''
    steelsquid_utils.execute_flash("paint_flash", None, seconds, paint, (matrix, rotate, address,), paint, (empty, rotate, address,))
    

def paint(matrix, rotate=0, address=0x70):
    '''
    Light a pattern
    matrix= two dimensinal array 8*8  [ROW, COLUMN]
    rotate: rotate the array clockwise this number of times
    '''
    if address not in address_setup:
        _setup(address)
        address_setup.append(address)
    else:
        clear(address)
    for i in range(rotate):
        matrix = zip(*matrix[::-1])
    i_row=0
    i_col=0
    value = 0
    for row in matrix:
        for cel in row:
            if cel:
                value |= COLUMN_VALUES[i_col]
            i_col = i_col + 1
        i_col=0
        steelsquid_i2c.write_8_bit(address, ROW_ADDRESS[i_row], value)
        value = 0
        i_row = i_row + 1



if __name__ == "__main__":
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        print("")
        printb("lmatrix test")
        print("Write a test")
        print("")
    else:
        if sys.argv[1]=='test':
            matrix = [[ 0,1,1,1,1,1,1,0],
                      [ 1,0,0,0,0,0,0,1],
                      [ 1,0,1,0,0,1,0,1],
                      [ 1,0,0,0,0,0,0,1],
                      [ 1,0,1,0,0,1,0,1],
                      [ 1,0,0,1,1,0,0,1],
                      [ 1,0,0,0,0,0,0,1],
                      [ 0,1,1,1,1,1,1,0]]
            paint(matrix, rotate=3)
            
