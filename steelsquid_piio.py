#!/usr/bin/python -OO


'''
Mostly wrapper functions (hard coded adresses and pins) for my steelsquid PIIO board
On the PIIO board the pins has the number 1,2,3... You can use that numbering or the normal Raspberrt Pi GPIO numbering.
The numbering looks like: 1_14, 2_15, 3_18...   Before the underscore is the PIIO board pin nr and after is the Raspberry Pi GPIO.
http://www.steelsquid.org/steelsquid-piio-board

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_trex
import steelsquid_event
import steelsquid_kiss_global
from decimal import Decimal
import time

EDGE_RISING = steelsquid_pi.EDGE_RISING
EDGE_FALLING = steelsquid_pi.EDGE_FALLING
EDGE_BOTH = steelsquid_pi.EDGE_BOTH
PULL_UP = steelsquid_pi.PULL_UP
PULL_DOWN = steelsquid_pi.PULL_DOWN
PULL_NONE = steelsquid_pi.PULL_NONE
GAIN_6_144_V = 6144
GAIN_6_144_V = 6144
GAIN_4_096_V = 4096
GAIN_2_048_V = 2048
GAIN_1_024_V = 1024
GAIN_0_512_V = 512
GAIN_0_256_V = 256

# Max Servo position
servo_position_max = 400
# Min Servo position
servo_position_min = 140
# Servo start position
servo_position = 260
# Motor max forward
motor_forward = 255
# Motor max backward
motor_backward = -255

counter=0
version = "1.0"


def shutdown():
    '''
    Shutdown and power off the PIIO board
    '''
    steelsquid_kiss_global.PIIO.on_disable()
    steelsquid_pi.po16_gpio_set(1, True)
    steelsquid_utils.execute_system_command_blind(['shutdown', 'now', '-h'])


def volt(number_of_decimals=-1, samples=1):
    '''
    Read main in voltage to the PIIO board
    Return: main in voltage
    '''
    v = steelsquid_pi.po12_adc_volt(3, samples=samples) / float(steelsquid_utils.get_parameter("voltage_divider", "0.1179"))
    if number_of_decimals!=-1:
        v = Decimal(v)
        v = round(v, number_of_decimals)
    return v


def volt_event(callback_method, min_change=0.01, sample_sleep=0.2, samples=1):
    '''
    Read main in voltage to the PIIO board and execute method if it change
    def callback_method(voltage):
       ...do stuff
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    def inner_callback_method(ch, voltage):
        callback_method(voltage / float(steelsquid_utils.get_parameter("voltage_divider", "0.1179")))
    return steelsquid_pi.po12_adc_event(3, inner_callback_method, min_change, sample_sleep, samples=samples)


def button(button_nr):
    '''
    Read status of the 6 buttons on the PIIO board
    button_nr = 1 to 6
    return True/False  (Pressed or not pressed)
    '''
    button_nr = int(button_nr)-1
    return not steelsquid_pi.mcp23017_get(21, button_nr)


def button_event(button_nr, callback_method):
    '''
    Listen for changes on the 6 buttons on the PIIO board
    button_nr = 1 to 6
    callback_method = Execute this method on event.
                    callback_method(button_nr, status)
                        ....Do something
    '''
    button_nr = int(button_nr)
    def mcp_event_callback_method(address, pin, status): 
        callback_method(button_nr, not status)
    steelsquid_pi.mcp23017_event(21, button_nr-1, mcp_event_callback_method, rpi_gpio=26)


def button_click(button_nr, callback_method):
    '''
    Listen for click on the 6 buttons on the PIIO board
    button_nr = 1 to 6
    callback_method = Execute this method on click.
                    callback_method(button_nr)
                        ....Do something
    '''
    button_nr = int(button_nr)
    def mcp_event_callback_method(address, pin): 
        callback_method(button_nr)
    steelsquid_pi.mcp23017_click(21, button_nr-1, mcp_event_callback_method, rpi_gpio=26)


