#!/usr/bin/python -OO


'''.
This is functionality for my alarm.
Connect different sensors to monitor your house or other thinks.
Also see utils.html

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
import steelsquid_kiss_global
from datetime import datetime
from datetime import timedelta
import time
import os
import urllib
import thread
import sys
import importlib


# Is this module started
# This is set by the system automatically.
is_started = False


def enable(argument=None):
    '''
    When this module is enabled what needs to be done? (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    if not steelsquid_kiss_global.stream() == "pi":
        steelsquid_kiss_global.stream_pi()


def disable(argument=None):
    '''
    When this module is disabled what needs to be done? (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    if steelsquid_kiss_global.stream() == "pi":
        steelsquid_kiss_global.stream_off()


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
        steelsquid_utils.shout("Steelsquid Alarm/Surveillance enabled")
        steelsquid_pi.gpio_event(25, GLOBAL.on_motion, resistor=steelsquid_pi.PULL_NONE)
        
        if not steelsquid_utils.has_parameter("alarm_security_movments"):
            steelsquid_utils.set_parameter("alarm_security_movments", "1");
        if not steelsquid_utils.has_parameter("alarm_security_movments_seconds"):
            steelsquid_utils.set_parameter("alarm_security_movments_seconds", "20");
        if not steelsquid_utils.has_parameter("alarm_security_seconds"):
            steelsquid_utils.set_parameter("alarm_security_seconds", "10");
        if not steelsquid_utils.has_parameter("alarm_security_wait"):
            steelsquid_utils.set_parameter("alarm_security_wait", "120");
        if not steelsquid_utils.has_parameter("alarm_light_acivate"):
            steelsquid_utils.set_parameter("alarm_light_acivate", "15");
        

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
        Check the alarm
        '''    
        # Try to read sensors
        try:
            GLOBAL.light_level = steelsquid_pi.yl40_light_level();
        except:
            pass
        try:
            temp, hum = steelsquid_pi.hdc1008();
            GLOBAL.temperature = round(temp, 1)
            GLOBAL.humidity = round(hum, 1)
        except:
            pass
        try:
            alarm_light_acivate = int(steelsquid_utils.get_parameter("alarm_light_acivate"));
            if alarm_light_acivate != -1:
                if int(GLOBAL.light_level)<alarm_light_acivate:
                    GLOBAL.lamp(True)
                else:
                    GLOBAL.lamp(False)
        except:
            pass
        if steelsquid_utils.get_flag("alarm"):
            if steelsquid_utils.has_parameter("socket_client"):
                # Send status to server
                server_ip = steelsquid_utils.get_parameter("socket_client")
                try:
                    statuses = []
                    name = steelsquid_utils.execute_system_command(['hostname'])[0]
                    armed = steelsquid_utils.get_flag("alarm_security")
                    statuses.append(name)
                    statuses.append(armed)
                    statuses.append(GLOBAL.alarm_triggered)
                    statuses.append(GLOBAL.motion_detected)
                    statuses.append(GLOBAL.is_siren_on)
                    statuses.append(GLOBAL.is_lamp_on)
                    statuses.append(GLOBAL.light_level)
                    statuses.append(GLOBAL.temperature)
                    statuses.append(GLOBAL.humidity)
                    steelsquid_kiss_global.socket_connection.send_request("alarm_push", statuses)
                except:
                    steelsquid_utils.shout()
            elif steelsquid_utils.get_flag("socket_server"):
                #Check if client still is connected, of not remove from status list
                for k in GLOBAL.clients_status.keys():
                    if k not in steelsquid_kiss_global.socket_connection.get_connected_ip_numbers():
                        del GLOBAL.clients_status[k]
                #Check if to send alarm to clients
                if not GLOBAL.alarm_triggered:
                    for key in GLOBAL.clients_status:
                        client = GLOBAL.clients_status[key]
                        GLOBAL.alarm_triggered = steelsquid_utils.to_boolean(client[2])
                        if GLOBAL.alarm_triggered:
                            break
                if GLOBAL.alarm_triggered:
                    alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
                    now = datetime.now()
                    delta = now - GLOBAL.last_trigger_clients
                    if delta.total_seconds() > alarm_security_wait:
                        if not GLOBAL.alarm_triggered:
                            GLOBAL.on_remote_alarm()
                        GLOBAL.last_trigger_clients=datetime.now() 
                        steelsquid_kiss_global.socket_connection.send_request("alarm_remote_alarm", [])
        return 1


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
    def alarm_status(session_id, parameters):
        '''
        Status of alarm
        '''
        if GLOBAL.siren():
            siren="true"
        else:
            siren="false"
        if GLOBAL.lamp():
            lamp="true"
        else:
            lamp="false"
        if GLOBAL.motion_detected:
            motion="true"
        else:
            motion="false"
        if GLOBAL.alarm_triggered:
            alarm_t="true"
        else:
            alarm_t="false"
        if steelsquid_utils.get_flag("alarm_security"):
            alarm_sec="true"
        else:
            alarm_sec="false"
        light_level = "---"
        if GLOBAL.light_level!=None:
            light_level = str(GLOBAL.light_level)
        temperature = "---"
        if GLOBAL.temperature!=None:
            temperature = str(GLOBAL.temperature)
        humidity = "---"
        if GLOBAL.humidity!=None:
            humidity = str(GLOBAL.humidity)
        return [motion, siren, lamp, alarm_t, alarm_sec, light_level, temperature, humidity]


    @staticmethod
    def alarm_settings(session_id, parameters):
        '''
        Settings of alarm
        '''
        is_saved=False
        if len(parameters) > 0:
            if int(parameters[2]) >= int(parameters[3]):
                raise Exception("Alarm time must be smaller than alarm wait!")
            steelsquid_utils.set_parameter("alarm_security_movments", parameters[0])
            steelsquid_utils.set_parameter("alarm_security_movments_seconds", parameters[1])
            steelsquid_utils.set_parameter("alarm_security_seconds", parameters[2])
            steelsquid_utils.set_parameter("alarm_security_wait", parameters[3])
            if parameters[4]=="True":
                steelsquid_utils.set_flag("alarm_security_activate_siren")
            else:
                steelsquid_utils.del_flag("alarm_security_activate_siren")
            if parameters[5]=="True":
                steelsquid_utils.set_flag("alarm_security_send_mail")
            else:
                steelsquid_utils.del_flag("alarm_security_send_mail")
            steelsquid_utils.set_parameter("alarm_light_acivate", parameters[6])
            if parameters[7]=="True":
                steelsquid_utils.set_flag("alarm_remote_siren")
            else:
                steelsquid_utils.del_flag("alarm_remote_siren")
            is_saved=True
        movments = steelsquid_utils.get_parameter("alarm_security_movments")
        movments_seconds = steelsquid_utils.get_parameter("alarm_security_movments_seconds")
        seconds = steelsquid_utils.get_parameter("alarm_security_seconds")
        wait_ = steelsquid_utils.get_parameter("alarm_security_wait")
        alarm_activate_siren = steelsquid_utils.get_flag("alarm_security_activate_siren")
        alarm_mail = steelsquid_utils.get_flag("alarm_security_send_mail")
        alarm_light_a = steelsquid_utils.get_parameter("alarm_light_acivate")
        alarm_remote_siren = steelsquid_utils.get_flag("alarm_remote_siren")
        return [is_saved, movments, movments_seconds, seconds, wait_, alarm_activate_siren, alarm_mail, alarm_light_a, alarm_remote_siren]


    @staticmethod
    def alarm_arm(session_id, parameters):
        '''
        Settings of alarm
        '''
        if len(parameters) > 0:
            if parameters[0]=="true":
                GLOBAL.arm(True)
            else:
                GLOBAL.arm(False)
        return [steelsquid_utils.get_flag("alarm_security")]


    @staticmethod
    def alarm_client_arm(session_id, parameters):
        '''
        Set status of client that is connected to this server
        '''
        if len(parameters)==1:
            if parameters[0] == "True":
                GLOBAL.arm(True)
            else:
                GLOBAL.arm(False)
            steelsquid_kiss_global.socket_connection.send_request("alarm_arm", parameters)
        else:
            if parameters[0]==steelsquid_utils.network_ip():
                if parameters[1] == "True":
                    GLOBAL.arm(True)
                else:
                    GLOBAL.arm(False)
            else:
                steelsquid_kiss_global.socket_connection.send_request("alarm_arm", parameters[1:], parameters[0])


    @staticmethod
    def alarm_client_siren(session_id, parameters):
        '''
        Activate/deactivate siren on client that is connected to this server
        '''
        if parameters[0] == "True":
            GLOBAL.siren(True)
        else:
            GLOBAL.siren(False)
        steelsquid_kiss_global.socket_connection.send_request("alarm_siren", parameters)


    @staticmethod
    def alarm_client_lamp(session_id, parameters):
        '''
        Activate/deactivate IR-lamp on client that is connected to this server
        '''
        if parameters[0] == "True":
            GLOBAL.lamp(True)
        else:
            GLOBAL.lamp(False)
        steelsquid_kiss_global.socket_connection.send_request("alarm_lamp", parameters)


    @staticmethod
    def alarm_siren(session_id, parameters):
        '''
        Aktivate/deactiva siren
        '''
        if parameters[0] == "true":
            GLOBAL.siren(True)
            return "Siren activated"
        else:
            GLOBAL.siren(False)
            return "Siren dectivated"


    @staticmethod
    def alarm_lamp(session_id, parameters):
        '''
        Aktivate/deactiva the lamp
        '''
        if parameters[0] == "true":
            GLOBAL.lamp(True)
            return "The lamp is on"
        else:
            GLOBAL.lamp(False)
            return "The lamp is off"


    @staticmethod
    def alarm_server(session_id, parameters):
        '''
        Status of alarm server
        '''
        alarm = steelsquid_utils.get_flag("alarm")
        if steelsquid_utils.get_flag("socket_server"):
            socket = "server"
        elif steelsquid_utils.has_parameter("socket_client"):
            socket = "client"
        else:
            socket = "disabled"
        return [alarm, socket]


    @staticmethod
    def alarm_server_statuses(session_id, parameters):
        '''
        Get all statuses from this server and connected clients
        '''
        return GLOBAL.get_statuses()


    @staticmethod
    def alarm_app_arm(session_id, parameters):
        '''
        The app set arm/disarm
        '''
        if parameters[0] == "True":
            GLOBAL.arm(True)
        else:
            GLOBAL.arm(False)
        steelsquid_kiss_global.socket_connection.send_request("alarm_arm", parameters)
        return steelsquid_utils.get_flag("alarm_security")


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
        
        
    @staticmethod
    def alarm_push_request(remote_address, parameters):
        '''
        Send status of client to server
        '''
        GLOBAL.clients_status[remote_address]=parameters
        

    @staticmethod
    def alarm_push_response(remote_address, parameters):
        '''
        Send status of client to server
        '''
        pass
        

    @staticmethod
    def alarm_push_error(remote_address, parameters):
        '''
        Send status of client to server
        '''
        steelsquid_utils.shout(parameters[0]);


    @staticmethod
    def alarm_remote_alarm_request(remote_address, parameters):
        '''
        Server send to all clients that some other clients or the server has an alarm
        '''
        GLOBAL.on_remote_alarm()
        

    @staticmethod
    def alarm_remote_alarm_response(remote_address, parameters):
        '''
        Server send to all clients that some other clients or the server has an alarm
        '''
        pass
        

    @staticmethod
    def alarm_remote_alarm_error(remote_address, parameters):
        '''
        Server send to all clients that some other clients or the server has an alarm
        '''
        steelsquid_utils.shout(parameters[0]);


    @staticmethod
    def alarm_arm_request(remote_address, parameters):
        '''
        Arm/disarm alarm on client (from server)
        '''
        if parameters[0] == "True":
            GLOBAL.arm(True)
        else:
            GLOBAL.arm(False)
        

    @staticmethod
    def alarm_arm_response(remote_address, parameters):
        '''
        Arm/disarm alarm on client (from server)
        '''
        pass
        

    @staticmethod
    def alarm_arm_error(remote_address, parameters):
        '''
        Arm/disarm alarm on client (from server)
        '''
        steelsquid_utils.shout(parameters[0]);


    @staticmethod
    def alarm_siren_request(remote_address, parameters):
        '''
        Activate/deaqctivate siren on client (from server)
        '''
        if parameters[0] == "True":
            GLOBAL.siren(True)
        else:
            GLOBAL.siren(False)
        

    @staticmethod
    def alarm_siren_response(remote_address, parameters):
        '''
        ctivate/deaqctivate siren on client (from server)
        '''
        pass
        

    @staticmethod
    def alarm_siren_error(remote_address, parameters):
        '''
        ctivate/deaqctivate siren on client (from server)
        '''
        steelsquid_utils.shout(parameters[0]);


    @staticmethod
    def alarm_lamp_request(remote_address, parameters):
        '''
        Activate/deaqctivate lamp on client (from server)
        '''
        if parameters[0] == "True":
            GLOBAL.lamp(True)
        else:
            GLOBAL.lamp(False)
        

    @staticmethod
    def alarm_lamp_response(remote_address, parameters):
        '''
        ctivate/deaqctivate lamp on client (from server)
        '''
        pass
        

    @staticmethod
    def alarm_lamp_error(remote_address, parameters):
        '''
        ctivate/deaqctivate lamp on client (from server)
        '''
        steelsquid_utils.shout(parameters[0]);
    
    
class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''
    # Is siren on
    is_siren_on = False

    # Is lamp on
    is_lamp_on = False

    # Motion detected
    motion_detected = False

    # Alarm is triggered
    alarm_triggered = False

    # Calculate when alarm should go off
    counter=0
    last_move = 0
    last_trigger = datetime.now() - timedelta(days =1 )

    # If this is a server calculate if to send alarm to clients
    last_trigger_clients = datetime.now() - timedelta(days =1 )

    # Lightlevel from PCF8591 (YL-40)
    light_level = None

    # Temperature from HDC1008
    temperature = None

    # Lightlevel from HDC1008
    humidity = None

    # Status from connected clients (if this is a server)
    # Is a dict with all clients and every object in the dict is a list of statuses from that client
    clients_status = {}

    ever2second = True
    
    @staticmethod
    def get_statuses():
        '''
        Get status of this device and also status on all connected clients
        '''
        statuses = []
        if steelsquid_utils.get_flag("alarm") and steelsquid_utils.get_flag("socket_server"):
            # Status of this local device
            ip = steelsquid_utils.network_ip()
            name = steelsquid_utils.execute_system_command(['hostname'])[0]
            armed = steelsquid_utils.get_flag("alarm_security")
            statuses.append(ip)
            statuses.append(name)
            statuses.append(armed)
            statuses.append(GLOBAL.alarm_triggered)
            statuses.append(GLOBAL.motion_detected)
            statuses.append(GLOBAL.is_siren_on)
            statuses.append(GLOBAL.is_lamp_on)
            statuses.append(GLOBAL.light_level)
            statuses.append(GLOBAL.temperature)
            statuses.append(GLOBAL.humidity)
            try:
                urllib.urlretrieve("http://"+ip+":8080/?action=snapshot", "/opt/steelsquid/web/snapshots/"+ip+".jpg")
            except:
                try:
                    os.remove("/opt/steelsquid/web/snapshots/"+ip+".jpg")
                except:
                    pass
            
            # Get status from all connected clients
            for key in GLOBAL.clients_status:
                client = GLOBAL.clients_status[key]
                statuses.append(key)
                statuses.extend(client)
                try:
                    urllib.urlretrieve("http://"+key+":8080/?action=snapshot", "/opt/steelsquid/web/snapshots/"+key+".jpg")
                except:
                    try:
                        os.remove("/opt/steelsquid/web/snapshots/"+key+".jpg")
                    except:
                        pass
                    
        return statuses
        
        
    @staticmethod
    def on_motion(pin, status):
        '''
        Execute on motion
        '''
        GLOBAL.motion_detected = status 
        if steelsquid_utils.get_flag("alarm_security"):
            nr_of_movments = int(steelsquid_utils.get_parameter("alarm_security_movments"))
            movments_under_time = int(steelsquid_utils.get_parameter("alarm_security_movments_seconds"))
            alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
            alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
            activate_siren = steelsquid_utils.get_flag("alarm_security_activate_siren")
            alarm_security_send_mail = steelsquid_utils.get_flag("alarm_security_send_mail")
            if status==True and GLOBAL.alarm_triggered==False:
                #Activate IR-lamp for 2 minute
                if not GLOBAL.lamp():
                    GLOBAL.lamp(True)
                    steelsquid_utils.execute_delay(120, GLOBAL.lamp, ((False),))
                now = datetime.now()
                delta = now - GLOBAL.last_trigger
                if delta.total_seconds() > alarm_security_wait:
                    if GLOBAL.last_move == 0:
                        GLOBAL.last_move = datetime.now()                
                    delta = now - GLOBAL.last_move
                    if delta.total_seconds()<movments_under_time:
                        GLOBAL.counter=GLOBAL.counter+1
                    else:
                        GLOBAL.counter=0
                        GLOBAL.last_move = 0
                    if GLOBAL.counter>=nr_of_movments:
                        GLOBAL.alarm_triggered=True
                        GLOBAL.last_trigger=datetime.now() 
                        if activate_siren:
                            GLOBAL.siren(True)
                        if alarm_security_send_mail:
                            GLOBAL.send_mail()
                        steelsquid_utils.execute_delay(alarm_for_seconds, GLOBAL.turn_off_alarm, None)

                    
    @staticmethod
    def send_mail():
        '''
        Send alarm mail
        '''
        try:
            urllib.urlretrieve("http://localhost:8080/?action=snapshot", "/tmp/snapshot1.jpg")
            time.sleep(1.5)
            urllib.urlretrieve("http://localhost:8080/?action=snapshot", "/tmp/snapshot2.jpg")
            time.sleep(1.5)
            urllib.urlretrieve("http://localhost:8080/?action=snapshot", "/tmp/snapshot3.jpg")
            ip = steelsquid_utils.network_ip_test_all()
            if steelsquid_utils.get_flag("web_https"):
                link = 'https://'+ip+'/utils?alarm'
            else:
                link = 'http://'+ip+'/utils?alarm'
            steelsquid_utils.notify("Security alarm from: " + os.popen("hostname").read()+"\n"+link, ["/tmp/snapshot1.jpg", "/tmp/snapshot2.jpg", "/tmp/snapshot3.jpg"])
        except:
            steelsquid_utils.shout()


    @staticmethod
    def turn_off_alarm():
        '''
        Turn off a activated alarm
        '''
        GLOBAL.siren(False)
        GLOBAL.alarm_triggered=False
        GLOBAL.counter=0
        GLOBAL.last_move = 0


    @staticmethod
    def arm(armIt):
        '''
        Turn on and of the alarm
        '''

        if armIt==True:
            steelsquid_utils.set_flag("alarm_security")
        else:
            steelsquid_utils.del_flag("alarm_security")
            GLOBAL.turn_off_alarm()
        

    @staticmethod
    def siren(activate=None):
        '''
        Aktivate the siren and get if it is activated
        '''    
        if activate!=None:
            if activate:
                steelsquid_pi.gpio_set(17, True);
            else:
                steelsquid_pi.gpio_set(17, False);
            GLOBAL.is_siren_on=activate
        return GLOBAL.is_siren_on


    @staticmethod
    def lamp(activate=None):
        '''
        Aktivate the lamp and get if it is activated
        '''    
        if activate!=None:
            if activate:
                steelsquid_pi.gpio_set(22, True);
                steelsquid_pi.gpio_set(27, True);
            else:
                steelsquid_pi.gpio_set(22, False);
                steelsquid_pi.gpio_set(27, False);
            GLOBAL.is_lamp_on=activate
        return GLOBAL.is_lamp_on


    @staticmethod
    def on_remote_alarm():
        '''
        If this clients server or other clients has an alarm
        turn on this device siren
        '''
        if steelsquid_utils.get_flag("alarm_security") and steelsquid_utils.get_flag("alarm_remote_siren"):
            alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
            GLOBAL.siren(True)
            steelsquid_utils.execute_delay(alarm_for_seconds, GLOBAL.siren, ((False),))

    
    
