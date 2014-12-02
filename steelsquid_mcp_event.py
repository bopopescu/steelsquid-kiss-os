#!/usr/bin/python -OO


'''
Contoll gpio on a  MCP230xx
Listen for button click

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_pi

def exec_this():
    print time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S") + " Click :-)"

if len(sys.argv)==1:
    from steelsquid_utils import printb
    print("")
    printb("mcp-event <address> <gpio number>")
    print("Listen for click event on gpio pin on MCP230xx")
    print("Address: 20, 21, 22, 23, 24, 25, 26, 27")
    print("")
else:
    try:
        steelsquid_pi.mcp23017_click(sys.argv[1], sys.argv[2], exec_this)
    except KeyboardInterrupt:
        pass
