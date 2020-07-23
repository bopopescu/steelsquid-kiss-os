#!/usr/bin/python -OO


'''
Send data between 2 NRF24L01+

You also need the pynrf24 (https://github.com/jpbarraca/pynrf24)
I also have pynrf24 on my github with some small changes, because Joao Paulo Barraca pynrf24 did not work with Raspberry Pi.
https://github.com/steelsquid/steelsquid-kiss-os/blob/master/steelsquid_nrf24.py

You can use this in 2 ways (server/client or main/subordinate).

SERVER/CLIENT:
One of the devices is server and the other client.
The server listen for commands and return answer to the client.
The client send commadn to the server and read the answer
The data can be any length but the command can only be package_size characters long

SERVER:
# Start as server
steelsquid_nrf24.server()
# Listen for requests
command, data = steelsquid_nrf24.listen()
# Answer back with response
steelsquid_nrf24.response(data)
# Or with error
steelsquid_nrf24.error(message)
# Then the server should start listen again
command, data = steelsquid_nrf24.listen()
...

CLIENT:
# Start as client
steelsquid_nrf24.client()
# Send reuest and get the answer
# Will throw exception on error or return None when timeout
data = steelsquid_nrf24.request(command, data)
...

MASTER/SLAVE:
One of the devices is main and can send data to the subordinate (example a file or video stream).
The data is cut up into packages and transmitted.
The subordinate can transmitt short command back to the main on every package of data it get.
This is usefull if you want to send a low resolution and low framerate video from the main to the subordinate.
And the subordinate then can send command back to the main.

MASTER:
# Start as main and register a command_method
# When subordinate send command to the main the command_method will execute
# But this only work if the main continuously sedn data to the client
def command_method(command):
   ...
steelsquid_nrf24.main(command_method)
# Send data to the client
steelsquid_nrf24.send(data)
steelsquid_nrf24.send(more_data)
steelsquid_nrf24.send(and_more_data)
...

SLAVE:
# start as subordinate
steelsquid_nrf24.subordinate()
# Listen for data from the main
data = steelsquid_nrf24.receive()
more_data = steelsquid_nrf24.receive()
more_data = steelsquid_nrf24.receive()
...
# Then in a nother thread the client can execute this to sned command to the main (max [package_size] characters long)
steelsquid_nrf24.command("a_command")

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

from nrf24 import NRF24
import steelsquid_utils
import threading
import time
import numpy


# Highest speed will transmit the shortest
BR_1MBPS = 0

# Medium speed
BR_2MBPS = 1

# Lowest speed will transmit further (up to 1km)
BR_250KBPS = 2

# GPIO to use for the CE pin
ce_pin = 25

# Radio pipe addresses for the 2 nodes to communicate (you can change this if you want)
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

# Use when listening
null_pipe = [0]

# The nrf24 radio
radio = None

# Only one thread can use this at a time    
lock = threading.Lock()

# Just a buffer to use
buff = []

# Package Size
package_size = 32

# For some strange reason i can not responde with the same package as last time???
# So i togle the response and error byte
last_r_no = 0  # 0 and 1 = OK answer, no more data
last_r = 2  # 2 and 3 = OK answer, more data
last_e = 4  # 4 and 5 error answer

# Method to execute when subordinate send commadn to main
command_callback_method=None

# subordinate want to send command to main
command_to_send=None


def server(channel=0x70, bit_rate=BR_250KBPS):
    '''
    Start this as server.
    Listen for a command from the client
    '''
    _init(channel, bit_rate)
    radio.startListening()
    radio.stopListening()
    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])


def client(channel=0x70, bit_rate=BR_250KBPS):
    '''
    Start this as client.
    Send command to server and then read answer
    '''
    _init(channel, bit_rate)
    radio.startListening()
    radio.stopListening()
    radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])


def _transmitter(is_transmitter):
    '''
    '''
    if is_transmitter:
        radio.stopListening()
    else:
        radio.startListening()
        

def _init(channel, bit_rate):
    '''
    Create the nrf24 radio object
    '''
    global radio
    radio = NRF24()
    radio.begin(0, 0, ce_pin)
    radio.setRetries(15, 15)
    radio.setPayloadSize(package_size)
    radio.setChannel(channel)
    radio.setDataRate(bit_rate)
    radio.setPALevel(NRF24.PA_MAX)
    #radio.setCRCLength(NRF24.CRC_8)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()

    
def listen(timeout=0):
    '''
    Listen for command from the client
    timeout: listen for command this long in seconds (0=listen for ever)
    Return tuple with (command, data)  data is a bytearray
           Can return None, None if no data or timeout
           Or command, None if no data with the command
    '''
    with lock:
        _transmitter(False)
        # Listen for a request
        count = 0
        try:
            while not radio.available(null_pipe):
                time.sleep(0.001)
                if timeout!=0:
                    if count >= (timeout*400):
                        return None, None # Timeout
                    count = count+1
            # Clear the buffer
            del buff[:]
            # Read request
            radio.read(buff)
            # must be more than 2 byte
            if len(buff)<3:
                return None, None
            else:
                # 0: No data/No more data
                # 1:Has data/Has more data
                more = buff[0]
                # Rest of this package is the command name
                buff.pop(0)
                command = bytearray(buff).decode("utf-8")
                if more==1:
                    data = bytearray()
                    while more==1:
                        # Listen for more data
                        count = 0
                        while not radio.available(pipes[1]):
                            time.sleep(0.001)
                            if timeout!=0:
                                if count >= (timeout*400):
                                    return None, None # Timeout
                                count = count+1
                        # Clear the buffer
                        del buff[:]
                        # Read request
                        radio.read(buff)
                        # must be more than 1 byte
                        if len(buff)<2:
                            more = 0
                        else:
                            more = buff[0]
                            buff.pop(0)
                            # Rest of this package is data
                            data.extend(bytearray(buff))
                    return command, data
                else:
                    return command, None
        except AttributeError, e:
            return None, None



def response(data=None):
    '''
    Return a OK answer to to client
    data: bytearray
    '''
    global last_r
    global last_r_no
    with lock:
        _transmitter(True)
        if data==None:
            # ok response with no data
            del buff[:]
            buff.append(last_r_no)
            if last_r_no==0:
                last_r_no=1
            else:
                last_r_no=0
            radio.write(buff)
        else:
            chunks = steelsquid_utils.split_chunks(data, package_size-1)
            cou=0
            for chunk in chunks:
                cou = cou + len(chunk)
                del buff[:]
                if chunk == chunks[-1]:
                    # No more data to send after this
                    buff.append(last_r_no)
                    if last_r_no==0:
                        last_r_no=1
                    else:
                        last_r_no=0
                else:
                    # More datat to send after this
                    buff.append(last_r)
                    if last_r==2:
                        last_r=3
                    else:
                        last_r=2
                buff.extend(bytearray(chunk))
                radio.write(buff)


def error(message=None):
    '''
    Return a ERROR answer to to client
    message: Max ? characters long (will cut it)
    '''
    global last_e
    with lock:
        _transmitter(True)
        del buff[:]
        buff.append(last_e)
        if last_e==4:
            last_e=5
        else:
            last_e=4
        if message != None and len(message)>0:
            if len(message)>package_size-1:
                message = message[:package_size-1]
            buff.extend(bytearray(message))
        radio.write(buff)
        

def request(command, data=None, timeout=4):
    '''
    Send a command to the server and wait for answer
    Can raise exception when server return error
    command: Max ? characters
    data: bytearray to the server
    timeout: listen for answer this long in seconds (0=listen for ever)
    Return: data (list of bytes from the server) None=timeout
    '''
    with lock:
        if radio!=None:
            if len(command)>package_size-1:
                raise Exception("Command max "+str(package_size-1)+" charactors")
            _transmitter(True)
            if data==None:
                # Send command with no data
                del buff[:]
                buff.append(0)
                buff.extend(bytearray(command))
                radio.write(buff)
            else:
                # Send command with data
                # First send command
                del buff[:]
                buff.append(1)
                buff.extend(bytearray(command))
                radio.write(buff)
                #Then send all the data
                chunks = steelsquid_utils.split_chunks(data, package_size-1)
                for chunk in chunks:
                    del buff[:]
                    if chunk == chunks[-1]:
                        # No more data to send after this
                        buff.append(0)
                    else:
                        # More datat to send after this
                        buff.append(1)
                    buff.extend(bytearray(chunk))
                    radio.write(buff)
            _transmitter(False)
            data = bytearray()
            more = 2
            try:
                while more==2 or more==3:
                    # Listen for more data
                    count=0
                    while not radio.available(null_pipe):
                        time.sleep(0.001)
                        if timeout!=0:
                            if count >= (timeout*400):
                                return None  # Timeout
                            count = count+1
                    # Clear the buffer
                    del buff[:]
                    # Read request
                    radio.read(buff)
                    # must be more than 1 byte
                    le = len(buff)
                    if le==0:
                        more = 0
                    elif le==1:
                        more = buff[0]
                    else:
                        more = buff[0]
                        buff.pop(0)
                        # Rest of this package is data
                        data.extend(bytearray(buff))
                if more == 4 or more == 5:
                    raise Exception(data.decode("utf-8"))
                else:
                    return data
            except AttributeError, e:
                return None
            
            
            
            
            
            
def main(command_method, channel=0x70, bit_rate=BR_2MBPS):
    '''
    Start as main and register a command_method
    When subordinate send command to the main the command_method will execute with the command as argument
    The argument is a string (max length=package_size)
    '''
    global command_callback_method
    _init(channel, bit_rate)
    radio.enableAckPayload()
    radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.startListening()
    radio.stopListening()
    command_callback_method = command_method


def send(data):
    '''
    Send data to the client
    Return True/False if succesfull
    '''
    del buff[:]
    # Split the data into chucks
    if data == None:
        chunks = []
    else:
        chunks = steelsquid_utils.split_chunks(data, package_size-1)
    if len(chunks)==0:
        chunks.append(None)
    for chunk in chunks:
        del buff[:]
        if chunk==None or chunk == chunks[-1]:
            # No more data to send after this
            buff.append(0)
        else:
            # More datat to send after this
            buff.append(1)
        if chunk!=None:
            buff.extend(bytearray(chunk))
        # Send the chunk
        if radio.write(buff):
            radio.whatHappened()
            # did it return with a payload (subordinate send back command)
            #if radio.isAckPayloadAvailable():   
            del buff[:] 
            radio.read(buff, radio.getDynamicPayloadSize())
            if len(buff)>1:
                command = bytearray(buff).decode("utf-8")
                # Execute the callbackmethod
                try:
                    command_callback_method(command)
                except:
                    steelsquid_utils.shout()
        else:
            radio.whatHappened()
            return False
    return True
            

def subordinate(channel=0x70, bit_rate=BR_2MBPS):
    '''
    Start this as subordinate.
    '''
    _init(channel, bit_rate)
    radio.enableAckPayload()
    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    radio.startListening()
    radio.stopListening()


def receive(timeout=0):
    '''
    Listen for data from the main
    timeout: listen this long in seconds then return None (0 = listen forever)
    '''
    global command_to_send
    # Listen for data
    data = bytearray()
    radio.startListening()
    while True:
        count=0
        while not radio.available(null_pipe):
            time.sleep(0.001)
            if timeout!=0:
                if count >= (timeout*400):
                    return None  # Timeout
                count = count+1
        # Clear the buffer
        del buff[:]
        # the answer array
        radio.read(buff, radio.getDynamicPayloadSize())
        # must be more than 0 byte
        if len(buff)==0:
            return data
        else:
            # 0: No data/No more data
            # 1: Has data/Has more data
            more = buff[0]
            # Rest of this package is data
            buff.pop(0)
            data.extend(bytearray(buff))            
            # Is there some command to send to the main
            if command_to_send!=None:
                cts = command_to_send
                command_to_send=None
                radio.writeAckPayload(1, cts, len(cts))  
            else:
                radio.writeAckPayload(1, [0], 1)  
            # No more data return the answer
            if more==0:
                return data
            
   
def command(the_command, parameters=None):
    '''
    Then in a nother thread the subordinate can execute this to sned command to the main
    the_command + parameters kan be max 32 charactors long
    Paramaters: List of strings
    If you enter parameters the string to the main will lock like: the_command|parameters1|parameters2...
    If parameters=None the string sent to main is only the_command
    '''
    global command_to_send
    if parameters==None:
        the_command = bytearray(the_command)
        if len(the_command)>package_size:
            raise Exception("Command max "+str(package_size)+" charactors")
        command_to_send=the_command
    else:
        string = the_command + "|" + "|".join(parameters)
        string = bytearray(string)
        if len(string)>package_size:
            raise Exception("Command max "+str(package_size)+" charactors")
        command_to_send=string
        
            
            
def stop():
    '''
    Stop and clean this server/client
    '''
    try:
        radio.end()
        radio = None
    except:
        pass
        

def to_boolean(data):
    '''
    Convert data to a boolean
    '''
    if data==None:
        return False
    data = str(data).lower()
    if data=="1" or data=="true" or data=="y":
        return True
    else:
        return False


def to_string(data):
    '''
    Convert data to string
    '''
    if data!=None:
        data = data.decode("utf-8")
        return data
    else:
        return None


def to_int(data):
    '''
    Convert data to int
    '''
    if data!=None:
        data = data.decode("utf-8")
        return int(data)
    else:
        return None


def to_list(data):
    '''
    Convert data to list with strings in
    '''
    if data!=None:
        return data.decode("utf-8").split("|")
    else:
        return None


def from_boolean(b):
    '''
    Convert boolean to data you can send
    '''
    if b:
        return "1"
    else:
        return "0"


def from_string(s):
    '''
    Convert string to data you can send
    '''
    return bytearray(s)


def from_int(i):
    '''
    Convert int to data you can send
    '''
    return bytearray(str(i))


def from_list(l):
    '''
    Convert data to list with strings in
    '''
    return bytearray('|'.join(l))
