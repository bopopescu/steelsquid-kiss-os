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


import sys
import RPi.GPIO as GPIO
import time
import os
import steelsquid_utils
import threading
import thread
from Adafruit_PWM_Servo_Driver import PWM
import Adafruit_MCP230xx
import thread
import signal
from Adafruit_ADS1x15 import ADS1x15
from Adafruit_MCP4725 import MCP4725
from Adafruit_I2C import Adafruit_I2C
import steelsquid_trex
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from sets import Set
import Diablo
import steelsquid_event
import smbus
import math

SETUP_NONE = 0
SETUP_OUT = 1
SETUP_IN = 2
SETUP_IN_3V3 = 3
SETUP_IN_GND = 4
TIMEOUT = 2100
setup = [SETUP_NONE] * 32
lcd = None
toggle = [False] * 32
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
lcd_last_text = ""
lock = threading.Lock()
distance_created = False
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
toggle_mcp = []
sabertooth = None
dac = None
mcp4728_i2c = None
lock_rbada = threading.Lock()
lock_sabertooth = threading.Lock()
lock_hcsr04 = threading.Lock()
lock_ads1015_48 = threading.Lock()
lock_ads1015_49 = threading.Lock()
lock_ads1015_4A = threading.Lock()
lock_ads1015_4B = threading.Lock()
lock_mcp4725 = threading.Lock()
lock_mcp4728 = threading.Lock()
DC = 9
RST = 7
SPI_PORT = 0
SPI_DEVICE = 0
nokia_lcd = None
font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro.ttf", 10)
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
draw = ImageDraw.Draw(image)
lcd_auto = 0
worker_commands = {}
worker_thread_started = False
diablo = None
i2c_servo12c = None
i2c_mpu_6050 = None



def worker_thread():
    global worker_commands
    try:
        while True:
            for work_key in worker_commands.keys():
                try:
                    work = worker_commands[work_key]
                    command = work[0]
                    if command == "gpio_flash_3v3":
                        only_one = work[1]
                        gpio = work[2]
                        if only_one == None:
                            gpio_toggle_3v3(gpio)
                        elif only_one:
                            gpio_set_3v3(gpio, True)
                            work[1] = False
                        else:
                            gpio_set_3v3(gpio, False)
                            worker_commands.pop(work_key, None)
                    elif command == "gpio_flash_gnd":
                        only_one = work[1]
                        gpio = work[2]
                        if only_one == None:
                            gpio_toggle_gnd(gpio)
                        elif only_one:
                            gpio_set_gnd(gpio, True)
                            work[1] = False
                        else:
                            gpio_set_gnd(gpio, False)
                            worker_commands.pop(work_key, None)
                    elif command == "mcp23017_flash":
                        only_one = work[1]
                        address = work[2]
                        gpio = work[3]
                        if only_one == None:
                            mcp23017_toggle(address, gpio)
                        elif only_one:
                            mcp23017_set(address, gpio, True)
                            work[1] = False
                        else:
                            mcp23017_set(address, gpio, False)
                            worker_commands.pop(work_key, None)
                    elif command == "mcp23017_click":
                        address = work[1]
                        gpio = work[2]
                        mcp = work[3]
                        cal_m = work[4]
                        #last = work[5]
                        if(mcp.input(gpio) >> gpio)==0:
                            work[5] = True
                        else:
                            if work[5] == True:
                                try:
                                    cal_m(address, gpio)
                                except:
                                    steelsquid_utils.shout("Error: mcp23017_click", is_error=True, always_show=True)
                                work[5] = False
                    elif command == "mcp23017_event":
                        address = work[1]
                        gpio = work[2]
                        mcp = work[3]
                        cal_m = work[4]
                        #last = work[5]
                        if(mcp.input(gpio) >> gpio)==0:
                            if work[5] == False:
                                try:
                                    cal_m(address, gpio, True)
                                except:
                                    steelsquid_utils.shout("Error: mcp23017_event", is_error=True, always_show=True)
                            work[5] = True
                        else:
                            if work[5] == True:
                                try:
                                    cal_m(address, gpio, False)
                                except:
                                    steelsquid_utils.shout("Error: mcp23017_event", is_error=True, always_show=True)
                            work[5] = False
                    elif command == "ads1015_event":
                        address = work[1]
                        gpio = work[2]
                        ads = work[3]
                        cal_m = work[4]
                        #last = work[5]
                        gain = work[6]
                        newv = ads.readADCSingleEnded(gpio, gain, 250) / 1000
                        if newv != work[5]:
                            try:
                                cal_m(address, gpio, newv)
                            except:
                                steelsquid_utils.shout("Error: ads1015_event", is_error=True, always_show=True)
                            work[5] = newv
                except:
                    worker_commands.pop(work_key, None)
                    steelsquid_utils.shout("Fatal error in steelsquid_pi worker thread: " +work_key, is_error=True)
            time.sleep(0.3)
    except AttributeError:
        pass
            

