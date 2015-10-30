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
import readline
from datetime import datetime

steel_last = 0
base_remote_server=[]
base_remote_port=""
base_remote_user=""
base_remote_password=""
python_files = []
web_files = []
extra_files = []
img_files = []

ssh = []
sftp = []
channel = []
channel_f = []
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
    global img_files
    global ssh
    global sftp
    global channel
    global channel_f 
    print ""
    steelsquid_utils.log("Load settings from steelsquid-kiss-os.sh")
    with open("steelsquid-kiss-os.sh") as f:
        for line in f:
            line = line.replace("\n","")
            if line.startswith("python_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                python_files.append([line, 0])
            elif line.startswith("web_root_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                web_files.append([line, 0])
            elif line.startswith("web_img_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                img_files.append([line, 0])
    if os.path.isfile("config.txt"):
        print ""
        steelsquid_utils.log("Load settings from config.txt")
        i = 0
        with open("config.txt") as f:
            for line in f:
                line = line.replace("\n","")
                if i == 0:
                    tmp = line.split(',')
                    for x in tmp:
                        base_remote_server.append(x.strip())
                    le = len(base_remote_server)
                    ssh = [None] * le
                    sftp = [None] * le
                    channel = [None] * le
                    channel_f = [None] * le
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
    else:
        steelsquid_utils.log("config.txt not found!!!")
        sys.exit()

        
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
        for o in img_files:
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
        global base_remote_server
        global ssh
        global channel
        global channel_f
        global sftp
        disconnect()
        x = 0
        for server in base_remote_server:
            try:
                print ""
                steelsquid_utils.log("Connecting to: " + server)
                ssh[x].connect(server, port=int(base_remote_port), username=base_remote_user, password=base_remote_password)
                channel[x] = ssh[x].get_transport().open_session()
                channel[x].get_pty()
                channel[x].invoke_shell()
                channel_f[x] = channel[x].makefile()
                sftp[x] = ssh[x].open_sftp()
                x = x + 1
            except Exception, e:
                steelsquid_utils.shout()
                raise e
            
            
def disconnect():
    global ssh
    global sftp
    for x in range(0, len(base_remote_server)):
        try:
            sftp[x].close()
        except:
            pass
        try:
            ssh[x].close()
        except:
            pass
    

def transmit(local, remote):
    print ""
    steelsquid_utils.log("SYNC: " + local)
    for x in range(0, len(base_remote_server)):
        try:
            sftp[x].put(local, remote)
        except:
            try:
                connect()
                sftp[x].put(local, remote)            
            except:
                pass
        

def send_command(command):
    '''
    '''
    for x in range(0, len(base_remote_server)):
        try:
            ssh[x].exec_command(command)
        except:
            try:
                connect()
                ssh[x].exec_command(command)
            except:
                pass


def send_command_read_answer(command):
    '''
    '''
    for x in range(0, len(base_remote_server)):
        try:
            stdin, stdout, stderr = ssh[x].exec_command(command)
            printempty = True
            for line in stdout.readlines():
                line = line.strip().replace("\n","").replace("\r","")
                if len(line)>0:
                    printempty = True
                    print line
                elif printempty:
                    printempty = False
                    print
            printempty = True
            for line in stderr.readlines():
                if len(line)>0:
                    printempty = True
                    print line
                elif printempty:
                    printempty = False
                    print
        except:
            try:
                connect()
                stdin, stdout, stderr = ssh[x].exec_command(command)
                for line in stdout.readlines():
                    line = line.strip().replace("\n","").replace("\r","")
                    if len(line)>0:
                        print line
                for line in stderr.readlines():
                    line = line.strip().replace("\n","").replace("\r","")
                    if len(line)>0:
                        print line
            except:
                pass


def listen_for_std(x):
    '''
    '''
    time.sleep(1)
    print ""
    steelsquid_utils.log("Listen for output from: " + base_remote_server[x])
    global channel_f
    while True:
        try:
            if not channel_f[x].closed:
                first = True
                last_time = 1000
                for line in channel_f[x]:
                    if first:
                        first = False
                    else:
                        line = line[:-1]
                        line = " ".join(line.split())
                        if len(line)>0:
                            cur_time = time.time() * 1000
                            ms = cur_time - last_time
                            answer = remove_timestamp(line)
                            if answer != None:
                                if ms > 100:
                                    print ""
                                    steelsquid_utils.log("FROM REMOTE DEVICE: " + base_remote_server[x])
                                print answer
                                last_time = cur_time
        except:
            steelsquid_utils.shout()
            try:
                connect()
            except:
                pass
        time.sleep(2)
        
            
def remove_timestamp(line): 
    if len(line)>18:
        if line[4]=='-' and line[7]=='-' and line[10]==' ' and line[13]==':' and line[16]==':':
            if len(line)>19:
                return line[20:]
            else:
                return None
    return line


def print_menu(): 
    print "------------------------------------------------------------------------------"
    print "Listen for changes and commit to following server(s)"
    print ', '.join(base_remote_server)
    print "------------------------------------------------------------------------------"
    print " H : help   : Show this help"
    print " Q : quit   : This program will terminate"
    print " C : custom : Reload the custom modules (/opt/steelsquid/python/expand/...)"
    print " E : expand : Reload steelsquid_kiss_expand.py"
    print " S : server : Reload ...uid_kiss_http_expand.py, ...uid_kiss_socket_expand.py"
    print " A : all    : Start/Restart steelsquid service (implememt all changes)"
    print " K : kill   : Stop steelsquid service"
    print " R : reboot : Reboot the remote machine"
    print "------------------------------------------------------------------------------"
    print "You can also send any other ordinary terminal line command (ls, mkdir...)"
    print "------------------------------------------------------------------------------"


if __name__ == '__main__':
    load_data()
    for x in range(0, len(base_remote_server)):
        ssh[x] = paramiko.SSHClient()
        ssh[x].set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh[x].set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        connect()
    except:
        pass
    for x in range(0, len(base_remote_server)):
        thread.start_new_thread(listen_for_std, (x,)) 
    print ""
    print_menu()
    thread.start_new_thread(listener, ()) 
    answer = ""
    cont = True
    while cont:
        answer = raw_input("\n# ")
        if answer == "H" or answer == "h" or answer == "help":
            print_menu()
        elif answer == "Q" or answer == "q" or answer == "quit":
            cont = False
        elif answer == "C" or answer == "c" or answer == "custom":
            steelsquid_utils.log("Request reload of custom modules")
            send_command("event reload custom")
        elif answer == "E" or answer == "e" or answer == "expand":
            steelsquid_utils.log("Request reload of steelsquid_kiss_expand.py")
            send_command("event reload expand")
        elif answer == "S" or answer == "s" or answer == "server":
            steelsquid_utils.log("Request reload of ...uid_kiss_http_expand.py, ...uid_kiss_socket_expand.py")
            send_command("event reload server")
        elif answer == "A" or answer == "a" or answer == "all":
            steelsquid_utils.log("Request service restart")
            send_command("steelsquid restart")
        elif answer == "K" or answer == "k" or answer == "kill":
            steelsquid_utils.log("Request roboot")
            send_command("systemctl stop steelsquid")
        elif answer == "R" or answer == "r" or answer == "reboot":
            steelsquid_utils.log("Request roboot")
            send_command("reboot &")
        elif len(answer.strip())>0:
            send_command_read_answer(answer)
    disconnect()
    steelsquid_utils.log("By :-)")
    
