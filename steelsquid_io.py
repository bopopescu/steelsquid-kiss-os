#!/usr/bin/python -OO


'''
Mostly wrapper functions for my steelsquid IO board

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU General Public License
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_pi

GAIN_6_144_V = 6144
GAIN_4_096_V = 4096
GAIN_2_048_V = 2048
GAIN_1_024_V = 1024
GAIN_0_512_V = 512
GAIN_0_256_V = 256

sabertooth = None

def gpio_set_3v3(gpio, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to 3.3v
    @param gpio: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_set_3v3(gpio, state)


def gpio_set_gnd(gpio, state):
    '''
    set gpio pin to hight (true) or low (false) on a pin connecte to ground
    @param gpio: GPIO number (1 to 24)
    @param state: True/False
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_set_gnd(gpio, state)


def gpio_get_3v3(gpio):
    '''
    Get gpio pin state (connect gpio to 3.3v)
    @param gpio: GPIO number (1 to 24)
    @return: True/False
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    return steelsquid_pi.gpio_get_3v3(gpio)


def gpio_get_gnd(gpio):
    '''
    Get gpio pin state
    @param gpio: GPIO number (1 to 24)
    @return: 0 / GPIO.LOW / False or 1 / GPIO.HIGH / True
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    return steelsquid_pi.gpio_get_gnd(gpio)


