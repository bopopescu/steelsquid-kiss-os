#!/usr/bin/python -OO


'''
Get gpio pin status hight (on) or low (off)
Input parameter 3v3 or gnd and the gpio number

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU General Public License
@change: 2013-10-25 Created
'''


import sys
import steelsquid_pi

if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("pi-get <gnd or 3v3> <gpio number>")
    print("Get gpio pin status hight (on) or low (off)")
    print("")
else:
	try:
		if sys.argv[1] == "gnd":
			status = steelsquid_pi.gpio_get_gnd(sys.argv[2])
		elif sys.argv[1] == "3v3":
			status = steelsquid_pi.gpio_get_3v3(sys.argv[2])
		else:
			status = steelsquid_pi.gpio_get_3v3(sys.argv[1])		
		if status == True:
			print "on"
		else:
			print "off"
	except KeyboardInterrupt:
		pass
	finally:
		steelsquid_pi.gpio_cleanup
