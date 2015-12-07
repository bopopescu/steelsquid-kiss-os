#!/usr/bin/python -OO


'''.
This is an exempel file how to use the expand directory.
Files under the /opt/steelsquid/python/expand/ directory will be inportet aoutomatically.

If you use steelsquid_syncronisation:
Add this to config.txt and it will bli transmitted to the device automatically.
custom.py | /opt/steelsquid/python/expand/custom.py
Or if you putt this file under the expand folder on you development computer, steelsquid_syncronisation will automatically transfer it to the 
/opt/steelsquid/python/expand/ drectory on the Raspberry pi

If function on_enable() exist it will be executed when system starts (boot)
If function on_disable() exist it will be executed when system stops (shutdown)
If function on_network(status, wired, wifi_ssid, wifi, wan) exist it will be execute on network up or down
If function on_loop() exist it will execute over and over again untill it return None or -1
If finction on_event_data(key, value) exist it will execute when data is changed with steelsquid_kiss_global.set_event_data(key, value)

If this is a PIIO board
And if function on_low_bat(voltage) exist it will execute when voltage is to low.
And if function on_button(button_nr) exist it will execute when button 1 to 6 is clicken on the PIIO board
And if function on_button_info() exist it will execute when info button clicken on the PIIO board
And if function on_switch(dip_nr, status) exist it will execute when switch 1 to 6 is is changed on the PIIO board

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2014-12-26 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import steelsquid_kiss_global


# Is this enabled (on_enable has executed)
# This is set by the system automaticaly
is_enabled = False


def activate():
    '''
    Return True/False if this functionality is to be enabled (execute on_enable)
    return: True/False
    '''    
    return False


def on_enable():
    '''
    This will execute when system starts
    Do not execute long running stuff here, do it in on_loop...
    '''
    pass 
    

def on_disable():
    '''
    This will execute when system stops
    '''
    pass 

    
def on_loop():
    '''
    This will execute over and over again untill it return None or -1
    If it return a number larger than 0 it will sleep for that number of seconds before execute again.
    If it return 0 it will not not sleep, will execute again imediately.
    '''    
    return -1


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
    
    
def on_event_data(key, value):
    '''
    This will fire when data is changed with steelsquid_kiss_global.set_event_data(key, value)
    key=The key of the data
    value=The value of the data
    '''    
    pass
    

def on_low_bat(voltage):
    '''
    THIS ONLY WORKS ON THE PIIO BOARD...
    Execute when voltage is to low.
    Is set with the paramater: voltage_waring  
    voltage = Current voltage
    '''    
    pass


def on_button_info():
    '''
    THIS ONLY WORKS ON THE PIIO BOARD...
    Execute when info button clicken on the PIIO board
    '''    
    pass
    

def on_button(button_nr):
    '''
    THIS ONLY WORKS ON THE PIIO BOARD...
    Execute when button 1 to 6 is clicken on the PIIO board
    button_nr = button 1 to 6
    '''    
    pass


def on_switch(dip_nr, status):
    '''
    THIS ONLY WORKS ON THE PIIO BOARD...
    Execute when switch 1 to 6 is is changed on the PIIO board
    dip_nr = DIP switch nr 1 to 6
    status = True/False   (on/off)
    '''    
    pass


