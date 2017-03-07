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
    servo_position_pan_start = 480

    # Max Servo position
    servo_position_pan_max = 660

    # Min Servo position
    servo_position_pan_min = 290

    # When system start move servo here
    servo_position_tilt_start = 450

    # Max Servo position
    servo_position_tilt_max = 507

    # Min Servo position
    servo_position_tilt_min = 250

    # Max motor speed
    motor_max = 80 










##############################################################################################################################################################################################
class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe toy enable something in the WEB class and want to use it from the LOOP class.
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
    This is usefull under development if you wan to test different values when you restart the module,
    otherwise the value from the first execution to be used ...
      _persistent_off = True
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
        







##############################################################################################################################################################################################
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
        OUTPUT.sum_flash()
        IO.UNITS.headlight(False)
        IO.UNITS.highbeam(False)
        IO.UNITS.ir(False)
        IO.UNITS.siren(False)
        IO.UNITS.cam_light(False)
        OUTPUT.mood(0)
        # Way ???
        steelsquid_pi.gpio_set(26, True)        
        # Max volume
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "100%"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["alsactl", "store"], wait_for_finish=True)
        # Center camera
        IO.UNITS.camera(STATIC.servo_position_pan_start, STATIC.servo_position_tilt_start)
        # Setup gstreamer
        steelsquid_gstreamer.setup_camera_mic(SETTINGS.video_ip, 6607, SETTINGS.audio_ip, 6608, SETTINGS.width, SETTINGS.height, SETTINGS.fps, SETTINGS.bitrate)
        # Listen for signals fromPIR sensors
        steelsquid_pi.gpio_event(13, INPUT.pir_front, resistor=steelsquid_pi.PULL_NONE)
        steelsquid_pi.gpio_event(26, INPUT.pir_left, resistor=steelsquid_pi.PULL_NONE)
        steelsquid_pi.gpio_event(19, INPUT.pir_right, resistor=steelsquid_pi.PULL_NONE)
        steelsquid_pi.gpio_event(6, INPUT.pir_back, resistor=steelsquid_pi.PULL_NONE)


    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        RADIO.PUSH_1.motor_left = 0
        RADIO.PUSH_1.motor_right = 0
        IO.UNITS.drive(0, 0)
        steelsquid_pi.cleanup()
       




        
        



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
    def lte_speek_gps_data_temp_alti():
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
        # Turn of speeker
        if LOOP.last_speek != None:
            if time.time() - LOOP.last_speek > STATIC.speeker_timeout:
                IO.UNITS.speeker(False)
                LOOP.last_speek = None
        # read GPS
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
        # Read temp and altitude
        temp, pres, alti = steelsquid_pi.mpl3115A2()
        RADIO.LOCAL.temperature = str(int(temp))
        RADIO.LOCAL.pressure = str(int(pres))
        RADIO.LOCAL.altitude = str(int(alti))
        # Core temp
        tm = steelsquid_utils.execute_system_command(["vcgencmd", "measure_temp"])[0]
        tm = tm.replace("temp=", "")
        tm = tm.replace("'C", "")
        RADIO.LOCAL.temperature_core = str(int(round(float(tm), 0)))
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
                steelsquid_utils.execute_min_time(DO.speek, ("The driver is temporarily away. Please do not touch the robot", False, True,), 20)
        return 1










