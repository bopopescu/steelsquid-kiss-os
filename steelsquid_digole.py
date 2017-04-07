#!/usr/bin/python -OO


'''
A simple module to print stuff to digoleserial displays
http://digole.com/index.php?productID=1218

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

import time
import steelsquid_utils
import math
import sys
import serial
import thread


ser = None


def setup(serial_port="/dev/ttyUSB0", baudrate=115200, direction=0):
    '''
    Constructor.
    @param speed_min_add: Motor speed can be 1 to 63. if this is 10 then the lowest speed is 10 not 1
                        Use this if the motor dont spin on low voltage
    '''
    global ser
    ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0)                
    _write_command("SB"+str(baudrate))
    ser.close()
    ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0)                
    clear_screen()
    ser.close()
    ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0)                
    _write_command("SB"+str(baudrate))
    ser.close()
    ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0)                
    clear_screen()
    
    
def clear_screen():
    '''
    CLear screen
    '''
    _write_command("CL")


def write_text(txt, col = None, row = None):
    '''
    Write text
    '''
    if col!= None:
        _write_command("ETP")
        _write_int(col)
        _write_int(row)         
    _write_command("TT"+str(txt), terminate=True)


def write_text_line(txt, padding = None):
    '''
    Write text
    '''
    _write_command("TT"+str(txt)+"\n\r", terminate=True)
    if padding!=None:
        _write_command("ETO")
        _write_int(0)
        _write_int(padding)


def text_position(col, row):
    '''
    Set text position
    '''
    _write_command("TP")
    _write_int(col)
    _write_int(row)


def position(col, row):
    '''
    Set text position
    '''
    _write_command("ETP")
    _write_int(col)
    _write_int(row)    

def _write_command(command_string, terminate = False):
    ''' 
    Write command
    '''
    global ser
    if ser == None:
        setup()
    for c in command_string:
        ser.write(c)
    if terminate:
        ser.write(chr(0))


def _write_int(i):
    '''
    Write command
    '''
    global ser
    if ser == None:
        setup()
    if i > 255:
        ser.write(chr(255))
        ser.write(chr(i-255))
    else:
        ser.write(chr(i))

            
            
if __name__ == "__main__":
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        print("")
        printb("digole <text>")
        print("Write text")
        print("")
    else:
        text_position(0, 0)
        write_text("DATA USAGE\n\r")
                