if worker_thread_started == False:
    worker_thread_started = True
    thread.start_new_thread(worker_thread, ())


def cleanup():
    '''
    Clean all event detection (click, blink...)
    '''
    gpio_cleanup()
    worker_thread.clear()
    

def gpio_event_remove(gpio):
    '''
    Remove listening for input event
    @param gpio: GPIO number
    '''
    GPIO.remove_event_detect(gpio)


def gpio_cleanup():
    '''
    cleanup
    '''
    global setup
    GPIO.remove_event_detect(channel)
    setup = [SETUP_NONE] * 32    
    GPIO.cleanup()


def gpio_setup_out(gpio):
    '''
    set gpio pin to output mode
    @param gpio: GPIO number
    '''
    global setup
    GPIO.setup(int(gpio), GPIO.OUT)
    setup[int(gpio)] == SETUP_OUT


def gpio_setup_in_3v3(gpio):
    '''
    set gpio pin to input mode (connect gpio to 3.3v)
    @param gpio: GPIO number
    '''
    global setup
    GPIO.setup(int(gpio), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    setup[int(gpio)] == SETUP_IN_3V3


def gpio_setup_in_gnd(gpio):
    '''
    set gpio pin to input mode (connect gpio to ground)
    @param gpio: GPIO number
    '''
    global setup
    GPIO.setup(int(gpio), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    setup[int(gpio)] == SETUP_IN_GND


def gpio_set(gpio, state):
    '''
    set gpio pin to already configured pin
    @param gpio: GPIO number
    @param state: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    GPIO.output(int(gpio), state)


def gpio_get(gpio):
    '''
    Get gpio pin state from already configured pin
    @param gpio: GPIO number
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    return GPIO.input(int(gpio))


def gpio_set_3v3(gpio, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to 3.3v
    @param gpio: GPIO number
    @param state: True/False
    '''
    global setup
    if not setup[int(gpio)] == SETUP_OUT:
        gpio_setup_out(gpio)
    GPIO.output(int(gpio), not state)


def gpio_set_gnd(gpio, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to ground
    @param gpio: GPIO number
    @param state: True/False
    '''
    global setup
    if not setup[int(gpio)] == SETUP_OUT:
        gpio_setup_out(gpio)
    GPIO.output(int(gpio), state)


def gpio_get_3v3(gpio):
    '''
    Get gpio pin state (connect gpio to 3.3v)
    @param gpio: GPIO number
    @return: True/False
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_3V3:
        gpio_setup_in_3v3(gpio)
    if GPIO.input(int(gpio)) == 1:
        return True
    else:
        return False


def gpio_get_gnd(gpio):
    '''
    Get gpio pin state
    @param gpio: GPIO number
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_GND:
        gpio_setup_in_gnd(gpio)
    if GPIO.input(int(gpio)) == 1:
        return False
    else:
        return True


def gpio_toggle_3v3(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to 3.3v
    @param gpio: GPIO number
    '''
    global toggle
    if toggle[gpio] == True:
        toggle[gpio] = False
        gpio_set_3v3(gpio, False)
        return False
    else:
        toggle[gpio] = True
        gpio_set_3v3(gpio, True)
        return True


def gpio_toggle_current_3v3(gpio):
    '''
    Get current togle status
    '''
    global toggle
    return toggle[gpio]


def gpio_toggle_gnd(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to gnd
    @param gpio: GPIO number
    '''
    global toggle
    if toggle[gpio] == True:
        toggle[gpio] = False
        gpio_set_gnd(gpio, False)
        return False
    else:
        toggle[gpio] = True
        gpio_set_gnd(gpio, True)
        return True


def gpio_toggle_current_gnd(gpio):
    '''
    Get current togle status
    '''
    global toggle
    return toggle[gpio]


def gpio_event_3v3(gpio, callback_method):
    '''
    Listen for events on gpio pin and 3.3v
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_3V3:
        gpio_setup_in_3v3(gpio)
    def call_met(para):
        status = gpio_get_3v3(para)
        try:
            callback_method(para, status)          
        except:
            steelsquid_utils.shout()
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_event_gnd(gpio, callback_method):
    '''
    Listen for events on gpio pin and ground
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_GND:
        gpio_setup_in_gnd(gpio)
    def call_met(para):
        status = gpio_get_gnd(para)
        try:
            callback_method(para, status)          
        except:
            steelsquid_utils.shout()
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_click_3v3(gpio, callback_method):
    '''
    Connect a button to gpio pin and 3.3v
    Will fire when button is released. If press more than 1s it will be ignore
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_3V3:
        gpio_setup_in_3v3(gpio)
    def call_met(para):
        global down
        global up
        status = gpio_get_3v3(para)
        if status == True:
            up = -1
            down = time.time()            
        else:
            if down != -1:
                up = time.time()        
                delta = up - down        
                down = -1
                up = -1
                delta =  int(delta * 1000)
                if delta > 100 and delta < 1000:
                    try:
                        callback_method(para)
                    except:
                        steelsquid_utils.shout()
            else:
                up = -1
    global down
    global up
    down = -1
    up = -1
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_click_gnd(gpio, callback_method):
    '''
    Connect a button to gpio pin and ground
    Will fire when button is released. If press more than 1s it will be ignore
    @param gpio: GPIO number
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_GND:
        gpio_setup_in_gnd(gpio)
    def call_met(para):
        global down
        global up
        status = gpio_get_gnd(para)
        if status == True:
            up = -1
            down = time.time()            
        else:
            if down != -1:
                up = time.time()        
                delta = up - down        
                down = -1
                up = -1
                delta =  int(delta * 1000)
                if delta > 100 and delta < 1000:
                    try:
                        callback_method(para)
                    except:
                        steelsquid_utils.shout()                        
            else:
                up = -1
    global down
    global up
    down = -1
    up = -1
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_flash_3v3(gpio, enable):
    '''
    Flash a gpio on and off connected to 3.3v

    @param gpio: The gpio to flash
    @param enable: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    command = "gpio_flash_3v3"
    key = command + str(gpio)
    if enable == None or enable:
        post = [None] * 3
        post[0] = command
        if enable:
            post[1] = False
        else:
            post[1] = True
        post[2] = gpio
        worker_commands[key] = post
    else:
        worker_commands.pop(key, None)
        toggle[gpio] = False
        gpio_set_3v3(gpio, False)
    
    
def gpio_flash_gnd(gpio, enable):
    '''
    Flash a gpio on and off connected to ground

    @param gpio: The gpio to flash
    @param enable: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    command = "gpio_flash_gnd"
    key = command + str(gpio)
    if enable == None or enable:
        post = [None] * 3
        post[0] = command
        if enable:
            post[1] = False
        else:
            post[1] = True
        post[2] = gpio
        worker_commands[key] = post
    else:
        worker_commands.pop(key, None)
        toggle[gpio] = False
        gpio_set_gnd(gpio, False)


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
            mcp_20 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 16)
        if mcp_setup_20[gpio] != SETUP_OUT:
            mcp_setup_20[gpio] == SETUP_OUT
            mcp_20.pullup(gpio, 0)
            mcp_20.config(gpio, mcp_20.OUTPUT)
        return mcp_20
    elif address == 21:
        global mcp_21
        if mcp_21 == None:
            mcp_21 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x21, num_gpios = 16)
        if mcp_setup_21[gpio] != SETUP_OUT:
            mcp_setup_21[gpio] == SETUP_OUT
            mcp_21.pullup(gpio, 0)
            mcp_21.config(gpio, mcp_21.OUTPUT)
        return mcp_21
    elif address == 22:
        global mcp_22
        if mcp_22 == None:
            mcp_22 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x22, num_gpios = 16)
        if mcp_setup_22[gpio] != SETUP_OUT:
            mcp_setup_22[gpio] == SETUP_OUT
            mcp_22.pullup(gpio, 0)
            mcp_22.config(gpio, mcp_22.OUTPUT)
        return mcp_22
    elif address == 23:
        global mcp_23
        if mcp_23 == None:
            mcp_23 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x23, num_gpios = 16)
        if mcp_setup_23[gpio] != SETUP_OUT:
            mcp_setup_23[gpio] == SETUP_OUT
            mcp_23.pullup(gpio, 0)
            mcp_23.config(gpio, mcp_23.OUTPUT)
        return mcp_23
    elif address == 24:
        global mcp_24
        if mcp_24 == None:
            mcp_24 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x24, num_gpios = 16)
        if mcp_setup_24[gpio] != SETUP_OUT:
            mcp_setup_24[gpio] == SETUP_OUT
            mcp_24.pullup(gpio, 0)
            mcp_24.config(gpio, mcp_24.OUTPUT)
        return mcp_24
    elif address == 25:
        global mcp_25
        if mcp_25 == None:
            mcp_25 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x25, num_gpios = 16)
        if mcp_setup_25[gpio] != SETUP_OUT:
            mcp_setup_25[gpio] == SETUP_OUT
            mcp_25.pullup(gpio, 0)
            mcp_25.config(gpio, mcp_25.OUTPUT)
        return mcp_25
    elif address == 26:
        global mcp_26
        if mcp_26 == None:
            mcp_26 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x26, num_gpios = 16)
        if mcp_setup_26[gpio] != SETUP_OUT:
            mcp_setup_26[gpio] == SETUP_OUT
            mcp_26.pullup(gpio, 0)
            mcp_26.config(gpio, mcp_26.OUTPUT)
        return mcp_26
    elif address == 27:
        global mcp_27
        if mcp_27 == None:
            mcp_27 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x27, num_gpios = 16)
        if mcp_setup_27[gpio] != SETUP_OUT:
            mcp_setup_27[gpio] == SETUP_OUT
            mcp_27.pullup(gpio, 0)
            mcp_27.config(gpio, mcp_27.OUTPUT)
        return mcp_27


