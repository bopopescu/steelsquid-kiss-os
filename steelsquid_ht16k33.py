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
import time
import thread
import types

DISPLAY_ADDRESS=0x80
BRIGHTNESS_ADDRESS=0xE0
OSCILLATOR=0x21
ROW_ADDRESS = [0x00, 0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0E]
COLUMN_VALUES = [0x80, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40]

matrix_empty = [[ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,0,0,0,0,0]]

matrix_smile = [[ 0,0,0,0,0,0,0,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,1,1,0,0,0],
                [ 0,1,0,0,0,0,1,0],
                [ 0,0,1,1,1,1,0,0],
                [ 0,0,0,0,0,0,0,0]]
              
matrix_straight = [[ 0,0,0,0,0,0,0,0],
                   [ 0,1,1,0,0,1,1,0],
                   [ 0,1,1,0,0,1,1,0],
                   [ 0,0,0,0,0,0,0,0],
                   [ 0,0,0,1,1,0,0,0],
                   [ 0,0,0,0,0,0,0,0],
                   [ 0,1,1,1,1,1,1,0],
                   [ 0,0,0,0,0,0,0,0]]

matrix_sad = [[ 0,0,0,0,0,0,0,0],
              [ 0,1,1,0,0,1,1,0],
              [ 0,1,1,0,0,1,1,0],
              [ 0,0,0,0,0,0,0,0],
              [ 0,0,0,1,1,0,0,0],
              [ 0,0,0,0,0,0,0,0],
              [ 0,0,1,1,1,1,0,0],
              [ 0,1,0,0,0,0,1,0]]

matrix_angry = [[ 0,1,0,0,0,0,1,0],
                [ 0,0,1,0,0,1,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,1,1,1,1,0,0],
                [ 0,0,0,0,0,0,0,0]]

matrix_error = [[ 0,1,1,1,1,1,1,0],
                [ 1,0,0,0,0,0,0,1],
                [ 1,0,1,0,0,1,0,1],
                [ 1,0,0,1,1,0,0,1],
                [ 1,0,0,1,1,0,0,1],
                [ 1,0,1,0,0,1,0,1],
                [ 1,0,0,0,0,0,0,1],
                [ 0,1,1,1,1,1,1,0]]


matrix_type_1 = [[ 0,1,1,1,1,1,1,0],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 0,1,1,0,0,1,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,1,0,0,0,0],
                 [ 0,0,1,0,0,0,0,0]]

matrix_type_2 = [[ 0,1,1,1,1,1,1,0],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,1,0,0,0,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 0,1,1,0,0,1,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,1,0,0,0,0],
                 [ 0,0,1,0,0,0,0,0]]

matrix_type_3 = [[ 0,1,1,1,1,1,1,0],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,1,1,0,0,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 0,1,1,0,0,1,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,1,0,0,0,0],
                 [ 0,0,1,0,0,0,0,0]]

matrix_type_4 = [[ 0,1,1,1,1,1,1,0],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,1,1,1,0,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 0,1,1,0,0,1,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,1,0,0,0,0],
                 [ 0,0,1,0,0,0,0,0]]

matrix_type_5 = [[ 0,1,1,1,1,1,1,0],
                 [ 1,0,0,0,0,0,0,1],
                 [ 1,0,1,1,1,1,0,1],
                 [ 1,0,0,0,0,0,0,1],
                 [ 0,1,1,0,0,1,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,1,0,0,0,0],
                 [ 0,0,1,0,0,0,0,0]]

matrix_speak_1 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,1,1,1,1,0],
                  [ 0,0,0,0,0,0,0,0]]

matrix_speak_2 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,1,1,1,1,0],
                  [ 0,0,1,1,1,1,0,0]]

                  
matrix_heart_4 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 1,1,1,1,1,1,1,1],
                  [ 1,1,1,1,1,1,1,1],
                  [ 1,1,1,1,1,1,1,1],
                  [ 0,1,1,1,1,1,1,0],
                  [ 0,0,1,1,1,1,0,0],
                  [ 0,0,0,1,1,0,0,0]]                  

matrix_heart_3 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,1,1,1,1,1,1,0],
                  [ 0,1,1,1,1,1,1,0],
                  [ 0,0,1,1,1,1,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,0,0,0,0,0,0,0]]                  

matrix_heart_2 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,1,0,0,1,0,0],
                  [ 0,0,1,1,1,1,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0]]                  

matrix_heart_1 = [[ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,0,0,0,0,0]]                  

matrix_wave_3 = [[ 0,0,1,1,1,0,0,0],
                 [ 1,0,1,1,1,0,1,0],
                 [ 0,1,0,1,0,1,0,0],
                 [ 0,0,1,1,1,0,0,0],
                 [ 0,0,0,1,0,0,0,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,1,1,0,1,1,0,0]]                  

