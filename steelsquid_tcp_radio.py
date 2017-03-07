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

# Port nuumbers
PORT_SYNC = 6601
PORT_COMMAND = 6602
PORT_PUSH = [0, 6603, 6604, 6605, 6606]

# Timeout on send data
TIMEOUT = 4

# Number of seconds meaning that the connection is lost
CONNECTION_LOST = 4

# The socket listen/connect (sync)
lis_sync = None
con_sync = None

# The socket listen/connat (commands)
lis_command = None
con_command = None

# The socket listen/connat (push)
lis_push = [None] * 6
con_push = [None] * 6

#Read buffers
buff_sync = None
buff_command = None
buff_push = [None] * 6

# Server/port
is_t_remote = False
server_ip = None

# Last Sync
last_sync = datetime.datetime.now()

# Last command
last_command = datetime.datetime.now()

# Last push
last_push = [datetime.datetime.now()] * 6

# End of package
ETB = chr(0x17)

# OK response
ACK = chr(0x06)

# ERROR response
NAK = chr(0x15)

# Ping request
BEL = chr(0x7)

# Lock when send request
lock = threading.Lock()

# How long is the ping time
ping_time = -1


def setup_server(is_the_remote):
    '''
    Setup this as the sever.
    The server will listen for connections from the client
    is_the_remote = this one send the push and request to the other 
    '''
    global lis_sync
    global lis_command
    global server_ip
    global is_t_remote
    global buff_sync
    global buff_command
    close()
    buff_sync = StringIO.StringIO()
    buff_command = StringIO.StringIO()
    buff_push[1] = StringIO.StringIO()
    buff_push[2] = StringIO.StringIO()
    buff_push[3] = StringIO.StringIO()
    buff_push[4] = StringIO.StringIO()
    server_ip = None
    is_t_remote = is_the_remote
    socket.setdefaulttimeout(TIMEOUT)
    # Create sync socket
    lis_sync = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_sync.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_sync.bind(('', PORT_SYNC))    
    lis_sync.listen(3)
    lis_sync.settimeout(TIMEOUT)
    # Create command socket
    lis_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_command.bind(('', PORT_COMMAND))    
    lis_command.listen(3)
    lis_command.settimeout(TIMEOUT)
    # Create push 1 socket
    lis_push[1] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_push[1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_push[1].bind(('', PORT_PUSH[1]))    
    lis_push[1].listen(3)
    lis_push[1].settimeout(TIMEOUT)
    # Create push 2 socket
    lis_push[2] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_push[2].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_push[2].bind(('', PORT_PUSH[2]))    
    lis_push[2].listen(3)
    lis_push[2].settimeout(TIMEOUT)
    # Create push 3 socket
    lis_push[3] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_push[3].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_push[3].bind(('', PORT_PUSH[3]))    
    lis_push[3].listen(3)
    lis_push[3].settimeout(TIMEOUT)
    # Create push 4 socket
    lis_push[4] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lis_push[4].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lis_push[4].bind(('', PORT_PUSH[4]))    
    lis_push[4].listen(3)
    lis_push[4].settimeout(TIMEOUT)


def setup_client(is_the_remote, host):
    '''
    Setup this as the client.
    The client will try to connect to the server
    is_the_remote = this one send the push and request to the other 
    '''
    global con_sync
    global con_command
    global server_ip
    global is_t_remote
    global buff_sync
    global buff_command
    close()
    buff_sync = StringIO.StringIO()
    buff_command = StringIO.StringIO()
    buff_push[1] = StringIO.StringIO()
    buff_push[2] = StringIO.StringIO()
    buff_push[3] = StringIO.StringIO()
    buff_push[4] = StringIO.StringIO()
    server_ip = host
    is_t_remote = is_the_remote
    socket.setdefaulttimeout(TIMEOUT)
        

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
    return diff.total_seconds()<CONNECTION_LOST
    

def get_last_ping_time():
    '''
    How long did last response of ping take
    '''
    return ping_time
    

def get_last_sync():
    '''
    How long sinse last synk
    '''
    diff = datetime.datetime.now()-last_sync
    return diff.total_seconds()


def get_last_command():
    '''
    How long sinse last command
    '''
    diff = datetime.datetime.now()-last_command
    return diff.total_seconds()


def get_last_push(nr):
    '''
    How long sinse last push
    '''
    diff = datetime.datetime.now()-last_push[nr]
    return diff.total_seconds()


def sync_connected():
    '''
    Is it connected to remote host
    '''
    return con_sync!=None


def sync_disconnect():
    '''
    diconnect from host
    '''
    global con_sync
    try:
        con_sync.close()
    except:
        pass
    con_sync = None


def sync_listen():
    '''
    Listen on sync socket 
    '''
    global lis_sync
    global con_sync
    global last_sync
    new_con, _ = lis_sync.accept()
    try:
        con_sync.close()
    except:
        pass
    last_sync = datetime.datetime.now()
    con_sync = new_con


def sync_connect():
    '''
    Connect the sync socket
    '''
    global con_sync
    global last_sync
    try:
        con_sync.close()
    except:
        pass
    con_sync = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con_sync.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    con_sync.settimeout(TIMEOUT)
    con_sync.connect((server_ip, PORT_SYNC))
    last_sync = datetime.datetime.now()
    

def command_connected():
    '''
    Is it connected to remote host
    '''
    return con_command!=None


def command_disconnect():
    '''
    diconnect from host
    '''
    global con_command
    try:
        con_command.close()
    except:
        pass
    con_command = None


def command_listen():
    '''
    Listen on command socket 
    '''
    global lis_command
    global con_command
    global last_command
    new_con, _ = lis_command.accept()
    new_con.settimeout(TIMEOUT)
    try:
        con_command.close()
    except:
        pass
    last_command = datetime.datetime.now()
    con_command = new_con


def command_connect():
    '''
    Connect the command socket
    '''
    global con_command
    global last_command
    try:
        con_command.close()
    except:
        pass
    con_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    con_command.settimeout(TIMEOUT)
    con_command.connect((server_ip, PORT_COMMAND))
    last_command = datetime.datetime.now()
    

def push_listen(nr):
    '''
    Listen on push_1 socket 
    '''
    new_con, _ = lis_push[nr].accept()
    new_con.settimeout(TIMEOUT)
    try:
        con_push[nr].close()
    except:
        pass
    last_push[nr] = datetime.datetime.now()
    con_push[nr] = new_con


def push_connected(nr):
    '''
    Is it connected to remote host
    '''
    return con_push[nr]!=None


def push_disconnect(nr):
    '''
    diconnect from host
    '''
    try:
        con_push[nr].close()
    except:
        pass
    con_push[nr] = None


def push_connect(nr):
    '''
    Connect the push_1 socket
    '''
    try:
        con_push[nr].close()
    except:
        pass
    con_push[nr] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con_push[nr].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    con_push[nr].settimeout(TIMEOUT)
    
    con_push[nr].connect((server_ip, PORT_PUSH[nr]))
    last_push[nr] = datetime.datetime.now()
    

def sync_request(data):
    '''
    Write a sync request and wait for response
    data: is a list of strings
    Return data (is a list of strings from the response) 
    Raise: exception (connection lost)
    '''
    global last_sync
    _write_data(con_sync, data)
    answer = _read_data(con_sync, buff_sync)
    last_sync = datetime.datetime.now()
    return answer


def sync_read():
    '''
    Listen for sync request
    Return data (is a list of strings) (Can be None)
    Raise: socket.Timeouterror (Do nothing)
    Raise: other exception (connection lost)
    '''
    global last_sync
    answer = _read_data(con_sync, buff_sync)
    last_sync = datetime.datetime.now()
    return answer


def sync_response(data):
    '''
    Write a sync response
    data: is a list of strings
    Raise: exception (connection lost)
    '''
    _write_data(con_sync, data)

    
def command_request(command, data):
    '''
    Write a command request and wait for response
    data: is a list of strings
    Return data (is a list of strings from the response)
    Raise: exception (error on request)
    '''
    
    with(lock):
        global last_command
        _write_command(con_command, command, data)
        status, answer = _read_ok_err(con_command, buff_command)
        last_command = datetime.datetime.now()
        if status:
            return answer
        else:
            raise RuntimeError(command + ": "+answer) 


def command_read():
    '''
    Listen for command request
    Return command, data (is a list of strings)
    Raise: socket.Timeouterror (Do nothing)
    Raise: other exception (connection lost)
    '''
    global last_command
    command, answer = _read_command(con_command, buff_command)
    last_command = datetime.datetime.now()
    return command, answer


def command_response_ok(data):
    '''
    Write a OK command response
    data: is a list of strings 
    Raise: exception (connection lost)
    '''
    _write_ok(con_command, data)


def command_response_err(error_string):
    '''
    Write a ERROR command response
    Raise: exception (connection lost)
    '''
    _write_err(con_command, error_string)


def command_ping():
    '''
    Send ping
    Raise: exception (connection lost)
    '''
    global last_command
    global ping_time
    with(lock):
        try:
            start = datetime.datetime.now()
            con_command.sendall(BEL)
            data = con_command.recv(1)
            ping_time = (datetime.datetime.now() - start).total_seconds()
            con_command.sendall(BEL)
            last_command = datetime.datetime.now()
        except Exception as e:
            ping_time = 99
            raise e


def push_request(nr, data):
    '''
    Write a push_1 request
    data: is a list of strings
    Raise: exception (connection lost)
    '''
    _write_data(con_push[nr], data)
    last_push[nr] = datetime.datetime.now()


def push_read(nr):
    '''
    Listen for push_1 request
    Return data (is a list of strings)
    Raise: socket.Timeouterror (Do nothing)
    Raise: other exception (connection lost)
    '''
    answer = _read_data(con_push[nr], buff_sync, is_push=nr)
    last_push[nr] = datetime.datetime.now()
    return answer


def push_ping(nr):
    '''
    Send ping
    Raise: exception (connection lost)
    '''
    _write_ping(con_push[nr])
    last_push[nr] = datetime.datetime.now()










def _write_data(con, data):
    '''
    Send a package
    '''
    if data==None:
        con.sendall(ETB)
    else:
        data = '|'.join([str(mli) for mli in data])
        h = steelsquid_utils.mini_hash(data)
        con.sendall(data + ETB + h)


def _write_command(con, command, data):
    '''
    Send a package
    '''
    if data==None:
        con.sendall(command + ETB + ETB)
    else:
        data = '|'.join([str(mli) for mli in data])
        h = steelsquid_utils.mini_hash(data)
        con.sendall(command + ETB + data + ETB + h)


def _write_ok(con, data):
    '''
    Send a package
    '''
    if data==None:
        con.sendall(ACK + ETB)
    else:
        data = '|'.join([str(mli) for mli in data])
        h = steelsquid_utils.mini_hash(data)
        con.sendall(ACK + data + ETB + h)


def _write_ping(con):
    '''
    Send a package
    '''
    con.sendall(BEL)


def _write_err(con, error):
    '''
    Send a package
    '''
    if error==None:
        con.sendall(NAK + ETB)
    else:
        h = steelsquid_utils.mini_hash(error)
        con.sendall(NAK + error + ETB + h)


def _read_data(con, buff, is_push=0):
    '''
    Read a package
    '''
    global last_sync
    buff.truncate(0)
    buff.seek(0)
    while True:
        data = con.recv(1)
        if data==None or data == '':
            raise socket.error("socket connection broken")        
        if data == ETB: 
            break       
        if data == BEL: 
            last_push[is_push] = datetime.datetime.now()
            raise socket.timeout("PING")        
        else:     
            buff.write(data)
    if buff.len>0:
        ca = con.recv(1)
        data = buff.getvalue()
        h = steelsquid_utils.mini_hash(data)
        if h == ca:
            data = data.split("|")
            return data
        else:
            return None
    else:
        return []


def _read_command(con, buff):
    '''
    Read a package
    '''
    global last_command
    global ping_time
    buff.truncate(0)
    buff.seek(0)
    while True:
        data = con.recv(1)
        if data==None or data == '':
            raise socket.error("socket connection broken")        
        if data == ETB: 
            break       
        if data == BEL: 
            last_command = datetime.datetime.now()
            try:
                start = datetime.datetime.now()
                con.sendall(BEL)
                data = con.recv(1)
                ping_time = (datetime.datetime.now() - start).total_seconds()
            except Exception as e:
                ping_time = 99
                raise e
            raise socket.timeout("PING")        
        else:     
            buff.write(data)
    
    command = buff.getvalue()
    
    buff.truncate(0)
    buff.seek(0)
    while True:
        data = con.recv(1)
        if data==None or data == '':
            raise socket.error("socket connection broken")        
        if data == ETB: 
            break       
        buff.write(data)
    if buff.len>0:
        ca = con.recv(1)
        data = buff.getvalue()
        h = steelsquid_utils.mini_hash(data)
        if h == ca:
            data = data.split("|")
            return command, data
        else:
            return None, None        
    else:
        return command, []


def _read_ok_err(con, buff):
    '''
    Read a package
    '''
    global last_command
    buff.truncate(0)
    buff.seek(0)
    is_ok = None
    while True:
        data = con.recv(1)
        if data==None or data == '':
            raise socket.error("socket connection broken")        
        if data == ETB: 
            break       
        if is_ok==None:
            if data == ACK: 
                is_ok = True
            if data == NAK: 
                is_ok = False
        else:     
            buff.write(data)
    if buff.len>0:
        ca = con.recv(1)
        data = buff.getvalue()
        h = steelsquid_utils.mini_hash(data)
        if h == ca:
            if is_ok:
                return True, data.split("|")
            else:
                return False, data
        else:
            raise socket.timeout("CRC error")        
    else:
        if is_ok:
            return True, []
        else:
            return False, ""

         









def close():
    '''
    Close all
    '''
    close_listeners()
    close_connections()
    try:
        buff_sync.close()
    except:
        pass
    try:
        buff_command.close()
    except:
        pass
    try:
        buff_push[0].close()
    except:
        pass
    try:
        buff_push[1].close()
    except:
        pass
    try:
        buff_push[2].close()
    except:
        pass
    try:
        buff_push[3].close()
    except:
        pass
    
 
def close_listeners():
    '''
    Close all listeners
    '''
    global lis_sync
    global lis_command
    try:
        lis_sync.close()
    except:
        pass
    lis_sync = None
    try:
        lis_command.close()
    except:
        pass
    lis_command = None
    try:
        lis_push[0].close()
    except:
        pass
    lis_push[0] = None
    try:
        lis_push[1].close()
    except:
        pass
    lis_push[1] = None
    try:
        lis_push[2].close()
    except:
        pass
    lis_push[2] = None
    try:
        lis_push[3].close()
    except:
        pass
    lis_push[3] = None


def close_connections():
    '''
    Close all connections
    '''
    sync_disconnect()
    command_disconnect()
    push_disconnect(1)
    push_disconnect(2)
    push_disconnect(3)
    push_disconnect(4)





