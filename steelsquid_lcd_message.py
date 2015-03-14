#!/usr/bin/python -OO


'''
Print message to HDD44780 compatible LCD from Raspberry Pi
And also to a Nokia51010 LCD

http://tronixlabs.com/news/tutorial-serial-i2c-backpack-for-hd44780compatible-lcd-modules-with-arduino/
https://www.sparkfun.com/products/10168

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
import time

if len(sys.argv)<3:
    from steelsquid_utils import printb
    print("")
    printb("lcd-missage hddd <message>")
    print("Print message to HDD44780 compatible LCD connected directly to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage hdd <message>")
    print("Print message to HDD44780 compatible LCD connected via i2c to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage nokia <message>")
    print("Print message to Nokia5110 LCD connected via spi to the Raspberry Pi.")
    print("See http://www.steelsquid.org/pi-io-example")
    print("")
    printb("lcd-missage ssd <message>")
    print("Print message to ssd1306 oled LCD connected via i2c to the Raspberry Pi.")
    print("")
    print("http://tronixlabs.com/news/tutorial-serial-i2c-backpack-for-hd44780compatible-lcd-modules-with-arduino/")
    print("https://www.sparkfun.com/products/10168")
    print("NOTE! When you execute this from the command line it execute outside of steelsquid daemon, and may interrupt for example the LCD, DAC, ADC or extra GPIO.")
    print("It is meant to be used inside the steelsquid daemon (see http://www.steelsquid.org/steelsquid-kiss-os-development)")
    print("")
elif sys.argv[1] == 'hddd':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=False)
elif sys.argv[1] == 'hdd':
	steelsquid_pi.hdd44780_write(sys.argv[2:], is_i2c=True)
elif sys.argv[1] == 'nokia':
	steelsquid_pi.nokia5110_write(sys.argv[2:])
elif sys.argv[1] == 'ssd':
	steelsquid_pi.ssd1306_write(sys.argv[2:])
