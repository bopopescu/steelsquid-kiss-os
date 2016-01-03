#!/usr/bin/python -OO


'''
Some useful stuff for Raspberry Pi
 - Print text to HDD44780 compatible LCD
 - Print text to a nokia5110 LCD
 - Print text to ssd1306 oled  LCD
 - Read GPIO input.
 - Set GPIO output.
 - Measure_distance with a with HC-SR04.
 - Controll Adafruit 16-Channel servo driver
 - Use a MCP230xx
 - Analog input ADS1015
 - Controll Trex robot controller
 - Sabertooth motor controller
 - Piborg diablo motor controller
 - mpu6050 Acc/Gyro board

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_i2c
import steelsquid_utils
import steelsquid_trex
import sys
import time
import os
import threading
import thread
import thread
import signal
import smbus
import math
import RPi.GPIO as GPIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from sets import Set
from Adafruit_PWM_Servo_Driver import PWM
from MCP23017 import MCP23017
from Adafruit_ADS1x15 import ADS1x15
from Adafruit_MCP4725 import MCP4725
from Adafruit_I2C import Adafruit_I2C
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
import Diablo

EDGE_RISING = GPIO.RISING
EDGE_FALLING = GPIO.FALLING
EDGE_BOTH = GPIO.BOTH
PULL_UP = GPIO.PUD_UP
PULL_DOWN = GPIO.PUD_DOWN
PULL_NONE = GPIO.PUD_OFF
SETUP_NONE = 0
SETUP_OUT = 1
SETUP_IN = 2
TIMEOUT = 2100
setup = [SETUP_NONE] * 32
lcd = None
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
lcd_last_text = ""
lock = threading.Lock()
lock_mcp = threading.Lock()
lock_event = threading.Lock()
distances_created = []
pwm = None
ads_48 = None
ads_49 = None
ads_4A = None
ads_4B = None
GAIN_6_144_V = 6144
GAIN_4_096_V = 4096
GAIN_2_048_V = 2048
GAIN_1_024_V = 1024
GAIN_0_512_V = 512
GAIN_0_256_V = 256
mcp_setup_20 = [SETUP_NONE] * 16
mcp_setup_21 = [SETUP_NONE] * 16
mcp_setup_22 = [SETUP_NONE] * 16
mcp_setup_23 = [SETUP_NONE] * 16
mcp_setup_24 = [SETUP_NONE] * 16
mcp_setup_25 = [SETUP_NONE] * 16
mcp_setup_26 = [SETUP_NONE] * 16
mcp_setup_27 = [SETUP_NONE] * 16
mcp_20 = None
mcp_21 = None
mcp_22 = None
mcp_23 = None
mcp_24 = None
mcp_25 = None
mcp_26 = None
mcp_27 = None
sabertooth = None
dac = None
vref_voltage = 3.3
nokia_lcd = None
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
draw = ImageDraw.Draw(image)
lcd_auto = 0
mcp23017_events = {}
mcp23017_events[20] = []
mcp23017_events[21] = []
mcp23017_events[22] = []
mcp23017_events[23] = []
mcp23017_events[24] = []
mcp23017_events[25] = []
mcp23017_events[26] = []
mcp23017_events[27] = []
diablo = None
po16_setup = [SETUP_NONE] * 8
event_notificatin_list=[]
event_last_mpu6050_movement=None
event_last_mpu6050_rotation=None
po12_adc_has_setup=False


def cleanup():
    '''
    Clean all event detection 
    '''
    gpio_event_remove(None)
    gpio_cleanup()
    event_notificatin_cleanup()
    mcp23017_cleanup()
    

def gpio_event_remove(gpio=None):
    '''
    Remove listening for input event
    @param gpio: GPIO number (None remove all)
    '''
    if gpio==None:
        for i in range(4, 27, 1):
            try:
                GPIO.remove_event_detect(i)
            except:
                pass
    else:
        GPIO.remove_event_detect(gpio)


def gpio_cleanup():
    '''
    cleanup
    '''
    global setup
    setup = [SETUP_NONE] * 32    
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)


def gpio_setup_out(gpio):
    '''
    set gpio pin to output mode
    @param gpio: GPIO number
    '''
    global setup
    gpio = int(gpio)
    GPIO.setup(gpio, GPIO.OUT, pull_up_down=GPIO.PUD_OFF)
    setup[gpio] == SETUP_OUT


def gpio_setup_in(gpio, resistor=PULL_DOWN):
    '''
    set gpio pin to input mode 
    @param gpio: GPIO number
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    '''
    global setup
    gpio = int(gpio)
    GPIO.setup(gpio, GPIO.IN, pull_up_down=resistor)
    setup[gpio] == SETUP_IN


def gpio_set(gpio, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin
    @param gpio: GPIO number
    @param state: True/False
    '''
    global setup
    state = steelsquid_utils.to_boolean(state)
    gpio = int(gpio)
    if not setup[gpio] == SETUP_OUT:
        gpio_setup_out(gpio)
    GPIO.output(gpio, state)


