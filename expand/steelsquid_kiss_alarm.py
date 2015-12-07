#!/usr/bin/python -OO


'''.
This is functionality for my alarm.
Connect different sensors to monitor your house or other thinks.
Also see utils.html, steelsquid_kiss_http_server.py

If function on_enable() exist it will be executed when system starts (boot)
If function on_disable() exist it will be executed when system stops (shutdown)
If function on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
If function on_loop() exist it will execute over and over again untill it return None or -1
If finction on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)

If this is a PIIO board
And if function on_low_bat(voltage) exist it will execute when voltage is to low.
And if function on_button(button_nr) exist it will execute when button 1 to 6 is clicken on the PIIO board
And if function on_button_info() exist it will execute when info button clicken on the PIIO board
And if function on_switch(dip_nr, status) exist it will execute when switch 1 to 6 is is changed on the PIIO board

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-12-26 Created
'''


import steelsquid_utils
import steelsquid_event
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


# Is this enabled (on_enable has executed)
# This is set by the system automaticaly
is_enabled = False

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

# Commands from Alarm Arm app {id, time}
alarm_arm = {}

ever2second = True


def activate():
    '''
    Return True/False if this functionality is to be enabled (execute on_enable)
    return: True/False
    '''    
    return steelsquid_utils.get_flag("rover")


def on_enable():
    '''
    This will execute when system starts
    Do not execute long running stuff here, do it in on_loop...
    '''
    steelsquid_utils.shout("Steelsquid Alarm/Surveillance enabled")
    steelsquid_pi.gpio_event(25, cls.on_motion, resistor=steelsquid_pi.PULL_NONE)
    
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
    

def on_disable():
    '''
    This will execute when system stops
    Do not execute long running stuff here
    '''
    pass
    
    
def on_loop():
    '''
    This will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again imediately.
    '''    
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second

    # Try to read sensors
    try:
        light_level = steelsquid_pi.yl40_light_level();
    except:
        pass
    try:
        temp, hum = steelsquid_pi.hdc1008();
        temperature = round(temp, 1)
        humidity = round(hum, 1)
    except:
        pass
    try:
        alarm_light_acivate = int(steelsquid_utils.get_parameter("alarm_light_acivate"));
        if alarm_light_acivate != -1:
            if int(light_level)<alarm_light_acivate:
                lamp(True)
            else:
                lamp(False)
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
                motion_detected = motion_detected
                statuses.append(name)
                statuses.append(armed)
                statuses.append(alarm_triggered)
                statuses.append(motion_detected)
                statuses.append(is_siren_on)
                statuses.append(is_lamp_on)
                statuses.append(light_level)
                statuses.append(temperature)
                statuses.append(humidity)
                steelsquid_kiss_global.socket_connection.send_request("alarm_push", statuses)
            except:
                steelsquid_utils.shout()
        elif steelsquid_utils.get_flag("socket_server"):
            #Check if client still is connected, of not remove from status list
            for k in clients_status.keys():
                if k not in steelsquid_kiss_global.socket_connection.get_connected_ip_numbers():
                    del clients_status[k]
            #Check if to send alarm to clients
            alarm_triggered = alarm_triggered
            if not alarm_triggered:
                for key in clients_status:
                    client = clients_status[key]
                    alarm_triggered = steelsquid_utils.to_boolean(client[2])
                    if alarm_triggered:
                        break
            if alarm_triggered:
                alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
                now = datetime.now()
                delta = now - last_trigger_clients
                if delta.total_seconds() > alarm_security_wait:
                    if not alarm_triggered:
                        on_remote_alarm()
                    last_trigger_clients=datetime.now() 
                    steelsquid_kiss_global.socket_connection.send_request("alarm_remote_alarm", [])
        if steelsquid_utils.get_flag("alarm_app"):
            for client_id in alarm_arm.keys():
                last_timestamp = alarm_arm[client_id]
                now = datetime.now()
                delta = now - last_timestamp
                if delta.total_seconds() > 600:
                    alarm_arm.pop(client_id, None)
            if len(alarm_arm)==0:
                if not steelsquid_utils.get_flag("alarm_security"):
                    steelsquid_kiss_global.Alarm.arm(True)
                    steelsquid_kiss_global.socket_connection.send_request("alarm_arm", ["True"])
            else:
                if steelsquid_utils.get_flag("alarm_security"):
                    steelsquid_kiss_global.Alarm.arm(False)
                    steelsquid_kiss_global.socket_connection.send_request("alarm_arm", ["False"])
    return 1


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
    
    
def on_event_data(key, value):
    '''
    This will fire when data is changed with steelsquid_kiss_global.set_event_data(key, value)
    key=The key of the data
    value=The value of the data
    '''    
    pass
    
    
