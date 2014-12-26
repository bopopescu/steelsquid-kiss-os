#!/usr/bin/python -OO


'''
Read analog in from ADS1015 (0 to 5v)
http://www.adafruit.com/product/1083

NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.
It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_pi

if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("ads1015 <address> <gpio number>")
    print("Read analog from ADS1015 (0 to 5v)")
    print("address= 48, 49, 4A, 4B ")
    print("gpio = 0 to 3")
    print("")
    print("http://www.adafruit.com/product/1083")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        print steelsquid_pi.ads1015(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        pass