def mcp23017_setup_in(address, gpio):
    '''
    Set MCP23017 as input
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 h7as 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    if address == 20:
        global mcp_20
        if mcp_20 == None:
            mcp_20 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 16)
        if mcp_setup_20[gpio] != SETUP_IN:
            mcp_setup_20[gpio] == SETUP_IN
            mcp_20.config(gpio, mcp_20.INPUT)
            mcp_20.pullup(gpio, 1)
        return mcp_20
    elif address == 21:
        global mcp_21
        if mcp_21 == None:
            mcp_21 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x21, num_gpios = 16)
        if mcp_setup_21[gpio] != SETUP_IN:
            mcp_setup_21[gpio] == SETUP_IN
            mcp_21.config(gpio, mcp_21.INPUT)
            mcp_21.pullup(gpio, 1)
        return mcp_21
    elif address == 22:
        global mcp_22
        if mcp_22 == None:
            mcp_22 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x22, num_gpios = 16)
        if mcp_setup_22[gpio] != SETUP_IN:
            mcp_setup_22[gpio] == SETUP_IN
            mcp_22.config(gpio, mcp_22.INPUT)
            mcp_22.pullup(gpio, 1)
        return mcp_22
    elif address == 23:
        global mcp_23
        if mcp_23 == None:
            mcp_23 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x23, num_gpios = 16)
        if mcp_setup_23[gpio] != SETUP_IN:
            mcp_setup_23[gpio] == SETUP_IN
            mcp_23.config(gpio, mcp_23.INPUT)
            mcp_23.pullup(gpio, 1)
        return mcp_23
    elif address == 24:
        global mcp_24
        if mcp_24 == None:
            mcp_24 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x24, num_gpios = 16)
        if mcp_setup_24[gpio] != SETUP_IN:
            mcp_setup_24[gpio] == SETUP_IN
            mcp_24.config(gpio, mcp_24.INPUT)
            mcp_24.pullup(gpio, 1)
        return mcp_24
    elif address == 25:
        global mcp_25
        if mcp_25 == None:
            mcp_25 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x25, num_gpios = 16)
        if mcp_setup_25[gpio] != SETUP_IN:
            mcp_setup_25[gpio] == SETUP_IN
            mcp_25.config(gpio, mcp_25.INPUT)
            mcp_25.pullup(gpio, 1)
        return mcp_25
    elif address == 26:
        global mcp_26
        if mcp_26 == None:
            mcp_26 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x26, num_gpios = 16)
        if mcp_setup_26[gpio] != SETUP_IN:
            mcp_setup_26[gpio] == SETUP_IN
            mcp_26.config(gpio, mcp_26.INPUT)
            mcp_26.pullup(gpio, 1) 
        return mcp_26
    elif address == 27:
        global mcp_27
        if mcp_27 == None:
            mcp_27 = Adafruit_MCP230xx.Adafruit_MCP230XX(busnum = 1, address = 0x27, num_gpios = 16)
        if mcp_setup_27[gpio] != SETUP_IN:
            mcp_setup_27[gpio] == SETUP_IN
            mcp_27.config(gpio, mcp_27.INPUT)
            mcp_27.pullup(gpio, 1)
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
    mcp = mcp23017_setup_out(address, gpio)
    if value == True:
        mcp.output(gpio, 1) 
    else:
        mcp.output(gpio, 0) 
        
        
def mcp23017_get(address, gpio):
    '''
    Is a gpio connected to earth or not
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    @return: True/False
    True = Connected to earth
    False = Not connecte dto earth
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio)
    if(mcp.input(gpio) >> gpio)==0:
        return True
    else:
        return False

        