def switch(dip_nr):
    '''
    Read status of the 6 dip switch on the PIIO board
    dip_nr = 1 to 6
    return True/False 
    '''
    dip_nr = (int(dip_nr)-14)*-1
    return not steelsquid_pi.mcp23017_get(21, dip_nr)


def switch_event(dip_nr, callback_method):
    '''
    Listen for changes on the 6 dip switches on the PIIO board
    dip_nr = 1 to 6
    callback_method = Execute this method on event.
                    callback_method(dip_nr, status)
                        ....Do something
    '''
    ndip_nr = (int(dip_nr)-14)*-1
    def mcp_event_callback_method(address, pin, status): 
        callback_method(dip_nr, not status)
    steelsquid_pi.mcp23017_event(21, ndip_nr, mcp_event_callback_method, rpi_gpio=26)


def led(led_nr, status):
    '''
    Turn on or off the user LED
    led_nr = 1 to 6
    status = True/False 
    '''
    led_nr=int(led_nr)
    if led_nr == 1:
        led_nr=2
    elif led_nr == 2:
        led_nr=4
    elif led_nr == 3:
        led_nr=5
    elif led_nr == 4:
        led_nr=6
    elif led_nr == 5:
        led_nr=7
    elif led_nr == 6:
        led_nr=8
    steelsquid_pi.po16_gpio_set(led_nr, status)


def led_flash(led_nr, status, seconds):
    '''
    Turn on and off the LED on given interval
    led_nr = 1 to 6
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_utils.execute_flash("led" + str(led_nr), status, seconds, led, (led_nr, True,), led, (led_nr, False,))


def buz(status):
    '''
    Turn on or off the buzzer
    status = True/False 
    '''
    steelsquid_pi.po12_digital_out(2, status)


def buz_flash(status, seconds):
    '''
    Turn on and off the buzzer on given interval
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_utils.execute_flash("buz_flash", status, seconds, steelsquid_pi.po12_digital_out, (2, True,), steelsquid_pi.po12_digital_out, (2, False,))


def lcd(text=None, number_of_seconds = 0):
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
    steelsquid_pi.ssd1306_write(text, number_of_seconds)


def gpio_set(gpio, state, use_piio_pin_nr=True):
    '''
    Set gpio pin to hight (true) or low (false) on a pin
    This is marked with GPIO and GPIO_5V on the PIIO board.
    @param gpio: GPIO number (Raspberry GPIO or piio pin nr)
    @param state: True/False
    @param use_piio_pin_nr: Use PIIO pin nr or Raspberry GPIO nr.
    '''
    state = steelsquid_utils.to_boolean(state)
    if use_piio_pin_nr:
        gpio = __convert_to_gpio(gpio)
    steelsquid_pi.gpio_set(gpio, state)


def gpio_flash(gpio, status, seconds, use_piio_pin_nr=True):
    '''
    Change to hight (true) or low (false) on a pin alternately
    This is marked with GPIO and GPIO_5V on the PIIO board.
    @param gpio: GPIO number
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    @param use_piio_pin_nr: Use PIIO pin nr or Raspberry GPIO nr.
    '''
    steelsquid_utils.execute_flash("gpio_flash"+str(gpio), status, seconds, gpio_set, (gpio, True, use_piio_pin_nr,), gpio_set, (gpio, False, use_piio_pin_nr,))


def gpio_get(gpio, resistor=PULL_DOWN, use_piio_pin_nr=True):
    '''
    Get gpio pin state
    This is marked with GPIO and GPIO_5V on the PIIO board.
    Connect GPIO to gnd (using internal pull-up)    
    @param gpio: GPIO number (Raspberry GPIO or piio pin nr)
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    @param use_piio_pin_nr: Use PIIO pin nr or Raspberry GPIO nr.
    @return: True/False
    '''
    if use_piio_pin_nr:
        gpio = __convert_to_gpio(gpio)
    return steelsquid_pi.gpio_get(gpio, resistor)


