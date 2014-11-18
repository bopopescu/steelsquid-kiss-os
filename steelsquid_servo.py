#!/usr/bin/python -OO


'''
Controll Adafruit 16-Channel servo driver

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU General Public License
@change: 2014-09-25 Created
'''


import sys
import steelsquid_pi
import time


if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("pi-servo <servo> <value>")
    print("Move Adafruit 16-channel I2c servo to position (pwm value)")
    print("servo: 0 to 15")
    print("value: min=150, max=600 (may differ between servos)")
else:
    try:
        steelsquid_pi.rbada70_move(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        pass

