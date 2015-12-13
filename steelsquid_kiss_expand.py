#!/usr/bin/python -OO


'''
Use this file to implement you own stuff...

You can omit all the undelaying methods and classes and this module will just be imported...

If method activate(): Return True/False if this functionality is to be enabled/disabled (execute on_enable on_disable... or not)

If Class with name SYSTEM has this staticmethods
 on_enable() exist it will be executed when system starts (boot)
 on_disable() exist it will be executed when system stops (shutdown)
 on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
 on_bluetooth(status) exist it will be execute on bluetooth enabled
 on_loop() exist it will execute over and over again untill it return None or -1
 on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)

Class with name WEB:
 Methods in this class will be executed by the webserver if activate() return True and the webserver is enabled
 If is a GET it will return files and if it is a POST it executed commands.
 It is meant to be used as follows.
 1. Make a call from the browser (GET) and a html page is returned back.
 2. This html page then make AJAX (POST) call to the server to retrieve or update data.
 3. The data sent to and from the server can just be a simple list of strings.
 See steelsquid_http_server.py for more examples how it work

Class with name SOCKET:
 Methods in this class will be executed by the socket connection if activate() return True and the socket connection is enabled
 A simple class that i use to sen async socket command to and from client/server.
 A request can be made from server to client or from client to server
 See steelsquid_connection.py and steelsquid_socket_connection.py
 - on_connect(remote_address): When a connection is enabled
 - on_disconnect(error_message): When a connection is lost

If this is a PIIO board
And Class with name  PIIO has this staticmethods:
 on_low_bat(voltage) exist it will execute when voltage is to low.
 on_button(button_nr) exist it will execute when button 1 to 6 is clicken on the PIIO board
 on_button_info() exist it will execute when info button clicken on the PIIO board
 on_switch(dip_nr, status) exist it will execute when switch 1 to 6 is is changed on the PIIO board

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


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import steelsquid_kiss_global


# Is this enabled (on_enable has executed)
# This is set by the system automaticaly
is_enabled = False


def activate():
    '''
    Return True/False if this functionality is to be enabled (execute on_enable)
    return: True/False
    '''    
    return False


class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if activate() return True
    '''
    
    @staticmethod
    def on_enable():
        '''
        This will execute when system starts
        Do not execute long running stuff here, do it in on_loop...
        '''
        pass
        

    @staticmethod
    def on_disable():
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
        return -1


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


class WEB(object):
    '''
    Methods in this class will be executed by the webserver if activate() return True and the webserver is enabled
    If is a GET it will return files and if it is a POST it executed commands.
    It is meant to be used as follows.
    1. Make a call from the browser (GET) and a html page is returned back.
    2. This html page then make AJAX (POST) call to the server to retrieve or update data.
    3. The data sent to and from the server can just be a simple list of strings.
    See steelsquid_http_server.py for more examples how it work
    '''


class SOCKET(object):
    '''
    Methods in this class will be executed by the socket connection if activate() return True and the socket connection is enabled
    A simple class that i use to sen async socket command to and from client/server.
    A request can be made from server to client or from client to server
    See steelsquid_connection.py and steelsquid_socket_connection.py
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
    Methods in this class will be executed by the system if activate() return True and this is a PIIO board
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
        steelsquid_kiss_global.set_event_data("apan", "ola")


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
    
    
    
