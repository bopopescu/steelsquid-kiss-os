#!/usr/bin/python -OO


'''
Listen for signal on gpio pin on the raspberry pi
Input parameter is the gpio number

NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.
It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import time
import sys
import steelsquid_pi


def callback_method(gpio, status):
    '''
    On event
    '''
    if status:
        print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " On :-)"
    else:
        print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " Off :-)"


if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("pi-event <gnd or 3v3> <gpio number>")
    print("Listen for signal on gpio pin and 3.3v on the raspberry pi")
    print("")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        if sys.argv[1] == "gnd":
            steelsquid_pi.gpio_event_gnd(sys.argv[2], callback_method)
        elif sys.argv[1] == "3v3":
            steelsquid_pi.gpio_event_3v3(sys.argv[2], callback_method)
        else:
            steelsquid_pi.gpio_event_3v3(sys.argv[1], callback_method)
        raw_input("Waiting for event...\n")
    except KeyboardInterrupt:
        pass
    finally:
        steelsquid_pi.gpio_cleanup
