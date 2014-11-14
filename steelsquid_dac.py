#!/usr/bin/python -OO


'''
Write analog out from MCP4725 (0 to 5v)

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
    printb("dac <address> <value>")
    print("Write analog out from MCP4725 (0 to 5v)")
    print("address= 60 ")
    print("value = 0 and 4095")
    print("")
else:
    try:
        steelsquid_pi.dac_set(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        pass
