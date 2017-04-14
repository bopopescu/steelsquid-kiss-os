#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''.
My 6wd drive rover "irrbloss"

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-09-08 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_kiss_global
import steelsquid_nm
import steelsquid_kiss_boot
import time
import stat
import datetime
import thread  
import steelsquid_hmtrlrs
import steelsquid_ht16k33 as lmatrix
import steelsquid_tcp_radio
import math
from decimal import Decimal
import os
from espeak import espeak
import gps
import steelsquid_gstreamer
import steelsquid_gps
import steelsquid_bno0055


# Is this module started
# This is set by the system automatically.
is_started = False


def enable(argument=None):
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
              (execute: steelsquid module XXX on theArgument)
    '''
    # Clear any saved settings for this module
    steelsquid_kiss_global.clear_modules_settings("kiss_irrbloss")
    # Change hostname
    steelsquid_utils.set_hostname("irrbloss")
    # Enable transeiver as client
    steelsquid_kiss_global.radio_hmtrlrs(True)
    # Enable TCP-radio as client
    steelsquid_kiss_global.radio_hmtrlrs(True)
    # Enable tcp radio as client and then listen for command from the host
    steelsquid_kiss_global.radio_tcp(False, steelsquid_utils.network_ip_wan())
    # Change GPIO for transceiver
    steelsquid_utils.set_parameter("hmtrlrs_config_gpio", str(STATIC.gpio_hmtrlrs_config))
    steelsquid_utils.set_parameter("hmtrlrs_reset_gpio", str(STATIC.gpio_hmtrlrs_reset))
    # Enable camera
    steelsquid_utils.execute_system_command_blind(["steelsquid", "camera-on"], wait_for_finish=True)
    # Max volume
    steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)
    steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "100%"], wait_for_finish=True)
    steelsquid_utils.execute_system_command_blind(["alsactl", "store"], wait_for_finish=True)
    


def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    # Enable the automatic print if IP to LCD
    steelsquid_utils.del_flag("no_net_to_lcd")
    # Disable the HM-TRLR-S
    steelsquid_kiss_global.hmtrlrs_status(None)






##############################################################################################################################################################################################
class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''

    # Number of seconds when connection probably is lost 
    connection_lost_timeout = 20

    # Number of seconds when ttop the video and audio stream
    connection_lost_streams = 15
    
    # Help timeout
    help_timeout = 40
    
    # Number of seconds when connection probably is lost 
    # Reboot the rover
    connection_lost_timeout_reboot = 90
    
    # Turn of speeker after this number of idle seconds
    speeker_timeout = 240
        
    # Remote voltages(lipo 3s) 
    remote_voltage_max = 12.6      # 4.2V
    remote_voltage_warning = 10.8  # 3.6V
    remote_voltage_min = 9.6       # 3.2V

    # Rover voltages(lipo 4s)
    rover_voltage_max = 16.8        # 4.2V
    rover_voltage_warning = 14.4    # 3.6V
    rover_voltage_min = 12.8        # 3.2V
    
    # interrup GPIO for mcp23017
    gpio_mcp23017_20_trig = 4

    # GPIO for the HM-TRLR-S
    gpio_hmtrlrs_config = 18
    gpio_hmtrlrs_reset = 23

    # When system start move servo here
    servo_position_tilt_start = 400

    # Max Servo position
    servo_position_tilt_max = 470

    # Min Servo position
    servo_position_tilt_min = 320

    # Max gyro drive straight value
    max_drive_straight = 20









##############################################################################################################################################################################################
class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe to enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''

    








##############################################################################################################################################################################################
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
      _persistent_off = True
    This is usefull under development if you wan to test different values when you restart the module,
    To sum up: Variables in class SETTINGS that has value: Boolean, Array, Integer, Float, String will be will be persistent.
    '''
    
    # This will tell the system not to save and read the settings from disk
    _persistent_off = False
    
    # 1=radio 2=wifi 3=3g4g
    control = 1
        
    # IP-number for this remote control
    control_ip = ""
        
    # IP-number were to send the video stream
    video_ip = ""
        
    # IP-number were to send the audio stream
    audio_ip = ""

    # Width/height for the stream
    width = "800"
    height = "480"

    # Width for the stream
    fps = "20"

    # Bitrate for the stream
    bitrate = "800000"

    # TCP for video stream
    tcp_video = False 
    
    # use low light settings for camera
    low_light = False       