def get_statuses():
    '''
    Get status of this device and also status on all connected clients
    '''
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    statuses = []
    if steelsquid_utils.get_flag("alarm") and steelsquid_utils.get_flag("socket_server"):
        # Status of this local device
        ip = steelsquid_utils.network_ip()
        name = steelsquid_utils.execute_system_command(['hostname'])[0]
        armed = steelsquid_utils.get_flag("alarm_security")
        statuses.append(ip)
        statuses.append(name)
        statuses.append(armed)
        statuses.append(alarm_triggered)
        statuses.append(motion_detected)
        statuses.append(is_siren_on)
        statuses.append(is_lamp_on)
        statuses.append(light_level)
        statuses.append(temperature)
        statuses.append(humidity)
        try:
            urllib.urlretrieve("http://"+ip+":8080/?action=snapshot", "/opt/steelsquid/web/snapshots/"+ip+".jpg")
        except:
            try:
                os.remove("/opt/steelsquid/web/snapshots/"+ip+".jpg")
            except:
                pass
        
        # Get status from all connected clients
        for key in clients_status:
            client = clients_status[key]
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
    
    
def on_motion(pin, status):
    '''
    Execute on motion
    '''
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    motion_detected = status 
    if steelsquid_utils.get_flag("alarm_security"):
        nr_of_movments = int(steelsquid_utils.get_parameter("alarm_security_movments"))
        movments_under_time = int(steelsquid_utils.get_parameter("alarm_security_movments_seconds"))
        alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
        alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
        activate_siren = steelsquid_utils.get_flag("alarm_security_activate_siren")
        alarm_security_send_mail = steelsquid_utils.get_flag("alarm_security_send_mail")
        if status==True and alarm_triggered==False:
            #Activate IR-lamp for 1 minute
            if not lamp():
                lamp(True)
                steelsquid_utils.execute_delay(120, lamp, ((False),))
            now = datetime.now()
            delta = now - last_trigger
            if delta.total_seconds() > alarm_security_wait:
                if last_move == 0:
                    last_move = datetime.now()                
                delta = now - last_move
                if delta.total_seconds()<movments_under_time:
                    counter=counter+1
                else:
                    counter=0
                    last_move = 0
                if counter>=nr_of_movments:
                    alarm_triggered=True
                    last_trigger=datetime.now() 
                    if activate_siren:
                        siren(True)
                    if alarm_security_send_mail:
                        send_mail()
                    steelsquid_utils.execute_delay(alarm_for_seconds, turn_off_alarm, None)

                
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


def turn_off_alarm():
    '''
    Turn off a activated alarm
    '''
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    siren(False)
    alarm_triggered=False
    counter=0
    last_move = 0


def arm(armIt):
    '''
    Turn on and of the alarm
    '''
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    if armIt==True:
        steelsquid_utils.set_flag("alarm_security")
    else:
        steelsquid_utils.del_flag("alarm_security")
        turn_off_alarm()
    

def siren(activate=None):
    '''
    Aktivate the siren and get if it is activated
    '''    
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    if activate!=None:
        if activate:
            steelsquid_pi.gpio_set(17, True);
        else:
            steelsquid_pi.gpio_set(17, False);
        is_siren_on=activate
    return is_siren_on


def lamp(activate=None):
    '''
    Aktivate the lamp and get if it is activated
    '''    
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    if activate!=None:
        if activate:
            steelsquid_pi.gpio_set(22, True);
            steelsquid_pi.gpio_set(27, True);
        else:
            steelsquid_pi.gpio_set(22, False);
            steelsquid_pi.gpio_set(27, False);
        is_lamp_on=activate
    return is_lamp_on


def on_remote_alarm():
    '''
    If this clients server or other clients has an alarm
    turn on this device siren
    '''
    global is_enabled
    global is_siren_on
    global is_lamp_on
    global motion_detected
    global alarm_triggered 
    global counter
    global last_move
    global last_trigger
    global last_trigger_clients
    global light_level
    global temperature
    global humidity 
    global clients_status
    global alarm_arm 
    global ever2second
    if steelsquid_utils.get_flag("alarm_security") and steelsquid_utils.get_flag("alarm_remote_siren"):
        alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
        siren(True)
        steelsquid_utils.execute_delay(alarm_for_seconds, siren, ((False),))

    
    
