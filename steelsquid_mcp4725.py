#!/usr/bin/python -OO


'''
Write analog out from MCP4725 (0 to 5v)
http://www.adafruit.com/product/935

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
    printb("mcp4725 <address> <value>")
    print("Write analog out from MCP4725 (0 to 5v)")
    print("address= 60 ")
    print("value = 0 and 4095")
    print("")
    print("http://www.adafruit.com/product/935")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        steelsquid_pi.mcp4725(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        pass