matrix_wave_2 = [[ 0,0,1,1,1,0,0,0],
                 [ 0,0,1,1,1,0,0,0],
                 [ 0,0,0,1,0,0,0,0],
                 [ 1,1,1,1,1,1,1,0],
                 [ 0,0,0,1,0,0,0,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,1,1,0,1,1,0,0]]                  

matrix_wave_1 = [[ 0,0,1,1,1,0,0,0],
                 [ 0,0,1,1,1,0,0,0],
                 [ 0,0,0,1,0,0,0,0],
                 [ 0,0,1,1,1,0,0,0],
                 [ 0,1,0,1,0,1,0,0],
                 [ 1,0,1,0,1,0,1,0],
                 [ 0,0,1,0,1,0,0,0],
                 [ 0,1,1,0,1,1,0,0]]                  

wait_1 = [[ 0,0,0,1,1,0,0,0],
          [ 0,0,0,1,1,0,0,0],
          [ 0,0,0,1,1,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]

wait_2 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,1,1,0],
          [ 0,0,0,0,1,1,1,0],
          [ 0,0,0,0,0,1,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]

wait_3 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,1,1,1],
          [ 0,0,0,0,0,1,1,1],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]

wait_4 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,1,0,0],
          [ 0,0,0,0,1,1,1,0],
          [ 0,0,0,0,0,1,1,0],
          [ 0,0,0,0,0,0,0,0]]

wait_5 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,1,1,0,0,0],
          [ 0,0,0,1,1,0,0,0],
          [ 0,0,0,1,1,0,0,0]]

wait_6 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,1,0,0,0,0,0],
          [ 0,1,1,1,0,0,0,0],
          [ 0,1,1,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]

wait_7 = [[ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 1,1,1,0,0,0,0,0],
          [ 1,1,1,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]
                
wait_8 = [[ 0,0,0,0,0,0,0,0],
          [ 0,1,1,0,0,0,0,0],
          [ 0,1,1,1,0,0,0,0],
          [ 0,0,1,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0],
          [ 0,0,0,0,0,0,0,0]]

connect_1 = [[ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0]]

connect_2 = [[ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,1,1,1,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0]]

connect_3 = [[ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,1,1,1,0,0,0],
             [ 0,1,0,0,0,1,0,0],
             [ 0,1,0,1,0,1,0,0],
             [ 0,1,0,1,0,1,0,0],
             [ 0,0,1,1,1,0,0,0],
             [ 0,0,0,1,0,0,0,0]]

connect_4 = [[ 0,0,0,0,0,0,0,0],
             [ 0,0,1,1,1,0,0,0],
             [ 0,1,0,0,0,1,0,0],
             [ 1,0,0,0,0,0,1,0],
             [ 1,0,0,1,0,0,1,0],
             [ 1,0,0,1,0,0,1,0],
             [ 0,1,0,1,0,1,0,0],
             [ 0,0,1,1,1,0,0,0]]

connect_5 = [[ 0,0,1,1,1,0,0,0],
             [ 0,1,0,0,0,1,0,0],
             [ 1,0,0,0,0,0,1,0],
             [ 0,0,0,0,0,0,0,1],
             [ 0,0,0,1,0,0,0,1],
             [ 0,0,0,1,0,0,0,1],
             [ 1,0,0,1,0,0,1,0],
             [ 0,1,0,1,0,1,0,0]]

connect_6 = [[ 0,1,0,0,0,1,0,0],
             [ 1,0,0,0,0,0,1,0],
             [ 0,0,0,0,0,0,0,1],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,1],
             [ 1,0,0,1,0,0,1,0]]

connect_7 = [[ 1,0,0,0,0,0,1,0],
             [ 0,0,0,0,0,0,0,1],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,1]]

connect_8 = [[ 0,0,0,0,0,0,0,1],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,0,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0],
             [ 0,0,0,1,0,0,0,0]]

                          
matrix_animate_typing = [matrix_type_1, matrix_type_2, matrix_type_3, matrix_type_4, matrix_type_5]
matrix_animate_speak = [matrix_speak_1, matrix_speak_2, matrix_smile, matrix_speak_2]
matrix_animate_heart = [matrix_empty, matrix_empty, matrix_empty, matrix_heart_1, matrix_heart_2, matrix_heart_3, matrix_heart_4, matrix_heart_4, matrix_heart_4, matrix_heart_4, matrix_heart_4, matrix_heart_4, matrix_heart_3, matrix_heart_2, matrix_heart_1]
matrix_animate_wave = [matrix_wave_1, matrix_wave_2, matrix_wave_3, matrix_wave_2]
matrix_animate_wait = [wait_1, wait_2, wait_3, wait_4, wait_5, wait_6, wait_7, wait_8]
matrix_animate_connect = [connect_1, connect_2, connect_3, connect_4, connect_5, connect_6, connect_7, connect_8]

