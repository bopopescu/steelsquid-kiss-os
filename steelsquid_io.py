#!/usr/bin/python -OO


'''
Mostly wrapper functions (hard coded adresses and pins) for my steelsquid IO board
http://www.steelsquid.org/steelsquid-io

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

version = "1.0"

def cleanup():
    '''
    Clean all event detection (click, blink...)
    '''
    steelsquid_pi.cleanup()


def gpio_set_3v3(pin, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to 3.3v
    @param pin: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_3v3(gpio, state)


def gpio_set_gnd(pin, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to ground
    @param pin: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_set_gnd(gpio, state)


def gpio_get_3v3(pin):
    '''
    Get gpio pin state (connect gpio to 3.3v)
    @param pin: GPIO number (1 to 24)
    @return: True/False
    '''
    gpio = __convert_to_gpio(pin)
    return steelsquid_pi.gpio_get_3v3(gpio)


def gpio_get_gnd(pin):
    '''
    Get gpio pin state
    @param pin: GPIO number (1 to 24)
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    gpio = __convert_to_gpio(pin)
    return steelsquid_pi.gpio_get_gnd(gpio)


def gpio_event_3v3(pin, callback_method):
    '''
    Listen for events on gpio pin and 3.3v
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_event_3v3(gpio, callback_method)


def gpio_event_gnd(pin, callback_method):
    '''
    Listen for events on gpio pin and ground
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(pin, status)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_event_gnd(gpio, callback_method)


def gpio_click_3v3(pin, callback_method):
    '''
    Connect a button to gpio pin and 3.3v
    Will fire when button is released. If press more than 1s it will be ignore
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_click_3v3(gpio, callback_method)


def gpio_click_gnd(pin, callback_method):
    '''
    Connect a button to gpio pin and ground
    Will fire when button is released. If press more than 1s it will be ignore
    @param pin: GPIO number (1 to 24)
    @param callback_method: execute this method on event (paramater is the gpio)
                            callback_method(pin)
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_click_gnd(gpio, callback_method)


def gpio_flash_3v3(pin, enable):
    '''
    Flash a gpio on and off connected to 3.3v

    @param pin: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_3v3(gpio, enable)
    
    
def gpio_flash_gnd(pin, enable):
    '''
    Flash a gpio on and off connected to ground

    @param pin: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    gpio = __convert_to_gpio(pin)
    steelsquid_pi.gpio_flash_gnd(gpio, enable)


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
    elif pin == 23:
        return 19
    elif pin == 24:
        return 26
    

def led_err(status):
    '''
    Turn on / off the red error LED
    '''
    steelsquid_pi.mcp23017_set(27, 4, status)


def led_err_flash(status):
    '''
    Flash on / off the red error LED
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    steelsquid_pi.mcp23017_flash(27, 4, status)


def led_ok(status):
    '''
    Turn on / off the green OK LED
    '''
    steelsquid_pi.mcp23017_set(27, 3, status)


def led_ok_flash(status):
    '''
    Flash on / off the green OK LED
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    steelsquid_pi.mcp23017_flash(27, 3, status)


def led_net(status):
    '''
    Turn on / off the yellow network LED
    '''
    steelsquid_pi.mcp23017_set(27, 5, status)


def led_net_flash(status):
    '''
    Flash on / off the yellow NET LED
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    steelsquid_pi.mcp23017_flash(27, 5, status)


def led_bt(status):
    '''
    Turn on / off the blue bluetooth LED
    '''
    steelsquid_pi.mcp23017_set(27, 6, status)


def led_net_flash(status):
    '''
    Flash on / off the blue bluetooth LED
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    steelsquid_pi.mcp23017_flash(27, 6, status)


def led(led_no, status):
    '''
    Turn on / off user leds
    '''
    if led_no == 1:
        steelsquid_pi.mcp23017_set(27, 7, status)
    elif led_no == 2:
        steelsquid_pi.mcp23017_set(26, 0, status)
    elif led_no == 3:
        steelsquid_pi.mcp23017_set(26, 1, status)


