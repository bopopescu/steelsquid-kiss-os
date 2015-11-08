#!/usr/bin/python -OO


'''
Global stuff for steelsquid kiss os
Reach the http server and Socket connection.
I also add some extra stuff here like Rover, IO and alarm

Use this to add functionality that my be used from different part of the system... example http server and socket server...

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import time
from datetime import datetime
from datetime import timedelta
import os
import urllib
import thread
import sys
import steelsquid_kiss_global


# The socket connection, if enabled (not enabled = None)
# Flag: socket_server
# Parameter: socket_client
socket_connection = None


# The http webserver, if enabled (not enabled = None)
# Flag: web
http_server = None


class Alarm(object):
    '''
    Fuctionality for my rover controller
    Also see utils.html, steelsquid_kiss_http_server.py, steelsquid_kiss_socket_connection.py
    '''
    
    # Is the alarm functionality enabled
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
    
    @classmethod
    def enable(cls):
        '''
        Enable the alarm functionality (this is set by steelsquid_boot)
        Flag: alarm
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
        # Execute this every second
        steelsquid_event.subscribe_to_event("second", cls.on_every_second, None, False)
        
        
    @classmethod
    def on_every_second(cls, args, para):
        '''
        Read lightlevel, temperature and humidity in background every second
        Also if this is a client, send status to server.
        '''
        # Try to read sensors
        try:
            cls.light_level = steelsquid_pi.yl40_light_level();
        except:
            pass
        try:
            temp, hum = steelsquid_pi.hdc1008();
            cls.temperature = round(temp, 1)
            cls.humidity = round(hum, 1)
        except:
            pass
        try:
            alarm_light_acivate = int(steelsquid_utils.get_parameter("alarm_light_acivate"));
            if alarm_light_acivate != -1:
                if int(cls.light_level)<alarm_light_acivate:
                    cls.lamp(True)
                else:
                    cls.lamp(False)
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
                    motion_detected = cls.motion_detected
                    statuses.append(name)
                    statuses.append(armed)
                    statuses.append(cls.alarm_triggered)
                    statuses.append(cls.motion_detected)
                    statuses.append(cls.is_siren_on)
                    statuses.append(cls.is_lamp_on)
                    statuses.append(cls.light_level)
                    statuses.append(cls.temperature)
                    statuses.append(cls.humidity)
                    steelsquid_kiss_global.socket_connection.send_request("alarm_push", statuses)
                except:
                    steelsquid_utils.shout()
            elif steelsquid_utils.get_flag("socket_server"):
                #Check if client still is connected, of not remove from status list
                for k in cls.clients_status.keys():
                    if k not in steelsquid_kiss_global.socket_connection.get_connected_ip_numbers():
                        del cls.clients_status[k]
                #Check if to send alarm to clients
                alarm_triggered = cls.alarm_triggered
                if not alarm_triggered:
                    for key in cls.clients_status:
                        client = cls.clients_status[key]
                        alarm_triggered = steelsquid_utils.to_boolean(client[2])
                        if alarm_triggered:
                            break
                if alarm_triggered:
                    alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
                    now = datetime.now()
                    delta = now - cls.last_trigger_clients
                    if delta.total_seconds() > alarm_security_wait:
                        if not cls.alarm_triggered:
                            cls.on_remote_alarm()
                        cls.last_trigger_clients=datetime.now() 
                        steelsquid_kiss_global.socket_connection.send_request("alarm_remote_alarm", [])
            if steelsquid_utils.get_flag("alarm_app"):
                for client_id in cls.alarm_arm.keys():
                    last_timestamp = cls.alarm_arm[client_id]
                    now = datetime.now()
                    delta = now - last_timestamp
                    if delta.total_seconds() > 600:
                        cls.alarm_arm.pop(client_id, None)
                if len(cls.alarm_arm)==0:
                    if not steelsquid_utils.get_flag("alarm_security"):
                        steelsquid_kiss_global.Alarm.arm(True)
                        steelsquid_kiss_global.socket_connection.send_request("alarm_arm", ["True"])
                else:
                    if steelsquid_utils.get_flag("alarm_security"):
                        steelsquid_kiss_global.Alarm.arm(False)
                        steelsquid_kiss_global.socket_connection.send_request("alarm_arm", ["False"])

                
    @classmethod
    def get_statuses(cls):
        '''
        Get status of this device and also status on all connected clients
        '''
        statuses = []
        if steelsquid_utils.get_flag("alarm") and steelsquid_utils.get_flag("socket_server"):
            # Status of this local device
            ip = steelsquid_utils.network_ip()
            name = steelsquid_utils.execute_system_command(['hostname'])[0]
            armed = steelsquid_utils.get_flag("alarm_security")
            motion_detected = cls.motion_detected
            statuses.append(ip)
            statuses.append(name)
            statuses.append(armed)
            statuses.append(cls.alarm_triggered)
            statuses.append(cls.motion_detected)
            statuses.append(cls.is_siren_on)
            statuses.append(cls.is_lamp_on)
            statuses.append(cls.light_level)
            statuses.append(cls.temperature)
            statuses.append(cls.humidity)
            try:
                urllib.urlretrieve("http://"+ip+":8080/?action=snapshot", "/opt/steelsquid/web/snapshots/"+ip+".jpg")
            except:
                try:
                    os.remove("/opt/steelsquid/web/snapshots/"+ip+".jpg")
                except:
                    pass
            
            # Get status from all connected clients
            for key in cls.clients_status:
                client = cls.clients_status[key]
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
        
        
    @classmethod
    def on_motion(cls, pin, status):
        '''
        Execute on motion
        '''
        cls.motion_detected = status 
        if steelsquid_utils.get_flag("alarm_security"):
            nr_of_movments = int(steelsquid_utils.get_parameter("alarm_security_movments"))
            movments_under_time = int(steelsquid_utils.get_parameter("alarm_security_movments_seconds"))
            alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
            alarm_security_wait = int(steelsquid_utils.get_parameter("alarm_security_wait"))
            activate_siren = steelsquid_utils.get_flag("alarm_security_activate_siren")
            alarm_security_send_mail = steelsquid_utils.get_flag("alarm_security_send_mail")
            if status==True and cls.alarm_triggered==False:
                now = datetime.now()
                delta = now - cls.last_trigger
                if delta.total_seconds() > alarm_security_wait:
                    if cls.last_move == 0:
                        cls.last_move = datetime.now()                
                    delta = now - cls.last_move
                    if delta.total_seconds()<movments_under_time:
                        cls.counter=cls.counter+1
                    else:
                        cls.counter=0
                        cls.last_move = 0
                    if cls.counter>=nr_of_movments:
                        cls.alarm_triggered=True
                        cls.last_trigger=datetime.now() 
                        if activate_siren:
                            cls.siren(True)
                        if alarm_security_send_mail:
                            cls.send_mail()
                        steelsquid_utils.execute_delay(alarm_for_seconds, cls.turn_off_alarm, None)
                    
    @classmethod
    def send_mail(cls):
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

    @classmethod
    def turn_off_alarm(cls):
        '''
        Turn off a activated alarm
        '''
        cls.siren(False)
        cls.alarm_triggered=False
        cls.counter=0
        cls.last_move = 0

    @classmethod
    def arm(cls, armIt):
        '''
        Turn on and of the alarm
        '''
        if armIt==True:
            steelsquid_utils.set_flag("alarm_security")
        else:
            steelsquid_utils.del_flag("alarm_security")
            cls.turn_off_alarm()
        

    @classmethod
    def siren(cls, activate=None):
        '''
        Aktivate the siren and get if it is activated
        '''    
        if activate!=None:
            if activate:
                steelsquid_pi.gpio_set(17, True);
            else:
                steelsquid_pi.gpio_set(17, False);
            cls.is_siren_on=activate
        return cls.is_siren_on

    @classmethod
    def lamp(cls, activate=None):
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
            cls.is_lamp_on=activate
        return cls.is_lamp_on


    @classmethod
    def on_remote_alarm(cls):
        '''
        If this clients server or other clients has an alarm
        turn on this device siren
        '''
        if steelsquid_utils.get_flag("alarm_security") and steelsquid_utils.get_flag("alarm_remote_siren"):
            alarm_for_seconds = int(steelsquid_utils.get_parameter("alarm_security_seconds"))
            cls.siren(True)
            steelsquid_utils.execute_delay(alarm_for_seconds, cls.siren, ((False),))


