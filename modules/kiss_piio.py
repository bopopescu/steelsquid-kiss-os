#!/usr/bin/python -OO


'''.
Fuctionality for my PIIO board
steelsquid_PIIO.py

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
import steelsquid_kiss_boot
import time
from datetime import datetime
from datetime import timedelta
import os
import urllib
import threading
import thread
import sys


# Is this module started
# This is set by the system automatically.
is_started = False

# Last voltage read
last_print_voltage = 0


def enable(argument=None):
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    Maybe you need create some files or enable other stuff.
    '''
    steelsquid_utils.set_flag("auto")
    steelsquid_utils.del_flag("nokia")
    steelsquid_utils.del_flag("hdd")
    steelsquid_utils.del_flag("ssd")


def disable(argument=None):
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    '''
    pass


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
        steelsquid_utils.shout("Steelsquid PIIO board enabled")
        # Reset all LED
        steelsquid_piio.led(1, False)
        steelsquid_piio.led(2, False)
        steelsquid_piio.led(3, False)
        steelsquid_piio.led(4, False)
        steelsquid_piio.led(5, False)
        steelsquid_piio.led(6, False)
        steelsquid_piio.buz(False)    
        steelsquid_piio.error(False)    
        steelsquid_piio.ok(False)    
        steelsquid_piio.bt(False)    
        # Listen for clicka on power off button
        steelsquid_piio.power_off_click(SYSTEM.on_button_poweroff)
        # Listen for clicka on info button
        steelsquid_piio.info_click(SYSTEM.on_button_info)
        
        # Listen for clicka on buttons if there is some modules that listen
        if steelsquid_kiss_global._has_modules_method("PIIO", "on_button"):
            steelsquid_piio.button_click(1, SYSTEM.on_button)
            steelsquid_piio.button_click(2, SYSTEM.on_button)
            steelsquid_piio.button_click(3, SYSTEM.on_button)
            steelsquid_piio.button_click(4, SYSTEM.on_button)
            steelsquid_piio.button_click(5, SYSTEM.on_button)
            steelsquid_piio.button_click(6, SYSTEM.on_button)
        # Listen for event on switch if there is some modules that listen
        if steelsquid_kiss_global._has_modules_method("PIIO", "on_switch"):
            steelsquid_piio.switch_event(1, SYSTEM.on_switch)
            steelsquid_piio.switch_event(2, SYSTEM.on_switch)
            steelsquid_piio.switch_event(3, SYSTEM.on_switch)
            steelsquid_piio.switch_event(4, SYSTEM.on_switch)
            steelsquid_piio.switch_event(5, SYSTEM.on_switch)
            steelsquid_piio.switch_event(6, SYSTEM.on_switch)
        # Listen for movement if there is some modules that listen
        if steelsquid_kiss_global._has_modules_method("PIIO", "on_movement"):
            steelsquid_piio.movement_event(SYSTEM.on_movement)
        # Listen for rotation if there is some modules that listen
        if steelsquid_kiss_global._has_modules_method("PIIO", "on_rotation"):
            steelsquid_piio.rotation_event(SYSTEM.on_rotation)
        # Load voltage varning and power off
        LOOP.voltage_waring = float(steelsquid_utils.get_parameter("voltage_warning", "-1"))
        LOOP.voltage_poweroff = float(steelsquid_utils.get_parameter("voltage_poweroff", "-1"))
        
        

    @staticmethod
    def on_stop():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
        # Reset all LED
        steelsquid_piio.buz_flash(None, 0.1)
        steelsquid_piio.low_bat(False)
        steelsquid_piio.bt(False)
        steelsquid_piio.net(False)
        steelsquid_piio.led(1, False)
        steelsquid_piio.led(2, False)
        steelsquid_piio.led(3, False)
        steelsquid_piio.led(4, False)
        steelsquid_piio.led(5, False)
        steelsquid_piio.led(6, False)
        # Clean all event listening
        steelsquid_pi.cleanup()
        

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
        if status:            
            steelsquid_piio.net(True)
        else:
            steelsquid_piio.net(False)
        
        
    @staticmethod
    def on_bluetooth(status):
        '''
        Execute when bluetooth is enabled
        status = True/False
        '''    
        if status:
            steelsquid_piio.bt(True)        
        else:
            steelsquid_piio.bt(False)        
        

    @staticmethod
    def on_button_info():
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when info button clicken on the PIIO board
        '''    
        steelsquid_piio.buz_flash(None, 0.1)
        steelsquid_kiss_boot.execute_task_event("network")
        steelsquid_kiss_global._execute_all_modules("PIIO", "on_button_info")
        

    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        steelsquid_kiss_global._execute_all_modules("PIIO", "on_button", (button_nr,)) 


    @staticmethod
    def on_switch(dip_nr, status):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when switch 1 to 6 is is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        steelsquid_kiss_global._execute_all_modules("PIIO", "on_switch", (dip_nr, status,))


    @staticmethod
    def on_button_poweroff():
        '''
        Power off the system
        '''
        steelsquid_piio.shutdown()    


    @staticmethod
    def on_movement(x, y, z):
        '''
        Movement
        '''    
        steelsquid_kiss_global._execute_all_modules("PIIO", "on_movement", (x, y, z,))


    @staticmethod
    def on_rotation(x, y):
        '''
        Rotaton
        '''    
        steelsquid_kiss_global._execute_all_modules("PIIO", "on_rotation", (x, y,))
    

class LOOP(object):
    '''
    Every static method with no inparameters will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again immediately.
    Every method will execute in its own thread
    '''

    voltage_waring = -1
    voltage_poweroff = -1
    voltage_poweroff_count = 0

    
    @staticmethod
    def on_loop():
        '''
        Check voltage level
        '''    
        global last_print_voltage
        new_voltage = steelsquid_piio.volt(2, 4)
        steelsquid_kiss_global.last_voltage=new_voltage
        v_warn=""
        if new_voltage<LOOP.voltage_waring:
            v_warn=" (Warning)"
            steelsquid_piio.low_bat(True)
            steelsquid_kiss_global._execute_all_modules("PIIO", "on_low_bat", (new_voltage,))
        else:
            steelsquid_piio.low_bat(False)
        if new_voltage<LOOP.voltage_poweroff:
            if LOOP.voltage_poweroff_count>=3:
                LOOP.voltage_poweroff_count=0
                steelsquid_piio.shutdown()
            else:
                LOOP.voltage_poweroff_count=LOOP.voltage_poweroff_count+1
        else:
            LOOP.voltage_poweroff_count=0
            
        if new_voltage != steelsquid_piio.last_voltage:
            steelsquid_piio.last_voltage = new_voltage
            if abs(new_voltage - last_print_voltage)>=0.1:
                if last_print_voltage == 0:
                    steelsquid_utils.shout("Voltage is: " + str(new_voltage), to_lcd=False)
                last_print_voltage = new_voltage
                steelsquid_kiss_global._execute_all_modules("PIIO", "on_voltage_change", (new_voltage,))
                if not steelsquid_utils.get_flag("no_lcd_voltage") and not steelsquid_utils.get_flag("no_net_to_lcd"):
                    last = steelsquid_pi.lcd_last_text
                    if last != None and "VOLTAGE: " in last:
                        i1 = last.find("VOLTAGE: ", 0) + 9
                        if i1 != -1:
                            i2 = last.find("\n", i1)
                            if i2 == -1:
                                news = last[:i1]+str(new_voltage)+v_warn
                            else:
                                news = last[:i1]+str(new_voltage)+v_warn+last[i2:]
                            steelsquid_piio.lcd(news, number_of_seconds = 0)
        return 1
    
    
