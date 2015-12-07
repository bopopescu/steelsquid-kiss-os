#!/usr/bin/python -OO


'''
Global stuff for steelsquid kiss os
Reach the http server and Socket connection.
I also add some extra stuff here like Rover, IO and alarm

Use this to add functionality that my be used from different part of the system... example http server and socket server...

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
from datetime import datetime
from datetime import timedelta
import os
import urllib
import threading
import thread
import sys
import steelsquid_kiss_global
import steelsquid_piio
import steelsquid_boot
import importlib
import importlib
import expand
import steelsquid_kiss_expand
import Queue


# The socket connection, if enabled (not enabled = None)
# Flag: socket_server
# Parameter: socket_client
socket_connection = None

# The http webserver, if enabled (not enabled = None)
# Flag: web
http_server = None

# All loaded custom expand files (python module names in the expand directory that has bean imported)
expand_modules=[]

# Global data (key, Value)
event_data={}

# If data is changed in event_data, the methods in the list will fire (one thread will fire all events sequentially)
event_data_callback_methods=[]

# List with events that is to be fire by thread...
event_data_queue=Queue.Queue()

# Lock object for add to event_data_callback_methods
lock = threading.Lock()

# If more than this events pending for execution dropp new events
max_pending_events=128


def get_expand_module(name):
    '''
    Get a module from the expand directory
    Only return modules that has bean activated
    return: The module
    '''    
    return sys.modules['expand.'+name]


def is_expand_module(name):
    '''
    Check if a module is imported and active
    return: True/False
    '''    
    if 'expand.'+name in sys.modules:
        mod = sys.modules['expand.'+name]
        return hasattr(mod, "activate") and mod.activate() and mod.is_enabled
    else:
        return False
    
       
def add_event_data_callback(method):
    '''
    Add event callback method
    This method will fire when data is changed
    def method(key, value):
    '''    
    with lock:
        if len(event_data_callback_methods)==0:
            thread.start_new_thread(__event_data_handler, ()) 
        event_data_callback_methods.append(method)
        

def remove_event_data_callback(method):
    '''
    Remove event callback method
    '''    
    with lock:
        try:
            event_data_callback_methods.remove(method)
        except ValueError:
            pass        

           
def get_event_data(key):
    '''
    Get event data.
    return: The value (None = not found/No value)
    '''    
    try:
        return event_data[key]
    except ValueError:
        return None        


def set_event_data(key, value):
    '''
    Set event data.
    When eventdata is set methods in event_data_callback_methods will fire
    key: Key for the data
    value: Value for the data
    '''    
    event_data[key]=value
    if len(event_data_callback_methods)>0 and event_data_queue.qsize() < max_pending_events:
        event_data_queue.put((key, value))


def del_event_data(key, value):
    '''
    Delete event data.
    When eventdata is deleted methods in event_data_callback_methods will fire (with value=None)
    key: Key for the data
    '''    
    try:
        del event_data[key]
    except:
        pass
    if event_data_queue.qsize() < max_pending_events:
        event_data_queue.put((key, None))


def __event_data_handler():
    '''
    Fire the event data events
    '''    
    while True:
        key, value = event_data_queue.get()
        try:
            for method in event_data_callback_methods:
                method(key, value)
        except:
            steelsquid_utils.shout("Fatal error in event_data_handler: "+key, is_error=True)            


class PIIO(object):
    '''
    Fuctionality for my Steelsquid PIIO board
    Also see steelquid_piio.py
    '''

    # Is the PIIO board functionality enabled
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


    @classmethod
    def activate(cls):
        '''
        Return True/False if this functionality is to be enabled (execute on_enable)
        return: True/False
        '''    
        return steelsquid_utils.get_flag("piio")
        

    @classmethod
    def on_enable(cls):
        '''
        Enable the IO board functionality (this is executed by steelsquid_boot)
        Do not execute long running stuff here, do it in on_loop...
        '''    
        global expand_modules
        steelsquid_utils.shout("Steelsquid PIIO board enabled")
        for name in expand_modules:
            mod = sys.modules['expand.'+name]
            if hasattr(mod, "activate") and mod.activate():
                if hasattr(mod, "on_button_info") and callable(getattr(mod, "on_button_info")):
                    cls.expand_on_button_info=True
                if hasattr(mod, "on_button") and callable(getattr(mod, "on_button")):
                    cls.expand_on_button=True
                if hasattr(mod, "on_switch") and callable(getattr(mod, "on_switch")):
                    cls.expand_on_switch=True
        if steelsquid_kiss_expand.activate():
            if hasattr(steelsquid_kiss_expand, "on_button_info") and callable(getattr(steelsquid_kiss_expand, "on_button_info")):
                cls.steel_expand_on_button_info=True
            if hasattr(steelsquid_kiss_expand, "on_button") and callable(getattr(steelsquid_kiss_expand, "on_button")):
                cls.steel_expand_on_button=True
            if hasattr(steelsquid_kiss_expand, "on_switch") and callable(getattr(steelsquid_kiss_expand, "on_switch")):
                cls.steel_expand_on_switch=True
        steelsquid_piio.led(1, False)
        steelsquid_piio.led(2, False)
        steelsquid_piio.led(3, False)
        steelsquid_piio.led(4, False)
        steelsquid_piio.led(5, False)
        steelsquid_piio.led(6, False)
        steelsquid_piio.power_off_click(cls.on_poweroff_button_click)
        steelsquid_piio.info_click(cls.on_button_info)
        if cls.expand_on_button or cls.steel_expand_on_button:
            steelsquid_piio.button_click(1, cls.on_button)
            steelsquid_piio.button_click(2, cls.on_button)
            steelsquid_piio.button_click(3, cls.on_button)
            steelsquid_piio.button_click(4, cls.on_button)
            steelsquid_piio.button_click(5, cls.on_button)
            steelsquid_piio.button_click(6, cls.on_button)
        if cls.expand_on_switch or cls.steel_expand_on_switch:
            steelsquid_piio.switch_event(1, cls.on_switch)
            steelsquid_piio.switch_event(2, cls.on_switch)
            steelsquid_piio.switch_event(3, cls.on_switch)
            steelsquid_piio.switch_event(4, cls.on_switch)
            steelsquid_piio.switch_event(5, cls.on_switch)
            steelsquid_piio.switch_event(6, cls.on_switch)


    @classmethod
    def on_disable(cls):
        '''
        Disable the IO board functionality (this is executed by steelsquid_boot)
        Use this when system shutdown
        Do not execute long running stuff here...
        '''    
        cls.is_enabled=False
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


    @classmethod
    def on_loop(cls):
        '''
        This will execute over and over again untill it return None or -1
        If it return a number larger than 0 it will sleep for that number of seconds before execute again.
        If it return 0 it will not not sleep, will execute again imediately.
        '''    
        new_voltage = steelsquid_piio.volt(2, 4)
        voltage_waring = int(steelsquid_utils.get_parameter("voltage_waring", "10"))
        voltage_poweroff = int(steelsquid_utils.get_parameter("voltage_poweroff", "8"))
        v_warn=""
        if new_voltage<voltage_waring:
            v_warn=" (Warning)"
            steelsquid_piio.low_bat(True)
            try:
                cls.on_low_bat(new_voltage)
                if steelsquid_utils.get_flag("rover"):
                    steelsquid_kiss_global.Rover.on_low_bat(new_voltage)
                if steelsquid_utils.get_flag("alarm"):
                    steelsquid_kiss_global.Alarm.on_low_bat(new_voltage)
                for name in expand_modules:
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
            if new_voltage != cls.last_voltage:
                if abs(new_voltage - cls.last_print_voltage)>=0.1:
                    if cls.last_print_voltage == 0:
                        steelsquid_utils.shout("Voltage is: " + str(new_voltage), to_lcd=False)
                    cls.last_print_voltage = new_voltage
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


    @classmethod
    def on_network(cls, status, wired, wifi_ssid, wifi, wan):
        '''
        Execute on network up or down.
        status = True/False (up or down)
        wired = Wired ip number
        wifi_ssid = Cnnected to this wifi
        wifi = Wifi ip number
        wan = Ip on the internet
        '''    
        pass


    @classmethod
    def on_low_bat(cls, voltage):
        '''
        Execute when voltage is to low.
        Is set with the paramater: voltage_waring
        voltage = Current voltage
        '''    
        pass


    @classmethod
    def on_button_info(cls):
        '''
        Execute when info button clicken on the PIIO board
        '''    
        global expand_modules
        steelsquid_piio.buz_flash(None, 0.1)
        steelsquid_event.broadcast_event("network")
        if cls.expand_on_button_info:
            try:
                for name in expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_button_info()
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_button_info", is_error=True)

        if cls.steel_expand_on_button_info:
            try:
                steelsquid_kiss_expand.on_button_info()
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_button_info", is_error=True)


    @classmethod
    def on_button(cls, button_nr):
        '''
        Execute when button 1 to 6 is clicken on the PIIO board
        button_nr = button 1 to 6
        '''    
        global expand_modules
        if cls.expand_on_button:
            try:
                for name in expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_button(button_nr)
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_button", is_error=True)

        if cls.steel_expand_on_button:
            try:
                steelsquid_kiss_expand.on_button(button_nr)
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_button", is_error=True)


    @classmethod
    def on_switch(cls, dip_nr, status):
        '''
        Execute when switch 1 to 6 is changed on the PIIO board
        dip_nr = DIP switch nr 1 to 6
        status = True/False   (on/off)
        '''    
        global expand_modules
        if cls.expand_on_switch:
            try:
                for name in expand_modules:
                    mod = sys.modules['expand.'+name]
                    mod.on_switch(dip_nr, status)
            except:
                steelsquid_utils.shout("Fatal error in expand."+name+" on_switch", is_error=True)
        if cls.steel_expand_on_switch:
            try:
                steelsquid_kiss_expand.on_switch(dip_nr, status)
            except:
                steelsquid_utils.shout("Fatal error in steelsquid_kiss_expand on_switch", is_error=True)


    @classmethod
    def on_poweroff_button_click(cls):
        '''
        Power off the system
        '''
        steelsquid_piio.shutdown()
                

