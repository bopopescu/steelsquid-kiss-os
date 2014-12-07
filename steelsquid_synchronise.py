#!/usr/bin/python -OO


'''
Automatic listen for changes abd commit changes to a nother system via ssh (install on remote system)

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
import os
import steelsquid_utils
import paramiko

steel_last = 0
base_remote_server=""
base_remote_port=""
base_remote_user=""
base_remote_password=""
python_files = []
web_files = []
img_files = []
extra_files = []
ssh = None
sftp = None


def load_data():
    '''
    '''
    global base_remote_server
    global base_remote_port
    global base_remote_user
    global base_remote_password
    global python_files
    global web_files
    global img_files
    global extra_files
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
            elif line.startswith("web_img_downloads["):
                line = line.split("=")[1]
                line = line.replace("$base/","")
                line = line.replace("\"","")
                img_files.append([line, 0])
    if os.path.isfile("config.txt"):
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

def transmit(local, remote):
    try:
        global ssh
        global sftp
        if ssh == None:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(base_remote_server, port=int(base_remote_port), username=base_remote_user, password=base_remote_password)
            sftp = ssh.open_sftp()
        try:
            sftp.put(local, remote)
        except:
            try:
                sftp.close()
            except:
                pass
            try:
                ssh.close()
            except:
                pass
            ssh.connect(base_remote_server, port=int(base_remote_port), username=base_remote_user, password=base_remote_password)
            sftp = ssh.open_sftp()
            sftp.put(local, remote)            
        steelsquid_utils.log("SYNC: " + local)
    except Exception, e:
        steelsquid_utils.log("Connection ERROR: " + str(e))
        
                    

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
        #for o in python_files:
        #    file_name = o[0]
        #    file_last = o[1]
        #    file_change = os.path.getmtime(file_name)
        #    if file_change != file_last:
        #        o[1] = file_change
                
        time.sleep(0.5)
        
    


if __name__ == '__main__':
    print ""
    print "Listen for changes and commit to: " + base_remote_server
    print " - Ttype q and press Enter this program will terminte."
    print " - Only press Enter the target machine steelsquid service will be restarted"
    print ""
    load_data()
    thread.start_new_thread(listener, ()) 
    answer = ""
    while answer != "q":
        answer = raw_input()
    try:
        sftp.close()
    except:
        pass
    try:
        ssh.close()
    except:
        pass
    steelsquid_utils.log("By :-)")
    
