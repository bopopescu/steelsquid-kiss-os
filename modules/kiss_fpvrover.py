#!/usr/bin/python -OO


'''.
Fuctionality for my FPV rover

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-12-26 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_piio
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
    #Clear any saved settings for this module
    steelsquid_kiss_global.clear_modules_settings("kiss_fpvrover")
    # Is this the remote or the rover
    if argument!=None and (argument=="rover"):
        steelsquid_utils.set_flag("is_rover")
        # Enable the HM-TRLR-S as server
        steelsquid_kiss_global.hmtrlrs_status("server")
    else:
        steelsquid_utils.del_flag("is_rover")
        # Enable the HM-TRLR-S as client
        steelsquid_kiss_global.hmtrlrs_status("client")
    # Enable the link by default
    steelsquid_utils.set_flag("is_link_enabled")
    # Disable the automatic print if IP to LCD...this module will do it
    steelsquid_utils.set_flag("no_net_to_lcd")
    # Set the voltage warning and power off (lipo 4s)
    steelsquid_utils.set_parameter("voltage_warning", STATIC.voltage_warning)
    steelsquid_utils.set_parameter("voltage_poweroff", STATIC.voltage_poweroff)
    # Enable the PIIO board
    if not steelsquid_kiss_global.is_module_enabled("kiss_piio"):
        steelsquid_kiss_global.module_status("kiss_piio", True, restart=True) # Trigger reboot




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
    # Disable the PIIO board and PI camera streaming (if necessary)
    if steelsquid_kiss_global.is_module_enabled("kiss_piio"):
        steelsquid_kiss_global.module_status("kiss_piio", False, restart=True) # Trigger reboot




class STATIC(object):
    '''
    Put static variables here (Variables that never change).
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # voltage warning and power off (lipo 4s)
    voltage_warning = 13.8
    voltage_poweroff = 12.8

    # PIIO board LEDs
    network_led = 1
    low_speed_led = 5
    link_led = 2
    headlamp_led = 3
    cruise_control_led = 4
    link_toggle_led = 6

    # GPIO Buttons
    slow_drive_button = 1
    link_toggle_button = 2
    
    # PIIO board button
    network_button = 1
    headlamp_button = 6
    horn_button = 5
    center_button = 3
    channel_button = 2
    cruise_control_button = 4
    
    # ADC
    spin_pin = 1
    tilt_pin = 2
    drive_pin = 4
    steer_pin = 3




