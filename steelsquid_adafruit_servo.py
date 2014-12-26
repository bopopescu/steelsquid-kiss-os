#!/usr/bin/python -OO


'''
Controll Adafruit 16-Channel servo driver
http://www.adafruit.com/product/815

NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.
It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-09-25 Created
'''


import sys
import steelsquid_pi
import time


if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("ada-servo <servo> <value>")
    print("Move Adafruit 16-channel I2c servo to position (pwm value)")
    print("servo: 0 to 15")
    print("value: min=150, max=600 (may differ between servos)")
    print("")
    print("http://www.adafruit.com/product/815")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        steelsquid_pi.rbada70_move(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        pass

