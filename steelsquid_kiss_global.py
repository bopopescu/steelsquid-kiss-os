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
    Also see steelquid_io.py
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
    Also see utils.html, steelsquid_kiss_http_server.py, steelsquid_socket_connection.py
    '''

    # Is the IO board functionality enabled
    is_enabled = False

    @classmethod
    def enable(cls):
        '''
        Enable the IO board functionality (this is done by steelsquid_boot)
        Flag: io
        '''    
        import steelsquid_io
        steelsquid_utils.shout("Steelsquid IO board enabled")
        steelsquid_io.button_click(steelsquid_io.BUTTON_UP, cls.on_button_up)
        steelsquid_io.button_click(steelsquid_io.BUTTON_DOWN, cls.on_button_down)
        steelsquid_io.button_click(steelsquid_io.BUTTON_LEFT, cls.on_button_left)
        steelsquid_io.button_click(steelsquid_io.BUTTON_RIGHT, cls.on_button_right)
        steelsquid_io.button_click(steelsquid_io.BUTTON_SELECT, cls.on_button_select)
        steelsquid_io.dip_event(1, cls.on_dip_1)
        steelsquid_io.dip_event(2, cls.on_dip_2)
        steelsquid_io.dip_event(3, cls.on_dip_3)
        steelsquid_io.dip_event(4, cls.on_dip_4)
        if steelsquid_utils.get_flag("development"):
            steelsquid_event.subscribe_to_event("button", cls.dev_button, ())
            steelsquid_event.subscribe_to_event("dip", cls.dev_dip, ())
        cls.is_enabled=True

    @classmethod
    def on_button_up(cls, address, pin):
        '''
        If the UP button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [steelsquid_io.BUTTON_UP])

    @classmethod
    def on_button_down(cls, address, pin):
        '''
        If the DOWN button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [steelsquid_io.BUTTON_DOWN])

    @classmethod
    def on_button_left(cls, address, pin):
        '''
        If the LEFT button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [steelsquid_io.BUTTON_LEFT])

    @classmethod
    def on_button_right(cls, address, pin):
        '''
        If the RIGHT button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [steelsquid_io.BUTTON_RIGHT])

    @classmethod
    def on_button_select(cls, address, pin):
        '''
        If the SELECT button is pressed
        '''    
        import steelsquid_io
        steelsquid_event.broadcast_event("button", [steelsquid_io.BUTTON_SELECT])

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
    def dev_button(cls, args, para):
        '''
        In development mode shout if the button is pressed
        '''    
        import steelsquid_io
        bu = int(para[0])
        if bu == steelsquid_io.BUTTON_UP:
            steelsquid_utils.shout_time("Button UP pressed!")
        elif bu == steelsquid_io.BUTTON_DOWN:
            steelsquid_utils.shout_time("Button DOWN pressed!")
        elif bu == steelsquid_io.BUTTON_LEFT:
            steelsquid_utils.shout_time("Button LEFT pressed!")
        elif bu == steelsquid_io.BUTTON_RIGHT:
            steelsquid_utils.shout_time("Button RIGHT pressed!")
        elif bu == steelsquid_io.BUTTON_SELECT:
            steelsquid_utils.shout_time("Button SELECT pressed!")

    @classmethod
    def dev_dip(cls, args, para):
        '''
        In development mode shout if the DIP is changed
        '''    
        import steelsquid_io
        steelsquid_utils.shout_time("DIP " + str(para[0]) +": "+ str(para[1]))
        
