#!/usr/bin/python -OO


'''
Automatic listen for changes abd commit changes to a nother system via ssh (install on remote system)
Messages and error from the raspberry will also be displayed (same as on the console on the Raspberry Pi).
Example if you execute steelsquid_utils.shout(...) or steelsquid_utils.debug(...) it will show up on the screen when you syncronize.

Using settings from steelsquid-kiss-os.sh
base_remote_server=192.168.0.194
base_remote_port=22
base_remote_user=root
base_remote_password=raspberry

Settings will be used in config.txt is it exists.
4 first rows:
ip
port
user
password

Will check for changes in this files:
steelsquid-kiss-os.sh
The files in the paramater python_downloads inside steelsquid-kiss-os.sh
The files in the paramater web_root_downloads inside steelsquid-kiss-os.sh

Will also check config.txt 6 row and forward for files.
Example config.txt
192.168.0.194
22
root
raspberry

/home/steelsquid/steelsquid-kiss-os/mypythonfile.py|/opt/steelsquid/python/mypythonfile1.py
/home/steelsquid/steelsquid-kiss-os/autoinportthis.py|/opt/steelsquid/python/run/autoinportthis.py
/home/steelsquid/steelsquid-kiss-os/myhtml.html|/opt/steelsquid/web/myhtml.html

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import time
import sys
import thread
import threading
import os
import steelsquid_utils
import paramiko
import select
from datetime import datetime

steel_last = 0
base_remote_server=""
base_remote_port=""
base_remote_user=""
base_remote_password=""
python_files = []
web_files = []
extra_files = []
ssh = None
sftp = None
channel = None
channel_f = None
lock = threading.Lock()

def load_data():
    '''
    '''
    global base_remote_server
    global base_remote_port
    global base_remote_user
    global base_remote_password
    global python_files
    global web_files
    global extra_files
    print ""
    steelsquid_utils.log("Load settings from steelsquid-kiss-os.sh")
    with open("steelsquid-kiss-os.sh") as f:
        for line in f:
            line = line.replace("\n","")
            if line.startswith("base_remote_server="):
                base_remote_server = line.split("=")[1]
            elif line.startswith("base_remote_port="):
                base_remote_port = line.split("=")[1]
            elif line.startswith("base_remote_user="):
                base_remote_user = line.split("=")[1]
            elif line.startswith("base_remote_password="):
                base_remote_password = line.split("=")[1]
            elif line.startswith("python_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                python_files.append([line, 0])
            elif line.startswith("web_root_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                web_files.append([line, 0])
    if os.path.isfile("config.txt"):
        print ""
        steelsquid_utils.log("Load settings from config.txt")
        i = 0
        with open("config.txt") as f:
            for line in f:
                line = line.replace("\n","")
                if i == 0:
                    base_remote_server = line
                elif i == 1:
                    base_remote_port = line
                elif i == 2:
                    base_remote_user = line
                elif i == 3:
                    base_remote_password = line
                elif i > 4:
                    line = line.split("|")
                    line[0] = line[0].strip()
                    line[1] = line[1].strip()
                    line.append(0)
                    extra_files.append(line)
                i = i + 1 

        
def listener():
    '''
    '''
    global steel_last
    while True:
        steel_file = "steelsquid-kiss-os.sh"
        steel_change = os.path.getmtime(steel_file)
        if steel_change != steel_last:
            steel_last = steel_change
            transmit(steel_file, "/opt/steelsquid/"+steel_file)
        for o in python_files:
            file_name = o[0]
            file_last = o[1]
            file_change = os.path.getmtime(file_name)
            if file_change != file_last:
                o[1] = file_change
                transmit(file_name, "/opt/steelsquid/python/"+file_name)
        for o in web_files:
            file_name = o[0]
            file_last = o[1]
            file_change = os.path.getmtime(file_name)
            if file_change != file_last:
                o[1] = file_change
                transmit(file_name, "/opt/steelsquid/web/"+file_name)
        for o in extra_files:
            file_local = o[0]
            file_remote = o[1]
            file_last = o[2]
            file_change = os.path.getmtime(file_local)
            if file_change != file_last:
                o[2] = file_change
                transmit(file_local, file_remote)
        time.sleep(0.5)


def connect():
    with lock:
        global ssh
        global channel
        global channel_f
        global sftp
        disconnect()
        try:
            print ""
            steelsquid_utils.log("Connecting to: " + base_remote_server)
            ssh.connect(base_remote_server, port=int(base_remote_port), username=base_remote_user, password=base_remote_password)
            channel = ssh.get_transport().open_session()
            channel.get_pty()
            channel.invoke_shell()
            channel_f = channel.makefile()
            sftp = ssh.open_sftp()
        except Exception, e:
            steelsquid_utils.log(str(e))
            raise e


def disconnect():
    global ssh
    global sftp
    try:
        sftp.close()
    except:
        pass
    try:
        ssh.close()
    except:
        pass
    

def transmit(local, remote):
    print ""
    steelsquid_utils.log("SYNC: " + local)
    try:
        sftp.put(local, remote)
    except:
        try:
            connect()
            sftp.put(local, remote)            
        except:
            pass
        

def send_command(command):
    '''
    '''
    try:
        ssh.exec_command(command)
    except:
        try:
            connect()
            ssh.exec_command(command)
        except:
            pass


def listen_for_std():
    '''
    '''
    time.sleep(1)
    print ""
    steelsquid_utils.log("Listen for output from remote device")
    global channel_f
    while True:
        try:
            if not channel_f.closed:
                first = True
                last_time = 1000
                for line in channel_f:
                    if first:
                        first = False
                    else:
                        line = line[:-1]
                        line = " ".join(line.split())
                        if len(line)>0:
                            cur_time = time.time() * 1000
                            ms = cur_time - last_time
                            if ms > 100:
                                print ""
                                steelsquid_utils.log("FROM REMOTE DEVICE:")
                            print line
                            last_time = cur_time
        except:
            steelsquid_utils.shout()
            try:
                connect()
            except:
                pass
        time.sleep(2)
            
    

if __name__ == '__main__':
    load_data()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        connect()
    except:
        pass
    thread.start_new_thread(listen_for_std, ()) 
    print ""
    print "Listen for changes and commit to " + base_remote_server
    print " - 0, H: Show this help."
    print " - 1, Q: This program will terminate."
    print " - 2, C: Reload the custom modules."
    print " - 3, E: Reload the HTTP and Socket expand server."
    print " - 4, S: Restart steelsquid service."
    print " - 5, K: Stop steelsquid service."
    print " - 6, R: Reboot the remote machine."
    thread.start_new_thread(listener, ()) 
    answer = ""
    cont = True
    while cont:
        answer = raw_input()
        if answer == "0" or answer == "H" or answer == "h":
            print "Listen for changes and commit to " + base_remote_server
            print " - 0, H: Show this help."
            print " - 1, Q: This program will terminate."
            print " - 2, C: Reload the custom modules."
            print " - 3, E: Reload the HTTP and Socket expand server."
            print " - 4, S: Restart steelsquid service."
            print " - 5, K: Stop steelsquid service."
            print " - 6, R: Reboot the remote machine."
        elif answer == "1" or answer == "Q" or answer == "q":
            cont = False
        elif answer == "2" or answer == "C" or answer == "c":
            steelsquid_utils.log("Request reload of custom modules")
            send_command("steelsquid-event reload custom")
        elif answer == "3" or answer == "E" or answer == "e":
            steelsquid_utils.log("Request reload of servers")
            send_command("steelsquid-event reload server")
        elif answer == "4" or answer == "S" or answer == "s":
            steelsquid_utils.log("Request service restart")
            send_command("steelsquid restart")
        elif answer == "5" or answer == "K" or answer == "k":
            steelsquid_utils.log("Request roboot")
            send_command("systemctl stop steelsquid")
        elif answer == "6" or answer == "R" or answer == "r":
            steelsquid_utils.log("Request roboot")
            send_command("reboot &")
    try:
        sftp.close()
    except:
        pass
    try:
        ssh.close()
    except:
        pass
    steelsquid_utils.log("By :-)")
    