def gpio_event(gpio, callback_method, bouncetime_ms=60, resistor=PULL_DOWN, edge=EDGE_BOTH, use_piio_pin_nr=True):
    '''
    Listen for events on gpio pin
    Connect GPIO to gnd (using internal pull-up)    
    This is marked with GPIO and GPIO_5V on the PIIO board.
    @param gpio: GPIO number (Raspberry GPIO or piio pin nr)
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    @edge: EDGE_BOTH, EDGE_FALLING, EDGE_RISING
    @param use_piio_pin_nr: Use PIIO pin nr or Raspberry GPIO nr.
    '''
    gpio = int(gpio)
    if use_piio_pin_nr:
        ngpio = __convert_to_gpio(gpio)
    else:
        ngpio=int(gpio)
    def inner_callback_method(pin, status):
        callback_method(gpio, status)
    steelsquid_pi.gpio_event(ngpio, inner_callback_method, bouncetime_ms, resistor, edge)


def gpio_click(gpio, callback_method, bouncetime_ms=60, resistor=PULL_DOWN, use_piio_pin_nr=True):
    '''
    Connect a button to gpio pin
    Connect GPIO to gnd (using internal pull-up)    
    Will fire when button is released. If press more than 1s it will be ignore
    This is marked with GPIO and GPIO_5V on the PIIO board.
    @param gpio: GPIO number (Raspberry GPIO or piio pin nr)
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    @resistor: PULL_UP, PULL_DOWN, PULL_NONE
    @param use_piio_pin_nr: Use PIIO pin nr or Raspberry GPIO nr.
    '''
    gpio = int(gpio)
    if use_piio_pin_nr:
        ngpio = __convert_to_gpio(gpio)
    else:
        ngpio=int(gpio)
    def inner_callback_method(pin):
        callback_method(gpio)
    steelsquid_pi.gpio_click(ngpio, inner_callback_method, bouncetime_ms, resistor)
    

def __convert_to_gpio(pin):
    pin = int(pin)
    if pin == 1:
        return 14
    elif pin == 2:
        return 15
    elif pin == 3:
        return 18
    elif pin == 4:
        return 23
    elif pin == 5:
        return 24
    elif pin == 6:
        return 25
    elif pin == 7:
        return 8
    elif pin == 8:
        return 7
    elif pin == 9:
        return 12
    elif pin == 10:
        return 16
    elif pin == 11:
        return 20
    elif pin == 12:
        return 21
    elif pin == 13:
        return 4
    elif pin == 14:
        return 17
    elif pin == 15:
        return 27
    elif pin == 16:
        return 22
    elif pin == 17:
        return 10
    elif pin == 18:
        return 9
    elif pin == 19:
        return 11
    elif pin == 20:
        return 5
    elif pin == 21:
        return 6
    elif pin == 22:
        return 13
    else:
        raise ValueError("GPIO number can only be 1 to 22, you try to use " + pin)


def xgpio_set(gpio, value):
    '''
    Set a gpio hight or low on the XGPIO pins.
    @param gpio: 1 to 8
    @param value: True/False
    '''
    gpio = __convert_to_xgpio(gpio)
    steelsquid_pi.mcp23017_set(20, gpio, value)