def mcp23017_toggle(address, gpio):
    '''
    Toggle gpio pin to hight/low on a mcp
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_out(address, gpio)
    global toggle_mcp
    if [address, gpio] in toggle_mcp:
        mcp.output(gpio, 0)
        try:
            toggle_mcp.remove([address, gpio])
        except:
            pass
        return False
    else:
        mcp.output(gpio, 1)
        toggle_mcp.append([address, gpio])
        return True


def mcp23017_toggle_current(address, gpio):
    '''
    Get current toggle status
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_out(address, gpio)
    global toggle_mcp
    if [address, gpio] in toggle_mcp:
        return True
    else:
        return False


def mcp23017_flash(address, gpio, status):
    '''
    Toggle gpio pin to hight/low on a mcp
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    gpio = int(gpio)
    address = int(address)
    command = "mcp23017_flash"
    key = command + str(address) + str(gpio)
    if status == None or status:
        post = [None] * 4
        post[0] = command
        if status:
            post[1] = False
        else:
            post[1] = True
        post[2] = address
        post[3] = gpio
        worker_commands[key] = post
    else:
        worker_commands.pop(key, None)
        mcp.output(gpio, 0)
        try:
            toggle_mcp.remove([address, gpio])
        except:
            pass


def mcp23017_click(address, gpio, callback_method):
    '''
    Listen for click
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio)
    command = "mcp23017_click"
    key = command + str(address) + str(gpio)
    post = [None] * 6
    post[0] = command
    post[1] = address
    post[2] = gpio
    post[3] = mcp
    post[4] = callback_method
    post[5] = False
    worker_commands[key] = post
        
        
