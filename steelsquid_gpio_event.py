#!/usr/bin/python -OO


'''
Listen for signal on gpio pin on the raspberry pi
Input parameter is the gpio number

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import time
import sys
import steelsquid_pi


def on_m(self):
    '''
    On event
    '''
    print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " On :-)"


def off_m(self):
    '''
    On event
    '''
    print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " Off :-)"


if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("pi-event <gnd or 3v3> <gpio number>")
    print("Listen for signal on gpio pin and 3.3v on the raspberry pi")
    print("")
else:
    try:
        if sys.argv[1] == "gnd":
            steelsquid_pi.gpio_event_gnd(sys.argv[2], on_m, off_m)
        elif sys.argv[1] == "3v3":
            steelsquid_pi.gpio_event_3v3(sys.argv[2], on_m, off_m)
        else:
            steelsquid_pi.gpio_event_3v3(sys.argv[1], on_m, off_m)
        raw_input("Waiting for event...\n")
    except KeyboardInterrupt:
        pass
    finally:
        steelsquid_pi.gpio_cleanup
