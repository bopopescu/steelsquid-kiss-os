#!/usr/bin/python -OO


'''
Contoll gpio on a  MCP230xx

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
    printb("mcp-get <address> <gpio number>")
    print("Get gpio pin status on MCP230xx")
    print("Address: 20, 21, 22, 23, 24, 25, 26, 27")
    print("On: Connected to earth")
    print("Off: Not connected to earth")
    print("")
else:
    try:
        if(steelsquid_pi.mcp23017_get(sys.argv[1], sys.argv[2])):
            print "On"
        else:
            print "Off"
    except KeyboardInterrupt:
        pass
