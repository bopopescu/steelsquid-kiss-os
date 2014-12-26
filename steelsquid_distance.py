#!/usr/bin/python -OO


'''
Measure_distance with a with HC-SR04
Paramater 1 = GPIO for Trig
Paramater 2 = GPIO for Echo

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
    printb("pi-distance <GPIO for Trig> <GPIO for Echo>")
    print("Measure_distance with a HC-SR04")
    print("http://www.micropik.com/PDF/HCSR04.pdf")
    print("")
else:
	try:
		distance = steelsquid_pi.hcsr04_distance(sys.argv[1], sys.argv[2])
		if distance == -1:
			print "Out of range!"
		else:
			print str(distance) + " cm"
	except KeyboardInterrupt:
		pass
	finally:
		steelsquid_pi.gpio_cleanup
