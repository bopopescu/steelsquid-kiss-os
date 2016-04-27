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

# After this number of seconds without sync the link is probably lost
LINK_LOST_SUGGESTION = 4

# Sleep this long after a request/broadcast or other transaction is sent...
STRANS_SLEEP = 0.01

# Long range but slow speed
MODE_SLOW = "MODE_SLOW"

# Medum range and medium speed
MODE_MEDIUM = "MODE_MEDIUM"

# Fast speed but short range
MODE_FAST = "MODE_FAST"

# Try to resend a request this number of times if get timout
NUMBER_OF_RETRY = 3

# Only one thread can use this at a time    
lock = threading.RLock()

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

# Push broadcasts
# steelsquid kiss os using this when push variables from client to server
DC1 = chr(0x11)
DC2 = chr(0x12)
DC3 = chr(0x13)
DC4 = chr(0x14)

# Sunc request
# steelsquid kiss os using this when sync variables between client and server
SYN = chr(0x16)

# Last OK send/reseive 
last_sync = datetime.datetime.now()

# If no command in a while try to init the device again
resetup_count = 0
resetup_count_max = 4

# Temporary disable the request and broadcast
disable = False


def setup(serial_port="/dev/ttyAMA0", config_gpio=25, reset_gpio=23, baudrate=38400, mode=MODE_MEDIUM, timeout_mutipple=1):
    '''
    Setup the serial interface
    serial_port: The serial port (/dev/ttyAMA0, /dev/ttyUSB1...)
    config_gpio_: GPIO number to use for setting the device in configuration mode or communication mode
    reset_gpio_: GPIO to use to send reset signal
    mode: MODE_SLOW   = Long range but slow speed
          MODE_MEDIUM = Medum range and medium speed
          MODE_FAST   = Fast speed but short range
    timeout_mutipple: mitipply the timeout time on the different modes with this...
                      MODE_SLOW   = 6s * timeout_mutipple
                      MODE_MEDIUM = 0.5s * timeout_mutipple
                      MODE_FAST   = 0.2s * timeout_mutipple
    
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
    ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=0.5)
    time.sleep(STRANS_SLEEP)
    # Set reset hight (low will reset the device)
    steelsquid_pi.gpio_set(reset_gpio, True)
    time.sleep(STRANS_SLEEP)
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
    if mode==MODE_SLOW:
        ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=7*timeout_mutipple)
    elif mode==MODE_MEDIUM:
        ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=0.3*timeout_mutipple)
    elif mode==MODE_FAST:
        ser = serial.Serial(serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True, timeout=0.2*timeout_mutipple)
    time.sleep(STRANS_SLEEP)
    # Set the HM-TRLR-S in communication mode
    steelsquid_pi.gpio_set(config_gpio, True)
    # Enable CRC
    _send_command("AT+LRCRC=1")
    # Packagesize
    _send_command("AT+LRPL=32")
    # Syncworld
    _send_command("AT+SYNL=2")
    _send_command("AT+SYNW=3412")
    # Set mode
    if mode==MODE_SLOW:
        # Set LoRa
        _send_command("AT+MODE=0")
        _send_command("AT+LRSBW=6")
        _send_command("AT+LRSF=C")
    elif mode==MODE_MEDIUM:
        # Set LoRa
        _send_command("AT+MODE=0")
        _send_command("AT+LRSBW=8")
        _send_command("AT+LRSF=9")
    elif mode==MODE_FAST:
        # Set FSK 
        _send_command("AT+MODE=2")
    
    time.sleep(STRANS_SLEEP)


def resetup():
    '''
    Run the last setup again.
    '''
    setup(serial_port_, config_gpio_, reset_gpio_, baudrate_, mode_)


def is_linked():
    '''
    After about 4 seconds without sync the link is probably lost
    '''
    diff = datetime.datetime.now()-last_sync
    return diff.total_seconds()<resetup_count_max


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
        time.sleep(STRANS_SLEEP)
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
        time.sleep(STRANS_SLEEP)
    finally:
        # Set the HM-TRLR-S in communication mode
        steelsquid_pi.gpio_set(config_gpio_, True)
        time.sleep(STRANS_SLEEP)

             
         
def _read_line():
    '''
    Read a line from the serial port
    Return: string (None = error/timeout)
    '''
    global resetup_count
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
            
                    
def _read_chr():
    '''
    Read a chr
    Return: chr (None = error/timeout)
    '''
    global resetup_count
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

            
def listen():
    '''
    Listen for command from the client
    Return tuple with (command, data)  data is a list of strings
           Can return (None, None) if timeout
    '''
    global last_sync
    with lock:
        # Read request
        req = _read_chr()
        if req == None:
            req = _read_chr()
        if req==None:
            return None, None
        elif req==SUB:
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
            last_sync = datetime.datetime.now()
            return command, data
        elif req==ENQ:
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
            last_sync = datetime.datetime.now()
            return command, data
        elif req==DC1:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 1, data # True indicate that it is a push broadcast
        elif req==DC2:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 2, data # True indicate that it is a push broadcast
        elif req==DC3:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 3, data # True indicate that it is a push broadcast
        elif req==DC4:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 4, data # True indicate that it is a push broadcast
        elif req==SYN:
            # Read sync data (steelsquid-kiss os using this...)
            data = _read_line()
            if data==None:
                return None, None
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 0, data # False indicate that it is a sync request
        else:
            return None, None


def response_sync(data):
    '''
    Return a sync answer to the client
    data: Data to responde back to client with (data is a list of strings)
    '''
    global last_sync
    with lock:
        # Write push answer
        ser.write(SYN)
        if data!=None:
            data = '|'.join([str(mli) for mli in data])
            ser.write(data)
        ser.write("\n")
        ser.flush()


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
        

def request(command, data=None, _do_not_use=0):
    '''
    Send a command to the server and wait for answer, will only wait for 3.2 seconds then timeout (return None)
    command: The command
    data: Data to the server  (data is a list of strings)
    Return: data (data is a list of strings from the server)
    Raise exception if error from server or timeout on response
    '''
    if disable:
        raise Exception("The transceiver is dissabled")
    else:
        global last_sync
        with lock:
            time.sleep(STRANS_SLEEP)
            # Write a request
            ser.write(ENQ)
            ser.write(command)
            ser.write("\n")
            if data!=None:
                _data = '|'.join([str(mli) for mli in data])
                ser.write(_data)
            ser.write("\n")
            ser.flush()
            # Listen for response
            req = _read_chr()
            if req==None:
                # Try one more time...
                if _do_not_use<NUMBER_OF_RETRY:
                    dnu = _do_not_use + 1
                    return request(command, data, _do_not_use=dnu)
                else:
                    raise Exception(command +": Request timeout (ACK/NAC)")
            elif req == ACK:
                le = _read_line()
                if le == None:
                    # Try one more time...
                    if _do_not_use<NUMBER_OF_RETRY:
                        dnu = _do_not_use + 1
                        return request(command, data, _do_not_use=dnu)
                    else:
                        raise Exception(command +": Request timeout (Data)")
                elif len(le)==0:
                    last_sync = datetime.datetime.now()
                    return []
                else:
                    last_sync = datetime.datetime.now()
                    return le.split("|")
            elif req == NAK:
                raise Exception(command +": "+ _read_line())
            else:
                raise Exception("Unknown response: "+str(req))
 
 
def request_sync(data=None, _do_not_use=0):
    '''
    Send a command to the server and wait for answer, will only wait for 3.2 seconds then timeout (return None)
    This will send a sync request...steelsquid_kiss_os using this...
    data: Data to the server  (data is a list of strings)
    Return: data (data is a list of strings from the server)
    Raise exception if error from server or timeout on response
    '''
    if disable:
        raise Exception("The transceiver is dissabled")
    else:
        global last_sync
        with lock:
            time.sleep(STRANS_SLEEP)
            # Write a sync request
            ser.write(SYN)
            if data!=None:
                _data = '|'.join([str(mli) for mli in data])
                ser.write(_data)
            ser.write("\n")
            ser.flush()
            # Listen for response
            # start = datetime.datetime.now()
            req = _read_chr()
            if req==None:
                # Try one more time...
                if _do_not_use<NUMBER_OF_RETRY:
                    dnu = _do_not_use + 1
                    return request_sync(data, _do_not_use=dnu)
                else:
                    raise Exception("Sync Request timeout (SYN)")
            elif req == SYN:
                le = _read_line()
                #print (datetime.datetime.now()-start).total_seconds()
                if le == None:
                    # Try one more time...
                    if _do_not_use<NUMBER_OF_RETRY:
                        dnu = _do_not_use + 1
                        return request_sync(data, _do_not_use=dnu)
                    else:
                        raise Exception("Sync Request timeout (Data)")
                elif len(le)==0:
                    last_sync = datetime.datetime.now()
                    return []
                else:
                    last_sync = datetime.datetime.now()
                    return le.split("|")
            else:
                raise Exception("Unknown sync response...")

            

def broadcast(command, data=None):
    '''
    Broadcast to the server...do not wait for any answer
    command: The command
    data: Data to the server  (data is a list of strings)
    '''
    if disable:
        raise Exception("The transceiver is dissabled")
    else:
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
            time.sleep(STRANS_SLEEP)
            
            
def broadcast_push(push_nr, data=None):
    '''
    Broadcast to the server...do not wait for any answer
    This will send a push requst...steelsquid_kiss_os using this....
    data: Data to the server  (data is a list of strings)
    '''
    if disable:
        raise Exception("The transceiver is dissabled")
    else:
        global last_sync
        with lock:
            # Write a push broadcast
            if push_nr==1:
                ser.write(DC1)
            if push_nr==2:
                ser.write(DC2)
            if push_nr==3:
                ser.write(DC3)
            if push_nr==4:
                ser.write(DC4)
            if data!=None:
                data = '|'.join([str(mli) for mli in data])
                ser.write(data)
            ser.write("\n")
            ser.flush()
            time.sleep(STRANS_SLEEP)
            

def stop():
    '''
    Close the serial interface (no more read or write)
    '''
    ser.close()


