#!/usr/bin/python -OO


'''
Print text on a HDD44780 compatible LCD from Raspberry Pi
Either directly to the LCD or via the I2C.

Using code from Adafruit Raspberry Pi Python Code and I2CLibraries with some small changes from me.

Copyright (c) 2012-2013 Limor Fried, Kevin Townsend and Mikey Sklar for Adafruit Industries.
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00


import time


class CharLCD(object):
    
    __slots__ = ['GPIO', 'pin_rs', 'pin_e', 'pins_db', 'displaycontrol', 'displayfunction', 'displaymode', 'numlines', 'currline', 'row_offsets']

    def __init__(self):
        import RPi.GPIO as GPIO
        from time import sleep
        self.GPIO = GPIO
        self.pin_rs = 25
        self.pin_e = 24
        if GPIO.RPI_REVISION == 2:
            self.pins_db = [23, 17, 27, 22]
        else:
            self.pins_db = [23, 17, 21, 22]
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)
        self.write4bits(0x33)  # initialization
        self.write4bits(0x32)  # initialization
        self.write4bits(0x28)  # 2 line 5x7 matrix
        self.write4bits(0x0C)  # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06)  # shift cursor right
        self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.displayfunction |= LCD_2LINE

        """ Initialize to default text direction (for romance languages) """
        self.displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.write4bits(LCD_ENTRYMODESET | self.displaymode)  # set the entry mode

        self.clear()
        self.begin(16, 2)
        self.display_on()

    def begin(self, cols, lines):
        if (lines > 1):
            self.numlines = lines
            self.displayfunction |= LCD_2LINE
            self.currline = 0

    def home(self):
        self.write4bits(LCD_RETURNHOME)  # set cursor position to zero
        self.delay_microseconds(3000)  # this command takes a long time!

    def clear(self):
        self.write4bits(LCD_CLEARDISPLAY)  # command to clear display
        self.delay_microseconds(3000)    # 3000 microsecond sleep, clearing the display takes a long time

    def position(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if (row > self.numlines):
            row = self.numlines - 1  # we count rows starting w/0
            self.write4bits(LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def display_off(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~LCD_DISPLAYON
        self.write4bits(LCD_DISPLAYCONTROL | self.displaycontrol)

    def display_on(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= LCD_DISPLAYON
        self.write4bits(LCD_DISPLAYCONTROL | self.displaycontrol)

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4bits(0xC0)  # next line
            else:
                self.write4bits(ord(char), True)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        self.delay_microseconds(1000)  # 1000 microsecond sleep
        bits = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)
        self.pulse_enable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4, 8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[:: - 1][i - 4], True)
        self.pulse_enable()

    def delay_microseconds(self, microseconds):
        from time import sleep
        seconds = microseconds / float(1000000)    # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulse_enable(self):
        self.GPIO.output(self.pin_e, False)
        self.delay_microseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, True)
        self.delay_microseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, False)
        self.delay_microseconds(1)  # commands need > 37us to settle


class CharLCDIcc(object):

    # Commands
    CMD_Clear_Display = 0x01
    CMD_Return_Home = 0x02
    CMD_Entry_Mode = 0x04
    CMD_Display_Control = 0x08
    CMD_Cursor_Display_Shift = 0x10
    CMD_Function_Set = 0x20
    CMD_DDRAM_Set = 0x80

    # Options
    OPT_Increment = 0x02                    # CMD_Entry_Mode
    OPT_Display_Shift = 0x01                # CMD_Entry_Mode
    OPT_Enable_Display = 0x04               # CMD_Display_Control
    OPT_Enable_Cursor = 0x02                # CMD_Display_Control
    OPT_Enable_Blink = 0x01                 # CMD_Display_Control
    OPT_Display_Shift = 0x08                # CMD_Cursor_Display_Shift
    OPT_Shift_Right = 0x04                  # CMD_Cursor_Display_Shift 0 = Left
    OPT_2_Lines = 0x08                      # CMD_Function_Set 0 = 1 line
    OPT_5x10_Dots = 0x04                    # CMD_Function_Set 0 = 5x7 dots
    

    def __init__(self):
        import smbus
        self.addr = 0x27
        self.bus = smbus.SMBus(1)

        self.en = 2
        self.rs = 0
        self.rw = 1
        self.d4 = 4
        self.d5 = 5
        self.d6 = 6
        self.d7 = 7
        self.backlight = 3

        self.backlight_state = True

        # Activate LCD
        initialize_i2c_data = 0x00
        initialize_i2c_data = self._pinInterpret(self.d4, initialize_i2c_data, 0b1)
        initialize_i2c_data = self._pinInterpret(self.d5, initialize_i2c_data, 0b1)
        self._enable(initialize_i2c_data)   
        time.sleep(0.2)
        self._enable(initialize_i2c_data)
        time.sleep(0.1)
        self._enable(initialize_i2c_data)
        time.sleep(0.1)  

        # Initialize 4-bit mode
        initialize_i2c_data = self._pinInterpret(self.d4, initialize_i2c_data, 0b0)
        self._enable(initialize_i2c_data)
        time.sleep(0.01)

        self.command(self.CMD_Function_Set | self.OPT_2_Lines)
        self.command(self.CMD_Display_Control | self.OPT_Enable_Display | self.OPT_Enable_Cursor)
        self.command(self.CMD_Clear_Display)
        self.command(self.CMD_Entry_Mode | self.OPT_Increment |  self.OPT_Display_Shift) 
        self.command(self.CMD_Display_Control | self.OPT_Enable_Display)
    
    def clear(self):
        self.command(self.CMD_Clear_Display)
        time.sleep(0.1)
    
    def home(self):
        self.command(self.CMD_Return_Home)
        time.sleep(0.1)

    def position(self, line, pos):
        if line == 1:
            address = pos
        elif line == 2:
            address = 0x40 + pos
        elif line == 3:
            address = 0x14 + pos
        elif line == 4:
            address = 0x54 + pos
        self.command(self.CMD_DDRAM_Set + address)

    def message(self, string):
        if "\n" in string:
            spli = string.split('\n')
            line = 1
            for wo in spli:
                self.position(line, 0)
                self.message(wo)
                line = line + 1
        else:
            for c in string:
                self.writeChar(c)
      
    def display_on(self):
        if self.backlight >= 0:
            self.bus.write_byte(self.addr, self._pinInterpret(self.backlight, 0x00, 0b1))
            self.backlight_state = True

    def display_off(self):
        if self.backlight >= 0: 
            self.bus.write_byte(self.addr, self._pinInterpret(self.backlight, 0x00, 0b0))   
            self.backlight_state = False

    def command(self, data):
        self._write(data)

    def writeChar(self, char):
        self._write(ord(char), False)

    def _write(self, data, command=True):
        i2c_data = 0x00

        #Add data for high nibble
        hi_nibble = data >> 4
        i2c_data = self._pinInterpret(self.d4, i2c_data, (hi_nibble & 0x01))
        i2c_data = self._pinInterpret(self.d5, i2c_data, ((hi_nibble >> 1) & 0x01))
        i2c_data = self._pinInterpret(self.d6, i2c_data, ((hi_nibble >> 2) & 0x01))
        i2c_data = self._pinInterpret(self.d7, i2c_data, ((hi_nibble >> 3) & 0x01))

        # Set the register selector to 1 if this is data
        if command != True:
            i2c_data = self._pinInterpret(self.rs, i2c_data, 0x1)

        # Toggle Enable 
        self._enable(i2c_data)

        i2c_data = 0x00

        #Add data for high nibble
        low_nibble = data & 0x0F 
        i2c_data = self._pinInterpret(self.d4, i2c_data, (low_nibble & 0x01))
        i2c_data = self._pinInterpret(self.d5, i2c_data, ((low_nibble >> 1) & 0x01))
        i2c_data = self._pinInterpret(self.d6, i2c_data, ((low_nibble >> 2) & 0x01))
        i2c_data = self._pinInterpret(self.d7, i2c_data, ((low_nibble >> 3) & 0x01))

        # Set the register selector to 1 if this is data
        if command != True:
            i2c_data = self._pinInterpret(self.rs, i2c_data, 0x1)
        
        self._enable(i2c_data)
        
        time.sleep(0.01)
        
    def _pinInterpret(self, pin, data, value="0b0"):
        if value:
            # Construct mask using pin
            mask = 0x01 << (pin)  
            data = data | mask
        else:
            # Construct mask using pin
            mask = 0x01 << (pin) ^ 0xFF
            data = data & mask
        return data 
    
    def _enable(self, data):
        # Determine if black light is on and insure it does not turn off or on
        if self.backlight_state:
            data = self._pinInterpret(self.backlight, data, 0b1)
        else:
            data = self._pinInterpret(self.backlight, data, 0b0)
        
        self.bus.write_byte(self.addr, data)
        self.bus.write_byte(self.addr, self._pinInterpret(self.en, data, 0b1))
        self.bus.write_byte(self.addr, data)