def xgpio_flash(gpio, status, seconds):
    '''
    Set a gpio hight or low on XGPIO pins
    Change to hight (true) or low (false) on a pin alternately
    @param gpio: GPIO number
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("xgpio_set"+str(gpio), status, seconds, xgpio_set, (gpio, True,), xgpio_set, (gpio, False,))
        
        
def xgpio_get(gpio, pullup=True):
    '''
    Get status on pin on the XGPIO pins.
    Connect GPIO to gnd (using internal pull-up)    
    @param gpio: 1 to 8
    @return: True/False
    True = Hight (1)
    False = Low (0)
    '''
    gpio = __convert_to_xgpio(gpio)
    return steelsquid_pi.mcp23017_get(20, gpio, pullup)


def xgpio_event(gpio, callback_method, pullup=True): 
    ''' 
    Listen for event on the XGPIO pins.
    Connect GPIO to gnd (using internal pull-up)    
    @param gpio: 2 to 8
    @param callback_method: execute this method on event (paramater is the address, gpio and status (True/False))
                            callback_method(pin, status)
    @param pullup: Use internal pululp
    '''
    gpio = int(gpio)
    ngpio = __convert_to_xgpio(gpio)
    def inner_callback_method(address, pin, status):
        callback_method(gpio, status)
    steelsquid_pi.mcp23017_event(20, ngpio, inner_callback_method, pullup, 19)
    

def xgpio_click(gpio, callback_method, pullup=True):
    '''
    Listen for click on the XGPIO pins.
    Connect GPIO to gnd (using internal pull-up)    
    @param gpio: 1 to 8
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(pin)
    '''
    gpio = int(gpio)
    ngpio = __convert_to_xgpio(gpio)
    def inner_callback_method(address, pin):
        callback_method(gpio)
    steelsquid_pi.mcp23017_click(20, ngpio, inner_callback_method, pullup, 19)


def __convert_to_xgpio(pin):
    pin = int(pin)
    if pin == 1:
        return 15
    elif pin == 2:
        return 14
    elif pin == 3:
        return 13
    elif pin == 4:
        return 12
    elif pin == 5:
        return 11
    elif pin == 6:
        return 10
    elif pin == 7:
        return 9
    elif pin == 8:
        return 8
    else:
        raise ValueError("XGPIO number can only be 1 to 8, you try to use " + pin)


def power(gpio, value):
    '''
    Set the status of the POWER pins.
    Connect POWER pin to the device you want to control (voltage from 4V to 50V), 500mA
    The POWER pin is GND, so from the voltage source to the device then to POWER pin.
    @param gpio: 1 to 8
    @param value: True/False
    '''
    gpio = int(gpio)
    if gpio > 8:
        raise ValueError("POWER pin number can only be 1 to 8, you try to use " + pin)
    steelsquid_pi.mcp23017_set(20, gpio-1, value)


def power_flash(gpio, status, seconds):
    '''
    Set a gpio hight or low on POWER pins
    Change to hight (true) or low (false) on a pin alternately
    Connect POWER pin to the device you want to control (voltage from 4V to 50V), 500mA
    The POWER pin is GND, so from the voltage source to the device then to POWER pin.
    @param gpio: GPIO number
    @param status: True/False (None = Only alternate one time (True, false))
    @param seconds: Seconds between state change
    '''
    steelsquid_utils.execute_flash("power_flash"+str(gpio), status, seconds, power, (gpio, True,), power, (gpio, False,))
        
    
def adc(channel, samples=1):
    '''
    Read the analog voltage in on the ADC pins
    channel = 1 to 7
    Return 0V to 3.3V
    '''
    channel = int(channel)
    if channel==1:
        channel=4
    elif channel==2:
        channel=5
    elif channel==3:
        channel=6
    elif channel==4:
        channel=7
    elif channel==5:
        channel=2
    elif channel==6:
        channel=8
    elif channel==7:
        channel=1
    return steelsquid_pi.po12_adc_volt(channel, samples=samples)


def adc_event(channel, callback_method, min_change=0.01, sample_sleep=0.2, samples=1):
    '''
    Read the analog voltage in on the ADC pins and execute method if it change
    def callback_method(channel, voltage):
       ...do stuff
    channel = 1 to 7
    callback_method: Execute this method on change
    min_change: Only execute method if value change this mutch from last time
    sample_sleep: Sleep ths long between sample (only one thread handle all events so the last set sleep time is in use)
    '''
    channel = int(channel)
    if channel==1:
        nchannel=4
    elif channel==2:
        nchannel=5
    elif channel==3:
        nchannel=6
    elif channel==4:
        nchannel=7
    elif channel==5:
        nchannel=2
    elif channel==6:
        nchannel=8
    elif channel==7:
        nchannel=1
    def inner_callback_method(ch, voltage):
        callback_method(channel, voltage)
    return steelsquid_pi.po12_adc_event(nchannel, inner_callback_method, min_change, sample_sleep, samples=samples)


def dac(volt_1, volt_2, volt_3, volt_4):
    '''
    Write analog out from the 4 DAC pins (0 to 3.3v)
    volt0 to3 = Voltage on pins (0 and 4095)
    '''
    steelsquid_pi.mcp4728(61, volt_1, volt_2, volt_3, volt_4)


def servo(servo, position):
    '''
    Move a servo connected to the PIIO board.
    Servo: 1 to 12
    Position: 0 to 255
    '''
    servo=int(servo)
    steelsquid_pi.servo12c(servo-1, position)


def pwm(pin, value):
    '''
    Set pwm value on one of the 4 PWM pins.
    The PWM pins use the same curcit that control the DC motors.
    You can not use the PWM and MOTOR controller at the same time.
    pin: 1 to 4
    value: 0 to 1023
    '''
    pin=int(pin)
    if pin == 1:
        pin=3
    elif pin == 3:
        pin=1
    steelsquid_pi.po16_pwm(pin, value)
    
    
def motor(motor_1, motor_2):
    '''
    Set speed of two DC motors.
    The motors use the same curcit as the PWM pins.
    You can not use the PWM and MOTOR controller at the same time.
    -1023 = fullspeed reverse
    0 = not moving
    1023 = fullspeed forward
    motor_1: -1023 to 1023 
    motor_2: -1023 to 1023
    '''
    motor_1 = int(motor_1)
    motor_2 = int(motor_2)
    if motor_1 < 0:
        steelsquid_pi.po16_pwm(1, 0)
        steelsquid_pi.po16_pwm(4, motor_1*-1)
    elif motor_1 > 0:
        steelsquid_pi.po16_pwm(1, motor_1)
        steelsquid_pi.po16_pwm(4, 0)
    else:
        steelsquid_pi.po16_pwm(1, 0)
        steelsquid_pi.po16_pwm(4, 0)
    if motor_2 < 0:
        steelsquid_pi.po16_pwm(3, 0)
        steelsquid_pi.po16_pwm(2, motor_2*-1)
    elif motor_2 > 0:
        steelsquid_pi.po16_pwm(3, motor_2)
        steelsquid_pi.po16_pwm(2, 0)
    else:
        steelsquid_pi.po16_pwm(3, 0)
        steelsquid_pi.po16_pwm(2, 0)


def movement():
    '''
    Read movement with the gyro sensor.
    Returns: (x, y, z)
    '''
    return steelsquid_pi.mpu6050_movement()
    

def rotation():
    '''
    Read rotation angle in degrees for both the X & Y.
    Returns: (x, y)
    '''
    return steelsquid_pi.mpu6050_rotation()


def movement_event(callback_method, min_change=10, sample_sleep=0.2):
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
    steelsquid_pi.mpu6050_movement_event(callback_method, min_change, sample_sleep)


def rotation_event(callback_method, min_change=2, sample_sleep=0.2):
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
    steelsquid_pi.mpu6050_rotation_event(callback_method, min_change, sample_sleep)


def bt(status):
    '''
    Turn on and off the bluetooth led (BT)
    status = True/False 
    '''
    steelsquid_pi.po12_digital_out(3, status)


def bt_flash(status, seconds):
    '''
    Turn on and off the bluetooth led on given interval (BT)
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_utils.execute_flash("bt_flash", status, seconds, bt, (True,), bt, (False,))