def led_flash(led_no, status):
    '''
    Flash on / off user leds
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    if led_no == 1:
        steelsquid_pi.mcp23017_flash(27, 7, status)
    elif led_no == 2:
        steelsquid_pi.mcp23017_flash(26, 0, status)
    elif led_no == 3:
        steelsquid_pi.mcp23017_flash(26, 1, status)


def summer(status):
    '''
    Turn on/off the summer
    SUM
    '''
    steelsquid_pi.mcp23017_set(26, 14, status)


def summer_flash(status):
    '''
    SUM
    Flash on / off the summer
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    steelsquid_pi.mcp23017_flash(26, 14, status)


def button(which_button, callback_method):
    '''
    Listen for user button clicks
    which_button = 1-6
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    '''
    which_button = int(which_button)
    if which_button == 1:
        which_button = 13
    elif which_button == 2:
        which_button = 12
    elif which_button == 3:
        which_button = 11
    elif which_button == 4:
        which_button = 10
    elif which_button == 5:
        which_button = 9
    elif which_button == 6:
        which_button = 8
    steelsquid_pi.mcp23017_click(26, which_button, callback_method)


def dip(dip_nr, callback_method):
    '''
    Listen for DIP change
    dip_nr = 1 to 6
    @param callback_method: execute this method on event (paramater is the address, gpio and status (True/False))
                            callback_method(address, pin, status)
    '''
    dip_nr = int(dip_nr) + 1
    steelsquid_pi.mcp23017_event(26, dip_nr, callback_method)


def button_info(callback_method):
    '''
    Listen for info button click
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    '''
    steelsquid_pi.mcp23017_click(27, 0, callback_method)


def button_power_off(callback_method):
    '''
    Listen for power off button click
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    '''
    steelsquid_pi.mcp23017_click(27, 1, callback_method)
    
    
def power_off():
    '''
    Send a power of signal, the delay surcit will wait for some seconds (selectable by the DELAY_POWER_OF trim)
    '''
    steelsquid_pi.mcp23017_set(26, 15, True)
    steelsquid_utils.execute_system_command_blind(['shutdown', '-h', 'now'])


def xgpio_get(pin_nr):
    '''
    Get hight/low on extra gpio
    pin_nr = 1 to 16
    '''
    pin_nr = int(pin_nr) - 1
    return steelsquid_pi.mcp23017_get(20, pin_nr)
    
        
def xgpio_set(pin_nr, status):
    '''
    Set hight/low on extra gpio
    pin_nr = 1 to 16
    '''
    pin_nr = int(pin_nr) - 1
    steelsquid_pi.mcp23017_set(20, pin_nr, status)


def xgpio_toggle(pin_nr):
    '''
    Toggle hight/low on extra gpio
    pin_nr = 1 to 16
    '''
    pin_nr = int(pin_nr) - 1
    steelsquid_pi.mcp23017_toggle(20, pin_nr)


def xgpio_toggle_current(pin_nr):
    '''
    Get current toggle hight/low from extra gpio
    pin_nr = 1 to 16
    '''
    pin_nr = int(pin_nr) - 1
    return steelsquid_pi.mcp23017_toggle_current(20, pin_nr)


def xgpio_flash(pin_nr, status):
    '''
    Toggle gpio pin to hight/low on a mcp
    @param pin_nr: 1 to 16
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    pin_nr = int(pin_nr) - 1
    return steelsquid_pi.mcp23017_flash(20, pin_nr, status)


def xgpio_click(pin_nr, callback_method):
    '''
    Listen for click
    @param pin_nr: 1 to 16
    @param callback_method: execute this method on event (paramater is the address and gpio)
                            callback_method(address, pin)
    '''
    pin_nr = int(pin_nr) - 1
    return steelsquid_pi.mcp23017_click(20, callback_method)


def xgpio_event(pin_nr, callback_method):
    '''
    Listen for event
    @param pin_nr: 1 to 16
    @param callback_method: execute this method on event (paramater is the address, gpio and status (True/False))
                            callback_method(address, pin, status)
    '''
    pin_nr = int(pin_nr) - 1
    return steelsquid_pi.mcp23017_event(20, callback_method)


def power(pin_nr, status):
    '''
    Turn on / off the power ouput (uln2801)
    pin_nr = 1 to 8
    '''
    pin_nr = int(pin_nr) + 7
    steelsquid_pi.mcp23017_set(27, pin_nr, status)


def power_toggle(pin_nr):
    '''
    Toggle power ouput (uln2801)
    pin_nr = 1 to 8
    '''
    pin_nr = int(pin_nr) + 7
    steelsquid_pi.mcp23017_toggle(27, pin_nr)


def power_toggle_current(pin_nr):
    '''
    Get current toggle hight/low from power ouput (uln2801)
    pin_nr = 1 to 8
    '''
    pin_nr = int(pin_nr) + 7
    return steelsquid_pi.mcp23017_toggle_current(27, pin_nr)


def power_flash(pin_nr, status):
    '''
    Toggle power ouput (uln2801) pin to hight/low
    @param pin_nr: 1 to 8
    @param status: Strart or stop the flashing (True/False)
                   None = only flash once
    '''
    pin_nr = int(pin_nr) + 7
    return steelsquid_pi.mcp23017_flash(27, pin_nr, status)


def adc_1(pin, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015
    pin = 1 to 4
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015(48, pin, gain)
        

def adc_1_median(pin, gain=GAIN_6_144_V, samples=16):
    '''
    Read analog in from ADS1015
    pin = 1 to 3
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015_median(48, pin, gain, samples)


