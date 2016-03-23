#!/usr/bin/python -OO


'''
Send and reseive messages with HM-TRLR-S transiver 
http://www.digikey.com/product-detail/en/HM-TRLR-S-868/HM-TRLR-S-868-ND/5051756

One of the devices is server and the other client.
The server listen for commands and return answer to the client.
The client send commadn to the server and read the answer

SERVER:
# Setup the serial interface
steelsquid_hmtrlrs.setup()
# Listen for requests (Will listen for 1 seconds, if no data in that time return (None, None))
command, data = steelsquid_hmtrlrs.listen()
# Answer back with response
steelsquid_hmtrlrs.response(data)
# Or with error
steelsquid_hmtrlrs.error(message)
# Then the server should start listen again
command, data = steelsquid_hmtrlrs.listen()
...

CLIENT:
# Setup the serial interface
steelsquid_hmtrlrs.setup()
# Send reuest and get the answer
# Will throw exception on error or return None when timeout (Will listen for max 2 seconds for answer then return None)
data = steelsquid_hmtrlrs.request(command, data)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2016-02-17 Created
'''

import thread
import threading
import time
import datetime
import steelsquid_utils
import serial
import sys
import steelsquid_pi

# Long range but slow speed
MODE_SLOW = "MODE_SLOW"

# Medum range and medium speed
MODE_MEDIUM = "MODE_MEDIUM"

# Fast speed but short range
MODE_FAST = "MODE_FAST"

# Only one thread can use this at a time    
lock = threading.Lock()

# The serial interface
ser = None

# GPIO for config and reset
config_gpio_ = None
reset_gpio_ = None

# Port
serial_port_ = None

# Baudrate
baudrate_=38400

# Mode
mode_=MODE_MEDIUM

# Request
ENQ = chr(0x05)

# Broadcast
SUB = chr(0x1A)

# OK response
ACK = chr(0x06)

# ERROR response
NAK = chr(0x15)

# Send this back when reseive request to let client now that the server processing
SYN = chr(0x16)

# Last OK send/reseive 
last_sync = datetime.datetime.now()

# If no command in a while try to init the device again
resetup_count = 0
resetup_count_max = 2

def setup(serial_port="/dev/ttyAMA0", config_gpio=25, reset_gpio=23, baudrate=38400, mode=MODE_MEDIUM):
    '''
    Setup the serial interface
    serial_port: The serial port (/dev/ttyAMA0, /dev/ttyUSB1...)
    config_gpio_: GPIO number to use for setting the device in configuration mode or communication mode
    reset_gpio_: GPIO to use to send reset signal
    mode: MODE_SLOW   = Long range but slow speed
          MODE_MEDIUM = Medum range and medium speed
          MODE_FAST   = Fast speed but short range
    '''
    global ser
    global serial_port_
    global config_gpio_
    global reset_gpio_
    global baudrate_
    global mode_

    serial_port_=serial_port
    config_gpio_ = config_gpio
    reset_gpio_ = reset_gpio
    baudrate_ = baudrate
    mode_ = mode
    
    # Create the serial interface
    ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=0.4)
    time.sleep(0.01)
    # Set reset hight (low will reset the device)
    steelsquid_pi.gpio_set(reset_gpio, True)
    time.sleep(0.01)
    # Set baudrate
    try:
        _send_command("AT+SPR=6")
    except:
        steelsquid_utils.shout("Unable to use default baudrate, trying new boudrate...")
    # Create the serial interface with new  baudrate
    try:
        ser.close
    except:
        pass
    ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=0.5)
    time.sleep(0.01)
    # Set the HM-TRLR-S in communication mode
    steelsquid_pi.gpio_set(config_gpio, True)
    # Set mode
    if mode==MODE_SLOW:
        # Set LoRa
        _send_command("AT+MODE=0")
        _send_command("AT+LRSBW=6")
        _send_command("AT+LRSF=C")
    elif mode==MODE_MEDIUM:
        # Set LoRa
        _send_command("AT+MODE=0")
        _send_command("AT+LRSBW=7")
        _send_command("AT+LRSF=8")
    elif mode==MODE_FAST:
        # Set FSK 
        _send_command("AT+MODE=2")
    
    time.sleep(0.01)


    def resetup():
        '''
        Run the last setup again.
        '''
        setup(serial_port_, config_gpio_, reset_gpio_, baudrate_, mode_)


def set_chanel(channel):
    '''
    Set channel
    channel= 0 to 15
    '''
    
    with lock:
        channel = str(channel)
        if channel=="10":
            channel = "A"
        elif channel=="11":
            channel = "B"
        elif channel=="12":
            channel = "C"
        elif channel=="13":
            channel = "D"
        elif channel=="14":
            channel = "E"
        elif channel=="15":
            channel = "F"
        _send_command("AT+CS="+channel)
    
             
def _send_command(com):
    '''
    Send a command to the transiver
    '''
    # Set the HM-TRLR-S in command mode
    steelsquid_pi.gpio_set(config_gpio_, False)
    try:
        time.sleep(0.01)
        ser.write(com)
        ser.write("\n")
        ser.flush()
        line = ser.readline()
        if "ERROR" in line:
            if line.split(":")[1]=="0":
                raise Exception("The command format is wrong.")
            elif line.split(":")[1]=="1":
                raise Exception("The parameter is wrong.")
            else:
                raise Exception("The command is failed. ")
        time.sleep(0.01)
    finally:
        # Set the HM-TRLR-S in communication mode
        steelsquid_pi.gpio_set(config_gpio_, True)
        time.sleep(0.01)

             
         
