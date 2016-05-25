#!/usr/bin/python -OO


'''
A simple serial interface for RMCS-220X High-Torque Encoder DC Servo Motor and Driver .
https://www.active-robots.com/fileuploader/download/download/?d=0&file=custom%2Fupload%2FFile-1440671791.pdf

Set speed of the motor or move to position

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-05-18 Created
'''

import serial
import sys


class rmcs220x:
    '''
    The server
    '''

    def __init__(self, serial_port="/dev/ttyAMA0", speed_damping=10):
        '''
        Constructor.
        serial_port: /dev/ttyUSB0, /dev/ttyUSB0, /dev/ttyAMA0
        speed_damping: 0 to 255  (0 = no damping, 255 max damping)
        Damping variable sets a limit on how quickly the true speed and change based on its current value. It
        allows for smooth ramp up and down for speeds and removes jerks and clicks in the system. 
        '''
        self.ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True)                
        self.ser.write('Y\r')
        self.ser.flush()
        self.ser.write('D'+str(speed_damping)+'\r')
        self.ser.flush()


    def set_speed(self, speed):
        '''
        Set the speed of the motor.
        from -255 to +255
        -255 = 100% back speed
        0 = no speed
        255 = 100% forward speed
        '''
        speed = int(speed)
        if speed < -255 or speed > 255: 
            raise ValueError("Must be -255 to +255")
        self.ser.write('S')
        self.ser.write(str(speed))
        self.ser.write('\r')
        self.ser.flush()
            

    def set_position(self, position):
        '''
        Set the position of the motor.
        1 to 1825 (0 to 365 degrees)
        '''
        position = int(position)
        if position < 1 or position > 1825:
            raise ValueError("Must be 1 to 1825")
        self.ser.write('G')
        self.ser.write(str(position))
        self.ser.write('\r')
        self.ser.flush()

            
if __name__ == "__main__":
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        print("")
        printb("rmcs220x speed <port> <speed>")
        print("Set speed of RMCS-220X High-Torque Encoder DC Servo Motor and Driver ")
        print("port: /dev/ttyUSB0, /dev/ttyUSB0, /dev/ttyAMA0")
        print("speed: -255 to +255")
    else:
        try:
            sab = rmcs220x(sys.argv[2])
            if sys.argv[1]=='speed':
                sab.set_speed(sys.argv[3])
            elif sys.argv[1]=='position':
                sab.set_position(sys.argv[3])
        except KeyboardInterrupt:
            pass