class DYNAMIC(object):
    '''
    Put dynamic variables here.
    If you have variables holding some data that you use and change in this module, you can put them here.
    Maybe toy enable something in the WEB class and want to use it from the LOOP class.
    Instead of adding it to either WEB or LOOP you can add it here.
    It is not necessary to put it her, but i think it is kind of nice to have it inside this class.
    '''
    
    # Cruise controll is sactive
    cruise_control = False    
    
    # Last LCD message to print
    last_lcd_message = None
    
    # Using this when i print a message to LCD, so the next ip/voltage uppdat dont ovrewrite the message to fast
    stop_next_lcd_message = False
    
    # Only send one halt drive command
    send_dive_zero = True
    
    # channel in use 
    channel = 8

    # Last time the client send a drive command
    last_drive_command = datetime.datetime.now()

    # Current servo position
    servo_position_turn = 210
    servo_position_tilt = 210

    # Is lamp on
    lamp_status=False

    # Last voltage read from rover
    rover_last_v = "?"




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

    # Is this the rover or the remote control
    is_rover = False

    # Is the 433Mhz link to rover enabled 
    is_link_enabled = False

    # When system start move servo here
    servo_position_turn_start = 120

    # Max Servo position
    servo_position_turn_max = 255

    # Min Servo position
    servo_position_turn_min = 0

    # When system start move servo here
    servo_position_tilt_start = 100

    # Max Servo position
    servo_position_tilt_max = 225

    # Min Servo position
    servo_position_tilt_min = 70

    # Motor max forward
    motor_forward_max = 1000

    # Motor max backward
    motor_backward_max = -1000
    
    
    

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
        # Rover stuff   
        if SETTINGS.is_rover:
            steelsquid_utils.shout("Steelsquid Range Rover enabled")
            # Set servos start position
            DYNAMIC.servo_position_turn = SETTINGS.servo_position_turn_start
            DYNAMIC.servo_position_tilt = SETTINGS.servo_position_tilt_start
            # Move the sevo to start position
            GLOBAL.turn(DYNAMIC.servo_position_turn)
            GLOBAL.tilt(DYNAMIC.servo_position_tilt)
            # Turn off lamp
            GLOBAL.lamp(False)   
        # Remote control stuff   
        else:
            steelsquid_utils.shout("Steelsquid Range Rover Controller enabled")
            # Listen for slow drive button click
            steelsquid_piio.xgpio_click(STATIC.slow_drive_button, PIIO.on_low_speed, pullup=True)
            # Light the link enabled LED
            steelsquid_piio.led(STATIC.link_toggle_led, SETTINGS.is_link_enabled)
            # Listen for toggle link button click
            steelsquid_piio.xgpio_click(STATIC.link_toggle_button, PIIO.on_link_toggle, pullup=True)
        # Is network enabled
        if steelsquid_nm.get_network_status():
            steelsquid_piio.led(STATIC.network_led, True)
        else:
            steelsquid_piio.led(STATIC.network_led, False)
        

    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        steelsquid_piio.xgpio_event_remove(STATIC.slow_drive_button)
       
       
        

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
        # Rover stuff 
        if SETTINGS.is_rover:
            # If more than 2 second since last drive command stop the drive (connection may be lost)
            drive_delta = datetime.datetime.now() - DYNAMIC.last_drive_command
            if drive_delta.total_seconds()>2:
                GLOBAL.motor(0, 0)
        # Remote control stuff   
        else:
            if SETTINGS.is_link_enabled:
                try:
                    # Send status command to rover
                    status = steelsquid_hmtrlrs.request("status")
                    # read the answer
                    DYNAMIC.lamp_status = steelsquid_utils.to_boolean(status[0])
                    DYNAMIC.rover_last_v = status[1]                
                    low_speed = steelsquid_utils.to_boolean(status[2])
                    # Light some LEDs
                    steelsquid_piio.led(STATIC.low_speed_led, low_speed)
                    steelsquid_piio.led(STATIC.link_led, True)
                    steelsquid_piio.led(STATIC.headlamp_led, DYNAMIC.lamp_status)
                    # Check if low battery on rover
                    v_int = float(DYNAMIC.rover_last_v)
                    if v_int < STATIC.voltage_warning:
                        steelsquid_piio.low_bat(True)
                    else:
                        steelsquid_piio.low_bat(False)
                except:
                    pass
        # Print IP/voltage to LCD
        if not DYNAMIC.stop_next_lcd_message:
            print_this = []
            if steelsquid_kiss_global.last_net:
                if steelsquid_kiss_global.last_wifi_name!="---":
                    print_this.append(steelsquid_kiss_global.last_wifi_name)
                    print_this.append(steelsquid_kiss_global.last_wifi_ip)
                if steelsquid_kiss_global.last_lan_ip!="---":
                    print_this.append(steelsquid_kiss_global.last_lan_ip)
            if SETTINGS.is_rover:
                if steelsquid_kiss_global.last_voltage != None:
                    print_this.append("ROVER:" + str(steelsquid_kiss_global.last_voltage)+"V")
            else:
                if steelsquid_kiss_global.last_voltage != None:
                    print_this.append("REMOTE:" + str(steelsquid_kiss_global.last_voltage)+"V")
                print_this.append("ROVER:" + DYNAMIC.rover_last_v+"V")
            if len(print_this)>0:
                new_lcd_message = "\n".join(print_this)
                if new_lcd_message!=DYNAMIC.last_lcd_message:
                    DYNAMIC.last_lcd_message = new_lcd_message
                    steelsquid_pi.ssd1306_write(new_lcd_message, 0)
        else:
            DYNAMIC.stop_next_lcd_message=False
        # Is network enabled
        if steelsquid_nm.get_network_status():
            steelsquid_piio.led(STATIC.network_led, True)
        else:
            steelsquid_piio.led(STATIC.network_led, False)
        # Is connection with remote transiever OK (If no OK command in 4 seconds connection lost)
        delta = datetime.datetime.now() - steelsquid_hmtrlrs.last_sync
        if delta.total_seconds()>4:
            steelsquid_piio.led(STATIC.link_led, False)
        return 2 # Execute this method again in 2 second




    @staticmethod
    def on_loop_fast():
        '''
        Execute every 0.05 second
        ''' 
        # Rover stuff   
        if SETTINGS.is_rover:
            pass
        # Remote control stuff   
        else:
            if SETTINGS.is_link_enabled:
                # Send tilt and drive command to the server
                try:
                    # Read the camera tilt joystick status
                    spin = int(round(steelsquid_piio.adc(STATIC.spin_pin, samples=3)* 10, 0))
                    tilt = int(round(steelsquid_piio.adc(STATIC.tilt_pin, samples=3)* 10, 0))
                    # If joystick is moved sent to rover
                    if spin!=17 or tilt!=17:
                        steelsquid_hmtrlrs.broadcast("tilt", [spin, tilt])
                    # Read the drive joystick status
                    drive = int(round(steelsquid_piio.adc(STATIC.drive_pin, samples=3)* 100, 0))
                    steer = int(round(steelsquid_piio.adc(STATIC.steer_pin, samples=3)* 100, 0))
                    # Do nothing on gitter data
                    if drive>158 and drive<172:
                        drive=165
                    if steer>158 and steer<172:
                        steer=165
                    # Disable or enable cruise control
                    if drive!=165:
                        DYNAMIC.cruise_control = False
                        steelsquid_piio.led(STATIC.cruise_control_led, DYNAMIC.cruise_control)
                    elif DYNAMIC.cruise_control:
                        drive=330
                    # Send drive command to rover
                    if drive!=165 or steer!=165:
                        steelsquid_hmtrlrs.broadcast("drive", [drive, steer])
                        DYNAMIC.send_dive_zero=True
                    # If the joystick is not move sent one stop drive command to rover
                    elif DYNAMIC.send_dive_zero:
                        steelsquid_hmtrlrs.broadcast("drive", [165, 165])
                        DYNAMIC.send_dive_zero=False
                except:
                    steelsquid_utils.shout()
        return 0.01 # Execute this method again in 0.01 second