class Rover(object):
    '''
    Fuctionality for my rover controller
    Also see utils.html, steelsquid_kiss_http_server.py, steelsquid_kiss_socket_connection.py
    '''

    # Is the rover functionality enabled
    is_enabled = False
    
    @classmethod
    def enable(cls):
        '''
        Enable the rover functionality (this is set by steelsquid_boot)
        Flag: rover
        '''    
        import steelsquid_piio
        steelsquid_utils.shout("Steelsquid Rover enabled")
        steelsquid_piio.servo_position = steelsquid_utils.get_parameter("servo_position", steelsquid_piio.servo_position)
        steelsquid_piio.servo_position_max = steelsquid_utils.get_parameter("servo_position_max", steelsquid_piio.servo_position_max)
        steelsquid_piio.servo_position_min = steelsquid_utils.get_parameter("servo_position_min", steelsquid_piio.servo_position_min)
        steelsquid_piio.motor_forward = steelsquid_utils.get_parameter("motor_forward", steelsquid_piio.motor_forward)
        steelsquid_piio.motor_backward = steelsquid_utils.get_parameter("motor_backward", steelsquid_piio.motor_backward)
        steelsquid_piio.servo(1, steelsquid_piio.servo_position)       
        steelsquid_event.subscribe_to_event("second", cls.on_second, ())         
        cls.is_enabled=True

    @classmethod
    def on_second(cls, args, para):
        '''
        If no signal after 1 second stop the rover. (connection lost!!!)
        '''
        import steelsquid_piio
        now = time.time()*1000
        if now - steelsquid_piio.trex_motor_last_change() > 1000:
            try:
                steelsquid_piio.trex_motor(0,0)
            except:
                pass
                
    @classmethod
    def info(cls):
        '''
        Get info on rover functionality
        '''
        enabled = steelsquid_utils.get_flag("rover")
        if enabled:
            import steelsquid_piio
            battery_voltage, _, _, _, _, _, _, _, _ = steelsquid_piio.trex_status()
            battery_voltage = float(battery_voltage)/100
            return [True, battery_voltage, steelsquid_piio.gpio_22_xv_toggle_current(2), steelsquid_piio.gpio_22_xv_toggle_current(1), steelsquid_piio.servo_position, steelsquid_piio.servo_position_min, steelsquid_piio.servo_position_max, steelsquid_piio.motor_backward, steelsquid_piio.motor_forward]
        else:
            return False


    @classmethod
    def light(cls):
        '''
        Light on and off (toggle)
        '''
        import steelsquid_piio
        status = steelsquid_piio.gpio_22_xv_toggle(2)
        steelsquid_piio.gpio_22_xv(3, status)
        return status


    @classmethod
    def alarm(cls):
        '''
        Alarm on and off (toggle)
        '''
        import steelsquid_piio
        return steelsquid_piio.gpio_22_xv_toggle(1)


    @classmethod
    def tilt(cls, value):
        '''
        Tilt the camera
        '''
        import steelsquid_piio
        if value == True:
            steelsquid_piio.servo_move(1, 10)
        elif value == False:
            steelsquid_piio.servo_move(1, -10)
        else:
            value = int(value)
            steelsquid_piio.servo(1, value)


    @classmethod
    def drive(cls, left, right):
        '''
        Tilt the camera
        '''
        import steelsquid_piio
        left = int(left)
        right = int(right)
        steelsquid_piio.trex_motor(left, right)