##############################################################################################################################################################################################
class RADIO(object):
    '''
    This is the new RADIO functionality.
    This is similar to tho old but can handle HM-TRLR-S transceiver and TCP socket connections.

    HM-TRLR-S
        Enable the HM-TRLR-S server functionality in command line: set-flag radio_hmtrlrs_server
        On client device: set-flag radio_hmtrlrs_client
        Must restart the steelsquid daeomon for it to take effect.
        In python you can do: steelsquid_kiss_global.radio_hmtrlrs(status)
        status: True=Enable as server
                False=Enable as client
                None=Disable
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
            # Flash and sount when connection lost
            if last_ping<STATIC.connection_lost_timeout:
                steelsquid_utils.execute_if_changed(DO.connected, True, execute_first_time=False)
            else:
                steelsquid_utils.execute_if_changed(DO.connected, False, execute_first_time=True)
            # Close streams
            if last_ping>STATIC.connection_lost_streams:
                doit = steelsquid_utils.execute_min_time(DO.show, (3, ), STATIC.connection_lost_timeout_reboot)
            # Help is on its way
            if last_ping>STATIC.help_timeout and last_ping < STATIC.connection_lost_timeout_reboot-3:
                steelsquid_utils.execute_min_time(DO.speek, ("No connection. If i'm in the way please move me to the side of the road", False, True, ), 10)
            # If no connection in 90 seconds...reboot
            if last_ping>STATIC.connection_lost_timeout_reboot:
                doit = steelsquid_utils.execute_one_time(DO.speek, ("No connection in 90 seconds. Reboot in progress", False, True, ))
                if doit:
                    steelsquid_kiss_global.reboot(6) 
        else:
            RADIO.PUSH_1.motor_left = 0
            RADIO.PUSH_1.motor_right = 0
            IO.UNITS.drive(0, 0)

    
    @staticmethod
    def on_sync():
        '''
        Will execute about every second or when steelsquid_kiss_global.radio_interrupt() 
        Use this to check for changes in varibales under REMOTE.
        '''
        # Change show
        steelsquid_utils.execute_if_changed(DO.show, RADIO.REMOTE.show)
        # Set mood
        steelsquid_utils.execute_if_changed(OUTPUT.mood, RADIO.REMOTE.mood)
        # Set ir
        steelsquid_utils.execute_if_changed(IO.UNITS.ir, RADIO.REMOTE.ir)
        # Set cam light
        steelsquid_utils.execute_if_changed(IO.UNITS.cam_light, RADIO.REMOTE.cam_light)
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

        # Cam light
        cam_light = False

        # IR light
        ir = False

        # Show this on screen
        # 1 = save   2 = settings   3 = Map   4 = FPV
        show = 3         
    

    class PUSH_1(object):
        '''
        All varibales in this class will be synced from the client to the server when on_push(1) on the client return True
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        '''
        # Speed of the motors
        motor_left = 0
        motor_right = 0

        @staticmethod
        def on_push():
            '''
            If this is the clent:
                This will execute over and over again..
                Return True, 0.1 will push all variables in PUSH_1 to the server
                                 And then sleep for 0.1 number of seconds
                Return False, 0.1 do not push anything and slepp 0.1 second
            If this is the server:
                This will execute when the client send a push to the server
                Will ignore the return....
            '''
            left = RADIO.PUSH_1.motor_left
            right = RADIO.PUSH_1.motor_right
            diff = abs(left-right)
            if left != 0 and diff<4:
                diff = int(abs(math.ceil(IO.heading)))
                diff = diff * 3
                if diff>40:
                    diff = 40
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
            else:
                steelsquid_bno0055.zero_heading()
            IO.UNITS.drive(left, right)        
            return 0.01

            


    class PUSH_2(object):
        '''
        All varibales in this class will be synced from the client to the server when on_push(2) on the client return True
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        '''
        # tilt/pan
        camera_pan = STATIC.servo_position_pan_start
        camera_tilt = STATIC.servo_position_tilt_start

        @staticmethod
        def on_push():
            '''
            If this is the clent:
                This will execute over and over again..
                Return True, 0.1 will push all variables in PUSH_1 to the server
                                 And then sleep for 0.1 number of seconds
                Return False, 0.1 do not push anything and slepp 0.1 second
            If this is the server:
                This will execute when the client send a push to the server
                Will ignore the return....
            '''
            IO.UNITS.camera(RADIO.PUSH_2.camera_pan, RADIO.PUSH_2.camera_tilt)
        
        
        
    class REQUEST(object):
        '''
        HM-TRLR-S
            If the clent execute: data = steelsquid_hmtrlrs.request("a_command", data)
            A method with the name a_command(data) will execute on the server in this class.
            The server then can return some data that the client will reseive...
            You can also execute: steelsquid_hmtrlrs.broadcast("a_command", data)
            If you do not want a response back from the server. 
            The method on the server should then return None.
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
class INPUT(object):
    '''
    User related stuff...
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











##############################################################################################################################################################################################
class OUTPUT(object):
    '''
    User related stuff...
    Put input stuff her, maybe method to execute when a button is pressed.
    Put output stuff her, maybe method that light a LED.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    '''
    
    @staticmethod
    def sum_flash(dummy=False):
        '''
        Sound the summer for short time
        ''' 
        if not dummy:
            thread.start_new_thread(OUTPUT.sum_flash, (True,))
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
            UTILS.play("/root/whistle.wav", sleep=0.5)
        elif nr == 2:
            lmatrix.paint(lmatrix.matrix_smile, 3)
        elif nr == 3:
            lmatrix.paint(lmatrix.matrix_sad, 3)
        elif nr == 4:
            lmatrix.animate_wave(True)
            UTILS.play("/root/horn.wav", times=2, sleep=0.5)
        elif nr == 5:
            steelsquid_utils.execute_blink("away_flash", True, IO.UNITS.headlight, (True,), 0.01, IO.UNITS.headlight, (False,), 4)
            lmatrix.animate_wait(True)
        else:
            steelsquid_utils.execute_blink("away_flash", False)
            lmatrix.animate_stop()
            
        
        
        





##############################################################################################################################################################################################
class IO(object):
    '''
    Put IO stuff her, maybe read stuff from sensors.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    And you can use the reader thread...
    '''

    # IMU
    heading = 0.0


    @staticmethod
    def reader():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        RADIO.LOCAL.rover_voltage = IO.UNITS.read_in_voltage()
        RADIO.LOCAL.rover_ampere = IO.UNITS.read_in_ampere()
        IO.heading, RADIO.LOCAL.roll, RADIO.LOCAL.pitch = steelsquid_bno0055.read(switch_roll_pitch=True)
        return 0
    
    
       
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
            return int(v)
            

        @staticmethod
        def headlight(status):
            '''
            Enable headlights
            ''' 
            steelsquid_pi.gpio_set(16, not status)
            

        @staticmethod
        def highbeam(status):
            '''
            Enable highbeam
            ''' 
            status = not status
            steelsquid_pi.gpio_set(7, status)
            steelsquid_pi.gpio_set(12, status)
            

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
        def cam_light(status):
            '''
            Enable cam light
            ''' 
            steelsquid_pi.gpio_set(20, not status)


        @staticmethod
        def ir(status):
            '''
            Enable irlight
            ''' 
            steelsquid_pi.gpio_set(8, not status)
            

        @staticmethod
        def camera(pan, tilt):
            '''
            Move servo
            '''
            # Check the values...getting some crapp data some time....
            if pan!=None:
                if pan < 0 or pan > 800:
                    return
            if tilt!=None:
                if tilt < 0 or tilt > 800:
                    return

            if pan!=None:
                if pan<STATIC.servo_position_pan_min:
                    pan = STATIC.servo_position_pan_min
                elif pan>STATIC.servo_position_pan_max:
                    pan = STATIC.servo_position_pan_max
                steelsquid_pi.pca9685_move(1, pan)
            if tilt!=None:
                if tilt<STATIC.servo_position_tilt_min:
                    tilt = STATIC.servo_position_tilt_min
                elif tilt>STATIC.servo_position_tilt_max:
                    tilt = STATIC.servo_position_tilt_max
                steelsquid_pi.pca9685_move(0, tilt)      

            

        @staticmethod
        def drive(left, right):
            '''
            Drive
            '''
            # Check value
            if left>STATIC.motor_max:
                left = STATIC.motor_max
            elif left<STATIC.motor_max*-1:
                left = STATIC.motor_max*-1
            if right>STATIC.motor_max:
                right = STATIC.motor_max
            elif right<STATIC.motor_max*-1:
                right = STATIC.motor_max*-1
            steelsquid_pi.sabertooth_motor_speed(left*-1, right*-1, the_port="/dev/ttyUSB0")

            
        @staticmethod
        def speeker(status):
            '''
            Turn on and off speekers
            '''
            steelsquid_pi.gpio_set(21, not status)
            
        
        








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
                DO.speek("Connected to control station", False, True)
                lmatrix.animate_stop()
            else:
                DO.speek("Connection lost. Trying to reconnect", False, True)
                lmatrix.animate_start(lmatrix.matrix_animate_connect, rotate=3, seconds=0.05)
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
            sleep = False
            if LOOP.last_speek == None:
                sleep = True
            LOOP.last_speek = time.time()
            IO.UNITS.speeker(True)
            if sleep:
                time.sleep(5)
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
        thread.start_new_thread(UTILS._play, (sound, times, sleep))
        

    @staticmethod
    def _play(sound, times, sleep1):
        sleep = False
        if LOOP.last_speek == None:
            sleep = True
        LOOP.last_speek = time.time()
        IO.UNITS.speeker(True)
        if sleep:
            time.sleep(5)
        time.sleep(sleep1)
        for i in range(times):
            steelsquid_utils.execute_system_command_blind(["aplay", sound])