def mcp23017_event(address, gpio, callback_method):
    '''
    Listen for event
    @address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    @param callback_method: execute this method on event (paramater is the address, gpio and status (True/False))
                            callback_method(address, pin, status)
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_in(address, gpio)
    command = "mcp23017_event"
    key = command + str(address) + str(gpio)
    post = [None] * 6
    post[0] = command
    post[1] = address
    post[2] = gpio
    post[3] = mcp
    post[4] = callback_method
    post[5] = False
    worker_commands[key] = post


def ads1015(address, gpio, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    address= 48, 49, 4A, 4B 
    gpio = 0 to 3
    '''
    address = str(address)
    gpio = int(gpio)
    return __ads1015(address).readADCSingleEnded(gpio, gain, 250) / 1000


def ads1015_median(address, gpio, gain=GAIN_6_144_V, samples=16):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    Median of sumber of samples
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
        with lock_ads1015_48:
            global ads_48
            if ads_48==None:
                ads_48 = ADS1x15(address = 0x48, ic=0x00)
            return ads_48
    elif address == "49":
        with lock_ads1015_49:
            global ads_49
            if ads_49==None:
                ads_49 = ADS1x15(address = 0x49, ic=0x00)
            return ads_49
    elif address == "4A":
        with lock_ads1015_4A:
            global ads_4A
            if ads_4A==None:
                ads_4A = ADS1x15(address = 0x4A, ic=0x00)
            return ads_4A
    elif address == "4B":
        with lock_ads1015_4B:
            global ads_4B
            if ads_4B==None:
                ads_4B = ADS1x15(address = 0x4B, ic=0x00)
            return ads_4B


