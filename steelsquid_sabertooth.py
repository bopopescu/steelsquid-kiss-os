#!/usr/bin/python -OO


'''
A simple serial interface for Sabertooth motor controller.
motor1 = left 
motor2 = right
http://www.dimensionengineering.com/products/sabertooth2x25

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


class SteelsquidSabertooth():
    '''
    The server
    '''

    def __init__(self, serial_port="/dev/ttyS0", baudrate=2400, speed_min_add = 5):
        '''
        Constructor.
        @param speed_min_add: Motor speed can be 1 to 63. if this is 10 then the lowest speed is 10 not 1
                            Use this if the motor dont spin on low voltage
        '''
        self.serial_port=serial_port
        self.baudrate = baudrate
        self.speed_min_add = speed_min_add
        self.speed_interval = 63 - speed_min_add
        self.ser = serial.Serial(self.serial_port, self.baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True)                


    def set_dc_speed(self, left, right):
        '''
        Set the speed.
        from -100 to +100
        -100 = 100% back speed
        0 = no speed
        100 = 100% forward speed
        '''
        if left != None:
            left = int(left)
            if left < -100 or left > 100:
                raise ValueError("Must be -100 to +100")
            if left > 0:
                value = int(math.ceil(self.speed_interval*(float(left)/100)))
                left = 64 + self.speed_min_add + value
            elif left < 0:
                value = int(math.ceil(self.speed_interval*(float(left*-1)/100)))
                left = 64 - (self.speed_min_add + value)
            else:
                left = 64
            
            self.ser.write(chr(left))
        if right != None:
            right = int(right)
            if right < -100 or right > 100:
                raise ValueError("Must be -100 to +100")
            if right > 0:
                value = int(math.ceil(self.speed_interval*(float(right)/100)))
                right = 192 + self.speed_min_add + value
            elif right < 0:
                value = int(math.ceil(self.speed_interval*(float(right*-1)/100)))
                right = 192 - (self.speed_min_add + value)
            else:
                right = 192
            self.ser.write(chr(right))
        self.ser.flush()
        

    def stop(self):
        '''
        Stop this controller.
        '''
        ser.close()
            
            
if __name__ == "__main__":
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        print("")
        printb("sabertooth <port> <left> <right>")
        print("Set speed of Sabertooth motor controller")
        print("port: /dev/ttyUSB0, /dev/ttyUSB0, /dev/ttyAMA0")
        print("left: Left speed from -100 to +100")
        print("right: Right speed from -100 to +100")
        print("")
        print("http://www.dimensionengineering.com/products/sabertooth2x25")
        print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
        print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    else:
        try:
            sab = SteelsquidSabertooth(sys.argv[1])
            sab.set_dc_speed(sys.argv[2], sys.argv[3])
        except KeyboardInterrupt:
            pass


