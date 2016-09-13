#!/usr/bin/python -OO


'''.
Fuctionality for my remote station caser
Use it to control rovers...and more...

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
    steelsquid_kiss_global.clear_modules_settings("kiss_station")
    # Enable transeiver as client
    steelsquid_kiss_global.hmtrlrs_status("client")
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
    # Change GPIO for transceiver
    steelsquid_utils.set_parameter("hmtrlrs_config_gpio", str(STATIC.hmtrlrs_config_gpio))
    steelsquid_utils.set_parameter("hmtrlrs_reset_gpio", str(STATIC.hmtrlrs_reset_gpio))
    # Enable midori browser start on the composite screen
    steelsquid_utils.execute_system_command_blind(['steelsquid', 'mbrowser-on', 'http://localhost/speak'])
    


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
    steelsquid_utils.del_parameter("voltage_poweroff")
    # Disable the HM-TRLR-S
    steelsquid_kiss_global.hmtrlrs_status(None)






class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # Station voltages(lipo 3s) 
    station_voltage_max = 12.6      # 4.2V
    station_voltage_warning = 10.5  # 3.5V
    station_voltage_min = 9.6       # 3.2V

    # Rover voltages(lipo 4s)
    rover_voltage_max = 16.8        # 4.2V
    rover_voltage_warning = 14      # 3.5V
    rover_voltage_min = 12.8        # 3.2V
    
    # GPIO for the HM-TRLR-S
    hmtrlrs_config_gpio = 25
    hmtrlrs_reset_gpio = 23

    # Max motor speed
    motor_max = 1000

    # When system start move servo here
    servo_position_pan_start = 370

    # Max Servo position
    servo_position_pan_max = 615

    # Min Servo position
    servo_position_pan_min = 140

    # When system start move servo here
    servo_position_tilt_start = 300

    # Max Servo position
    servo_position_tilt_max = 430

    # Min Servo position
    servo_position_tilt_min = 140






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

    # Remote station voltage (this station)
    voltage_station = 0
    





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
        steelsquid_utils.shout("Steelsquid Remote Station started")
        # Reset some GPIO
        steelsquid_pi.gpio_set(8, False)
        # Enable network by default
        try:
            steelsquid_nm.set_network_status(True)        
        except:
            pass
        # Set the on OK and ERROR callback methods...they just flash some LED
        steelsquid_utils.on_ok_callback_method=GLOBAL.ok_led_flash
        steelsquid_utils.on_err_callback_method=GLOBAL.err_led_flash
        # Start listen on buttons
        steelsquid_pi.mcp23017_click(21, 0, SYSTEM.on_network_button, pullup=True, rpi_gpio=26)
        steelsquid_pi.mcp23017_click(21, 3, SYSTEM.on_transceiver_button, pullup=True, rpi_gpio=26)
        steelsquid_pi.mcp23017_click(21, 6, SYSTEM.on_video_button, pullup=True, rpi_gpio=26)
        steelsquid_pi.gpio_click(7, SYSTEM.on_horn_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(6, SYSTEM.on_headlights_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(17, SYSTEM.on_left_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(22, SYSTEM.on_center_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(24, SYSTEM.on_right_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(9, SYSTEM.on_cruise_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(13, SYSTEM.on_highbeam_button, resistor=steelsquid_pi.PULL_UP)
        steelsquid_pi.gpio_click(11, SYSTEM.on_slow_button, resistor=steelsquid_pi.PULL_UP)
        # Is network enabled (light the led?)
        GLOBAL.network_on_led(steelsquid_nm.get_network_status())
        # Is transceiver enabled
        GLOBAL.transceiver_on_led(not steelsquid_hmtrlrs.disable)   
        

    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        steelsquid_pi.cleanup()
       
       
    @staticmethod
    def on_network_button(address, pin):
        '''
        When the toggle network button is clicked
        '''        
        if steelsquid_nm.get_network_status():
            GLOBAL.write_message("Disable the network\nPlease wait!")
            # LED
            GLOBAL.network_on_led(False)
            # Disable network localy
            steelsquid_nm.set_network_status(False)
            # Send disable network command to rover
            RADIO_SYNC.CLIENT.is_network_on = False
        else:
            GLOBAL.write_message("Enable the network\nPlease wait!")
            # LED
            GLOBAL.network_on_led(True)
            # Enable network localy
            steelsquid_nm.set_network_status(True)
            # Send enable network command to rover
            RADIO_SYNC.CLIENT.is_network_on = True
               

    @staticmethod
    def on_transceiver_button(address, pin):
        '''
        When the toggle transceiver button is clicked
        '''
        if not steelsquid_hmtrlrs.disable:
            GLOBAL.write_message("Disable the transceiver\nPlease wait!")
        else:
            GLOBAL.write_message("Enable the transceiver\nPlease wait!")
        steelsquid_hmtrlrs.disable = not steelsquid_hmtrlrs.disable
        GLOBAL.transceiver_on_led(not steelsquid_hmtrlrs.disable)      

        
    @staticmethod
    def on_video_button(address, pin):
        '''
        When the toggle video button is clicked
        '''
        if RADIO_SYNC.CLIENT.is_video_on:
            GLOBAL.write_message("Disable the video\nPlease wait!")
        else:
            GLOBAL.write_message("Enable the video\nPlease wait!")
        # Change the value (Will sync with rover)
        RADIO_SYNC.CLIENT.is_video_on = not RADIO_SYNC.CLIENT.is_video_on
        # Do it localy
        GLOBAL.video_on_led(RADIO_SYNC.CLIENT.is_video_on)        
        GLOBAL.video(RADIO_SYNC.CLIENT.is_video_on)        
        

    @staticmethod
    def on_horn_button(pin):
        '''
        When the horn button is clicked
        '''
        # Flash icon
        GLOBAL.horn_led_flash()        
        # Send horn command to rover
        steelsquid_hmtrlrs.request("horn")
                
        
    @staticmethod
    def on_left_button(pin):
        '''
        Left camera button clicked
        '''
        # Flash icon
        GLOBAL.left_led_flash()        
        # Send center command to rover
        steelsquid_hmtrlrs.request("left")
        # Center local values
        RADIO_PUSH_2.camera_pan=STATIC.servo_position_pan_max
        RADIO_PUSH_2.camera_tilt=STATIC.servo_position_tilt_start
        

    @staticmethod
    def on_center_button(pin):
        '''
        Center camera button clicked
        '''
        # Flash icon
        GLOBAL.center_led_flash()        
        # Send center command to rover
        steelsquid_hmtrlrs.request("center")
        # Center local values
        RADIO_PUSH_2.camera_pan=STATIC.servo_position_pan_start
        RADIO_PUSH_2.camera_tilt=STATIC.servo_position_tilt_start


    @staticmethod
    def on_right_button(pin):
        '''
        Right camera button clicked
        '''
        # Flash icon
        GLOBAL.right_led_flash()        
        # Send center command to rover
        steelsquid_hmtrlrs.request("right")
        # Center local values
        RADIO_PUSH_2.camera_pan=STATIC.servo_position_pan_min
        RADIO_PUSH_2.camera_tilt=STATIC.servo_position_tilt_start

                
    @staticmethod
    def on_cruise_button(pin):
        '''
        Cruise controll button clicked
        '''
        # Change the value (Will sync with rover)
        RADIO_SYNC.CLIENT.is_cruise_on = not RADIO_SYNC.CLIENT.is_cruise_on
        steelsquid_kiss_global.radio_interrupt()
        # Light the led
        GLOBAL.cruise_led(RADIO_SYNC.CLIENT.is_cruise_on)


    @staticmethod
    def on_headlights_button(pin):
        '''
        When the headlights button is clicked
        '''
        # Change the value (Will sync with rover)
        RADIO_SYNC.CLIENT.is_headlights_on = not RADIO_SYNC.CLIENT.is_headlights_on
        steelsquid_kiss_global.radio_interrupt()
        # Light the led
        GLOBAL.headlamp_led(RADIO_SYNC.CLIENT.is_headlights_on)


    @staticmethod
    def on_highbeam_button(pin):
        '''
        When the highbeam button is clicked
        '''
        # Change the value (Will sync with rover)
        RADIO_SYNC.CLIENT.is_highbeam_on = not RADIO_SYNC.CLIENT.is_highbeam_on
        steelsquid_kiss_global.radio_interrupt()
        # Light the led
        GLOBAL.highbeam_led(RADIO_SYNC.CLIENT.is_highbeam_on)
       
        
    @staticmethod
    def on_slow_button(pin):
        '''
        Slow button clicked
        '''
        # Light the led
        GLOBAL.slow_led(RADIO_SYNC.CLIENT.is_slow_on)
        
        



class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''
    
    @staticmethod
    def Update_lcd_and_leds():
        '''
        Execute every 1 second
        ''' 
        try:
            # Read station voltage
            DYNAMIC.voltage_station = GLOBAL.read_in_volt(2, 3)
            # Light the voltage bars
            GLOBAL.station_bar(DYNAMIC.voltage_station)
            GLOBAL.rover_bar(RADIO_SYNC.SERVER.voltage_rover)
            # Voltage warning
            if DYNAMIC.voltage_station<STATIC.station_voltage_warning or RADIO_SYNC.SERVER.voltage_rover<STATIC.rover_voltage_warning:
                GLOBAL.err_led_flash()
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
                # Voltage
                if DYNAMIC.voltage_station<STATIC.station_voltage_warning:
                    print_this.append("Statin: " + str(DYNAMIC.voltage_station) + "V  ***LOW***")
                else:
                    print_this.append("Statin: " + str(DYNAMIC.voltage_station) + "V")
                if not steelsquid_hmtrlrs.is_linked():
                    print_this.append("Rover: No connection!")
                elif RADIO_SYNC.SERVER.voltage_rover<STATIC.rover_voltage_warning:
                    print_this.append("Rover: " + str(RADIO_SYNC.SERVER.voltage_rover)+ "V  ***LOW***")
                else:
                    print_this.append("Rover: " + str(RADIO_SYNC.SERVER.voltage_rover)+ "V")
                print_this.append("            " + str(RADIO_SYNC.SERVER.ampere_rover)+ "A")
                # Set Network LED status
                GLOBAL.network_conneced_led(connected)
                # Write text to LCD
                if len(print_this)>0:
                    new_lcd_message = "\n".join(print_this)
                    if new_lcd_message!=DYNAMIC.last_lcd_message:
                        DYNAMIC.last_lcd_message = new_lcd_message
                        steelsquid_pi.ssd1306_write(new_lcd_message, 0)
            else:
                DYNAMIC.stop_next_lcd_message=False
            # Is network enabled LED
            GLOBAL.network_on_led(steelsquid_nm.get_network_status())             
        except:
            steelsquid_utils.shout()
        return 1 # Execute this method again in 1 second






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
        # Check if connection is lost
        if seconds_since_last_ok_ping<steelsquid_hmtrlrs.LINK_LOST_SUGGESTION:
            GLOBAL.transceiver_connected_led(True)
        else:
            GLOBAL.transceiver_connected_led(False)
        
        
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

        # Ampere for the rover
        ampere_rover = 0.0






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
    
    # This will not sdend to server
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
        # Get the drive joystick location
        drive = steelsquid_pi.po12_adc(3, 3)
        drive = 515 - drive
        if drive > -20 and drive < 20:
            drive = 0
        steer = steelsquid_pi.po12_adc(4, 3)
        steer = 515 - steer
        if steer > -20 and steer < 20:
            steer = 0
        # Remap the joystick range
        drive = int(steelsquid_utils.remap(drive, -170, 170, STATIC.motor_max*-1, STATIC.motor_max))
        steer = int(steelsquid_utils.remap(steer, -170, 170, STATIC.motor_max*-1, STATIC.motor_max))
        # Convert to left and right motor values
        motor_left = drive
        motor_right = drive
        if steer>0 or steer<0:
            motor_right = motor_right - steer
            motor_left = motor_left + steer
        
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
        if motor_left == 0 and motor_right==0:
            if RADIO_PUSH_1._sent_zero_count>=6:
                return False # Do not update to server
            else:
                RADIO_PUSH_1._sent_zero_count=RADIO_PUSH_1._sent_zero_count+1
                return True # Do not update to server
        else:
            RADIO_PUSH_1._sent_zero_count=0
            return True # Send update to server






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
        # Get the tilt/pan joystick location
        pan = steelsquid_pi.po12_adc(2, 3)
        pan = pan - 515
        if pan > -20 and pan < 20:
            pan = 0
        tilt = steelsquid_pi.po12_adc(1, 3)
        tilt = 515 - tilt
        if tilt > -20 and tilt < 20:
            tilt = 0
        if pan != 0 or tilt!=0:
            pan = RADIO_PUSH_2.camera_pan - int(pan/15)
            tilt = RADIO_PUSH_2.camera_tilt - int(tilt/15)
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
    def text_to_speach(session_id, parameters):
        '''
        Get info on the rover
        '''
        print "AAA"
        steelsquid_hmtrlrs.request("text_to_speach", parameters)




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
    def ok_led_flash():
        '''
        Flash the OK LED
        ''' 
        steelsquid_pi.mcp23017_flash(21, 9, None, 0.1)


    @staticmethod
    def err_led_flash():
        '''
        Flash the ERROR LED
        ''' 
        steelsquid_pi.mcp23017_flash(21, 10, None, 0.2)


    @staticmethod
    def network_on_led(status):
        '''
        Turn the network LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 1, status)


    @staticmethod
    def network_conneced_led(status):
        '''
        Turn the network connected LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 2, status)


    @staticmethod
    def transceiver_on_led(status):
        '''
        Turn the transceiver LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 4, status)


    @staticmethod
    def transceiver_connected_led(status):
        '''
        Turn the transceiver connected LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 5, status)


    @staticmethod
    def video(status):
        '''
        Turn the power to the monitor and RX on or off
        ''' 
        steelsquid_pi.mcp23017_set(20, 0, status)


    @staticmethod
    def video_on_led(status):
        '''
        Turn the video on LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 7, status)


    @staticmethod
    def video_tx_led(status):
        '''
        Turn the rover is transmitting video LED on or off
        ''' 
        steelsquid_pi.mcp23017_set(21, 8, status)


    @staticmethod
    def headlamp_led(status):
        '''
        Turn the rover headlight LED on or off
        ''' 
        steelsquid_pi.gpio_set(12, status)


    @staticmethod
    def highbeam_led(status):
        '''
        Turn the rover highbeam_led LED on or off
        ''' 
        steelsquid_pi.gpio_set(16, status)


    @staticmethod
    def cruise_led(status):
        '''
        Turn the rover cruise controll LED on or off
        ''' 
        steelsquid_pi.gpio_set(25, status)


    @staticmethod
    def slow_led(status):
        '''
        Turn the rover slow speed LED on or off
        ''' 
        steelsquid_pi.gpio_set(8, status)


    @staticmethod
    def horn_led_flash():
        '''
        FLash the horn led
        ''' 
        steelsquid_pi.gpio_flash(5, None, 1)


    @staticmethod
    def left_led_flash():
        '''
        FLash
        ''' 
        steelsquid_pi.gpio_flash(27, None, 1)


    @staticmethod
    def center_led_flash():
        '''
        FLash the horn led
        ''' 
        steelsquid_pi.gpio_flash(23, None, 1)


    @staticmethod
    def right_led_flash():
        '''
        FLash
        ''' 
        steelsquid_pi.gpio_flash(10, None, 1)


    @staticmethod
    def station_bar(voltage):
        '''
        Light the station led bar (voltage)
        ''' 
        leds = int(steelsquid_utils.remap(voltage, STATIC.station_voltage_min, STATIC.station_voltage_max, 1, 10))
        if leds<=1:
            steelsquid_pi.mcp23017_flash(20, 10)
            steelsquid_pi.mcp23017_set(20, 9, False)
            steelsquid_pi.mcp23017_set(20, 8, False)
            steelsquid_pi.mcp23017_set(20, 7, False)
            steelsquid_pi.mcp23017_set(20, 6, False)
            steelsquid_pi.mcp23017_set(20, 5, False)
            steelsquid_pi.mcp23017_set(20, 4, False)
            steelsquid_pi.mcp23017_set(20, 3, False)
            steelsquid_pi.mcp23017_set(20, 2, False)
            steelsquid_pi.mcp23017_set(20, 1, False)
        elif leds<=2:
            steelsquid_pi.mcp23017_flash(20, 10)
            steelsquid_pi.mcp23017_flash(20, 9)
            steelsquid_pi.mcp23017_set(20, 8, False)
            steelsquid_pi.mcp23017_set(20, 7, False)
            steelsquid_pi.mcp23017_set(20, 6, False)
            steelsquid_pi.mcp23017_set(20, 5, False)
            steelsquid_pi.mcp23017_set(20, 4, False)
            steelsquid_pi.mcp23017_set(20, 2, False)
            steelsquid_pi.mcp23017_set(20, 1, False)
        else:
            steelsquid_pi.mcp23017_set(20, 10, not leds <= 1)
            steelsquid_pi.mcp23017_set(20, 9, not leds <= 2)
            steelsquid_pi.mcp23017_set(20, 8, not leds <= 3)
            steelsquid_pi.mcp23017_set(20, 7, not leds <= 4)
            steelsquid_pi.mcp23017_set(20, 6, not leds <= 5)
            steelsquid_pi.mcp23017_set(20, 5, not leds <= 6)
            steelsquid_pi.mcp23017_set(20, 4, not leds <= 7)
            steelsquid_pi.mcp23017_set(20, 3, not leds <= 8)
            steelsquid_pi.mcp23017_set(20, 2, not leds <= 9)
            steelsquid_pi.mcp23017_set(20, 1, not leds <= 10)


    @staticmethod
    def rover_bar(voltage):
        '''
        Light the rover led bar (voltage)
        ''' 
        leds = int(steelsquid_utils.remap(voltage, STATIC.rover_voltage_min, STATIC.rover_voltage_max, 1, 10))
        if leds<=1:
            steelsquid_pi.mcp23017_set(20, 15, False)
            steelsquid_pi.mcp23017_set(20, 14, False)
            steelsquid_pi.mcp23017_set(20, 13, False)
            steelsquid_pi.mcp23017_set(20, 12, False)
            steelsquid_pi.mcp23017_set(20, 11, False)
            steelsquid_pi.mcp23017_set(21, 15, False)
            steelsquid_pi.mcp23017_set(21, 14, False)
            steelsquid_pi.mcp23017_set(21, 13, False)
            steelsquid_pi.mcp23017_set(21, 12, False)
            steelsquid_pi.mcp23017_flash(21, 11)
        elif leds<=2:
            steelsquid_pi.mcp23017_set(20, 15, False)
            steelsquid_pi.mcp23017_set(20, 14, False)
            steelsquid_pi.mcp23017_set(20, 13, False)
            steelsquid_pi.mcp23017_set(20, 12, False)
            steelsquid_pi.mcp23017_set(20, 11, False)
            steelsquid_pi.mcp23017_set(21, 15, False)
            steelsquid_pi.mcp23017_set(21, 14, False)
            steelsquid_pi.mcp23017_set(21, 13, False)
            steelsquid_pi.mcp23017_flash(21, 12)
            steelsquid_pi.mcp23017_flash(21, 11)
        else:
            steelsquid_pi.mcp23017_set(20, 15, not leds <= 10)
            steelsquid_pi.mcp23017_set(20, 14, not leds <= 9)
            steelsquid_pi.mcp23017_set(20, 13, not leds <= 8)
            steelsquid_pi.mcp23017_set(20, 12, not leds <= 7)
            steelsquid_pi.mcp23017_set(20, 11, not leds <= 6)
            steelsquid_pi.mcp23017_set(21, 15, not leds <= 5)
            steelsquid_pi.mcp23017_set(21, 14, not leds <= 4)
            steelsquid_pi.mcp23017_set(21, 13, not leds <= 3)
            steelsquid_pi.mcp23017_set(21, 12, not leds <= 2)
            steelsquid_pi.mcp23017_set(21, 11, not leds <= 1)


    @staticmethod
    def read_in_volt(number_of_decimals=-1, samples=1):
        '''
        Read main in voltage
        '''
        v = steelsquid_pi.po12_adc_volt(8, samples=samples) / float(steelsquid_utils.get_parameter("voltage_divider", "0.1179"))
        if number_of_decimals!=-1:
            v = Decimal(v)
            v = round(v, number_of_decimals)
        return v
