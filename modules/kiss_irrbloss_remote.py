#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

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
import steelsquid_gstreamer
from espeak import espeak
import steelsquid_digole


espeak.set_voice("en+f5")

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
    steelsquid_kiss_global.clear_modules_settings("kiss_irrbloss_remote")
    # Change hostname
    steelsquid_utils.set_hostname("irrbloss_remote")
    # Enable transeiver as client
    steelsquid_kiss_global.radio_hmtrlrs(False)
    # Enable tcp radio as server and then send command to the host
    steelsquid_kiss_global.radio_tcp(True, steelsquid_utils.network_ip_wan())
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
    # Change GPIO for transceiver
    steelsquid_utils.set_parameter("hmtrlrs_config_gpio", str(STATIC.gpio_hmtrlrs_config))
    steelsquid_utils.set_parameter("hmtrlrs_reset_gpio", str(STATIC.gpio_hmtrlrs_reset))
    # Enable midori browser start on the composite screen
    steelsquid_utils.execute_system_command_blind(['steelsquid', 'mbrowser-on', 'http://localhost/irrbloss'])
    # Set hdmi resoulrion
    steelsquid_utils.execute_system_command_blind(['steelsquid', 'hdmi-res', '800', '480'])
    # Do not print IP to LCD automaticaly
    steelsquid_utils.set_flag("no_net_to_lcd")



def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
              (execute: steelsquid module XXX off theArgument)
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

    # Default sleep time between IO polling
    sleep = 0.06

    # Number of seconds when connection probably is lost 
    connection_lost_timeout = 6
    
    # Remote voltages(lipo 3s) 
    remote_voltage_max = 12.6      # 4.2V
    remote_voltage_warning = 10.8  # 3.6V
    remote_voltage_min = 9.6       # 3.2V

    # Rover voltages(lipo 4s)
    rover_voltage_max = 16.8        # 4.2V
    rover_voltage_warning = 14.4    # 3.6V
    rover_voltage_min = 12.8        # 3.2V

    # Battery ampere/hour
    rover_amp_hour = 30             # 3 * 10Ah
    
    # interrup GPIO for mcp23017
    gpio_mcp23017_20_trig = 18
    gpio_mcp23017_21_trig = 24

    # GPIO for the HM-TRLR-S
    gpio_hmtrlrs_config = 25
    gpio_hmtrlrs_reset = 23

    # When system start move servo here
    servo_position_tilt_start = 400

    # Max Servo position
    servo_position_tilt_max = 470

    # Min Servo position
    servo_position_tilt_min = 320







##############################################################################################################################################################################################
class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe to enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''

    # TImer
    timer = False
    timer_start = None
    timer_stop = None
        
    # Hud text
    hud_text=""

    # Ping time to rover (99 = no connection)
    ping_time = 99

    # Force close of streams
    force_stream_close = False

    # mute sound
    mute = False

    # Last time mood 5actovated
    last_mood_away = None

    # dis
    dis=0
    unit="meter"









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
        # Fixed font on LCD...want to have columns
        steelsquid_oled_ssd1306.use_fix_font()
        # Startup message
        steelsquid_utils.shout("Steelsquid Irrbloss Remote start")
        # Set the on OK and ERROR callback methods...they just flash some LED
        steelsquid_utils.on_ok_callback_method=UTILS.on_ok
        steelsquid_utils.on_err_callback_method=UTILS.on_err
        # Reset some GPIO
        IO.OUTPUT.sum_flash(led=False)
        IO.OUTPUT.led_connected(False)
        IO.OUTPUT.led_error(False)
        IO.OUTPUT.led_gps_connected(False)
        IO.OUTPUT.led_low_light(SETTINGS.low_light)
        IO.OUTPUT.led_laser(False)
        IO.OUTPUT.led_tcp_video(SETTINGS.tcp_video)
        IO.OUTPUT.led_cruise(False)
        IO.OUTPUT.led_mute(False)
        IO.OUTPUT.led_timer(False)
        IO.OUTPUT.led_save(False)

        IO.OUTPUT.led_spec_turn(False)
        IO.OUTPUT.led_away(False)
        IO.OUTPUT.led_siren(True)
        # Show the map interface on screen
        try:
            DO.show(3)
        except:
            pass
        # no mode
        DO.mood(None)
        # Light the use external hdmi LED
        IO.OUTPUT.led_use_external_hdmi(SETTINGS.use_external_hdmi)
        # Light the controll LED
        IO.OUTPUT.led_control(SETTINGS.control)
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        # Load some settings
        if steelsquid_utils.is_empty(SETTINGS.control_ip) or steelsquid_utils.is_empty(SETTINGS.video_ip) or steelsquid_utils.is_empty(SETTINGS.audio_ip):
            ip = steelsquid_utils.network_ip_wan()
            if steelsquid_utils.is_empty(SETTINGS.control_ip):
                SETTINGS.control_ip = ip
            if steelsquid_utils.is_empty(SETTINGS.video_ip):
                SETTINGS.video_ip = ip
            if steelsquid_utils.is_empty(SETTINGS.audio_ip):
                SETTINGS.audio_ip = ip    
        # Setup gstreamer
        steelsquid_gstreamer.setup_display_speaker(SETTINGS.video_ip, 6607, SETTINGS.audio_ip, 6608, SETTINGS.width, SETTINGS.height, SETTINGS.fps, UTILS.get_save_directory, SETTINGS.tcp_video, SETTINGS.low_light)
        # Max volume
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "100%"], wait_for_finish=True)
        steelsquid_utils.execute_system_command_blind(["alsactl", "store"], wait_for_finish=True)
        # Write header texttodisplay
        steelsquid_digole.text_position(0, 0)
        steelsquid_digole.write_text_line(steelsquid_utils.get_date_time() +"   00:00:00", padding=17)
        
        steelsquid_digole.write_text_line("DATA USAGE", padding=5)
        steelsquid_digole.write_text_line("USB USAGE", padding=5)
        steelsquid_digole.write_text_line("BANDWIDTH", padding=5)
        steelsquid_digole.write_text_line("LATENCY", padding=17)
        
        steelsquid_digole.write_text_line("VOLTAGE", padding=5)
        steelsquid_digole.write_text_line("CURRENT", padding=17)
        
        steelsquid_digole.write_text_line("DISTANCE", padding=5)
        steelsquid_digole.write_text_line("ALTITUDE", padding=5)
        steelsquid_digole.write_text_line("SPEED", padding=17)
        
        steelsquid_digole.write_text_line("T CORE/OUT", padding=5)
        steelsquid_digole.write_text_line("AIR PRESSURE", padding=5)
        steelsquid_digole.write_text_line("AIR HUMIDITY", padding=5)
        steelsquid_digole.write_text_line("ILLUMINANCE", padding=5)
        steelsquid_digole.write_text_line("ROLL/PITCH")

    

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
       
        
    @staticmethod
    def on_network(status, wired, usb, wifi_ssid, wifi, wan):
        '''
        Execute on network up or down.
        status = True/False (up or down)
        wired = Wired ip number
        wifi_ssid = Cnnected to this wifi
        wifi = Wifi ip number
        wan = Ip on the internet
        '''    
        IO.OUTPUT.led_network(status)        
        

    @staticmethod
    def on_xkey(key):
        '''
        If steelsquid browser-on or mbrowser-on is activated
        Some keys is catched and a then is executed her instead.
        Key can be:
        ESC, DEL, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12
        '''    
        bit = False
        if key == "ESC":
            bit = True
            SETTINGS.bitrate = "200000"
        elif key == "F1":
            bit = True
            SETTINGS.bitrate = "400000"
        elif key == "F2":
            bit = True
            SETTINGS.bitrate = "600000"
        elif key == "F3":
            bit = True
            SETTINGS.bitrate = "800000"
        elif key == "F4":
            bit = True
            SETTINGS.bitrate = "1000000"
        elif key == "F5":
            bit = True
            SETTINGS.bitrate = "1200000"
        elif key == "F6":
            bit = True
            SETTINGS.bitrate = "1400000"
        elif key == "F7":
            bit = True
            SETTINGS.bitrate = "1600000"
        elif key == "F8":
            bit = True
            SETTINGS.bitrate = "1800000"
        elif key == "F9":
            bit = True
            SETTINGS.bitrate = "2000000"
        elif key == "F10":
            bit = True
            SETTINGS.bitrate = "2200000"
        elif key == "DEL":
            bit = True
            SETTINGS.bitrate = "2400000"
        if bit:
            DO.mood(0)
            IO.OUTPUT.led_mood(None)        
            steelsquid_kiss_global.radio_request("change_bitrate", [SETTINGS.bitrate])
            steelsquid_kiss_global.save_module_settings()
        elif key == "PLUS":
            steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "500+"])
            
        
        
        
        



