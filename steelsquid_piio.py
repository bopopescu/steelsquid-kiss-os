#!/usr/bin/python -OO


'''
Mostly wrapper functions for my steelsquid IO board
Use PIN number from the board.

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_trex

GAIN_6_144_V = 6144
GAIN_6_144_V = 6144
GAIN_4_096_V = 4096
GAIN_2_048_V = 2048
GAIN_1_024_V = 1024
GAIN_0_512_V = 512
GAIN_0_256_V = 256

BUTTON_UP = 8
BUTTON_DOWN = 4
BUTTON_LEFT = 6
BUTTON_RIGHT = 5
BUTTON_SELECT = 7

def gpio_pi_set_3v3(pin, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to 3.3v
    @param pin: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_3v3(gpio, state)


def gpio_pi_set_gnd(pin, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to ground
    @param pin: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_gnd(gpio, state)


def gpio_pi_get_3v3(pin):
    '''
    Get gpio pin state (connect gpio to 3.3v)
    @param pin: GPIO number (1 to 24)
    @return: True/False
    '''
    gpio = __convert_to_gpio(pin)
    return steelsquid_pi.gpio_get_3v3(gpio)


def gpio_pi_get_gnd(pin):
    '''
    Get gpio pin state
    @param pin: GPIO number (1 to 24)
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    gpio = __convert_to_gpio(pin)
    return steelsquid_pi.gpio_get_gnd(gpio)


def gpio_pi_toggle_3v3(pin):
    '''
    Toggle gpio pin to hight/low on a pin connecte to 3.3v
    @param pin: GPIO number (1 to 24)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_toggle_3v3(gpio)

def gpio_pi_toggle_gnd(pin):
    '''
    Toggle gpio pin to hight/low on a pin connecte to gnd
    @param pin: GPIO number (1 to 24)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_toggle_3v3(gpio)


def gpio_pi_event_3v3(pin, high_method, low_method):
    '''
    Listen for events on gpio pin and 3.3v
    @param pin: GPIO number (1 to 24)
    @param high_method: On high
    @param low_method: On low
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_event_3v3(gpio, high_method, low_method)


def gpio_pi_event_gnd(pin, high_method, low_method):
    '''
    Listen for events on gpio pin and ground
    @param pin: GPIO number (1 to 24)
    @param high_method: On high
    @param low_method: On low
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_event_gnd(gpio, high_method, low_method)


def gpio_pi_click_3v3(pin, callback_method):
    '''
    Connect a button to gpio pin and 3.3v
    Will fire when button is released. If press more than 1s it will be ignore
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_click_3v3(gpio, callback_method)


def gpio_pi_click_gnd(pin, callback_method):
    '''
    Connect a button to gpio pin and ground
    Will fire when button is released. If press more than 1s it will be ignore
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_click_gnd(gpio, callback_method)


def gpio_pi_flash_3v3(pin, enable):
    '''
    Flash a gpio on and off (1 second) connected to 3.3v

    @param pin: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_3v3(gpio, enable)
    
    
def gpio_pi_flash_gnd(pin, enable):
    '''
    Flash a gpio on and off (1 second) connected to ground

    @param pin: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_gnd(gpio, enable)