class PIIO(object):
    '''
    Fuctionality for my Steelsquid PIIO board
    Also see steelquid_io.py
    '''

    # Is the PIIO board functionality enabled
    is_enabled = False
    
    # Last voltage read
    last_voltage = 0
    
    # Last voltage read
    last_print_voltage = 0

    @classmethod
    def enable(cls):
        '''
        Enable the IO board functionality (this is done by steelsquid_boot)
        Flag: io
        '''    
        import steelsquid_piio
        steelsquid_utils.shout("Steelsquid IO board enabled")
        steelsquid_piio.button(1, cls.on_button_1)
        steelsquid_piio.button(2, cls.on_button_2)
        steelsquid_piio.button(3, cls.on_button_3)
        steelsquid_piio.button(4, cls.on_button_4)
        steelsquid_piio.button(5, cls.on_button_5)
        steelsquid_piio.button(6, cls.on_button_6)
        steelsquid_piio.dip(1, cls.on_dip_1)
        steelsquid_piio.dip(2, cls.on_dip_2)
        steelsquid_piio.dip(3, cls.on_dip_3)
        steelsquid_piio.dip(4, cls.on_dip_4)
        steelsquid_piio.dip(5, cls.on_dip_5)
        steelsquid_piio.dip(6, cls.on_dip_6)
        steelsquid_piio.button_info(cls.on_button_info)
        steelsquid_piio.button_power_off(cls.on_button_power_off)
        if steelsquid_utils.get_flag("development"):
            steelsquid_event.subscribe_to_event("button", cls.dev_button, ())
            steelsquid_event.subscribe_to_event("dip", cls.dev_dip, ())
        if not steelsquid_utils.get_flag("no_lcd_voltage"):
            steelsquid_event.subscribe_to_event("seconds", cls.on_read_voltage, ())
        steelsquid_event.subscribe_to_event("poweroff", cls.on_poweroff, ())
        cls.is_enabled=True


    @classmethod
    def on_poweroff(cls, args, para):
        '''
        Power off the system
        '''
        import steelsquid_piio
        steelsquid_piio.power_off()

    @classmethod
    def on_read_voltage(cls, args, para):
        '''
        Read voltage and display on LCD
        '''
        import steelsquid_piio
        import datetime
        new_voltage = steelsquid_piio.voltage()
        if new_voltage != cls.last_voltage:
            if abs(new_voltage - cls.last_print_voltage)>=0.1:
                if cls.last_print_voltage == 0:
                    steelsquid_utils.shout("Voltage is: " + str(new_voltage), to_lcd=False)
                else:
                    steelsquid_utils.shout("Voltage changed: " + str(new_voltage), to_lcd=False)
                cls.last_print_voltage = new_voltage
            cls.last_voltage = new_voltage
            last = steelsquid_pi.lcd_last_text
            if last != None and "VOLTAGE: " in last:
                i1 = last.find("VOLTAGE: ", 0) + 9
                if i1 != -1:
                    i2 = last.find("\n", i1)
                    if i2 == -1:
                        news = last[:i1]+str(new_voltage)
                    else:
                        news = last[:i1]+str(new_voltage)+last[i2:]
                    steelsquid_piio.lcd_write(news, number_of_seconds = 0)
                
                    
    @classmethod
    def dev_button(cls, args, para):
        '''
        In development mode shout if the button is pressed
        '''    
        import steelsquid_piio
        bu = str(para[0])
        steelsquid_utils.shout_time("Button " + bu + " pressed!")

    @classmethod
    def dev_dip(cls, args, para):
        '''
        In development mode shout if the DIP is changed
        '''    
        import steelsquid_piio
        steelsquid_utils.shout_time("DIP " + str(para[0]) +": "+ str(para[1]))

    @classmethod
    def on_button_power_off(cls, address, pin):
        '''
        If shutdown button is clicked
        '''    
        import steelsquid_piio
        steelsquid_piio.power_off()

    @classmethod
    def on_button_info(cls, address, pin):
        '''
        If info button is clicked
        '''    
        import steelsquid_piio
        steelsquid_piio.led_ok_flash(None)
        steelsquid_event.broadcast_event("network")

    @classmethod
    def on_button_1(cls, address, pin):
        '''
        If the 1 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [1])

    @classmethod
    def on_button_2(cls, address, pin):
        '''
        If the 2 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [2])

    @classmethod
    def on_button_3(cls, address, pin):
        '''
        If the 3 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [3])

    @classmethod
    def on_button_4(cls, address, pin):
        '''
        If the 4 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [4])

    @classmethod
    def on_button_5(cls, address, pin):
        '''
        If the 5 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [5])

    @classmethod
    def on_button_6(cls, address, pin):
        '''
        If the 6 button is pressed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("button", [6])

    @classmethod
    def on_dip_1(cls, address, pin, status):
        '''
        If DIP 1 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [1, status])

    @classmethod
    def on_dip_2(cls, address, pin, status):
        '''
        If DIP 2 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [2, status])

    @classmethod
    def on_dip_3(cls, address, pin, status):
        '''
        If DIP 3 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [3, status])

    @classmethod
    def on_dip_4(cls, address, pin, status):
        '''
        If DIP 4 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [4, status])

    @classmethod
    def on_dip_5(cls, address, pin, status):
        '''
        If DIP 5 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [5, status])

    @classmethod
    def on_dip_6(cls, address, pin, status):
        '''
        If DIP 6 changed
        '''    
        import steelsquid_piio
        steelsquid_event.broadcast_event("dip", [6, status])