class PIIO(object):
    '''
    THIS ONLY WORKS ON THE PIIO BOARD...
    Methods in this class will be executed by the system if module is enabled and this is a PIIO board
    Enebale this module like this: steelsquid piio-on
     on_voltage_change(voltage) Will fire when in voltage to the PIIO board i changed.
     on_low_bat(voltage) Will execute when voltage is to low.
     on_button(button_nr) Will execute when button 1 to 6 is clicken on the PIIO board
     on_button_info() Will execute when info button clicken on the PIIO board
     on_switch(dip_nr, status) Will execute when switch 1 to 6 is is changed on the PIIO board
     on_movement(x, y, z) will execute if Geeetech MPU-6050 is connected and the device is moved.
     on_rotation(x, y) will execute if Geeetech MPU-6050 is connected and the device is tilted.
    '''    
    
    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        # Network on/off
        if button_nr==STATIC.network_button:
            DYNAMIC.stop_next_lcd_message=True
            if steelsquid_nm.get_network_status():
                steelsquid_piio.ok_flash(None, 0.5)
                steelsquid_utils.shout("Disable the network\nPlease wait!")
                steelsquid_nm.set_network_status(False)
                steelsquid_piio.led(STATIC.network_led, False)
            else:
                steelsquid_piio.ok_flash(None, 0.5)
                steelsquid_utils.shout("Enable the network\nPlease wait!")
                steelsquid_nm.set_network_status(True)
                steelsquid_piio.led(STATIC.network_led, True)
        # Headlamp on/off
        elif button_nr==STATIC.headlamp_button:
            DYNAMIC.lamp_status = not DYNAMIC.lamp_status
            if SETTINGS.is_link_enabled:
                # Send commanf to rover
                try:
                    steelsquid_hmtrlrs.request("lamp", [DYNAMIC.lamp_status])
                    steelsquid_piio.led(STATIC.headlamp_led, DYNAMIC.lamp_status)
                except:
                    steelsquid_piio.error_flash()
                    steelsquid_utils.shout()
            else:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout("Enable linking!!!")
        # Horn sound i second
        elif button_nr==STATIC.horn_button:
            if SETTINGS.is_link_enabled:
                # Send command to rover
                try:
                    steelsquid_hmtrlrs.request("horn")
                    steelsquid_piio.ok_flash()
                except:
                    steelsquid_piio.error_flash()
                    steelsquid_utils.shout()
            else:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout("Enable linking!!!")
        # Center the camera
        elif button_nr==STATIC.center_button:
            if SETTINGS.is_link_enabled:
                # Send command to rover
                try:
                    steelsquid_hmtrlrs.broadcast("center")
                except:
                    steelsquid_piio.error_flash()
                    steelsquid_utils.shout()            
            else:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout("Enable linking!!!")
        # Change channel
        elif button_nr==STATIC.channel_button:
            # Send command to rover
            try:
                if DYNAMIC.channel<15:
                    DYNAMIC.channel = DYNAMIC.channel + 1
                else:
                    DYNAMIC.channel=0
                DYNAMIC.stop_next_lcd_message=True
                steelsquid_hmtrlrs.set_chanel(DYNAMIC.channel)
                steelsquid_utils.shout("CHANNEL: " + str(DYNAMIC.channel))
            except:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout()            
        # cruise control
        elif button_nr==STATIC.cruise_control_button:
            if SETTINGS.is_link_enabled:
                DYNAMIC.cruise_control = not DYNAMIC.cruise_control
                steelsquid_piio.led(STATIC.cruise_control_led, DYNAMIC.cruise_control)
            else:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout("Enable linking!!!")
            
            
    @staticmethod
    def on_low_speed(gpio):
        '''
        When press the low speed button
        '''
        if SETTINGS.is_link_enabled:
            # Toggle the low speed
            if SETTINGS.motor_forward_max==400:
                SETTINGS.motor_forward_max=1000
                SETTINGS.motor_backward_max=-1000
            else:
                SETTINGS.motor_forward_max=400
                SETTINGS.motor_backward_max=-400
            # Send command to rover
            try:
                steelsquid_hmtrlrs.request("low_speed", [SETTINGS.motor_forward_max==400])
                steelsquid_piio.led(STATIC.low_speed_led, SETTINGS.motor_forward_max==400)
            except:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout()            
        else:
                steelsquid_piio.error_flash()
                steelsquid_utils.shout("Enable linking!!!")


    @staticmethod
    def on_link_toggle(gpio):
        '''
        When the toggle link button is clicked
        '''
        SETTINGS.is_link_enabled = not SETTINGS.is_link_enabled
        # Light the link enabled LED
        steelsquid_piio.led(STATIC.link_toggle_led, SETTINGS.is_link_enabled)
        


        
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
    def status(parameters):
        '''
        A request from client to read status of the rover
        '''
        steelsquid_piio.led(STATIC.link_led, True)     
        return [DYNAMIC.lamp_status, steelsquid_kiss_global.last_voltage, SETTINGS.motor_forward_max==400]


    @staticmethod
    def lamp(parameters):
        '''
        A request from client to turn on/off the lamp
        '''
        GLOBAL.lamp(parameters[0])   
        return []


    @staticmethod
    def horn(parameters):
        '''
        A request from client to sound the horn for 1 second
        '''
        steelsquid_piio.power_flash(6)
        return []


    @staticmethod
    def center(parameters):
        '''
        A request from client to center the camera
        '''
        # Move the sevo to start position
        GLOBAL.turn(SETTINGS.servo_position_turn_start)
        GLOBAL.tilt(SETTINGS.servo_position_tilt_start)


    @staticmethod
    def tilt(parameters):
        '''
        A request from client to move camera
        '''
        turn = int(parameters[0])
        tilt = int(parameters[1])
        if turn<17:
            turn = (17-turn)
            GLOBAL.turn(DYNAMIC.servo_position_turn+(turn*2))
        elif turn>17:
            turn = (turn-17)
            GLOBAL.turn(DYNAMIC.servo_position_turn-(turn*2))
        if tilt<17:
            tilt = (17-tilt)
            GLOBAL.tilt(DYNAMIC.servo_position_tilt-(tilt*2))
        elif tilt>17:
            tilt = (tilt-17)
            GLOBAL.tilt(DYNAMIC.servo_position_tilt+(tilt*2))


    @staticmethod
    def drive(parameters):
        '''
        A request from client to move camera
        '''
        drive = int(parameters[0])
        steer = int(parameters[1])     
        drive = int(steelsquid_utils.remap(drive, 0, 330, SETTINGS.motor_backward_max, SETTINGS.motor_forward_max))
        steer = int(steelsquid_utils.remap(steer, 0, 330, SETTINGS.motor_backward_max, SETTINGS.motor_forward_max)/2)
        
        motor_left = drive
        motor_right = drive
        if steer>0:
            motor_right = motor_right - steer
            motor_left = motor_left + steer
        elif steer<0:
            motor_right = motor_right - steer
            motor_left = motor_left + steer
        
        if motor_right>SETTINGS.motor_forward_max:
            motor_right = SETTINGS.motor_forward_max
        elif motor_right<SETTINGS.motor_backward_max:
            motor_right = SETTINGS.motor_backward_max
        
        if motor_left>SETTINGS.motor_forward_max:
            motor_left = SETTINGS.motor_forward_max
        elif motor_left<SETTINGS.motor_backward_max:
            motor_left = SETTINGS.motor_backward_max
        
        GLOBAL.motor(motor_left, motor_right)


    @staticmethod
    def low_speed(parameters):
        '''
        A request to enable/disable low speed
        '''
        low = steelsquid_utils.to_boolean(parameters[0])
        if low:
            SETTINGS.motor_forward_max = 400
            SETTINGS.motor_backward_max = -400
            steelsquid_piio.led(STATIC.low_speed_led, True)
        else:
            SETTINGS.motor_forward_max = 1000
            SETTINGS.motor_backward_max = -1000
            steelsquid_piio.led(STATIC.low_speed_led, False)
        return []




