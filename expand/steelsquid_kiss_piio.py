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
import steelsquid_event
import steelsquid_pi
import steelsquid_piio
import steelsquid_kiss_global
import steelsquid_boot
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
last_voltage = 0

# Last voltage read
last_print_voltage = 0


def enable():
    '''
    When this module is enabled what needs to be done (execute: steelsquid module XXX on)
    Maybe you need create some files or enable other stuff.
    '''
    steelsquid_utils.set_flag("auto")
    steelsquid_utils.del_flag("nokia")
    steelsquid_utils.del_flag("hdd")
    steelsquid_utils.del_flag("ssd")


def disable():
    '''
    When this module is disabled what needs to be done (execute: steelsquid module XXX off)
    Maybe you need remove some files or disable other stuff.
    '''
    pass


class SYSTEM(object):
    '''
    Methods in this class will be executed by the system if module is activated
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
        # Listen for clicka on buttons
        steelsquid_piio.button_click(1, SYSTEM.on_button)
        steelsquid_piio.button_click(2, SYSTEM.on_button)
        steelsquid_piio.button_click(3, SYSTEM.on_button)
        steelsquid_piio.button_click(4, SYSTEM.on_button)
        steelsquid_piio.button_click(5, SYSTEM.on_button)
        steelsquid_piio.button_click(6, SYSTEM.on_button)
        # Listen for event on switch
        steelsquid_piio.switch_event(1, SYSTEM.on_switch)
        steelsquid_piio.switch_event(2, SYSTEM.on_switch)
        steelsquid_piio.switch_event(3, SYSTEM.on_switch)
        steelsquid_piio.switch_event(4, SYSTEM.on_switch)
        steelsquid_piio.switch_event(5, SYSTEM.on_switch)
        steelsquid_piio.switch_event(6, SYSTEM.on_switch)
        

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
    def on_loop():
        '''
        This will execute over and over again untill it return None or -1
        If it return a number larger than 0 it will sleep for that number of seconds before execute again.
        If it return 0 it will not not sleep, will execute again imediately.
        '''    
        global last_voltage
        global last_print_voltage
        new_voltage = steelsquid_piio.volt(2, 4)
        voltage_waring = int(steelsquid_utils.get_parameter("voltage_waring", "10"))
        voltage_poweroff = int(steelsquid_utils.get_parameter("voltage_poweroff", "8"))
        v_warn=""
        if new_voltage<voltage_waring:
            v_warn=" (Warning)"
            steelsquid_piio.low_bat(True)
            steelsquid_kiss_global._execute_all_expand_modules("PIIO", "on_low_bat", (new_voltage,))
        else:
            steelsquid_piio.low_bat(False)
        if new_voltage<voltage_poweroff:
            steelsquid_piio.shutdown()
            
        if not steelsquid_utils.get_flag("no_lcd_voltage"):
            if new_voltage != last_voltage:
                if abs(new_voltage - last_print_voltage)>=0.1:
                    if last_print_voltage == 0:
                        steelsquid_utils.shout("Voltage is: " + str(new_voltage), to_lcd=False)
                    last_print_voltage = new_voltage
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
    def on_event_data(key, value):
        '''
        This will fire when data is changed with steelsquid_kiss_global.set_event_data(key, value)
        key=The key of the data
        value=The value of the data
        '''    
        pass


    @staticmethod
    def on_button_info():
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when info button clicken on the PIIO board
        '''    
        steelsquid_piio.buz_flash(None, 0.1)
        steelsquid_event.broadcast_event("network")
        steelsquid_kiss_global._execute_all_expand_modules("PIIO", "on_button_info")
        

    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        steelsquid_kiss_global._execute_all_expand_modules("PIIO", "on_button", (button_nr,))


    @staticmethod
    def on_switch(dip_nr, status):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when switch 1 to 6 is is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        steelsquid_kiss_global._execute_all_expand_modules("PIIO", "on_switch", (dip_nr, status,))


    @staticmethod
    def on_button_poweroff():
        '''
        Power off the system
        '''
        steelsquid_piio.shutdown()    
            
    
class GLOBAL(object):
    '''
    Put global staticmethods in this class, methods you use from different part of the system.
    Maybe the same methods is used from the WEB, SOCKET or other part, then put that method her.
    It is not necessary to put it her, you can also put it direcly in the module (but i think it is kind of nice to have it inside this class)
    '''
    
    
