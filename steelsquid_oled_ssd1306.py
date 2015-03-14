#!/usr/bin/python -OO

import time

from Adafruit_I2C import Adafruit_I2C
import Adafruit_GPIO.I2C as I2C
import Image
import ImageDraw
import ImageFont

# Constants
SSD1306_I2C_ADDRESS = 0x3C  # 011110+SA0+RW - 0x3C or 0x3D
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2
WIDTH = 128
HEIGHT = 64
PAGES = HEIGHT/8
buffer = [0]*(WIDTH*PAGES)
i2c_bus = None
image = None
draw = None
font = None

def init():
    '''
    Clear the screen
    '''
    global i2c_bus
    global image
    global draw
    global font
    if i2c_bus == None:
        i2c_bus = I2C.get_i2c_device(0x3C)
        command(SSD1306_DISPLAYOFF)                    # 0xAE
        command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        command(0x80)                                  # the suggested ratio 0x80
        command(SSD1306_SETMULTIPLEX)                  # 0xA8
        command(0x3F)
        command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        command(0x0)                                   # no offset
        command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        command(SSD1306_CHARGEPUMP)                    # 0x8D
        command(0x14)
        command(SSD1306_MEMORYMODE)                    # 0x20
        command(0x00)                                  # 0x0 act like ks0108
        command(SSD1306_SEGREMAP | 0x1)
        command(SSD1306_COMSCANDEC)
        command(SSD1306_SETCOMPINS)                    # 0xDA
        command(0x12)
        command(SSD1306_SETCONTRAST)                   # 0x81
        command(0xCF)
        command(SSD1306_SETPRECHARGE)                  # 0xd9
        command(0xF1)
        command(SSD1306_SETVCOMDETECT)                 # 0xDB
        command(0x40)
        command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        command(SSD1306_NORMALDISPLAY)                 # 0xA6
        command(SSD1306_DISPLAYON)
        image = Image.new('1', (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)        
        font = ImageFont.truetype("/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro.ttf", 10)
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    
    
def write(text, width, height):
    '''
    Write text
    '''
    global image
    global draw
    global font
    draw.text((width, height), text, font=font, fill=255)


def show():
    '''
    Show on display
    '''
    global image
    img_to_buf(image)
    display()

def command(c):
    '''
    Send command byte to display.
    '''
    control = 0x00   # Co = 0, DC = 0
    i2c_bus.write8(control, c)

def data(c):
    '''
    Send byte of data to display.
    '''
    control = 0x40   # Co = 0, DC = 0
    i2c_bus.write8(control, c)

def display():
    '''
    Write display buffer to physical display.
    '''
    command(SSD1306_COLUMNADDR)
    command(0)              # Column start address. (0 = reset)
    command(WIDTH-1)   # Column end address.
    command(SSD1306_PAGEADDR)
    command(0)              # Page start address. (0 = reset)
    command(PAGES-1)  # Page end address.
    for i in range(0, len(buffer), 16):
        control = 0x40   # Co = 0, DC = 0
        i2c_bus.writeList(control, buffer[i:i+16])

def img_to_buf(image):
    '''
    Set buffer to value of Python Imaging Library image.  The image should
    be in 1 bit mode and a size equal to the display size.
    '''
    # Grab all the pixels from the image, faster than getpixel.
    pix = image.load()
    # Iterate through the memory pages
    index = 0
    for page in range(PAGES):
        # Iterate through all x axis columns.
        for x in range(WIDTH):
            # Set the bits for the column of pixels at the current position.
            bits = 0
            # Don't use range here as it's a bit slow
            for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                bits = bits << 1
                bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1
            # Update buffer byte and increment to next byte.
            buffer[index] = bits
            index += 1

def set_contrast(contrast):
    '''
    Sets the contrast of the display.  Contrast should be a value between
    0 and 255.
    '''
    if contrast < 0 or contrast > 255:
        raise ValueError('Contrast must be a value from 0 to 255 (inclusive).')
    command(SSD1306_SETCONTRAST)
    command(contrast)


