#!/usr/bin/python -OO


'''
Controll steelsquid kiss os with simle socket commands
Socket inplementation of steelsquid_connection...

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@change: 2013-10-25 Created
'''


import steelsquid_socket_connection
import steelsquid_utils
import socket
import sys
import select
import steelsquid_sabertooth
import thread
import os
import time

class SteelsquidKissSocketServer(steelsquid_socket_connection.SteelsquidSocketConnection):


    def __init__(self, is_server, port=22222):
        '''
        Constructor
        '''
        super(SteelsquidKissSocketServer, self).__init__(is_server, port=port)

    def on_setup_server(self):
        '''
        Override this to setup the server.
        Example setup the serversocket
        Will loop until server is stopped.
        @return: Listener object (example serversocket)
        '''
        return super(SteelsquidKissSocketServer, self).on_setup_server()


    def on_close_connection(self, connection_object, error_message):
        '''
        Override this to close the connection.
        Will also execute on connection lost or no connection
        @param server_object: The connection (Can be None)
        @param error_message: I a error (Can be None)
        '''
        try:
            steelsquid_pi_board.sabertooth_set_speed(0, 0)
        except:
            pass
        connection_object.close()


    def on_close_listener(self, listener_object, error_message):
        '''
        Override this to close the listener.
        Will also execute on unable to listen
        @param listener_object: The listener (Can be None)
        @param error_message: I a error (Can be None)
        '''
        try:
            steelsquid_pi_board.sabertooth_set_speed(0, 0)
        except:
            pass
        listener_object.close()


    def on_start(self):
        '''
        Override this to do start on start
        '''
        steelsquid_utils.shout("Socket connection started")
        if steelsquid_utils.get_flag("rover"):
            steelsquid_utils.shout("Rover enabled")
        try:
            steelsquid_pi_board.sabertooth_set_speed(0, 0)
        except:
            pass


    def on_stop(self):
        '''
        Override this to do start on stop
        '''
        try:
            steelsquid_pi_board.sabertooth_set_speed(0, 0)
        except:
            pass


    def drive_request(self, parameters):
        import steelsquid_pi_board
        left = int(parameters[0])
        right = int(parameters[1])
        steelsquid_pi_board.sabertooth_set_speed(left, right)

    def drive_response(self, parameters):
        pass

    def drive_error(self, parameters):
        print "ERROR"
        print parameters


