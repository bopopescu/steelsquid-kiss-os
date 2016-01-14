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
import steelsquid_pi
import steelsquid_piio
import steelsquid_kiss_global
import time
import datetime


# Is this module started
# This is set by the system automatically.
is_started = False


def enable():
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    '''
    # Enable the PIIO board and PI camera streaming (if necessary)
    if not steelsquid_kiss_global.is_module_enabled("kiss_piio") and not steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", True, restart=False) # Not trigger reboot
    elif not steelsquid_kiss_global.is_module_enabled("kiss_piio") and steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", True, restart=True) # Trigger reboot
    if not steelsquid_kiss_global.stream() == "pi":
        steelsquid_kiss_global.stream_pi() #Will trigger reboot
        


def disable():
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    '''
    # Disable the PIIO board and PI camera streaming (if necessary)
    if steelsquid_kiss_global.is_module_enabled("kiss_piio") and steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", False, restart=False) # Not trigger reboot
    elif steelsquid_kiss_global.is_module_enabled("kiss_piio") and steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", False, restart=True) # Trigger reboot
    if steelsquid_kiss_global.stream() == "pi":
        steelsquid_kiss_global.stream_off() #Will trigger reboot


class SETTINGS(object):
    '''
    The system will try to load settings with the same name as all variables in the class SETTINGS.
    If the variable value is Boolean: steelsquid_utils.get_flag("variable_name")
    If the variable value is Integer, Float, String: steelsquid_utils.get_parameter("variable_name")
    If the variable value is Array []: steelsquid_utils.get_list("variable_name")
    The variable value will also be used as default value if the paramater or list not is found
    When the system shutdowen the value of the variable will also be saved to disk
    EX: this_is_a_flag = False
        this_is_a_parameter = "a_default_value"
        this_is_a_list = []
    System try to read: steelsquid_utils.get_flag("this_is_a_flag")
    System try to read: steelsquid_utils.get_parameter("this_is_a_parameter", "a_default_value")
    System try to read: steelsquid_utils.get_list("this_is_a_list", [])
    To sum up: Variables in class SETTINGS that has value: Boolean, Array, Integer, Float, String will be will be persistent.
    '''
    # Number of seconds until drive stop if no commands from client (connection lost, stop the rover)
    max_drive_delta = 1

    # When system start move servo here
    servo_position_start = 210

    # Max Servo position
    servo_position_max = 230

    # Min Servo position
    servo_position_min = 80

    # Motor max forward
    motor_forward_max = 1023

    # Motor max backward
    motor_backward_max = -1023

    # start with this value when drive forward (if lower than this the motor do not turn)
    motor_forward_start = 200

    # start with this value when drive backward (if lower than this the motor do not turn)
    motor_backward_start = -200


class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if module is enabled
    on_start() exist it will be executed when system starts (boot)
    on_stop() exist it will be executed when system stops (shutdown)
    on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
    on_vpn(status, name, ip) This will fire when a VPN connection is enabled/disabled.
    on_bluetooth(status) exist it will be execute on bluetooth enabled
    on_mount(type_of_mount, remote, local) This will fire when USB, Samba(windows share) or SSH is mounted.
    on_umount(type_of_mount, remote, local) This will fire when USB, Samba(windows share) or SSH is unmounted.
    on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)
    '''

    @staticmethod
    def on_start():
        '''
        This will execute when system starts
        Do not execute long running stuff here, do it in on_loop...
        '''
        steelsquid_utils.shout("Steelsquid Rover enabled")
        # Set servo start position
        WEB.servo_position = SETTINGS.servo_position_start
        # Move the sevo to start position
        steelsquid_piio.servo(1, WEB.servo_position)       


class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    @staticmethod
    def on_loop():
        '''
        If more than "configurable" second since last drive command stop the drive (connection may be lost)
        '''    
        drive_delta = datetime.datetime.now() - WEB.last_drive_command
        if drive_delta.total_seconds()>1:
            steelsquid_piio.motor(0, 0)
        return 0.5 # Execute this method again in half a second


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
    
    # Current servo position
    servo_position = 210

    # Is the lamp on or off
    lamp_status = False
    
    # Last time the client send a drive command
    last_drive_command = datetime.datetime.now()

    
    @staticmethod
    def rover_settings(session_id, parameters):
        '''
        Get info on the rover
        '''
        return [WEB.servo_position, SETTINGS.servo_position_max, SETTINGS.servo_position_min, SETTINGS.motor_forward_max, SETTINGS.motor_backward_max, SETTINGS.motor_forward_start, SETTINGS.motor_backward_start, WEB.lamp_status]
    
    
    @staticmethod
    def rover_camera(session_id, parameters):
        '''
        Tilt camera up and down
        '''
        position = int(parameters[0])
        if position>SETTINGS.servo_position_max:
            position=SETTINGS.servo_position_max
        elif position<SETTINGS.servo_position_min:
            position=SETTINGS.servo_position_min
        WEB.servo_position = position
        steelsquid_piio.servo(1, position)


    @staticmethod
    def rover_drive(session_id, parameters):
        '''
        Tilt camera up and down
        '''
        left = int(parameters[0])
        right = int(parameters[1])
        if left>SETTINGS.motor_forward_max:
            left=SETTINGS.motor_forward_max
        elif left<SETTINGS.motor_backward_max:
            left=SETTINGS.motor_backward_max
        if right>SETTINGS.motor_forward_max:
            right=SETTINGS.motor_forward_max
        elif right<SETTINGS.motor_backward_max:
            right=SETTINGS.motor_backward_max
        WEB.last_drive_command = datetime.datetime.now()
        steelsquid_piio.motor(left, right)
    
        
    @staticmethod
    def rover_lamp(session_id, parameters):
        '''
        Turn the lamp on and off
        '''
        status = steelsquid_utils.to_boolean(parameters[0])
        steelsquid_piio.power(1, status)
        
