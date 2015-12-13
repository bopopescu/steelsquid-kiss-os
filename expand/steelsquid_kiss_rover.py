#!/usr/bin/python -OO


'''.
Fuctionality for my rover controller
Also see utils.html

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-12-26 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import steelsquid_piio
import steelsquid_kiss_global


# Is this enabled (on_enable has executed)
# This is set by the system automaticaly
is_enabled = False


def activate():
    '''
    Return True/False if this functionality is to be enabled (execute on_enable)
    return: True/False
    '''    
    return steelsquid_utils.get_flag("rover")


class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if activate() return True
    '''

    @staticmethod
    def on_enable():
        '''
        This will execute when system starts
        Do not execute long running stuff here, do it in on_loop...
        '''
        steelsquid_utils.shout("Steelsquid Rover enabled")
        steelsquid_piio.servo_position = steelsquid_utils.get_parameter("servo_position", steelsquid_piio.servo_position)
        steelsquid_piio.servo_position_max = steelsquid_utils.get_parameter("servo_position_max", steelsquid_piio.servo_position_max)
        steelsquid_piio.servo_position_min = steelsquid_utils.get_parameter("servo_position_min", steelsquid_piio.servo_position_min)
        steelsquid_piio.motor_forward = steelsquid_utils.get_parameter("motor_forward", steelsquid_piio.motor_forward)
        steelsquid_piio.motor_backward = steelsquid_utils.get_parameter("motor_backward", steelsquid_piio.motor_backward)
        steelsquid_piio.servo(1, steelsquid_piio.servo_position)       
        

    @staticmethod
    def on_disable():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        pass
        
        
    @staticmethod
    def on_loop():
        '''
        This will execute over and over again untill it return None or -1
        If it return a number larger than 0 it will sleep for that number of seconds before execute again.
        If it return 0 it will not not sleep, will execute again imediately.
        '''    
        now = time.time()*1000
        if now - steelsquid_piio.trex_motor_last_change() > 1000:
            try:
                steelsquid_piio.trex_motor(0,0)
            except:
                pass
        return 1


    @staticmethod
    def on_network(status, wired, wifi_ssid, wifi, wan):
        '''
        Execute on network up or down.
        status = True/False (up or down)
        wired = Wired ip number
        wifi_ssid = Cnnected to this wifi
        wifi = Wifi ip number
        wan = Ip on the internet
        '''    
        pass
        
        
    @staticmethod
    def on_bluetooth(status):
        '''
        Execute when bluetooth is enabled
        status = True/False
        '''    
        pass
        
        
    @staticmethod
    def on_event_data(key, value):
        '''
        This will fire when data is changed with steelsquid_kiss_global.set_event_data(key, value)
        key=The key of the data
        value=The value of the data
        '''    
        pass


