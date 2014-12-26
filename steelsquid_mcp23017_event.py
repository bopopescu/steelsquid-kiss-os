#!/usr/bin/python -OO


'''
Contoll gpio on a  MCP230xx
Listen for button click
http://www.raspberrypi-spy.co.uk/2013/07/how-to-use-a-mcp23017-i2c-port-expander-with-the-raspberry-pi-part-1/

NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.
It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import time
import steelsquid_pi

def exec_this():
    print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " Click :-)"

if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("mcp23017-event <address> <gpio number>")
    print("Listen for click event on gpio pin on MCP230xx")
    print("Address: 20, 21, 22, 23, 24, 25, 26, 27")
    print("")
    print("http://www.raspberrypi-spy.co.uk/2013/07/how-to-use-a-mcp23017-i2c-port-expander-with-the-raspberry-pi-part-1/")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
else:
    try:
        steelsquid_pi.mcp23017_click(sys.argv[1], sys.argv[2], exec_this)
        raw_input("Waiting for event...\n")
    except KeyboardInterrupt:
        pass