def gpio_pi_flash_3v3_timer(pin, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_3v3_timer(gpio, seconds)
   
   
def gpio_pi_flash_gnd_timer(pin, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_gnd_timer(gpio, seconds)
 
 
def gpio_pi_set_3v3_timer(pin, seconds):
    '''
    On for sertant time
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_3v3_timer(gpio, seconds)
   
   
def gpio_pi_set_gnd_timer(pin, seconds):
    '''
    On for sertant time
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_gnd_timer(gpio, seconds)


def __convert_to_gpio(pin):
    pin = int(pin)
    if pin == 1:
        return 21
    elif pin == 2:
        return 20
    elif pin == 3:
        return 16
    elif pin == 4:
        return 12
    elif pin == 5:
        return 25
    elif pin == 6:
        return 24
    elif pin == 7:
        return 23
    elif pin == 8:
        return 18
    elif pin == 9:
        return 15
    elif pin == 10:
        return 14
    elif pin == 11:
        return 26
    elif pin == 12:
        return 19
    elif pin == 13:
        return 13
    elif pin == 14:
        return 6
    elif pin == 15:
        return 5
    elif pin == 16:
        return 22
    elif pin == 17:
        return 27
    elif pin == 18:
        return 17
    elif pin == 19:
        return 4
    

def led_error(status):
    '''
    Turn on / off the red LED
    LEDR
    '''
    steelsquid_pi.mcp23017_set(23, 9, status)


def led_error_toggle():
    '''
    Toggle on / off the red LED
    LEDR
    '''
    steelsquid_pi.mcp23017_toggle(23, 9)


def led_error_flash(status):
    '''
    Flash on / off the red LED
    LEDR
    '''
    steelsquid_pi.mcp23017_flash(23, 9, status)


def led_error_timer(seconds):
    '''
    Turn on LED for number of seconds
    LEDR
    '''
    steelsquid_pi.mcp23017_set_timer(23, 9, seconds)


def led_error_flash_timer(seconds):
    '''
    Flash on / off the red LED for number fo seconds
    LEDR
    '''
    steelsquid_pi.mcp23017_flash_timer(23, 9, seconds)


def led_ok(status):
    '''
    Turn on / off the green LED
    LEDG
    '''
    steelsquid_pi.mcp23017_set(23, 10, status)


def led_ok_toggle():
    '''
    Toggle on / off the green LED
    LEDG
    '''
    steelsquid_pi.mcp23017_toggle(23, 10)


def led_ok_flash(status):
    '''
    Flash on / off the green LED
    LEDG
    '''
    steelsquid_pi.mcp23017_flash(23, 10, status)


def led_ok_timer(seconds):
    '''
    Turn on LED for number of seconds
    LEDG
    '''
    steelsquid_pi.mcp23017_set_timer(23, 10, seconds)


def led_ok_flash_timer(seconds):
    '''
    Flash on / off the green LED for number fo seconds
    LEDG
    '''
    steelsquid_pi.mcp23017_flash_timer(23, 10, seconds)


def relay(relay_nr, status):
    '''
    relay_nr = 1 to 4
    Turn on / off the relay
    '''
    relay_nr = relay_nr + 1
    steelsquid_pi.mcp23017_set(23, relay_nr, status)


def relay_toggle(relay_nr):
    '''
    relay_nr = 1 to 4
    Flash on / off the relay
    '''
    relay_nr = relay_nr + 1
    steelsquid_pi.mcp23017_toggle(23, relay_nr)


def relay_flash(relay_nr, status):
    '''
    relay_nr = 1 to 4
    Flash on / off the relay
    '''
    relay_nr = relay_nr + 1
    steelsquid_pi.mcp23017_flash(23, relay_nr, status)


def relay_timer(relay_nr, seconds):
    '''
    relay_nr = 1 to 4
    Turn on relay for number of seconds
    '''
    relay_nr = relay_nr + 1
    steelsquid_pi.mcp23017_set_timer(23, relay_nr, seconds)


def relay_flash_timer(relay_nr, seconds):
    '''
    relay_nr = 1 to 4
    Flash on / off the relayfor number fo seconds
    '''
    relay_nr = relay_nr + 1
    steelsquid_pi.mcp23017_flash_timer(23, relay_nr, seconds)


def gpio_22_xv(pin_nr, status):
    '''
    pin_nr = 1 to 16
    Turn on / off the power ouput (uln2801)
    GPIO_22_XV
    '''
    pin_nr = int(pin_nr)
    steelsquid_pi.mcp23017_set(22, pin_nr-1, status)


def gpio_22_xv_toggle(pin_nr):
    '''
    pin_nr = 1 to 16
    Toggle on / off the power ouput (uln2801)
    GPIO_22_XV
    '''
    pin_nr = int(pin_nr)
    steelsquid_pi.mcp23017_toggle(22, pin_nr-1)

def gpio_22_xv_flash(pin_nr, status):
    '''
    pin_nr = 1 to 16
    Flash on / off the power ouput (uln2801)
    GPIO_22_XV
    '''
    pin_nr = int(pin_nr)
    steelsquid_pi.mcp23017_flash(22, pin_nr-1, status)


def gpio_22_xv_timer(pin_nr, seconds):
    '''
    pin_nr = 1 to 16
    Turn on power ouput (uln2801) for number of seconds
    GPIO_22_XV
    '''
    pin_nr = int(pin_nr)
    steelsquid_pi.mcp23017_set_timer(22, pin_nr-1, seconds)


def gpio_22_xv_flash_timer(pin_nr, seconds):
    '''
    pin_nr = 1 to 16
    Flash on / off the power ouput (uln2801) for number fo seconds
    GPIO_22_XV
    '''
    pin_nr = int(pin_nr)
    steelsquid_pi.mcp23017_flash_timer(22, pin_nr-1, seconds)


def sum(status):
    '''
    Tirn on/off the summer
    SUM
    '''
    steelsquid_pi.mcp23017_set(23, 15, status)


def sum_flash(status):
    '''
    SUM
    Flash on / off the summer
    '''
    steelsquid_pi.mcp23017_flash(23, 15, status)


def sum_toggle():
    '''
    SUM
    Toggle on / off the summer
    '''
    steelsquid_pi.mcp23017_toggle(23, 15)


def sum_timer(seconds):
    '''
    SUM
    Turn on summer for number of seconds
    '''
    steelsquid_pi.mcp23017_set_timer(23, 15, seconds)


def sum_flash_timer(seconds):
    '''
    SUM
    Flash on / off the summer for number fo seconds
    '''
    steelsquid_pi.mcp23017_flash_timer(23, 15, seconds)


def button(which_button):
    '''
    Get status on button
    which_button = BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_SELECT
    '''
    button_nr = int(button_nr)
    return steelsquid_pi.mcp23017_get(23, which_button)


def button_click(which_button, callback_method):
    '''
    Listen for button click
    which_button = BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_SELECT
    '''
    steelsquid_pi.mcp23017_click(23, which_button, callback_method)


def dip(dip_nr):
    '''
    Get status on DIP
    dip_nr = 1 to 4
    '''
    dip_nr = int(dip_nr)
    if dip_nr == 1:
        return steelsquid_pi.mcp23017_get(23, 11)
    elif dip_nr == 2:
        return steelsquid_pi.mcp23017_get(23, 12)
    elif dip_nr == 3:
        return steelsquid_pi.mcp23017_get(23, 14)
    elif dip_nr == 4:
        return steelsquid_pi.mcp23017_get(23, 13)


def dip_event(dip_nr, callback_method):
    '''
    Listen for DIP change
    dip_nr = 1 to 4
    '''
    dip_nr = int(dip_nr)
    if dip_nr == 1:
        steelsquid_pi.mcp23017_event(23, 11, callback_method)
    elif dip_nr == 2:
        steelsquid_pi.mcp23017_event(23, 12, callback_method)
    elif dip_nr == 3:
        steelsquid_pi.mcp23017_event(23, 14, callback_method)
    elif dip_nr == 4:
        steelsquid_pi.mcp23017_event(23, 13, callback_method)


def gpio_20_3v3_get(pin):
    '''
    Get status on extra gpio 3v3
    GPIO_20_3V3
    pin = 1 to 16
    '''
    pin = int(pin)
    return steelsquid_pi.mcp23017_get(20, pin - 1)


def gpio_20_3v3_click(pin, callback_method):
    '''
    Listen for click on extra gpio 3v3
    GPIO_20_3V3
    pin = 1 to 8
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_click(20, pin-1, callback_method)


def gpio_20_3v3_event(pin, callback_method):
    '''
    Listen for change on extra gpio 3v3
    GPIO_20_3V3
    pin = 1 to 8
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_event(20, pin-1, callback_method)


def gpio_20_3v3_set(pin, status):
    '''
    pin = 1 to 16
    Turn on / off the extra gpio 3v3
    GPIO_20_3V3
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_set(20, pin-1, status)


def gpio_20_3v3_toggle(pin):
    '''
    pin = 1 to 16
    Toggle on / off the extra gpio 3v3
    GPIO_20_3V3
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_toggle(20, pin-1)

def gpio_20_3v3_flash(pin, status):
    '''
    pin = 1 to 16
    Flash on / off the extra gpio 3v3
    GPIO_20_3V3
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_flash(20, pin-1, status)


def gpio_20_3v3_timer(pin, seconds):
    '''
    pin = 1 to 16
    Turn on extra 3v3 gpio for number of seconds
    GPIO_20_3V3
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_set_timer(20, pin-1, seconds)


def gpio_20_3v3_flash_timer(pin, seconds):
    '''
    pin = 1 to 16
    Flash on / off the extra 3v3 gpio for number fo seconds
    GPIO_20_3V3
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_flash_timer(20, pin-1, seconds)





def gpio_21_5v_get(pin):
    '''
    Get status on extra gpio 5V
    GPIO_21_5V
    pin = 1 to 16
    '''
    pin = int(pin)
    return steelsquid_pi.mcp23017_get(21, pin - 1)


def gpio_21_5v_click(pin, callback_method):
    '''
    Listen for click on extra gpio 5V
    GPIO_21_5V
    pin = 1 to 8
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_click(21, pin-1, callback_method)


def gpio_21_5v_event(pin, callback_method):
    '''
    Listen for change on extra gpio 5V
    GPIO_21_5V
    pin = 1 to 8
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_event(21, pin-1, callback_method)


def gpio_21_5v_set(pin, status):
    '''
    pin = 1 to 16
    Turn on / off the extra gpio 5V
    GPIO_21_5V
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_set(21, pin-1, status)


def gpio_21_5v_toggle(pin):
    '''
    pin = 1 to 16
    Toggle on / off the extra gpio 5V
    GPIO_21_5V
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_toggle(21, pin-1)

def gpio_21_5v_flash(pin, status):
    '''
    pin = 1 to 16
    Flash on / off the extra gpio 5V
    GPIO_21_5V
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_flash(21, pin-1, status)


def gpio_21_5v_timer(pin, seconds):
    '''
    pin = 1 to 16
    Turn on extra 5V gpio for number of seconds
    GPIO_21_5V
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_set_timer(21, pin-1, seconds)


def gpio_21_5v_flash_timer(pin, seconds):
    '''
    pin = 1 to 16
    Flash on / off the extra 5V gpio for number fo seconds
    GPIO_21_5V
    '''
    pin = int(pin)
    steelsquid_pi.mcp23017_flash_timer(21, pin-1, seconds)


def adc_48_5v(pin, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    pin = 1 to 8
    '''
    pin = int(pin) + 1
    return steelsquid_pi.ads1015(48, 0, gain)
        

def adc_48_5v_event(pin, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    pin = 1 to 8
    '''
    pin = int(pin) + 1
    return steelsquid_pi.ads1015_event(48, 0, callback_method, gain)


def adc_49_5v(pin, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    pin = 1 to 8
    '''
    pin = int(pin) + 1
    return steelsquid_pi.ads1015(49, 0, gain)
        

def adc_49_5v_event(pin, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    pin = 1 to 8
    '''
    pin = int(pin) + 1
    return steelsquid_pi.ads1015_event(49, 0, callback_method, gain)


def dac_61_5v(volt0, volt1, volt2, volt3):
    '''
    Write analog out from MCP4728 (0 to 5v)
    volt1 to 3 = Voltage on pins (0 and 4095)
    '''
    steelsquid_pi.mcp4728(61, volt0, volt1, volt2, volt3)


def lcd_write(text, number_of_seconds = 0, force_setup = True):
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
    steelsquid_pi.nokia5110_write(text, number_of_seconds, force_setup)
            

def measure_distance(trig_gpio, echo_gpio, force_setup = False):
    '''
    Measure_distance with a with HC-SR04.
    @param trig_gpio: The trig gpio
    @param echo_gpio: The echo gpio
    @param force_setup: Force setup of pins
    @return: The distance in cm (-1 = unable to mesure)
    '''
    steelsquid_pi.hcsr04_distance(trig_gpio, echo_gpio, force_setup)


def servo_move(servo, value):
    '''
    Move Adafruit 16-channel I2c servo to position (pwm value)
    @param servo: 0 to 15
    @param value: min=150, max=600 (may differ between servos)
    '''
    steelsquid_pi.rbada70_move(servo, value)


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


def aaa(bb):
    print bb
    
if __name__ == '__main__':
    analog_event(1, aaa, GAIN_4_096_V)
    raw_input("Press Enter to continue...")