##############################################################################################################################################################################################
class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if module is enabled
    You may remove the methods you do not want to use
    on_start() 
        Will be executed when system starts (boot)
    on_stop() 
        Will be executed when system stops (shutdown)
    on_network(status, wired, usb, wifi_ssid, wifi, wan) 
        Will be execute on network up or down
    on_vpn(status, name, ip) 
        This will fire when a VPN connection is enabled/disabled.
    on_bluetooth(status) 
        Will be execute on bluetooth enabled
    on_mount(type_of_mount, remote, local) 
        This will fire when USB, Samba(windows share) or SSH is mounted.
    on_umount(type_of_mount, remote, local)
        This will fire when USB, Samba(windows share) or SSH is unmounted.
    on_event_data(key, value) 
        Will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)
    on_xkey(key) 
        If steelsquid browser-on or mbrowser-on is activated
        Some keys is catched and a then is executed her instead.
        Key can be: ESC, DEL, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12
    '''

    @staticmethod
    def on_start():
        '''
        This will execute when system starts
        Do not execute long running stuff here, do it in on_loop...
        '''
        # Startup message
        steelsquid_utils.shout("Steelsquid Irrbloss start")
        if SETTINGS.control==1:
            co = "Radio"
        elif SETTINGS.control==2:
            co = "WIFI"
        elif SETTINGS.control==3:
            co = "3G/4G"
        else:
            co = "Not saved"
        steelsquid_utils.shout("Control: " + co + "\n" + "Control IP: " + SETTINGS.control_ip + "\n" + "Video stream IP: " + SETTINGS.video_ip + "\n" + "Audio stream IP: " + SETTINGS.audio_ip + "\n" + "Resolution: " + SETTINGS.width+"x"+SETTINGS.height+ "\n" + "FPS: " + SETTINGS.fps + "\n")
        # Set the on OK and ERROR callback methods...they just flash some LED
        steelsquid_utils.on_ok_callback_method=UTILS.on_ok
        steelsquid_utils.on_err_callback_method=UTILS.on_err
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        # Enable and disable networkcards
        UTILS.set_net_status(SETTINGS.control)
        # Reset some GPIO
        IO.OUTPUT.sum_flash()
        IO.UNITS.headlight(False)
        IO.UNITS.highbeam(False)
        IO.UNITS.siren(False)
        IO.UNITS.speeker(True)
        IO.OUTPUT.mood(0)
        # Way ???
        steelsquid_pi.gpio_set(26, True)        
        # Max volume
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "100%"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["alsactl", "store"], wait_for_finish=True)
        # Center camera
        IO.UNITS.camera(0, STATIC.servo_position_tilt_start, False)
        # Setup gstreamer
        steelsquid_gstreamer.setup_camera_mic(SETTINGS.video_ip, 6607, SETTINGS.audio_ip, 6608, SETTINGS.width, SETTINGS.height, SETTINGS.fps, SETTINGS.bitrate, SETTINGS.tcp_video, SETTINGS.low_light)


    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        RADIO.PUSH_1.motor_left = 0
        RADIO.PUSH_1.motor_right = 0
        IO.UNITS.drive(0, 0)
        steelsquid_bno0055.zero_heading()
        steelsquid_pi.cleanup()
       
       
    @staticmethod
    def on_network(status, wired, usb, wifi_ssid, wifi, wan):
        '''
        Will be execute on network up or down
        '''
        RADIO.LOCAL.wan = wan




        
        



##############################################################################################################################################################################################
class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    # Using this for check speekers on for 2 minutes then turn off
    last_speek=None
    
    
    @staticmethod
    def lte_gps_data_temp_alti():
        '''
        Check that the LTE dongle is disabled when not in use
        Also read GPS
        And data usage
        ''' 
        # check for LTE dongle
        if SETTINGS.control!=3:
            lines = steelsquid_utils.execute_system_command(["ifconfig"])
            for line in lines:
                if "usb0" in line:
                    UTILS.set_net_status(SETTINGS.control)
                    break;

        RADIO.LOCAL.gps_con = steelsquid_gps.connected()
        RADIO.LOCAL.gps_lat = steelsquid_gps.latitude()
        RADIO.LOCAL.gps_long= steelsquid_gps.longitude()
        RADIO.LOCAL.gps_alt = steelsquid_gps.altitude()
        RADIO.LOCAL.gps_speed = steelsquid_gps.speed()
        #RADIO.LOCAL.gps_long=17.3755498
        #RADIO.LOCAL.gps_lat=62.4151552
        # Rean network usage
        card = "wlan0"
        if SETTINGS.control == 3:
            card = "usb0"       
        answer=steelsquid_utils.execute_system_command(["ifconfig", card])[-1] 
        answer = answer.split(":")
        answer = float(int(answer[1].split(" ")[0]) + int(answer[2].split(" ")[0]))
        RADIO.LOCAL.data_usage = str(round(answer/1073741824, 1))
        # Core temp
        tm = steelsquid_utils.execute_system_command(["vcgencmd", "measure_temp"])[0]
        tm = tm.replace("temp=", "")
        tm = tm.replace("'C", "")
        RADIO.LOCAL.temperature_core = str(int(round(float(tm), 0)))
        # Calcultae max value for the drive (not over 12V)
        if RADIO.LOCAL.rover_voltage != -1:
            v = int((12.0/RADIO.LOCAL.rover_voltage)*100)
            if v >100:
                RADIO.LOCAL.motor_max = 100
            else:
                RADIO.LOCAL.motor_max = v
        return 6  


    @staticmethod
    def bandwidth_reader_checkpir():
        '''
        Read bandwidth
        And check PIR
        ''' 
         # Read remote voltage
        if SETTINGS.control == 3:
            RADIO.LOCAL.bandwidth = str(round(steelsquid_utils.bandwidth("usb0"), 1))
        else:
            RADIO.LOCAL.bandwidth = str(round(steelsquid_utils.bandwidth("wlan0"), 1))
        # Check PIR
        if RADIO.REMOTE.mood == 5:
            if RADIO.LOCAL.pir_front or RADIO.LOCAL.pir_left or RADIO.LOCAL.pir_right or RADIO.LOCAL.pir_back:
                if LOOP.last_speek == None or (datetime.datetime.now()-LOOP.last_speek).total_seconds() > 20:
                    LOOP.last_speek = datetime.datetime.now()
                    UTILS.play("away.wav")
        return 1










##############################################################################################################################################################################################
class RADIO(object):
    '''
    Two devices can communicate. It is ment to be used as a remote controll over TCP
    To enable this device as remote controll execute: steelsquid_kiss_global.radio_tcp(true)
    To enable this device as receiver of remote signals execute: steelsquid_kiss_global.radio_tcp(false, "ip to remote")
    '''
    
    
    @staticmethod
    def on_check(last_ping, ping_time, ping_time_median):
        '''
        Will execute about every half second.
        Us this to check for connection lost
        last_ping: Seconds since last communication with the remote host
                   -1 = no data (just after boot)
        ping_time: Seconds of the last ping time (how long did it take for the remote to answer a ping)
                   99 = timeout or error in comunikation
                   -1 = no data (just after boot)
        ping_time_median: Median of the last 5 ping_time
                   -1 = no data (just after boot)
        '''
        if last_ping != -1:
            # Stop drive if no commadn in 1 second
            if last_ping>1:
                RADIO.PUSH_1.motor_left = 0
                RADIO.PUSH_1.motor_right = 0
                IO.UNITS.drive(0, 0)
                steelsquid_bno0055.zero_heading()
            # Flash and sount when connection lost
            if last_ping<STATIC.connection_lost_timeout:
                steelsquid_utils.execute_if_changed(DO.connected, True, execute_first_time=False)
            else:
                steelsquid_utils.execute_if_changed(DO.connected, False, execute_first_time=True)
            # Close streams
            if last_ping>STATIC.connection_lost_streams:
                doit = steelsquid_utils.execute_min_time(steelsquid_gstreamer.low_bandwidth, (), STATIC.connection_lost_streams)
            # Help is on its way
            if last_ping>STATIC.help_timeout and last_ping < STATIC.connection_lost_timeout_reboot-3:
                steelsquid_utils.execute_min_time(UTILS.play, ("move.wav", ), 15)
            # If no connection in 90 seconds...reboot
            if last_ping>STATIC.connection_lost_timeout_reboot:
                doit = steelsquid_utils.execute_min_time(UTILS.play, ("reboot.wav", ), 15)
                if doit:
                    steelsquid_kiss_global.reboot(6) 
        else:
            RADIO.PUSH_1.motor_left = 0
            RADIO.PUSH_1.motor_right = 0
            IO.UNITS.drive(0, 0)
            steelsquid_bno0055.zero_heading()
            
    
    @staticmethod
    def on_sync():
        '''
        Will execute about every second or when steelsquid_kiss_global.radio_interrupt() 
        Use this to check for changes in varibales under REMOTE.
        '''
        # Change show
        steelsquid_utils.execute_if_changed(DO.show, RADIO.REMOTE.show)
        # Set mood
        steelsquid_utils.execute_if_changed(IO.OUTPUT.mood, RADIO.REMOTE.mood)
        # highbeam
        steelsquid_utils.execute_if_changed(IO.UNITS.highbeam, RADIO.REMOTE.highbeam)
        # headlight
        steelsquid_utils.execute_if_changed(IO.UNITS.headlight, RADIO.REMOTE.headlight)


    class LOCAL(object):
        '''
        All varibales in this class will be synced from this machine to the remote about every second
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        Use steelsquid_kiss_global.radio_interrupt() to sync imediately
        LOCAL (on this machine) sync to REMOTE (on remote machine)
        '''
        # Rover voltage (this rover)
        rover_voltage = -1.0

        # Rover ampere (this rover)
        rover_ampere = -1

        # Temp
        temperature = "---"

        # Temp core
        temperature_core = "---"

        # altitude
        altitude = "---"
        
        # pressure
        pressure = "---"
        
        # pressure
        humidity = 0

        # data_usage
        data_usage = "---"

        # GPS connection
        gps_con = False

        # GPS longitud
        gps_long = 0.0

        # GPS latitid
        gps_lat = 0.0

        # GPS Altitude
        gps_alt = 0

        # GPS speed
        gps_speed = 0

        # Bandwidth
        bandwidth = "0"

        # roll
        roll = 0.0

        # pitch
        pitch = 0.0

        # Front PIR
        pir_front = False

        # Left PIR
        pir_left = False

        # Right PIR
        pir_right = False

        # Back PIR
        pir_back = False

        # Ambient lighting
        light = 0.0
    
        # Max motor speed
        motor_max = 80
    
        # WAN ip for the rover
        wan = ""



    class REMOTE(object):
        '''
        All varibales in this class will be synced from remote host to this machine
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        LOCAL (on remote machine) sync to REMOTE (on this machine)
        '''
        # 0=off 1=heart 2=smile 3=sad 4=wave
        mood = 0

        # Use laser
        laser = False

        # Use headlight
        headlight = False

        # Use high beam
        highbeam = False

        # Show this on screen
        # 1 = save   2 = settings   3 = Map   4 = FPV
        show = 3         

        # Is cruise control enabled (this is the speed)
        cruise = 0
        
        # Drive forward and backwardto turn
        spec_turn = False


    class PUSH_1(object):
        '''
        All varibales in this class (PUSH_1 to PUSH_4) will be synced from the remote control to the receiver when on_push() on the remote controll return True
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        '''
        # Speed of the motors
        motor_left = 0
        motor_right = 0

        @staticmethod
        def on_push():
            '''
            If this is the remote control:
                This will execute over and over again..
                Return True, 0.1 will push all variables in PUSH_1 to the server
                                 And then sleep for 0.1 number of seconds
                Return False, 0.1 do not push anything and slepp 0.1 second
            If this is the receiver:
                This will execute when the remote control send a push to the receiver
                Will ignore the return....
            '''
            left = RADIO.PUSH_1.motor_left
            right = RADIO.PUSH_1.motor_right
            diff = abs(left-right)
            if left != 0 and diff<4 and IO.last_drive_left!=0:
                diff = int(abs(math.ceil(IO.heading)))
                diff = diff * 3
                if diff>STATIC.max_drive_straight:
                    diff = STATIC.max_drive_straight
                if left > 20 or left < -20:
                    if IO.heading < 0:
                        left = left - diff
                    elif IO.heading > 0:
                        right = right - diff
                else:
                    if IO.heading < 0:
                        right = right + diff
                    elif IO.heading > 0:
                        left = left + diff
                if left>30:
                    IO.UNITS.drive(left, right, ramping=True)        
                else:
                    IO.UNITS.drive(left, right)        
            else:
                steelsquid_bno0055.zero_heading()
                IO.UNITS.drive(left, right)        
            return 0.01

            


    class PUSH_2(object):
        '''
        All varibales in this class (PUSH_1 to PUSH_4) will be synced from the remote control to the receiver when on_push() on the remote controll return True
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
       '''
        # tilt/pan
        camera_pan = 0
        camera_tilt = STATIC.servo_position_tilt_start
        can_pan = False

        @staticmethod
        def on_push():
            '''
            If this is the remote control:
                This will execute over and over again..
                Return True, 0.1 will push all variables in PUSH_1 to the server
                                 And then sleep for 0.1 number of seconds
                Return False, 0.1 do not push anything and slepp 0.1 second
            If this is the receiver:
                This will execute when the remote control send a push to the receiver
                Will ignore the return....
            '''
            IO.UNITS.camera(RADIO.PUSH_2.camera_pan, RADIO.PUSH_2.camera_tilt, RADIO.PUSH_2.can_pan)
        
        
        
    class REQUEST(object):
        '''
        If the remote control execute: data = steelsquid_kiss_global.radio_request("a_command", data)
        A method with the name a_command(data) will execute on the receiver in this class.
        The receiver then can return some data that the remote control will reseive...
        If server method raise exception the steelsquid_hmtrlrs.request("a_command", data) will also raise a exception.
        '''
        @staticmethod

        def control(parameters):
            '''
            A request from client to change controll method 
            (radio/wifi/4G)
            '''
            con = int(parameters[0])
            code = parameters[1]
            if (con == 1 or con == 2 or con == 3) and code == "1234567":
                SETTINGS.control = con
                if SETTINGS.control==1:
                    steelsquid_kiss_global.radio_switch(steelsquid_kiss_global.TYPE_HMTRLRS)
                else:
                    steelsquid_kiss_global.radio_switch(steelsquid_kiss_global.TYPE_TCP)
                steelsquid_kiss_global.save_module_settings()
                steelsquid_utils.execute_delay(2, UTILS.set_net_status, (con, ))
                steelsquid_kiss_global.restart(delay=4)
                return []
            else:
                raise Exception("Command error")
        
        @staticmethod
        def siren(parameters):
            '''
            A request from client to sound the iren for 1 second
            '''
            IO.UNITS.siren()
            return []


        @staticmethod
        def change_bitrate(parameters):
            '''
            A request from change bitrate
            '''
            SETTINGS.bitrate = parameters[0]
            steelsquid_kiss_global.save_module_settings()
            steelsquid_gstreamer.video_bitrate(SETTINGS.bitrate)


        @staticmethod
        def tcp_video(parameters):
            '''
            A request from enable/disable TCP video
            '''
            SETTINGS.tcp_video = steelsquid_utils.to_boolean(parameters[0])
            steelsquid_kiss_global.save_module_settings()
            steelsquid_gstreamer.video_tcp(SETTINGS.tcp_video)


        @staticmethod
        def low_light(parameters):
            '''
            A request from enable/disable low light camera
            '''
            SETTINGS.low_light = steelsquid_utils.to_boolean(parameters[0])
            steelsquid_kiss_global.save_module_settings()
            steelsquid_gstreamer.low_light(SETTINGS.low_light)


        @staticmethod
        def save_settings(parameters):
            '''
            A request from client to save settings
            '''
            if len(parameters)==8:
                if parameters[7]=="1234567":
                    if steelsquid_utils.is_ip_number(parameters[0]) and steelsquid_utils.is_ip_number(parameters[1]) and steelsquid_utils.is_ip_number(parameters[2]):
                        SETTINGS.control_ip = parameters[0]
                        SETTINGS.video_ip = parameters[1]
                        SETTINGS.audio_ip = parameters[2]
                        SETTINGS.width = parameters[3]
                        SETTINGS.height = parameters[4]
                        SETTINGS.fps = parameters[5]
                        SETTINGS.bitrate = parameters[6]
                        steelsquid_utils.set_parameter("tcp_radio_host", SETTINGS.control_ip)                    
                        steelsquid_kiss_global.save_module_settings()
                        steelsquid_kiss_global.restart(delay=2)
                        return []


        @staticmethod
        def speek(parameters):
            '''
            A request from client to speek
            '''
            DO.speek(parameters[0])
            return []
            

        @staticmethod
        def typing(parameters, dummy=None):
            '''
            Is typing on keyboard
            '''
            lmatrix.animate_typing(7)
            return []









        





##############################################################################################################################################################################################
class IO(object):
    '''
    Put IO stuff her, maybe read stuff from sensors or listen for button press.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    Maybe use on_start() to start listen on GPIO or enable sensors...
    reader_1 to reader_4 is threads that execute in separate threads.
    _suppress_error = True Will not print error if reader_1 to 4 shrow error
    '''

    # Print error if reader_1 to 4 shrow error
    _suppress_error = True
    
    # IMU
    heading = 0.0
    
    # Last
    last_drive_left = 0
    last_drive_right = 0

    # Alterback and forward
    _forward_timer = datetime.datetime.now()
    _f_shift = 0
    _left = 0
    _right = 0
    left = 0
    right = 0


    @staticmethod
    def on_start():
        '''
        This will execute when system starts, it is the same as on_start in SYSTEM but put IO stuff her.
        Do not execute long running stuff here, do it in on_loop...
        Maybe use this to start listen on GPIO or enable sensors
        '''
        # Listen for signals fromPIR sensors
        steelsquid_pi.gpio_event(13, IO.INPUT.pir_front, resistor=steelsquid_pi.PULL_NONE)
        steelsquid_pi.gpio_event(26, IO.INPUT.pir_left, resistor=steelsquid_pi.PULL_NONE)
        steelsquid_pi.gpio_event(19, IO.INPUT.pir_right, resistor=steelsquid_pi.PULL_NONE)
        #steelsquid_pi.gpio_event(6, IO.INPUT.pir_back, resistor=steelsquid_pi.PULL_NONE)
    

    @staticmethod
    def reader_1():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        RADIO.LOCAL.rover_voltage = IO.UNITS.read_in_voltage()
        RADIO.LOCAL.rover_ampere = IO.UNITS.read_in_ampere()
        IO.heading, RADIO.LOCAL.roll, p = steelsquid_bno0055.read(switch_roll_pitch=True)
        RADIO.LOCAL.pitch = p+3
        return 0


    @staticmethod
    def reader_2():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        # Read humidity
        hum = steelsquid_pi.si7021_hum()
        RADIO.LOCAL.humidity = int(hum)
        # Read temp and altitude
        temp, pres, alti = steelsquid_pi.mpl3115A2()
        RADIO.LOCAL.temperature = str(int(temp))
        RADIO.LOCAL.pressure = str(int(pres))
        RADIO.LOCAL.altitude = str(int(alti))
        # Read light
        RADIO.LOCAL.light = steelsquid_pi.tsl2561()
        return 0
    
    
    @staticmethod
    def reader_3():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        # Turn the rover by driving forward and backward (not just turn on on the spot)
        if RADIO.REMOTE.spec_turn and ((IO.left < 0 and IO.right > 0) or (IO.left > 0 and IO.right < 0)):
            go_right = IO.left>0
            turn = abs(IO.left)
            turn_slow = int(turn)
            turn_fast = int(turn*2)
            inc = 5
            now = datetime.datetime.now()
            # Restart from drive forward
            if IO._f_shift == 0:
                IO._left = 0
                IO._right = 0
                IO._forward_timer = datetime.datetime.now()               
            diff = (now - IO._forward_timer).total_seconds()
            # Drive forward
            if diff < 0.5:
                IO._f_shift = 1
                if go_right:
                    if IO._left < turn_fast:
                        IO._left = IO._left + inc
                    if IO._right < turn_slow:
                        IO._right = IO._right + inc
                else:
                    if IO._left < turn_slow:
                        IO._left = IO._left + inc
                    if IO._right < turn_fast:
                        IO._right = IO._right + inc
            # SLow down
            elif diff < 1:
                IO._f_shift = 2
                if IO._left > 0:
                    IO._left = IO._left - inc
                if IO._right > 0:
                    IO._right = IO._right - inc
            # Drive backward
            elif diff < 1.5:
                if IO._f_shift != 3:
                    IO._left = 0
                    IO._right = 0
                IO._f_shift = 3
                if go_right:
                    if IO._left > turn_slow*-1:
                        IO._left = IO._left - inc
                    if IO._right > turn_fast*-1:
                        IO._right = IO._right - inc
                else:
                    if IO._left > turn_fast*-1:
                        IO._left = IO._left - inc
                    if IO._right > turn_slow*-1:
                        IO._right = IO._right - inc
            # Slow down
            elif diff < 2:
                IO._f_shift = 4
                if IO._left < 0:
                    IO._left = IO._left + inc
                if IO._right < 0:
                    IO._right = IO._right + inc
            else:
                IO._f_shift = 0
            # Sen signal to motor controller    
            steelsquid_pi.sabertooth_motor_speed(IO._left*-1, IO._right*-1, the_port="/dev/ttyUSB0", ramping=False)
        return 0.01
    
    
    @staticmethod
    def reader_4():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        steelsquid_pi.pca9685_move(1, 410, address = 0x41)
        return 0.5
        
       
    class UNITS(object):
        '''
        In this class i puth static methods that example reads data from sensors.
        Often it is the reader thread that acces this methods.
        '''
        
        
        @staticmethod
        def read_in_voltage():
            '''
            Read main in voltage
            '''
            v = steelsquid_pi.po12_adc_volt_smooth(8, median_size=64) / 0.1190
            v = Decimal(v)
            v = round(v, 1)
            if v > 20:
                v = 16.8
            return v


        @staticmethod
        def read_in_ampere():
            '''
            Read main in ampere
            '''
            v = steelsquid_pi.po12_adc_smooth(7, median_size=64)
            v = v - 503
            v = v * 0.003225806
            v = v / 0.026
            v = Decimal(v)
            v = math.ceil(v)
            if v > 90:
                v = 40
            return int(v)
            

        @staticmethod
        def headlight(status):
            '''
            Enable headlights
            ''' 
            steelsquid_pi.gpio_set(16, not status)        
            steelsquid_pi.gpio_set(20, not status)        
            

        @staticmethod
        def highbeam(status):
            '''
            Enable highbeam
            ''' 
            status = not status
            #steelsquid_pi.gpio_set(7, status)
            steelsquid_pi.gpio_set(12, status)
            steelsquid_pi.gpio_set(25, status) 
            steelsquid_pi.gpio_set(24, status) 
            

        @staticmethod
        def siren(status = None):
            '''
            siren
            ''' 
            if status==None:
                steelsquid_pi.mcp23017_flash(20, 5)
            else:
                steelsquid_pi.mcp23017_set(20, 5, status)
            

        @staticmethod
        def camera(pan, tilt, can_pan):
            '''
            Move servo
            '''
            # Check the values...getting some crapp data some time....
            if tilt!=None:
                if tilt < 0 or tilt > 800:
                    return
            if can_pan:
                steelsquid_pi.pca9685_move(2, 300, address = 0x41)
                if pan!=None:
                    steelsquid_pi.pca9685_move(1, 410+(pan/3), address = 0x41)
            else:
                steelsquid_pi.pca9685_move(2, 500, address = 0x41)
            if tilt!=None:
                if tilt<STATIC.servo_position_tilt_min:
                    tilt = STATIC.servo_position_tilt_min
                elif tilt>STATIC.servo_position_tilt_max:
                    tilt = STATIC.servo_position_tilt_max
                steelsquid_pi.pca9685_move(0, tilt, address = 0x41)      
            

        @staticmethod
        def drive(left, right, ramping = True):
            '''
            Drive
            '''

            if left>RADIO.LOCAL.motor_max:
                left = RADIO.LOCAL.motor_max
            elif left<RADIO.LOCAL.motor_max*-1:
                left = RADIO.LOCAL.motor_max*-1
            if right>RADIO.LOCAL.motor_max:
                right = RADIO.LOCAL.motor_max
            elif right<RADIO.LOCAL.motor_max*-1:
                right = RADIO.LOCAL.motor_max*-1
            IO.last_drive_left = left
            IO.last_drive_right = right
            IO.left = left
            IO.right = right
            # Turn the rover by driving forward and backward (not just turn on on the spot)
            #This is made in the thread reader_3
            if RADIO.REMOTE.spec_turn and ((left < 0 and right > 0) or (left > 0 and right < 0)):
                pass
            else:
                IO._left = 0
                IO._right = 0
                IO._f_shift = 0
                IO._forward_timer = datetime.datetime.now()               
                # Sen signal to motor controller    
                steelsquid_pi.sabertooth_motor_speed(left*-1, right*-1, the_port="/dev/ttyUSB0", ramping = ramping)

            
        @staticmethod
        def speeker(status):
            '''
            Turn on and off speekers
            '''
            steelsquid_pi.gpio_set(21, not status)



    class INPUT(object):
        '''
        Put input stuff her, maybe method to execute when a button is pressed.
        It is not necessary to put it her, but i think it is kind of nice to have it inside this class
        '''

        @staticmethod
        def pir_front(gpio, status):
            '''
            Front PIR
            '''
            RADIO.LOCAL.pir_front = status


        @staticmethod
        def pir_left(gpio, status):
            '''
            Left PIR
            '''
            RADIO.LOCAL.pir_left = status


        @staticmethod
        def pir_right(gpio, status):
            '''
            Right PIR
            '''
            RADIO.LOCAL.pir_right = status


        @staticmethod
        def pir_back(gpio, status):
            '''
            Back PIR
            '''
            RADIO.LOCAL.pir_back = status



    class OUTPUT(object):
        '''
        Put output stuff her, maybe method that light a LED.
        It is not necessary to put it her, but i think it is kind of nice to have it inside this class
        '''
        
        @staticmethod
        def sum_flash(dummy=False):
            '''
            Sound the summer for short time
            ''' 
            if not dummy:
                thread.start_new_thread(IO.OUTPUT.sum_flash, (True,))
            else:
                steelsquid_pi.po12_digital_out(1, True)
                steelsquid_pi.po12_digital_out(2, True)
                steelsquid_pi.po12_digital_out(3, True)
                time.sleep(0.02)
                steelsquid_pi.po12_digital_out(1, False)
                steelsquid_pi.po12_digital_out(2, False)
                steelsquid_pi.po12_digital_out(3, False)


        @staticmethod
        def mood(nr):
            '''
            Set smiley in led array
            0=off 1=heart 2=smile 3=sad 4=wave
            ''' 
            lmatrix.animate_stop()
            if nr == 1:
                lmatrix.animate_heart(True)
                UTILS.play("whistle.wav", sleep=0.5)
            elif nr == 2:
                lmatrix.paint(lmatrix.matrix_smile)
                UTILS.play("ding.wav", sleep=0.5)
            elif nr == 3:
                lmatrix.paint(lmatrix.matrix_sad)
                UTILS.play("angry.wav", sleep=0.5)
            elif nr == 4:
                lmatrix.animate_wave(True)
                UTILS.play("horn.wav", times=2, sleep=0.5)
            elif nr == 5:
                steelsquid_utils.execute_blink("away_flash", True, IO.UNITS.headlight, (True,), 0.01, IO.UNITS.headlight, (False,), 2)
                lmatrix.animate_wait(True)
            else:
                steelsquid_utils.execute_blink("away_flash", False)
                lmatrix.animate_stop()
                
        
        
        
        








##############################################################################################################################################################################################
class DO(object):
    '''
    Put staticmethods in this class, methods that carry ut mutipple thinks
    Maybe light led, send request and handle error from the request
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''

    @staticmethod
    def connected(status, dummy=False):
        '''
        Fire connection lost or not
        ''' 
        if not dummy:
            if status:
                steelsquid_utils.execute_one_time_clean()
                UTILS.play("connected.wav")
                lmatrix.animate_stop()
            else:
                UTILS.play("reconnect.wav")
                lmatrix.animate_connect(True)
            steelsquid_utils.execute_blink("connected_flash_1", not status, DO.connected, (True, True,), 0.04, DO.connected, (False, True,), 2)
        else:
            steelsquid_pi.gpio_set(16, not status)
            steelsquid_pi.po12_digital_out(1, status)
            steelsquid_pi.po12_digital_out(2, status)
            #steelsquid_pi.po12_digital_out(3, status)



    @staticmethod
    def show(this):
        '''
        1=save   2 = settings   3 = Map   4 = FPV
        ''' 
        if this == 1:
            steelsquid_gstreamer.video(True)
            steelsquid_gstreamer.audio(True)
        elif this == 4:
            steelsquid_gstreamer.video(True)
            steelsquid_gstreamer.audio(True)
        else:
            steelsquid_gstreamer.video(False)
            steelsquid_gstreamer.audio(False)


    @staticmethod
    def speek(text, lcd=True, english=False, dummy=None):
        '''
        Speek text
        '''
        if dummy == None:
            thread.start_new_thread(DO.speek, (text, lcd, english, "",)) 
        else:
            #sleep = False
            #if LOOP.last_speek == None:
            #    sleep = True
            #LOOP.last_speek = time.time()
            #IO.UNITS.speeker(True)
            #if sleep:
            #    time.sleep(5)
            t = len(text)/10
            if t < 1:
                t = 0.8
            if english:
                espeak.set_voice("en+f5")
            else:
                espeak.set_voice("sv+f5")
            espeak.synth(text)
            if lcd:
                lmatrix.animate_speak(t, leav_this=lmatrix.matrix_smile)
                lmatrix.clear(10)
















