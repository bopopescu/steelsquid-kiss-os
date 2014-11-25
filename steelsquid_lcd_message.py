#!/usr/bin/python -OO


'''
Print message to HDD44780 compatible LCD from Raspberry Pi

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_pi

if len(sys.argv)<3:
    from steelsquid_utils import printb
    print("")
    printb("lcd-missage direct <message>")
    print("Print message to HDD44780 compatible LCD connected directly to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage i2c <message>")
    print("Print message to HDD44780 compatible LCD connected bia i2c to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
elif sys.argv[1] == 'direct':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=False)
elif sys.argv[1] == 'i2c':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=True)