def adc_1_event(pin, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    pin = 1 to 4
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(address, pin, value)
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015_event(48, pin, callback_method, gain)


def adc_2(pin, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015
    pin = 1 to 3
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015(49, pin, gain)


def adc_2_median(pin, gain=GAIN_6_144_V, samples=16):
    '''
    Read analog in from ADS1015
    pin = 1 to 3
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015_median(49, pin, gain, samples)


def adc_2_event(pin, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    pin = 1 to 3
    @param callback_method: execute this method on event (paramater is the gpio and status (True/False))
                            callback_method(address, pin, value)
    '''
    pin = int(pin) - 1
    return steelsquid_pi.ads1015_event(49, pin, callback_method, gain)


def voltage():
    '''
    Get voltage in to Steelsquid IO board as a float (V_IN)
    '''
    return adc_2_median(4) / float(steelsquid_utils.get_parameter("voltage_divider", "0.15"))







def dac_61_5v(volt1, volt2, volt3, volt4):
    '''
    Write analog out from MCP4728 (0 to 5v)
    volt1 to 4 = Voltage on pins (0 and 4095)
    '''
    steelsquid_pi.mcp4728(61, volt1, volt2, volt3, volt4)


def lcd_write(text, number_of_seconds = 0):
    '''
    Print text to the Oled display
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
            

def measure_distance(trig_gpio, echo_gpio, force_setup = False):
    '''
    Measure_distance with a with HC-SR04.
    @param trig_gpio: The trig gpio
    @param echo_gpio: The echo gpio
    @param force_setup: Force setup of pins
    @return: The distance in cm (-1 = unable to mesure)
    '''
    steelsquid_pi.hcsr04_distance(trig_gpio, echo_gpio, force_setup)


def servo(servo, value):
    '''
    Move Adafruit 16-channel I2c servo to position (pwm value)
    @param servo: 1 to 16
    @param value: min=150, max=600 (may differ between servos)
    Set max/min value in the paramaters: servo_position_max, servo_position_min
    '''
    servo = int(servo)
    value = int(value)
    if value>servo_position_max:
        value = servo_position_max
    elif value<servo_position_min:
        value = servo_position_min
    servo_position = value
    steelsquid_pi.rbada70_move(servo-1, value)


def servo_move(servo, value):
    '''
    Move Adafruit 16-channel I2c servo to position (pwm value)
    @param servo: 1 to 16
    @param value: increase/decrice with this value (min=150, max=600 (may differ between servos))
    Set max/min value in the paramaters: servo_position_max, servo_position_min
    '''
    global servo_position
    servo_position = servo_position + int(value)
    if servo_position>servo_position_max:
        servo_position = servo_position_max
    elif servo_position<servo_position_min:
        servo_position = servo_position_min
    servo = int(servo)
    steelsquid_pi.rbada70_move(servo-1, servo_position)


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


def trex_motor_last_change():
    '''
    Last timestamp when motor chnge values
    @return: last time i ms
    '''
    return steelsquid_trex.motor_last_change


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
    import sys
    if len(sys.argv)==1:
        from steelsquid_utils import printb
        printb("Some commands for Steelsquid IO board.")
        print("")
        printb("io poweroff")
        print("Power of the IO board")
    else:
        command = sys.argv[1]
        if command == "poweroff":
            steelsquid_utils.execute_system_command_blind(["steelsquid-event", "poweroff"])
        else:
            print "Unknown command!!!"
