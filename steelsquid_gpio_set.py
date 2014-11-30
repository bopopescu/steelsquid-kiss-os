#!/usr/bin/python -OO


'''
Set gpio pin to hight (on) or low (off)
Input parameter is 3v3 or gnd and the gpio number and the on/off

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
    printb("pi-set <gnd or 3v3> <gpio number> <on or off>")
    print("Set gpio pin status hight (on) or low (off)")
    print("")
else:
	try:
		if sys.argv[1] == "gnd":
			if sys.argv[2] == "on":
				steelsquid_pi.gpio_set_gnd(sys.argv[2], True)
			else:
				steelsquid_pi.gpio_set_gnd(sys.argv[2], False)
		elif sys.argv[1] == "3v3":
			if sys.argv[2] == "on":
				steelsquid_pi.gpio_set_3v3(sys.argv[2], True)
			else:
				steelsquid_pi.gpio_set_3v3(sys.argv[2], False)
		else:
			if sys.argv[2] == "on":
				steelsquid_pi.gpio_set_gnd(sys.argv[1], True)
			else:
				steelsquid_pi.gpio_set_gnd(sys.argv[1], False)
	except KeyboardInterrupt:
		pass
	finally:
		steelsquid_pi.gpio_cleanup
