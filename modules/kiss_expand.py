#!/usr/bin/python -OO


'''
Use this file to implement you own stuff...

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

class STATIC(object):
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.

class DYNAMIC(object):
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe toy enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.

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
 If you want to disable save and read the settings from disk add a variable like this.
 This is usefull under development if you wan to test different values when you restart the module,
 otherwise the value from the first execution to be used ...
  _persistent_off = True
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

Class RADIO
    If you have a NRF24L01+ transceiver connected to this device you can use server/client or master/slave functionality.
    NRF24L01+
        Enable the nrf24 server functionality in command line: set-flag  nrf24_server
        On client device: set-flag  nrf24_client
        Master: set-flag  nrf24_master
        Slave: set-flag  nrf24_slave
        Must restart the steelsquid daeomon for it to take effect.
        In python you can do: steelsquid_kiss_global.nrf24_status(status)
        status: server=Enable as server
                client=Enable as client
                aster=Enable as master
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

The class with name GLOBAL
 Put global staticmethods in this class, methods you use from different part of the system.
 Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
 It is not necessary to put it her, you can also put it direcly in the module or use a nother name (but i think it is kind of nice to have it inside this class)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import os
import time
import thread
import threading
import steelsquid_utils
import steelsquid_pi
import steelsquid_kiss_global


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
    pass




def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    pass




class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''




class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe toy enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''




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
    To sum up: Variables in class SETTINGS that has value: Boolean, Array, Integer, Float, String will be persistent.
    '''
    
    
    

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
        pass
        

    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        pass


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
    def on_vpn(status, name, ip):
        '''
        This will fire when a VPN connection is enabled/disabled.
        status = True/False  (VPN on or OFF)
        name = Name of the VPN connection
        ip = VPN IP address  (None if status=False)
        '''    
        pass
        
        
    @staticmethod
    def on_bluetooth(status):
        '''
        Execute when bluetooth is enabled/disabled
        status = True/False
        '''    
        pass


    @staticmethod
    def on_mount(type_of_mount, remote, local):
        '''
        This will fire when USB, Samba(windows share) or SSH is mounted.
        type_of_mount = usb, samba, ssh
        remote = Remote path
        local = Where is it mounted localy
        '''    
        pass


    @staticmethod
    def on_umount(type_of_mount, remote, local):
        '''
        This will fire when USB, Samba(windows share) or SSH is unmounted.
        type_of_mount = usb, samba, ssh
        remote = Remote path
        local = Where is it mounted localy
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




class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''

    @staticmethod
    def example_loop():
        '''
        Just a example loop
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

    @staticmethod
    def example_event(val1, val2):
        '''
        Just a example event
        '''    
        pass




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
    THIS ONLY WORKS ON THE PIIO BOARD...
    Methods in this class will be executed by the system if module is enabled and this is a PIIO board
    Enebale this module like this: steelsquid piio-on
     on_voltage_change(voltage) Will fire when in voltage to the PIIO board i changed.
     on_low_bat(voltage) Will execute when voltage is to low.
     on_button(button_nr) Will execute when button 1 to 6 is clicken on the PIIO board
     on_button_info() Will execute when info button clicken on the PIIO board
     on_switch(dip_nr, status) Will execute when switch 1 to 6 is is changed on the PIIO board
     on_movement(x, y, z) will execute if Geeetech MPU-6050 is connected and the device is moved.
     on_rotation(x, y) will execute if Geeetech MPU-6050 is connected and the device is tilted.
    '''
        
    @staticmethod
    def on_voltage_change(voltage):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Will fire when in voltage to the PIIO board i changed
        voltage = Current voltage
        '''    
        pass

        
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


    @staticmethod
    def on_movement(x, y, z):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute if Geeetech MPU-6050 is connected and the device is moved.
        '''    
        pass


    @staticmethod
    def on_rotation(x, y):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute if Geeetech MPU-6050 is connected and the device is tilted.
        '''    
        pass




class RADIO(object):
    '''
    If you have a NRF24L01+ or HM-TRLR-S transceiver connected to this device you can use server/client or master/slave functionality.
    NRF24L01+
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
        pass

    
    
class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''

    
    
    
