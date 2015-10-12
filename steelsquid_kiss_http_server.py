#!/usr/bin/python -OO


'''
Use this to implement HTTP stuff, will execute on boot
Do not execute long running stuff or the system won't start properly.
This will always execute with root privilege.
The web-server will be started by steelsquid_boot.py

Use this to expand the capabilities of the webserver.
Handle stuff in index.html
-Administartot
-Download manager
-Mediaplayer
-Filemanager

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import subprocess
from subprocess import Popen, PIPE, STDOUT
import steelsquid_http_server
import threading
import thread
import steelsquid_utils
import os
import time
import pwd
import grp
import xmlrpclib
import steelsquid_boot
import steelsquid_kiss_global
from pprint import pprint


DOWNLOAD_RPC = "http://localhost:6800/rpc"
DOWNLOAD_LIST =['gid', 'totalLength', 'completedLength', 'downloadSpeed', 'uploadSpeed', 'files', 'status']
ALLOWED = ['/media/', '/mnt/', '/root/']


class SteelsquidKissHttpServer(steelsquid_http_server.SteelsquidHttpServer):


    def __init__(self, port, root, authorization, only_localhost, local_web_password, use_https):
        super(SteelsquidKissHttpServer, self).__init__(port, root, authorization, only_localhost, local_web_password, use_https)
        self.root_dir = "/root"
    
    def is_localhost(self, session_id, parameters):
        '''
        Is the client localhost
        '''
        if self.client_ip == "127.0.0.1":
            return [True, steelsquid_utils.get_parameter("font").rstrip('\n')]
        else:
            return [False, steelsquid_utils.get_parameter("font").rstrip('\n')]

    def wifi_status(self, session_id, parameters):
        '''
        Where are you connected
        '''
        answer = steelsquid_utils.execute_system_command(['net', 'system-status'])
        if answer[0] == 'None':
            return ["Not connected!", "---", "---", "---"]
        else:
            ip_wired = steelsquid_utils.network_ip_wired()
            ip_wifi = steelsquid_utils.network_ip_wifi()
            wan_ipp = steelsquid_utils.network_ip_wan()
            return [answer[0], ip_wired, ip_wifi, wan_ipp]
        
    def wifi_list(self, session_id, parameters):
        '''
        List of available wifi points
        '''
        import steelsquid_nm
        acc_p_list = steelsquid_nm.get_access_points(False)
        answer = []
        for acc_p in acc_p_list:
            answer.append(acc_p[1])
            if acc_p[3] == steelsquid_nm.WIRELESS_CAPABILITIES_NONE:
                answer.append("Open")
            else:
                answer.append(acc_p[3])
        return answer

    def wifi_connect(self, session_id, parameters):
        '''
        Connect wifi points
        '''
        import steelsquid_nm
        if parameters[1] == "Open":
            steelsquid_utils.execute_system_command(['net', 'system-connect', parameters[0]])
        elif parameters[1] == steelsquid_nm.WIRELESS_CAPABILITIES_WEP:
            steelsquid_utils.execute_system_command(['net', 'system-connect', parameters[0], parameters[2]])
        elif parameters[1] == steelsquid_nm.WIRELESS_CAPABILITIES_WPA:
            steelsquid_utils.execute_system_command(['net', 'system-connect', parameters[0], parameters[2]])
        else:
            raise Exception("Unknown WIFI type: " + parameters[1])
            
    def sshfs_add(self, session_id, parameters):
        '''
        Add sshfs mount
        '''
        if len(parameters[0]) == 0:
            raise Exception("Please enter IP or hostname")
        elif len(parameters[1]) == 0:
            raise Exception("Please enter Port number")
        elif len(parameters[2]) == 0:
            raise Exception("Please enter Username")
        elif len(parameters[4]) == 0:
            raise Exception("Please enter Local directory")
        elif len(parameters[5]) == 0:
            raise Exception("Please enter SSH-server directory")
        else:
            ip = parameters[0]
            port = parameters[1]
            user = parameters[2]
            password = parameters[3]
            local = "/mnt/network/" + parameters[4]
            remote = parameters[5]
            
            homedfolder = "/root/"+parameters[4]
            if os.path.isdir(local) and os.listdir(local) != []:
                raise Exception(local + " is not empty!")
            elif os.path.isdir(local) and steelsquid_utils.is_mounted(local):
                raise Exception(local + " is already mounted!")
            elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
                raise Exception(homedfolder + " is not empty!")
            elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
                raise Exception(homedfolder + " is already mounted!")
            steelsquid_utils.deleteFileOrFolder(homedfolder)
            steelsquid_utils.deleteFileOrFolder(local)
            os.makedirs(local)
            os.symlink(local, homedfolder)
            
            mount_filename = "/root/Mount-" + local.split('/')[-1] + ".sh"
            mount_cmd = "#!/bin/bash\numount %s\nsleep 0.3\numount -f %s\nsleep 0.3\numount -f -l %s\nsleep 0.3\nsshfs -o allow_other,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no -p %s %s@%s:%s %s" % (local, local, local, port, user, ip, remote, local)
            umount_filename = "/root/Umount-" + local.split('/')[-1] + ".sh"
            umount_cmd = "#!/bin/bash\numount %s\nsleep 0.3\numount -f %s\nsleep 0.3\numount -f -l %s" % (local, local, local)
            steelsquid_utils.write_to_file(mount_filename, mount_cmd)
            steelsquid_utils.write_to_file(umount_filename, umount_cmd)
            os.system("chmod +x " + mount_filename)
            os.system("chmod +x " + umount_filename)
            row = ip + "|" + port + "|" + user + "|" + password + "|" + local + "|" + remote
            steelsquid_utils.add_to_list("sshfs", row)
            return "Mount added"

    def sshfs_del(self, session_id, parameters):
        '''
        Del sshfs mount
        '''
        number = parameters[0]
        steelsquid_utils.del_from_list("sshfs", int(number))
        return "Mount deleted"

    def sshfs_get(self, session_id, parameters):
        '''
        Get sshfs mount
        '''
        answer = []
        mount_list = steelsquid_utils.get_list("sshfs")
        count = 0
        for row in mount_list:
            row = row.split("|")
            ip = row[0]
            port = row[1]
            user = row[2]
            password = row[3]
            local = row[4]
            remote = row[5]                        
            answer.append(count)
            answer.append(ip)
            answer.append(port)
            answer.append(user)
            answer.append(local)
            answer.append(remote)
            answer.append(steelsquid_utils.is_mounted(local))
            if len(password) > 0:
                answer.append("True")
            else:
                answer.append("False")
            count = count + 1
        return answer

    def sshfs_mount(self, session_id, parameters):
        '''
        Connect to sshfs
        '''
        self.lock_command('sshfs_mount')
        row = steelsquid_utils.get_from_list("sshfs", int(parameters[0]))
        row = row.split("|")
        ip = row[0]
        port = row[1]
        user = row[2]
        password = row[3]
        local = row[4]
        remote = row[5]
        if len(password)==0:
            password = parameters[1]
        try:
            os.makedirs(local)
        except:
            pass
        try:
            homedfolder = "/root/"+local
            os.symlink(local, homedfolder)
        except:
            pass
        steelsquid_utils.mount_sshfs(ip, port, user, password, remote, local)
        return "Drive mounted."

    def sshfs_umount(self, session_id, parameters):
        '''
        Disconnect from sshfs
        '''
        row = steelsquid_utils.get_from_list("sshfs", int(parameters[0]))
        row = row.split("|")
        ip = row[0]
        local = row[4]
        remote = row[5]
        steelsquid_utils.umount(local, "ssh", ip, remote)
        return "Drive unmounted."


    def sshfs_local_get(self, session_id, parameters):
        '''
        Get directoris in home folder
        '''
        answer = []
        mount_list_smb = steelsquid_utils.get_list("samba")
        mount_list_sshfs = steelsquid_utils.get_list("sshfs")
        home = "/mnt/network/"
        lst = os.listdir(home)
        lst.sort()
        for d in lst:
            homed = home+d
            if os.path.isdir(homed) and not d.startswith('.') and os.listdir(homed) == [] and not steelsquid_utils.is_mounted(homed) and not d == "Media":
                add_it = True
                for row in mount_list_sshfs:
                    row = row.split("|")
                    local = row[4]
                    if local == homed:
                        add_it = False
                for row in mount_list_smb:
                    row = row.split("|")
                    local = row[3]
                    if local == homed:
                        add_it = False
                if add_it:
                    homedfolder = "/root/"+d
                    if os.path.isdir(homedfolder) and os.listdir(homedfolder) == [] and not steelsquid_utils.is_mounted(homedfolder):
                        answer.append(d)
                    elif os.path.isfile(homedfolder):
                        answer.append(d)
                    elif not os.path.isdir(homedfolder):
                        answer.append(d)
        return answer

    def sshfs_local_add(self, session_id, parameters):
        '''
        Add directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/root/"+parameters[0]
        if os.path.isdir(the_dir) and os.listdir(the_dir) != []:
            raise Exception(the_dir + " is not empty!")
        elif os.path.isdir(the_dir) and steelsquid_utils.is_mounted(the_dir):
            raise Exception(the_dir + " is already mounted!")
        elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
            raise Exception(homedfolder + " is not empty!")
        elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
            raise Exception(homedfolder + " is already mounted!")
        elif os.path.isdir(the_dir):
            steelsquid_utils.deleteFileOrFolder(homedfolder)
            os.symlink(the_dir, homedfolder)
            raise Exception(parameters[0] + " already a mount point!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        os.makedirs(the_dir)
        os.symlink(the_dir, homedfolder)
        return "Local mount point created"

    def sshfs_local_del(self, session_id, parameters):
        '''
        Remove directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/root/"+parameters[0]
        if os.path.isdir(the_dir) and os.listdir(the_dir) != []:
            raise Exception(the_dir + " is not empty!")
        elif os.path.isdir(the_dir) and steelsquid_utils.is_mounted(the_dir):
            raise Exception(the_dir + " is already mounted!")
        elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
            raise Exception(homedfolder + " is not empty!")
        elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
            raise Exception(homedfolder + " is already mounted!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        return "Local mount point removed"

    def samba_add(self, session_id, parameters):
        '''
        Add samba mount
        '''
        if len(parameters[0]) == 0:
            raise Exception("Please enter IP or hostname")
        elif len(parameters[3]) == 0:
            raise Exception("Please enter Local directory")
        elif len(parameters[4]) == 0:
            raise Exception("Please enter share name")
        else:
            ip = parameters[0]
            user = parameters[1]
            password = parameters[2]
            local = "/mnt/network/" + parameters[3]
            remote = parameters[4]
            
            homedfolder = "/root/"+parameters[3]
            if os.path.isdir(local) and os.listdir(local) != []:
                raise Exception(local + " is not empty!")
            elif os.path.isdir(local) and steelsquid_utils.is_mounted(local):
                raise Exception(local + " is already mounted!")
            elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
                raise Exception(homedfolder + " is not empty!")
            elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
                raise Exception(homedfolder + " is already mounted!")
            steelsquid_utils.deleteFileOrFolder(homedfolder)
            steelsquid_utils.deleteFileOrFolder(local)
            os.makedirs(local)
            os.symlink(local, homedfolder)

            mount_filename = "/root/Mount-" + local.split('/')[-1] + ".sh"
            mount_cmd = "#!/bin/bash\numount %s\nsleep 0.3\numount -f %s\nsleep 0.3\numount -f -l %s\nsleep 0.3\nsshfs -o allow_other,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no -p %s %s@%s:%s" % (local, local, local, user, ip, remote, local)
            umount_filename = "/root/Umount-" + local.split('/')[-1] + ".sh"
            umount_cmd = "#!/bin/bash\numount %s\nsleep 0.3\numount -f %s\nsleep 0.3\numount -f -l %s" % (local, local, local)
            steelsquid_utils.write_to_file(mount_filename, mount_cmd)
            steelsquid_utils.write_to_file(umount_filename, umount_cmd)
            os.system("chmod +x " + mount_filename)
            os.system("chmod +x " + umount_filename)
            row = ip + "|" + user + "|" + password + "|" + local + "|" + remote
            steelsquid_utils.add_to_list("samba", row)
            return "Mount added"

    def samba_mount(self, session_id, parameters):
        '''
        Connect to samba
        '''
        self.lock_command('samba_mount')
        row = steelsquid_utils.get_from_list("samba", int(parameters[0]))
        row = row.split("|")
        ip = row[0]
        user = row[1]
        password = row[2]
        local = row[3]
        remote = row[4]
        try:
            os.makedirs(local)
        except:
            pass
        try:
            homedfolder = "/root/"+local
            os.symlink(local, homedfolder)
        except:
            pass
        steelsquid_utils.mount_samba(ip, user, password, remote, local)
        return "Drive mounted."

    def samba_del(self, session_id, parameters):
        '''
        Del samba mount
        '''
        number = parameters[0]
        steelsquid_utils.del_from_list("samba", int(number))
        return "Mount deleted"

    def samba_get(self, session_id, parameters):
        '''
        Del samba mount
        '''
        answer = []
        mount_list = steelsquid_utils.get_list("samba")
        count = 0
        for row in mount_list:
            row = row.split("|")
            ip = row[0]
            user = row[1]
            password = row[2]
            local = row[3]
            remote = row[4]
            answer.append(count)
            answer.append(ip)
            answer.append(user)
            answer.append(local)
            answer.append(remote)
            answer.append(steelsquid_utils.is_mounted(local))
            count = count + 1
        return answer

    def samba_umount(self, session_id, parameters):
        '''
        Disconnect from samba
        '''
        row = steelsquid_utils.get_from_list("samba", int(parameters[0]))
        row = row.split("|")
        ip = row[0]
        local = row[3]
        remote = row[4]
        steelsquid_utils.umount(local, "samba", ip, remote)
        return "Drive unmounted."

    def samba_list(self, session_id, parameters):
        '''
        List all shares from samba server
        '''
        ip = parameters[0]
        user = parameters[1]
        password = parameters[2]
        if len(ip)==0:
            raise Exception("Please enter IP or hostname")
        answer = steelsquid_utils.list_samba(ip, user, password)
        if len(answer)==0:
            raise Exception("No shares found on the server")
        return answer

    def samba_local_get(self, session_id, parameters):
        '''
        Get directoris in home folder
        '''
        answer = []
        mount_list_smb = steelsquid_utils.get_list("samba")
        mount_list_sshfs = steelsquid_utils.get_list("sshfs")
        home = "/mnt/network/"
        lst = os.listdir(home)
        lst.sort()
        for d in lst:
            homed = home+d
            if os.path.isdir(homed) and not d.startswith('.') and os.listdir(homed) == [] and not steelsquid_utils.is_mounted(homed) and not d == "Media":
                add_it = True
                for row in mount_list_sshfs:
                    row = row.split("|")
                    local = row[4]
                    if local == homed:
                        add_it = False
                for row in mount_list_smb:
                    row = row.split("|")
                    local = row[3]
                    if local == homed:
                        add_it = False
                if add_it:
                    homedfolder = "/root/"+d
                    if os.path.isdir(homedfolder) and os.listdir(homedfolder) == [] and not steelsquid_utils.is_mounted(homedfolder):
                        answer.append(d)
                    elif os.path.isfile(homedfolder):
                        answer.append(d)
                    elif not os.path.isdir(homedfolder):
                        answer.append(d)
        return answer

    def samba_local_add(self, session_id, parameters):
        '''
        Add directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/root/"+parameters[0]
        if os.path.isdir(the_dir) and os.listdir(the_dir) != []:
            raise Exception(the_dir + " is not empty!")
        elif os.path.isdir(the_dir) and steelsquid_utils.is_mounted(the_dir):
            raise Exception(the_dir + " is already mounted!")
        elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
            raise Exception(homedfolder + " is not empty!")
        elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
            raise Exception(homedfolder + " is already mounted!")
        elif os.path.isdir(the_dir):
            steelsquid_utils.deleteFileOrFolder(homedfolder)
            os.symlink(the_dir, homedfolder)
            raise Exception(parameters[0] + " already a mount point!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        os.makedirs(the_dir)
        os.symlink(the_dir, homedfolder)
        return "Local mount point created"

    def samba_local_del(self, session_id, parameters):
        '''
        Remove directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/root/"+parameters[0]
        if os.path.isdir(the_dir) and os.listdir(the_dir) != []:
            raise Exception(the_dir + " is not empty!")
        elif os.path.isdir(the_dir) and steelsquid_utils.is_mounted(the_dir):
            raise Exception(the_dir + " is already mounted!")
        elif os.path.isdir(homedfolder) and os.listdir(homedfolder) != []:
            raise Exception(homedfolder + " is not empty!")
        elif os.path.isdir(homedfolder) and steelsquid_utils.is_mounted(homedfolder):
            raise Exception(homedfolder + " is already mounted!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        return "Local mount point removed"

    def hostname_get(self, session_id, parameters):
        '''
        Set and get keyboard
        '''
        return steelsquid_utils.execute_system_command(['hostname'])

    def hostname_set(self, session_id, parameters):
        '''
        Set and get keyboard
        '''
        if not steelsquid_utils.is_valid_hostname(parameters[0]):
            raise Exception("Not a valide hostname!") 
        steelsquid_utils.execute_system_command(['steelsquid', 'hostname', parameters[0]])
        return "Hostname changed"
        
    def download(self, session_id, parameters):
        '''
        Download
        '''
        if len(parameters)==1:
            if parameters[0]=="True":
                steelsquid_utils.set_flag("download")
                steelsquid_utils.execute_system_command(['steelsquid', 'download-on'])
            elif parameters[0]=="False":
                steelsquid_utils.del_flag("download")
                steelsquid_utils.execute_system_command(['steelsquid', 'download-off'])
            else:
                if steelsquid_utils.is_file_ok(parameters[0], ALLOWED, check_if_exist=False):
                    steelsquid_utils.set_parameter("download_dir", parameters[0])
                    steelsquid_utils.execute_system_command(['steelsquid', 'download-dir', parameters[0]])
                    steelsquid_utils.execute_system_command(['steelsquid', 'download-on'])
                else:
                    raise Exception("Download directory must be inside /root/, /mnt/ or /media/") 
        par = steelsquid_utils.get_parameter("download_dir")
        if len(par)==0:
            par = "/root/Downloads"
            steelsquid_utils.set_parameter("download_dir", par)
        return [steelsquid_utils.get_flag("download"), par]
        
    def tz_get(self, session_id, parameters):
        '''
        Get the curren timezone
        '''
        f = os.popen("date")
        date = f.read()
        return [steelsquid_utils.read_from_file("/etc/timezone"), date]

    def tz_set(self, session_id, parameters):
        '''
        Set the curren timezone
        '''
        steelsquid_utils.execute_system_command(['steelsquid', 'timezone-set', parameters[0]])

    def tz_list(self, session_id, parameters):
        '''
        Get the curren timezone
        '''
        zones = []
        base = "/usr/share/zoneinfo/"
        for dir in os.listdir(base):
            if os.path.isdir(os.path.join(base, dir)):
                zones.append(dir)
        zones = sorted(zones)
        tz = []
        for zone in zones:
            basezones = base+zone
            towns = []
            for basezone in os.listdir(basezones):
                if os.path.isfile(os.path.join(basezones, basezone)):
                    towns.append(basezone)
            towns = sorted(towns)
            for town in towns:
                tz.append(zone + "/" + town)
        return tz

    def keyboard_get(self, session_id, parameters):
        '''
        Get keyboard
        '''
        return steelsquid_utils.get_parameter("keyboard")

    def keyboard_set(self, session_id, parameters):
        '''
        Set and get keyboard
        '''
        if len(parameters) > 0:
            steelsquid_utils.execute_system_command(['steelsquid', 'keyboard', parameters[0]])
            steelsquid_utils.set_parameter("keyboard", parameters[0])
        return steelsquid_utils.get_parameter("keyboard")

    def keyboard_list(self, session_id, parameters):
        '''
        Set and get keyboard
        '''
        answer = []
        answer.append("ar")
        answer.append("bg-cp1251")
        answer.append("bg")
        answer.append("br-abnt2")
        answer.append("br-latin1")
        answer.append("by")
        answer.append("ca-multi")
        answer.append("cf")
        answer.append("cz-lat2-prog")
        answer.append("cz-lat2")
        answer.append("cz-us-qwerty")
        answer.append("defkeymap")
        answer.append("defkeymap_V1.0")
        answer.append("dk-latin1")
        answer.append("dk")
        answer.append("emacs")
        answer.append("emacs2")
        answer.append("es-cp850")
        answer.append("es")
        answer.append("et-nodeadkeys")
        answer.append("et")
        answer.append("fa")
        answer.append("fi-latin1")
        answer.append("fi")
        answer.append("gr-pc")
        answer.append("gr-utf8")
        answer.append("gr")
        answer.append("hebrew")
        answer.append("hu101")
        answer.append("il-heb")
        answer.append("il-phonetic")
        answer.append("il")
        answer.append("is-latin1-us")
        answer.append("is-latin1")
        answer.append("it-ibm")
        answer.append("it")
        answer.append("it2")
        answer.append("jp106")
        answer.append("kg")
        answer.append("kk")
        answer.append("la-latin1")
        answer.append("lisp-us")
        answer.append("lk201-us")
        answer.append("lt")
        answer.append("lt.l4")
        answer.append("lv-latin4")
        answer.append("lv-latin7")
        answer.append("mac-usb-dk-latin1")
        answer.append("mac-usb-es")
        answer.append("mac-usb-euro")
        answer.append("mac-usb-fi-latin1")
        answer.append("mac-usb-se")
        answer.append("mac-usb-uk")
        answer.append("mac-usb-us")
        answer.append("mk")
        answer.append("nl")
        answer.append("no-latin1")
        answer.append("no-standard")
        answer.append("no")
        answer.append("pc110")
        answer.append("pl")
        answer.append("pl1")
        answer.append("pt-latin1")
        answer.append("pt-old")
        answer.append("ro-academic")
        answer.append("ro-comma")
        answer.append("ro")
        answer.append("ru-cp1251")
        answer.append("ru-ms")
        answer.append("ru-yawerty")
        answer.append("ru")
        answer.append("ru1")
        answer.append("ru2")
        answer.append("ru3")
        answer.append("ru4")
        answer.append("ru_win")
        answer.append("se-fi-ir209")
        answer.append("se-fi-lat6")
        answer.append("se-ir209")
        answer.append("se-lat6")
        answer.append("se-latin1")
        answer.append("sk-prog-qwerty")
        answer.append("sk-prog")
        answer.append("sk-qwerty")
        answer.append("sr-cy")
        answer.append("th-tis")
        answer.append("tr_q-latin5")
        answer.append("tralt")
        answer.append("trq")
        answer.append("trqu")
        answer.append("ua-utf-ws")
        answer.append("ua-utf")
        answer.append("ua-ws")
        answer.append("ua")
        answer.append("uaw")
        answer.append("uaw_uni")
        answer.append("uk")
        answer.append("us-intl.iso01")
        answer.append("us-intl.iso15")
        answer.append("us-latin1")
        answer.append("us")
        return answer


    def password(self, session_id, parameters):
        '''
        Change password
        '''
        if parameters[0] != parameters[1]:
            raise Exception("Password does not match the confirm password")
        elif not steelsquid_utils.authenticate("root", parameters[2]):
            raise Exception("You entered wrong current password")
        else:
            proc=Popen(['passwd', 'root'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            proc.stdin.write(parameters[0] + '\n')
            proc.stdin.write(parameters[0])  
            proc.stdin.flush()  
            stdout, stderr = proc.communicate()  
            if proc.returncode == 0:
                steelsquid_utils.clear_authenticate_cache()
                return "Password changed"
            elif "new password is too simple" in stderr:
                raise Exception("New password is too simple")
            elif "You must choose a longer password" in stderr:
                raise Exception("You must choose a longer password")
            elif "new password cannot be a palindrome" in stderr:
                raise Exception("Password cannot be a palindrome")
            else:
                raise Exception("Wrong password")


    def ssh_dis(self, session_id, parameters):
        '''
        Enable or disable ssh server
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'ssh-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("ssh")
            else:
                proc=Popen(['steelsquid', 'ssh-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("ssh")
        return not steelsquid_utils.get_flag("ssh")

    def web_interface_disable(self, session_id, parameters):
        '''
        Get or set if the webinterface is disabled
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'web-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("web")
            else:
                proc=Popen(['steelsquid', 'web-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("web")
        return not steelsquid_utils.get_flag("web")

    def web_interface_share(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /root
        '''
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_share_on(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /root
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.set_flag("web_interface_share")
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_share_off(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /root
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.del_flag("web_interface_share")
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_localhost(self, session_id, parameters):
        '''
        Localhost
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'web-local-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("web_local")
            else:
                proc=Popen(['steelsquid', 'web-local-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("web_local")
        return steelsquid_utils.get_flag("local_web")

    def web_interface_https(self, session_id, parameters):
        '''
        http
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'web-https'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("use_https")
            else:
                proc=Popen(['steelsquid', 'web-http'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("use_https")
        return [steelsquid_utils.get_flag("use_https")]

    def web_interface_authentication(self, session_id, parameters):
        '''
        http
        '''
        return [steelsquid_utils.get_flag("web_authentication")]

    def web_interface_authentication_on(self, session_id, parameters):
        '''
        http
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            proc=Popen(['steelsquid', 'web-aut-on'], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
            steelsquid_utils.set_flag("web_authentication")
            return [steelsquid_utils.get_flag("web_authentication")]

    def web_interface_authentication_off(self, session_id, parameters):
        '''
        http
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            proc=Popen(['steelsquid', 'web-aut-off'], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
            steelsquid_utils.del_flag("web_authentication")
            return [steelsquid_utils.get_flag("web_authentication")]

    def shutdown(self, session_id, parameters):
        '''
        Shutdown the computer
        '''
        if steelsquid_utils.get_flag("io"):
            import steelsquid_io
            steelsquid_io.power_off()
        else:
            os.system('shutdown -h now')
        return "System shutting down"

    def reboot(self, session_id, parameters):
        '''
        Reboot the computer
        '''
        os.system('reboot')
        return "System reboots"

    def system_info(self, session_id, parameters):
        '''
        Return system info
        '''
        return steelsquid_utils.system_info_array()

    def upgrade(self, session_id, parameters):
        '''
        Upgrade the system
        '''
        if not steelsquid_utils.has_internet_connection():
            raise Exception("You must be connected to the internet to make an upgrade!")
        self.lock_command('upgrade')
        if parameters[0] == 'small':
            self.execute_system_command(['steelsquid', 'update'], "upgrade")
            self.execute_system_command(['steelsquid', 'update-web'], "upgrade")
            self.execute_system_command(['steelsquid', 'update-python'], "upgrade")
        elif parameters[0] == 'full':
            self.execute_system_command(['steelsquid', 'upgrade'], "upgrade")

    def monitor_disable(self, session_id, parameters):
        '''
        Enable or disable monitor
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'display-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("disable_monitor")
            else:
                proc=Popen(['steelsquid', 'display-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("disable_monitor")
        return steelsquid_utils.get_flag("disable_monitor")

    def camera(self, session_id, parameters):
        '''
        Enable or disable camera
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['steelsquid', 'camera-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.set_flag("camera")
            else:
                proc=Popen(['steelsquid', 'camera-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
                steelsquid_utils.del_flag("camera")
        return steelsquid_utils.get_flag("camera")


    def lcd(self, session_id, parameters):
        '''
        Get the use of lcd to display ip
        '''
        if steelsquid_utils.get_flag("nokia"):
            return "nokia"
        if steelsquid_utils.get_flag("hdd"):
            return "hdd"
        if steelsquid_utils.get_flag("ssd"):
            return "ssd"
        if steelsquid_utils.get_flag("auto"):
            return "auto"
        else:
            return "False"

    def lcd_disable(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        proc=Popen(['steelsquid', 'lcd-off'], stdout = PIPE, stderr = STDOUT)  
        proc.wait()
        return self.lcd(session_id, parameters)

    def lcd_auto(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        proc=Popen(['steelsquid', 'lcd-auto'], stdout = PIPE, stderr = STDOUT)  
        proc.wait()
        return self.lcd(session_id, parameters)

    def lcd_hdd(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        proc=Popen(['steelsquid', 'lcd-hdd'], stdout = PIPE, stderr = STDOUT)  
        proc.wait()
        return self.lcd(session_id, parameters)

    def lcd_nokia(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        proc=Popen(['steelsquid', 'lcd-nokia'], stdout = PIPE, stderr = STDOUT)  
        proc.wait()
        return self.lcd(session_id, parameters)

    def lcd_ssd(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        proc=Popen(['steelsquid', 'lcd-ssd'], stdout = PIPE, stderr = STDOUT)  
        proc.wait()
        return self.lcd(session_id, parameters)

    def mail_set(self, session_id, parameters):
        '''
        Set mail configuration
        '''
        if parameters[0] == "":
            raise Exception("SMTP host is required!")
        if parameters[1] != "" and parameters[2] == "":
            raise Exception("Enter password!")
        if parameters[3] == "":
            raise Exception("Email is required!")
        steelsquid_utils.set_parameter("mail_host", parameters[0])
        steelsquid_utils.set_parameter("mail_username", parameters[1])
        steelsquid_utils.set_parameter("mail_password", parameters[2])
        steelsquid_utils.set_parameter("mail_mail", parameters[3])

    def mail_get(self, session_id, parameters):
        '''
        Get mail configuration
        '''
        answer = []
        answer.append(steelsquid_utils.get_parameter("mail_host"))
        answer.append(steelsquid_utils.get_parameter("mail_username"))
        answer.append(steelsquid_utils.get_parameter("mail_mail"))
        return answer

    def mail_test(self, session_id, parameters):
        '''
        Test the mail configuration
        '''
        if parameters[0] == "":
            raise Exception("SMTP host is required!")
        if parameters[1] != "" and parameters[2] == "":
            raise Exception("Enter password!")
        if parameters[3] == "":
            raise Exception("Email is required!")
        steelsquid_utils.set_parameter("mail_host", parameters[0])
        steelsquid_utils.set_parameter("mail_username", parameters[1])
        steelsquid_utils.set_parameter("mail_password", parameters[2])
        steelsquid_utils.set_parameter("mail_mail", parameters[3])
        mail_host = steelsquid_utils.get_parameter("mail_host")
        mail_username = steelsquid_utils.get_parameter("mail_username")
        mail_password = steelsquid_utils.get_parameter("mail_password")
        mail_mail = steelsquid_utils.get_parameter("mail_mail")
        steelsquid_utils.send_mail(mail_host, mail_username, mail_password, "do-not-reply@steelsquid.org", mail_mail, os.popen("hostname").read(), "Test notification!")

    def gpu_mem_get(self, session_id, parameters):
        '''
        Get gpu mem
        '''
        return steelsquid_utils.execute_system_command(['steelsquid', 'gpu-mem'])

    def gpu_mem_set(self, session_id, parameters):
        '''
        Set gpu mem
        '''
        value = parameters[0]
        if not value.isdigit():
            raise Exception("Min=16 and max=448")
        else:
            inte = int(value)
            if inte < 16 or inte > 448:
                raise Exception("Min=16 and max=448")
            else:
                steelsquid_utils.execute_system_command(['steelsquid', 'gpu-mem', str(inte)])
                return "Memory changed"

    def downman(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_utils.get_flag("download")
        


    def downman_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'download-on']) 
            steelsquid_utils.set_flag("download")
        return steelsquid_utils.get_flag("download")


    def downman_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'download-off']) 
            steelsquid_utils.del_flag("download")
        return steelsquid_utils.get_flag("download")

    def download_activate(self, session_id, parameters):
        '''
        Add a download link
        '''
        steelsquid_utils.set_flag("download")
        steelsquid_utils.execute_system_command(['steelsquid', 'download-on'])

    def download_active(self, session_id, parameters):
        '''
        Get all active downloads
        '''
        dow = steelsquid_utils.get_parameter("download_dir")
        answer = []
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        r = s.aria2.tellActive(DOWNLOAD_LIST)
        for row in r:
            answer.append(row['gid'])
            total_length = int(row['totalLength'])
            answer.append(str(int(total_length)/1048576) + " MiB")
            completed_length = int(row['completedLength'])
            if total_length==0:
                answer.append("0%")
            else:    
                answer.append(str(int((float(completed_length)/float(total_length))*100)) + "%")
            download_speed = int(row['downloadSpeed'])/1048576
            answer.append(str(download_speed) + " MiB/s")
            upload_speed = int(row['uploadSpeed'])/1048576
            answer.append(str(upload_speed) + " MiB/s")
            files = ""
            for fil in row['files']:
                files=fil['path']
                break
            files = files.strip(dow)
            answer.append(files)
        return answer

    def download_paused(self, session_id, parameters):
        '''
        Get all pause downloads
        '''
        dow = steelsquid_utils.get_parameter("download_dir")
        answer = []
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        r = s.aria2.tellWaiting(0, 1000, DOWNLOAD_LIST)
        for row in r:
            answer.append(row['gid'])
            answer.append(row['status'])
            total_length = int(row['totalLength'])
            answer.append(str(int(total_length)/1048576) + " MiB")
            completed_length = int(row['completedLength'])
            if total_length==0:
                answer.append("0%")
            else:    
                answer.append(str(int((float(completed_length)/float(total_length))*100)) + "%")
            files = ""
            for fil in row['files']:
                files=fil['path']
                break
            files = files.strip(dow)
            answer.append(files)
        return answer

    def download_stopped(self, session_id, parameters):
        '''
        Get all stopped/finsish downloads
        '''
        dow = steelsquid_utils.get_parameter("download_dir")
        answer = []
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        r = s.aria2.tellStopped(-1, 20, DOWNLOAD_LIST)
        for row in r:
            if row['status'] == 'complete' or row['status'] == 'error':
                answer.append(row['gid'])
                answer.append(row['status'])
                total_length = int(row['totalLength'])
                answer.append(str(int(total_length)/1048576) + " MiB")
                completed_length = int(row['completedLength'])
                answer.append(str((completed_length/total_length)*100) + "%")
                files = ""
                for fil in row['files']:
                    files=fil['path']
                    break
                files = files.strip(dow)
                answer.append(files)
        return answer
        
    def download_remove(self, session_id, parameters):
        '''
        Add a download link
        '''
        import xmlrpclib
        from pprint import pprint
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        s.aria2.forceRemove(parameters[0])

    def download_pause(self, session_id, parameters):
        '''
        pause download
        '''
        import xmlrpclib
        from pprint import pprint
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        s.aria2.pause(parameters[0])

    def download_resume(self, session_id, parameters):
        '''
        pause download
        '''
        import xmlrpclib
        from pprint import pprint
        s = xmlrpclib.ServerProxy(DOWNLOAD_RPC)
        s.aria2.unpause(parameters[0])

    def download_new(self, session_id, parameters):
        '''
        Add a download link
        '''
        import xmlrpclib
        from pprint import pprint
        s = xmlrpclib.ServerProxy('http://localhost:6800/rpc')
        r = s.aria2.addUri([parameters[0]])

    def download_directory(self, session_id, parameters):
        '''
        Get download directory
        '''
        return steelsquid_utils.get_parameter("download_dir")

    def media_list(self, session_id, parameters):
        '''
        List media
        '''
        answer = []
        is_root = True
        if len(parameters) == 0:
            the_dir = self.root_dir
            is_root = True
        else:
            the_dir = parameters[0]
            is_ok = steelsquid_utils.is_file_ok(the_dir, ALLOWED)
            if is_ok == False:
                the_dir = self.root_dir
                is_root = True
            elif the_dir == self.root_dir:
                the_dir = self.root_dir
                is_root = True
            else:
                is_root = False
        lst = os.listdir(the_dir)
        lst.sort()
        dirs = []
        files = []
        for f in lst:
            if not f.startswith("."):
                if os.path.isdir(the_dir + "/" + f):
                    dirs.append(f)
                elif steelsquid_utils.is_video_file(str(f)):
                    files.append(f)
        if not is_root:
            answer.append("<==")
            answer.append("BACK")
            answer.append(" ")
            answer.append(os.path.dirname(the_dir))
        for filename in dirs:
            answer.append("DIR")
            answer.append(filename)
            answer.append(" ")
            answer.append(the_dir + "/" + filename)
        for filename in files:
            answer.append(" ")
            answer.append(filename)
            answer.append(str(os.path.getsize(the_dir + "/" + filename) >> 20) + " MB" )
            answer.append(the_dir + "/" + filename)
        return answer


    def media_play(self, session_id, parameters):
        '''
        play_file
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        the_dir = parameters[0]
        if steelsquid_utils.is_file_ok(the_dir, ALLOWED):        
            steelsquid_omx.play(the_dir)
        else:
            raise Exception("Link not allowed!!!")


    def media_stop(self, session_id, parameters):
        '''
        media_stop
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.stop()


    def media_pause(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.pause_toggle()


    def media_backward_short(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.backward_short()


    def media_forward_short(self, session_id, parameters):
        '''
        play_file
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.forward_short()


    def media_backward_long(self, session_id, parameters):
        '''
        play_file
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.backward_long()


    def media_forward_long(self, session_id, parameters):
        '''
        play_file
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.forward_long()


    def media_audio_previous(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.audio_previous()


    def media_audio_next(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.audio_next()


    def media_sub_previous(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.sub_previous()


    def media_sub_next(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.sub_next()


    def media_sub_toggle(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.sub_toggle()


    def media_volume_decrease(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.volume_decrease()


    def media_volume_increase(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.volume_increase()


    def media_playlist(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        plist = steelsquid_omx.playlist_list()
        answer = []
        for p in plist:
            n = os.path.basename(p)
            answer.append(n)
            answer.append(p)
        return answer
        

    def media_playlist_clear(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.playlist_clear()
        return self.media_playlist(session_id, parameters);


    def media_playlist_add(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        the_dir = parameters[0]
        if steelsquid_utils.is_file_ok(the_dir, ALLOWED):        
            steelsquid_omx.playlist_add(the_dir)
            return self.media_playlist(session_id, parameters);
        else:
            raise Exception("Link not allowed!!!")


    def media_playlist_remove(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.playlist_remove(parameters[0])
        return self.media_playlist(session_id, parameters);


    def media_playlist_play(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        the_dir = parameters[0]
        if steelsquid_utils.is_file_ok(the_dir, ALLOWED):        
            steelsquid_omx.playlist_play(the_dir)
        else:
            raise Exception("Link not allowed!!!")


    def media_playlist_previous(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.playlist_previous()


    def media_playlist_next(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        steelsquid_omx.playlist_next()


    def media_playing(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        import steelsquid_omx
        name = steelsquid_omx.playing()
        if name == None:
            return "No video is playing!"
        else:
            return os.path.basename(name)

    def file_list(self, session_id, parameters):
        '''
        List files
        '''
        if not steelsquid_utils.get_flag("web_interface_share"):
            raise Exception("web_interface_share is not enabled!!!")
        answer = []
        is_root = True
        if len(parameters) == 0:
            the_dir = self.get_session_data(session_id, "file_location")
            if the_dir == None:
                the_dir = self.root_dir
                is_root = True
        else:
            the_dir = parameters[0]            
        is_ok = steelsquid_utils.is_file_ok(the_dir, ALLOWED)
        if is_ok == False:
            the_dir = self.root_dir
            is_root = True
        elif the_dir == self.root_dir:
            the_dir = self.root_dir
            is_root = True
        else:
            is_root = False
        self.set_session_data(session_id, "file_location", the_dir)
        lst = os.listdir(the_dir)
        lst.sort()
        dirs = []
        files = []
        for f in lst:
            if not f.startswith("."):
                if os.path.isdir(the_dir + "/" + f):
                    dirs.append(f)
                else:
                    files.append(f)
        if not is_root:
            answer.append("<==")
            answer.append("BACK")
            answer.append(" ")
            answer.append(os.path.dirname(the_dir))
        for filename in dirs:
            answer.append("DIR")
            answer.append(filename)
            answer.append(" ")
            answer.append(the_dir + "/" + filename)
        for filename in files:
            answer.append(" ")
            answer.append(filename)
            f_size = os.path.getsize(the_dir + "/" + filename) >> 30
            if f_size != 0:
                answer.append(str(f_size) + " GB" )
            else:
                f_size = os.path.getsize(the_dir + "/" + filename) >> 20
                if f_size != 0:
                    answer.append(str(f_size) + " MB" )
                else:
                    f_size = os.path.getsize(the_dir + "/" + filename) >> 10
                    if f_size != 0:
                        answer.append(str(f_size) + " kB" )
                    else:
                        f_size = os.path.getsize(the_dir + "/" + filename)
                        answer.append(str(f_size) + " B" )
            answer.append(the_dir + "/" + filename)
        return answer


    def file_upload(self, session_id, parameters):
        '''
        Upload file
        '''
        the_file = self.get_session_data(session_id, "file_location")
        filename = parameters[0]
        stream = parameters[1]
        if the_file == None:
            the_file = self.root_dir
        the_file = the_file + "/" + filename
        if steelsquid_utils.is_file_ok(the_file, ALLOWED, check_if_exist=False):
            if os.path.exists(the_file):
                raise Exception("The file already exists!")
            else:
                with open(the_file, 'w') as out:
                    d = stream.read(8192)
                    while d:
                        out.write(d)
                        d = stream.read(8192)       
        else:
            raise Exception("Directory not allowed: "+the_file)


    def file_mkdir(self, session_id, parameters):
        '''
        Upload file
        '''
        the_file = self.get_session_data(session_id, "file_location")
        if the_file == None:
            the_file = self.root_dir
        the_file = the_file + "/" + parameters[0]
        if steelsquid_utils.is_file_ok(the_file, ALLOWED, check_if_exist=False):
            if os.path.exists(the_file):
                raise Exception("The name is already in use")
            else:
                steelsquid_utils.make_dirs(the_file)
        else:
            raise Exception("Directory not allowed: "+the_file)

    def file_mkfile(self, session_id, parameters):
        '''
        New file
        '''
        the_file = self.get_session_data(session_id, "file_location")
        if the_file == None:
            the_file = self.root_dir
        the_file = the_file + "/" + parameters[0]
        if steelsquid_utils.is_file_ok(the_file, ALLOWED, check_if_exist=False):
            if os.path.exists(the_file):
                raise Exception("The name is already in use")
            else:
                steelsquid_utils.write_to_file(the_file, "")
        else:
            raise Exception("Not allowed")
            

    def file_del(self, session_id, parameters):
        '''
        Upload file
        '''
        for t_file in parameters:
            if steelsquid_utils.is_file_ok(t_file, ALLOWED, check_if_exist=False):
                steelsquid_utils.deleteFileOrFolder(t_file)
            else:
                raise Exception("Not allowed: "+t_file)
            

    def file_rename(self, session_id, parameters):
        '''
        file
        '''
        current_name = parameters[0]
        new_name = parameters[1]
        if steelsquid_utils.is_file_ok(current_name, ALLOWED, check_if_exist=True) and steelsquid_utils.is_file_ok(new_name, ALLOWED, check_if_exist=False):
            if os.path.exists(new_name):
                raise Exception("The name is already in use: "+new_name)
            else:
                os.rename(current_name, new_name)
        else:
            raise Exception("Not allowed")


    def file_copy(self, session_id, parameters):
        '''
        file
        '''
        for t_file in parameters:
            if not steelsquid_utils.is_file_ok(t_file, ALLOWED, check_if_exist=False):
                raise Exception("Not allowed: "+t_file)
        self.set_session_data(session_id, "file_paste", list(parameters))
        self.set_session_data(session_id, "file_copy_or_cut", "copy")
        return "File(s)/folder(s) copied"


    def file_cut(self, session_id, parameters):
        '''
        file
        '''
        for t_file in parameters:
            if not steelsquid_utils.is_file_ok(t_file, ALLOWED, check_if_exist=False):
                raise Exception("Not allowed: "+t_file)
        self.set_session_data(session_id, "file_paste", list(parameters))
        self.set_session_data(session_id, "file_copy_or_cut", "cut")
        return "File(s)/folder(s) cut"
        

    def file_paste(self, session_id, parameters):
        '''
        file
        '''
        the_dir = self.get_session_data(session_id, "file_location")
        file_paste = self.get_session_data(session_id, "file_paste")        
        file_copy_or_cut = self.get_session_data(session_id, "file_copy_or_cut")        
        if file_paste == None or file_copy_or_cut==None or the_dir==None:
            raise Exception("No file or folder to paste!")
        for t_file in file_paste:
            if file_copy_or_cut == "copy":
                steelsquid_utils.copyFileOrFolder(t_file, the_dir)
            else:
                steelsquid_utils.moveFileOrFolder(t_file, the_dir)
        self.del_session_data(session_id, "file_paste")
        self.del_session_data(session_id, "file_copy_or_cut")
             
    def io(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_utils.get_flag("io")
        


    def io_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'io-on']) 
        return steelsquid_utils.get_flag("io")


    def io_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'io-off']) 
        return steelsquid_utils.get_flag("io")
             

    def socket_info(self, session_id, parameters):
        '''
        
        '''
        if steelsquid_utils.get_flag("socket_server"):
            return ["server", "Socket connection as server enabled on port 22222", "Disabled"]
        elif steelsquid_utils.has_parameter("socket_client"):
            return ["client", "Disabled", "Socket connection as client enabled ("+steelsquid_utils.get_parameter("socket_client")+":22222)", steelsquid_utils.get_parameter("socket_client")]
        else:
            return ["disabled", "Disabled", "Disabled"]

    def socket_server(self, session_id, parameters):
        '''
        
        '''
        steelsquid_utils.execute_system_command(['steelsquid', 'socket-server']) 
        return "Socket connection as server enabled"


    def socket_client(self, session_id, parameters):
        '''
        
        '''
        if len(parameters[0])<2:
            raise Exception("Server adress can not be empty")
        steelsquid_utils.execute_system_command(['steelsquid', 'socket-client', parameters[0]]) 
        return "Socket connection as client enabled"


    def socket_disable(self, session_id, parameters):
        '''
        
        '''
        steelsquid_utils.execute_system_command(['steelsquid', 'socket-off']) 
        return "Socket connection disabled"
             

    def bluetooth_info(self, session_id, parameters):
        '''
        
        '''
        return [steelsquid_utils.get_flag("bluetooth_pairing"), steelsquid_utils.get_parameter("bluetooth_pin")]


    def bluetooth_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'bluetooth-on']) 
        return [steelsquid_utils.get_flag("bluetooth_pairing"), steelsquid_utils.get_parameter("bluetooth_pin")]


    def bluetooth_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate("root", parameters[0]):
            raise Exception("Incorrect password for user root!")
        else:
            steelsquid_utils.execute_system_command(['steelsquid', 'bluetooth-off']) 
        return [steelsquid_utils.get_flag("bluetooth_pairing"), steelsquid_utils.get_parameter("bluetooth_pin")]


    def bluetooth_pin(self, session_id, parameters):
        '''
        
        '''
        if not parameters[0].isdigit():
            raise Exception("PIN must be digits")
        steelsquid_utils.execute_system_command(['steelsquid', 'bluetooth-pin', parameters[0]]) 
        return [steelsquid_utils.get_parameter("bluetooth_pin")]             


    def web_port(self, session_id, parameters):
        '''
        Get and set web server port
        '''
        if len(parameters)>0:
            steelsquid_utils.execute_system_command(['steelsquid', 'web-port', parameters[0]]) 
        if not steelsquid_utils.has_parameter("web-port"):
            if steelsquid_utils.get_flag("web-https"):
                steelsquid_utils.set_parameter("web-port", "443")
            else:
                steelsquid_utils.set_parameter("web-port", "80")
        return steelsquid_utils.get_parameter("web-port")


    def stream_port(self, session_id, parameters):
        '''
        Get and set stream server port
        '''
        if len(parameters)>0:
            steelsquid_utils.execute_system_command(['steelsquid', 'stream-port', parameters[0]]) 
        if not steelsquid_utils.has_parameter("stream-port"):
            steelsquid_utils.set_parameter("stream-port", "8080")
        return steelsquid_utils.get_parameter("stream-port")