def net(status):
    '''
    Turn on and off the network led (NET)
    status = True/False 
    '''
    steelsquid_pi.po12_digital_out(1, status)


def net_flash(status, seconds):
    '''
    Turn on and off the network led on given interval (NET)
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_utils.execute_flash("net_flash", status, seconds, net, (True,), net, (False,))


def error(status):
    '''
    Turn on and off the error led (ERROR)
    status = True/False 
    '''
    steelsquid_pi.mcp23017_set(21, 7, status)


def error_flash(status, seconds):
    '''
    Turn on and off the error led on given interval (ERROR)
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_pi.mcp23017_flash(21, 7, status, seconds)


def ok(status):
    '''
    Turn on and off the ok led (OK)
    status = True/False 
    '''
    steelsquid_pi.mcp23017_set(21, 6, status)


def ok_flash(status, seconds):
    '''
    Turn on and off the ok led on given interval (OK)
    status = True/False (if None: On and of one time)
    seconds = On and off intervall
    only_ones = Flash it one time only
    '''
    steelsquid_pi.mcp23017_flash(21, 6, status, seconds)


def low_bat(status):
    '''
    Turn on and off the low_bat bat LED flashing
    Will also buzz every 20 second
    status = True/False 
    '''
    global counter
    def flashit(status): 
        global counter
        steelsquid_pi.po16_gpio_set(3, status)
        if status:
            if counter==0:
                counter = counter+1
                buz(True)
            elif counter==10:
                counter=0
            else:
                counter = counter+1
        else:
            buz(False)
    steelsquid_utils.execute_flash("low_bat", status, 0.5, flashit, (True,), flashit, (False,))
    if not status:
        counter=0


