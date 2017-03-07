#!/usr/bin/python -OO


'''
Read values from bno0055

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

from Adafruit_BNO055 import BNO055
import steelsquid_utils
import thread
import time

bno = None
is_ok = False
starting = True
offset = None

heading = 0.0
roll = 0.0
pitch = 0.0


def _thread():
    '''
    Thread initialize BNO055
    '''
    global bno
    global is_ok
    global starting
    is_ok = False
    run0=True
    while run0:
        run1=True
        run2=True
        while run1:
            try:
                bno = BNO055.BNO055(serial_port='/dev/ttyS0', rst=18)
                run1=False
            except:
                time.sleep(0.5)
        while run2:
            try:
                if bno.begin():
                    run2 = False
                else:
                    pass
                    #steelsquid_utils.shout("Failed to initialize BNO055!")
            except:
                time.sleep(0.5)
        try:
            status, self_test, error = bno.get_system_status()
            if status == 0x01:
                pass
                #steelsquid_utils.shout(error, is_error=True)
            else:
                run0=False
        except:
            time.sleep(0.5)
    is_ok=True
    starting = False
        

def is_initialized():
    '''
    '''
    return is_ok and not starting


def read(heading_zero=True, switch_roll_pitch=False):
    '''
    Get BNO055 angles
    heading, roll, pitch
    Return None, None, None : Error in read data
    '''
    global starting
    global offset
    global heading
    global roll
    global pitch
    if is_initialized():
        for i in range(3):
            try:
                heading, roll, pitch = bno.read_euler()
                if heading_zero:
                    if heading > 180 and heading <= 360:
                        heading = heading - 360
                if offset == None:
                    offset = heading
                heading = heading - offset
                if switch_roll_pitch:
                    return heading, pitch, roll
                else:
                    return heading, roll, pitch
            except:
                pass
        if not starting:
            starting = True
            is_ok=False
            thread.start_new_thread(_thread, ())
    if switch_roll_pitch:
        return heading, pitch, roll
    else:
        return heading, roll, pitch


def zero_heading():
    '''
    Set next value heading vaue as zero
    '''
    global offset
    offset = None

starting = True
thread.start_new_thread(_thread, ())






