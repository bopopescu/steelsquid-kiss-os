#!/usr/bin/python -OO


'''.
Fuctionality for my rover controller
Also see rover.html (called from utils.html)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-12-26 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import steelsquid_piio
import steelsquid_kiss_global
import time


# Is this module started
# This is set by the system automatically.
is_started = False


def enable():
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    '''
    steelsquid_kiss_global.expand_module("steelsquid_kiss_piio", True, restart=False)
    steelsquid_kiss_global.stream_pi() #Will trigger reboot


def disable():
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    '''
    steelsquid_kiss_global.stream_off() #Will trigger reboot


class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if module is enabled
    on_start() exist it will be executed when system starts (boot)
    on_stop() exist it will be executed when system stops (shutdown)
    on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
    on_bluetooth(status) exist it will be execute on bluetooth enabled
    on_loop() exist it will execute over and over again untill it return None or -1
    on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)
    '''

    @staticmethod
    def on_start():
        '''
        This will execute when system starts
        Do not execute long running stuff here, do it in on_loop...
        '''
        steelsquid_utils.shout("Steelsquid Rover enabled")
        # Load servo start, max and min position
        GLOBAL.servo_position_start = steelsquid_utils.get_parameter("servo_position_start", GLOBAL.servo_position_start)
        GLOBAL.servo_position_max = steelsquid_utils.get_parameter("servo_position_max", GLOBAL.servo_position_max)
        GLOBAL.servo_position_min = steelsquid_utils.get_parameter("servo_position_min", GLOBAL.servo_position_min)
        # Set the sevo to start position
        steelsquid_piio.servo(1, GLOBAL.servo_position_start)       
        # Load DC motor max forward and backward speed
        GLOBAL.motor_forward_max = steelsquid_utils.get_parameter("motor_forward_max", GLOBAL.motor_forward_max)
        GLOBAL.motor_backward_max = steelsquid_utils.get_parameter("motor_backward_max", GLOBAL.motor_backward_max)
        

    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        pass
        
        
    @staticmethod
    def on_loop():
        '''
        This will execute over and over again untill it return None or -1
        If it return a number larger than 0 it will sleep for that number of seconds before execute again.
        If it return 0 it will not not sleep, will execute again imediately.
        '''    
        return 1


    @staticmethod
    def on_network(status, wired, wifi_ssid, wifi, wan):
        '''
        Execute on network up or down.
        status = True/False (up or down)
        wired = Wired ip number
        wifi_ssid = Cnnected to this wifi
        wifi = Wifi ip number
        wan = Ip on the internet
        '''    
        pass
        
        
    @staticmethod
    def on_bluetooth(status):
        '''
        Execute when bluetooth is enabled
        status = True/False
        '''    
        pass
        
        
    @staticmethod
    def on_event_data(key, value):
        '''
        This will fire when data is changed with steelsquid_kiss_global.set_event_data(key, value)
        key=The key of the data
        value=The value of the data
        '''    
        pass


class EVENTS(object):
    '''
    Create staticmethods in this class to listen for asynchronous events.
    Example: If you have a method like this:
      @staticmethod
      def this_is_a_event(a_parameter, another_parameter):
         print a_parameter+":"+another_parameter
    Then if a thread somewhere in the system execute this: steelsquid_kiss_global.broadcast_event("this_is_a_event", ("para1", "para2",))
    The method def this_is_a_event will execute asynchronous
    '''


class WEB(object):
    '''
    Methods in this class will be executed by the webserver if module is enabled and the webserver is enabled
    If is a GET it will return files and if it is a POST it executed commands.
    It is meant to be used as follows.
    1. Make a call from the browser (GET) and a html page is returned back.
    2. This html page then make AJAX (POST) call to the server to retrieve or update data.
    3. The data sent to and from the server can just be a simple list of strings.
    For more examples how it work:
     - steelsquid_http_server.py
     - steelsquid_kiss_http_server.py
     - web/index.html
    '''

    @staticmethod
    def rover_info(session_id, parameters):
        '''
        Get info on the rover
        '''
        pass


class SOCKET(object):
    '''
    Methods in this class will be executed by the socket connection if module is activated and the socket connection is enabled
    A simple class that i use to sen async socket command to and from client/server.
    A request can be made from server to client or from client to server
    See steelsquid_connection.py and steelsquid_socket_connection.py
     - on_connect(remote_address): When a connection is enabled
     - on_disconnect(error_message): When a connection is lost
   '''
    
    #Is this connection a server
    #This is set by the system
    is_server=False

    @staticmethod
    def on_connect(remote_address):
        '''
        When a connection is enabled
        @param remote_address: IP number to the host
        '''
        pass


    @staticmethod
    def on_disconnect(error_message):
        '''
        When a connection is closed
        Will also execute on connection lost or no connection
        @param error_message: I a error (Can be None)
        '''
        pass 

        
class PIIO(object):
    '''
    Methods in this class will be executed by the system if module is activated and this is a PIIO board
    '''

    @staticmethod
    def on_low_bat(voltage):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when voltage is to low.
        Is set with the paramater: voltage_waring
        voltage = Current voltage
        '''    
        pass


    @staticmethod
    def on_button_info():
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when info button clicken on the PIIO board
        '''    
        pass
        

    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        pass


    @staticmethod
    def on_switch(dip_nr, status):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when switch 1 to 6 is is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        pass

        
class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''
    # Servo start position
    servo_position_start = 200
    # Max Servo position
    servo_position_max = 230
    # Min Servo position
    servo_position_min = 80
    # Motor max forward
    motor_forward_max = 200
    # Motor max backward
    motor_backward_max = -200

    @staticmethod
    def dummy():
        '''
        Dummy
        '''
        pass


    
    
    