def gpio_toggle_3v3(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to 3.3v
    @param gpio: GPIO number (1 to 24)
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_toggle_3v3(gpio)

def gpio_toggle_gnd(gpio):
    '''
    Toggle gpio pin to hight/low on a pin connecte to gnd
    @param gpio: GPIO number (1 to 24)
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_toggle_3v3(gpio)


def gpio_event_3v3(gpio, high_method, low_method):
    '''
    Listen for events on gpio pin and 3.3v
    @param gpio: GPIO number (1 to 24)
    @param high_method: On high
    @param low_method: On low
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_event_3v3(gpio, high_method, low_method)


def gpio_event_gnd(gpio, high_method, low_method):
    '''
    Listen for events on gpio pin and ground
    @param gpio: GPIO number (1 to 24)
    @param high_method: On high
    @param low_method: On low
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_event_gnd(gpio, high_method, low_method)


def gpio_click_3v3(gpio, callback_method):
    '''
    Connect a button to gpio pin and 3.3v
    Will fire when button is released. If press more than 1s it will be ignore
    @param gpio: GPIO number (1 to 24)
    @param callback_method: execute this method on event
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_click_3v3(gpio, callback_method)


def gpio_click_gnd(gpio, callback_method):
    '''
    Connect a button to gpio pin and ground
    Will fire when button is released. If press more than 1s it will be ignore
    @param gpio: GPIO number (1 to 24)
    @param callback_method: execute this method on event
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_click_gnd(gpio, callback_method)


def gpio_flash_3v3(gpio, enable):
    '''
    Flash a gpio on and off (1 second) connected to 3.3v

    @param gpio: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_flash_3v3(gpio, enable)
    
    
def gpio_flash_gnd(gpio, enable):
    '''
    Flash a gpio on and off (1 second) connected to ground

    @param gpio: The gpio to flash (1 to 24)
    @param enable: Strart or stop the flashing (True/False)
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_flash_gnd(gpio, enable)


def gpio_flash_3v3_timer(gpio, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_flash_3v3_timer(gpio, seconds)
   
   
def gpio_flash_gnd_timer(gpio, seconds):
    '''
    Flash a gpio on and off for sertant time
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_flash_gnd_timer(gpio, seconds)
 
 
def gpio_set_3v3_timer(gpio, seconds):
    '''
    On for sertant time
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_set_3v3_timer(gpio, seconds)
   
   
def gpio_set_gnd_timer(gpio, seconds):
    '''
    On for sertant time
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.gpio_set_gnd_timer(gpio, seconds)
    
    
def lcd_write_text(text, number_of_seconds = 0, force_setup = True, is_i2c=True):
    '''
    Print text to HDD44780 compatible LCD
    @param text: Text to write (\n or \\ = new line)
    @param number_of_seconds: How long to show this message, then show the last message again (if there was one)
                              < 1 Show for ever
    EX1: Message in the screen: A message
         lcd_write_text("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A message
    EX2: Message in the screen: 
         lcd_write_text("A new message", number_of_seconds = 10)
         Message in the screen: A new message
         After ten seconds:
         Message in the screen: A new message
    @param force_setup: Force setup of pins
    @param is_icc: Is the LCD connected by i2c
    The text can also be a list, will join the list with spaces between.
    '''
    steelsquid_pi.lcd_write_text(text, number_of_seconds = 0, force_setup = True, is_i2c=True)
    

def measure_distance(trig_gpio, echo_gpio, force_setup = False):
    '''
    Measure_distance with a with HC-SR04.
    @param trig_gpio: The trig gpio
    @param echo_gpio: The echo gpio
    @param force_setup: Force setup of pins
    @return: The distance in cm (-1 = unable to mesure)
    '''
    steelsquid_pi.measure_distance(trig_gpio, echo_gpio, force_setup = False)


def servo_move(servo, value):
    '''
    Move servo to position (pwm value)
    @param servo: 0 to 15
    @param value: min=150, max=600 (may differ between servos)
    '''
    steelsquid_pi.servo_move(servo, value)


def red_led(status):
    '''
    Turn on / off the red LED
    '''
    steelsquid_pi.mcp_set(20, 9, status)


def red_led_flash(status):
    '''
    Flash on / off the red LED
    '''
    steelsquid_pi.mcp_flash(20, 9, status)


def red_led_timer(seconds):
    '''
    Turn on LED for number of seconds
    '''
    steelsquid_pi.mcp_set_timer(20, 9, seconds)


def red_led_flash_timer(seconds):
    '''
    Flash on / off the red LED for number fo seconds
    '''
    steelsquid_pi.mcp_flash_timer(20, 9, seconds)


def green_led(status):
    '''
    Turn on / off the green LED
    '''
    steelsquid_pi.mcp_set(20, 8, status)


def green_led_flash(status):
    '''
    Flash on / off the green LED
    '''
    steelsquid_pi.mcp_flash(20, 8, status)


def green_led_timer(seconds):
    '''
    Turn on LED for number of seconds
    '''
    steelsquid_pi.mcp_set_timer(20, 8, seconds)


def green_led_flash_timer(seconds):
    '''
    Flash on / off the green LED for number fo seconds
    '''
    steelsquid_pi.mcp_flash_timer(20, 8, seconds)


def relay(relay_nr, status):
    '''
    relay_nr = 1 to 4
    Turn on / off the relay
    '''
    if relay_nr == 1:
        steelsquid_pi.mcp_set(20, 10, status)
    elif relay_nr == 2:
        steelsquid_pi.mcp_set(20, 11, status)
    elif relay_nr == 3:
        steelsquid_pi.mcp_set(20, 12, status)
    elif relay_nr == 4:
        steelsquid_pi.mcp_set(20, 13, status)


def relay_flash(relay_nr, status):
    '''
    relay_nr = 1 to 4
    Flash on / off the relay
    '''
    if relay_nr == 1:
        steelsquid_pi.mcp_flash(20, 10, status)
    elif relay_nr == 2:
        steelsquid_pi.mcp_flash(20, 11, status)
    elif relay_nr == 3:
        steelsquid_pi.mcp_flash(20, 12, status)
    elif relay_nr == 4:
        steelsquid_pi.mcp_flash(20, 13, status)


def relay_timer(relay_nr, seconds):
    '''
    relay_nr = 1 to 4
    Turn on relay for number of seconds
    '''
    if relay_nr == 1:
        steelsquid_pi.mcp_set_timer(20, 10, seconds)
    elif relay_nr == 2:
        steelsquid_pi.mcp_set_timer(20, 11, seconds)
    elif relay_nr == 3:
        steelsquid_pi.mcp_set_timer(20, 12, seconds)
    elif relay_nr == 4:
        steelsquid_pi.mcp_set_timer(20, 13, seconds)


def relay_flash_timer(relay_nr, seconds):
    '''
    relay_nr = 1 to 4
    Flash on / off the relayfor number fo seconds
    '''
    if relay_nr == 1:
        steelsquid_pi.mcp_flash_timer(20, 10, seconds)
    elif relay_nr == 2:
        steelsquid_pi.mcp_flash_timer(20, 11, seconds)
    elif relay_nr == 3:
        steelsquid_pi.mcp_flash_timer(20, 12, seconds)
    elif relay_nr == 4:
        steelsquid_pi.mcp_flash_timer(20, 13, seconds)


def power_out(power_nr, status):
    '''
    power_nr = 1 to 8
    Turn on / off the power ouput (uln2801)
    '''
    steelsquid_pi.mcp_set(21, power_nr-1, status)


def power_out_flash(power_nr, status):
    '''
    power_nr = 1 to 8
    Flash on / off the power ouput (uln2801)
    '''
    steelsquid_pi.mcp_flash(21, power_nr-1, status)


def power_out_timer(power_nr, seconds):
    '''
    power_nr = 1 to 8
    Turn on power ouput (uln2801) for number of seconds
    '''
    steelsquid_pi.mcp_set_timer(21, power_nr-1, seconds)


def power_out_flash_timer(power_nr, seconds):
    '''
    power_nr = 1 to 8
    Flash on / off the power ouput (uln2801) for number fo seconds
    '''
    steelsquid_pi.mcp_flash_timer(21, power_nr-1, seconds)


def summer(status):
    '''
    Tirn on/off the summer
    '''
    steelsquid_pi.mcp_set(20, 14, status)


def summer_flash(status):
    '''
    power_nr = 1 to 8
    Flash on / off the power ouput (uln2801)
    '''
    steelsquid_pi.mcp_flash(20, 14, status)


def summer_timer(seconds):
    '''
    power_nr = 1 to 8
    Turn on power ouput (uln2801) for number of seconds
    '''
    steelsquid_pi.mcp_set_timer(20, 14, seconds)


def summer_flash_timer(seconds):
    '''
    power_nr = 1 to 8
    Flash on / off the power ouput (uln2801) for number fo seconds
    '''
    steelsquid_pi.mcp_flash_timer(20, 14, seconds)


def button(button_nr):
    '''
    Get status on button
    button_nr = 1 to 4
    '''
    if button_nr == 1:
        return steelsquid_pi.mcp_get(20, 7)
    elif button_nr == 2:
        return steelsquid_pi.mcp_get(20, 6)
    elif button_nr == 3:
        return steelsquid_pi.mcp_get(20, 5)
    elif button_nr == 4:
        return steelsquid_pi.mcp_get(20, 4)


def button_click(button_nr, callback_method):
    '''
    Listen for button click
    button_nr = 1 to 4
    '''
    if button_nr == 1:
        steelsquid_pi.mcp_click(20, 7, callback_method)
    elif button_nr == 2:
        steelsquid_pi.mcp_click(20, 6, callback_method)
    elif button_nr == 3:
        steelsquid_pi.mcp_click(20, 5, callback_method)
    elif button_nr == 4:
        steelsquid_pi.mcp_click(20, 4, callback_method)


def dip(dip_nr):
    '''
    Get status on DIP
    dip_nr = 1 to 4
    '''
    if dip_nr == 1:
        return steelsquid_pi.mcp_get(20, 3)
    elif dip_nr == 2:
        return steelsquid_pi.mcp_get(20, 2)
    elif dip_nr == 3:
        return steelsquid_pi.mcp_get(20, 1)
    elif dip_nr == 4:
        return steelsquid_pi.mcp_get(20, 0)


def dip_event(dip_nr, callback_method):
    '''
    Listen for DIP change
    dip_nr = 1 to 4
    '''
    if dip_nr == 1:
        steelsquid_pi.mcp_event(20, 3, callback_method)
    elif dip_nr == 2:
        steelsquid_pi.mcp_event(20, 2, callback_method)
    elif dip_nr == 3:
        steelsquid_pi.mcp_event(20, 1, callback_method)
    elif dip_nr == 4:
        steelsquid_pi.mcp_event(20, 0, callback_method)


def extra_in(gpio):
    '''
    Get status on ectra gpio
    gpio = 1 to 8
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    return steelsquid_pi.mcp_get(21, gpio+7)


def extra_in_click(gpio, callback_method):
    '''
    Listen for click on extra gpio
    gpio = 1 to 8
    '''
    gpio = int(gpio)
    gpio = gpio + 3
    steelsquid_pi.mcp_click(21, gpio+7, callback_method)


def extra_in_event(gpio, callback_method):
    '''
    Listen for change on extra gpio
    gpio = 1 to 8
    '''
    steelsquid_pi.mcp_event(21, gpio+7, callback_method)


def sabertooth_set_speed(left, right):
    '''
    Set the speed on a sabertooth dc motor controller.
    from -100 to +100
    -100 = 100% back speed
    0 = no speed
    100 = 100% forward speed
    '''
    global sabertooth
    if sabertooth==None:
        import steelsquid_sabertooth
        the_port = steelsquid_utils.get_parameter("sabertooth_port", "")
        if the_port=="" or "/dev/tty" not in the_port:
            steelsquid_utils.set_parameter("sabertooth_port", "/dev/ttyUSB3")
            the_port = "/dev/ttyUSB3"
        sabertooth = steelsquid_sabertooth.SteelsquidSabertooth(serial_port=the_port)
    sabertooth.set_speed(left, right)


def analog_in(gpio, gain=GAIN_6_144_V):
    '''
    Read analog in from ADS1015 (0 to 5 v)
    gpio = 1 to 8
    '''
    if gpio == 1:
        return steelsquid_pi.adc_get(48, 0, gain)
    elif gpio == 2:
        return steelsquid_pi.adc_get(48, 1, gain)
    elif gpio == 3:
        return steelsquid_pi.adc_get(48, 2, gain)
    elif gpio == 4:
        return steelsquid_pi.adc_get(48, 3, gain)
    elif gpio == 5:
        return steelsquid_pi.adc_get(49, 0, gain)
    elif gpio == 6:
        return steelsquid_pi.adc_get(49, 1, gain)
    elif gpio == 7:
        return steelsquid_pi.adc_get(49, 2, gain)
    elif gpio == 8:
        return steelsquid_pi.adc_get(49, 3, gain)
        

def analog_event(gpio, callback_method, gain=GAIN_6_144_V):
    '''
    Listen for changes on analog in from ADS1015
    gpio = 1 to 8
    '''
    if gpio == 1:
        return steelsquid_pi.adc_event(48, 0, callback_method, gain)
    elif gpio == 2:
        return steelsquid_pi.adc_event(48, 1, callback_method, gain)
    elif gpio == 3:
        return steelsquid_pi.adc_event(48, 2, callback_method, gain)
    elif gpio == 4:
        return steelsquid_pi.adc_event(48, 3, callback_method, gain)
    elif gpio == 5:
        return steelsquid_pi.adc_event(49, 0, callback_method, gain)
    elif gpio == 6:
        return steelsquid_pi.adc_event(49, 1, callback_method, gain)
    elif gpio == 7:
        return steelsquid_pi.adc_event(49, 2, callback_method, gain)
    elif gpio == 8:
        return steelsquid_pi.adc_event(49, 3, callback_method, gain)


def aaa(bb):
    print bb
    
if __name__ == '__main__':
    analog_event(1, aaa, GAIN_4_096_V)
    raw_input("Press Enter to continue...")