def ads1015_event(address, gpio, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    address= 48, 48, 4A, 4B 
    gpio = 0 to 3
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(address, pin, value)
    '''
    gpio = int(gpio)
    address = int(address)
    ads = __ads1015(address)
    command = "ads1015_event"
    key = command + str(address) + str(gpio)
    post = [None] * 7
    post[0] = command
    post[1] = address
    post[2] = gpio
    post[3] = ads
    post[4] = callback_method
    post[5] = -1
    post[6] = gain
    worker_commands[key] = post


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
        with lock_mcp4725:
            if dac==None:
                dac = MCP4725(0x60)
            dac.setVoltage(value)


def mcp4728(address, volt0, volt1, volt2, volt3):
    '''
    Write analog out from MCP4728 (0 to 5v)
    address = 61
    volt0 to3 = Voltage on pins (0 and 4095)
    '''
    global mcp4728_i2c
    address = int(address)
    if address == 61:
        address = 0x61
    volt0 = int(volt0)
    volt1 = int(volt1)
    volt2 = int(volt2)
    volt3 = int(volt3)
    with lock_mcp4728:
        if mcp4728_i2c == None:
            mcp4728_i2c = Adafruit_I2C(address)
        the_bytes = [(volt0 >> 8) & 0xFF, (volt0) & 0xFF, (volt1 >> 8) & 0xFF, (volt1) & 0xFF,
                 (volt2 >> 8) & 0xFF, (volt2) & 0xFF, (volt3 >> 8) & 0xFF, (volt3) & 0xFF]    
        mcp4728_i2c.writeList(0x50, the_bytes)
    
    
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
        steelsquid_utils.execute_delay(number_of_seconds, hdd44780_write, (None))
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
    if number_of_seconds > 0 and len(lcd_last_text) > 0:
        steelsquid_utils.execute_delay(number_of_seconds, nokia5110_write, (None))
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


def ssd1306_write(text, number_of_seconds = 0):
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
        steelsquid_utils.execute_delay(number_of_seconds, ssd1306_write, (None))
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
            ssd1306_write(text, number_of_seconds)
            lcd_auto = 1
        except:
            try:
                nokia5110_write(text, number_of_seconds, force_setup)
                lcd_auto = 2
            except:
                try:
                    hdd44780_write(text, number_of_seconds, force_setup, True)
                    lcd_auto = 3
                except:
                    lcd_auto = 4
    elif lcd_auto == 1:
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
    with lock_hcsr04:
        trig_gpio = int(trig_gpio)
        echo_gpio = int(echo_gpio)
        global distance_created
        if not distance_created or force_setup:
            gpio_setup_out(trig_gpio)
            gpio_setup_in_gnd(echo_gpio)
            gpio_set(trig_gpio, False)
            distance_created = True
        gpio_set(trig_gpio, False)
        time.sleep(0.001)
        gpio_set(trig_gpio, True)
        time.sleep(0.001)
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
                distance = echoduration * 17000
                return int(round(distance, 0))
            else:
                return -1
        else:
            return -1


def pca9685_move(servo, value):
    '''
    Move Adafruit 16-channel I2c servo to position (pwm value)
    @param servo: 0 to 15
    @param value: min=150, max=600 (may differ between servos)
    '''
    with lock_rbada:
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
    with lock_sabertooth:
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
    Move servo on a 12 servos with I2C Servo Controller IC.
    http://www.hobbytronics.co.uk/arduino-servo-controller
    Servo: 0 to 11
    Position: 0 to 255
    '''
    servo = int(servo)
    position = int(position)
    global i2c_servo12c
    if i2c_servo12c == None:
        i2c_servo12c = smbus.SMBus(1)
    i2c_servo12c.write_byte_data(address, servo, position)


def mpu6050_init(address=0x69):
    '''
    Init the mpu-6050 
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    '''
    global i2c_mpu_6050
    if i2c_mpu_6050 == None:
        i2c_mpu_6050 = smbus.SMBus(1)
        i2c_mpu_6050.write_byte_data(address, 0x6b, 0)


def mpu6050_gyro(address=0x69):
    '''
    Read mpu-6050 gyro data.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: (x, y, z)
    '''
    mpu6050_init(address)
    gyro_xout = read_word_2c(i2c_mpu_6050, address, 0x43) / 131
    gyro_xout = read_word_2c(i2c_mpu_6050, address, 0x45) / 131
    gyro_zout = read_word_2c(i2c_mpu_6050, address, 0x47) / 131
    return gyro_xout, gyro_xout, gyro_zout
    

def mpu6050_accel(address=0x69):
    '''
    Read mpu-6050 accelerometer data.
    SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050
    https://www.sparkfun.com/products/11028
    Returns: (x, y, z)
    '''
    mpu6050_init(address)
    accel_xout = read_word_2c(i2c_mpu_6050, address, 0x3b) / 16384.0
    accel_yout = read_word_2c(i2c_mpu_6050, address, 0x3d) / 16384.0
    accel_zout = read_word_2c(i2c_mpu_6050, address, 0x3f) / 16384.0
    return accel_xout, accel_yout, accel_zout


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


def read_word(bus, address, adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val


def read_word_2c(bus, address, adr):
    val = read_word(bus, address, adr)
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
    

if __name__ == '__main__':
    import sys
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        printb("IO commands for SteelsquidKissOS. Commands to get/set gpio and other stuff...")
        print("This is mostly for test purpuse, all logic should be made in the Steelsquid daemon")
        print("(e.g. steelsquid_kiss_global.py, expand.py...)")
        print("")
        print("You can execute the commands in two ways: direct or event")
        print("Direct execute the command in a own process outside of Steelsquid daemon, and may ")
        print("interrupt for example the LCD, DAC, ADC or extra GPIO.")
        print("Event send a command to the Steelsquid daemon witch in turn execute the command.")
        print("")
        print("Event is the preferred way if you want to make test from the command line.")
        print("Results from a event will not be return from the command itself, will be shouted")
        print("to all terminals... (events can only send command not receive answers.)")
        print("This events is mostly ment for test purpuse, inside Steelsquid daemon")
        print("you should use direct method.")
        print("")
        printb("d=direct")
        printb("e=event")
        print("")
        printb("pi <d/e> gpio_get_3v3 <gpio>")
        print("Get status of RaspberryPI GPIO")
        print("GPIO is connectoed to 3v3 (using internal pull-down)")
        print("gpio: 4-26")
        print("")
        printb("pi <d/e> gpio_set_3v3 <gpio> <true/false>")
        print("Set status of RaspberryPI GPIO")
        print("GPIO is connectoed to 3v3 (using internal pull-down)")
        print("gpio: 4-26")
        print("")
        printb("pi <d/e> gpio_get_gnd <gpio>")
        print("Get status of RaspberryPI GPIO")
        print("GPIO is connectoed to gnd (using internal pull-up)")
        print("gpio: 4-26")
        print("")
        printb("pi <d/e> gpio_set_gnd <gpio> <true/false>")
        print("Set status of RaspberryPI GPIO")
        print("GPIO is connectoed to gnd (using internal pull-up)")
        print("gpio: 4-26")
        print("")
        printb("pi <d/e> mcp23017_get <address> <gpio>")
        print("Get status gpio on a MCP23017")
        print("Connect GPIO to gnd (using internal pull-up)")
        print("address: 20-27")
        print("gpio: 0-15")
        print("")
        printb("pi <d/e> mcp23017_set <address> <gpio> <true/false>")
        print("Set a gpio hight or low on a MCP23017")
        print("Connect GPIO to gnd (using internal pull-up)")
        print("address: 20-27")
        print("gpio: 0-15")
        print("")
        printb("pi <d/e> ads1015 <address> <gpio>")
        print("Read analog in from ADS1015 (0 to 5 v)")
        print("address: 48, 49, 4A, 4B ")
        print("gpio: 0-3")
        print("")
        printb("pi <d/e> mcp4725 <address> <value>")
        print("Write analog out from MCP4725")
        print("address: 60 ")
        print("value: 0 and 4095")
        print("")
        printb("pi <d/e> mcp4728 <address> <volt0> <volt1> <volt2> <volt3>")
        print("Write analog out from MCP4728")
        print("address: 61")
        print("volt0-3: 0 and 4095")
        print("")
        printb("pi <d/e> hdd44780 <is_i2c> <text>")
        print("Print text to HDD44780 compatible LCD (\n or \\ = new line)")
        print("is_i2c: Is the LCD connected by I2C (true/false)")
        print("")
        printb("pi <d/e> nokia5110 <text>")
        print("Print text to nokia5110  LCD (\n or \\ = new line)")
        print("")
        printb("pi <d/e> ssd1306 <text>")
        print("Print text to ssd1306 oled LCD (\n or \\ = new line)")
        print("")
        printb("pi <d/e> hcsr04 <trig_gpio> <echo_gpio>")
        print("Measure_distance with a with HC-SR04.")
        print("trig_gpio: The trig gpio")
        print("echo_gpio: The echo gpio")
        print("")
        printb("pi <d/e> pca9685 <servo> <value>")
        print("Move Adafruit 16-channel I2c servo to position (pwm value).")
        print("servo: 0 to 15")
        print("value: min=150, max=600 (may differ between servos)")
        print("")
        printb("pi <d/e> sabertooth <port> <left> <right>")
        print("Set the speed on a sabertooth dc motor controller..")
        print("port: /dev/ttyAMA0, the_port=/dev/ttyUSB0")
        print("left and right: -100% to +100%")
        print("")
        printb("pi <d/e> trex_motor <left> <right>")
        print("Set TREX speed of the dc motors")
        print("left and right: -255 to 255")
        print("")
        printb("pi <d/e> trex_servo <servo> <position>")
        print("Set TREX servo position")
        print("servo: 1 to 6")
        print("Position: Typically the servo position should be a value between 1000 and 2000 although it will vary depending on the servos used")
        print("")
        printb("pi <d/e> trex_status")
        print("Get status from trex")
        print(" - Battery voltage:   An integer that is 100x the actual voltage")
        print(" - Motor current:  Current drawn by the motor in mA")
        print(" - Accelerometer")
        print(" - Impact")
        print("")
        printb("pi <d/e> diablo <left> <right>")
        print("Drive Piborg diablo motor board")
        print("left and right: -1000 to 1000")
        print("")
        printb("pi <d/e> servo12c <servo> <position>")
        print("Move servo on a 12 servos with I2C Servo Controller IC.")
        print("http://www.hobbytronics.co.uk/arduino-servo-controller")
        print("Servo: 0 to 11")
        print("Position: 0 to 255")
        print("")
        printb("pi <d/e> mpu6050_gyro")
        print("Read mpu-6050 gyro data.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi <d/e> mpu6050_accel")
        print("Read mpu-6050 accelerometer data.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
        print("")
        printb("pi <d/e> mpu6050_rotation")
        print("Read mpu-6050 rotation angle in degrees for both the X & Y.")
        print("SparkFun Triple Axis Accelerometer and Gyro Breakout - MPU-6050")
        print("https://www.sparkfun.com/products/11028")
    else:
        manner = sys.argv[1]
        command = sys.argv[2]
        if len(sys.argv)>3:
            para1 = sys.argv[3]
        if len(sys.argv)>4:
            para2 = sys.argv[4]
        if len(sys.argv)>5:
            para3 = sys.argv[5]
        if len(sys.argv)>6:
            para4 = sys.argv[6]
        if len(sys.argv)>7:
            para5 = sys.argv[7]
        if command == "gpio_get_3v3":
            if manner == "d" or manner == "direct":
                print gpio_get_3v3(para1)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["gpio_get_3v3", para1])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "gpio_get_gnd":
            if manner == "d" or manner == "direct":
                print gpio_get_gnd(para1) 
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["gpio_get_gnd", para1])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "gpio_set_3v3":
            if manner == "d" or manner == "direct":
                gpio_set_3v3(para1, steelsquid_utils.to_boolean(para2))
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["gpio_set_3v3", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "gpio_set_gnd":
            if manner == "d" or manner == "direct":
                gpio_set_gnd(para1, steelsquid_utils.to_boolean(para2))
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["gpio_set_gnd", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mcp23017_get":
            if manner == "d" or manner == "direct":
                print mcp23017_get(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mcp23017_get", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mcp23017_set":
            if manner == "d" or manner == "direct":
                mcp23017_set(para1, para2, steelsquid_utils.to_boolean(para3))
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mcp23017_set", para1, para2, para3])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "ads1015":
            if manner == "d" or manner == "direct":
                print ads1015(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["ads1015", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mcp4725":
            if manner == "d" or manner == "direct":
                mcp4725(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mcp4725", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mcp4728":
            if manner == "d" or manner == "direct":
                mcp4728(para1, para2, para3, para4, para5)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mcp4728", para1, para2, para3, para4, para5])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "hdd44780":
            if manner == "d" or manner == "direct":
                if steelsquid_utils.to_boolean(para1):
                    hdd44780_write(para2, number_of_seconds = 10, is_i2c=True)
                else:
                    hdd44780_write(para2, number_of_seconds = 10, is_i2c=False)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["hdd44780", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "nokia5110":
            if manner == "d" or manner == "direct":
                 nokia5110_write(para1, number_of_seconds = 10)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["nokia5110", para1])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "ssd1306":
            if manner == "d" or manner == "direct":
                 ssd1306_write(para1, number_of_seconds = 10)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["ssd1306", para1])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "hcsr04":
            if manner == "d" or manner == "direct":
                 print hcsr04_distance(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["hcsr04", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "pca9685":
            if manner == "d" or manner == "direct":
                 pca9685_move(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["pca9685", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "sabertooth":
            if manner == "d" or manner == "direct":
                 sabertooth_motor_speed(para2, para3, para1)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["sabertooth", para1, para2, para3])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "trex_motor":
            if manner == "d" or manner == "direct":
                 trex_motor(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["trex_motor", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "trex_servo":
            if manner == "d" or manner == "direct":
                 trex_servo(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["trex_servo", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "trex_status":
            if manner == "d" or manner == "direct":
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
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["trex_status"])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "diablo":
            if manner == "d" or manner == "direct":
                 diablo_motor_1(para1)
                 diablo_motor_2(para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["diablo", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "servo12c":
            if manner == "d" or manner == "direct":
                 servo12c(para1, para2)
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["servo12c", para1, para2])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mpu6050_gyro":
            if manner == "d" or manner == "direct":
                 print mpu6050_gyro()
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mpu6050_gyro"])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mpu6050_accel":
            if manner == "d" or manner == "direct":
                 print mpu6050_accel()
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mpu6050_accel"])
            else:
                print "Expected: direct (d), event (e)"
        elif command == "mpu6050_rotation":
            if manner == "d" or manner == "direct":
                 print mpu6050_rotation()
            elif manner == "e" or manner == "event":
                steelsquid_event.broadcast_event_external("pi_io_event", ["mpu6050_rotation"])
            else:
                print "Expected: direct (d), event (e)"
        else:
            print "Unknown command!!!"
    