def info():
    '''
    Get status of the INFO button
    @return: True/False
    True = Hight (1)
    False = Low (0)
    '''
    return not steelsquid_pi.mcp23017_get(21, 14, True)


def info_event(callback_method): 
    ''' 
    Listen for event on the info button.
    @param callback_method: execute this method on event 
                            callback_method(status)
    '''
    def inner_callback_method(address, pin, status):
        callback_method(not status)
    steelsquid_pi.mcp23017_event(21, 14, inner_callback_method, True, rpi_gpio=26)
    
    
def info_click(callback_method):
    '''
    Listen for click on the info button.
    @param callback_method: execute this method on event
                            callback_method()
    '''
    def inner_callback_method(address, pin):
        callback_method()
    steelsquid_pi.mcp23017_click(21, 14, inner_callback_method, True, rpi_gpio=26)
    

def power_off():
    '''
    Get status of the power off button
    @return: True/False
    True = Hight (1)
    False = Low (0)
    '''
    return not steelsquid_pi.mcp23017_get(21, 15, True)


def power_off_event(callback_method): 
    ''' 
    Listen for event on the power off button.
    @param callback_method: execute this method on event 
                            callback_method(status)
    '''
    def inner_callback_method(address, pin, status):
        callback_method(not status)
    steelsquid_pi.mcp23017_event(21, 15, inner_callback_method, True, rpi_gpio=26)
    
    
def power_off_click(callback_method):
    '''
    Listen for click on the power off button.
    @param callback_method: execute this method on event
                            callback_method()
    '''
    def inner_callback_method(address, pin):
        callback_method()
    steelsquid_pi.mcp23017_click(21, 15, inner_callback_method, True, rpi_gpio=26)


def gpio_event_callback_method(pin, status): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Pin " + str(pin) + " = " + str(status))


def gpio_click_callback_method(pin): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Pin Click " + str(pin) + " = Click")


def xgpio_event_callback_method(pin, status): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Pin " + str(pin) + " = " + str(status))


def xgpio_click_callback_method(pin): 
    '''
    To test the gpio event handler
    '''
    steelsquid_utils.log("Pin " + str(pin) + " = Click")

    