address_setup = []
running = 0
leav_this_on_stop= None



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


def clear(wait=0, address=0x70):
    '''
    Clear all leds
    Wait wait number of seconds before clear
    '''
    if wait==0:
        for i in range(0x10):
            steelsquid_i2c.write_8_bit(address, i, 0x00)    
    else:
        steelsquid_utils.execute_delay(wait, clear, (0, address,))
        

def get_matrix():
    '''
    Get matrix to use in paint
    '''
    return [[0 for x in range(8)] for y in range(8)] 


def paint_flash(matrix, rotate=2, address=0x70, seconds=1, status=None):
    '''
    Light a pattern
    matrix= two dimensinal array 8*8  [ROW, COLUMN]
    rotate: rotate the array clockwise this number of times
    '''
    steelsquid_utils.execute_flash("paint_flash", status, seconds, paint, (matrix, rotate, address,), paint, (empty, rotate, address,))
    

def paint(matrix, rotate=2, address=0x70):
    '''
    Light a pattern
    matrix= two dimensinal array 8*8  [ROW, COLUMN]
    rotate: rotate the array clockwise this number of times
    '''
    if address not in address_setup:
        _setup(address)
        address_setup.append(address)
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


def animate_start(matrix_list, rotate=2, seconds=1, address=0x70):
    '''
    Show all the matrix in a list
    sleep number of seconds between
    '''
    global running
    running = running + 1
    if running == 10000:
        running = 1
    thread.start_new_thread(_animate_thread, (running, matrix_list, rotate, seconds, address))


def animate_stop():
    '''
    Stop the animater
    '''
    global running
    running = running + 1
    clear()
    
    
def _animate_thread(r_id, matrix_list, rotate=2, seconds=1, address=0x70):
    while running==r_id:
        for matrix in matrix_list:
            paint(matrix, rotate, address)
            time.sleep(seconds)
            if running!=r_id:
                break
    if leav_this_on_stop == None:
        pass
        #clear()
    else:
        paint(leav_this_on_stop, rotate, address)
    


def animate_typing(status, rotate=2, address=0x70):
    '''
    Animate a typing icon
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    '''
    global leav_this_on_stop
    leav_this_on_stop = None
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_typing, rotate, 0.2)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_typing, rotate, 0.2)
        steelsquid_utils.execute_delay(status, animate_stop)


def animate_speak(status, leav_this=None, rotate=2, address=0x70):
    '''
    Animate a speaking mouth
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    leav_this = Do not clear, paint this instead
    '''
    global leav_this_on_stop
    leav_this_on_stop = leav_this
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_speak, rotate, 0.14)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_speak, rotate, 0.14)
        steelsquid_utils.execute_delay(status, animate_stop)


def animate_heart(status, rotate=2, address=0x70):
    '''
    Animate a heart
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    leav_this = Do not clear, paint this instead
    '''
    global leav_this_on_stop
    leav_this_on_stop = None
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_heart, rotate, 0.1)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_heart, rotate, 0.1)
        steelsquid_utils.execute_delay(status, animate_stop)


def animate_wave(status, rotate=2, address=0x70):
    '''
    Animate a waving man
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    leav_this = Do not clear, paint this instead
    '''
    global leav_this_on_stop
    leav_this_on_stop = None
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_wave, rotate, 0.15)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_wave, rotate, 0.15)
        steelsquid_utils.execute_delay(status, animate_stop)
        
        
def animate_wait(status, rotate=2, address=0x70):
    '''
    Animate a wait clock
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    leav_this = Do not clear, paint this instead
    '''
    global leav_this_on_stop
    leav_this_on_stop = None
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_wait, rotate, 0.1)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_wait, rotate, 0.1)
        steelsquid_utils.execute_delay(status, animate_stop)


def animate_connect(status, rotate=2, address=0x70):
    '''
    Animate a connect
    status = boolean: start or stop animation
    status = int: aimate for this number of seconds
    leav_this = Do not clear, paint this instead
    '''
    global leav_this_on_stop
    leav_this_on_stop = None
    if type(status) == types.BooleanType:
        if status:
            animate_start(matrix_animate_connect, rotate, 0.1)
        else:
            animate_stop()
    else:
        animate_start(matrix_animate_connect, rotate, 0.1)
        steelsquid_utils.execute_delay(status, animate_stop)


if __name__ == "__main__":
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        print("")
        printb("lmatrix test")
        print("Write a test")
        print("")
    else:
        if sys.argv[1]=='test':

            animate_connect(True)
            raw_input("Press Enter to continue...")
            
