#!/usr/bin/python -OO


'''
Read gps cordinates from gpsd

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

import steelsquid_utils
import thread
import gps
import math

gpsd = gps.gps(mode=gps.WATCH_ENABLE)


def _thread():
    '''
    Thread read from gps
    '''
    while True:
        try:
            gpsd.next()
        except:
            steelsquid_utils.shout()


def connected():
    '''
    Has GPS connection
    '''
    return gpsd.fix.latitude > 0 and gpsd.fix.longitude > 0


def satellites():
    '''
    Get nummber of satellites
    '''
    x = gpsd.satellites
    if math.isnan(x):
        return 0
    else:
        return int(x)


def latitude():
    '''
    Get latitude
    '''
    x = gpsd.fix.latitude
    if math.isnan(x):
        return 0
    else:
        return x
    


def longitude():
    '''
    Get longitude
    '''
    x = gpsd.fix.longitude
    if math.isnan(x):
        return 0
    else:
        return x


def altitude():
    '''
    Get altitude
    '''
    x = gpsd.fix.altitude
    if math.isnan(x):
        return 0
    else:
        return int(x)
    

def speed():
    '''
    Get altitude (km/h)
    '''
    x = gpsd.fix.speed
    if math.isnan(x):
        return 0
    else:
        return int(x * 3.6)

    

thread.start_new_thread(_thread, ())

