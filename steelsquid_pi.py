#!/usr/bin/python -OO


'''
Some useful stuff for Raspberry Pi
 - Print text to HDD44780 compatible LCD
 - Print text to a nokia511 LCD
 - Read GPIO input.
 - Set GPIO output.
 - Measure_distance with a with HC-SR04.
 - Controll Adafruit 16-Channel servo driver
 - Use a MCP230xx
 - Analog input ADS1015
 - Controll Trex robot controller
 - Sabertooth motor controller

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

SETUP_NONE = 0
SETUP_OUT = 1
SETUP_IN = 2
SETUP_IN_3V3 = 3
SETUP_IN_GND = 4
TIMEOUT = 2100
setup = [SETUP_NONE] * 32
lcd = None
toggle = [False] * 32
flash = [-1] * 32
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
running = False
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
flash_mcp = []
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
    return GPIO.input(int(gpio))


def gpio_get_gnd(gpio):
    '''
    Get gpio pin state
    @param gpio: GPIO number
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_GND:
        gpio_setup_in_gnd(gpio)
    return not GPIO.input(int(gpio))


def gpio_toggle_3v3(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to 3.3v
    @param gpio: GPIO number
    '''
    global toggle
    if toggle[gpio] == True:
        toggle[gpio] = False
        gpio_set_3v3(gpio, False)
    else:
        toggle[gpio] = True
        gpio_set_3v3(gpio, True)


def gpio_toggle_gnd(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to gnd
    @param gpio: GPIO number
    '''
    global toggle
    if toggle[gpio] == True:
        toggle[gpio] = False
        gpio_set_gnd(gpio, False)
    else:
        toggle[gpio] = True
        gpio_set_gnd(gpio, True)


def gpio_event_3v3(gpio, high_method, low_method):
    '''
    Listen for events on gpio pin and 3.3v
    @param gpio: GPIO number
    @param high_method: On high
    @param low_method: On low
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_3V3:
        gpio_setup_in_3v3(gpio)
    def call_met(para):
        status = gpio_get_3v3(para)
        try:
            if status == True:
                high_method(para)          
            else:
                low_method(para)          
        except:
            steelsquid_utils.shout()
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_event_gnd(gpio, high_method, low_method):
    '''
    Listen for events on gpio pin and ground
    @param gpio: GPIO number
    @param high_method: On high
    @param low_method: On low
    '''
    global setup
    if not setup[int(gpio)] == SETUP_IN_GND:
        gpio_setup_in_gnd(gpio)
    def call_met(para):
        status = gpio_get_gnd(para)
        try:
            if status == True:            
                high_method(para)          
            else:
                low_method(para)          
        except:
            steelsquid_utils.shout()
    GPIO.add_event_detect(int(gpio), GPIO.BOTH, callback=call_met, bouncetime=100)


def gpio_click_3v3(gpio, callback_method):
    '''
    Connect a button to gpio pin and 3.3v
    Will fire when button is released. If press more than 1s it will be ignore
    @param gpio: GPIO number
    @param callback_method: execute this method on event
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
    @param callback_method: execute this method on event
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
    Flash a gpio on and off (1 second) connected to 3.3v

    @param gpio: The gpio to flash
    @param enable: Strart or stop the flashing (True/False)
    '''
    global flash
    global running
    if enable:
        flash[gpio] = 1
    else:
        flash[gpio] = 0
    if not running:
        running = True
        thread.start_new_thread(do_flash, ())
    
    
def gpio_flash_gnd(gpio, enable):
    '''
    Flash a gpio on and off (1 second) connected to ground

    @param gpio: The gpio to flash
    @param enable: Strart or stop the flashing (True/False)
    '''
    global flash
    global running
    if enable:
        flash[gpio] = 3
    else:
        flash[gpio] = 2
    if not running:
        running = True
        thread.start_new_thread(do_flash, ())


def gpio_flash_3v3_timer(gpio, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    thread.start_new_thread(do_flash_3v3_timer, (gpio, seconds))
   
   
def gpio_flash_gnd_timer(gpio, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    thread.start_new_thread(do_flash_gnd_timer, (gpio, seconds))
 
 
def gpio_set_3v3_timer(gpio, seconds):
    '''
    On for sertant time
    '''
    thread.start_new_thread(do_set_3v3_timer, (gpio, seconds))
   
   
def gpio_set_gnd_timer(gpio, seconds):
    '''
    On for sertant time
    '''
    thread.start_new_thread(do_set_gnd_timer, (gpio, seconds))

        
def do_set_3v3_timer(gpio, seconds):
    '''
    On for number of seconds
    '''
    gpio_set_3v3(gpio, True)
    time.sleep(seconds)
    gpio_set_3v3(gpio, False)


def do_set_gnd_timer(gpio, seconds):
    '''
    On for number of seconds
    '''
    gpio_set_gnd(gpio, True)
    time.sleep(seconds)
    gpio_set_gnd(gpio, False)


def do_flash_3v3_timer(gpio, seconds):
    '''
    Flash for number of seconds
    '''
    gpio_flash_3v3(gpio, True)
    time.sleep(seconds)
    gpio_flash_3v3(gpio, False)


def do_flash_gnd_timer(gpio, seconds):
    '''
    Flash for number of seconds
    '''
    gpio_flash_gnd(gpio, True)
    time.sleep(seconds)
    gpio_flash_gnd(gpio, False)
            

def hdd44780_write(text, number_of_seconds = 0, force_setup = True, is_i2c=True):
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
                contrast = int(steelsquid_utils.get_parameter("nokia_contrast", 50))
                nokia_lcd.begin(contrast=contrast)
            nokia_lcd.image(image)
            nokia_lcd.display()


def hcsr04_distance(trig_gpio, echo_gpio, force_setup = False):
    '''
    Measure_distance with a with HC-SR04.
    @param trig_gpio: The trig gpio
    @param echo_gpio: The echo gpio
    @param force_setup: Force setup of pins
    @return: The distance in cm (-1 = unable to mesure)
    '''
    with lock_hcsr04:
        global distance_created
        if not distance_created or force_setup:
            gpio_setup_out(trig_gpio)
            gpio_setup_in_gnd(echo_gpio)
            gpio_set(trig_gpio, False)
            distance_created = True
        gpio_set(trig_gpio, False)
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
                distance = echoduration * 17000
                return int(round(distance, 0))
            else:
                return -1
        else:
            return -1


def rbada70_move(servo, value):
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


def sabertooth_motor_speed(left, right, the_port=None):
    '''
    Set the speed on a sabertooth dc motor controller.
    from -100 to +100
    -100 = 100% back speed
    0 = no speed
    100 = 100% forward speed
    '''
    with lock_sabertooth:
        global sabertooth
        if sabertooth==None:
            import steelsquid_sabertooth
            if the_port == None:
                the_port = steelsquid_utils.get_parameter("sabertooth_port", "")
            sabertooth = steelsquid_sabertooth.SteelsquidSabertooth(serial_port=the_port)
        sabertooth.set_dc_speed(left, right)


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


def mcp23017_click(address, gpio, callback_method):
    '''
    Listen for click
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    thread.start_new_thread(__mcp_click, (address, gpio, callback_method))


def __mcp_click(address, gpio, callback_method):
    '''
    '''
    mcp = mcp23017_setup_in(address, gpio)
    last = False
    while True:
        if(mcp.input(gpio) >> gpio)==0:
            last = True
        else:
            if last == True:
                try:
                    callback_method()
                except:
                    steelsquid_utils.shout()
            last = False
        time.sleep(0.15)
        
        
def mcp23017_event(address, gpio, callback_method):
    '''
    Listen for event
    Address: 20, 21, 22, 23, 24, 25, 26, 27
    @param gpio: 0 to 15
    The MCP23017 has 16 pins - A0 thru A7 + B0 thru B7. A0 is called 0 in the library, and A7 is called 7, then B0 continues from there as is called 8 and finally B7 is pin 15
    '''
    gpio = int(gpio)
    address = int(address)
    thread.start_new_thread(__mcp_event, (address, gpio, callback_method))


def __mcp_event(address, gpio, callback_method):
    '''
    '''
    mcp = mcp23017_setup_in(address, gpio)
    last = False
    while True:
        if(mcp.input(gpio) >> gpio)==0:
            if last == False:
                try:
                    callback_method(True)
                except:
                    steelsquid_utils.shout()
            last = True
        else:
            if last == True:
                try:
                    callback_method(False)
                except:
                    steelsquid_utils.shout()
            last = False
        time.sleep(0.15)

    

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
    else:
        mcp.output(gpio, 1)
        toggle_mcp.append([address, gpio])


def mcp23017_flash(address, gpio, status):
    '''
    Toggle gpio pin to hight/low on a mcp
    '''
    gpio = int(gpio)
    address = int(address)
    mcp = mcp23017_setup_out(address, gpio)
    global flash_mcp
    if status:
        try:
            flash_mcp.remove([address, gpio])
        except:
            pass
        flash_mcp.append([address, gpio])
    else:
        try:
            flash_mcp.remove([address, gpio])
        except:
            pass
        mcp.output(gpio, 0) 
    global running
    if not running:
        running = True
        thread.start_new_thread(do_flash, ())


def mcp23017_set_timer(address, gpio, seconds):
    '''
    '''
    thread.start_new_thread(do_mcp_set_time, (address, gpio, seconds))


def mcp23017_flash_timer(address, gpio, seconds):
    '''
    '''
    thread.start_new_thread(do_mcp_flash_time, (address, gpio, seconds))

        
def do_mcp_set_time(address, gpio, seconds):
    '''
    On for number of seconds
    '''
    mcp23017_set(address, gpio, True)
    time.sleep(seconds)
    mcp23017_set(address, gpio, False)


def do_mcp_flash_time(address, gpio, seconds):
    '''
    Flash for number of seconds
    '''
    mcp23017_flash(address, gpio, True)
    time.sleep(seconds)
    mcp23017_flash(address, gpio, False)


def do_flash():
    '''
    Toggle gpio on and off (will loop)
    '''
    global running
    running = True
    global flash
    global flash_mcp
    while running:
        for gpio in range(0, 32):
            if flash[gpio] == 0:
                gpio_set_3v3(gpio, False)
                flash[gpio] = -1
            elif flash[gpio] == 1:
                gpio_toggle_3v3(gpio)
            elif flash[gpio] == 2:
                gpio_set_gnd(gpio, False)
                flash[gpio] = -1
            elif flash[gpio] == 3:
                gpio_toggle_gnd(gpio)
        for address, gpio in flash_mcp:
            mcp23017_toggle(address, gpio)
        time.sleep(1)


def ads1015(address, gpio, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    address= 48, 49, 4A, 4B 
    gpio = 0 to 3
    '''
    address = str(address)
    gpio = int(gpio)
    if address == "48":
        with lock_ads1015_48:
            global ads_48
            if ads_48==None:
                ads_48 = ADS1x15(address = 0x48, ic=0x00)
            return ads_48.readADCSingleEnded(gpio, gain, 250) / 1000
    elif address == "49":
        with lock_ads1015_49:
            global ads_49
            if ads_49==None:
                ads_49 = ADS1x15(address = 0x49, ic=0x00)
            return ads_49.readADCSingleEnded(gpio, gain, 250) / 1000
    elif address == "4A":
        with lock_ads1015_4A:
            global ads_4A
            if ads_4A==None:
                ads_4A = ADS1x15(address = 0x4A, ic=0x00)
            return ads_4A.readADCSingleEnded(gpio, gain, 250) / 1000
    elif address == "4B":
        with lock_ads1015_4B:
            global ads_4B
            if ads_4B==None:
                ads_4B = ADS1x15(address = 0x4B, ic=0x00)
            return ads_4B.readADCSingleEnded(gpio, gain, 250) / 1000
        

def ads1015_event(address, gpio, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    address= 48, 48, 4A, 4B 
    gpio = 0 to 3
    '''
    gpio = int(gpio)
    address = str(address)
    thread.start_new_thread(__ads_event, (address, gpio, callback_method, gain))


def __ads_event(address, gpio, callback_method, gain):
    '''
    '''
    last = 0
    while True:
        new = adc_get(address, gpio, gain)
        if new != last:
            try:
                callback_method(new)
            except:
                steelsquid_utils.shout()
            last = new
        time.sleep(1)


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
    volt1 to 3 = Voltage on pins (0 and 4095)
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


if __name__ == '__main__':
    pass
    
