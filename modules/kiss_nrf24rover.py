#!/usr/bin/python -OO


'''.
Fuctionality for my nrf24 controller rover
Also see nrf24rover.html (called from utils.html)

One device is the controll unit and the other the rover.
Connect to the controll unit by WIFi and controll the rover over radio (NRF24L01)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-02-02 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_piio
import steelsquid_kiss_global
import time
import threading
import datetime
import steelsquid_nrf24
import urllib
import os

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
    steelsquid_kiss_global.clear_modules_settings("kiss_nrf24rover")
    # If this is the server (the rover)
    if argument!=None and (argument=="server" or argument=="rover" or argument=="master"):
        steelsquid_utils.set_flag("is_master")
        # Enable the server nrf24 functionality in Steelsquid kiss OS
        steelsquid_kiss_global.nrf24_status("master")
        # Enable the raspberry Pi camera
        steelsquid_kiss_global.camera_status(True)
        # Use low stream bandwith
        steelsquid_utils.set_flag("stream_low")
        # Enable camera streaming
        steelsquid_kiss_global.stream_pi() #Will trigger reboot
    # Or is this the controll device (client)
    else:
        steelsquid_utils.del_flag("is_master")
        # Enable the client nrf24 functionality in Steelsquid kiss OS
        steelsquid_kiss_global.nrf24_status("slave")        
    

def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    # Disable the nrf24 functionality in Steelsquid kiss OS
    steelsquid_kiss_global.nrf24_status(None)
    # Use normal stream bandwith
    steelsquid_utils.del_flag("stream_low")
    # Disable camera streaming
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
    If you want to disable save and read the settings from disk add a variable like this.
    This is usefull under development if you wan to test different values when you restart the module,
    otherwise the value from the first execution to be used ...
      _persistent_off = True
    To sum up: Variables in class SETTINGS that has value: Boolean, Array, Integer, Float, String will be will be persistent.
    '''
    
    # This will tell the system not to save and read the settings from disk
    _persistent_off = False

    # If this is the master (the rover)
    # Or is this the controll device (slave)
    is_master = True

    # The lamp is connected to this GPIO
    lamp_gpio = 12

    # Number of seconds until drive stop if no commands from client (connection lost, stop the rover)
    max_drive_delta = 1

    # When system start move servo here
    servo_position_start = 320

    # Max Servo position
    servo_position_max = 580

    # Min Servo position
    servo_position_min = 144

    # Motor max forward
    motor_forward_max = 100

    # Motor max backward
    motor_backward_max = -100

    # start with this value when drive forward (if lower than this the motor do not turn)
    motor_forward_start = 0

    # start with this value when drive backward (if lower than this the motor do not turn)
    motor_backward_start = 0


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
        # Only the rover need to do this
        if SETTINGS.is_master:
            steelsquid_utils.shout("Steelsquid NRF24 Rover enabled")
            # Set servo start position
            WEB.servo_position = SETTINGS.servo_position_start
            # Move the sevo to start position
            GLOBAL.tilt(WEB.servo_position)
        else:
            steelsquid_utils.shout("Steelsquid NRF24 Rover controller enabled")


    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        pass
        

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
        Execute in a loop
        '''    
        # Only the rover do this...not the controller
        if SETTINGS.is_master:
            try:
                # If more than "configurable" second since last drive command stop the drive (connection may be lost)
                drive_delta = datetime.datetime.now() - WEB.last_drive_command
                if drive_delta.total_seconds()>2:
                    GLOBAL.drive(0, 0)
                urllib.urlretrieve("http://localhost:8080/?action=snapshot", "/opt/steelsquid/web/tmpfs/nrf24rover.jpg")
                the_pic=None
                with open("/opt/steelsquid/web/tmpfs/nrf24rover.jpg", mode='rb') as f:
                    the_pic = bytearray(f.read())
                steelsquid_nrf24.send(the_pic)
            except:
                pass
            return 0.0001 # Execute this method again
        else:
            return None


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
    def nrf24rover_settings(session_id, parameters):
        '''
        Get info on the rover
        '''
        return [WEB.servo_position, SETTINGS.servo_position_max, SETTINGS.servo_position_min, SETTINGS.motor_forward_max, SETTINGS.motor_backward_max, SETTINGS.motor_forward_start, SETTINGS.motor_backward_start, WEB.lamp_status]


    @staticmethod
    def nrf24rover_status(session_id, parameters):
        '''
        Get status
        '''
        return []
    
    
    @staticmethod
    def nrf24rover_camera(session_id, parameters):
        '''
        Tilt camera up and down
        '''
        try:
            steelsquid_nrf24.command("tilt", parameters)
        except:
            steelsquid_utils.shout()


    @staticmethod
    def nrf24rover_drive(session_id, parameters):
        '''
        Tilt camera up and down
        '''
        steelsquid_nrf24.command("drive", parameters)
    
        
    @staticmethod
    def nrf24rover_lamp(session_id, parameters):
        '''
        Turn the lamp on and off
        '''
        steelsquid_nrf24.command("lamp", parameters)
        
        
class RADIO(object):
    '''
    If you have a NRF24L01+ transceiver connected to this device you can use server/client or master/slave functionality.
    Enable the nrf24 server functionality in command line: set-flag  nrf24_server
    On client device: set-flag  nrf24_client
    Master: set-flag  nrf24_master
    Slave: set-flag  nrf24_slave
    Must restart the steelsquid daeomon for it to take effect.
    In python you can do: steelsquid_kiss_global.nrf24_status(status)
        status: server=Enable as server
                client=Enable as client
                master=Enable as master
                slave=Enable as slave
                None=Disable
    SERVER/CLIENT:
    If the clent execute: data = steelsquid_nrf24.request("a_command", data)
    A method with the name a_command(data) will execute on the server in class RADIO.
    The server then can return some data that the client will reseive...
    If server method raise exception the steelsquid_nrf24.request("a_command", data) will also raise a exception.
    MASTER/SLAVE:
    One of the devices is master and can send data to the slave (example a file or video stream).
    The data is cut up into packages and transmitted.
    The slave can transmitt short command back to the master on every package of data it get.
    This is usefull if you want to send a low resolution and low framerate video from the master to the slave.
    And the slave then can send command back to the master.
    Master execute: steelsquid_nrf24.send(data)
    The method: on_receive(data) will be called on the client
    Slave execute: steelsquid_nrf24.command("a_command", parameters)
    A method with the name: a_command(parameters) will be called on the master
                            parameters is a list of strings
    '''

    @staticmethod
    def on_receive(data):
        '''
        Data from the master to the slave
        '''
        with open("/opt/steelsquid/web/tmpfs/nrf24rover_t.jpg", mode='wb') as f:
            f.write(data)
        if os.path.getsize('/opt/steelsquid/web/tmpfs/nrf24rover_t.jpg')>1:
            os.rename("/opt/steelsquid/web/tmpfs/nrf24rover_t.jpg", "/opt/steelsquid/web/tmpfs/nrf24rover.jpg")

    
    @staticmethod
    def lamp(parameters):
        '''
        A request from client to turn on/off the lamp
        '''
        GLOBAL.lamp(parameters[0])   
        
    
    @staticmethod
    def drive(parameters):
        '''
        A request from client to set motor speed
        '''
        GLOBAL.drive(parameters[0], parameters[1])        
            

    @staticmethod
    def tilt(parameters):
        '''
        A request from client to set camera tilt
        '''
        GLOBAL.tilt(parameters[0])


class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''

    @staticmethod
    def lamp(status):
        '''
        Turn lamp on and off
        '''
        steelsquid_pi.gpio_set(SETTINGS.lamp_gpio, steelsquid_utils.to_boolean(status))

    
    @staticmethod
    def tilt(position):
        '''
        Set servo to position
        '''
        position = int(position)
        if position>SETTINGS.servo_position_max:
            position=SETTINGS.servo_position_max
        elif position<SETTINGS.servo_position_min:
            position=SETTINGS.servo_position_min
        WEB.servo_position = position
        steelsquid_pi.pca9685_move(0, position)
        
    
    @staticmethod
    def drive(left, right):
        '''
        Set speed of motors
        '''
        left = int(left)
        right = int(right)
        if left>SETTINGS.motor_forward_max:
            left=SETTINGS.motor_forward_max
        elif left<SETTINGS.motor_backward_max:
            left=SETTINGS.motor_backward_max
        if right>SETTINGS.motor_forward_max:
            right=SETTINGS.motor_forward_max
        elif right<SETTINGS.motor_backward_max:
            right=SETTINGS.motor_backward_max
        WEB.last_drive_command = datetime.datetime.now()
        steelsquid_pi.sabertooth_motor_speed(left, right)
