#!/usr/bin/python -OO


'''.
Remote for my 6wd drive rover "irrbloss"

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
from decimal import Decimal
import os
import steelsquid_tcp_radio
import steelsquid_oled_ssd1306
import math

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
    steelsquid_kiss_global.clear_modules_settings("kiss_irrbloss_remote")
    # Change hostname
    steelsquid_utils.set_hostname("irrbloss_remote")
    # Enable transeiver as client
    steelsquid_kiss_global.hmtrlrs_status("client")
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
    # Change GPIO for transceiver
    steelsquid_utils.set_parameter("hmtrlrs_config_gpio", str(STATIC.gpio_hmtrlrs_config))
    steelsquid_utils.set_parameter("hmtrlrs_reset_gpio", str(STATIC.gpio_hmtrlrs_reset))
    # Enable midori browser start on the composite screen
    steelsquid_utils.execute_system_command_blind(['steelsquid', 'browser-on', 'http://localhost/irrbloss'])
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
    remote_voltage_warning = 10.8  # 3.6V
    remote_voltage_min = 9.6       # 3.2V

    # Rover voltages(lipo 4s)
    rover_voltage_max = 16.8        # 4.2V
    rover_voltage_warning = 14.4    # 3.6V
    rover_voltage_min = 12.8        # 3.2V
    
    # interrup GPIO for mcp23017
    gpio_mcp23017_20_trig = 18
    gpio_mcp23017_21_trig = 24

    # GPIO for the HM-TRLR-S
    gpio_hmtrlrs_config = 25
    gpio_hmtrlrs_reset = 23

    # When system start move servo here
    servo_position_pan_start = 459

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

    # Remote voltage (this remote)
    remote_voltage = -1

    # Remote ampere (this remote)
    remote_ampere = -1

    # Show this on screen
    # 1 = Speek   2 = settings   3 = Map   4 = FPV
    show = 1

    # Stream audio
    audio = False

    # TImer
    timer = False
    timer_start = None
    timer_stop = None
        
    # Is cruise control enabled (this is the speed)
    cruise = 0

    # Save to disk
    save = False






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
    
    # Use external HDMI display
    use_external_hdmi = False
    
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
    
    # GPS home lat
    gps_home_lat = 0.0
    
    # GPS home longitud
    gps_home_long = 0.0
    
    # GPS home altitud
    gps_home_alt = 0

    



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
        steelsquid_oled_ssd1306.use_fix_font()
        # Startup message
        steelsquid_utils.shout("Steelsquid Irrbloss Remote start")
        # Load some settings
        if steelsquid_utils.is_empty(SETTINGS.control_ip) or steelsquid_utils.is_empty(SETTINGS.video_ip) or steelsquid_utils.is_empty(SETTINGS.audio_ip):
            ip = steelsquid_utils.network_ip_wan()
            if steelsquid_utils.is_empty(SETTINGS.control_ip):
                SETTINGS.control_ip = ip
            if steelsquid_utils.is_empty(SETTINGS.video_ip):
                SETTINGS.video_ip = ip
            if steelsquid_utils.is_empty(SETTINGS.audio_ip):
                SETTINGS.audio_ip = ip    
        # Reset some GPIO
        OUTPUT.sum_flash(led=False)
        OUTPUT.led_connected(False)
        OUTPUT.led_error(False)
        OUTPUT.led_gps_connected(False)
        OUTPUT.led_headlight(False)
        OUTPUT.led_laser(False)
        OUTPUT.led_siren(True)
        OUTPUT.led_center(True)
        OUTPUT.led_cruise(False)
        OUTPUT.led_audio(False)
        OUTPUT.led_timer(False)
        OUTPUT.led_save(False)
        OUTPUT.led_gps(False)
        try:
            GLOBAL.show(1)
        except:
            pass
        GLOBAL.set_mood(None)
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        # Set the on OK and ERROR callback methods...they just flash some LED
        steelsquid_utils.on_ok_callback_method=GLOBAL.on_ok
        steelsquid_utils.on_err_callback_method=GLOBAL.on_err
        # Start listen on buttons
        steelsquid_pi.mcp23017_click(21, 6, INPUT.button_use_external_hdmi, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 11, INPUT.button_siren, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 9, INPUT.button_cruise, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(20, 0, INPUT.button_laser, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 2, INPUT.button_cam_light, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 13, INPUT.button_headlight, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 15, INPUT.button_highbeam, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 4, INPUT.button_center, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 9, INPUT.button_fpv, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(21, 2, INPUT.button_audio, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 4, INPUT.button_save, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 13, INPUT.button_timer, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 15, INPUT.button_gps, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)

        steelsquid_pi.mcp23017_click(20, 11, INPUT.button_settings, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(21, 0, INPUT.button_map, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)

        steelsquid_pi.gpio_click(10, INPUT.button_mood_smile, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(9, INPUT.button_mood_straight, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(11, INPUT.button_mood_sad, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(5, INPUT.button_mood_angry, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(6, INPUT.button_control_radio, resistor=steelsquid_pi.PULL_UP)        
        steelsquid_pi.gpio_click(19, INPUT.button_control_wifi, resistor=steelsquid_pi.PULL_UP)        
        steelsquid_pi.gpio_click(20, INPUT.button_control_3g4g, resistor=steelsquid_pi.PULL_UP)        
        # Light the use external hdmi LED
        OUTPUT.led_use_external_hdmi(SETTINGS.use_external_hdmi)
        # Light the controll LED
        OUTPUT.led_control(SETTINGS.control)


    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        steelsquid_pi.po12_digital_out(1, False)
        steelsquid_pi.po12_digital_out(2, False)
        steelsquid_pi.po12_digital_out(3, False)
        steelsquid_pi.cleanup()
       
        
        



class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
        
    # tilt/pan 
    camera_pan = 0
    camera_tilt = 0

    # drive/steer/turn
    drive = 0
    steer = 0
    turn = 0
    
    # time_count
    time_count = 0
    
    #
    audio_killed = False
    video_killed = False
    hud_killed = False
    hud_txt = ""
    E = '.'
    D = ':'
    
    @staticmethod
    def update_lcd_and_other():
        '''
        Update the LCD
        Light LED
        ''' 
        try:
            # Wite to LCD
            if not DYNAMIC.stop_next_lcd_message:
                print_this = []
                print_this_hud = []
                # Time
                if LOOP.time_count==0 or LOOP.time_count==1 or LOOP.time_count==2:
                    tt = steelsquid_utils.get_date_time()
                    print_this.append(tt)
                    print_this.append('\n')
                    print_this_hud.append(tt)
                    print_this_hud.append(" .... ")
                else:
                    # Timer
                    if DYNAMIC.timer_start == None:
                        print_this.append("TIME ---\n")
                        print_this_hud.append("MISSION ................ \n")
                    else:
                        if DYNAMIC.timer:
                            diff = datetime.datetime.now() - DYNAMIC.timer_start
                            hours, remainder = divmod(diff.total_seconds(), 3600)
                            minutes, seconds = divmod(remainder, 60) 
                            if hours>9:
                                OUTPUT.led_timer(False)
                                DYNAMIC.timer_stop = datetime.datetime.now()
                                DYNAMIC.timer = False
                            else:
                                tt = "%d:%02d:%02d " % (int(hours), int(minutes), int(seconds))
                                print_this.append("TIME ")
                                print_this.append(tt)
                                print_this.append('\n')
                                print_this_hud.append("MISSION")
                                print_this_hud.append(LOOP.D)
                                print_this_hud.append(tt.ljust(16, LOOP.E))
                                print_this_hud.append(" ")
                        else:
                            diff = DYNAMIC.timer_stop - DYNAMIC.timer_start
                            hours, remainder = divmod(diff.total_seconds(), 3600)
                            minutes, seconds = divmod(remainder, 60) 
                            tt = "%d:%02d:%02d " % (int(hours), int(minutes), int(seconds))
                            print_this.append("TIME ")
                            print_this.append(tt)
                            print_this.append('\n')
                            print_this_hud.append("MISSION")
                            print_this_hud.append(LOOP.D)
                            print_this_hud.append(tt.ljust(16, LOOP.E))
                            print_this_hud.append(" ")
                LOOP.time_count = LOOP.time_count + 1
                if LOOP.time_count>=6:
                    LOOP.time_count=0
                # net/disk usage
                for name in os.listdir("/media"):
                    directory = os.path.join("/media", name)
                    if not os.path.isdir(directory) or name == "HiLink":
                        directory = None
                    else:
                        break
                if directory == None:
                    tt = "DATA " + RADIO_SYNC.SERVER.data_usage + "G "
                    print_this.append(tt)
                    print_this.append('\n')
                    tt = "DATA"+ LOOP.D + RADIO_SYNC.SERVER.data_usage + "G "
                    print_this_hud.append(tt.ljust(9, LOOP.E))
                else:
                    print_this.append("DATA " + (RADIO_SYNC.SERVER.data_usage + "G").ljust(6) + "USB " + str(steelsquid_utils.get_disk_usage(directory))+"%")
                    print_this.append('\n')
                    tt = "DATA" +LOOP.D + (RADIO_SYNC.SERVER.data_usage + "G ").ljust(9, LOOP.E) + " USB"+ LOOP.D + str(steelsquid_utils.get_disk_usage(directory))+"% "
                    print_this_hud.append(tt.ljust(27, LOOP.E))
                # Temp humidity
                print_this.append("TEMP " + (RADIO_SYNC.SERVER.temperature + "C").ljust(6)+"HUM " + RADIO_SYNC.SERVER.humidity + "%")
                print_this.append('\n')
                print_this_hud.append(" TEMP"+LOOP.D + (RADIO_SYNC.SERVER.temperature + "C ").ljust(8, LOOP.E)+" HUM"+LOOP.D + (RADIO_SYNC.SERVER.humidity + "% ").ljust(8, LOOP.E))
                # Voltage/Amp for the remote
                if DYNAMIC.remote_voltage != -1 and DYNAMIC.remote_ampere != -1:
                    print_this.append("REMO "+(str(steelsquid_utils.get_lipo_percentage(DYNAMIC.remote_voltage, 3))+"%").ljust(6)+ (str(DYNAMIC.remote_voltage) + "V").ljust(6) + str(DYNAMIC.remote_ampere) + "A")
                    print_this.append('\n')
                # Voltage/Amp for the rover
                if RADIO_SYNC.SERVER.rover_voltage != -1 and RADIO_SYNC.SERVER.rover_ampere != -1:
                    print_this.append("ROVE "+(str(steelsquid_utils.get_lipo_percentage(RADIO_SYNC.SERVER.rover_voltage, 4))+"%").ljust(6)+(str(RADIO_SYNC.SERVER.rover_voltage) + "V").ljust(6) + str(RADIO_SYNC.SERVER.rover_ampere) + "A  ")
                    print_this.append('\n')
                    print_this_hud.append((" BAT"+LOOP.D+(str(steelsquid_utils.get_lipo_percentage(RADIO_SYNC.SERVER.rover_voltage, 4))+"%")+LOOP.D+(str(RADIO_SYNC.SERVER.rover_voltage) + "V")+LOOP.D + (str(RADIO_SYNC.SERVER.rover_ampere) + "A ")).ljust(22, LOOP.E))
                # Cruise controll
                if DYNAMIC.cruise > 0:
                    print_this_hud.append((" CRUISE"+LOOP.D + str(DYNAMIC.cruise) + "%").ljust(18, LOOP.E))
                    OUTPUT.led_cruise(True)
                else:
                    print_this_hud.append(" CRUISE"+LOOP.D+"0% .... ")
                    OUTPUT.led_cruise(False)

                print_this_hud.append("CAMLIGHT")
                print_this_hud.append(LOOP.D)
                print_this_hud.append(GLOBAL.to_on_off(RADIO_SYNC.CLIENT.cam_light))

                print_this_hud.append("HEADLIGHT")
                print_this_hud.append(LOOP.D)
                print_this_hud.append(GLOBAL.to_on_off(RADIO_SYNC.CLIENT.headlight))

                print_this_hud.append("HIGHBEAM")
                print_this_hud.append(LOOP.D)
                print_this_hud.append(GLOBAL.to_on_off(RADIO_SYNC.CLIENT.highbeam))

                # GPS
                if RADIO_SYNC.SERVER.gps_long!=0 and RADIO_SYNC.SERVER.gps_lat!=0 and SETTINGS.gps_home_lat != 0:
                    RADIO_SYNC.CLIENT.gps_from_home = steelsquid_utils.distance(RADIO_SYNC.SERVER.gps_lat, RADIO_SYNC.SERVER.gps_long, SETTINGS.gps_home_lat, SETTINGS.gps_home_long)
                    print_this.append(("DIST " + str(RADIO_SYNC.CLIENT.gps_from_home)+"m").ljust(11))
                    print_this.append(str(RADIO_SYNC.SERVER.gps_speed))
                    print_this.append("km/h")                    
                    print_this_hud.append("DISTANCE")
                    print_this_hud.append(LOOP.D)
                    print_this_hud.append((str(RADIO_SYNC.CLIENT.gps_from_home)+"m ").ljust(10, LOOP.E))
                    print_this_hud.append(" DISTANCE")
                    print_this_hud.append(LOOP.D)
                    print_this_hud.append(str(RADIO_SYNC.SERVER.gps_speed)+"km/h")
                    

                if RADIO_SYNC.CLIENT.mood==1:
                    print_this_hud.append(":-) ")
                elif RADIO_SYNC.CLIENT.mood==2:
                    print_this_hud.append(":-| ")
                elif RADIO_SYNC.CLIENT.mood==3:
                    print_this_hud.append(":-( ")
                elif RADIO_SYNC.CLIENT.mood==4:
                    print_this_hud.append(">:-(")
                else:
                    print_this_hud.append("    ")

                LOOP.hud_txt = "".join(print_this_hud)
                #print LOOP.hud_txt
                # Write text to LCD
                if len(print_this)>0:
                    new_lcd_message = "".join(print_this)
                    if new_lcd_message!=DYNAMIC.last_lcd_message:
                        DYNAMIC.last_lcd_message = new_lcd_message
                        steelsquid_pi.ssd1306_write(new_lcd_message, 0)
            else:
                DYNAMIC.stop_next_lcd_message=False       
            # Set Network LED status
            OUTPUT.led_network(steelsquid_kiss_global.last_net)
            # Check connection
            if SETTINGS.control == 1:
                OUTPUT.led_connected(steelsquid_hmtrlrs.is_linked())
            else:
                OUTPUT.led_connected(steelsquid_tcp_radio.is_linked())
        except:
            steelsquid_utils.shout()
        return 1 # Execute this method again in 1 second


    @staticmethod
    def volt_amp_reader():
        '''
        Read voltage, amp
        ''' 
        # Read remote voltage
        DYNAMIC.remote_voltage = GLOBAL.read_in_voltage()
        DYNAMIC.remote_ampere = GLOBAL.read_in_ampere()
        # Low voltage beep
        beep = False
        if DYNAMIC.remote_voltage != -1 and DYNAMIC.remote_ampere != -1:
            if DYNAMIC.remote_voltage<STATIC.remote_voltage_warning:
                beep=True
        if RADIO_SYNC.SERVER.rover_voltage != -1 and RADIO_SYNC.SERVER.rover_ampere != -1:
            if RADIO_SYNC.SERVER.rover_voltage<STATIC.rover_voltage_warning:
                beep=True
        if beep:
            OUTPUT.sum_flash()
        return 0


    @staticmethod
    def pan_tilt_drive_steer_reader():
        '''
        Pan til reader
        ''' 
        p, t = GLOBAL.read_pan_tilt()
        if p>=-515 and p<=515 and t>=-515 and t<=515:
            LOOP.camera_pan = p
            LOOP.camera_tilt = t
        d, s, t= GLOBAL.read_drive_steer()
        if d>=-515 and d<=515 and s>=-515 and s<=515 and t>=-515 and t<=515:
            LOOP.drive = d;
            LOOP.steer = s
            LOOP.turn = t
        return 0


    @staticmethod
    def audio_stream():
        '''
        Audio stream
        ''' 
        if DYNAMIC.audio == True:
            LOOP.audio_killed = False
            if DYNAMIC.save:
                try:
                    for name in os.listdir("/media"):
                        directory = os.path.join("/media", name)
                        if not os.path.isdir(directory) or name == "HiLink":
                            directory = None
                        else:
                            break
                    if directory != None:
                        d = os.path.join(directory, steelsquid_utils.get_date())
                        t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+"_audio.wav")
                        try:
                            os.mkdir(d);
                        except:
                            pass
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=6603"])
                    try:
                        steelsquid_utils.execute_system_command(["nice", "-n", "8", "gst-launch-1.0", "-e", "udpsrc", "port=6603", "caps=application/x-rtp", "!", "rtppcmudepay", "!", "mulawdec", "!", "tee", "name=myt", "!", "queue", "!", "alsasink", "sync=true", "myt.", "!", "queue", "!", "audioconvert", "!", "audioresample", "!", "wavenc", "!", "filesink", "location="+t]) 
                    except:
                        thread.start_new_thread(GLOBAL._save_flash, (DYNAMIC.save,)) 
                except:
                    steelsquid_utils.shout()
            else:
                steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=6603"])
                try:
                    steelsquid_utils.execute_system_command(["nice", "-n", "8", "gst-launch-1.0", "-e", "udpsrc", "port=6603", "caps=application/x-rtp", "!", "rtppcmudepay", "!", "mulawdec", "!", "alsasink", "sync=true"]) 
                except:
                    pass
        elif not LOOP.audio_killed:
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=6603"])
            LOOP.audio_killed = True
        return 0.5


    @staticmethod
    def video_stream():
        '''
        Video stream
        ''' 
        if DYNAMIC.show == 4:
            LOOP.video_killed = False
            if DYNAMIC.save:
                try:
                    for name in os.listdir("/media"):
                        directory = os.path.join("/media", name)
                        if not os.path.isdir(directory) or name == "HiLink":
                            directory = None
                        else:
                            break
                    if directory != None:
                        d = os.path.join(directory, steelsquid_utils.get_date())
                        t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+"_video.mp4")
                        try:
                            os.mkdir(d);
                        except:
                            pass
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e tcpserversrc host=0.0.0.0 port=6602"])
                    try:
                        steelsquid_utils.execute_system_command(["nice", "-n", "5", "gst-launch-1.0", "-e", "tcpserversrc", "host=0.0.0.0", "port=6602", "!", "tee", "name=t", "!", "h264parse", "!", "omxh264dec", "!", "glimagesink", "sync=true", "t.", "!", "queue", "!", "video/x-h264,width="+SETTINGS.width+",height="+SETTINGS.height+",framerate=" + SETTINGS.fps + "/1,profile=constrained-baseline", "!", "h264parse", "!", "mp4mux", "!", "filesink", "location="+t]) 
                    except:
                        thread.start_new_thread(GLOBAL._save_flash, (DYNAMIC.save,)) 
                except:
                    steelsquid_utils.shout()
            else:
                steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e tcpserversrc host=0.0.0.0 port=6602"])
                time.sleep(0.5)
                try:
                    steelsquid_utils.execute_system_command(["nice", "-n", "5", "gst-launch-1.0", "-e", "tcpserversrc", "host=0.0.0.0", "port=6602", "!", "h264parse", "!", "omxh264dec", "!", "glimagesink", "sync=true"]) 
                except:
                    pass
        elif not LOOP.video_killed:
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e tcpserversrc host=0.0.0.0 port=6602"])
            LOOP.video_killed = True
        return 0.5
        
        
    @staticmethod
    def hud_stream():
        '''
        HUD stream
        ''' 
        if DYNAMIC.show == 4:
            LOOP.hud_killed = False
            if DYNAMIC.save:
                try:
                    for name in os.listdir("/media"):
                        directory = os.path.join("/media", name)
                        if not os.path.isdir(directory) or name == "HiLink":
                            directory = None
                        else:
                            break
                    if directory != None:
                        d = os.path.join(directory, steelsquid_utils.get_date())
                        t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+"_hud.mp4")
                        try:
                            os.mkdir(d);
                        except:
                            pass
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 videotestsrc"])
                    steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=1234"])
                    try:
                        steelsquid_utils.execute_system_command_blind(["nice", "-n", "10", "gst-launch-1.0", "-e", "udpsrc", "port=1234", "!", "application/x-rtp,media=video,clock-rate=90000,encoding-name=H264", "!", "rtph264depay", "!", "h264parse", "!", "mp4mux", "dts-method=0", "!", "filesink", "location="+t], wait_for_finish=False)
                        time.sleep(0.2)
                        while DYNAMIC.save:
                            
                            steelsquid_utils.execute_system_command_blind(["nice", "-n", "10", "gst-launch-1.0", "videotestsrc", "pattern=black", "!", "video/x-raw,width=" + SETTINGS.width + ",height=80,framerate=" + SETTINGS.fps + "/1", "!", "textoverlay", "text="+LOOP.hud_txt, "wrap-mode=0", "valignment=bottom", "halignment=center", "font-desc=FreeMono 10", "xpad=0", "ypad=0", "!", "omxh264enc", "target-bitrate="+SETTINGS.bitrate, "control-rate=3", "!", "rtph264pay", "!", "udpsink", "host=127.0.0.1", "port=1234"], wait_for_finish=False) 
                            time.sleep(2)
                            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 videotestsrc"])
                    except:
                        steelsquid_utils.shout()
                except:
                    steelsquid_utils.shout()
        elif not LOOP.hud_killed:
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 videotestsrc"])
            steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=1234"])
            LOOP.hud_killed = True
        return 0.5
        







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
        if seconds_since_last_ok_ping>3:
            DYNAMIC.cruise = 0
        # Is GPS connected
        OUTPUT.led_gps_connected(RADIO_SYNC.SERVER.gps_con)
        
        
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

        # GPS how long from home
        gps_from_home = 0

        
    class SERVER(object):
        '''
        All varibales in this class will be synced from the server to the client
        '''
        # Rover voltage (this rover)
        rover_voltage = -1.0

        # Rover ampere (this rover)
        rover_ampere = -1

        # Temp
        temperature = "---"

        # Humidity
        humidity = "---"

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
    # Only want to send sertant number of stopp signals
    _sent_zero_count = 0

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
        # If move youstick stop cruisecontroll
        if LOOP.drive > 100 or LOOP.steer > 100 or LOOP.drive < -100 or LOOP.steer < -100:
            DYNAMIC.cruise=0
        # Cruise controll
        if DYNAMIC.cruise>0:
            RADIO_PUSH_1._sent_zero_count = 0
            # Remap the joystick range
            turn = int(steelsquid_utils.remap(LOOP.turn, -510, 510, STATIC.motor_max*-1, STATIC.motor_max))
            # Drive 
            turn = turn/10
            motor_left = DYNAMIC.cruise + turn
            motor_right = DYNAMIC.cruise - turn

            # Chack that the waluses is in range (-100 to 100)
            if motor_right>STATIC.motor_max:
                motor_right = STATIC.motor_max
            elif motor_right<STATIC.motor_max*-1:
                motor_right = STATIC.motor_max*-1
            if motor_left>STATIC.motor_max:
                motor_left = STATIC.motor_max
            elif motor_left<STATIC.motor_max*-1:
                motor_left = STATIC.motor_max*-1
            # Set the value that will be sent to the server
            RADIO_PUSH_1.motor_left=motor_left
            RADIO_PUSH_1.motor_right=motor_right
            
            return True
        elif LOOP.turn != 0:
            RADIO_PUSH_1._sent_zero_count = 0
            # Remap the joystick range
            turn = int(steelsquid_utils.remap(LOOP.turn, -510, 510, STATIC.motor_max*-1, STATIC.motor_max))
            # Drive 
            turn = turn/2
            motor_left = turn
            motor_right = turn*-1

            # Chack that the waluses is in range (-100 to 100)
            if motor_right>STATIC.motor_max:
                motor_right = STATIC.motor_max
            elif motor_right<STATIC.motor_max*-1:
                motor_right = STATIC.motor_max*-1
            if motor_left>STATIC.motor_max:
                motor_left = STATIC.motor_max
            elif motor_left<STATIC.motor_max*-1:
                motor_left = STATIC.motor_max*-1
                
            # Set the value that will be sent to the server
            RADIO_PUSH_1.motor_left=motor_left
            RADIO_PUSH_1.motor_right=motor_right
            
            return True
        elif LOOP.drive != 0 or LOOP.steer!=0:
            RADIO_PUSH_1._sent_zero_count = 0
            # Remap the joystick range
            drive = int(steelsquid_utils.remap(LOOP.drive, -510, 510, STATIC.motor_max*-1, STATIC.motor_max))
            steer = int(steelsquid_utils.remap(LOOP.steer, -510, 510, STATIC.motor_max*-1, STATIC.motor_max))
            
            # Drive 
            steer = steer/4
            motor_left = drive
            motor_right = drive
            motor_left = motor_left - steer
            motor_right = motor_right + steer

            # Chack that the waluses is in range (-100 to 100)
            if motor_right>STATIC.motor_max:
                motor_right = STATIC.motor_max
            elif motor_right<STATIC.motor_max*-1:
                motor_right = STATIC.motor_max*-1
            if motor_left>STATIC.motor_max:
                motor_left = STATIC.motor_max
            elif motor_left<STATIC.motor_max*-1:
                motor_left = STATIC.motor_max*-1
                
            # Set the value that will be sent to the server
            RADIO_PUSH_1.motor_left=motor_left
            RADIO_PUSH_1.motor_right=motor_right
            
            return True
        else:
            if RADIO_PUSH_1._sent_zero_count<6:
                RADIO_PUSH_1._sent_zero_count = RADIO_PUSH_1._sent_zero_count + 1
                RADIO_PUSH_1.motor_left = 0
                RADIO_PUSH_1.motor_right = 0
                return True
            else:
                return False






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
        if LOOP.camera_pan != 0 or LOOP.camera_tilt!=0:
            if SETTINGS.control == 1:
                pan = RADIO_PUSH_2.camera_pan + int(LOOP.camera_pan/30)
                tilt = RADIO_PUSH_2.camera_tilt - int(LOOP.camera_tilt/30)
            else:
                pan = RADIO_PUSH_2.camera_pan + int(LOOP.camera_pan/100)
                tilt = RADIO_PUSH_2.camera_tilt - int(LOOP.camera_tilt/100)
            if pan<STATIC.servo_position_pan_min:
                pan = STATIC.servo_position_pan_min
            elif pan>STATIC.servo_position_pan_max:
                pan = STATIC.servo_position_pan_max
            if tilt<STATIC.servo_position_tilt_min:
                tilt = STATIC.servo_position_tilt_min
            elif tilt>STATIC.servo_position_tilt_max:
                tilt = STATIC.servo_position_tilt_max
            RADIO_PUSH_2.camera_pan = pan
            RADIO_PUSH_2.camera_tilt = tilt
            return True
        # Nothing
        else:
            return False






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
    def settings_save(session_id, parameters):
        '''
        Set the control/video/audio ip
        '''
        para = []
        SETTINGS.control_ip = parameters[0]
        para.append(parameters[0])
        SETTINGS.video_ip = parameters[1]
        para.append(parameters[1])
        SETTINGS.audio_ip = parameters[2]
        para.append(parameters[2])
        resolution = parameters[3]
        r= resolution.split(':')
        SETTINGS.width = r[0]
        para.append(r[0])
        SETTINGS.height = r[1]
        para.append(r[1])
        SETTINGS.fps = parameters[4]
        para.append(parameters[4])
        SETTINGS.bitrate = parameters[5]
        para.append(parameters[5])
        para.append("1234567")
        steelsquid_kiss_global.save_module_settings()
        try:
            steelsquid_hmtrlrs.request("settings_save", para)
        except:
            try:
                steelsquid_hmtrlrs.request("settings_save", para)
            except:
                try:
                    steelsquid_hmtrlrs.request("settings_save", para)
                except:
                    pass
        steelsquid_kiss_global.restart(delay=2)
        return []


    @staticmethod
    def settings_get(session_id, parameters):
        '''
        Get the control/video/audio ip
        '''
        SETTINGS.width, SETTINGS.height
        return [SETTINGS.control_ip, SETTINGS.video_ip, SETTINGS.audio_ip, SETTINGS.width+":"+SETTINGS.height, SETTINGS.fps, SETTINGS.bitrate]

    
    @staticmethod
    def get_lan_ip(session_id, parameters):
        '''
        Get lan ip
        '''
        return [steelsquid_utils.network_ip()]

    
    @staticmethod
    def get_wan_ip(session_id, parameters):
        '''
        Get lan ip
        '''
        return [steelsquid_utils.network_ip_wan()]
        

    @staticmethod
    def show(session_id, parameters):
        '''
        Get the show
        '''
        return [DYNAMIC.show]



    @staticmethod
    def gps(session_id, parameters):
        '''
        Get the map
        '''
        return [SETTINGS.gps_home_lat, SETTINGS.gps_home_long, RADIO_SYNC.SERVER.gps_lat, RADIO_SYNC.SERVER.gps_long]


    @staticmethod
    def speek(session_id, parameters):
        '''
        Get the show
        '''
        if SETTINGS.control == 1:
            steelsquid_hmtrlrs.request("speek", parameters)
        else:
            steelsquid_tcp_radio.request("speek", parameters)

        

    @staticmethod
    def network(session_id, parameters):
        '''
        Get network
        '''
        return [steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_wan_ip]
        






class INPUT(object):
    '''
    Put input stuff her, maybe method to execute when a button is pressed.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    '''

    @staticmethod
    def button_mood_smile(pin):
        '''
        Push the smile button
        '''        
        GLOBAL.set_mood(1)


    @staticmethod
    def button_mood_straight(pin):
        '''
        Push the straight button
        '''        
        GLOBAL.set_mood(2)


    @staticmethod
    def button_mood_sad(pin):
        '''
        Push the sad button
        '''        
        GLOBAL.set_mood(3)


    @staticmethod
    def button_mood_angry(pin):
        '''
        Push the angry button
        '''        
        GLOBAL.set_mood(4)
        

    @staticmethod
    def button_control_radio(pin):
        '''
        Push the radio control button
        '''        
        GLOBAL.set_control(1)


    @staticmethod
    def button_control_wifi(pin):
        '''
        Push the radio control button
        '''        
        GLOBAL.set_control(2)


    @staticmethod
    def button_control_3g4g(pin):
        '''
        Push the radio control button
        '''        
        GLOBAL.set_control(3)
 

    @staticmethod
    def button_use_external_hdmi(address, pin):
        '''
        Toggle use of external HDMI monitor
        '''        
        GLOBAL.toggle_use_external_hdmi()


    @staticmethod
    def button_laser(address, pin):
        '''
        Toggle use of laser
        '''        
        RADIO_SYNC.CLIENT.laser = not RADIO_SYNC.CLIENT.laser
        OUTPUT.led_laser(RADIO_SYNC.CLIENT.laser)
        
        
    @staticmethod
    def button_headlight(address, pin):
        '''
        Toggle headlight
        '''        
        RADIO_SYNC.CLIENT.headlight = not RADIO_SYNC.CLIENT.headlight
        OUTPUT.led_headlight(RADIO_SYNC.CLIENT.headlight)
        
        
    @staticmethod
    def button_highbeam(address, pin):
        '''
        Toggle highbeam
        '''        
        RADIO_SYNC.CLIENT.highbeam = not RADIO_SYNC.CLIENT.highbeam
        OUTPUT.led_highbeam(RADIO_SYNC.CLIENT.highbeam)
        
        
    @staticmethod
    def button_siren(address, pin):
        '''
        Siren for 1 second
        '''        
        if SETTINGS.control == 1:
            steelsquid_hmtrlrs.request("siren")
        else:
            steelsquid_tcp_radio.request("siren")
        OUTPUT.led_siren()


    @staticmethod
    def button_center(address, pin):
        '''
        Center camera
        '''        
        OUTPUT.led_center()
        RADIO_PUSH_2.camera_pan = STATIC.servo_position_pan_start
        RADIO_PUSH_2.camera_tilt = STATIC.servo_position_tilt_start
        if SETTINGS.control == 1:
            steelsquid_kiss_global.radio_interrupt(check_on_push=False)        
        else:
            steelsquid_kiss_global.tcp_radio_interrupt(check_on_push=False)        
        

    @staticmethod
    def button_cam_light(address, pin):
        '''
        Camera loght
        '''        
        RADIO_SYNC.CLIENT.cam_light = not RADIO_SYNC.CLIENT.cam_light
        OUTPUT.led_cam_light(RADIO_SYNC.CLIENT.cam_light)


    @staticmethod
    def button_cruise(address, pin):
        '''
        Camera loght
        '''        
        OUTPUT.led_cruise(DYNAMIC.cruise>0)
        if DYNAMIC.cruise < STATIC.motor_max:
            DYNAMIC.cruise = DYNAMIC.cruise + 5


    @staticmethod
    def button_fpv(address, pin):
        '''
        FPV
        1 = Speek   2 = settings   3 = Map   4 = FPV
        '''
        if DYNAMIC.show == 4:
            GLOBAL.show(1)
        else:
            GLOBAL.show(4)


    @staticmethod
    def button_settings(address, pin):
        '''
        settings
        1 = Speek   2 = settings   3 = Map   4 = FPV
        '''        
        if DYNAMIC.show == 2:
            GLOBAL.show(1)
        else:
            GLOBAL.show(2)


    @staticmethod
    def button_map(address, pin):
        '''
        map
        1 = Speek   2 = settings   3 = Map   4 = FPV
        '''        
        if DYNAMIC.show == 3:
            GLOBAL.show(1)
        else:
            GLOBAL.show(3)
                
 
    @staticmethod
    def button_audio(address, pin):
        '''
        Toggle use of audio
        '''        
        GLOBAL.audio(not DYNAMIC.audio)
        
        
    @staticmethod
    def button_timer(address, pin):
        '''
        button_timer
        '''        
        # TImer
        if DYNAMIC.timer:
            OUTPUT.led_timer(False)
            DYNAMIC.timer_stop = datetime.datetime.now()
            DYNAMIC.timer = False
        else:
            OUTPUT.led_timer(True)
            DYNAMIC.timer_start = datetime.datetime.now()
            DYNAMIC.timer = True


    @staticmethod
    def button_save(address, pin):
        '''
        button_timer
        '''        
        GLOBAL.save(not DYNAMIC.save)


    @staticmethod
    def button_gps(address, pin):
        '''
        button_timer
        '''        
        OUTPUT.led_gps()
        SETTINGS.gps_home_lat=RADIO_SYNC.SERVER.gps_lat
        SETTINGS.gps_home_long=RADIO_SYNC.SERVER.gps_long
        SETTINGS.gps_home_alt=SETTINGS.gps_home_alt
        steelsquid_kiss_global.save_module_settings()








class OUTPUT(object):
    '''
    Put output stuff her, maybe method that light a LED.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    '''

    @staticmethod
    def led_network(status):
        '''
        Network connected LED
        ''' 
        steelsquid_pi.gpio_set(16, status)


    @staticmethod
    def led_connected(status):
        '''
        Connected to rover
        ''' 
        steelsquid_pi.gpio_set(7, status)


    @staticmethod
    def led_gps_connected(status):
        '''
        Connected to rover
        ''' 
        steelsquid_pi.gpio_set(12, status)


    @staticmethod
    def led_error_flash():
        '''
        Flash the error led
        ''' 
        steelsquid_pi.gpio_flash(8)


    @staticmethod
    def led_error(status):
        '''
        Error led
        ''' 
        steelsquid_pi.gpio_set(8, status)

        
    @staticmethod
    def led_mood(mood):
        '''
        Light the mood led
        1=smile 2=straight 3=sad 4=angry
        ''' 
        if mood == 1:
            steelsquid_pi.gpio_set(4, True)
            steelsquid_pi.gpio_set(17, False)
            steelsquid_pi.gpio_set(27, False)
            steelsquid_pi.gpio_set(22, False)
        elif mood == 2:
            steelsquid_pi.gpio_set(4, False)
            steelsquid_pi.gpio_set(17, True)
            steelsquid_pi.gpio_set(27, False)
            steelsquid_pi.gpio_set(22, False)
        elif mood == 3:
            steelsquid_pi.gpio_set(4, False)
            steelsquid_pi.gpio_set(17, False)
            steelsquid_pi.gpio_set(27, True)
            steelsquid_pi.gpio_set(22, False)
        elif mood == 4:
            steelsquid_pi.gpio_set(4, False)
            steelsquid_pi.gpio_set(17, False)
            steelsquid_pi.gpio_set(27, False)
            steelsquid_pi.gpio_set(22, True)
        else:
            steelsquid_pi.gpio_set(4, False)
            steelsquid_pi.gpio_set(17, False)
            steelsquid_pi.gpio_set(27, False)
            steelsquid_pi.gpio_set(22, False)
            

    @staticmethod
    def led_control(con):
        '''
        Light the control led
        1=radio 2=wifi 3=3G/4G
        ''' 
        if con == 1:
            steelsquid_pi.gpio_set(13, True)
            steelsquid_pi.gpio_set(26, False)
            steelsquid_pi.gpio_set(21, False)
        elif con == 2:
            steelsquid_pi.gpio_set(13, False)
            steelsquid_pi.gpio_set(26, True)
            steelsquid_pi.gpio_set(21, False)
        elif con == 3:
            steelsquid_pi.gpio_set(13, False)
            steelsquid_pi.gpio_set(26, False)
            steelsquid_pi.gpio_set(21, True)


    @staticmethod
    def led_use_external_hdmi(status):
        '''
        Use external hdmi monitor LED
        ''' 
        steelsquid_pi.mcp23017_set(21, 7, status)


    @staticmethod
    def led_audio(status):
        '''
        Use 
        ''' 
        steelsquid_pi.mcp23017_set(21, 3, status)
        
       
    @staticmethod
    def sum_flash(led=True):
        '''
        Sound the summer for short time
        ''' 
        if led:
            steelsquid_pi.gpio_set(8, True)
        #steelsquid_pi.po12_digital_out(1, True)
        #steelsquid_pi.po12_digital_out(2, True)
        #steelsquid_pi.po12_digital_out(3, True)
        time.sleep(0.01)
        steelsquid_pi.po12_digital_out(1, False)
        steelsquid_pi.po12_digital_out(2, False)
        steelsquid_pi.po12_digital_out(3, False)
        if led:
            steelsquid_pi.gpio_set(8, False)
        

    @staticmethod
    def led_laser(status):
        '''
        Light the laser LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 1, status)

    
    @staticmethod
    def led_headlight(status):
        '''
        Light the hadlight LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 12, status)

    
    @staticmethod
    def led_highbeam(status):
        '''
        Light the highbeam LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 14, status)                 

    
    @staticmethod
    def led_cam_light(status):
        '''
        Light the cam light LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 3, status)   
        
    
    @staticmethod
    def led_siren(turnOff=False):
        '''
        Light the siren LED for a second
        ''' 
        if turnOff:
            steelsquid_pi.mcp23017_set(21, 10, False)                 
        else:
            steelsquid_pi.mcp23017_flash(21, 10, seconds=1)                 


    @staticmethod
    def led_center(turnOff=False):
        '''
        Light the center for a second
        ''' 
        if turnOff:
            steelsquid_pi.mcp23017_set(20, 5, False)                 
        else:
            steelsquid_pi.mcp23017_flash(20, 5, seconds=1)                 
        

    @staticmethod
    def led_cruise(status):
        '''
        Light the cruise LED
        ''' 
        steelsquid_pi.mcp23017_set(21, 8, status)   
        
        

    @staticmethod
    def led_fpv(status):
        '''
        Light the fpv LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 8, status)           


    @staticmethod
    def led_settings(status):
        '''
        Light the settings LED
        ''' 
        steelsquid_pi.mcp23017_set(20, 10, status)      


    @staticmethod
    def led_map(status):
        '''
        Light the map LED
        ''' 
        steelsquid_pi.mcp23017_set(21, 1, status)      


    @staticmethod
    def led_timer(status):
        '''
        led_timer
        ''' 
        steelsquid_pi.mcp23017_set(21, 12, status)


    @staticmethod
    def led_save(status):
        '''
        led_timer
        ''' 
        steelsquid_pi.mcp23017_set(21, 5, status)  


    @staticmethod
    def led_gps(status=None):
        '''
        Use external hdmi monitor LED
        ''' 
        if status==None:
            steelsquid_pi.mcp23017_flash(21, 14)
        else:
            steelsquid_pi.mcp23017_set(21, 14, status)
        
        
 





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
        v = steelsquid_pi.po12_adc_volt(8, samples=8) / 0.114
        v = Decimal(v)
        v = round(v, 1)
        return v


    @staticmethod
    def read_in_ampere():
        '''
        Read main in ampere
        '''
        v = steelsquid_pi.po12_adc(7, samples=100)
        v = v - 510
        v = v * 0.003225806
        v = v / 0.027
        v = Decimal(v)
        v = math.ceil(v)
        return int(v)


    @staticmethod
    def read_pan_tilt():
        '''
        Read pan and tilt
        '''
        pan = steelsquid_pi.po12_adc(5, samples=3)
        pan = pan - 515
        if pan > -20 and pan < 20:
            pan = 0
        tilt = steelsquid_pi.po12_adc(4, samples=3)
        tilt = 515 - tilt
        if tilt > -20 and tilt < 20:
            tilt = 0
        return pan, tilt


    @staticmethod
    def read_drive_steer():
        '''
        Read drive and steer
        '''
        drive = steelsquid_pi.po12_adc(1, samples=3)
        drive = drive - 515
        if drive > -20 and drive < 20:
            drive = 0
        steer = steelsquid_pi.po12_adc(2, samples=3)
        steer = 515 - steer
        if steer > -20 and steer < 20:
            steer = 0
        turn = steelsquid_pi.po12_adc(3, samples=3)
        turn = 515 - turn
        if turn > -50 and turn < 50:
            turn = 0
        return drive, steer, turn
        

    @staticmethod
    def set_mood(mood):
        '''
        Set mood
        0=off 1=smile 2=straight 3=sad 4=angry
        '''        
        if mood == None:
            mood = 0
        elif mood == RADIO_SYNC.CLIENT.mood:
            mood = 0
        OUTPUT.led_mood(mood)
        RADIO_SYNC.CLIENT.mood = mood
        if SETTINGS.control == 1:
            steelsquid_kiss_global.radio_interrupt()
        else:
            steelsquid_kiss_global.tcp_radio_interrupt()
        

    @staticmethod
    def set_control(con):
        '''
        Set with way to control rover
        1=radio 2=wifi 3=3g4g
        '''        
        try:
            steelsquid_hmtrlrs.request("set_control", [con, "1234567"])
        except:
            time.sleep(1)
            try:
                steelsquid_hmtrlrs.request("set_control", [con, "1234567"])
            except:
                time.sleep(1)
                try:
                    steelsquid_hmtrlrs.request("set_control", [con, "1234567"])
                except:
                    pass
        OUTPUT.led_control(con)
        SETTINGS.control = con
        steelsquid_kiss_global.save_module_settings()
        if SETTINGS.control==1:
            steelsquid_kiss_global.tcp_radio_disable()
        else:
            steelsquid_kiss_global.tcp_radio_server(True)
        time.sleep(0.5)
        steelsquid_kiss_global.restart(delay=4)
        


    @staticmethod
    def toggle_use_external_hdmi():
        '''
        Toggle use of external HDMI monitor
        Will reboot....
        '''        
        SETTINGS.use_external_hdmi = not SETTINGS.use_external_hdmi
        steelsquid_kiss_global.save_module_settings()
        OUTPUT.led_use_external_hdmi(SETTINGS.use_external_hdmi)
        if SETTINGS.use_external_hdmi:
            os.system("steelsquid monitor-0")
            os.system("steelsquid monitor-csi-off")
        else:
            os.system("steelsquid monitor-180")
            os.system("steelsquid monitor-csi-on")
        steelsquid_kiss_global.reboot()


    @staticmethod
    def audio(on, do_save=True):
        '''
        Audiohttps://www.google.se/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwji77mO9brRAhWB_iwKHX_ID90QFggdMAA&url=http%3A%2F%2Fstackoverflow.com%2Fquestions%2F8814383%2Fsending-sigint-ctrl-c-to-program-running-in-eclipse-console&usg=AFQjCNEPAt6pEUEgpOOCO5nnLxJFC2m6Aw&sig2=4NouXbTWRRmu7wwZNd4jnA&bvm=bv.143423383,d.bGg
        '''        
        if SETTINGS.control == 1:
            steelsquid_hmtrlrs.request("stream_audio", [on])
        else:
            steelsquid_tcp_radio.request("stream_audio", [on])
        DYNAMIC.audio = on
        if do_save and DYNAMIC.save:            
            GLOBAL.save(Falsee)
        steelsquid_utils.execute_system_command_blind(["pkill", "-f", "gst-launch-1.0 -e udpsrc port=6603"])
        OUTPUT.led_audio(DYNAMIC.audio)


    @staticmethod
    def show(this, do_save=True):
        '''
        Show this on screen
        1 = Speek   2 = settings   3 = Map   4 = FPV
        '''        
        do_screen = DYNAMIC.save
        if this == 4:
            if SETTINGS.control == 1:
                steelsquid_hmtrlrs.request("stream_video", [True])
            else:
                steelsquid_tcp_radio.request("stream_video", [True])
        else:
            if SETTINGS.control == 1:
                steelsquid_hmtrlrs.request("stream_video", [False])
            else:
                steelsquid_tcp_radio.request("stream_video", [False])
            if do_save and DYNAMIC.save:            
                GLOBAL.save(False)
        steelsquid_utils.execute_system_command_blind(["pkill", "-INT", "gst-launch-1.0"])
        DYNAMIC.show = this
        if DYNAMIC.show == 1:
            OUTPUT.led_settings(False)
            OUTPUT.led_map(False)
            OUTPUT.led_fpv(False)
        elif DYNAMIC.show == 2:
            OUTPUT.led_settings(True)
            OUTPUT.led_map(False)
            OUTPUT.led_fpv(False)
        elif DYNAMIC.show == 3:
            OUTPUT.led_settings(False)
            OUTPUT.led_map(True)
            OUTPUT.led_fpv(False)
            if do_screen:
                t = GLOBAL.get_save_file("_map.png")
                steelsquid_utils.execute_delay(2, steelsquid_utils.execute_system_command, (["/root/screen", t],))
        elif DYNAMIC.show == 4:
            OUTPUT.led_settings(False)
            OUTPUT.led_map(False)
            OUTPUT.led_fpv(True)


    @staticmethod
    def save(on):
        '''
        Save to disk
        '''        
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        if directory == None:
            thread.start_new_thread(GLOBAL._save_flash, ()) 
        else:
            DYNAMIC.save = on
            OUTPUT.led_save(DYNAMIC.save)
            if DYNAMIC.save:
                try:
                    GLOBAL.show(4, do_save=False)
                except:
                    pass
                try:
                    GLOBAL.audio(True, do_save=False)
                except:
                    pass
            else:
                try:
                    GLOBAL.show(1, do_save=False)
                except:
                    pass
                try:
                    GLOBAL.audio(False, do_save=False)
                except:
                    pass



    @staticmethod
    def _save_flash(leav_on=False):
        '''
        Flash LED
        '''        
        for i in range(20):
            steelsquid_pi.mcp23017_set(21, 5, i%2==0)  
            time.sleep(0.1)
        steelsquid_pi.mcp23017_set(21, 5, leav_on)  
        
        
    @staticmethod
    def to_on_off(boolean):
        '''
        to_on_off
        '''
        if boolean:
            return "On ..... "
        else:
            return "Off .... "        
            
            
    @staticmethod
    def get_save_file(fname):
        '''
        get_save_file
        '''
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        if directory != None:
            d = os.path.join(directory, steelsquid_utils.get_date())
            t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+fname)
            try:
                os.mkdir(d);
            except:
                pass
        return t
            