##############################################################################################################################################################################################
class UTILS(object):
    '''
    Put utils staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''
    @staticmethod
    def write_message(message=None, is_errorr=False):
        '''
        Write message to LCD
        ''' 
        DYNAMIC.stop_next_lcd_message=True
        steelsquid_utils.shout(string=message, is_error=is_errorr)


    @staticmethod
    def on_ok(message):
        '''
        OK
        ''' 
        pass


    @staticmethod
    def on_err(message):
        '''
        Some error
        ''' 
        IO.UNITS.led_error_flash()
        

    @staticmethod
    def set_net_status(con):
        '''
        Set with way to control rover
        1=radio 2=wifi 3=3g4g
        '''        
        # Enable wifi but disable usb0 (3G/4G modem)
        if con==1:
            steelsquid_utils.execute_system_command_blind(["killall", "gst-launch-1.0"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "wlan0", "up"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "usb0", "down"])
        # Enable wifi but disable usb0 (3G/4G modem)
        elif con==2:
            steelsquid_utils.execute_system_command_blind(["killall", "gst-launch-1.0"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "wlan0", "up"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "usb0", "down"])
        # Disable wifi but enable usb0 (3G/4G modem)
        elif con==3:
            steelsquid_utils.execute_system_command_blind(["killall", "gst-launch-1.0"])
            #steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "wlan0", "down"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "usb0", "up"])


    @staticmethod
    def play(sound, times = 1, sleep = 0):
        '''
        Play a sound
        ''' 
        sound = "/opt/steelsquid/web/snd/"+sound
        thread.start_new_thread(UTILS._play, (sound, times, sleep))
        

    @staticmethod
    def _play(sound, times, sleep1):
        #sleep = False
        #if LOOP.last_speek == None:
        #    sleep = True
        #LOOP.last_speek = time.time()
        #IO.UNITS.speeker(True)
        #if sleep:
        #    time.sleep(5)
        time.sleep(sleep1)
        for i in range(times):
            steelsquid_utils.execute_system_command_blind(["aplay", sound])