class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''
    
    @staticmethod
    def turn(turn):
        '''
        Set servo to position
        '''
        if turn<SETTINGS.servo_position_turn_min:
            DYNAMIC.servo_position_turn = SETTINGS.servo_position_turn_min
        elif turn>SETTINGS.servo_position_turn_max:
            DYNAMIC.servo_position_turn = SETTINGS.servo_position_turn_max
        else:
            DYNAMIC.servo_position_turn = turn
        steelsquid_piio.servo(1, DYNAMIC.servo_position_turn)


    @staticmethod
    def tilt(tilt):
        '''
        Set servo to position
        '''
        if tilt<SETTINGS.servo_position_tilt_min:
            DYNAMIC.servo_position_tilt = SETTINGS.servo_position_tilt_min
        elif tilt>SETTINGS.servo_position_tilt_max:
            DYNAMIC.servo_position_tilt = SETTINGS.servo_position_tilt_max
        else:
            DYNAMIC.servo_position_tilt = tilt
        steelsquid_piio.servo(2, DYNAMIC.servo_position_tilt)
        
    
    @staticmethod
    def motor(left, right):
        '''
        Set speed of motors
        '''
        DYNAMIC.last_drive_command = datetime.datetime.now()
        steelsquid_pi.diablo_motor_1(left);
        steelsquid_pi.diablo_motor_2(right);


    @staticmethod
    def lamp(status):
        '''
        Toggle the headlamp
        '''
        status = steelsquid_utils.to_boolean(status)
        DYNAMIC.lamp_status=status
        steelsquid_piio.power(1, status)
        steelsquid_piio.power(2, status) 
        steelsquid_piio.power(3, status) 
        steelsquid_piio.power(4, status) 
        steelsquid_piio.power(5, status) 
