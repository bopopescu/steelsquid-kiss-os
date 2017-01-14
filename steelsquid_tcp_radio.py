#!/usr/bin/python -OO


'''
Send and reseive messages using tcp 

One of the devices is server and the other client.
One listen for commands and return answer.
The other send commadn and read the answer

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
import socket
import sys
import steelsquid_pi
import StringIO

# The socket
sock = None
con = None

# Server/port
is_t_remote = False
server_ip = None
port_nr = None

# Try to resend a request this number of times if get timout
NUMBER_OF_RETRY = 3

# Only one thread can use this at a time    
lock = threading.RLock()

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

# Sync request
# steelsquid kiss os using this when sync variables between client and server
SYN = chr(0x16)

# Bell
# Using this to check that connection is open...
BEL = chr(0x06)

# Last OK send/reseive 
last_sync = datetime.datetime.now()

# Timeout on connection read
TIMEOUT = 2

def setup(is_the_remote, host=None, port=6601):
    '''
    Setup the interface
    is_the_remote = this one send the push to the other 
    if host==None (this is a server, listen for connections)
    
    '''
    global sock
    global server_ip
    global port_nr
    global is_t_remote
    server_ip = host
    is_t_remote = is_the_remote
    port_nr = port
    if is_server:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port_nr))    
        sock.listen(3)
        

def is_server():
    '''
    It this unit a server
    '''
    return server_ip == None


def is_remote():
    '''
    It this one send the push to the other 
    '''
    return is_t_remote


def is_linked():
    '''
    After about 4 seconds without sync the link is probably lost
    '''
    diff = datetime.datetime.now()-last_sync
    return diff.total_seconds()<4


def get_last_link():
    '''
    How long sinse last synk
    '''
    diff = datetime.datetime.now()-last_sync
    return diff.total_seconds()


def is_connected():
    '''
    Is connected
    '''
    return con != None


def connect():
    '''
    Connect to server
    '''
    global sock
    global con
    close_connection()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((server_ip, port_nr))
    sock.settimeout(TIMEOUT)
    con = sock


def listen_for_connection():
    '''
    Listen for connections from client
    '''
    global con
    new_con, _ = sock.accept()
    new_con.settimeout(TIMEOUT)
    close_connection()
    con = new_con


def close_connection():
    '''
    Close connecxtion
    '''
    global con
    try:
        con.close()
    except:
        pass
    con = None


def close_listener():
    '''
    Close listener
    '''
    global sock
    try:
        sock.close()
    except:
        pass
    sock = None


def stop():
    '''
    Close 
    '''
    close_listener()
    close_connection()


def _write_data(typ, data):
    '''
    Send a package
    '''
    if data==None:
        _write(typ+"\n")
    else:
        data = '|'.join([str(mli) for mli in data])
        _write(typ+data+"\n")


def _write_error(typ, error):
    '''
    Send a package
    '''
    if error==None:
        _write(typ+"\n")
    else:
        _write(typ+str(error)+"\n")


def _write_command(typ, command, data):
    '''
    Send a package
    '''
    if data==None:
        _write(typ+command+"\n\n")
    else:
        data = '|'.join([str(mli) for mli in data])
        _write(typ+command+"\n"+data+"\n")

             
def _write(string):
    '''
    Send a string to the remote host
    '''
    if con == None:
        raise socket.error("socket connection broken")
    con.sendall(string)
        
        
def _write_char(char):
    '''
    Send a char to the remote host
    '''
    if con == None:
        raise socket.error("socket connection broken")
    con.sendall(char)
        
        
def _read_chr():
    '''
    Read a char from the remote host
    '''
    if con == None:
        raise socket.error("socket connection is None")
    chunk = con.recv(1)
    if chunk==None:
        raise socket.error("socket connection broken: None")        
    if chunk == '':
        raise socket.error("socket connection broken: ''")        
    return chunk

        
        
def _read_1_line():
    '''
    Read one line
    '''
    if con == None:
        raise socket.error("socket connection broken")
    buff = StringIO.StringIO()
    try:
        while True:
            data = con.recv(1)
            if data==None or data == '':
                raise socket.error("socket connection broken")        
            if data == '\n': 
                break       
            else:     
                buff.write(data)
        chunk = buff.getvalue()
        return chunk
    finally:
        buff.close()


def _read_2_lines():
    '''
    Read two lines
    '''
    if con == None:
        raise socket.error("socket connection broken")
    buff = StringIO.StringIO()
    try:
        while True:
            data = con.recv(1)
            if data==None or data == '':
                raise socket.error("socket connection broken")        
            if data == '\n': 
                break       
            else:     
                buff.write(data)
        nr1 = buff.getvalue()
        buff.close()
        buff = StringIO.StringIO()
        while True:
            data = con.recv(1)
            if data==None or data == '':
                raise socket.error("socket connection broken")        
            if data == '\n': 
                break       
            else:     
                buff.write(data)
        
        nr2 = buff.getvalue()
        if len(nr2)==0:
            nr2=""
        return nr1, nr2
    finally:
        buff.close()
         
            
def listen():
    '''
    Listen for command from the client
    Return tuple with (command, data)  data is a list of strings
    Return None = do nothing
    '''
    with lock:
        global last_sync
        # Read request
        req = _read_chr()
        if req==SUB:
            # Read broadcast command
            command, data = _read_2_lines()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return command, data
        elif req==ENQ:
            # Read request command
            command, data = _read_2_lines()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return command, data
        elif req==DC1:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_1_line()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 1, data # 1 indicate that it is a push broadcast
        elif req==DC2:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_1_line()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 2, data # 2 indicate that it is a push broadcast
        elif req==DC3:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_1_line()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 3, data # 3 indicate that it is a push broadcast
        elif req==DC4:
            # Read push data (steelsquid-kiss os using this...)
            data = _read_1_line()
            if len(data)==0:
                data = []
            else:
                data = data.split("|")
            last_sync = datetime.datetime.now()
            return 4, data # 4 indicate that it is a push broadcast
        elif req==SYN:
            # Read sync data (steelsquid-kiss os using this...)
            data = _read_1_line()
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
    with lock:
        # Write push answer
        _write_data(SYN, data)


def response(data=None):
    '''
    Return a OK answer to to client
    data: Data to responde back to client with (data is a list of strings)
    '''
    with lock:
        # Write ok answer
        _write_data(ACK, data)
        

def error(message=None):
    '''
    Return a ERROR answer to to client
    message: The error message to send back to client (a string)
    '''
    with lock:
        # Write error answer
        _write_error(NAK, message)
        

def request(command, data=None):
    '''
    Send a command to the server and wait for answer,
    command: The command
    data: Data to the server  (data is a list of strings)
    Return: data (data is a list of strings from the server)
    '''
    global last_sync
    with lock:
        # Write a request
        _write_command(ENQ, command, data)
        # Listen for response
        req = _read_chr()
        if req == ACK:
            le = _read_1_line()
            if len(le)==0:
                last_sync = datetime.datetime.now()
                return []
            else:
                last_sync = datetime.datetime.now()
                return le.split("|")
        elif req == NAK:
            raise Exception(command +": "+ _read_1_line())
        else:
            raise socket.error("Unknown response: "+str(req))
 
 
def request_sync(data=None):
    '''
    Send a command to the server and wait for answer
    This will send a sync request...steelsquid_kiss_os using this...
    data: Data to the server  (data is a list of strings)
    Return: data (data is a list of strings from the server)
    '''
    global last_sync
    with lock:
        # Write a sync request
        _write_data(SYN, data)
        # Listen for response
        req = _read_chr()
        if req == SYN:
            le = _read_1_line()
            if len(le)==0:
                last_sync = datetime.datetime.now()
                return []
            else:
                last_sync = datetime.datetime.now()
                return le.split("|")
        else:
            raise socket.error("Unknown sync response...")
            

def broadcast(command, data=None):
    '''
    Broadcast to the server...do not wait for any answer
    command: The command
    data: Data to the server  (data is a list of strings)
    '''
    global last_sync
    with lock:
        # Write a broadcast
        _write_command(SUB, command, data)
            
            
def broadcast_push(push_nr, data=None):
    '''
    Broadcast to the server...do not wait for any answer
    This will send a push requst...steelsquid_kiss_os using this....
    data: Data to the server  (data is a list of strings)
    '''
    with lock:
        # Write a push broadcast
        if push_nr==1:
            _write_data(DC1, data)
        if push_nr==2:
            _write_data(DC2, data)
        if push_nr==3:
            _write_data(DC3, data)
        if push_nr==4:
            _write_data(DC4, data)
            



