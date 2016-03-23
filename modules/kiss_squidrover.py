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
import time
import datetime
import steelsquid_hmtrlrs


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
    steelsquid_utils.del_parameter("voltage_poweroff")
    # Disable the HM-TRLR-S
    steelsquid_kiss_global.hmtrlrs_status(None)






class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # voltage warning (lipo 7s)
    voltage_warning = 24.5
    
    # GPIO for the HM-TRLR-S
    hmtrlrs_config_gpio = 4
    hmtrlrs_reset_gpio = 18

    # When system start move servo here
    servo_position_pan_start = 120

    # Max Servo position
    servo_position_pan_max = 255

    # Min Servo position
    servo_position_pan_min = 0

    # When system start move servo here
    servo_position_tilt_start = 100

    # Max Servo position
    servo_position_tilt_max = 225

    # Min Servo position
    servo_position_tilt_min = 70

    # Max motor speed
    motor_max = 200





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

    # Current pan
    pan = STATIC.servo_position_pan_start

    # Current tilt
    tilt = STATIC.servo_position_tilt_start

    # Last time the client send a drive command
    last_command = datetime.datetime.now()
    
    # Is cuise control on
    is_cruise_on = False




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
    
    # Is the transceiver on
    is_video_on = False

    
        



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
        import steelsquid_piio
        steelsquid_piio.servo(1, DYNAMIC.pan)
        steelsquid_piio.servo(2, DYNAMIC.tilt)
        
        

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
    
    @staticmethod
    def on_loop_slow():
        '''
        Execute every 2 second
        ''' 
        # If more than 2 second since last command stop the drive (connection may be lost)
        drive_delta = datetime.datetime.now() - DYNAMIC.last_command
        sec = 2
        if DYNAMIC.is_cruise_on:
            sec=4
        if drive_delta.total_seconds()>sec:
            DYNAMIC.is_cruise_on=False
            GLOBAL.drive(0, 0)
        # If more than 16 seconds beep and flash lights
        if drive_delta.total_seconds()>16:
            import steelsquid_piio
            steelsquid_piio.power_flash(1, status=None, seconds=1)
            steelsquid_piio.power_flash(2, status=None, seconds=1) 
            steelsquid_piio.power_flash(3, status=None, seconds=1) 
            steelsquid_piio.power_flash(4, status=None, seconds=1) 
            steelsquid_piio.power_flash(5, status=None, seconds=1) 
            steelsquid_piio.power_flash(6, status=None, seconds=0.01)
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
        # Read voltage
        import steelsquid_piio
        steelsquid_kiss_global.last_voltage = steelsquid_piio.volt(2, 4)
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
    def r(parameters):
        '''
        Cruise controll
        '''
        DYNAMIC.is_cruise_on = not DYNAMIC.is_cruise_on
        if DYNAMIC.is_cruise_on:
            GLOBAL.drive(0, 0)
            return [1]
        else:
            GLOBAL.drive(0, 0)
            return [0]


    @staticmethod
    def n(parameters):
        '''
        Network
        A request from client to enable or dissable network
        '''
        # Disable network
        steelsquid_nm.set_network_status(parameters[0]=="1")
        return []


    @staticmethod
    def t(parameters):
        '''
        TX
        A request from client to enable or disable the video transmitter
        '''
        return []


    @staticmethod
    def d(parameters):
        '''
        Drive
        A request from client drive the rover
        '''
        try:
            # Speed of the left motor (-1000 to 1000)
            left_motor = int(parameters[0])
            # Speed of the right motor (-1000 to 1000)
            right_motor = int(parameters[1])
            # Set motor speed
            GLOBAL.drive(left_motor, right_motor)
            # Set last command
            DYNAMIC.last_command = datetime.datetime.now()
        except:
            pass


    @staticmethod
    def c(parameters):
        '''
        Camera
        A request from client to tilt or pan camera
        '''
        try:
            # pan camera left and right
            pan = int(parameters[0])
            # Tilt camera up and down
            tilt = int(parameters[1])
            GLOBAL.pan(pan/10)
            GLOBAL.tilt(tilt/10)
            # Set last command
            DYNAMIC.last_command = datetime.datetime.now()
        except:
            pass


    @staticmethod
    def h(parameters):
        '''
        Horn
        A request from client to sound the horn
        '''
        import steelsquid_piio
        steelsquid_piio.power_flash(6)
        return []


    @staticmethod
    def e(parameters):
        '''
        Center
        A request from client to center the camera
        '''
        import steelsquid_piio
        DYNAMIC.pan = STATIC.servo_position_pan_start
        DYNAMIC.tilt = STATIC.servo_position_tilt_start
        steelsquid_piio.servo(1, DYNAMIC.pan)
        steelsquid_piio.servo(2, DYNAMIC.tilt)
        return []


    @staticmethod
    def l(parameters):
        '''
        Headlight
        A request from client to turn on headlights
        '''
        import steelsquid_piio
        status = steelsquid_utils.to_boolean(parameters[0])
        steelsquid_piio.power(1, status)
        steelsquid_piio.power(2, status) 
        steelsquid_piio.power(3, status) 
        steelsquid_piio.power(4, status) 
        steelsquid_piio.power(5, status) 
        return []


    @staticmethod
    def u(parameters):
        '''
        Update
        A request from remote to rover for:
         - Left motor speed
         - Right motor speed
         - Pan camera
         - Tilt camera
         - tx
         - Headlght
        Send back this to remote:
         - battery voltage
        '''
        # Speed of the left motor (-1000 to 1000)
        left = int(parameters[0])
        # Speed of the right motor (-1000 to 1000)
        right = int(parameters[1])
        # Tilt camera up and down
        pan = int(parameters[2])
        # pan camera left and right
        tilt = int(parameters[3])
        # Enable the video
        tx = parameters[4]=="1"
        # Enable the video
        GLOBAL.headlights(parameters[5]=="1")
        # Camera
        GLOBAL.pan(pan/10)
        GLOBAL.tilt(tilt/10)
        # Drive
        GLOBAL.drive(left, right)
        # Set last command
        DYNAMIC.last_command = datetime.datetime.now()
        if DYNAMIC.is_cruise_on:
            return [steelsquid_kiss_global.last_voltage, "1"]
        else:
            return [steelsquid_kiss_global.last_voltage, "0"]




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
    def headlights(status):
        '''
        headlights
        '''
        import steelsquid_piio
        steelsquid_piio.power(1, status)
        steelsquid_piio.power(2, status) 
        steelsquid_piio.power(3, status) 
        steelsquid_piio.power(4, status) 
        steelsquid_piio.power(5, status)         


    @staticmethod
    def pan(pan):
        '''
        Move pan servo
        '''
        import steelsquid_piio
        DYNAMIC.pan = DYNAMIC.pan-pan
        if DYNAMIC.pan<STATIC.servo_position_pan_min:
            DYNAMIC.pan = STATIC.servo_position_pan_min
        elif DYNAMIC.pan>STATIC.servo_position_pan_max:
            DYNAMIC.pan = STATIC.servo_position_pan_max
        steelsquid_piio.servo(1, DYNAMIC.pan)


    @staticmethod
    def tilt(tilt):
        '''
        Move tilt servo
        '''
        import steelsquid_piio
        DYNAMIC.tilt = DYNAMIC.tilt-tilt
        if DYNAMIC.tilt<STATIC.servo_position_tilt_min:
            DYNAMIC.tilt = STATIC.servo_position_tilt_min
        elif DYNAMIC.tilt>STATIC.servo_position_tilt_max:
            DYNAMIC.tilt = STATIC.servo_position_tilt_max
        steelsquid_piio.servo(2, DYNAMIC.tilt)


    @staticmethod
    def drive(left, right):
        '''
        Drive
        '''
        # Cruise controll
        if DYNAMIC.is_cruise_on:
            if left > right:
                diff = left - right
                left = 1000
                right = 1000 - diff/2
            else:
                diff = right - left
                left = 1000 - diff/2
                right = 1000
        # Check values
        if left>STATIC.motor_max:
            left = STATIC.motor_max
        elif left<STATIC.motor_max*-1:
            left = STATIC.motor_max*-1
        if right>STATIC.motor_max:
            right = STATIC.motor_max
        elif right<STATIC.motor_max*-1:
            right = STATIC.motor_max*-1
        steelsquid_pi.diablo_motor_1(left);
        steelsquid_pi.diablo_motor_2(right);