##############################################################################################################################################################################################
class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    @staticmethod
    def voltage_current_led():
        '''
        Read voltage and current
        Also print to LCD
        ''' 
        # Low voltage beep
        beep = False
        if RADIO.REMOTE.rover_voltage != -1:
            if RADIO.REMOTE.rover_voltage<STATIC.rover_voltage_warning:
                beep=True
        if beep:
            pass
            #IO.OUTPUT.sum_flash()
        # Generate OLED text and HUD text
        hud = []
        lcd = []
        ping = str(int(float(DYNAMIC.ping_time)*1000))
        bit = str(float(SETTINGS.bitrate)/1000000)
        
        # Add date/time or mission time
        d = steelsquid_utils.get_date_time()
        mt = "---"
        if DYNAMIC.timer:
            if DYNAMIC.timer_start != None:
                mt = steelsquid_utils.get_time_diff_string(DYNAMIC.timer_start, datetime.datetime.now())
        else:
            if DYNAMIC.timer_stop != None:
                mt = steelsquid_utils.get_time_diff_string(DYNAMIC.timer_start, DYNAMIC.timer_stop)
        
        if DYNAMIC.timer_start == None:
            lcd.append(d+"   00:00:00")
        elif DYNAMIC.timer:
            lcd.append(d+"   "+mt)
        else:
            lcd.append(d+"   "+mt)
        # Date time/mission time
        hud.append(d)
        hud.append("<br>")
        if mt != None:
            hud.append("<span class='hud'>Mission time:</span> ")
            hud.append(mt)
            hud.append("<br><div style='height:8px'></div>")                
        # net/disk usage
        directory = None
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        # USB/temp
        usb = None
        if directory != None:
            usb = str(steelsquid_utils.get_disk_usage(directory))
        # Data usage
        hud.append("<span class='hud'>Data  usage:</span> ")
        hud.append(RADIO.REMOTE.data_usage)
        hud.append(" GB<br>")
        lcd.append(RADIO.REMOTE.data_usage + " GB")
        # USB
        if usb != None:
            hud.append("<span class='hud'>USB usage:</span> ")
            hud.append(usb)
            hud.append(" %<br>")
            lcd.append(usb + " %")
        else:
            hud.append("<span class='hud'>USB usage:</span> ")
            hud.append("No USB stick")
            hud.append("<br>")
            lcd.append("---")
        # bandwidth
        hud.append("<span class='hud'>Bandwidth:</span> ")
        hud.append(RADIO.REMOTE.bandwidth)
        hud.append(" KB/s<br>")
        lcd.append(RADIO.REMOTE.bandwidth + " KB/s")
        # Ping time
        hud.append("<span class='hud'>Latency:</span> ")
        if DYNAMIC.ping_time<99:
            hud.append(ping)
            hud.append(" ms<br><div style='height:8px'></div>")
            lcd.append(ping + " ms")
        else:
            hud.append("No connection!<br><div style='height:8px'></div>")
            lcd.append("---")
        # Rover voltage ampere
        if RADIO.REMOTE.rover_voltage != -1:
            v = RADIO.REMOTE.rover_voltage
            a = RADIO.REMOTE.rover_ampere
            if v > 99:
                v=20
            if a > 99:
                a=20
            bat_proc = steelsquid_utils.get_lipo_percentage(v, 4)
            ah_left = bat_proc * 0.01 * STATIC.rover_amp_hour
            h_left = round(ah_left / a, 1)
            hud.append("<span class='hud'>Voltage:</span> ")
            hud.append(str(bat_proc))
            hud.append(" % (")
            hud.append(str(v))
            hud.append(" V)<br>")
            hud.append("<span class='hud'>Current:</span> ")
            hud.append(str(a))
            hud.append(" A (")
            hud.append(str(h_left))
            hud.append("h left)<br><div style='height:8px'></div>")
            lcd.append(str(bat_proc) + "% (" + str(v) + " V)")
            lcd.append(str(a) + "A (" + str(h_left) + " h left)")
        else:
            lcd.append("---")
            lcd.append("---")
        # Cruise controll
        hud.append("<span class='hud'>Cruise control:</span> ")
        hud.append(str(RADIO.LOCAL.cruise))
        hud.append(" %<br>")
        # GPS
        if RADIO.REMOTE.gps_long!=0 and RADIO.REMOTE.gps_lat!=0 and SETTINGS.gps_home_lat != 0:
            DYNAMIC.dis, unit, DYNAMIC.unit = steelsquid_utils.distance(RADIO.REMOTE.gps_lat, RADIO.REMOTE.gps_long, SETTINGS.gps_home_lat, SETTINGS.gps_home_long)
            from_home = str(DYNAMIC.dis)
            hud.append("<span class='hud'>Distance:</span> ")
            hud.append(from_home)
            hud.append(" ")
            hud.append(unit)
            hud.append("<br>")
            hud.append("<span class='hud'>Altitude:</span> ")
            hud.append(str(RADIO.REMOTE.gps_alt))
            hud.append(" m<br>")
            hud.append("<span class='hud'>Speed:</span> ")
            hud.append(str(RADIO.REMOTE.gps_speed))
            hud.append(" km/h<br>")
            lcd.append(from_home + " " + unit)
            lcd.append(str(RADIO.REMOTE.gps_alt) + " m")
            lcd.append(str(RADIO.REMOTE.gps_speed) + " km/h")
        else:
            hud.append("<span class='hud'>Distance:</span> ")
            hud.append("No GPS!<br>")
            hud.append("<span class='hud'>Altitude:</span> ")
            hud.append("No GPS!<br>")
            hud.append("<span class='hud'>Speed:</span> ")
            hud.append("No GPS!<br>")
            lcd.append("---")
            lcd.append("---")
            lcd.append("---")
        # Headlight
        hud.append("<div style='height:8px'></div><span class='hud'>Headlight:</span> ")
        hud.append(UTILS.to_on_off(RADIO.LOCAL.headlight))
        hud.append("<br>")
        # Highbeam
        hud.append("<span class='hud'>Highbeam:</span> ")
        hud.append(UTILS.to_on_off(RADIO.LOCAL.highbeam))
        hud.append("<br>")
        # Mood
        hud.append("<span class='hud'>Mode:</span> ")
        if RADIO.LOCAL.mood==1:
            hud.append("Heart <span style='font-weight: 900;font-size:16px'>&#9829;</span><br>")
        elif RADIO.LOCAL.mood==2:
            hud.append("Smile <span style='font-weight: 900;font-size:16px'>&#9786</span><br>")
        elif RADIO.LOCAL.mood==3:
            hud.append("Sad <span style='font-weight: 900;font-size:16px'>&#9785;</span><br>")
        elif RADIO.LOCAL.mood==4:
            hud.append("Wave <span style='font-weight: 900;font-size:16px'>&#9836;</span><br>")
        elif RADIO.LOCAL.mood==5:
            hud.append("Away <span style='font-weight: 900;font-size:16px'>&#9888;</span><br>")
        else:
            hud.append("Nothing<br>")
        #Temp
        hud.append("<div style='height:8px'></div><span class='hud'>T core/out:</span> ")
        hud.append(RADIO.REMOTE.temperature_core + "&deg;C / " + RADIO.REMOTE.temperature)
        hud.append("&deg;C<br>")
        hud.append("<span class='hud'>Air pressure:</span> ")
        hud.append(RADIO.REMOTE.pressure)
        hud.append(" kPa<br>")
        hud.append("<span class='hud'>Air humidity:</span> ")
        hud.append(str(RADIO.REMOTE.humidity))
        hud.append(" %<br>")
        hud.append("<span class='hud'>Illuminance:</span> ")
        hud.append(str(RADIO.REMOTE.light))
        hud.append(" lx<br>")
        r = str(abs(int(RADIO.REMOTE.roll)))
        p = str(abs(int(RADIO.REMOTE.pitch)))
        hud.append("<span class='hud'>Roll/Pitch:</span> ")
        hud.append(r)
        hud.append("&deg; / ")
        hud.append(p)
        hud.append("&deg;")
        lcd.append(str(RADIO.REMOTE.temperature_core) + " C / " + str(RADIO.REMOTE.temperature) + " C")
        lcd.append(str(RADIO.REMOTE.pressure) + " kPa")
        lcd.append(str(RADIO.REMOTE.humidity) + " %")
        lcd.append(str(RADIO.REMOTE.light) + " lx")
        lcd.append(r + " / " + p)
        # Set HUD TEXT
        DYNAMIC.hud_text = "".join(hud)
        # Print to LCD
        c= 110
        r = 0
        s = 18
        l = 30
        steelsquid_digole.text_position(0, 0)
        steelsquid_digole.write_text(lcd[0])
        r = r + 41
        steelsquid_digole.write_text(lcd[1]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[2]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[3]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[4]+"   ", col = c, row = r)
        r = r + l
        steelsquid_digole.write_text(lcd[5]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[6]+"  ", col = c, row = r)
        r = r + l
        steelsquid_digole.write_text(lcd[7]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[8]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[9]+"   ", col = c, row = r)
        r = r + l
        steelsquid_digole.write_text(lcd[10]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[11]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[12]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[13]+"   ", col = c, row = r)
        r = r + s
        steelsquid_digole.write_text(lcd[14]+"   ", col = c, row = r)
        return 0.4
       
        
    @staticmethod
    def ip_oled():
        '''
        RSMal OLED display
        ''' 
        shout_string = []
        if steelsquid_kiss_global.last_net:
            if steelsquid_kiss_global.last_wifi_name != "---":
                shout_string.append("WIFI: ")
                shout_string.append(steelsquid_kiss_global.last_wifi_name)
                shout_string.append("\n")
                shout_string.append(steelsquid_kiss_global.last_wifi_ip)
                if steelsquid_kiss_global.last_lan_ip!="---":
                    shout_string.append("\nWIRED: ")
                    shout_string.append(steelsquid_kiss_global.last_lan_ip)
                if steelsquid_kiss_global.last_wan_ip != "---":
                    shout_string.append("\nWAN: ")
                    shout_string.append(steelsquid_kiss_global.last_wan_ip)
            else:
                if steelsquid_kiss_global.last_lan_ip!="---":
                    shout_string.append("WIRED: ")
                    shout_string.append(steelsquid_kiss_global.last_lan_ip)
                if steelsquid_kiss_global.last_wan_ip != "---":
                    shout_string.append("\nWAN: ")
                    shout_string.append(steelsquid_kiss_global.last_wan_ip)
            if not steelsquid_utils.is_empty(RADIO.REMOTE.wan):
                shout_string.append("\nROVER: ")
                shout_string.append(RADIO.REMOTE.wan)
        else:
            shout_string.append("No network!\n")
        mes = "".join(shout_string)
        steelsquid_utils.shout(mes, leave_on_lcd = True)
        time.sleep(1)






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
        Will execute about every 0.2 second or when steelsquid_kiss_global.radio_interrupt() or when reseive a sync from the remote host
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
            # Stop cruise if conenction lost
            if last_ping>1:
                RADIO.PUSH_1.motor_left = 0
                RADIO.PUSH_1.motor_right = 0
                IO.OUTPUT.led_cruise(False)
                RADIO.LOCAL.cruise=0
            # Connection lost
            if last_ping<STATIC.connection_lost_timeout:
                DYNAMIC.ping_time = ping_time_median
                steelsquid_utils.execute_if_changed(DO.connected, True)
            else:
                DYNAMIC.ping_time = 99
                steelsquid_utils.execute_if_changed(DO.connected, False)

    
    @staticmethod
    def on_sync():
        '''
        Will execute about every second or when steelsquid_kiss_global.radio_interrupt() or when reseive a sync from the remote host
        Use this to check for changes in varibales under REMOTE.
        '''
        # Is GPS connected
        IO.OUTPUT.led_gps_connected(RADIO.REMOTE.gps_con)
        # Check PIR (Only check if mood away for10 seconds)
        if RADIO.LOCAL.mood == 5 and DYNAMIC.last_mood_away != None:
            diff = (datetime.datetime.now() - DYNAMIC.last_mood_away).total_seconds()
            if diff > 10:
                if RADIO.REMOTE.pir_front or RADIO.REMOTE.pir_left or RADIO.REMOTE.pir_right or RADIO.REMOTE.pir_back:
                    steelsquid_utils.execute_min_time(DO.pir, (RADIO.REMOTE.pir_front, RADIO.REMOTE.pir_left, RADIO.REMOTE.pir_right, RADIO.REMOTE.pir_back,), min_seconds=10)
        

    class LOCAL(object):
        '''
        All varibales in this class will be synced from this machine to the remote about every second
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        Use steelsquid_kiss_global.radio_interrupt() to sync imediately
        LOCAL (on this machine) sync to REMOTE (on remote machine)
        '''
        # 0=off 1=heart 2=smile 3=sad 4=wave 5=away
        mood = 0

        # Use laser
        laser = False

        # Use headlight
        headlight = False

        # Use high beam
        highbeam = False

        # Show this on screen
        # 1 = Save   2 = settings   3 = Map   4 = FPV
        show = 3

        # Is cruise control enabled (this is the speed)
        cruise = 0
    
        # Drive forward and backwardto turn
        spec_turn = False
        

    class REMOTE(object):
        '''
        All varibales in this class will be synced from remote host to this machine
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        LOCAL (on remote machine) sync to REMOTE (on this machine)
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
        

    class PUSH_1(object):
        '''
        All varibales in this class (PUSH_1 to PUSH_4) will be synced from the remote control to the receiver when on_push() on the remote controll return True
        OBS! The variables most be in the same order on both the machines
        The variables can only be int, float, bool or string.
        '''
        # Only want to send sertant number of stopp signals
        _sent_zero_count = 0

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
            # Read from stiks
            drive, steer, turn = (IO.drive, IO.steer, IO.turn_s)
            #Cruise
            if RADIO.LOCAL.cruise != 0:
                # Check if to stop cruise
                do_some = steelsquid_utils.do_someting("stop_cruise")
                if do_some == False:
                    RADIO.PUSH_1.motor_left=0
                    RADIO.PUSH_1.motor_right=0
                elif do_some == True:
                    RADIO.PUSH_1.motor_left=0
                    RADIO.PUSH_1.motor_right=0
                    RADIO.LOCAL.cruise=0
                elif drive > 100 or steer > 100 or drive < -100 or steer < -100:
                    IO.OUTPUT.led_cruise(False)
                    RADIO.PUSH_1.motor_left=0
                    RADIO.PUSH_1.motor_right=0
                    steelsquid_utils.do_someting("stop_cruise", 2)
                else:
                    RADIO.PUSH_1._sent_zero_count = 0
                    # Remap the joystick range
                    turn = int(steelsquid_utils.remap(turn, -510, 510, RADIO.REMOTE.motor_max*-1, RADIO.REMOTE.motor_max))
                    # Drive 
                    turn = turn/4
                    motor_left = RADIO.LOCAL.cruise + turn
                    motor_right = RADIO.LOCAL.cruise - turn
                    # Chack that the waluses is in range (-100 to 100)
                    motor_left, motor_right = UTILS.check_motor_values(motor_left, motor_right)
                    # Set the value that will be sent to the server
                    RADIO.PUSH_1.motor_left = motor_left
                    RADIO.PUSH_1.motor_right = motor_right
                return True, STATIC.sleep
            elif turn > 90 or turn < -90:
                RADIO.PUSH_1._sent_zero_count = 0
                # Remap the joystick range
                turn = int(steelsquid_utils.remap(turn, -510, 510, RADIO.REMOTE.motor_max*-1, RADIO.REMOTE.motor_max))
                # Calculate drive
                turn = int(turn/1.5)
                motor_left = turn
                motor_right = turn*-1
                # Chack that the values is in range (-100 to 100)
                motor_left, motor_right = UTILS.check_motor_values(motor_left, motor_right)
                # Set the value that will be sent to the server
                RADIO.PUSH_1.motor_left = motor_left
                RADIO.PUSH_1.motor_right = motor_right
                return True, STATIC.sleep
            elif drive != 0 or steer!=0:
                RADIO.PUSH_1._sent_zero_count = 0
                # Remap the joystick range
                drive = int(steelsquid_utils.remap(drive, -510, 510, RADIO.REMOTE.motor_max*-1, RADIO.REMOTE.motor_max))
                steer = int(steelsquid_utils.remap(steer, -510, 510, RADIO.REMOTE.motor_max*-1, RADIO.REMOTE.motor_max))
                # Drive 
                steer = steer/2
                motor_left = drive - steer
                motor_right = drive + steer
                # Chack that the waluses is in range (-100 to 100)
                motor_left, motor_right = UTILS.check_motor_values(motor_left, motor_right)
                # Set the value that will be sent to the server
                RADIO.PUSH_1.motor_left=motor_left
                RADIO.PUSH_1.motor_right=motor_right
                return True, STATIC.sleep
            elif RADIO.PUSH_1._sent_zero_count<8:
                RADIO.PUSH_1._sent_zero_count = RADIO.PUSH_1._sent_zero_count + 1
                RADIO.PUSH_1.motor_left=0
                RADIO.PUSH_1.motor_right=0
                return True, STATIC.sleep
            else:
                return False, STATIC.sleep


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

        _last_t = datetime.datetime.now()

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
            ts = datetime.datetime.now()
            pan = IO.pan
            tilt = IO.tilt
            turn = IO.turn_p
            if turn!=0:
                new_t = datetime.datetime.now()
                if (new_t-RADIO.PUSH_2._last_t).total_seconds() > 0.8:
                    RADIO.PUSH_2.camera_tilt = STATIC.servo_position_tilt_start
                    RADIO.PUSH_2.can_pan = not RADIO.PUSH_2.can_pan
                RADIO.PUSH_2._last_t = new_t
                return True, STATIC.sleep
            elif pan!=0 or tilt!=0:
                tilt = RADIO.PUSH_2.camera_tilt + int(tilt/50)
                if tilt<STATIC.servo_position_tilt_min:
                    tilt = STATIC.servo_position_tilt_min
                elif tilt>STATIC.servo_position_tilt_max:
                    tilt = STATIC.servo_position_tilt_max
                RADIO.PUSH_2.camera_pan = pan
                RADIO.PUSH_2.camera_tilt = tilt
                return True, STATIC.sleep
            else:
                return False, STATIC.sleep
                







##############################################################################################################################################################################################
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
    def save_settings(session_id, parameters):
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
        
        steelsquid_utils.execute_system_command_blind(['steelsquid', 'hdmi-res', SETTINGS.width, SETTINGS.height])
        
        # Save to disk
        steelsquid_kiss_global.save_module_settings()
        # Send to rover
        steelsquid_kiss_global.radio_request("save_settings", para)
        # Restart service
        steelsquid_kiss_global.restart(delay=2)
        return []


    @staticmethod
    def load_settings(session_id, parameters):
        '''
        Get the control/video/audio ip
        '''
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
        return [RADIO.LOCAL.show]



    @staticmethod
    def get_gps(session_id, parameters):
        '''
        Get the map
        '''
        return [SETTINGS.gps_home_lat, SETTINGS.gps_home_long, RADIO.REMOTE.gps_lat, RADIO.REMOTE.gps_long]


    @staticmethod
    def get_hud(session_id, parameters):
        '''
        Get the map
        '''
        bit = str(float(SETTINGS.bitrate)/1000000)
        doit = DYNAMIC.force_stream_close
        DYNAMIC.force_stream_close = False
        return [DYNAMIC.hud_text, "<span class='hud'>Video bitrate:</span> "+bit+" Mbit", doit, int(RADIO.REMOTE.roll*-1), int(RADIO.REMOTE.pitch*-1)]


    @staticmethod
    def speek(session_id, parameters):
        '''
        Make rover speek
        '''
        if parameters[0] == '----':
            parameters[0] = "Jag är " +str(DYNAMIC.dis)+ " " +DYNAMIC.unit+  " från hemmet"
        steelsquid_kiss_global.radio_request("speek", parameters)

        
    @staticmethod
    def network(session_id, parameters):
        '''
        Get network
        '''
        return [steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_wan_ip]


    @staticmethod
    def screenshot(session_id, parameters):
        '''
        Take screenshot
        '''
        t = UTILS.get_save_file("screen.png")
        steelsquid_utils.execute_system_command(["/usr/bin/screenshot", t])
        return t


    @staticmethod
    def set_home(session_id, parameters):
        '''
        Set home
        '''
        SETTINGS.gps_home_lat=RADIO.REMOTE.gps_lat
        SETTINGS.gps_home_long=RADIO.REMOTE.gps_long
        SETTINGS.gps_home_alt=SETTINGS.gps_home_alt
        steelsquid_kiss_global.save_module_settings()
        return "Home position changed"
        

    @staticmethod
    def typing(session_id, parameters):
        '''
        Typing on keyboard
        '''
        steelsquid_kiss_global.radio_request("typing")


    @staticmethod
    def vol_down(session_id, parameters):
        '''
        vol_down
        '''
        steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "500-"])
        
        

                
        
            









##############################################################################################################################################################################################
class IO(object):
    '''
    Put IO stuff her, maybe read stuff from sensors or listen for button press.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class
    Maybe use on_start() to start listen on GPIO or enable sensors...
    reader_1 to reader_4 is threads that execute in separate threads.
    '''

    # Move camera
    pan = 0
    tilt = 0
    turn_p = 0

    # Drive and steer
    drive = 0
    steer = 0
    turn_s = 0


    @staticmethod
    def on_start():
        '''
        This will execute when system starts, it is the same as on_start in SYSTEM but put IO stuff her.
        Do not execute long running stuff here, do it in on_loop...
        Maybe use this to start listen on GPIO or enable sensors
        '''
        # Start listen on buttons
        steelsquid_pi.mcp23017_click(21, 6, IO.INPUT.button_use_external_hdmi, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 9, IO.INPUT.button_cruise, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig, last_click_time=True)
        steelsquid_pi.mcp23017_click(20, 0, IO.INPUT.button_laser, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 2, IO.INPUT.button_highbeam, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 13, IO.INPUT.button_away, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)

        steelsquid_pi.mcp23017_click(20, 15, IO.INPUT.button_low_light, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(21, 15, IO.INPUT.button_siren, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 11, IO.INPUT.button_spec_turn, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        
        steelsquid_pi.mcp23017_click(20, 6, IO.INPUT.button_tcp_video, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 4, IO.INPUT.button_headlight, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(20, 9, IO.INPUT.button_fpv, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(21, 2, IO.INPUT.button_save, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 4, IO.INPUT.button_mute, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(21, 13, IO.INPUT.button_timer, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_21_trig)
        steelsquid_pi.mcp23017_click(20, 11, IO.INPUT.button_settings, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.mcp23017_click(21, 0, IO.INPUT.button_map, pullup=True, rpi_gpio=STATIC.gpio_mcp23017_20_trig)
        steelsquid_pi.gpio_click(10, IO.INPUT.button_mood_heart, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(9, IO.INPUT.button_mood_smile, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(11, IO.INPUT.button_mood_sad, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(5, IO.INPUT.button_mood_wave, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(6, IO.INPUT.button_control_radio, resistor=steelsquid_pi.PULL_UP)        
        steelsquid_pi.gpio_click(19, IO.INPUT.button_control_wifi, resistor=steelsquid_pi.PULL_UP)        
        steelsquid_pi.gpio_click(20, IO.INPUT.button_control_3g4g, resistor=steelsquid_pi.PULL_UP)        
    

    @staticmethod
    def reader():
        '''
        This will execute over and over again untill return -1 or None
        Use this to read from sensors in one place.
        Return the number of seconds you want to sleep until next execution
        '''
        IO.pan, IO.tilt, IO.turn_p = IO.UNITS.read_pan_tilt()
        IO.drive, IO.steer, IO.turn_s = IO.UNITS.read_drive_steer()
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
            v = steelsquid_pi.po12_adc_volt_smooth(8, median_size=11) / 0.1127
            v = Decimal(v)
            v = round(v, 1)
            return v


        @staticmethod
        def read_in_ampere():
            '''
            Read main in ampere
            '''
            v = steelsquid_pi.po12_adc_smooth(7, median_size=11)
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
            pan = steelsquid_pi.po12_adc_smooth_max(5)
            pan = pan - 515
            if pan > -20 and pan < 20:
                pan = 0
            tilt = steelsquid_pi.po12_adc_smooth_max(4)
            tilt = 515 - tilt
            if tilt > -20 and tilt < 20:
                tilt = 0
            turn = steelsquid_pi.po12_adc_smooth_max(6)
            turn = 515 - turn
            if turn > -50 and turn < 50:
                turn = 0
            return pan, tilt, turn


        @staticmethod
        def read_drive_steer():
            '''
            Read drive and steer
            '''
            drive = steelsquid_pi.po12_adc_smooth_max(1)
            drive = drive - 515
            if drive > -20 and drive < 20:
                drive = 0
            steer = steelsquid_pi.po12_adc_smooth_max(2)
            steer = 515 - steer
            if steer > -20 and steer < 20:
                steer = 0
            turn = steelsquid_pi.po12_adc_smooth_max(3)
            turn = 515 - turn
            if turn > -50 and turn < 50:
                turn = 0
            if drive < -10:
                steer = steer * -1 
            return drive, steer, turn



    class INPUT(object):
        '''
        Put input stuff her, maybe method to execute when a button is pressed.
        It is not necessary to put it her, but i think it is kind of nice to have it inside this class
        '''

       
        @staticmethod
        def button_use_external_hdmi(address, pin):
            '''
            Toggle use of external HDMI monitor
            '''        
            SETTINGS.use_external_hdmi = not SETTINGS.use_external_hdmi
            steelsquid_kiss_global.save_module_settings()
            IO.OUTPUT.led_use_external_hdmi(SETTINGS.use_external_hdmi)
            if SETTINGS.use_external_hdmi:
                os.system("steelsquid monitor-0")
                os.system("steelsquid monitor-csi-off")
            else:
                os.system("steelsquid monitor-180")
                os.system("steelsquid monitor-csi-on")
            steelsquid_kiss_global.reboot()            
        
        
        @staticmethod
        def button_mood_smile(pin):
            '''
            Push the smile button
            0=off 1=heart 2=smile 3=sad 4=wave
            '''        
            DO.mood(2)


        @staticmethod
        def button_mood_heart(pin):
            '''
            Push the heart button
            0=off 1=heart 2=smile 3=sad 4=wave
            '''        
            DO.mood(1)


        @staticmethod
        def button_mood_sad(pin):
            '''
            Push the sad button
            0=off 1=heart 2=smile 3=sad 4=wave
            '''        
            DO.mood(3)


        @staticmethod
        def button_mood_wave(pin):
            '''
            Push the angry button
            0=off 1=heart 2=smile 3=sad 4=wave
            '''        
            DO.mood(4)
            

        @staticmethod
        def button_control_radio(pin):
            '''
            Push the radio control button
            '''        
            DO.control(1)


        @staticmethod
        def button_control_wifi(pin):
            '''
            Push the radio control button
            '''        
            DO.control(2)


        @staticmethod
        def button_control_3g4g(pin):
            '''
            Push the radio control button
            '''        
            DO.control(3)


        @staticmethod
        def button_laser(address, pin):
            '''
            Toggle use of laser
            '''        
            RADIO.LOCAL.laser = not RADIO.LOCAL.laser
            IO.OUTPUT.led_laser(RADIO.LOCAL.laser)
            
            
        @staticmethod
        def button_headlight(address, pin):
            '''
            Toggle headlight
            '''        
            RADIO.LOCAL.headlight = not RADIO.LOCAL.headlight
            IO.OUTPUT.led_headlight(RADIO.LOCAL.headlight)
            steelsquid_kiss_global.radio_interrupt()        
            
            
        @staticmethod
        def button_highbeam(address, pin):
            '''
            Toggle highbeam
            '''        
            RADIO.LOCAL.highbeam = not RADIO.LOCAL.highbeam
            IO.OUTPUT.led_highbeam(RADIO.LOCAL.highbeam)
            steelsquid_kiss_global.radio_interrupt()        
            
            
        @staticmethod
        def button_siren(address, pin):
            '''
            Siren for 1 second
            '''        
            steelsquid_kiss_global.radio_request("siren")
            IO.OUTPUT.led_siren()


        @staticmethod
        def button_tcp_video(address, pin):
            '''
            tcp_video 
            '''        
            SETTINGS.tcp_video = not SETTINGS.tcp_video
            steelsquid_gstreamer.video_tcp(SETTINGS.tcp_video)
            steelsquid_kiss_global.radio_request("tcp_video", [SETTINGS.tcp_video])
            steelsquid_kiss_global.save_module_settings()
            IO.OUTPUT.led_tcp_video(SETTINGS.tcp_video)


        @staticmethod
        def button_cruise(address, pin, last_click_time):
            '''
            Camera loght
            '''    
            if last_click_time<0.4:
                if RADIO.LOCAL.cruise > 0:
                    RADIO.LOCAL.cruise = RADIO.LOCAL.cruise - 20
                    if RADIO.LOCAL.cruise < 0:
                        RADIO.LOCAL.cruise=0
            else:
                if RADIO.LOCAL.cruise < 20:
                    RADIO.LOCAL.cruise = 20
                elif RADIO.LOCAL.cruise < RADIO.REMOTE.motor_max:
                    RADIO.LOCAL.cruise = RADIO.LOCAL.cruise + 10
            IO.OUTPUT.led_cruise(RADIO.LOCAL.cruise>0)


        @staticmethod
        def button_fpv(address, pin):
            '''
            FPV
            1 = Save   2 = settings   3 = Map   4 = FPV
            '''
            if RADIO.LOCAL.show == 4:
                DO.show(3)
            else:
                DO.show(4)


        @staticmethod
        def button_settings(address, pin):
            '''
            settings
            1 = Save   2 = settings   3 = Map   4 = FPV
            '''        
            DO.show(2)


        @staticmethod
        def button_map(address, pin):
            '''
            map
            1 = Save   2 = settings   3 = Map   4 = FPV
            '''        
            DO.show(3)
            
            
        @staticmethod
        def button_timer(address, pin):
            '''
            button_timer
            '''        
            # TImer
            if DYNAMIC.timer:
                IO.OUTPUT.led_timer(False)
                DYNAMIC.timer_stop = datetime.datetime.now()
                DYNAMIC.timer = False
            else:
                IO.OUTPUT.led_timer(True)
                DYNAMIC.timer_start = datetime.datetime.now()
                DYNAMIC.timer = True


        @staticmethod
        def button_save(address, pin):
            '''
            button
            1 = Save   2 = settings   3 = Map   4 = FPV
            '''        
            if RADIO.LOCAL.show == 1:
                RADIO.LOCAL.show = 3
            else:
                RADIO.LOCAL.show = 1
            DO.show(RADIO.LOCAL.show)


        @staticmethod
        def button_away(address, pin):
            '''
            Away
            '''        
            DO.mood(5)


        @staticmethod
        def button_mute(address, pin):
            '''
            button
            '''        
            DYNAMIC.mute = not DYNAMIC.mute
            IO.OUTPUT.led_mute(DYNAMIC.mute)
            if DYNAMIC.mute:
                steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "mute"], wait_for_finish=True)
            else:
                steelsquid_utils.execute_system_command_blind(["amixer", "set", "PCM", "unmute"], wait_for_finish=True)


        @staticmethod
        def button_spec_turn(address, pin):
            '''
            Drive forward and back to turn
            '''        
            RADIO.LOCAL.spec_turn = not RADIO.LOCAL.spec_turn
            IO.OUTPUT.led_spec_turn(RADIO.LOCAL.spec_turn)        
                    

        @staticmethod
        def button_low_light(address, pin):
            '''
            Camera loght
            '''        
            SETTINGS.low_light = not SETTINGS.low_light
            steelsquid_gstreamer.low_light(SETTINGS.low_light)
            steelsquid_kiss_global.radio_request("low_light", [SETTINGS.low_light])
            steelsquid_kiss_global.save_module_settings()
            IO.OUTPUT.led_low_light(SETTINGS.low_light)        



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
            0=off 1=heart 2=smile 3=sad 4=wave
            ''' 
            if mood == None:
                steelsquid_pi.gpio_flash(4,)
                steelsquid_pi.gpio_flash(17)
                steelsquid_pi.gpio_flash(27)
                steelsquid_pi.gpio_flash(22)
                DYNAMIC.last_mood_away = None
            elif mood == 1:
                steelsquid_pi.gpio_set(4, True)
                steelsquid_pi.gpio_set(17, False)
                steelsquid_pi.gpio_set(27, False)
                steelsquid_pi.gpio_set(22, False)
                DYNAMIC.last_mood_away = None
                IO.OUTPUT.led_away(False)
            elif mood == 2:
                steelsquid_pi.gpio_set(4, False)
                steelsquid_pi.gpio_set(17, True)
                steelsquid_pi.gpio_set(27, False)
                steelsquid_pi.gpio_set(22, False)
                DYNAMIC.last_mood_away = None
                IO.OUTPUT.led_away(False)
            elif mood == 3:
                steelsquid_pi.gpio_set(4, False)
                steelsquid_pi.gpio_set(17, False)
                steelsquid_pi.gpio_set(27, True)
                steelsquid_pi.gpio_set(22, False)
                DYNAMIC.last_mood_away = None
                IO.OUTPUT.led_away(False)
            elif mood == 4:
                steelsquid_pi.gpio_set(4, False)
                steelsquid_pi.gpio_set(17, False)
                steelsquid_pi.gpio_set(27, False)
                steelsquid_pi.gpio_set(22, True)
                DYNAMIC.last_mood_away = None
                IO.OUTPUT.led_away(False)
            elif mood == 5:
                steelsquid_pi.gpio_set(4, False)
                steelsquid_pi.gpio_set(17, False)
                steelsquid_pi.gpio_set(27, False)
                steelsquid_pi.gpio_set(22, False)
                DYNAMIC.last_mood_away = datetime.datetime.now()
                IO.OUTPUT.led_away(True)
            else:
                steelsquid_pi.gpio_set(4, False)
                steelsquid_pi.gpio_set(17, False)
                steelsquid_pi.gpio_set(27, False)
                steelsquid_pi.gpio_set(22, False)
                DYNAMIC.last_mood_away = None
                IO.OUTPUT.led_away(False)
                

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
        def sum_flash(led=True, dummy=False):
            '''
            Sound the summer for short time
            ''' 
            if not dummy:
                thread.start_new_thread(IO.OUTPUT.sum_flash, (led, True,))
            else:
                if led:
                    steelsquid_pi.gpio_set(8, True)
                steelsquid_pi.po12_digital_out(1, True)
                steelsquid_pi.po12_digital_out(2, True)
                steelsquid_pi.po12_digital_out(3, True)
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
            steelsquid_pi.mcp23017_set(20, 5, status)        

        
        @staticmethod
        def led_highbeam(status):
            '''
            Light the highbeam LED
            ''' 
            steelsquid_pi.mcp23017_set(20, 3, status)                
            

        @staticmethod
        def led_tcp_video(status):
            '''
            Light the tcp video
            ''' 
            steelsquid_pi.mcp23017_set(20, 7, status)                 
            

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
            steelsquid_pi.mcp23017_set(21, 3, status)  


        @staticmethod
        def led_save_flash(leav_on=False):
            '''
            led_timer
            ''' 
            thread.start_new_thread(IO.OUTPUT._save_flash, (leav_on,)) 


        @staticmethod
        def _save_flash(leav_on=False):
            '''
            Flash LED
            '''        
            for i in range(20):
                steelsquid_pi.mcp23017_set(21, 3, i%2==0)  
                time.sleep(0.1)
            steelsquid_pi.mcp23017_set(21, 3, leav_on)  


        @staticmethod
        def led_mute(status):
            '''
            Use 
            ''' 
            steelsquid_pi.mcp23017_set(21, 5, status)


        @staticmethod
        def led_spec_turn(status):
            '''
            Drive forward and backard to turn
            ''' 
            steelsquid_pi.mcp23017_set(21, 10, status)            
            
            
        @staticmethod
        def led_low_light(status=None):
            '''
            Away
            ''' 
            if status==None:
                steelsquid_pi.mcp23017_flash(20, 14)
            else:
                steelsquid_pi.mcp23017_set(20, 14, status)
                        
            
        @staticmethod
        def led_siren(turnOff=False):
            '''
            Light the siren LED for a second
            ''' 
            if turnOff:
                steelsquid_pi.mcp23017_set(21, 14, False)                 
            else:
                steelsquid_pi.mcp23017_flash(21, 14, seconds=1)                 
            

        @staticmethod
        def led_away(status=None):
            '''
            Light the cam light LED
            ''' 
            if status==None:
                steelsquid_pi.mcp23017_flash(20, 12)
            else:
                steelsquid_pi.mcp23017_set(20, 12, status)
            



        





