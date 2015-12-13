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
import steelsquid_kiss_expand
import time
from datetime import datetime
from datetime import timedelta
import os
import urllib
import threading
import thread
import sys


# Is this enabled (on_enable has executed)
# This is set by the system automaticaly
is_enabled = False

# Last voltage read
last_voltage = 0

# Last voltage read
last_print_voltage = 0

# Expand has on_button_info method
expand_on_button_info = False
# Expand has on_button method
expand_on_button = False
# Expand has on_switch method
expand_on_switch = False

# Custom has on_button_info method
steel_expand_on_button_info = False
# Custom has on_button method
steel_expand_on_button = False
# Custom has on_switch method
steel_expand_on_switch = False


def activate():
    '''
    Return True/False if this functionality is to be enabled (execute on_enable)
    return: True/False
    '''    
    return steelsquid_utils.get_flag("piio")


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
        global last_voltage
        global last_print_voltage
        global expand_on_button_info
        global expand_on_button
        global expand_on_switch
        global steel_expand_on_button_info
        global steel_expand_on_button
        global steel_expand_on_switch
        steelsquid_utils.shout("Steelsquid PIIO board enabled")
        for name in steelsquid_boot.expand_modules:
            mod = sys.modules['expand.'+name]
            if hasattr(mod, "activate") and mod.activate():
                if hasattr(mod, "on_button_info") and callable(getattr(mod, "on_button_info")):
                    expand_on_button_info=True
                if hasattr(mod, "on_button") and callable(getattr(mod, "on_button")):
                    expand_on_button=True
                if hasattr(mod, "on_switch") and callable(getattr(mod, "on_switch")):
                    expand_on_switch=True
        if steelsquid_kiss_expand.activate():
            if hasattr(steelsquid_kiss_expand, "on_button_info") and callable(getattr(steelsquid_kiss_expand, "on_button_info")):
                steel_expand_on_button_info=True
            if hasattr(steelsquid_kiss_expand, "on_button") and callable(getattr(steelsquid_kiss_expand, "on_button")):
                steel_expand_on_button=True
            if hasattr(steelsquid_kiss_expand, "on_switch") and callable(getattr(steelsquid_kiss_expand, "on_switch")):
                steel_expand_on_switch=True
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
        steelsquid_piio.power_off_click(on_poweroff_button_click)
        steelsquid_piio.info_click(on_button_info)
        if expand_on_button or steel_expand_on_button:
            steelsquid_piio.button_click(1, on_button)
            steelsquid_piio.button_click(2, on_button)
            steelsquid_piio.button_click(3, on_button)
            steelsquid_piio.button_click(4, on_button)
            steelsquid_piio.button_click(5, on_button)
            steelsquid_piio.button_click(6, on_button)
        if expand_on_switch or steel_expand_on_switch:
            steelsquid_piio.switch_event(1, on_switch)
            steelsquid_piio.switch_event(2, on_switch)
            steelsquid_piio.switch_event(3, on_switch)
            steelsquid_piio.switch_event(4, on_switch)
            steelsquid_piio.switch_event(5, on_switch)
            steelsquid_piio.switch_event(6, on_switch)
        

    @staticmethod
    def on_disable():
        '''
        This will execute when system stops
        Do not execute long running stuff here
        '''
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
        
        
    @staticmethod
    def on_loop():
        '''
        This will execute over and over again untill it return None or -1
        If it return a number larger than 0 it will sleep for that number of seconds before execute again.
        If it return 0 it will not not sleep, will execute again imediately.
        '''    
        global last_voltage
        global last_print_voltage
        global expand_on_button_info
        global expand_on_button
        global expand_on_switch
        global steel_expand_on_button_info
        global steel_expand_on_button
        global steel_expand_on_switch
        new_voltage = steelsquid_piio.volt(2, 4)
        voltage_waring = int(steelsquid_utils.get_parameter("voltage_waring", "10"))
        voltage_poweroff = int(steelsquid_utils.get_parameter("voltage_poweroff", "8"))
        v_warn=""
        if new_voltage<voltage_waring:
            v_warn=" (Warning)"
            steelsquid_piio.low_bat(True)
            try:
                on_low_bat(new_voltage)
                if steelsquid_utils.get_flag("rover"):
                    steelsquid_kiss_global.Rover.on_low_bat(new_voltage)
                if steelsquid_utils.get_flag("alarm"):
                    steelsquid_kiss_global.Alarm.on_low_bat(new_voltage)
                for name in steelsquid_kiss_global.expand_modules:
                    mod = sys.modules['expand.'+name]
                    if hasattr(mod, "activate") and mod.activate():
                        if hasattr(mod, "on_low_bat") and callable(getattr(mod, "on_low_bat")):
                            mod.on_low_bat(new_voltage)
                if steelsquid_kiss_expand.activate():
                    if hasattr(steelsquid_kiss_expand, "on_low_bat") and callable(getattr(steelsquid_kiss_expand, "on_low_bat")):
                        steelsquid_kiss_expand.on_low_bat(new_voltage)
            except:
                steelsquid_utils.shout()
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
        steelsquid_piio.buz_flash(None, 0.1)
        steelsquid_event.broadcast_event("network")
        if expand_on_button_info:
            try:
                for name in steelsquid_kiss_global.expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_button_info()
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_button_info", is_error=True)

        if steel_expand_on_button_info:
            try:
                steelsquid_kiss_expand.on_button_info()
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_button_info", is_error=True)
        

    @staticmethod
    def on_button(button_nr):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        if expand_on_button:
            try:
                for name in steelsquid_boot.expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_button(button_nr)
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_button", is_error=True)

        if steel_expand_on_button:
            try:
                steelsquid_kiss_expand.on_button(button_nr)
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_button", is_error=True)


    @staticmethod
    def on_switch(dip_nr, status):
        '''
        THIS ONLY WORKS ON THE PIIO BOARD...
        Execute when switch 1 to 6 is is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        if expand_on_switch:
            try:
                for name in steelsquid_boot.expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_switch(dip_nr, status)
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_switch", is_error=True)
        if steel_expand_on_switch:
            try:
                steelsquid_kiss_expand.on_switch(dip_nr, status)
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_switch", is_error=True)


    @staticmethod
    def on_poweroff_button_click():
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
    
    
