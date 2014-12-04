#!/usr/bin/python -OO


'''
Set gpio pin to hight (on) or low (off) MCP230xx
hight = 5v
low = earth

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
    printb("mcp-set <address> <gpio number> <on or off>")
    print("Set gpio pin status on MCP230xx")
    print("Address: 20, 21, 22, 23, 24, 25, 26, 27")
    print("Set gpio pin status hight (on) or low (off)")
    print("")
else:
    try:
        if sys.argv[3] == "on":
            steelsquid_pi.mcp23017_set(sys.argv[1], sys.argv[2], True)
        else:
            steelsquid_pi.mcp23017_set(sys.argv[1], sys.argv[2], False)
    except KeyboardInterrupt:
        pass
