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
from collections import deque


bno = None
is_ok = False
offset = None

heading = 0.0
roll = 0.0
pitch = 0.0

fifo = deque([], 3)

def _thread():
    '''
    Thread initialize BNO055
    '''
    global bno
    global is_ok
    is_ok = False
    while True:
        if not is_ok:
            for i in range(10):
                try:
                    bno = BNO055.BNO055(serial_port='/dev/ttyS0', rst=18)
                    break
                except:
                    time.sleep(0.5)
            for i in range(10):
                try:
                    if bno.begin():
                        break
                    else:
                        time.sleep(0.5)
                except:
                    steelsquid_utils.shout()
                    time.sleep(0.5)
            for i in range(10):
                try:
                    status, self_test, error = bno.get_system_status()
                    if status == 0x01:
                        time.sleep(0.5)
                    else:
                        break
                except:
                    time.sleep(0.5)
            is_ok=True
        else:
            time.sleep(0.5)
        

def is_initialized():
    '''
    '''
    return is_ok


def _read(heading_zero=True, switch_roll_pitch=False):
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
    global is_ok
    if is_ok:
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
            steelsquid_utils.shout()
        is_ok=False
    if switch_roll_pitch:
        return 0, pitch, roll
    else:
        return 0, roll, pitch


def read(heading_zero=True, switch_roll_pitch=False):
    '''
    Get BNO055 angles
    heading, roll, pitch
    Return None, None, None : Error in read data
    '''
    heading, pitch, roll = _read(heading_zero, switch_roll_pitch)
    fifo.append(heading)
    heading = steelsquid_utils.median(list(fifo))
    return heading, pitch, roll


def zero_heading():
    '''
    Set next value heading vaue as zero
    '''
    global offset
    offset = None


thread.start_new_thread(_thread, ())






