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


    def rover_info_request(self, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.info()
        

    def rover_info_response(self, parameters):
        '''
        '''
        pass
        

    def rover_info_error(self, parameters):
        '''
        '''
        pass


    def rover_light_request(self, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.light()
        

    def rover_light_response(self, parameters):
        '''
        '''
        pass
        

    def rover_light_error(self, parameters):
        '''
        '''
        pass


    def rover_alarm_request(self, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.alarm()
        

    def rover_alarm_response(self, parameters):
        '''
        '''
        pass
        

    def rover_alarm_error(self, parameters):
        '''
        '''
        pass


    def rover_tilt_request(self, parameters):
        '''
        '''
        steelsquid_kiss_global.Rover.tilt(parameters[0])
        

    def rover_tilt_response(self, parameters):
        '''
        '''
        pass
        

    def rover_tilt_error(self, parameters):
        '''
        '''
        pass


    def rover_drive_request(self, parameters):
        '''
        '''
        steelsquid_kiss_global.Rover.drive(parameters[0], parameters[1])
        

    def rover_drive_response(self, parameters):
        '''
        '''
        pass
        

    def rover_drive_error(self, parameters):
        '''
        '''
        pass