class WEB(object):
    '''
    Methods in this class will be executed by the webserver if activate() return True and the webserver is enabled
    If is a GET it will return files and if it is a POST it executed commands.
    It is meant to be used as follows.
    1. Make a call from the browser (GET) and a html page is returned back.
    2. This html page then make AJAX (POST) call to the server to retrieve or update data.
    3. The data sent to and from the server can just be a simple list of strings.
    See steelsquid_http_server.py for more examples how it work
    '''

    @staticmethod
    def rover_info(session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.info()


    @staticmethod
    def rover_enable(session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'rover-on']) 
        return steelsquid_utils.get_flag("rover")


    @staticmethod
    def rover_disable(session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'rover-off']) 
        return steelsquid_utils.get_flag("rover")

    @staticmethod
    def rover_light(session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.light()


    @staticmethod
    def rover_alarm(session_id, parameters):
        '''
        
        '''
        return steelsquid_kiss_global.Rover.alarm()


    @staticmethod
    def rover_tilt(session_id, parameters):
        '''
        
        '''
        import steelsquid_io
        if parameters[0]=="True":
            steelsquid_kiss_global.Rover.tilt(True)
        else:
            steelsquid_kiss_global.Rover.tilt(False)
            

    @staticmethod
    def rover_stop(session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(0, 0)


    @staticmethod
    def rover_left(session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(-40, 40)


    @staticmethod
    def rover_right(session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(40, -40)


    @staticmethod
    def rover_forward(session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(40, 40)


    @staticmethod
    def rover_backward(session_id, parameters):
        '''
        
        '''
        steelsquid_kiss_global.Rover.drive(-40, -40)


class SOCKET(object):
    '''
    Methods in this class will be executed by the socket connection if activate() return True and the socket connection is enabled
    A simple class that i use to sen async socket command to and from client/server.
    A request can be made from server to client or from client to server
    See steelsquid_connection.py and steelsquid_socket_connection.py
    '''
    
    #Is this connection a server
    #This is set by the system
    is_server=False

    @staticmethod
    def on_connect(remote_address):
        '''
        When a connection is enabled
        @param remote_address: IP number to the host
        '''
        pass


    @staticmethod
    def on_disconnect(error_message):
        '''
        When a connection is closed
        Will also execute on connection lost or no connection
        @param error_message: I a error (Can be None)
        '''
        steelsquid_pi_board.sabertooth_set_speed(0, 0) 
    
    
    @staticmethod
    def rover_info_request(remote_address, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.info()
        

    @staticmethod
    def rover_info_response(remote_address, parameters):
        '''
        '''
        pass
        

    @staticmethod
    def rover_info_error(remote_address, parameters):
        '''
        '''
        pass


    @staticmethod
    def rover_light_request(remote_address, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.light()
        

    @staticmethod
    def rover_light_response(remote_address, parameters):
        '''
        '''
        pass
        

    @staticmethod
    def rover_light_error(remote_address, parameters):
        '''
        '''
        pass


    @staticmethod
    def rover_alarm_request(remote_address, parameters):
        '''
        '''
        return steelsquid_kiss_global.Rover.alarm()
        

    @staticmethod
    def rover_alarm_response(remote_address, parameters):
        '''
        '''
        pass
        

    @staticmethod
    def rover_alarm_error(remote_address, parameters):
        '''
        '''
        pass


    @staticmethod
    def rover_tilt_request(remote_address, parameters):
        '''
        '''
        steelsquid_kiss_global.Rover.tilt(parameters[0])
        

    @staticmethod
    def rover_tilt_response(remote_address, parameters):
        '''
        '''
        pass
        

    @staticmethod
    def rover_tilt_error(remote_address, parameters):
        '''
        '''
        pass


    @staticmethod
    def rover_drive_request(remote_address, parameters):
        '''
        '''
        steelsquid_kiss_global.Rover.drive(parameters[0], parameters[1])
        

    @staticmethod
    def rover_drive_response(remote_address, parameters):
        '''
        '''
        pass
        

    @staticmethod
    def rover_drive_error( remote_address, parameters):
        '''
        '''
        pass
    
        
class PIIO(object):
    '''
    Methods in this class will be executed by the system if activate() return True and this is a PIIO board
    '''

    @staticmethod
    def on_low_bat(voltage):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when voltage is to low.
        Is set with the paramater: voltage_waring
        voltage = Current voltage
        '''    
        pass


    @staticmethod
    def on_button_info():
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when info button clicken on the PIIO board
        '''    
        pass
        

    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        pass


    @staticmethod
    def on_switch(dip_nr, status):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when switch 1 to 6 is is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        pass

        
class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''

    @staticmethod
    def info():
        '''
        Get info on rover functionality
        '''
        enabled = steelsquid_utils.get_flag("rover")
        if enabled:
            import steelsquid_piio
            battery_voltage, _, _, _, _, _, _, _, _ = steelsquid_piio.trex_status()
            battery_voltage = float(battery_voltage)/100
            return [True, battery_voltage, steelsquid_piio.gpio_22_xv_toggle_current(2), steelsquid_piio.gpio_22_xv_toggle_current(1), steelsquid_piio.servo_position, steelsquid_piio.servo_position_min, steelsquid_piio.servo_position_max, steelsquid_piio.motor_backward, steelsquid_piio.motor_forward]
        else:
            return False


    @staticmethod
    def light():
        '''
        Light on and off (toggle)
        '''
        status = steelsquid_piio.gpio_22_xv_toggle(2)
        steelsquid_piio.gpio_22_xv(3, status)
        return status


    @staticmethod
    def alarm():
        '''
        Alarm on and off (toggle)
        '''
        return steelsquid_piio.gpio_22_xv_toggle(1)


    @staticmethod
    def tilt(value):
        '''
        Tilt the camera
        '''
        import steelsquid_piio
        if value == True:
            steelsquid_piio.servo_move(1, 10)
        elif value == False:
            steelsquid_piio.servo_move(1, -10)
        else:
            value = int(value)
            steelsquid_piio.servo(1, value)


    @staticmethod
    def drive(left, right):
        '''
        Tilt the camera
        '''
        left = int(left)
        right = int(right)
        steelsquid_piio.trex_motor(left, right)

    
    
    
