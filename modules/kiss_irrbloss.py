#!/usr/bin/python -OO


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
import datetime
import thread  
import steelsquid_hmtrlrs
import steelsquid_ht16k33 as lmatrix
import steelsquid_tcp_radio
from decimal import Decimal
import os
from espeak import espeak
espeak.set_voice("sv+f5")

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
    steelsquid_kiss_global.hmtrlrs_status("server")
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
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






class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # Remote voltages(lipo 3s) 
    remote_voltage_max = 12.6      # 4.2V
    remote_voltage_warning = 10.5  # 3.5V
    remote_voltage_min = 9.6       # 3.2V

    # Rover voltages(lipo 4s)
    rover_voltage_max = 16.8        # 4.2V
    rover_voltage_warning = 14      # 3.5V
    rover_voltage_min = 12.8        # 3.2V
    
    # interrup GPIO for mcp23017
    gpio_mcp23017_20_trig = 4

    # GPIO for the HM-TRLR-S
    gpio_hmtrlrs_config = 18
    gpio_hmtrlrs_reset = 23

    # When system start move servo here
    servo_position_pan_start = 452

    # Max Servo position
    servo_position_pan_max = 700

    # Min Servo position
    servo_position_pan_min = 125

    # When system start move servo here
    servo_position_tilt_start = 450

    # Max Servo position
    servo_position_tilt_max = 550

    # Min Servo position
    servo_position_tilt_min = 200

    # Max motor speed
    motor_max = 80 

    # Max motor speed change
    motor_max_change = 50

    mood_smile = [[ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,0,1,1,0,0,0],
                  [ 0,1,0,0,0,0,1,0],
                  [ 0,0,1,1,1,1,0,0],
                  [ 0,0,0,0,0,0,0,0]]
                  
    mood_straight = [[ 0,0,0,0,0,0,0,0],
                     [ 0,1,1,0,0,1,1,0],
                     [ 0,1,1,0,0,1,1,0],
                     [ 0,0,0,0,0,0,0,0],
                     [ 0,0,0,1,1,0,0,0],
                     [ 0,0,0,0,0,0,0,0],
                     [ 0,1,1,1,1,1,1,0],
                     [ 0,0,0,0,0,0,0,0]]

    mood_sad = [[ 0,0,0,0,0,0,0,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,1,1,0,0,1,1,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,0,1,1,0,0,0],
                [ 0,0,0,0,0,0,0,0],
                [ 0,0,1,1,1,1,0,0],
                [ 0,1,0,0,0,0,1,0]]

    mood_angry = [[ 0,1,0,0,0,0,1,0],
                  [ 0,0,1,0,0,1,0,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,1,1,0,0,1,1,0],
                  [ 0,0,0,0,0,0,0,0],
                  [ 0,0,1,1,1,1,0,0],
                  [ 0,0,0,0,0,0,0,0]]

    connection_lost = [[ 0,1,1,1,1,1,1,0],
                       [ 1,0,0,0,0,0,0,1],
                       [ 1,0,1,0,0,1,0,1],
                       [ 1,0,0,1,1,0,0,1],
                       [ 1,0,0,1,1,0,0,1],
                       [ 1,0,1,0,0,1,0,1],
                       [ 1,0,0,0,0,0,0,1],
                       [ 0,1,1,1,1,1,1,0]]




class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe toy enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # Last LCD message to print
    last_lcd_message = None
    
    # Using this when i print a message to LCD, so the next ip/voltage uppdat dont ovrewrite the message to fast
    stop_next_lcd_message = False

    # Stream audio
    audio = False

    # Stream video
    video = False



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
    resolution = "width=800,height=480"

    # Width for the stream
    fps = "20"

    # Bitrate for the stream
    bitrate = "800000"
        




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
        steelsquid_utils.shout("Control: " + co + "\n" + "Control IP: " + SETTINGS.control_ip + "\n" + "Video stream IP: " + SETTINGS.video_ip + "\n" + "Audio stream IP: " + SETTINGS.audio_ip + "\n" + "Resolution: " + SETTINGS.resolution + "\n" + "FPS: " + SETTINGS.fps + "\n")
        GLOBAL.set_net_status(SETTINGS.control)
        # Reset some GPIO
        OUTPUT.sum_flash()
        OUTPUT.laser(False)
        OUTPUT.headlight(False)
        OUTPUT.highbeam(False)
        steelsquid_pi.gpio_set(26, True)        
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        # Set the on OK and ERROR callback methods...they just flash some LED
        steelsquid_utils.on_ok_callback_method=GLOBAL.on_ok
        steelsquid_utils.on_err_callback_method=GLOBAL.on_err
        # Max volume
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "100%"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["alsactl", "store"], wait_for_finish=True)
        # Center camera
        OUTPUT.camera(STATIC.servo_position_pan_start, STATIC.servo_position_tilt_start)


    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        steelsquid_pi.cleanup()
       
        
        



