#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This will execute when steelsquid-kiss-os starts.
Will only execute steelsquid-kiss-boot.
Using this to speed up start of steelsquid kiss daemon.
The reason some files aren't compiled is that the main script, 
which you invoke with python main.py is recompiled every time you run the script. 
All imported scripts will be compiled and stored on the disk.

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''
import steelsquid_kiss_boot


if __name__ == '__main__':
    steelsquid_kiss_boot.main()
