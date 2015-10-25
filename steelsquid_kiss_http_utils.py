#!/usr/bin/python -OO


'''
Do not execute long running stuff or the system won't start properly.
This will always execute with root privilege.
The web-server will be started by steelsquid_boot.py
See steelsquid-kiss-http-server.py for example

Use this to expand the capabilities of the webserver.
Handle stuff in utils.html
-Camera streaming
-Alarm
-Rover

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_kiss_http_server
import steelsquid_utils
import steelsquid_event
import steelsquid_kiss_global
import subprocess
from subprocess import Popen, PIPE, STDOUT


class SteelsquidKissHttpServerUtils(steelsquid_kiss_http_server.SteelsquidKissHttpServer):
    
    __slots__ = []

    def __init__(self, port, root, authorization, only_localhost, local_web_password, use_https):
        super(SteelsquidKissHttpServerUtils, self).__init__(port, root, authorization, only_localhost, local_web_password, use_https)


    def stream(self, session_id, parameters):
        '''
        Enable or disable streamimg
        '''
        if len(parameters) > 0:
            if parameters[0] == "usb":
                proc=Popen(['steelsquid', 'stream-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("stream")
                steelsquid_utils.del_flag("stream-pi")
            elif parameters[0] == "pi":
                proc=Popen(['steelsquid', 'stream-pi-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("stream")
                steelsquid_utils.set_flag("stream-pi")
                steelsquid_utils.set_flag("camera")
            else:
                proc=Popen(['steelsquid', 'stream-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("stream")
                steelsquid_utils.del_flag("stream-pi")
        if steelsquid_utils.get_flag("stream"):
            return "usb"
        elif steelsquid_utils.get_flag("stream-pi"):
            return "pi"
        else:
            return "false"


    def stream_frames(self, session_id, parameters):
        '''
        Enable or disable streamimg
        '''
        if not steelsquid_utils.has_parameter("stream_frames"):
            steelsquid_utils.set_parameter("stream_frames", "4")
        if len(parameters) > 0:
            steelsquid_utils.set_parameter("stream_frames", parameters[0])
            return [steelsquid_utils.get_parameter("stream_frames"), "Settings saved"]
        else:
            return [steelsquid_utils.get_parameter("stream_frames"), ""]


    def alarm(self, session_id, parameters):
        '''
        Enable or disable alarm
        '''
        if len(parameters) > 0:
            if parameters[0] == "true":
                proc=Popen(['steelsquid', 'alarm-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("alarm")
            else:
                proc=Popen(['steelsquid', 'alarm-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("alarm")
        if steelsquid_utils.get_flag("alarm"):
            return "true"
        else:
            return "false"


    def alarm_status(self, session_id, parameters):
        '''
        Status of alarm
        '''
        if steelsquid_kiss_global.Alarm.siren():
            siren="true"
        else:
            siren="false"
        if steelsquid_kiss_global.Alarm.lamp():
            lamp="true"
        else:
            lamp="false"
        if steelsquid_kiss_global.Alarm.motion_detected:
            motion="true"
        else:
            motion="false"
        if steelsquid_kiss_global.Alarm.alarm_triggered:
            alarm_t="true"
        else:
            alarm_t="false"
        if steelsquid_utils.get_flag("alarm_security"):
            alarm_sec="true"
        else:
            alarm_sec="false"
        light_level = "---"
        if steelsquid_kiss_global.Alarm.light_level!=None:
            light_level = str(steelsquid_kiss_global.Alarm.light_level)
        temperature = "---"
        if steelsquid_kiss_global.Alarm.temperature!=None:
            temperature = str(steelsquid_kiss_global.Alarm.temperature)
        humidity = "---"
        if steelsquid_kiss_global.Alarm.humidity!=None:
            humidity = str(steelsquid_kiss_global.Alarm.humidity)
        return [motion, siren, lamp, alarm_t, alarm_sec, light_level, temperature, humidity]


    def alarm_settings(self, session_id, parameters):
        '''
        Settings of alarm
        '''
        is_saved=False
        if len(parameters) > 0:
            if int(parameters[2]) >= int(parameters[3]):
                raise Exception("Alarm time must be smaller than alarm wait!")
                alarm_light_acivate
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


    def alarm_arm(self, session_id, parameters):
        '''
        Settings of alarm
        '''
        if len(parameters) > 0:
            if parameters[0]=="true":
                steelsquid_kiss_global.Alarm.arm(True)
            else:
                steelsquid_kiss_global.Alarm.arm(False)
        return [steelsquid_utils.get_flag("alarm_security")]


    def alarm_client_set(self, session_id, parameters):
        '''
        Set status of client that is connected to this server
        '''
        if len(parameters)==1:
            if parameters[0] == "True":
                steelsquid_kiss_global.Alarm.arm(True)
            else:
                steelsquid_kiss_global.Alarm.arm(False)
            steelsquid_kiss_global.socket_connection.send_request("alarm_client_set", parameters)
        else:
            if parameters[0]==steelsquid_utils.network_ip():
                if parameters[1] == "True":
                    steelsquid_kiss_global.Alarm.arm(True)
                else:
                    steelsquid_kiss_global.Alarm.arm(False)
            else:
                steelsquid_kiss_global.socket_connection.send_request("alarm_client_set", parameters[1:], parameters[0])


    def alarm_arm(self, session_id, parameters):
        '''
        Settings of alarm
        '''
        if len(parameters) > 0:
            if parameters[0]=="true":
                steelsquid_kiss_global.Alarm.arm(True)
            else:
                steelsquid_kiss_global.Alarm.arm(False)
        return [steelsquid_utils.get_flag("alarm_security")]



    def alarm_siren(self, session_id, parameters):
        '''
        Aktivate/deactiva siren
        '''
        if parameters[0] == "true":
            steelsquid_kiss_global.Alarm.siren(True)
            return "Siren activated"
        else:
            steelsquid_kiss_global.Alarm.siren(False)
            return "Siren dectivated"


    def alarm_lamp(self, session_id, parameters):
        '''
        Aktivate/deactiva the lamp
        '''
        if parameters[0] == "true":
            steelsquid_kiss_global.Alarm.lamp(True)
            return "The lamp is on"
        else:
            steelsquid_kiss_global.Alarm.lamp(False)
            return "The lamp is off"


    def alarm_server(self, session_id, parameters):
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


    def alarm_server_statuses(self, session_id, parameters):
        '''
        Get all statuses from this server and connected clients
        '''
        return steelsquid_kiss_global.Alarm.get_statuses()


    def rover_info(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.info()


    def rover_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'rover-on']) 
        return steelsquid_utils.get_flag("rover")


    def rover_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'rover-off']) 
        return steelsquid_utils.get_flag("rover")

    def rover_light(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.light()


    def rover_alarm(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.alarm()


    def rover_tilt(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_io
        if parameters[0]=="True":
            steelsquid_kiss_global.Rover.tilt(True)
        else:
            steelsquid_kiss_global.Rover.tilt(False)
            

    def rover_stop(self, session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(0, 0)


    def rover_left(self, session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(-40, 40)


    def rover_right(self, session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(40, -40)


    def rover_forward(self, session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(40, 40)


    def rover_backward(self, session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(-40, -40)
