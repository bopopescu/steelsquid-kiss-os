#!/usr/bin/python -OO


'''
Write analog out from MCP4728 (0 to 5v)
http://www.proto-advantage.com/store/p/MCP4728_Breakout_Board.php

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
    printb("mcp4728 <address> <volt0> <volt1> <volt2> <volt3>")
    print("Write analog out from MCP4728 (0 to 5v)")
    print("address= 61")
    print("volt0 to 3 = Voltage on pins (0 and 4095)")
    print("")
    print("http://www.proto-advantage.com/store/p/MCP4728_Breakout_Board.php")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        steelsquid_pi.mcp4728(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    except KeyboardInterrupt:
        pass
