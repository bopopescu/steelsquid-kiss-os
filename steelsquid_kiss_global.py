#!/usr/bin/python -OO


'''
Global stuff for steelsquid kiss os
Reach the http server and Socket connection.
I also add some extra stuff here like Rover and IO

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import time


# The socket connection, if enabled (not enabled = None)
# Flag: socket_connection
socket_connection = None


# The http webserver, if enabled (not enabled = None)
# Flag: web
http_server = None


class Rover(object):
    '''
    Fuctionality for my rover controller
    Also see utils.html, steelsquid_kiss_http_server.py, steelsquid_kiss_socket_connection.py
    '''

    # Is the rover functionality enabled
    is_enabled = False
    
    @classmethod
    def enable(cls):
        '''
        Enable the rover functionality (this is set by steelsquid_boot)
        Flag: rover
        '''    
        import steelsquid_io
        steelsquid_utils.shout("Steelsquid Rover enabled")
        steelsquid_io.servo_position = steelsquid_utils.get_parameter("servo_position", steelsquid_io.servo_position)
        steelsquid_io.servo_position_max = steelsquid_utils.get_parameter("servo_position_max", steelsquid_io.servo_position_max)
        steelsquid_io.servo_position_min = steelsquid_utils.get_parameter("servo_position_min", steelsquid_io.servo_position_min)
        steelsquid_io.motor_forward = steelsquid_utils.get_parameter("motor_forward", steelsquid_io.motor_forward)
        steelsquid_io.motor_backward = steelsquid_utils.get_parameter("motor_backward", steelsquid_io.motor_backward)
        steelsquid_io.servo(1, steelsquid_io.servo_position)       
        steelsquid_event.subscribe_to_event("second", cls.on_second, ())         
        cls.is_enabled=True

    @classmethod
    def on_second(cls, args, para):
        '''
        If no signal after 1 second stop the rover. (connection lost!!!)
        '''
        import steelsquid_io
        now = time.time()*1000
        if now - steelsquid_io.trex_motor_last_change() > 1000:
            try:
                steelsquid_io.trex_motor(0,0)
            except:
                pass
                
    @classmethod
    def info(cls):
        '''
        Get info on rover functionality
        '''
        enabled = steelsquid_utils.get_flag("rover")
        if enabled:
            import steelsquid_io
            battery_voltage, _, _, _, _, _, _, _, _ = steelsquid_io.trex_status()
            battery_voltage = float(battery_voltage)/100
            return [True, battery_voltage, steelsquid_io.gpio_22_xv_toggle_current(2), steelsquid_io.gpio_22_xv_toggle_current(1), steelsquid_io.servo_position, steelsquid_io.servo_position_min, steelsquid_io.servo_position_max, steelsquid_io.motor_backward, steelsquid_io.motor_forward]
        else:
            return False


    @classmethod
    def light(cls):
        '''
        Light on and off (toggle)
        '''
        import steelsquid_io
        status = steelsquid_io.gpio_22_xv_toggle(2)
        steelsquid_io.gpio_22_xv(3, status)
        return status


    @classmethod
    def alarm(cls):
        '''
        Alarm on and off (toggle)
        '''
        import steelsquid_io
        return steelsquid_io.gpio_22_xv_toggle(1)


    @classmethod
    def tilt(cls, value):
        '''
        Tilt the camera
        '''
        import steelsquid_io
        if value == True:
            steelsquid_io.servo_move(1, 10)
        elif value == False:
            steelsquid_io.servo_move(1, -10)
        else:
            value = int(value)
            steelsquid_io.servo(1, value)


    @classmethod
    def drive(cls, left, right):
        '''
        Tilt the camera
        '''
        import steelsquid_io
        left = int(left)
        right = int(right)
        steelsquid_io.trex_motor(left, right)


class IO(object):
    '''
    Fuctionality for my Steelsquid IO board
    Also see steelquid_io.py
    '''

    # Is the IO board functionality enabled
    is_enabled = False
    
    # Last voltage read
    last_voltage = 0
    
    # Last voltage read
    last_print_voltage = 0

    @classmethod
    def enable(cls):
        '''
        Enable the IO board functionality (this is done by steelsquid_boot)
        Flag: io
        '''    
        import steelsquid_io
        steelsquid_utils.shout("Steelsquid IO board enabled")
        steelsquid_io.button(1, cls.on_button_1)
        steelsquid_io.button(2, cls.on_button_2)
        steelsquid_io.button(3, cls.on_button_3)
        steelsquid_io.button(4, cls.on_button_4)
        steelsquid_io.button(5, cls.on_button_5)
        steelsquid_io.button(6, cls.on_button_6)
        steelsquid_io.dip(1, cls.on_dip_1)
        steelsquid_io.dip(2, cls.on_dip_2)
        steelsquid_io.dip(3, cls.on_dip_3)
        steelsquid_io.dip(4, cls.on_dip_4)
        steelsquid_io.dip(5, cls.on_dip_5)
        steelsquid_io.dip(6, cls.on_dip_6)
        steelsquid_io.button_info(cls.on_button_info)
        steelsquid_io.button_power_off(cls.on_button_power_off)
        if steelsquid_utils.get_flag("development"):
            steelsquid_event.subscribe_to_event("button", cls.dev_button, ())
            steelsquid_event.subscribe_to_event("dip", cls.dev_dip, ())
        if not steelsquid_utils.get_flag("no_lcd_voltage"):
            steelsquid_event.subscribe_to_event("seconds", cls.on_read_voltage, ())
        steelsquid_event.subscribe_to_event("poweroff", cls.on_poweroff, ())
        cls.is_enabled=True


    @classmethod
    def on_poweroff(cls, args, para):
        '''
        Power off the system
        '''
        import steelsquid_io
        steelsquid_io.power_off()

    @classmethod
    def on_read_voltage(cls, args, para):
        '''
        Read voltage and display on LCD
        '''
        import steelsquid_io
        import datetime
        new_voltage = steelsquid_io.voltage()
        if new_voltage != cls.last_voltage:
            if abs(new_voltage - cls.last_print_voltage)>=0.1:
                if cls.last_print_voltage == 0:
                    steelsquid_utils.shout("Voltage is: " + str(new_voltage), to_lcd=False)
                else:
                    steelsquid_utils.shout("Voltage changed: " + str(new_voltage), to_lcd=False)
                cls.last_print_voltage = new_voltage
            cls.last_voltage = new_voltage
            last = steelsquid_pi.lcd_last_text
            if last != None and "VOLTAGE: " in last:
                i1 = last.find("VOLTAGE: ", 0) + 9
                if i1 != -1:
                    i2 = last.find("\n", i1)
                    if i2 == -1:
                        news = last[:i1]+str(new_voltage)
                    else:
                        news = last[:i1]+str(new_voltage)+last[i2:]
                    steelsquid_io.lcd_write(news, number_of_seconds = 0)
                
                    
    @classmethod
    def dev_button(cls, args, para):
        '''
        In development mode shout if the button is pressed
        '''    
        import steelsquid_io
        bu = str(para[0])
        steelsquid_utils.shout_time("Button " + bu + " pressed!")

    @classmethod
    def dev_dip(cls, args, para):
        '''
        In development mode shout if the DIP is changed
        '''    
        import steelsquid_io
        steelsquid_utils.shout_time("DIP " + str(para[0]) +": "+ str(para[1]))

    @classmethod
    def on_button_power_off(cls, address, pin):
        '''
        If shutdown button is clicked
        '''    
        import steelsquid_io
        steelsquid_io.power_off()

    @classmethod
    def on_button_info(cls, address, pin):
        '''
        If info button is clicked
        '''    
        import steelsquid_io
        steelsquid_io.led_ok_flash(None)
        steelsquid_event.broadcast_event("network")

    @classmethod
    def on_button_1(cls, address, pin):
        '''
        If the 1 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [1])

    @classmethod
    def on_button_2(cls, address, pin):
        '''
        If the 2 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [2])

    @classmethod
    def on_button_3(cls, address, pin):
        '''
        If the 3 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [3])

    @classmethod
    def on_button_4(cls, address, pin):
        '''
        If the 4 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [4])

    @classmethod
    def on_button_5(cls, address, pin):
        '''
        If the 5 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [5])

    @classmethod
    def on_button_6(cls, address, pin):
        '''
        If the 6 button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [6])

    @classmethod
    def on_dip_1(cls, address, pin, status):
        '''
        If DIP 1 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [1, status])

    @classmethod
    def on_dip_2(cls, address, pin, status):
        '''
        If DIP 2 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [2, status])

    @classmethod
    def on_dip_3(cls, address, pin, status):
        '''
        If DIP 3 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [3, status])

    @classmethod
    def on_dip_4(cls, address, pin, status):
        '''
        If DIP 4 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [4, status])

    @classmethod
    def on_dip_5(cls, address, pin, status):
        '''
        If DIP 5 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [5, status])

    @classmethod
    def on_dip_6(cls, address, pin, status):
        '''
        If DIP 6 changed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("dip", [6, status])