class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    warning_flash = True
    last_mood = -1
    last_speek=None
    connection_lost=False
    connection_lost_count=0

    
    @staticmethod
    def update_lcd():
        '''
        Update the LCD
        ''' 
        try:            
            # Wite to LCD
            if not DYNAMIC.stop_next_lcd_message:
                print_this = []
                print_this.append(steelsquid_utils.get_date_time())
                connected = False
                # Get network status
                if steelsquid_kiss_global.last_net:
                    if steelsquid_kiss_global.last_wifi_name!="---":
                        print_this.append(steelsquid_kiss_global.last_wifi_name)
                        print_this.append(steelsquid_kiss_global.last_wifi_ip)
                        connected=True
                    if steelsquid_kiss_global.last_lan_ip!="---":
                        print_this.append(steelsquid_kiss_global.last_lan_ip)
                        connected=True
                    if steelsquid_kiss_global.last_usb_ip!="---":
                        print_this.append(steelsquid_kiss_global.last_usb_ip)
                        connected=True
                # Voltage
                if RADIO_SYNC.SERVER.rover_voltage != -1 and RADIO_SYNC.SERVER.rover_ampere != -1:
                    if RADIO_SYNC.SERVER.rover_voltage<STATIC.rover_voltage_warning:
                        if LOOP.warning_flash:
                            LOOP.warning_flash = False
                            print_this.append("Rover: " + str(RADIO_SYNC.SERVER.rover_voltage) + "V  " + str(RADIO_SYNC.SERVER.rover_ampere) + "A  LOW!")
                        else:
                            LOOP.warning_flash = True
                            print_this.append("Rover: " + str(RADIO_SYNC.SERVER.rover_voltage) + "V  " + str(RADIO_SYNC.SERVER.rover_ampere) + "A")
                    else:
                        print_this.append("Rover: " + str(RADIO_SYNC.SERVER.rover_voltage) + "V  " + str(RADIO_SYNC.SERVER.rover_ampere) + "A")                    
                # Write text to LCD
                if len(print_this)>0:
                    new_lcd_message = "\n".join(print_this)
                    if new_lcd_message!=DYNAMIC.last_lcd_message:
                        DYNAMIC.last_lcd_message = new_lcd_message
                        steelsquid_pi.ssd1306_write(new_lcd_message, 0)
            else:
                DYNAMIC.stop_next_lcd_message=False       
               
            # Connection lost
            if LOOP.connection_lost:
                if LOOP.connection_lost_count == 0:
                    lmatrix.paint_flash(STATIC.connection_lost, 3)
                    steelsquid_pi.gpio_flash(16, seconds=0.1, invert=False)
                    LOOP.connection_lost_count = LOOP.connection_lost_count + 1
                elif LOOP.connection_lost_count>=2:
                    LOOP.connection_lost_count = 0
                else:
                    LOOP.connection_lost_count = LOOP.connection_lost_count + 1
        except:
            steelsquid_utils.shout()
        return 1 # Execute this method again in 1 second


    @staticmethod
    def check_stuff():
        '''
        Uppdate other stuff
        ''' 
        try:
            # Update the mood
            if LOOP.last_mood != RADIO_SYNC.CLIENT.mood:      
                LOOP.last_mood = RADIO_SYNC.CLIENT.mood    
                if RADIO_SYNC.CLIENT.mood == 1:
                    lmatrix.paint(STATIC.mood_smile, 3)
                elif RADIO_SYNC.CLIENT.mood == 2:
                    lmatrix.paint(STATIC.mood_straight, 3)
                elif RADIO_SYNC.CLIENT.mood == 3:
                    lmatrix.paint(STATIC.mood_sad, 3)
                elif RADIO_SYNC.CLIENT.mood == 4:
                    lmatrix.paint(STATIC.mood_angry, 3)
                else:
                    lmatrix.clear()
            # Laser
            OUTPUT.laser(RADIO_SYNC.CLIENT.laser)
            # headlight
            OUTPUT.headlight(RADIO_SYNC.CLIENT.headlight)
            # highbeam
            OUTPUT.highbeam(RADIO_SYNC.CLIENT.highbeam)
            # cam light
            OUTPUT.cam_light(RADIO_SYNC.CLIENT.cam_light)
        except:
            steelsquid_utils.shout()
        return 1


    @staticmethod
    def vol_amp_reader():
        '''
        Read voltage and amp
        ''' 
        try:
            # Read remote voltage
            RADIO_SYNC.SERVER.rover_voltage = GLOBAL.read_in_voltage()
            RADIO_SYNC.SERVER.rover_ampere = GLOBAL.read_in_ampere()
            # Low voltage beep
            if RADIO_SYNC.SERVER.rover_voltage != -1 and RADIO_SYNC.SERVER.rover_ampere != -1:
                if RADIO_SYNC.SERVER.rover_voltage<STATIC.rover_voltage_warning:
                    OUTPUT.sum_flash()

        except:
            steelsquid_utils.shout()
        return 0
        
        
    @staticmethod
    def stream_video():
        '''
        Stream video
        ''' 
        if not steelsquid_utils.is_empty(SETTINGS.video_ip):
            if DYNAMIC.video:
                try:
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 v4l2src"])
                    time.sleep(0.5)
                    steelsquid_utils.execute_system_command(["modprobe", "bcm2835-v4l2", "gst_v4l2src_is_broken=1"])
                    steelsquid_utils.execute_system_command(["gst-launch-1.0", "v4l2src", "device=/dev/video0", "!", "video/x-raw," + SETTINGS.resolution + ",framerate=" + SETTINGS.fps + "/1", "!", "omxh264enc", "target-bitrate="+SETTINGS.bitrate, "control-rate=3", "!", "tcpclientsink", "host="+SETTINGS.video_ip, "port=6602"])
                    #steelsquid_utils.execute_system_command(["gst-launch-1.0", "v4l2src", "do-timestamp=false", "device=/dev/video0", "!", "video/x-raw,width=1280,height=720,framerate=25/1", "!", "omxh264enc", "!", "tcpclientsink", "host="+SETTINGS.video_ip, "port=6602"])
                except:
                    steelsquid_utils.shout()
            else:
                steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 v4l2src"])
        return 1


    @staticmethod
    def stream_audio():
        '''
        Stream audio
        ''' 
        if not steelsquid_utils.is_empty(SETTINGS.audio_ip):
            if DYNAMIC.audio:
                try:
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 alsasrc"])
                    time.sleep(0.5)
                    steelsquid_utils.execute_system_command(["gst-launch-1.0", "alsasrc", "device=sysdefault:CARD=1", "!", "mulawenc", "!", "rtppcmupay", "!", "udpsink", "host="+SETTINGS.audio_ip, "port=6603"])
                except:
                    steelsquid_utils.shout()
            else:
                steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 alsasrc"])
        return 4
        
        
    @staticmethod
    def check_lte_and_espeek():
        '''
        Check that the LTE dongle is disabled when not in use
        ''' 
        if SETTINGS.control!=3:
            lines = steelsquid_utils.execute_system_command(["ifconfig"])
            for line in lines:
                if "usb0" in line:
                    GLOBAL.set_net_status(SETTINGS.control)
                    break;
        if LOOP.last_speek != None:
            if time.time() - LOOP.last_speek > 120:
                steelsquid_pi.gpio_set(21, True)
                LOOP.last_speek = None
        return 10


        
        



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
    HM-TRLR-S
        Enable the HM-TRLR-S server functionality in command line: set-flag  hmtrlrs_server
        On client device: set-flag  hmtrlrs_client
        Must restart the steelsquid daeomon for it to take effect.
        In python you can do: steelsquid_kiss_global.hmtrlrs_status(status)
        status: server=Enable as server
                client=Enable as client
                None=Disable
        SERVER/CLIENT:
        If the clent execute: data = steelsquid_hmtrlrs.request("a_command", data)
        A method with the name a_command(data) will execute on the server in class RADIO.
        The server then can return some data that the client will reseive...
        You can also execute: steelsquid_hmtrlrs.broadcast("a_command", data)
        If you do not want a response back from the server. 
        The method on the server should then return None.
        If server method raise exception the steelsquid_hmtrlrs.request("a_command", data) will also raise a exception.
    '''

    @staticmethod
    def siren(parameters):
        '''
        A request from client to sound the iren for 1 second
        '''
        OUTPUT.siren()
        return []


    @staticmethod
    def settings_save(parameters):
        '''
        A request from client to save settings
        '''
        if len(parameters)==7:
            if parameters[6]=="1234567":
                if steelsquid_utils.is_ip_number(parameters[0]) and steelsquid_utils.is_ip_number(parameters[1]) and steelsquid_utils.is_ip_number(parameters[2]):
                    if parameters[3] != None and parameters[4] != None:
                        SETTINGS.control_ip = parameters[0]
                        SETTINGS.video_ip = parameters[1]
                        SETTINGS.audio_ip = parameters[2]
                        SETTINGS.resolution = parameters[3]
                        SETTINGS.fps = parameters[4]
                        SETTINGS.bitrate = parameters[5]
                        steelsquid_utils.set_parameter("tcp_radio_host", SETTINGS.control_ip)
                        steelsquid_kiss_global.save_module_settings()
                        steelsquid_kiss_global.reboot(delay=4)
                        return []


    @staticmethod
    def set_control(parameters):
        '''
        A request from client to save settings
        '''
        print "sadasdadsd"
        print parameters
        con = int(parameters[0])
        code = parameters[1]
        if (con == 1 or con == 2 or con == 3) and code == "1234567":
            SETTINGS.control = con
            steelsquid_kiss_global.save_module_settings()
            GLOBAL.set_net_status(con)
            if SETTINGS.control==1:
                steelsquid_kiss_global.tcp_radio_disable()
            else:
                steelsquid_kiss_global.tcp_radio_client(False, host = SETTINGS.control_ip)
            steelsquid_kiss_global.restart(delay=4)
            return []


    @staticmethod
    def speek(parameters, dummy=None):
        '''
        A request from client to speek
        '''
        if dummy == None:
            thread.start_new_thread(RADIO.speek, (parameters, "",)) 
        else:
            sleep = False
            if LOOP.last_speek == None:
                sleep = True
            LOOP.last_speek = time.time()
            steelsquid_pi.gpio_set(21, False)
            if sleep:
                time.sleep(5)
            espeak.synth(parameters[0])
        return []
        
        
    @staticmethod
    def stream_video(parameters):
        '''
        A request from client to stream or not to stream video
        '''
        if steelsquid_utils.is_empty(SETTINGS.video_ip):
            raise Exception("IP not set")
        else:
            DYNAMIC.video = parameters[0]=="True"
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 v4l2src"])
            return []
        
        
        
        
    @staticmethod
    def stream_audio(parameters):
        '''
        A request from client to stream or not to stream audio
        '''
        if steelsquid_utils.is_empty(SETTINGS.audio_ip):
            raise Exception("IP not set")
        else:
            DYNAMIC.audio = parameters[0]=="True"
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 alsasrc"])
            return []






class RADIO_SYNC(object):
    '''
    Class RADIO_SYNC
      If you use a HM-TRLR-S and it is enabled (set-flag  hmtrlrs_server) this class will make the client send
      ping commadns to the server.
      staticmethod: on_sync(seconds_since_last_ok_ping)
        seconds_since_last_ok_ping: Seconds since last sync that went OK (send or reseive)
        Will fire after every sync on the client (ones a second or when steelsquid_kiss_global.radio_interrupt() is executed)
        This will also be executed on server (When sync is reseived or about every seconds when no activity from the client).
    Class CLIENT   (Inside RADIO_SYNC)
      All varibales in this class will be synced from the client to the server
      OBS! The variables most be in the same order in the server and client
      The variables can only be int, float, bool or string
      If you have the class RADIO_SYNC this inner class must exist or the system want start
    Class SERVER   (Inside RADIO_SYNC)
      All varibales in this class will be synced from the server to the client
      OBS! The variables most be in the same order in the server and client
      The variables can only be int, float, bool or string
      If you have the class RADIO_SYNC this inner class must exist or the system want start
    '''    
    
    @staticmethod
    def on_sync(seconds_since_last_ok_ping):
        '''
        seconds_since_last_ok_ping: Seconds since last sync that went OK (send or reseive)
        Will fire after every sync on the client (ones a second or when steelsquid_kiss_global.radio_interrupt() is executed)
        This will also be executed on server (When sync is reseived or about every seconds when no activity from the client).
        '''
        # Stop drive if no commadn in 1 second
        if seconds_since_last_ok_ping>1:
            RADIO_SYNC.CLIENT.cruise = False
            RADIO_PUSH_1.motor_left = 0
            RADIO_PUSH_1.motor_right = 0
            OUTPUT.drive(RADIO_PUSH_1.motor_left, RADIO_PUSH_1.motor_right)
        # Flash and sount when connection lost
        if seconds_since_last_ok_ping>10:
            LOOP.connection_lost=True
        else:
            LOOP.connection_lost=False
        LOOP.check_stuff()
        
        
    class CLIENT(object):
        '''
        All varibales in this class will be synced from the client to the server
        '''        
        # 0=off 1=smile 2=straight 3=sad 4=angry
        mood = 0

        # Use laser
        laser = False

        # Use headlight
        headlight = False

        # Use high beam
        highbeam = False

        # Cam light
        cam_light = False
        
        # Is cruise control enabled
        cruise = False

        
    class SERVER(object):
        '''
        All varibales in this class will be synced from the server to the client
        '''
        # Rover voltage (this rover)
        rover_voltage = -1.0

        # Rover ampere (this rover)
        rover_ampere = -1.0





class RADIO_PUSH_1(object):
    '''
    Class RADIO_PUSH_1 (to 4)
      If you use a HM-TRLR-S and it is enabled (set-flag  hmtrlrs_server) this class will make the client send the
      values of variables i this class to the server.
      You can have 4 RADIO_PUSH classes RADIO_PUSH_1 ti RADIO_PUSH_4
      This is faster than RADIO_SYNC because the client do not need to wait for ansver fron server
      OBS! The variables most be in the same order in the server and client
      It will not read anything back (if you want the sync values from the server use RADIO_SYNC)
      So all varibales in this class will be the same on the server and client, but client can only change the values.
      The variables can only be int, float, bool or string
      staticmethod: on_push()
        You must have this staticmethod or this functionality will not work
        On client it will fire before every push sent (ones every 0.01 second), return True or False
        True=send update to server, False=Do not send anything to server
        On server it will fire on every push received
    '''

    # Speed of the motors
    motor_left = 0
    motor_right = 0

    @staticmethod
    def on_push():
        '''
        You must have this staticmethod or this functionality will not work
        On client it will fire before every push sent (ones every 0.01 second), return True or False
        True=send update to server, False=Do not send anything to server
        On server it will fire on every push received
        '''
        OUTPUT.drive(RADIO_PUSH_1.motor_left, RADIO_PUSH_1.motor_right)






class RADIO_PUSH_2(object):
    '''
    Class RADIO_PUSH_1 (to 4)
      If you use a HM-TRLR-S and it is enabled (set-flag  hmtrlrs_server) this class will make the client send the
      values of variables i this class to the server.
      You can have 4 RADIO_PUSH classes RADIO_PUSH_1 ti RADIO_PUSH_4
      This is faster than RADIO_SYNC because the client do not need to wait for ansver fron server
      OBS! The variables most be in the same order in the server and client
      It will not read anything back (if you want the sync values from the server use RADIO_SYNC)
      So all varibales in this class will be the same on the server and client, but client can only change the values.
      staticmethod: on_push()
        You must have this staticmethod or this functionality will not work
        On client it will fire before every push sent (ones every 0.01 second), return True or False
        True=send update to server, False=Do not send anything to server
        On server it will fire on every push received
    '''
    # tilt/pan
    camera_pan = STATIC.servo_position_pan_start
    camera_tilt = STATIC.servo_position_tilt_start


    @staticmethod
    def on_push():
        '''
        You must have this staticmethod or this functionality will not work
        On client it will fire before every push sent (ones every 0.01 second), return True or False
        True=send update to server, False=Do not send anything to server
        On server it will fire on every push received
        '''
        OUTPUT.camera(RADIO_PUSH_2.camera_pan, RADIO_PUSH_2.camera_tilt)
        






class INPUT(object):
    '''
    Put input stuff her, maybe method to execute when a button is pressed.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    '''








class OUTPUT(object):
    '''
    Put output stuff her, maybe method that light a LED.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    '''
    last_left = 0
    last_right = 0
    
    @staticmethod
    def sum_flash():
        '''
        Sound the summer for short time
        ''' 
        #steelsquid_pi.po12_digital_out(1, True)
        #steelsquid_pi.po12_digital_out(2, True)
        #steelsquid_pi.po12_digital_out(3, True)
        time.sleep(0.02)
        #steelsquid_pi.po12_digital_out(1, False)
        #steelsquid_pi.po12_digital_out(2, False)
        #steelsquid_pi.po12_digital_out(3, False)
        

    @staticmethod
    def laser(status):
        '''
        Enable led list
        ''' 
        pass
        #steelsquid_pi.gpio_set(16, not status)
        

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
    def siren():
        '''
        Enable highbeam
        ''' 
        steelsquid_pi.mcp23017_flash(20, 5)
                

    @staticmethod
    def cam_light(status):
        '''
        Enable cam light
        ''' 
        steelsquid_pi.gpio_set(20, not status)


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
        if left!=None and left!=0:
            if left < -100 or left > 100:
                return
            if OUTPUT.last_left > 0 and left > 0:
                if left - OUTPUT.last_left > STATIC.motor_max_change:
                    return
            if OUTPUT.last_left > 0 and left < 0:
                if (left*-1) + OUTPUT.last_left > STATIC.motor_max_change:
                    return
            if OUTPUT.last_left < 0 and left < 0:
                if (left*-1) - (OUTPUT.last_left*-1) > STATIC.motor_max_change:
                    return
            if OUTPUT.last_left < 0 and left > 0:
                if left + (OUTPUT.last_left*-1) > STATIC.motor_max_change:
                    return
        if right!=None and right!=0:
            if right < -100 or right > 100:
                return
            if OUTPUT.last_right > 0 and right > 0:
                if left - OUTPUT.last_right > STATIC.motor_max_change:
                    return
            if OUTPUT.last_right > 0 and right < 0:
                if (right*-1) + OUTPUT.last_right > STATIC.motor_max_change:
                    return
            if OUTPUT.last_right < 0 and right < 0:
                if (right*-1) - (OUTPUT.last_right*-1) > STATIC.motor_max_change:
                    return
            if OUTPUT.last_right < 0 and right > 0:
                if right + (OUTPUT.last_right*-1) > STATIC.motor_max_change:
                    return

        OUTPUT.last_left = left
        OUTPUT.last_right = right
        # Cruise controll
        #if RADIO_SYNC.CLIENT.is_cruise_on:
        #    GLOBAL.cruise_enabled = True
        #    if left > right:
        #        diff = left - right
        #        left = STATIC.motor_max
        #        right = STATIC.motor_max - diff/2
        #    else:
        #        diff = right - left
        #        left = STATIC.motor_max - diff/2
        #       right = STATIC.motor_max
        # Check values
        if left>STATIC.motor_max:
            left = STATIC.motor_max
        elif left<STATIC.motor_max*-1:
            left = STATIC.motor_max*-1
        if right>STATIC.motor_max:
            right = STATIC.motor_max
        elif right<STATIC.motor_max*-1:
            right = STATIC.motor_max*-1
        steelsquid_pi.sabertooth_motor_speed(left, right, the_port="/dev/ttyUSB0")




class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
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
        OUTPUT.led_error_flash()


    @staticmethod
    def read_in_voltage():
        '''
        Read main in voltage
        '''
        v = steelsquid_pi.po12_adc_volt(8, samples=8) / 0.1195
        v = Decimal(v)
        v = round(v, 1)
        return v


    @staticmethod
    def read_in_ampere():
        '''
        Read main in ampere
        '''
        v = steelsquid_pi.po12_adc(7, samples=100)
        v = v - 503
        v = v * 0.003225806
        v = v / 0.026

        v = Decimal(v)
        v = round(v, 1)
        return v

        

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
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "wlan0", "down"])
            steelsquid_utils.execute_system_command_blind(["ip", "link", "set", "usb0", "up"])






