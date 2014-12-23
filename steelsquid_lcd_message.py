#!/usr/bin/python -OO


'''
Print message to HDD44780 compatible LCD from Raspberry Pi
And also to a Nokia51010 LCD

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_pi
import time

if len(sys.argv)<3:
    from steelsquid_utils import printb
    print("")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("")
    printb("lcd-missage hddd <message>")
    print("Print message to HDD44780 compatible LCD connected directly to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage hdd <message>")
    print("Print message to HDD44780 compatible LCD connected bia i2c to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage nokia <message>")
    print("Print message to Nokia5110 LCD connected bia spi to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
elif sys.argv[1] == 'hddd':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=False)
elif sys.argv[1] == 'hdd':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=True)
elif sys.argv[1] == 'nokia':
	steelsquid_pi.nokia5110_write(sys.argv[2:])
