#!/usr/bin/python -OO


'''.
Fuctionality for my rover controller
Also see rover.html (called from utils.html)

For this to start on boot you need to enable it, you can do it like this:
Command line: steelsquid module kiss_expand on
Python: steelsquid_kiss_global.module_status("kiss_expand", True)
Syncrinization program: Press E and then enter

You can omit all the undelaying methods and classes and this module will just be imported...

Varibale is_started
 Is this module started
 This is set by the system automatically.

If a method named enable exist:
 When this module is enabled what needs to be done (execute: steelsquid module XXX on)
 Maybe you need create some files or enable other stuff.

If a method named disable exist:
 When this module is disabled what needs to be done (execute: steelsquid module XXX off)
 Maybe you need remove some files or disable other stuff.

If Class with name SETTINGS exist:
 The system will try to load settings with the same name as all variables in the class SETTINGS.
 If the variable value is Boolean: steelsquid_utils.get_flag("variable_name")
 If the variable value is Integer, Float, String: steelsquid_utils.get_parameter("variable_name")
 If the variable value is Array []: steelsquid_utils.get_list("variable_name")
 The variable value will also be used as default value if the paramater or list not is found
 When the system shutdowen the value of the variable will also be saved to disk
 EX: 
   class SETTINGS(object):
       this_is_a_flag = False
       this_is_a_parameter = "a_default_value"
       this_is_a_list = []
   System try to read: steelsquid_utils.get_flag("this_is_a_flag")
   System try to read: steelsquid_utils.get_parameter("this_is_a_parameter", "a_default_value")
   System try to read: steelsquid_utils.get_list("this_is_a_list", [])
 To sum up: Variables in class SETTINGS that has value: Boolean, Array, Integer, Float, String will be persistent.

If Class with name SYSTEM has this staticmethods
 on_start() exist it will be executed when system starts (boot)
 on_stop() exist it will be executed when system stops (shutdown)
 on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
 on_vpn(status, name, ip) This will fire when a VPN connection is enabled/disabled.
 on_bluetooth(status) exist it will be execute on bluetooth enabled
 on_mount(type_of_mount, remote, local) This will fire when USB, Samba(windows share) or SSH is mounted.
 on_umount(type_of_mount, remote, local) This will fire when USB, Samba(windows share) or SSH is unmounted.
 on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)

If Class with name LOOP
 Every static method with no inparameters will execute over and over again untill it return None or -1
 If it return a number larger than 0 it will sleep for that number of seconds before execute again.
 If it return 0 it will not not sleep, will execute again immediately.
 Every method will execute in its own thread

Class with name EVENTS
 Create staticmethods in this class to listen for asynchronous events.
 Example: If you have a method like this:
   @staticmethod
   def this_is_a_event(a_parameter, another_parameter):
      print a_parameter+":"+another_parameter
 Then if a thread somewhere in the system execute this: steelsquid_kiss_global.broadcast_event("this_is_a_event", ("para1", "para2",))
 The method def this_is_a_event will execute asynchronous

Class with name WEB:
 Methods in this class will be executed by the webserver if module is activated and the webserver is enabled
 If is a GET it will return files and if it is a POST it executed commands.
 It is meant to be used as follows.
 1. Make a call from the browser (GET) and a html page is returned back.
 2. This html page then make AJAX (POST) call to the server to retrieve or update data.
 3. The data sent to and from the server can just be a simple list of strings.
 See steelsquid_http_server.py for more examples how it work

Class with name SOCKET:
 Methods in this class will be executed by the socket connection if module is activated and the socket connection is enabled
 A simple class that i use to sen async socket command to and from client/server.
 A request can be made from server to client or from client to server
 See steelsquid_connection.py and steelsquid_socket_connection.py
 - on_connect(remote_address): When a connection is enabled
 - on_disconnect(error_message): When a connection is lost

If this is a PIIO board
Methods in this class will be executed by the system if module is enabled and this is a PIIO board
Enebale this module like this: steelsquid piio-on
 on_voltage_change(voltage) Will fire when in voltage to the PIIO board i changed 
 on_low_bat(voltage) exist it will execute when voltage is to low.
 on_button(button_nr) exist it will execute when button 1 to 6 is clicken on the PIIO board
 on_button_info() exist it will execute when info button clicken on the PIIO board
 on_switch(dip_nr, status) exist it will execute when switch 1 to 6 is is changed on the PIIO board
 on_movement(x, y, z) will execute if Geeetech MPU-6050 is connected and the device is moved.
 on_rotation(x, y) will execute if Geeetech MPU-6050 is connected and the device is tilted.

The class with name GLOBAL
 Put global staticmethods in this class, methods you use from different part of the system.
 Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
 It is not necessary to put it her, you can also put it direcly in the module or use a nother name (but i think it is kind of nice to have it inside this class)

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


def enable(argument=None):
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
        
    #Clear any saved settings for this module
    steelsquid_kiss_global.clear_modules_settings("kiss_rover")
    # Get what tyoe of rover this is from the start argument
    if argument!=None and argument=="large":
        # If this is a large rover use other defualt settings
        steelsquid_utils.set_parameter("rover_type", "large")
        steelsquid_utils.set_parameter("servo_position_start", "70")
        steelsquid_utils.set_parameter("servo_position_max", "160")
        steelsquid_utils.set_parameter("servo_position_min", "10")
        steelsquid_utils.set_parameter("motor_forward_max", "1000")
        steelsquid_utils.set_parameter("motor_backward_max", "-1000")
        steelsquid_utils.set_parameter("motor_forward_start", "75")
        steelsquid_utils.set_parameter("motor_backward_start", "-75")
    elif argument!=None and argument=="mini":
        # If this is a large rover use other defualt settings
        steelsquid_utils.set_parameter("rover_type", "mini")
        steelsquid_utils.set_parameter("servo_position_start", "85")
        steelsquid_utils.set_parameter("servo_position_max", "140")
        steelsquid_utils.set_parameter("servo_position_min", "30")
        steelsquid_utils.set_parameter("motor_forward_max", "800")
        steelsquid_utils.set_parameter("motor_backward_max", "-800")
        steelsquid_utils.set_parameter("motor_forward_start", "170")
        steelsquid_utils.set_parameter("motor_backward_start", "-170")
    else:
        steelsquid_utils.set_paramater("rover_type", "small")
    # Enable the PIIO board
    if not steelsquid_kiss_global.is_module_enabled("kiss_piio") and not steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", True, restart=False) # Not trigger reboot
    elif not steelsquid_kiss_global.is_module_enabled("kiss_piio") and steelsquid_kiss_global.stream():
        steelsquid_kiss_global.module_status("kiss_piio", True, restart=True) # Trigger reboot
    # Enable PI camera streaming (if necessary)
    if not steelsquid_kiss_global.stream() == "pi":
        steelsquid_kiss_global.stream_pi() #Will trigger reboot


def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
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
    # What type of rover is this. This is set by the enable module (Small or large, default small)
    rover_type = "small"

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
        steelsquid_utils.shout("Steelsquid Rover enabled ("+SETTINGS.rover_type+")")
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
        return [WEB.servo_position, SETTINGS.servo_position_max, SETTINGS.servo_position_min, SETTINGS.motor_forward_max, SETTINGS.motor_backward_max, SETTINGS.motor_forward_start, SETTINGS.motor_backward_start, WEB.lamp_status, SETTINGS.rover_type]
    
    
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
        # The large rover uses Piborg diablo motor controller
        if SETTINGS.rover_type=="large":
            steelsquid_pi.diablo_motor_1(left);
            steelsquid_pi.diablo_motor_2(right);
        else:
            steelsquid_piio.motor(left, right)
    
        
    @staticmethod
    def rover_lamp(session_id, parameters):
        '''
        Turn the lamp on and off
        '''
        status = steelsquid_utils.to_boolean(parameters[0])
        steelsquid_piio.power(1, status)
        steelsquid_piio.power(2, status) 
        