if __name__ == '__main__':
    import sys
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        printb("Send commands to the Steelsquid IO board from the command line.")
        printb("This is mostly ment for test purpuse.")
        printb("You should use it from example steelsquid_kiss_expand.py running inside the steelsquid daemon.")
        printb("This may interupt the steelsquid daemon so for example the power off button stop working.")
        print("")
        printb("piio shutdown")
        print("Shutdown and power off the system")
        print("")
        printb("piio volt")
        print("Read main in voltage to the PIIO board and execute method if it change")
        print("Return: Main in voltage on the PIIO board")
        print("")
        printb("piio volt_event")
        print("Make method execute when the main in voltage to the PIIO board and execute method if it change")
        print("")
        printb("piio button <button_nr>")
        print("Read status of the 6 buttons on the PIIO board")
        print("button_nr = 1 to 6")
        print("")
        printb("piio button_event <button_nr>")
        print("Listen for change of the 6 buttons on the PIIO board")
        print("button_nr: 1-6")
        print("")
        printb("piio button_click <button_nr>")
        print("Listen for click on the 6 buttons on the PIIO board")
        print("button_nr: 1-6")
        print("")
        printb("piio switch <dip_nr>")
        print("Read status of the 6 dip switch on the PIIO board")
        print("dip_nr = 1 to 6")
        print("")
        printb("piio switch_event <dip_nr>")
        print("Listen for change of the 6 dip switch on the PIIO board")
        print("dip_nr: 1-6")
        print("")
        printb("piio led <led_nr> <on_or_off>")
        print("Turn on or off the user LED")
        print("led_nr: 1-6")
        print("on_or_off: on/off")
        print("")
        printb("piio buz <on_or_off>")
        print("Turn on or off the buzzer")
        print("on_or_off: on/off")
        print("")
        printb("piio lcd <text>")
        print("Print text to ssd1306 oled  LCD")
        print("")
        printb("piio gpio_get <pin>")
        print("Get status of RaspberryPI GPIO")
        print("This is marked with GPIO_3V3 and GPIO_5V on the PIIO board.")
        print("pin: 1-22 (PIIO board pin)")
        print("")
        printb("piio gpio_set <pin> <true/false>")
        print("Set status of RaspberryPI GPIO")
        print("This is marked with GPIO_3V3 and GPIO_5V on the PIIO board.")
        print("pin: 1-22 (PIIO board pin)")
        print("")
        printb("piio gpio_event <pin>")
        print("Listen for change of state on RaspberryPI GPIO")
        print("This is marked with GPIO_3V3 and GPIO_5V on the PIIO board.")
        print("pin: 1-22 (PIIO board pin)")
        print("")
        printb("piio gpio_click <pin>")
        print("Listen for click event on RaspberryPI GPIO")
        print("This is marked with GPIO_3V3 and GPIO_5V on the PIIO board.")
        print("pin: 1-22 (PIIO board pin)")
        print("")
        printb("piio xgpio_get <pin>")
        print("Get status of extra MCP2317 GPIO")
        print("This is marked with XGPIO on the PIIO board.")
        print("pin: 1-8 (PIIO board pin)")
        print("")
        printb("piio xgpio_set <pin> <true/false>")
        print("Set status of extra MCP2317 GPIO")
        print("This is marked with XGPIO on the PIIO board.")
        print("pin: 1-8")
        print("")
        printb("piio xgpio_event <pin>")
        print("Listen for change of state on extra MCP2317 GPIO")
        print("This is marked with XGPIO on the PIIO board.")
        print("pin: 1-8")
        print("")
        printb("piio xgpio_click <pin>")
        print("Listen for click event on extra MCP2317 GPIO")
        print("This is marked with XGPIO on the PIIO board.")
        print("pin: 1-8")
        print("")
        printb("piio power <pin> <true/false>")
        print("Set the status of the POWER pins")
        print("pin: 1-8")
        print("")
        printb("piio adc <channel>")
        print("Read the voltage value in on the 7 ADC pins")
        print("channel = 1 to 7")
        print("Return: 0 to 3.3")
        print("")
        printb("piio adc_event <channel>")
        print("Make method execute when the analog voltage in on the ADC change")
        print("channel = 1 to 7")
        print("")
        printb("piio dac <volt_1> <volt_2> <volt_3> <volt_4>")
        print("Write analog out from the 4 DAC pins (0 to 3.3v)")
        print("volt_1 to 4 = Voltage on pins (0 and 4095)")
        print("")
        printb("piio servo <servo_nr> <position>")
        print("Move a servo connected to the PIIO board.")
        print("servo_nr: 1-12")
        print("position: 0-255")
        print("")
        printb("piio pwm <pin> <value>")
        print("Set pwm value on one of the 4 PWM pins")
        print("The PWM pins is the same curcit that control the DC motors.")
        print("You can not use the PWM and MOTOR controller at the same time")
        print("pin: 1 to 4")
        print("value: 0 to 1023")
        print("")
        printb("piio motor <motor_1> <motor_1>")
        print("Set speed of the two DC motors.")
        print("-1023 = fullspeed reverse")
        print("0 = not moving")
        print("1023 = fullspeed forward")
        print("motor_1: -1023 to 1023")
        print("motor_2: -1023 to 1023")
        print("")
        printb("piio movement")
        print("Read movement with the gyro sensor.")
        print("")
        printb("piio rotation")
        print("Read mpu-6050 rotation angle in degrees for both the X & Y.")
        print("")
        printb("piio movement_event")
        print("Listen for movements on mpu-6050 and execute method on change.")
        print("")
        printb("piio rotation_event")
        print("Listen for mpu-6050 rotation angle in degrees and execute method on change.")
        print("")
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
        if command == "shutdown":
            shutdown()
        elif command == "volt":
            print volt()
        elif command == "volt_event":
            def adc_change(voltage):
                sys.stdout.write("Voltage="+str(voltage).ljust(20) + "\r")
                sys.stdout.flush()
            volt_event(adc_change)
            raw_input()
        elif command == "button":
            print button(para1)
        elif command == "button_event":
            def on_change(button_nr, status):
                sys.stdout.write(str(button_nr)+"="+str(status).ljust(10) + "\r")
                sys.stdout.flush()
            button_event(para1, on_change)
            raw_input()
        elif command == "button_click":
            def on_change(button_nr):
                sys.stdout.write("Click\n")
                sys.stdout.flush()
            button_click(para1, on_change)
            raw_input()
        elif command == "switch":
            print switch(para1)
        elif command == "switch_event":
            def on_change(dip_nr, status):
                sys.stdout.write(str(dip_nr)+"="+str(status).ljust(10) + "\r")
                sys.stdout.flush()
            switch_event(para1, on_change)
            raw_input()
        elif command == "led":
            led(para1, para2)
        elif command == "buz":
            buz(para1)
        elif command == "lcd":
            #Sending a event to the steelsquid daemon instead of executing it directly
            steelsquid_event.broadcast_event_external("pi_io_event", ["ssd1306", para1])
        elif command == "gpio_get":
            print gpio_get(para1)
        elif command == "gpio_set":
            gpio_set(para1, para2)
        elif command == "gpio_event":
            gpio_event(para1, gpio_event_callback_method)
            raw_input("Press any key to exit!")
        elif command == "gpio_click":
            gpio_click(para1, gpio_click_callback_method)
            raw_input("Press any key to exit!")
        elif command == "xgpio_get":
            print xgpio_get(para1)
        elif command == "xgpio_set":
            xgpio_set(para1, para2)
        elif command == "xgpio_event":
            xgpio_event(para1, xgpio_event_callback_method)
            raw_input("Press any key to exit!")
        elif command == "xgpio_click":
            xgpio_click(para1, xgpio_click_callback_method)
            raw_input("Press any key to exit!")
        elif command == "power":
            power(para1, para2)
        elif command == "adc":
            print adc(para1)
        elif command == "adc_event":
            def adc_change(channel, voltage):
                sys.stdout.write("Voltage("+str(channel)+")="+str(voltage).ljust(20) + "\r")
                sys.stdout.flush()
            adc_event(para1, adc_change)
            raw_input()
        elif command == "dac":
            dac(para1, para2, para3, para4)
        elif command == "servo":
            servo(para1, para2)
        elif command == "pwm":
            pwm(para1, para2)
        elif command == "motor":
            motor(para1, para2)
        elif command == "movement":
            print movement()
        elif command == "rotation":
            print rotation()
        elif command == "movement_event":
            def movement_change(x, y, z):
                sys.stdout.write("X="+str(x).ljust(8)+"Y="+str(y).ljust(8)+"Z="+str(z).ljust(8) + "\r")
                sys.stdout.flush()
            movement_event(movement_change)
            raw_input()
        elif command == "rotation_event":
            def rotation_changed(x, y):
                sys.stdout.write("X="+str(x).ljust(20)+"Y="+str(y).ljust(20) + "\r")
                sys.stdout.flush()
            rotation_event(rotation_changed)
            raw_input()
        else:
            print "Unknown command!!!"

