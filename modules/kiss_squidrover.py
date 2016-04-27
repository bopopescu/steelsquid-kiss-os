#!/usr/bin/python -OO


'''.
Fuctionality for my squid 8wd rover

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-03-13 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_kiss_global
import steelsquid_nm
import steelsquid_kiss_boot
import time
import datetime
import steelsquid_hmtrlrs
from decimal import Decimal
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
    steelsquid_kiss_global.clear_modules_settings("kiss_squidrover")
    # Enable transeiver as client
    steelsquid_kiss_global.hmtrlrs_status("server")
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
    # Change GPIO for transceiver
    #steelsquid_utils.set_parameter("hmtrlrs_config_gpio", str(STATIC.hmtrlrs_config_gpio))
    #steelsquid_utils.set_parameter("hmtrlrs_reset_gpio", str(STATIC.hmtrlrs_reset_gpio))


def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    # Enable the automatic print if IP to LCD
    steelsquid_utils.del_flag("no_net_to_lcd")
    # Remove the voltage warning and power off (lipo 4s)
    steelsquid_utils.del_parameter("voltage_warning")
    # Disable the HM-TRLR-S
    steelsquid_kiss_global.hmtrlrs_status(None)






class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # voltage warning (lipo 7s)
    voltage_warning = 24.5
    
    # Max motor speed
    motor_max = 300

    # When system start move servo here
    servo_position_pan_start = 400

    # Max Servo position
    servo_position_pan_max = 590

    # Min Servo position
    servo_position_pan_min = 180

    # When system start move servo here
    servo_position_tilt_start = 400

    # Max Servo position
    servo_position_tilt_max = 530

    # Min Servo position
    servo_position_tilt_min = 280






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

    # Using this to know when to turn on and off the cruise control
    cruise_enabled = False






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
        steelsquid_utils.shout("Steelsquid SquidRover started")
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        GLOBAL.camera(STATIC.servo_position_pan_start, STATIC.servo_position_tilt_start)
        
        
    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        GLOBAL.drive(0, 0)
        steelsquid_pi.cleanup()      
        
        
        



class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    @staticmethod
    def update_lcd_and_voltage():
        '''
        Execute every 2 second
        ''' 
        try:
            # Print IP/voltage to LCD
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
                # Write text to LCD
                if len(print_this)>0:
                    new_lcd_message = "\n".join(print_this)
                    if new_lcd_message!=DYNAMIC.last_lcd_message:
                        DYNAMIC.last_lcd_message = new_lcd_message
                        steelsquid_pi.ssd1306_write(new_lcd_message, 0)
            else:
                DYNAMIC.stop_next_lcd_message=False
            # Read rover voltage
            RADIO_SYNC.SERVER.voltage_rover = GLOBAL.voltage()
        except:
            if steelsquid_kiss_boot.running:
                steelsquid_utils.shout()
        return 2 # Execute this method again in 2 second
        
        




class RADIO(object):
    '''
    If you have a NRF24L01+ or HM-TRLR-S transceiver connected to this device you can use server/client or master/slave functionality.
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
    def horn(parameters):
        '''
        Horn
        A request from client to sound the horn
        '''
        GLOBAL.horn()
        return []


    @staticmethod
    def left(parameters):
        '''
        Center
        A request from client to left the camera
        '''
        GLOBAL.camera(STATIC.servo_position_pan_max, STATIC.servo_position_tilt_start)
        return []


    @staticmethod
    def center(parameters):
        '''
        Center
        A request from client to center the camera
        '''
        GLOBAL.camera(STATIC.servo_position_pan_start, STATIC.servo_position_tilt_start)
        return []


    @staticmethod
    def right(parameters):
        '''
        Center
        A request from client to right the camera
        '''
        GLOBAL.camera(STATIC.servo_position_pan_min, STATIC.servo_position_tilt_start)
        return []


    @staticmethod
    def text_to_speach(parameters):
        '''
        Say something
        '''
        espeak.synth(parameters[0])
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
            RADIO_SYNC.CLIENT.is_cruise_on = False
            DYNAMIC.cruise_enabled = False
            GLOBAL.drive(0, 0)
        # Check if connection is lost
        if seconds_since_last_ok_ping>steelsquid_hmtrlrs.LINK_LOST_SUGGESTION:
            GLOBAL.connection_lost()
        else:
            # Enable or disable network
            if steelsquid_nm.get_network_status()!=RADIO_SYNC.CLIENT.is_network_on:
                steelsquid_nm.set_network_status(RADIO_SYNC.CLIENT.is_network_on)
            # Cruise control
            if RADIO_SYNC.CLIENT.is_cruise_on and not DYNAMIC.cruise_enabled:
                DYNAMIC.cruise_enabled = True
                GLOBAL.drive(0, 0)
            elif not RADIO_SYNC.CLIENT.is_cruise_on and DYNAMIC.cruise_enabled:
                DYNAMIC.cruise_enabled = False
                GLOBAL.drive(0, 0)
            # Headlamps
            GLOBAL.headlights(RADIO_SYNC.CLIENT.is_headlights_on)   
            # highbeam
            GLOBAL.highbeam(RADIO_SYNC.CLIENT.is_highbeam_on)   
            # highbeam
            GLOBAL.video(RADIO_SYNC.CLIENT.is_video_on)   


    class CLIENT(object):
        '''
        All varibales in this class will be synced from the client to the server
        '''
        # Enable/disable the network (wifi)
        is_network_on = True

        # Enable/disable the video transmitter and reseiver
        is_video_on = False
        
        # Is cruise control enabled
        is_cruise_on = False
        
        # Is the headlights on
        is_headlights_on = False

        # Is the highbeam on
        is_highbeam_on = False
        
        
    class SERVER(object):
        '''
        All varibales in this class will be synced from the server to the client
        '''
        # Voltage for the rover
        voltage_rover = 0.0






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
        GLOBAL.drive(RADIO_PUSH_1.motor_left, RADIO_PUSH_1.motor_right)






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
    
    # Speed of the motors
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
        GLOBAL.camera(RADIO_PUSH_2.camera_pan, RADIO_PUSH_2.camera_tilt)






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
    def connection_lost():
        '''
        The connection to remote is lost
        ''' 
        pass
        

    @staticmethod
    def horn():
        '''
        Sound horn for a second
        '''
        pass
        steelsquid_pi.gpio_flash(6, None, 0.5)


    @staticmethod
    def headlights(status):
        '''
        headlights
        '''
        steelsquid_pi.gpio_set(26, status)


    @staticmethod
    def highbeam(status):
        '''
        highbeam
        '''
        steelsquid_pi.gpio_set(13, status)


    @staticmethod
    def video(status):
        '''
        Is video on
        '''
        steelsquid_pi.gpio_set(19, status)


    @staticmethod
    def camera(pan, tilt):
        '''
        Move servo
        '''
        if pan<STATIC.servo_position_pan_min:
            pan = STATIC.servo_position_pan_min
        elif pan>STATIC.servo_position_pan_max:
            pan = STATIC.servo_position_pan_max
        if tilt<STATIC.servo_position_tilt_min:
            tilt = STATIC.servo_position_tilt_min
        elif tilt>STATIC.servo_position_tilt_max:
            tilt = STATIC.servo_position_tilt_max
        steelsquid_pi.pca9685_move(14, pan)
        steelsquid_pi.pca9685_move(15, tilt)


    @staticmethod
    def drive(left, right):
        '''
        Drive
        '''
        # Cruise controll
        if RADIO_SYNC.CLIENT.is_cruise_on:
            GLOBAL.cruise_enabled = True
            if left > right:
                diff = left - right
                left = STATIC.motor_max
                right = STATIC.motor_max - diff/2
            else:
                diff = right - left
                left = STATIC.motor_max - diff/2
                right = STATIC.motor_max
        # Check values
        if left>STATIC.motor_max:
            left = STATIC.motor_max
        elif left<STATIC.motor_max*-1:
            left = STATIC.motor_max*-1
        if right>STATIC.motor_max:
            right = STATIC.motor_max
        elif right<STATIC.motor_max*-1:
            right = STATIC.motor_max*-1
        steelsquid_pi.diablo_motor_1(left)
        steelsquid_pi.diablo_motor_2(right)


    @staticmethod
    def voltage():
        '''
        Read voltage
        '''
        v = steelsquid_pi.ads1015(48, 0)*11.14
        v = Decimal(v)
        v = round(v, 2)
        return v