def _read_line(nr_of_times=8):
    '''
    Read a line from the serial port
    Return: string (None = error/timeout)
    nr_of_times=8: Will listen for 3.2 seconds then timeout
    '''
    global resetup_count
    for i in range(nr_of_times):
        by = ser.readline()
        if len(by)>0:
            resetup_count = 0
            return by.rstrip('\n')
    # If server starts when the client is powered of you must init the hmtrlrs
    # So if no ping command for a while try to init it again
    if resetup_count>=resetup_count_max:
        resetup_count = 0
        try:
            resetup()
        except:
            pass
    else:
        resetup_count = resetup_count + 1
    return None
            
                    
def _read_chr(nr_of_times=8):
    '''
    Read a chr
    Return: chr (None = error/timeout)
    nr_of_times=8: Will listen for 3.2 seconds then timeout
    '''
    global resetup_count
    for i in range(nr_of_times):
        by = ser.read(1)
        if len(by)>0:
            resetup_count = 0
            return by
    # If server starts when the client is powered of you must init the hmtrlrs
    # So if no ping command for a while try to init it again
    if resetup_count>=resetup_count_max:
        resetup_count = 0
        try:
            resetup()
        except:
            pass
    else:
        resetup_count = resetup_count + 1
    return None


def _read_chr_sync():
    '''
    Read a chr
    Return: chr (None = error/timeout)
    Will listen for 0.4 seconds then timeout
    '''
    global resetup_count
    by = ser.read(1)
    if len(by)>0:
        resetup_count = 0
        return by
    else:
        # If server starts when the client is powered of you must init the hmtrlrs
        # So if no ping command for a while try to init it again
        if resetup_count>=resetup_count_max:
            resetup_count = 0
            try:
                resetup()
            except:
                pass
        else:
            resetup_count = resetup_count + 1
        return None

            
def listen():
    '''
    Listen for command from the client
    Return tuple with (command, data)  data is a list of strings
           Can return (None, None) if timeout
    This method will only listen for 3.2 seconds, if no data in that time return (None, None)
    '''
    global last_sync
    with lock:
        # Read request
        req = _read_chr()
        if req==None:
            return None, None
        elif req==SUB:
            last_sync = datetime.datetime.now()
            # Read broadcast command
            command = _read_line()
            if command==None:
                return None, None
            # Read request data
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            return command, data
        elif req==ENQ:
            last_sync = datetime.datetime.now()
            # Read request command
            command = _read_line()
            if command==None:
                return None, None
            # Read request data
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            # Send this back when reseive request to let client now that the server processing
            ser.write(SYN)
            return command, data
        else:
            return None, None


def response(data=None):
    '''
    Return a OK answer to to client
    data: Data to responde back to client with (data is a list of strings)
    '''
    global last_sync
    with lock:
        # Write ok answer
        ser.write(ACK)
        if data!=None:
            data = '|'.join([str(mli) for mli in data])
            ser.write(data)
        ser.write("\n")
        ser.flush()
        last_sync = datetime.datetime.now()
        

def error(message=None):
    '''
    Return a ERROR answer to to client
    message: The error message to send back to client (a string)
    '''
    global last_sync
    with lock:
        # Write error answer
        ser.write(NAK)
        if message!=None:
            ser.write(str(message))
        ser.write("\n")
        ser.flush()
        last_sync = datetime.datetime.now()
        

def request(command, data=None):
    '''
    Send a command to the server and wait for answer, will only wait for 3.2 seconds then timeout (return None)
    command: The command
    data: Data to the server  (data is a list of strings)
    Return: data (data is a list of strings from the server)
    Raise exception if error from server or timeout on response
    '''
    global last_sync
    with lock:
        # Write a request
        ser.write(ENQ)
        ser.write(command)
        ser.write("\n")
        if data!=None:
            data = '|'.join([str(mli) for mli in data])
            ser.write(data)
        ser.write("\n")
        ser.flush()
        # Listen sync (is the server processing)
        req = _read_chr_sync()
        if req==None:
            req = _read_chr_sync()
            if req==None:
                raise Exception(command +": Sync Timeout")
        last_sync = datetime.datetime.now()
        # Listen for response
        req = _read_chr()
        if req==None:
            raise Exception(command +": Response Timeout")
        elif req == ACK:
            le = _read_line()
            if len(le)==0:
                return []
            else:
                return le.split("|")
        elif req == NAK:
            raise Exception(command +": "+ _read_line())
            

def broadcast(command, data=None):
    '''
    Broadcast to the server...do not wait for any answer
    command: The command
    data: Data to the server  (data is a list of strings)
    '''
    global last_sync
    with lock:
        # Write a broadcast
        ser.write(SUB)
        ser.write(command)
        ser.write("\n")
        if data!=None:
            data = '|'.join([str(mli) for mli in data])
            ser.write(data)
        ser.write("\n")
        ser.flush()
        last_sync = datetime.datetime.now()
            

def stop():
    '''
    Close the serial interface (no more read or write)
    '''
    ser.close()