##############################################################################################################################################################################################
class DO(object):
    '''
    Put staticmethods in this class, methods that carry ut mutipple thinks
    Maybe light led, send request and handle error from the request
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''

    @staticmethod
    def connected(status):
        '''
        Is connection lost or not
        '''        
        IO.OUTPUT.led_connected(status)


    @staticmethod
    def mood(mood):
        '''
        Set mood
        0=off 1=heart 2=smile 3=sad 4=wav   5=away
        '''        
        if mood == None:
            mood = 0
        elif mood == RADIO.LOCAL.mood:
            mood = 0
        IO.OUTPUT.led_mood(mood)
        RADIO.LOCAL.mood = mood
        steelsquid_kiss_global.radio_interrupt()
        

    @staticmethod
    def control(con):
        '''
        Set with way to control rover
        1=radio 2=wifi 3=3g4g
        '''        
        try:
            steelsquid_kiss_global.radio_request("control", [con, "1234567"])
        except:
            pass
        IO.OUTPUT.led_control(con)
        SETTINGS.control = con
        steelsquid_kiss_global.save_module_settings()
        if SETTINGS.control==1:
            steelsquid_kiss_global.radio_switch(steelsquid_kiss_global.TYPE_HMTRLRS)
        else:
            steelsquid_kiss_global.radio_switch(steelsquid_kiss_global.TYPE_TCP)
        steelsquid_kiss_global.restart(delay=4)


    @staticmethod
    def show(this):
        '''
        Show this on screen
        1 = Save   2 = settings   3 = Map   4 = FPV
        '''        
        if this==1 and UTILS.get_save_directory() == None:
            steelsquid_utils.error("No USB stick!")
            IO.OUTPUT.led_save_flash()
        else:
            RADIO.LOCAL.show = this
            # Save
            if RADIO.LOCAL.show == 1:
                steelsquid_gstreamer.save(True)
                IO.OUTPUT.led_save(True)
                IO.OUTPUT.led_fpv(True)                
                IO.OUTPUT.led_settings(False)
                IO.OUTPUT.led_map(False)
                if not DYNAMIC.timer:
                    IO.OUTPUT.led_timer(True)
                    DYNAMIC.timer_start = datetime.datetime.now()
                    DYNAMIC.timer = True
            # Settings
            elif RADIO.LOCAL.show == 2:
                steelsquid_gstreamer.save(False)
                IO.OUTPUT.led_save(False)
                IO.OUTPUT.led_fpv(False)                
                IO.OUTPUT.led_settings(True)
                IO.OUTPUT.led_map(False)
            # Map
            elif RADIO.LOCAL.show == 3:
                steelsquid_gstreamer.save(False)
                IO.OUTPUT.led_save(False)
                IO.OUTPUT.led_fpv(False)                
                IO.OUTPUT.led_settings(False)
                IO.OUTPUT.led_map(True)
            # FPV
            elif RADIO.LOCAL.show == 4:
                if steelsquid_gstreamer.save_to_disk:
                    steelsquid_gstreamer.save(False)
                steelsquid_gstreamer.video(True)
                steelsquid_gstreamer.audio(True)
                IO.OUTPUT.led_save(False)
                IO.OUTPUT.led_fpv(True)                
                IO.OUTPUT.led_settings(False)
                IO.OUTPUT.led_map(False)                            
            steelsquid_kiss_global.radio_interrupt()


    @staticmethod
    def pir(front, left, right, back):
        '''
        PIR movement
        '''   
        UTILS.play("warning.wav")     

                


        
        



        






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
        IO.OUTPUT.led_error_flash()

        
    @staticmethod
    def to_on_off(boolean):
        '''
        to_on_off
        '''
        if boolean:
            return "On"
        else:
            return "Off"        
            
            
    @staticmethod
    def get_save_file(fname):
        '''
        get_save_file
        '''
        directory = None
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        if directory != None:
            d = os.path.join(directory, steelsquid_utils.get_date())
            t = os.path.join(d, steelsquid_utils.get_time(delemitter="")+"_"+fname)
            try:
                os.mkdir(d);
            except:
                pass
            return t
        else:
            raise Exception("No USB disk found")
            
            
    @staticmethod
    def get_save_directory():
        '''
        get_save_file
        '''
        directory = None
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        return directory         


    @staticmethod
    def is_usb_connected():
        '''
        Is a usb disc connected
        '''
        directory = None
        for name in os.listdir("/media"):
            directory = os.path.join("/media", name)
            if not os.path.isdir(directory) or name == "HiLink":
                directory = None
            else:
                break
        return directory != None


    @staticmethod
    def check_motor_values(motor_left, motor_right):
        '''
        Is motor values OK
        '''
        if motor_right>RADIO.REMOTE.motor_max:
            motor_right = RADIO.REMOTE.motor_max
        elif motor_right<RADIO.REMOTE.motor_max*-1:
            motor_right = RADIO.REMOTE.motor_max*-1
        if motor_left>RADIO.REMOTE.motor_max:
            motor_left = RADIO.REMOTE.motor_max
        elif motor_left<RADIO.REMOTE.motor_max*-1:
            motor_left = RADIO.REMOTE.motor_max*-1
        return motor_left, motor_right


    @staticmethod
    def play(sound, times = 1, sleep = 0):
        '''
        Play a sound
        ''' 
        sound = "/opt/steelsquid/web/snd/"+sound
        thread.start_new_thread(UTILS._play, (sound, times, sleep))
        

    @staticmethod
    def _play(sound, times, sleep1):
        time.sleep(sleep1)
        for i in range(times):
            steelsquid_utils.execute_system_command_blind(["aplay", sound])







