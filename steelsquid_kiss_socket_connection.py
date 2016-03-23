#!/usr/bin/python -OO


'''
Controll steelsquid kiss os with simle socket commands
Socket inplementation of steelsquid_connection...

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_kiss_global
import steelsquid_socket_connection
import steelsquid_utils
import socket
import sys
import select
import thread
import os
import time

class SteelsquidKissSocketConnection(steelsquid_socket_connection.SteelsquidSocketConnection):


    def __init__(self, is_server, host='localhost', port=22222):
        '''
        Constructor
        '''
        super(SteelsquidKissSocketConnection, self).__init__(is_server, host, port=port)