def gpio_flash(gpio, status, seconds):
    '''
    Change to hight (true) or low (false) on a pin alternately
    @param gpio: GPIO number
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("gpio_flash"+str(gpio), status, seconds, gpio_set, (gpio, True,), gpio_set, (gpio, False,))


def gpio_get(gpio, resistor=PULL_DOWN):
    '''
    Get gpio pin state
    @param gpio: GPIO number
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    @return: True/False
    '''
    global setup
    gpio = int(gpio)
    if not setup[gpio] == SETUP_IN:
        gpio_setup_in(gpio, resistor)
    if GPIO.input(gpio) == 1:
        return True
    else:
        return False


def gpio_event(gpio, callback_method, bouncetime_ms=60, resistor=PULL_DOWN, edge=EDGE_BOTH):
    '''
    Listen for events on gpio pin
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    @edge: EDGE_BOTH, EDGE_FALLING, EDGE_RISING
    '''
    global setup
    gpio = int(gpio)
    if not setup[gpio] == SETUP_IN:
        gpio_setup_in(gpio, resistor)
    def call_met(para):
        status = False
        if GPIO.input(para) == 1:
            status = True
        try:
            callback_method(para, status)          
        except:
            steelsquid_utils.shout()
    if bouncetime_ms!=0:
        GPIO.add_event_detect(gpio, edge, callback=call_met, bouncetime=bouncetime_ms)
    else:
        GPIO.add_event_detect(gpio, edge, callback=call_met)


def gpio_click(gpio, callback_method, bouncetime_ms=60, resistor=PULL_DOWN):
    '''
    Connect a button to gpio pin
    Will fire when button is released.
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    '''
    global setup
    gpio = int(gpio)
    if not setup[gpio] == SETUP_IN:
        gpio_setup_in(gpio, resistor)
    def call_met(para):
        status = False
        if GPIO.input(para) == 1:
            status = True
        if status == (resistor==PULL_UP):
            try:
                callback_method(para)          
            except:
                steelsquid_utils.shout()
    global down
    global up
    down = -1
    up = -1
    if bouncetime_ms!=0:
        GPIO.add_event_detect(gpio, EDGE_BOTH, callback=call_met, bouncetime=bouncetime_ms)
    else:
        GPIO.add_event_detect(gpio, EDGE_BOTH, callback=call_met)


def mcp23017_setup_out(address, gpio):
    '''
    Set MCP23017 as output
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    if address == 20:
        global mcp_20
        if mcp_20 == None:
            with steelsquid_i2c.Lock():
                mcp_20 = MCP23017(busnum = 1, address = 0x20, num_gpios = 16)
                mcp_20.configSystemInterrupt(mcp_20.INTMIRRORON, mcp_20.INTPOLACTIVEHIGH)
        if mcp_setup_20[gpio] != SETUP_OUT:
            mcp_setup_20[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_20.pullUp(gpio, 0)
                mcp_20.pinMode(gpio, mcp_20.OUTPUT)
        return mcp_20
    elif address == 21:
        global mcp_21
        if mcp_21 == None:
            with steelsquid_i2c.Lock():
                mcp_21 = MCP23017(busnum = 1, address = 0x21, num_gpios = 16)
                mcp_21.configSystemInterrupt(mcp_21.INTMIRRORON, mcp_21.INTPOLACTIVEHIGH)
        if mcp_setup_21[gpio] != SETUP_OUT:
            mcp_setup_21[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_21.pullUp(gpio, 0)
                mcp_21.pinMode(gpio, mcp_21.OUTPUT)
        return mcp_21
    elif address == 22:
        global mcp_22
        if mcp_22 == None:
            with steelsquid_i2c.Lock():
                mcp_22 = MCP23017(busnum = 1, address = 0x22, num_gpios = 16)
                mcp_22.configSystemInterrupt(mcp_22.INTMIRRORON, mcp_22.INTPOLACTIVEHIGH)
        if mcp_setup_22[gpio] != SETUP_OUT:
            mcp_setup_22[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_22.pullUp(gpio, 0)
                mcp_22.pinMode(gpio, mcp_22.OUTPUT)
        return mcp_22
    elif address == 23:
        global mcp_23
        if mcp_23 == None:
            with steelsquid_i2c.Lock():
                mcp_23 = MCP23017(busnum = 1, address = 0x23, num_gpios = 16)
                mcp_23.configSystemInterrupt(mcp_23.INTMIRRORON, mcp_23.INTPOLACTIVEHIGH)
        if mcp_setup_23[gpio] != SETUP_OUT:
            mcp_setup_23[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_23.pullUp(gpio, 0)
                mcp_23.pinMode(gpio, mcp_23.OUTPUT)
        return mcp_23
    elif address == 24:
        global mcp_24
        if mcp_24 == None:
            with steelsquid_i2c.Lock():
                mcp_24 = MCP23017(busnum = 1, address = 0x24, num_gpios = 16)
                mcp_24.configSystemInterrupt(mcp_24.INTMIRRORON, mcp_24.INTPOLACTIVEHIGH)
        if mcp_setup_24[gpio] != SETUP_OUT:
            mcp_setup_24[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_24.pullUp(gpio, 0)
                mcp_24.pinMode(gpio, mcp_24.OUTPUT)
        return mcp_24
    elif address == 25:
        global mcp_25
        if mcp_25 == None:
            with steelsquid_i2c.Lock():
                mcp_25 = MCP23017(busnum = 1, address = 0x25, num_gpios = 16)
                mcp_25.configSystemInterrupt(mcp_25.INTMIRRORON, mcp_25.INTPOLACTIVEHIGH)
        if mcp_setup_25[gpio] != SETUP_OUT:
            mcp_setup_25[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_25.pullUp(gpio, 0)
                mcp_25.pinMode(gpio, mcp_25.OUTPUT)
        return mcp_25
    elif address == 26:
        global mcp_26
        if mcp_26 == None:
            with steelsquid_i2c.Lock():
                mcp_26 = MCP23017(busnum = 1, address = 0x26, num_gpios = 16)
                mcp_26.configSystemInterrupt(mcp_26.INTMIRRORON, mcp_26.INTPOLACTIVEHIGH)
        if mcp_setup_26[gpio] != SETUP_OUT:
            mcp_setup_26[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_26.pullUp(gpio, 0)
                mcp_26.pinMode(gpio, mcp_26.OUTPUT)
        return mcp_26
    elif address == 27:
        global mcp_27
        if mcp_27 == None:
            with steelsquid_i2c.Lock():
                mcp_27 = MCP23017(busnum = 1, address = 0x27, num_gpios = 16)
                mcp_27.configSystemInterrupt(mcp_27.INTMIRRORON, mcp_27.INTPOLACTIVEHIGH)
        if mcp_setup_27[gpio] != SETUP_OUT:
            mcp_setup_27[gpio] == SETUP_OUT
            with steelsquid_i2c.Lock():
                mcp_27.pullUp(gpio, 0)
                mcp_27.pinMode(gpio, mcp_27.OUTPUT)
        return mcp_27


def mcp23017_setup_in(address, gpio, pullup=True):
    '''
    Set MCP23017 as input
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    @param pullup: use pullup resistor
    The MCP23017 h7as 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    if pullup==True:
        pullup = 1
    else:
        pullup = 0
    if address == 20:
        global mcp_20
        if mcp_20 == None:
            with steelsquid_i2c.Lock():
                mcp_20 = MCP23017(busnum = 1, address = 0x20, num_gpios = 16)
                mcp_20.configSystemInterrupt(mcp_20.INTMIRRORON, mcp_20.INTPOLACTIVEHIGH)
        if mcp_setup_20[gpio] != SETUP_IN:
            mcp_setup_20[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_20.pinMode(gpio, mcp_20.INPUT)
                mcp_20.pullUp(gpio, pullup)
        return mcp_20
    elif address == 21:
        global mcp_21
        if mcp_21 == None:
            with steelsquid_i2c.Lock():
                mcp_21 = MCP23017(busnum = 1, address = 0x21, num_gpios = 16)
                mcp_21.configSystemInterrupt(mcp_21.INTMIRRORON, mcp_21.INTPOLACTIVEHIGH)
        if mcp_setup_21[gpio] != SETUP_IN:
            mcp_setup_21[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_21.pinMode(gpio, mcp_21.INPUT)
                mcp_21.pullUp(gpio, pullup)
        return mcp_21
    elif address == 22:
        global mcp_22
        if mcp_22 == None:
            with steelsquid_i2c.Lock():
                mcp_22 = MCP23017(busnum = 1, address = 0x22, num_gpios = 16)
                mcp_22.configSystemInterrupt(mcp_22.INTMIRRORON, mcp_22.INTPOLACTIVEHIGH)
        if mcp_setup_22[gpio] != SETUP_IN:
            mcp_setup_22[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_22.pinMode(gpio, mcp_22.INPUT)
                mcp_22.pullUp(gpio, pullup)
        return mcp_22
    elif address == 23:
        global mcp_23
        if mcp_23 == None:
            with steelsquid_i2c.Lock():
                mcp_23 = MCP23017(busnum = 1, address = 0x23, num_gpios = 16)
                mcp_23.configSystemInterrupt(mcp_23.INTMIRRORON, mcp_23.INTPOLACTIVEHIGH)
        if mcp_setup_23[gpio] != SETUP_IN:
            mcp_setup_23[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_23.pinMode(gpio, mcp_23.INPUT)
                mcp_23.pullUp(gpio, pullup)
        return mcp_23
    elif address == 24:
        global mcp_24
        if mcp_24 == None:
            with steelsquid_i2c.Lock():
                mcp_24 = MCP23017(busnum = 1, address = 0x24, num_gpios = 16)
                mcp_24.configSystemInterrupt(mcp_24.INTMIRRORON, mcp_24.INTPOLACTIVEHIGH)
        if mcp_setup_24[gpio] != SETUP_IN:
            mcp_setup_24[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_24.pinMode(gpio, mcp_24.INPUT)
                mcp_24.pullUp(gpio, pullup)
        return mcp_24
    elif address == 25:
        global mcp_25
        if mcp_25 == None:
            with steelsquid_i2c.Lock():
                mcp_25 = MCP23017(busnum = 1, address = 0x25, num_gpios = 16)
                mcp_25.configSystemInterrupt(mcp_25.INTMIRRORON, mcp_25.INTPOLACTIVEHIGH)
        if mcp_setup_25[gpio] != SETUP_IN:
            mcp_setup_25[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_25.pinMode(gpio, mcp_25.INPUT)
                mcp_25.pullUp(gpio, pullup)
        return mcp_25
    elif address == 26:
        global mcp_26
        if mcp_26 == None:
            with steelsquid_i2c.Lock():
                mcp_26 = MCP23017(busnum = 1, address = 0x26, num_gpios = 16)
                mcp_26.configSystemInterrupt(mcp_26.INTMIRRORON, mcp_26.INTPOLACTIVEHIGH)
        if mcp_setup_26[gpio] != SETUP_IN:
            mcp_setup_26[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_26.pinMode(gpio, mcp_26.INPUT)
                mcp_26.pullUp(gpio, pullup) 
        return mcp_26
    elif address == 27:
        global mcp_27
        if mcp_27 == None:
            with steelsquid_i2c.Lock():
                mcp_27 = MCP23017(busnum = 1, address = 0x27, num_gpios = 16)
                mcp_27.configSystemInterrupt(mcp_27.INTMIRRORON, mcp_27.INTPOLACTIVEHIGH)
        if mcp_setup_27[gpio] != SETUP_IN:
            mcp_setup_27[gpio] == SETUP_IN
            with steelsquid_i2c.Lock():
                mcp_27.pinMode(gpio, mcp_27.INPUT)
                mcp_27.pullUp(gpio, pullup)
        return mcp_27



def mcp23017_set(address, gpio, value):
    '''
    Set a gpio hight or low on a MCP23017
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @param value: True/False
    '''
    gpio = int(gpio)
    address = int(address)
    value = steelsquid_utils.to_boolean(value)
    mcp = mcp23017_setup_out(address, gpio)
    with steelsquid_i2c.Lock():
        if value == True:
            mcp.output(gpio, 1) 
        else:
            mcp.output(gpio, 0) 
        

def mcp23017_flash(address, gpio, status, seconds):
    '''
    Set a gpio hight or low on a MCP23017
    Change to hight (true) or low (false) on a pin alternately
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: GPIO number
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("mcp23017_flash"+str(address)+str(gpio), status, seconds, mcp23017_set, (address, gpio, True,), mcp23017_set, (address, gpio, False,))
        
        
def mcp23017_get(address, gpio, pullup=True):
    '''
    Get status on pin
    Connect GPIO to gnd (using internal pull-up)    
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @return: True/False
    True = Hight (1)
    False = Low (0)
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio, pullup)
    with steelsquid_i2c.Lock():
        if mcp.input(gpio)==1:
            return True
        else:
            return False


def mcp23017_event(address, gpio, callback_method, pullup=True, rpi_gpio=26): 
    ''' 
    Listen for event
    Connect GPIO to gnd (using internal pull-up)    
    If this is to work one of the trigger pin needs to be connected to raspberry Pi pin 26 (you can change this with paramater rpi_gpio)
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @param address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    @param callback_method: execute this method on event (paramater is the address, gpio and status (True/False))
                            callback_method(address, pin, status)
    @param pullup: Use internal pululp
    @param rpi_gpio: Raspberry pi glio number to use for the interruppt (Can not use the same gpio for mutipple mcp23017)
    '''
    global mcp23017_events
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio, pullup)
    mcp.configPinInterrupt(gpio, mcp.INTERRUPTON, mcp.INTERRUPTCOMPAREPREVIOUS)
    mcp.clearInterrupts()
    post = [None] * 4
    post[0] = gpio
    post[1] = callback_method
    post[2] = None
    post[3] = False #event
    with(lock_mcp):
        if len(mcp23017_events[address]) == 0: 
            mcp23017_events[address].append(post)
            def mcp23017_call(para, status):
                '''
                '''
                for p in mcp23017_events[address]:
                    gpio = p[0]
                    callback_method = p[1]
                    last_v = p[2]
                    is_click=p[3]
                    with steelsquid_i2c.Lock():
                        new_v = mcp.input(gpio)==1
                        if last_v==None:
                            p[2] = new_v
                        elif last_v != new_v:
                            if is_click:
                                if new_v==True:
                                    try:
                                        callback_method(address, gpio)
                                    except:
                                        steelsquid_utils.shout()
                            else:
                                try:
                                    callback_method(address, gpio, new_v)
                                except:
                                    steelsquid_utils.shout()
                                    
                            p[2] = new_v
                mcp.clearInterrupts()
            gpio_event(rpi_gpio, mcp23017_call, bouncetime_ms=0, resistor=PULL_DOWN, edge=EDGE_RISING)
        else: 
            mcp23017_events[address].append(post)
            

def mcp23017_click(address, gpio, callback_method, pullup=True, rpi_gpio=26):
    '''
    Listen for click
    Connect GPIO to gnd (using internal pull-up)    
    If this is to work one of the trigger pin needs to be connected to raspberry Pi pin 26 (you can change this with paramater rpi_gpio)
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @param Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    @param rpi_gpio: Raspberry pi glio number to use for the interruppt (Can not use the same gpio for mutipple mcp23017)
    '''
    global mcp23017_events
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio, pullup)
    mcp.configPinInterrupt(gpio, mcp.INTERRUPTON, mcp.INTERRUPTCOMPAREPREVIOUS)
    mcp.clearInterrupts()
    post = [None] * 4
    post[0] = gpio
    post[1] = callback_method
    post[2] = None
    post[3] = True #click
    with(lock_mcp):
        if len(mcp23017_events[address]) == 0: 
            mcp23017_events[address].append(post)
            def mcp23017_call(para, status):
                for p in mcp23017_events[address]:
                    gpio = p[0]
                    callback_method = p[1]
                    last_v = p[2]
                    is_click=p[3]
                    with steelsquid_i2c.Lock():
                        new_v = mcp.input(gpio)==1
                        if last_v==None:
                            p[2] = new_v
                        elif last_v != new_v:
                            if is_click:
                                if new_v==True:
                                    try:
                                        callback_method(address, gpio)
                                    except:
                                        steelsquid_utils.shout()
                            else:
                                try:
                                    callback_method(address, gpio, new_v)
                                except:
                                    steelsquid_utils.shout()
                                    
                            p[2] = new_v
                mcp.clearInterrupts()
            gpio_event(rpi_gpio, mcp23017_call, bouncetime_ms=0, resistor=PULL_DOWN, edge=EDGE_RISING)
        else: 
            mcp23017_events[address].append(post)


def mcp23017_event_remove(address, gpio):
    '''
    Remove listen for event or click on the MCP23017
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @param Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    '''
    global mcp23017_events
    gpio = int(gpio)
    address = int(address)
    with(lock_mcp):
        e_list = mcp23017_events[address]
        for i in xrange(len(e_list) - 1, -1, -1):
            post = e_list[i]
            if post[0]==gpio:
                del e_list[i]


def mcp23017_cleanup():
    '''
    Remove all listener on the MCP23017
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    global mcp23017_events
    with(lock_mcp):
        for key, e_list in mcp23017_events.items():
            for i in xrange(len(e_list) - 1, -1, -1):
                del e_list[i]


def ads1015(address, gpio, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    address= 48, 49, 4A, 4B 
    gpio = 0 to 3
    '''
    address = str(address)
    gpio = int(gpio)
    with steelsquid_i2c.Lock():
        return __ads1015(address).readADCSingleEnded(gpio, gain, 250) / 1000


def ads1015_median(address, gpio, gain=GAIN_6_144_V, samples=8):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    Median of number of samples
    address= 48, 49, 4A, 4B 
    gpio = 0 to 3
    '''
    a_list=[]
    for i in range(samples):
        value = ads1015(address, gpio, gain=GAIN_6_144_V)
        a_list.append(value)
        time.sleep(0.01)
    return steelsquid_utils.median(a_list)
    

def __ads1015(address):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    address= 48, 49, 4A, 4B 
    gpio = 0 to 3
    '''
    address = str(address)
    if address == "48":
        global ads_48
        if ads_48==None:
            ads_48 = ADS1x15(address = 0x48, ic=0x00)
        return ads_48
    elif address == "49":
        global ads_49
        if ads_49==None:
            ads_49 = ADS1x15(address = 0x49, ic=0x00)
        return ads_49
    elif address == "4A":
        global ads_4A
        if ads_4A==None:
            ads_4A = ADS1x15(address = 0x4A, ic=0x00)
        return ads_4A
    elif address == "4B":
        global ads_4B
        if ads_4B==None:
            ads_4B = ADS1x15(address = 0x4B, ic=0x00)
        return ads_4B


def mcp4725(address, value):
    '''
    Write analog out from MCP4725 (0 to 5v)
    address= 60
    value= 0 and 4095
    '''
    global dac
    address = str(address)
    value = int(value)
    if address == "60":
        if dac==None:
            dac = MCP4725(0x60)
        dac.setVoltage(value)


def mcp4728(address, volt0, volt1, volt2, volt3):
    '''
    Write analog out from MCP4728 (0 to 5v)
    address = 61
    volt0 to3 = Voltage on pins (0 and 4095)
    '''
    address = int(address)
    if address == 61:
        address = 0x61
    volt0 = int(volt0)
    volt1 = int(volt1)
    volt2 = int(volt2)
    volt3 = int(volt3)
    the_bytes = [(volt0 >> 8) & 0xFF, (volt0) & 0xFF, (volt1 >> 8) & 0xFF, (volt1) & 0xFF,
             (volt2 >> 8) & 0xFF, (volt2) & 0xFF, (volt3 >> 8) & 0xFF, (volt3) & 0xFF]    
    steelsquid_i2c.write_bytes(address, 0x50, the_bytes)
    
    
def hdd44780_write(text, number_of_seconds = 0, force_setup = False, is_i2c=True):
    '''
    Print text to HDD44780 compatible LCD
    @param text: Text to write (\n or \\ = new line)
    @param number_of_seconds: How long to show this message, then show the last message again (if there was one)
                              < 1 Show for ever
    EX1: Message in the screen: A message
         hdd44780_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A message
    EX2: Message in the screen: 
         hdd44780_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A new message
    @param force_setup: Force setup of pins
    @param is_icc: Is the LCD connected by i2c
    The text can also be a list, will join the list with spaces between.
    '''
    global lcd
    global lcd_last_text
    if number_of_seconds > 0 and len(lcd_last_text) > 0:
        steelsquid_utils.execute_delay(number_of_seconds, hdd44780_write, (None), print_error=False)
        hdd44780_write(text, -111, force_setup)
    else:
        with lock:
            if text == None:
                text = lcd_last_text
            elif number_of_seconds != -111:
                lcd_last_text = text
            if is_i2c:
                if lcd == None or force_setup:
                    from steelsquid_lcd_hdd44780 import CharLCDIcc
                    lcd = CharLCDIcc()
                else:
                    lcd.clear()
            else:
                if lcd == None or force_setup:
                    from steelsquid_lcd_hdd44780 import CharLCD
                    lcd = CharLCD()
                else:
                    lcd.clear()
            if isinstance(text, list):
                l = []
                for arg in text:
                    l.append(arg)
                    l.append(" ")
                if len(l) > 0:
                    l = l[:-1]
                text = ''.join(l)
            text = text.replace("\\", "\n")
            sli = text.split("\n")
            new_mes = []
            for line in sli:
                if len(line)>16:
                    line = line[:16]
                new_mes.append(line)
            if len(sli)==1:
                lcd.message(sli[0])
            elif len(sli)>1:
                lcd.message(sli[0]+'\n'+sli[1])


def hdd44780_status(status):
    '''
    Turn on/off a HDD44780 compatible LCD
    '''
    with lock:
        global lcd
        if lcd == None:
            from steelsquid_lcd_hdd44780 import CharLCDIcc
            lcd = CharLCDIcc()
        if status == True:
            lcd.display_on()
        else:
            lcd.display_off()


def nokia5110_write(text, number_of_seconds = 0, force_setup = False):
    '''
    Print text to nokia5110  LCD
    @param text: Text to write (\n or \\ = new line)
    @param number_of_seconds: How long to show this message, then show the last message again (if there was one)
                              < 1 Show for ever
    EX1: Message in the screen: A message
         lcd_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A message
    EX2: Message in the screen: 
         lcd_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A new message
    @param force_setup: Force setup of pins
    The text can also be a list, will join the list with spaces between.
    '''
    global nokia_lcd
    global lcd_last_text
    DC = 9
    RST = 7
    SPI_PORT = 0
    SPI_DEVICE = 0
    if number_of_seconds > 0 and len(lcd_last_text) > 0:
        steelsquid_utils.execute_delay(number_of_seconds, nokia5110_write, (None), print_error=False)
        nokia5110_write(text, -111, force_setup)
    else:
        with lock:
            if text == None:
                text = lcd_last_text
            elif number_of_seconds != -111:
                lcd_last_text = text
            if isinstance(text, list):
                l = []
                for arg in text:
                    l.append(arg)
                    l.append(" ")
                if len(l) > 0:
                    l = l[:-1]
                text = ''.join(l)
            text = text.replace("\\", "\n")
            if len(text)>17 and "\n" not in text:
                text = "".join(text[i:i+17] + "\n" for i in xrange(0,len(text),17))
            draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
            sli = text.split("\n")
            i = 0
            for line in sli:
                if len(line)>17:
                    line = line[:17]
                draw.text((0, i), line, font=font)
                i = i + 9
                if i > 36:
                    break
            if nokia_lcd == None or force_setup:
                nokia_lcd = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
                contrast = int(steelsquid_utils.get_parameter("nokia_contrast", 60))
                nokia_lcd.begin(contrast=contrast)
            nokia_lcd.image(image)
            nokia_lcd.display()


def ssd1306_write(text=None, number_of_seconds = 0):
    '''
    Print text to ssd1306 oled  LCD
    @param text: Text to write (\n or \\ = new line)
    @param number_of_seconds: How long to show this message, then show the last message again (if there was one)
                              < 1 Show for ever
    EX1: Message in the screen: A message
         lcd_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A message
    EX2: Message in the screen: 
         lcd_write("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A new message
    The text can also be a list, will join the list with spaces between.
    '''
    import steelsquid_oled_ssd1306
    global lcd_last_text
    if number_of_seconds > 0 and len(lcd_last_text) > 0:
        steelsquid_utils.execute_delay(number_of_seconds, ssd1306_write, (None), print_error=False)
        ssd1306_write(text, -111)
    else:
        with lock:
            if text == None:
                text = lcd_last_text
            elif number_of_seconds != -111:
                lcd_last_text = text
            if isinstance(text, list):
                l = []
                for arg in text:
                    l.append(arg)
                    l.append(" ")
                if len(l) > 0:
                    l = l[:-1]
                text = ''.join(l)
            text = text.replace("\\", "\n")
            if len(text)>25 and "\n" not in text:
                text = "".join(text[i:i+25] + "\n" for i in xrange(0,len(text),25))
            sli = text.split("\n")
            i = 1
            steelsquid_oled_ssd1306.init()
            for line in sli:
                if len(line)>25:
                    line = line[:25]
                steelsquid_oled_ssd1306.write(line, 2, i)
                i = i + 10
                if i > 61:
                    break
            steelsquid_oled_ssd1306.show()


def lcd_auto_write(text, number_of_seconds = 0, force_setup = False):
    global lcd_auto
    if lcd_auto == 0:
        try:
            ssd1306_write(" ", 0)
            lcd_auto = 1
        except:
            try:
                nokia5110_write(" ", 0, force_setup)
                lcd_auto = 2
            except:
                try:
                    hdd44780_write(" ", 0, force_setup, True)
                    lcd_auto = 3
                except:
                    lcd_auto = 4
    if lcd_auto == 1:
        try:
            ssd1306_write(text, number_of_seconds)
        except:
           lcd_auto = 0
    elif lcd_auto == 2:
        try:
            nokia5110_write(text, number_of_seconds, force_setup)
        except:
           lcd_auto = 0
    elif lcd_auto == 3:
        try:
            hdd44780_write(text, number_of_seconds, force_setup, True)       
        except:
           lcd_auto = 0


def hcsr04_distance(trig_gpio, echo_gpio, force_setup = False):
    '''
    Measure_distance with a with HC-SR04.
    @param trig_gpio: The trig gpio
    @param echo_gpio: The echo gpio
    @param force_setup: Force setup of pins
    @return: The distance in cm (-1 = unable to mesure)
    '''
    trig_gpio = int(trig_gpio)
    echo_gpio = int(echo_gpio)
    global distances_created
    if not trig_gpio in distances_created or force_setup:
        gpio_setup_out(trig_gpio)
        gpio_setup_in(echo_gpio, resistor=PULL_UP)
        gpio_set(trig_gpio, False)
        distances_created.append(trig_gpio)
        time.sleep(0.00001)
    gpio_set(trig_gpio, True)
    time.sleep(0.00001)
    gpio_set(trig_gpio, False)
    countdown = TIMEOUT
    while (gpio_get(echo_gpio) == False and countdown > 0):
        countdown = countdown - 1
    if countdown > 0:
        echostart = time.time()
        countdown = TIMEOUT
        while (gpio_get(echo_gpio) == True and countdown > 0):
            countdown = countdown - 1
        if countdown > 0:
            echoend = time.time()
            echoduration = echoend - echostart
            distance = echoduration * 17150
            return int(round(distance, 0))
        else:
            return -1
    else:
        return -1


def hcsr04_event(trig_gpio, echo_gpio, callback_method, min_change=2, sample_sleep=0.2):
    '''
    Listen for distance change with HC-SR04 and execute method on change.
    def callback_method(cm):
       ...do stuff
    The distance in cm (-1 = unable to mesure)
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    post = [None] * 6
    post[0] = 6  #hcsr04_event
    post[1] = callback_method
    post[2] = min_change
    post[3] = None
    post[4] = trig_gpio
    post[5] = echo_gpio
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)


def pca9685_move(servo, value):
    '''
    Move Adafruit 16-channel I2c servo to position (pwm value)
    @param servo: 0 to 15
    @param value: min=150, max=600 (may differ between servos)
    '''
    with steelsquid_i2c.Lock():
        global pwm
        if pwm == None:
            pwm = PWM(0x40, debug=False)
            pwm.setPWMFreq(60) 
        pwm.setPWM(int(servo), 0, int(value))


def sabertooth_motor_speed(left, right, the_port="/dev/ttyAMA0"):
    '''
    Set the speed on a sabertooth dc motor controller.
    left and right:
        from -100 to +100
        -100 = 100% back speed
        0 = no speed
        100 = 100% forward speed
    the_port: /dev/ttyAMA0, the_port=/dev/ttyUSB0...
    '''
    with steelsquid_i2c.Lock():
        left = int(left)
        right = int(right)
        global sabertooth
        if sabertooth==None:
            import steelsquid_sabertooth
            if the_port == None:
                the_port = steelsquid_utils.get_parameter("sabertooth_port", "")
            sabertooth = steelsquid_sabertooth.SteelsquidSabertooth(serial_port=the_port)
        sabertooth.set_dc_speed(left, right)
    

def trex_reset():
    '''
    Reset the trex controller to default
    Stop dc motors...
    '''
    steelsquid_trex.trex_reset()
    
    
def trex_motor(left, right):
    '''
    Set speed of the dc motors
    left and right can have the folowing values: -255 to 255
    -255 = Full speed astern
    0 = stop
    255 = Full speed ahead
    '''
    steelsquid_trex.trex_motor(left, right)


def trex_servo(servo, position):
    '''
    Set servo position
    Servo = 1 to 6
    Position = Typically the servo position should be a value between 1000 and 2000 although it will vary depending on the servos used
    '''
    steelsquid_trex.trex_servo(servo, position)


def trex_status():
    '''
    Get status from trex
     - Battery voltage:   An integer that is 100x the actual voltage
     - Motor current:  Current drawn by the motor in mA
     - Accelerometer
     - Impact
    Return tuple: battery_voltage, left_motor_current, right_motor_current, accelerometer_x, accelerometer_y, accelerometer_z, impact_x, impact_y, impact_z
    '''
    return steelsquid_trex.trex_status()


def diablo_motor_1(speed):
    '''
    Drive Piborg diablo motor 1
    Speed -1000 to 1000
    '''
    global diablo
    speed = int(speed)
    with steelsquid_i2c.Lock():
        if diablo == None:
            diablo = Diablo.Diablo()
            diablo.Init()
            diablo.ResetEpo()
            diablo.SetMotor1(0)         
            diablo.SetMotor2(0)         
        speed = float(speed)/1000
        diablo.SetMotor1(speed)         
    
    
def diablo_motor_2(speed):
    '''
    Drive Pibor g diablo motor 2
    Speed -1000 to 1000
    '''
    global diablo
    speed = int(speed)
    with steelsquid_i2c.Lock():
        if diablo == None:
            diablo = Diablo.Diablo()
            diablo.Init()
            diablo.ResetEpo()
            diablo.SetMotor1(0)         
            diablo.SetMotor2(0)         
        speed = float(speed)/1000
        diablo.SetMotor2(speed)         


def callback_method(gpio, status):
    '''
    On event
    '''
    if status:
        print "GPIO " + str(gpio) + ": True" 
    else:
        print "GPIO " + str(gpio) + ": False"


def servo12c(servo, position, address=0x28):
    '''
    Move servo on a servos12c with I2C Servo Controller IC.
    http://www.hobbytronics.co.uk/arduino-servo-controller
    Servo: 0 to 11
    Position: 0 to 255
    '''
    servo = int(servo)
    position = int(position)
    steelsquid_i2c.write_8_bit(address, servo, position)


def mpu6050_init(address=0x69):
    '''
    Init the mpu-6050 
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    '''
    steelsquid_i2c.write_8_bit(address, 0x6b, 0)
    

def mpu6050_accel(address=0x69):
    '''
    Read mpu-6050 accelerometer data.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: (x, y, z)
    '''
    mpu6050_init(address)
    accel_xout = read_word_2c(address, 0x3b) / 16384.0
    accel_yout = read_word_2c(address, 0x3d) / 16384.0
    accel_zout = read_word_2c(address, 0x3f) / 16384.0
    return accel_xout, accel_yout, accel_zout


def mpu6050_movement(address=0x69):
    '''
    Read mpu-6050 gyro data.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: (x, y, z)
    '''
    mpu6050_init(address)
    gyro_xout = read_word_2c(address, 0x43) / 131
    gyro_xout = read_word_2c(address, 0x45) / 131
    gyro_zout = read_word_2c(address, 0x47) / 131
    return gyro_xout, gyro_xout, gyro_zout


def mpu6050_rotation(address=0x69):
    '''
    Read mpu-6050 rotation angle in degrees for both the X & Y.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: (x, y)
    '''
    accel_xout, accel_yout, accel_zout = mpu6050_accel(address)
    x = get_x_rotation(accel_xout, accel_yout, accel_zout)
    y = get_y_rotation(accel_xout, accel_yout, accel_zout)    
    return x, y


def mpu6050_temp(address=0x69):
    '''
    Read the temperatur from mpu-6050 gyro.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: temperatur in C
    '''
    mpu6050_init(address)
    return read_word_2c(address, 0x41) / 340.00+36.53


def mpu6050_movement_event(callback_method, min_change=10, sample_sleep=0.2):
    '''
    Listen for movements on mpu-6050 and execute method on change.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    def callback_method(x, y, z):
       ...do stuff
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    post = [None] * 3
    post[0] = 1  #mpu6050_movement_event
    post[1] = callback_method
    post[2] = min_change
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)


def mpu6050_rotation_event(callback_method, min_change=2, sample_sleep=0.2):
    '''
    Listen for mpu-6050 rotation angle in degrees for both the X & Y changes and execute method on change.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    def callback_method(x, y):
       ...do stuff
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    post = [None] * 3
    post[0] = 2  #mpu6050_rotation_event
    post[1] = callback_method
    post[2] = min_change
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)


def mpu6050_event_remove():
    '''
    Stop listen for movements on mpu-6050 and execute method on change.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    '''
    global event_notificatin_list
    with(lock_event):
        for i in xrange(len(event_notificatin_list) - 1, -1, -1):
            post = event_notificatin_list[i]
            if post[0]==2:
                del event_notificatin_list[i]


def event_notificatin_cleanup():
    '''
    Stop listen for notification on alot of stuff
    '''
    global event_notificatin_list
    with(lock_event):
        for i in xrange(len(event_notificatin_list) - 1, -1, -1):
            del event_notificatin_list[i]

    
def __event_notificatin_thread():
    '''
    This thread check for changes on stuff and execute method
    '''
    global event_notificatin_list
    global event_sample_sleep
    global event_last_mpu6050_movement
    global event_last_mpu6050_rotation
    while len(event_notificatin_list) != 0:
        try:
            for post in event_notificatin_list:
                type_of_event=post[0]
                callback_method = post[1]
                if type_of_event==1: #mpu6050_movement_event
                    min_change = post[2]
                    new_x, new_y, new_z = mpu6050_movement()
                    if event_last_mpu6050_movement == None:
                        event_last_mpu6050_movement = (new_x, new_y, new_z)
                        callback_method(new_x, new_y, new_z)
                    else:
                        old_x, old_y, old_z = event_last_mpu6050_movement
                        dif_x = abs(new_x-old_x)
                        dif_y = abs(new_y-old_y)
                        dif_z = abs(new_z-old_z)
                        if dif_x>=min_change or dif_y>=min_change or dif_z>=min_change:
                            event_last_mpu6050_movement = (new_x, new_y, new_z)
                            callback_method(new_x, new_y, new_z)
                elif type_of_event==2: #mpu6050_rotation_event
                    min_change = post[2]
                    new_x, new_y = mpu6050_rotation()
                    if event_last_mpu6050_rotation == None:
                        event_last_mpu6050_rotation = (new_x, new_y)
                        callback_method(new_x, new_y)
                    else:
                        old_x, old_y = event_last_mpu6050_rotation
                        dif_x = abs(new_x-old_x)
                        dif_y = abs(new_y-old_y)
                        if dif_x>=min_change or dif_y>=min_change:
                            event_last_mpu6050_rotation = (new_x, new_y)
                            callback_method(new_x, new_y)
                elif type_of_event==3: #po12_adc_event
                    min_change = post[2]
                    old_v = post[4]
                    samples = post[5]
                    new_v = po12_adc_volt(post[3], samples)
                    if old_v == None:
                        post[4] = new_v
                        callback_method(post[3], new_v)
                    else:
                        dif_v = abs(new_v-old_v)
                        if dif_v>=min_change:
                            post[4] = new_v
                            callback_method(post[3], new_v)
                elif type_of_event==4: #po16_gpio_event
                    gpio = post[2]
                    old_v = post[3]
                    new_v = po16_gpio_get(gpio)
                    if old_v == None or old_v!=new_v:
                        post[3] = new_v
                        callback_method(gpio, new_v)
                elif type_of_event==5: #po16_gpio_click
                    gpio = post[2]
                    old_v = post[3]
                    new_v = po16_gpio_get(gpio)
                    if old_v == None:
                        post[3] = new_v
                    elif old_v!=new_v:
                        post[3] = new_v
                        if new_v==True:
                            callback_method(gpio, new_v)
                elif type_of_event==6: #hcsr04_event
                    min_change = post[2]
                    old_v = post[3]
                    trig_gpio = post[4]
                    echo_gpio = post[5]
                    new_v = hcsr04_distance(trig_gpio, echo_gpio)
                    if old_v == None or old_v!=new_v:
                        post[3] = new_v
                        callback_method(new_v)
            time.sleep(event_sample_sleep)
        except:
            steelsquid_utils.shout()
            time.sleep(10)
    

def read_word(address, adr):
    high = steelsquid_i2c.read_8_bit(address, adr)
    low = steelsquid_i2c.read_8_bit(address, adr+1)
    val = (high << 8) + low
    return val


def read_word_2c(address, adr):
    val = read_word(address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
    

def dist(a,b):
    return math.sqrt((a*a)+(b*b))


def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)


def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
    

def po12_digital_out(channel, status): 
    '''
    Set the digital out channel to hight or low on the P011/12 ADC
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    channel = 1 to 3
    status = True/False
    '''
    channel = int(channel)
    if steelsquid_utils.to_boolean(status):
        steelsquid_i2c.write_bytes(0x34, 2, [channel, 1])
    else:
        steelsquid_i2c.write_bytes(0x34, 2, [channel, 0])


def po12_digital_out_flash(channel, status, seconds):
    '''
    Set a gpio hight or low on a P011/12 ADC
    Change to hight (true) or low (false) on a pin alternately
    @param gpio: channel 1 to 3
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("po12_digital_out_flash"+str(channel), status, seconds, po12_digital_out, (channel, True,), po12_digital_out, (channel, False,))


def po12_adc_pullup(use_pullup): 
    '''
    By default there are weak pull up resistors internally attached to the ADC lines
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    use_pullup = True/False
    '''
    if steelsquid_utils.to_boolean(use_pullup):
        steelsquid_i2c.write_bytes(0x34, 4, [1])
    else:
        steelsquid_i2c.write_bytes(0x34, 4, [0])


def po12_adc_vref(vref): 
    '''
    Set Reference Voltage
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    vref: 
        1.024
        2.048 
        4.096 
        else: Voltage on the +V pin
    '''
    global vref_voltage
    if vref!=None:
        vref = float(vref)
        vref_voltage = vref
    if vref == 1.024:
        cmd = 1
    elif vref == 2.048:
        cmd = 2
    elif vref == 4.096:
        cmd = 3
    else:
        cmd = 4
    steelsquid_i2c.write_bytes(0x34, 3, [cmd])
    
    
def __po12_adc(channel):
    global po12_adc_has_setup
    if not po12_adc_has_setup:
        po12_adc_has_setup=True
        po12_adc_pullup(False)
        time.sleep(0.01)
        po12_adc_vref(None)
        time.sleep(0.01)
    channel = int(channel)
    return steelsquid_i2c.read_16_bit_command(0x34, 1, [channel], little_endian=False)
    

def po12_adc(channel, samples=1):
    '''
    Read the analog value in on the P011/12 ADC
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    channel = 1 to 8
    samples = number of samples and then calculate median
    Return 0 to 1023
    '''
    if samples==1:
        return __po12_adc(channel)
    else:
        a_list=[]
        for i in range(samples):
            value =  __po12_adc(channel)
            a_list.append(value)
            time.sleep(0.01)
        return steelsquid_utils.median(a_list)


def po12_adc_volt(channel, samples=1):
    '''
    Read the analog voltage in on the P011/12 ADC
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    channel = 1 to 8
    Return 0V to vref
    '''
    value = po12_adc(channel, samples)
    calc = value/float(1023)
    return vref_voltage * calc


def po12_adc_event(channel, callback_method, min_change=0.01, sample_sleep=0.2, samples=1):
    '''
    Read the analog voltage in on the P011/12 ADC and execute method if it change
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    def callback_method(channel, voltage):
       ...do stuff
    channel = 1 to 8
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    post = [None] * 6
    channel = int(channel)
    post[0] = 3  #po12_adc_event
    post[1] = callback_method
    post[2] = min_change
    post[3] = channel
    post[4] = None
    post[5] = samples
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)


def po12_adc_event_remove(channel):
    '''
    Stop listen for analog voltage in on the P011/12 ADC and execute method if it change
    http://www.pichips.co.uk/index.php/P011_ADC#rpii2c
    channel = 1 to 8
     '''
    global event_notificatin_list
    channel = int(channel)
    with(lock_event):
        for i in xrange(len(event_notificatin_list) - 1, -1, -1):
            post = event_notificatin_list[i]
            if post[0]==3 and post[3] == channel:
                del event_notificatin_list[i]


def po16_gpio_pullup(gpio, use_pullup): 
    '''
    Sets a weak pull up on the specified pin on the PO16
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    gpio 1 t to 8
    '''
    gpio = int(gpio)
    use_pullup = steelsquid_utils.to_boolean(use_pullup)
    if use_pullup:
        steelsquid_i2c.write_bytes(0x36, 2, [gpio, 1])
    else:
        steelsquid_i2c.write_bytes(0x36, 2, [gpio, 1])


def po16_gpio_get(gpio): 
    '''
    Read the state of gpio pin on the PO16
    This will return true if the gpio is connectid to ground
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    gpio 1 t to 8
    '''
    gpio = int(gpio)
    if not po16_setup[gpio-1] == SETUP_IN:
        po16_setup[gpio-1] = SETUP_IN
        steelsquid_i2c.write_bytes(0x36, 1, [gpio, 1])
    by = steelsquid_i2c.read_bytes_command(0x36, 6, [gpio], 1)
    if by[0]==1:
        return True
    else:
        return False
    

def po16_gpio_event(gpio, callback_method, sample_sleep=0.2):
    '''
    Read the Read the state of gpio pin on the PO16 and execute method if it change
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    def callback_method(gpio, status):
       ...do stuff
    gpio = 1 to 8
    callback_method: Execute this method on change
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    post = [None] * 4
    post[0] = 4  #po16_gpio_event
    post[1] = callback_method
    post[2] = gpio
    post[3] = None
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)
    

def po16_gpio_click(gpio, callback_method, sample_sleep=0.2):
    '''
    Read the Read the state of gpio pin on the PO16 and execute method if it change from low to hight (click)
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    def callback_method(gpio):
       ...do stuff
    gpio = 1 to 8
    callback_method: Execute this method on click
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    global event_notificatin_list
    global event_sample_sleep
    event_sample_sleep = sample_sleep
    gpio = int(gpio)
    post = [None] * 4
    post[0] = 5  #po16_gpio_click
    post[1] = callback_method
    post[2] = gpio
    post[3] = None
    with(lock_event):
        if len(event_notificatin_list) == 0: 
            event_notificatin_list.append(post)
            thread.start_new_thread(__event_notificatin_thread, ()) 
        else:
            event_notificatin_list.append(post)
    
    
def po16_gpio_event_remove(gpio):
    '''
    Stop listen for the state of gpio pin on the PO16 and execute method if it change from low to hight (click)
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    gpio = 1 to 8
     '''
    global event_notificatin_list
    gpio = int(gpio)
    with(lock_event):
        for i in xrange(len(event_notificatin_list) - 1, -1, -1):
            post = event_notificatin_list[i]
            if post[0]==5 and post[2]==gpio:
                del event_notificatin_list[i]
    

def po16_gpio_set(gpio, status): 
    '''
    Set the state of gpio pin on the PO16
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    gpio = 0 t to 8
    status = Treu/False
    '''
    gpio = int(gpio)
    status = steelsquid_utils.to_boolean(status)
    if not po16_setup[int(gpio-1)] == SETUP_OUT:
        po16_setup[int(gpio-1)] = SETUP_OUT
        steelsquid_i2c.write_bytes(0x36, 1, [gpio, 0])
    if steelsquid_utils.to_boolean(status):
        steelsquid_i2c.write_bytes(0x36, 5, [gpio, 1])
    else:
        steelsquid_i2c.write_bytes(0x36, 5, [gpio, 0])


def po16_gpio_flash(gpio, status, seconds):
    '''
    Set a gpio hight or low on a PO16
    Change to hight (true) or low (false) on a pin alternately
    @param gpio: channel 0 to 8
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("po16_gpio_flash"+str(gpio), status, seconds, po16_gpio_set, (gpio, True,), po16_gpio_set, (gpio, False,))


def po16_pwm(channel, value): 
    '''
    Set PWM value on channel on the PO16
    http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM
    channel = 1 to 4
    value = 0 to 1023
    '''
    channel = int(channel)
    value = int(value)
    steelsquid_i2c.write_bytes(0x36, 7, [channel, steelsquid_utils.get_hight_byte(value), steelsquid_utils.get_low_byte(value)])


def pcf8591_read(pin, address=0x48): 
    '''
    Read analog value from pcf8591
    http://dx.com/p/pcf8591-8-bit-a-d-d-a-converter-module-150190
    pin = 0 to 3
    return 0 to 255
    '''
    pin = int(pin)
    if pin==0:
        steelsquid_i2c.write_8_bit_raw(address, 0x40)
    elif pin==1:
        steelsquid_i2c.write_8_bit_raw(address, 0x41)
    elif pin==2:
        steelsquid_i2c.write_8_bit_raw(address, 0x42)
    else:
        steelsquid_i2c.write_8_bit_raw(address, 0x43)
    steelsquid_i2c.read_8_bit_raw(address)
    return steelsquid_i2c.read_8_bit_raw(address)


def pcf8591_write(value, address=0x48): 
    '''
    Set analog out value on pcf8591
    http://dx.com/p/pcf8591-8-bit-a-d-d-a-converter-module-150190
    value = 0 to 255
    '''
    value = int(value)
    steelsquid_i2c.write_8_bit(address, 0x40, value)


def yl40_light_level(address=0x48): 
    '''
    Read light level from YL-40 sensor (pcf8591)
    Just invert the scale to 0 to 255
    http://dx.com/p/pcf8591-8-bit-a-d-d-a-converter-module-150190
    return 0=dark  -->  255=super bright
    '''
    steelsquid_i2c.write_8_bit_raw(address, 0x40)
    steelsquid_i2c.read_8_bit_raw(address)
    value = steelsquid_i2c.read_8_bit_raw(address)
    value = (value-255)*-1
    return value
        

def hdc1008(address=0x40): 
    '''
    Read Temperature + Humidity from HDC1008
    Return tuple with Temperature and Humidity
    '''
    steelsquid_i2c.write_bytes(address, 0x02, [0x02, 0x00])
    time.sleep(0.015)
    steelsquid_i2c.write_8_bit_raw(address, 0x00)
    time.sleep(0.0625)
    b1 = steelsquid_i2c.read_8_bit_raw(address)
    b2 = steelsquid_i2c.read_8_bit_raw(address)
    temp = ((((b1<<8) + (b2))/65536.0)*165.0 ) - 40.0   
    time.sleep(0.015)
    steelsquid_i2c.write_8_bit_raw(address, 0x01)
    time.sleep(0.0625)
    b1 = steelsquid_i2c.read_8_bit_raw(address)
    b2 = steelsquid_i2c.read_8_bit_raw(address)
    hum = (((b1<<8) + (b2))/65536.0)*100.0
    return temp, hum


def gpio_event_callback_method(pin, status): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Pin" + str(pin) + " = " + str(status))


def mcp_event_callback_method(address, pin, status): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Address " + str(address) + ", Pin" + str(pin) + " = " + str(status))
    
    
if __name__ == '__main__':
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        printb("IO commands for Steelsquid Kiss OS. Commands to get/set gpio and other stuff...")
        print("This is mostly for test purpuse, all logic should be made in the Steelsquid daemon")
        print("(e.g. kiss_expand.py...)")
        print("This may interrupt for example the LCD, DAC, ADC...(this is only for test)")
        print("")
        printb("pi gpio_get <gpio>")
        print("Get status of RaspberryPI GPIO")
        print("gpio: 4-26")
        print("")
        printb("pi gpio_set <gpio> <true/false>")
        print("Set status of RaspberryPI GPIO")
        print("gpio: 4-26")
        print("")
        printb("pi d gpio_event <gpio>")
        print("Listen for changes on RaspberryPI GPIO")
        print("gpio: 4-26")
        print("")
        printb("pi mcp23017_get <address> <gpio>")
        print("Get status gpio on a MCP23017")
        print("Connect GPIO to gnd (using internal pull-up)")
        print("address: 20-27")
        print("gpio: 0-15")
        print("")
        printb("pi mcp23017_set <address> <gpio> <true/false>")
        print("Set a gpio hight or low on a MCP23017")
        print("address: 20-27")
        print("gpio: 0-15")
        print("")
        printb("pi d mcp23017_event <address> <gpio>")
        print("Listen for changes on MCP23017 pin")
        print("Connect GPIO to gnd (using internal pull-up)")
        print("If this is to work one of the trigger pin needs to be connected to raspberry Pi pin 26")
        print("address: 20-27")
        print("gpio: 0-15")
        print("")
        printb("pi ads1015 <address> <gpio>")
        print("Read analog in from ADS1015 (0 to 5 v)")
        print("address: 48, 49, 4A, 4B ")
        print("gpio: 0-3")
        print("")
        printb("pi mcp4725 <address> <value>")
        print("Write analog out from MCP4725")
        print("address: 60 ")
        print("value: 0 and 4095")
        print("")
        printb("pi mcp4728 <address> <volt0> <volt1> <volt2> <volt3>")
        print("Write analog out from MCP4728")
        print("address: 61")
        print("volt0-3: 0 and 4095")
        print("")
        printb("pi hdd44780 <is_i2c> <text>")
        print("Print text to HDD44780 compatible LCD (\n or \\ = new line)")
        print("is_i2c: Is the LCD connected by I2C (true/false)")
        print("")
        printb("pi nokia5110 <text>")
        print("Print text to nokia5110  LCD (\n or \\ = new line)")
        print("")
        printb("pi ssd1306 <text>")
        print("Print text to ssd1306 oled LCD (\n or \\ = new line)")
        print("")
        printb("pi hcsr04 <trig_gpio> <echo_gpio>")
        print("Measure_distance with a with HC-SR04.")
        print("trig_gpio: The trig gpio")
        print("echo_gpio: The echo gpio")
        print("")
        printb("pi pca9685 <servo> <value>")
        print("Move Adafruit 16-channel I2c servo to position (pwm value).")
        print("servo: 0 to 15")
        print("value: min=150, max=600 (may differ between servos)")
        print("")
        printb("pi sabertooth <port> <left> <right>")
        print("Set the speed on a sabertooth dc motor controller..")
        print("port: /dev/ttyAMA0, the_port=/dev/ttyUSB0")
        print("left and right: -100% to +100%")
        print("")
        printb("pi trex_motor <left> <right>")
        print("Set TREX speed of the dc motors")
        print("left and right: -255 to 255")
        print("")
        printb("pi trex_servo <servo> <position>")
        print("Set TREX servo position")
        print("servo: 1 to 6")
        print("Position: Typically the servo position should be a value between 1000 and 2000 although it will vary depending on the servos used")
        print("")
        printb("pi trex_status")
        print("Get status from trex")
        print(" - Battery voltage:   An integer that is 100x the actual voltage")
        print(" - Motor current:  Current drawn by the motor in mA")
        print(" - Accelerometer")
        print(" - Impact")
        print("")
        printb("pi diablo <left> <right>")
        print("Drive Piborg diablo motor board")
        print("left and right: -1000 to 1000")
        print("")
        printb("pi servo12c <servo> <position>")
        print("Move servo on a 12 servos with I2C Servo Controller IC.")
        print("http://www.hobbytronics.co.uk/arduino-servo-controller")
        print("Servo: 0 to 11")
        print("Position: 0 to 255")
        print("")
        printb("pi mpu6050_accel")
        print("Read mpu-6050 accelerometer data.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi mpu6050_movement")
        print("Read mpu-6050 gyro data.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi mpu6050_rotation")
        print("Read mpu-6050 rotation angle in degrees for both the X & Y.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi d mpu6050_movement_event")
        print("Listen for movements on mpu-6050 and execute method on change.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi d mpu6050_rotation_event")
        print("Listen for mpu-6050 rotation angle in degrees and execute method on change.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi po12_digital_out <channel> <status>")
        print("Set the digital out channel to hight or low on the P011/12 ADC")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("channel = 1 to 3")
        print("status = True/False")
        print("")
        printb("pi po12_adc_pullup <enable>")
        print("By default there are weak pull up resistors internally attached to the ADC lines")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("enable = true/false")
        print("")
        printb("pi po12_adc_vref <vref>")
        print("Set Reference Voltage")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("vref = 1.024")
        print("       2.048")
        print("       4.096")
        print("       Voltage on the +V pin")
        print("")
        printb("pi po12_adc <channel>")
        print("Read the analog value in on the P011/12 ADC")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("channel = 1 to 8")
        print("Return: 0 to 1023")
        print("")
        printb("pi po12_adc_volt <channel>")
        print("Read the analog voltage in on the P011/12 ADC")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("channel = 1 to 8")
        print("Return: 0V to vref")
        print("")
        printb("pi d po12_adc_event <channel>")
        print("Make method execute when the analog voltage in on the P011/12 ADC change")
        print("http://www.pichips.co.uk/index.php/P011_ADC#rpii2c")
        print("channel = 1 to 8")
        print("")
        printb("pi po16_gpio_pullup <gpio> <use_pullup>")
        print("Sets a weak pull up on the specified pin on the PO16")
        print("http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM")
        print("gpio = 1 to 8")
        print("use_pullup: True/False")
        print("")
        printb("pi po16_gpio_get <gpio>")
        print("Read the state of gpio pin on the PO16")
        print("This will return true if the gpio is connectid to ground")
        print("http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM")
        print("gpio = 1 to 8")
        print("Return: True/False")
        print("")
        printb("pi d po16_gpio_event <gpio>")
        print("Make method execute when state of gpio pin on the PO16 change")
        print("Set the state of gpio pin on the PO16")
        print("gpio = 1 to 8")
        print("")
        printb("pi po16_gpio_set <gpio> <status>")
        print("Set the state of gpio pin on the PO16")
        print("http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM")
        print("gpio = 1 to 8")
        print("status = True/False")
        print("")
        printb("pi po16_pwm <channel> <value>")
        print("Set PWM value on channel on the PO16")
        print("http://www.pichips.co.uk/index.php/P015_GPIO_with_PWM")
        print("channel = 1 to 4")
        print("value = 0 to 1023")
        print("")
        printb("pi pcf8591_read <pin>")
        print("Read analog value from pcf8591")
        print("http://dx.com/p/pcf8591-8-bit-a-d-d-a-converter-module-150190")
        print("pin = 0 to 3")
        print("")
        printb("pi pcf8591_write <value>")
        print("Set analog out value on pcf8591")
        print("http://dx.com/p/pcf8591-8-bit-a-d-d-a-converter-module-150190")
        print("value = 0 to 255")
        print("")
        printb("pi hdc1008")
        print("Read Temperature + Humidity from HDC1008")
        print("https://learn.adafruit.com/adafruit-hdc1008-temperature-and-humidity-sensor-breakout/overview")
        print("Temperatur in celsius and humidity in %")
    else:
        command = sys.argv[1]
        if len(sys.argv)>2:
            para1 = sys.argv[2]
        if len(sys.argv)>3:
            para2 = sys.argv[3]
        if len(sys.argv)>4:
            para3 = sys.argv[4]
        if len(sys.argv)>5:
            para4 = sys.argv[5]
        if len(sys.argv)>6:
            para5 = sys.argv[6]
        if command == "gpio_get":
            print gpio_get(para1)
        elif command == "gpio_set":
            gpio_set(para1, steelsquid_utils.to_boolean(para2))
        elif command == "gpio_event":
            gpio_event(para1, gpio_event_callback_method)
            raw_input("Press any key to exit!")
        elif command == "mcp23017_get":
            print mcp23017_get(para1, para2)
        elif command == "mcp23017_set":
            mcp23017_set(para1, para2, steelsquid_utils.to_boolean(para3))
        elif command == "mcp23017_event":
            mcp23017_event(para1, para2, mcp_event_callback_method)
            raw_input("Press any key to exit!")
        elif command == "ads1015":
            print ads1015(para1, para2)
        elif command == "mcp4725":
            mcp4725(para1, para2)
        elif command == "mcp4728":
            mcp4728(para1, para2, para3, para4, para5)
        elif command == "hdd44780":
            if steelsquid_utils.to_boolean(para1):
                hdd44780_write(para2, number_of_seconds = 10, is_i2c=True)
            else:
                hdd44780_write(para2, number_of_seconds = 10, is_i2c=False)
        elif command == "nokia5110":
            nokia5110_write(para1, number_of_seconds = 10)
        elif command == "ssd1306":
            ssd1306_write(para1, number_of_seconds = 10)
        elif command == "hcsr04":
            print hcsr04_distance(para1, para2)
        elif command == "pca9685":
            pca9685_move(para1, para2)
        elif command == "sabertooth":
            sabertooth_motor_speed(para2, para3, para1)
        elif command == "trex_motor":
            trex_motor(para1, para2)
        elif command == "trex_servo":
            trex_servo(para1, para2)
        elif command == "trex_status":
            battery_voltage, left_motor_current, right_motor_current, accelerometer_x, accelerometer_y, accelerometer_z, impact_x, impact_y, impact_z = trex_status()
            answer = []
            answer.append("battery_voltage: ")
            answer.append(str(battery_voltage))
            answer.append("\n")
            answer.append("left_motor_current: ")
            answer.append(str(left_motor_current))
            answer.append("\n")
            answer.append("right_motor_current: ")
            answer.append(str(right_motor_current))
            answer.append("\n")
            answer.append("accelerometer_x: ")
            answer.append(str(accelerometer_x))
            answer.append("\n")
            answer.append("accelerometer_y: ")
            answer.append(str(accelerometer_y))
            answer.append("\n")
            answer.append("accelerometer_z: ")
            answer.append(str(accelerometer_z))
            answer.append("\n")
            answer.append("impact_x: ")
            answer.append(str(impact_x))
            answer.append("\n")
            answer.append("impact_y: ")
            answer.append(str(impact_y))
            answer.append("\n")
            answer.append("impact_z: ")
            answer.append(str(impact_z))
            print "".join(answer)
        elif command == "diablo":
            diablo_motor_1(para1)
            diablo_motor_2(para2)
        elif command == "servo12c":
            servo12c(para1, para2)
        elif command == "mpu6050_accel":
            print mpu6050_accel()
        elif command == "mpu6050_movement":
            print mpu6050_movement()
        elif command == "mpu6050_rotation":
            print mpu6050_rotation()
        elif command == "mpu6050_movement_event":
            def movment_change(x, y, z):
                sys.stdout.write("X="+str(x).ljust(8)+"Y="+str(y).ljust(8)+"Z="+str(z).ljust(8) + "\r")
                sys.stdout.flush()
            mpu6050_movement_event(movment_change)
            raw_input()
        elif command == "mpu6050_rotation_event":
            def rotation_changed(x, y):
                sys.stdout.write("X="+str(x).ljust(20)+"Y="+str(y).ljust(20) + "\r")
                sys.stdout.flush()
            mpu6050_rotation_event(rotation_changed)
            raw_input()
        elif command == "po12_digital_out":
            po12_digital_out(para1, para2)
        elif command == "po12_adc_pullup":
            po12_adc_pullup(para1)
        elif command == "po12_adc_vref":
            po12_adc_vref(para1)
        elif command == "po12_adc":
            print po12_adc(para1)
        elif command == "po12_adc_volt":
            print po12_adc_volt(para1)
        elif command == "po12_adc_event":
            def on_change(channel, voltage):
                sys.stdout.write("Voltage="+str(voltage).ljust(20) + "\r")
                sys.stdout.flush()
            po12_adc_event(para1, on_change)
            raw_input()                
        elif command == "po16_gpio_pullup":
            po16_gpio_pullup(para1, para2)
        elif command == "po16_gpio_get":
            print po16_gpio_get(para1)
        elif command == "po16_gpio_event":
            def on_change(gpio, value):
                sys.stdout.write(gpio + "="+str(value).ljust(10) + "\r")
                sys.stdout.flush()
            po16_gpio_event(para1, on_change)
            raw_input()                
        elif command == "po16_gpio_set":
            po16_gpio_set(para1, para2)
        elif command == "po16_pwm":
            po16_pwm(para1, para2)
        elif command == "pcf8591_read":
            print pcf8591_read(para1)
        elif command == "pcf8591_write":
            pcf8591_write(para1)
        elif command == "hdc1008":
            temp, hum = hdc1008()
            print "Temperature: " + str(round(temp, 1)) + "C\nHumidity: " + str(round(hum, 1)) + "%"
        else:
            print "Unknown command!!!"
            
    

