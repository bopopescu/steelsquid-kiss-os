#!/usr/bin/python -OO


'''
Control/Configure steelsquid-kiss-os from web browser

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
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


USERNAME = "steelsquid"
DOWNLOAD_RPC = "http://localhost:6800/rpc"
DOWNLOAD_LIST =['gid', 'totalLength', 'completedLength', 'downloadSpeed', 'uploadSpeed', 'files', 'status']
ALLOWED = ['/media/', '/mnt/', '/home/steelsquid/']

class SteelsquidKissHttpServer(steelsquid_http_server.SteelsquidHttpServer):
    
    __slots__ = ['root_dir']

    def __init__(self, port, root, authorization, only_localhost, local_web_password, ban_ip_after_30_fail, use_https, drop_privilege=False):
        super(SteelsquidKissHttpServer, self).__init__(port, root, authorization, only_localhost, local_web_password, ban_ip_after_30_fail, use_https, drop_privilege)
        self.root_dir = "/home/" + USERNAME
    
    def is_localhost(self, session_id, parameters):
        '''
        Is the client localhost
        '''
        if self.client_ip == "127.0.0.1":
            return [True, steelsquid_utils.get_parameter("font").rstrip('\n')]
        else:
            return [False, steelsquid_utils.get_parameter("font").rstrip('\n')]

    def desktop(self, session_id, parameters):
        '''
        Is desktop installed
        '''
        return [steelsquid_utils.get_flag("desktop")]

    def wifi_status(self, session_id, parameters):
        '''
        Where are you connected
        '''
        answer = steelsquid_utils.execute_system_command(['sudo', 'steelsquid-nm', 'system-status'])
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
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid-nm', 'system-connect', parameters[0]])
        elif parameters[1] == steelsquid_nm.WIRELESS_CAPABILITIES_WEP:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid-nm', 'system-connect', parameters[0], parameters[2]])
        elif parameters[1] == steelsquid_nm.WIRELESS_CAPABILITIES_WPA:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid-nm', 'system-connect', parameters[0], parameters[2]])
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
            
            homedfolder = "/home/"+USERNAME+"/"+parameters[4]
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
            os.system("chown steelsquid:steelsquid " + homedfolder)
            
            mount_filename = "/home/"+USERNAME+"/Mount-" + local.split('/')[-1] + ".sh"
            mount_cmd = "#!/bin/bash\nsudo umount %s\nsleep 0.3\nsudo umount -f %s\nsleep 0.3\nsudo umount -f -l %s\nsleep 0.3\nsudo sshfs -o allow_other,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no -p %s %s@%s:%s %s" % (local, local, local, port, user, ip, remote, local)
            umount_filename = "/home/"+USERNAME+"/Umount-" + local.split('/')[-1] + ".sh"
            umount_cmd = "#!/bin/bash\nsudo umount %s\nsleep 0.3\nsudo umount -f %s\nsleep 0.3\nsudo umount -f -l %s" % (local, local, local)
            steelsquid_utils.write_to_file(mount_filename, mount_cmd)
            steelsquid_utils.write_to_file(umount_filename, umount_cmd)
            steelsquid_utils.set_permission(mount_filename)
            steelsquid_utils.set_permission(umount_filename)
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
            homedfolder = "/home/"+USERNAME+"/"+local
            os.symlink(local, homedfolder)
            os.system("chown steelsquid:steelsquid " + homedfolder)
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
                    homedfolder = "/home/"+USERNAME+"/"+d
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
        homedfolder = "/home/"+USERNAME+"/"+parameters[0]
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
            os.system("chown steelsquid:steelsquid " + homedfolder)
            raise Exception(parameters[0] + " already a mount point!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        os.makedirs(the_dir)
        os.symlink(the_dir, homedfolder)
        os.system("chown steelsquid:steelsquid " + homedfolder)
        return "Local mount point created"

    def sshfs_local_del(self, session_id, parameters):
        '''
        Remove directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/home/"+USERNAME+"/"+parameters[0]
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
            
            homedfolder = "/home/"+USERNAME+"/"+parameters[3]
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
            os.system("chown steelsquid:steelsquid " + homedfolder)

            mount_filename = "/home/"+USERNAME+"/Mount-" + local.split('/')[-1] + ".sh"
            mount_cmd = "#!/bin/bash\nsudo umount %s\nsleep 0.3\nsudo umount -f %s\nsleep 0.3\nsudo umount -f -l %s\nsleep 0.3\nsudo sshfs -o allow_other,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no -p %s %s@%s:%s" % (local, local, local, user, ip, remote, local)
            umount_filename = "/home/"+USERNAME+"/Umount-" + local.split('/')[-1] + ".sh"
            umount_cmd = "#!/bin/bash\nsudo umount %s\nsleep 0.3\nsudo umount -f %s\nsleep 0.3\nsudo umount -f -l %s" % (local, local, local)
            steelsquid_utils.write_to_file(mount_filename, mount_cmd)
            steelsquid_utils.write_to_file(umount_filename, umount_cmd)
            steelsquid_utils.set_permission(mount_filename)
            steelsquid_utils.set_permission(umount_filename)
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
            homedfolder = "/home/"+USERNAME+"/"+local
            os.symlink(local, homedfolder)
            os.system("chown steelsquid:steelsquid " + homedfolder)
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
                    homedfolder = "/home/"+USERNAME+"/"+d
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
        homedfolder = "/home/"+USERNAME+"/"+parameters[0]
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
            os.system("chown steelsquid:steelsquid " + homedfolder)
            raise Exception(parameters[0] + " already a mount point!")
        steelsquid_utils.deleteFileOrFolder(homedfolder)
        steelsquid_utils.deleteFileOrFolder(the_dir)
        os.makedirs(the_dir)
        os.symlink(the_dir, homedfolder)
        os.system("chown steelsquid:steelsquid " + homedfolder)
        return "Local mount point created"

    def samba_local_del(self, session_id, parameters):
        '''
        Remove directoris in home folder
        '''
        the_dir = steelsquid_utils.check_file_path("/mnt/network/" + parameters[0], "/mnt/network/", False)
        homedfolder = "/home/"+USERNAME+"/"+parameters[0]
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
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'hostname', parameters[0]])
        return "Hostname changed"
        
    def download(self, session_id, parameters):
        '''
        Download
        '''
        if len(parameters)==1:
            if parameters[0]=="True":
                steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-on'])
            elif parameters[0]=="False":
                steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-off'])
            else:
                if steelsquid_utils.is_file_ok(parameters[0], ALLOWED, check_if_exist=False):
                    steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-dir', parameters[0]])
                    steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-on'])
                else:
                    raise Exception("Download directory must be inside /home/steelsquid/, /mnt/ or /media/") 
        par = steelsquid_utils.get_parameter("download_dir")
        if len(par)==0:
            par = "/home/steelsquid/Downloads"
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
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'timezone-set', parameters[0]])

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
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'keyboard', parameters[0]])
        return steelsquid_utils.get_parameter("keyboard")

    def keyboard_list(self, session_id, parameters):
        '''
        Set and get keyboard
        '''
        answer = []
        answer.append("us")
        answer.append("English (US)")
        answer.append("ad")              
        answer.append("Catalan")
        answer.append("af")              
        answer.append("Afghani")
        answer.append("ara")             
        answer.append("Arabic")
        answer.append("al")              
        answer.append("Albanian")
        answer.append("am")              
        answer.append("Armenian")
        answer.append("at")              
        answer.append("German (Austria)")
        answer.append("az")              
        answer.append("Azerbaijani")
        answer.append("by")              
        answer.append("Belarusian")
        answer.append("be")              
        answer.append("Belgian")
        answer.append("bd")              
        answer.append("Bengali")
        answer.append("in")              
        answer.append("Indian")
        answer.append("ba")              
        answer.append("Bosnian")
        answer.append("br")              
        answer.append("Portuguese (Brazil)")
        answer.append("bg")              
        answer.append("Bulgarian")
        answer.append("ma")              
        answer.append("Arabic (Morocco)")
        answer.append("cm")              
        answer.append("English (Cameroon)")
        answer.append("mm")              
        answer.append("Burmese")
        answer.append("ca")              
        answer.append("French (Canada)")
        answer.append("cd")              
        answer.append("French (Democratic Republic of the Congo)")
        answer.append("cn")              
        answer.append("Chinese")
        answer.append("hr")              
        answer.append("Croatian")
        answer.append("cz")              
        answer.append("Czech")
        answer.append("dk")              
        answer.append("Danish")
        answer.append("nl")              
        answer.append("Dutch")
        answer.append("bt")              
        answer.append("Dzongkha")
        answer.append("ee")              
        answer.append("Estonian")
        answer.append("ir")              
        answer.append("Persian")
        answer.append("iq")              
        answer.append("Iraqi")
        answer.append("fo")              
        answer.append("Faroese")
        answer.append("fi")              
        answer.append("Finnish")
        answer.append("fr")             
        answer.append("French")
        answer.append("gh")             
        answer.append("English (Ghana)")
        answer.append("gn")              
        answer.append("French (Guinea)")
        answer.append("ge")              
        answer.append("Georgian")
        answer.append("de")              
        answer.append("German")
        answer.append("gr")              
        answer.append("Greek")
        answer.append("hu")              
        answer.append("Hungarian")
        answer.append("is")              
        answer.append("Icelandic")
        answer.append("il")              
        answer.append("Hebrew")
        answer.append("it")              
        answer.append("Italian")
        answer.append("jp")              
        answer.append("Japanese")
        answer.append("kg")              
        answer.append("Kyrgyz")
        answer.append("kh")              
        answer.append("Khmer (Cambodia)")
        answer.append("kz")              
        answer.append("Kazakh")
        answer.append("la")              
        answer.append("Lao")
        answer.append("latam")          
        answer.append("Spanish (Latin American)")
        answer.append("lt")              
        answer.append("Lithuanian")
        answer.append("lv")              
        answer.append("Latvian")
        answer.append("mao")             
        answer.append("Maori")
        answer.append("me")              
        answer.append("Montenegrin")
        answer.append("mk")             
        answer.append("Macedonian")
        answer.append("mt")              
        answer.append("Maltese")
        answer.append("mn")              
        answer.append("Mongolian")
        answer.append("no")              
        answer.append("Norwegian")
        answer.append("pl")              
        answer.append("Polish")
        answer.append("pt")              
        answer.append("Portuguese")
        answer.append("ro")              
        answer.append("Romanian")
        answer.append("ru")              
        answer.append("Russian")
        answer.append("rs")              
        answer.append("Serbian (Cyrillic)")
        answer.append("si")              
        answer.append("Slovenian")
        answer.append("sk")             
        answer.append("Slovak")
        answer.append("es")              
        answer.append("Spanish")
        answer.append("se")              
        answer.append("Swedish")
        answer.append("ch")              
        answer.append("German (Switzerland)")
        answer.append("sy")              
        answer.append("Arabic (Syria)")
        answer.append("tj")             
        answer.append("Tajik")
        answer.append("lk")              
        answer.append("Sinhala (phonetic)")
        answer.append("th")              
        answer.append("Thai")
        answer.append("tr")              
        answer.append("Turkish")
        answer.append("tw")              
        answer.append("Taiwanese")
        answer.append("ua")              
        answer.append("Ukrainian")
        answer.append("gb")              
        answer.append("English (UK)")
        answer.append("uz")              
        answer.append("Uzbek")
        answer.append("vn")              
        answer.append("Vietnamese")
        answer.append("kr")              
        answer.append("Korean")
        answer.append("nec_vndr/jp")     
        answer.append("Japanese (PC-98xx Series)")
        answer.append("ie")              
        answer.append("Irish")
        answer.append("pk")              
        answer.append("Urdu (Pakistan)")
        answer.append("mv")              
        answer.append("Dhivehi")
        answer.append("za")              
        answer.append("English (South Africa)")
        answer.append("epo")             
        answer.append("Esperanto")
        answer.append("np")              
        answer.append("Nepali")
        answer.append("ng")              
        answer.append("English (Nigeria)")
        answer.append("et")              
        answer.append("Amharic")
        answer.append("sn")              
        answer.append("Wolof")
        answer.append("brai")            
        answer.append("Braille")
        answer.append("tm")              
        answer.append("Turkmen")
        answer.append("ml")              
        answer.append("Bambara")
        answer.append("tz")              
        answer.append("Swahili (Tanzania)")
        answer.append("ke")              
        answer.append("Swahili (Kenya)")
        answer.append("bw")              
        answer.append("Tswana")
        answer.append("ph")              
        answer.append("Filipino")        
        return answer

    def mouse_get(self, session_id, parameters):
        '''
        Get mouse
        '''
        return [steelsquid_utils.get_parameter("mouse_speed"), steelsquid_utils.get_parameter("mouse_acc")]

    def mouse_set(self, session_id, parameters):
        '''
        Set mouse
        '''
        try:
            speed = int(parameters[0])
            acc = int(parameters[1])
            if speed < 1 or speed > 10:
                raise Exception("Speed must be between 1 and 10!")
            if acc < 1 or acc > 20:
                raise Exception("Acceleration must be between 1 and 20!")
        except:
            raise Exception("Value must be a number!")
        if len(parameters) > 0:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'mouse', parameters[0], parameters[1]])
        return [steelsquid_utils.get_parameter("mouse_speed"), steelsquid_utils.get_parameter("mouse_acc")]

    def font_get(self, session_id, parameters):
        '''
        Get font
        '''
        return [steelsquid_utils.get_parameter("font")]

    def font_set(self, session_id, parameters):
        '''
        Set font
        '''
        try:
            font = int(parameters[0])
            if font < 1 or font > 99:
                raise Exception("Value must be between 1 and 99!")
        except:
            raise Exception("Value must be a number!")
        if len(parameters) > 0:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'font', parameters[0]])
        return [steelsquid_utils.get_parameter("font")]

    def autologin(self, session_id, parameters):
        '''
        Get autologin
        '''
        if steelsquid_utils.get_flag("encrypt"):
            return "Encrypt"
        else:
            return steelsquid_utils.get_flag("autologin")

    def autologin_on(self, session_id, parameters):
        '''
        Set autologin
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'autologin-on'])
            return self.autologin(session_id, parameters)

    def autologin_off(self, session_id, parameters):
        '''
        Set autologin
        '''
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'autologin-off'])
        return self. autologin(session_id, parameters)

    def clean(self, session_id, parameters):
        '''
        Clear private data
        '''
        self.lock_command('clean')
        if parameters[0]=='True':
            self.execute_system_command(['sudo', 'steelsquid', 'clean-deep'], 'clean')
        else:
            self.execute_system_command(['sudo', 'steelsquid', 'clean'], 'clean')

    def password(self, session_id, parameters):
        '''
        Change password
        '''
        if parameters[0] != parameters[1]:
            raise Exception("Password does not match the confirm password")
        elif not steelsquid_utils.authenticate(USERNAME, parameters[2]):
            raise Exception("You entered wrong current password")
        else:
            proc=Popen(['passwd', 'steelsquid'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            if not steelsquid_utils.is_root():
                proc.stdin.write(parameters[2] + '\n')
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


    def ssh_disable(self, session_id, parameters):
        '''
        Enable or disable ssh server
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'ssh-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'ssh-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("disable_ssh")

    def ssh_openssh(self, session_id, parameters):
        '''
        Use openssh instead of dropear
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'ssh-openssh'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'ssh-dropbear'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("ssh_openssh")

    def ssh_port(self, session_id, parameters):
        '''
        Change ssh port
        '''
        if len(parameters) > 0:
            proc=Popen(['sudo', 'steelsquid', 'ssh-port', parameters[0]], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
        port = steelsquid_utils.get_parameter("ssh_port")
        if port == "":
            port = "22"
            steelsquid_utils.set_parameter("ssh_port", "22")
        return port

    def web_interface_disable(self, session_id, parameters):
        '''
        Get or set if the webinterface is disabled
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'web-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'web-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("disable_web")

    def web_interface_share(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /home/steelsquid
        '''
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_share_on(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /home/steelsquid
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.set_flag("web_interface_share")
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_share_off(self, session_id, parameters):
        '''
        On web interface share /mnt, /media and /home/steelsquid
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.del_flag("web_interface_share")
        return steelsquid_utils.get_flag("web_interface_share")

    def web_interface_localhost(self, session_id, parameters):
        '''
        Localhost
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'web-local-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'web-local-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("local_web")

    def web_interface_https(self, session_id, parameters):
        '''
        http
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'web-https'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'web-http'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return [steelsquid_utils.get_flag("use_https"), steelsquid_utils.get_parameter("web_port")]

    def web_interface_authentication(self, session_id, parameters):
        '''
        http
        '''
        return [not steelsquid_utils.get_flag("web_no_password")]

    def web_interface_authentication_on(self, session_id, parameters):
        '''
        http
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            proc=Popen(['sudo', 'steelsquid', 'web-aut-on'], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
            return [not steelsquid_utils.get_flag("web_no_password")]

    def web_interface_authentication_off(self, session_id, parameters):
        '''
        http
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            proc=Popen(['sudo', 'steelsquid', 'web-aut-off'], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
            return [not steelsquid_utils.get_flag("web_no_password")]

    def web_interface_port(self, session_id, parameters):
        '''
        http
        '''
        if len(parameters) > 0:
            proc=Popen(['sudo', 'steelsquid', 'web-port', parameters[0]], stdout = PIPE, stderr = STDOUT)  
            proc.wait()
        return steelsquid_utils.get_parameter("web_port") 

    def encrypt_info(self, session_id, parameters):
        '''
        Is the filesystem encrypted
        '''
        return [steelsquid_utils.get_flag("encrypt"), steelsquid_utils.is_root()]

    def encrypt_mode(self, session_id, parameters):
        '''
        restart to 
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            os.system("sudo /etc/init.d/steelsquid root")

    def encrypt_mode_exit(self, session_id, parameters):
        '''
        restart to 
        '''
        os.system("sudo /etc/init.d/steelsquid restart")

    def encrypt(self, session_id, parameters):
        '''
        Encrypt the filesystem
        '''
        import pexpect
        if steelsquid_utils.get_flag("encrypt"):
            raise Exception("The file system is already encrypted.")
        lst = os.listdir("/home/"+USERNAME)
        for d in lst:
            if steelsquid_utils.is_mounted("/home/"+USERNAME+"/"+d):
                raise Exception("You must umount folder /home/"+USERNAME+"/"+d)
        proc = Popen(['ps', '-fu', USERNAME], stdout = PIPE, stderr = STDOUT)
        proc.wait()
        out = proc.stdout.read()
        if out.count('\n') > 1:
            raise Exception("All sessions of the user "+USERNAME+" must log out before you can begin encrypting!")
        password = parameters[0]
        if not steelsquid_utils.authenticate(USERNAME, password):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            self.execute_system_command(['steelsquid', 'ssh-openssh'], "encrypt")
            try:
                self.execute_system_command(['steelsquid', 'autologin-off'], "encrypt")
                self.execute_system_command(["aptitude", "-R", "-y", "-o", "Aptitude::Cmdline::ignore-trust-violations=true", "install", "ecryptfs-utils", "cryptsetup"], "encrypt")
                self.execute_system_command(["modprobe", "ecryptfs"], "encrypt")
                cmd = "ecryptfs-migrate-home -u "+USERNAME
                child=pexpect.spawn(cmd, timeout=99999)
                i=child.expect_exact(['['+USERNAME+']: ', pexpect.EOF])
                if i==0:
                    child.sendline(password)
                    i=child.expect_exact(['['+USERNAME+']: ', '\n'])
                    if i==0:
                        raise Exception("User/Password error")
                    else:
                        for line in iter(child.readline, b''):
                            line = line.strip('\n').strip()
                            self.add_async_answer("encrypt", line)
                elif i==1:
                    raise Exception(child.before)
                os.chmod('/home/.ecryptfs', 0755)
                self.add_async_answer("encrypt", steelsquid_utils.make_log_string("Testing login"))
                cmd = "sudo login " + USERNAME
                child=pexpect.spawn(cmd)
                i=child.expect_exact(['Password: ', pexpect.EOF])
                if i==0:
                    child.sendline(password)
                    time.sleep(4)
                    child.sendline("exit")
                    i=child.expect_exact(pexpect.EOF)
                elif i==1:
                    raise Exception(child.before)
                self.add_async_answer("encrypt", steelsquid_utils.make_log_string("Remove backup"))
                steelsquid_utils.execute_system_command(["/bin/bash", "-c", "rm -r /home/"+USERNAME+".*"])
                steelsquid_utils.execute_system_command_blind("rm -r /home/nohup.out")
                if steelsquid_utils.get_flag("swap"):
                    self.add_async_answer("encrypt", steelsquid_utils.make_log_string("Encrypting swap"))
                    self.execute_system_command(["ecryptfs-setup-swap", "-f"], "encrypt")
                self.add_async_answer("encrypt", steelsquid_utils.make_log_string("The encryption is completed"))
                steelsquid_utils.set_flag("encrypt")
            finally:
                try:
                    child.close()
                except:
                    pass

    def shutdown(self, session_id, parameters):
        '''
        Shutdown the computer
        '''
        os.system('sudo shutdown -h now')
        return "System shutting down"

    def reboot(self, session_id, parameters):
        '''
        Reboot the computer
        '''
        os.system('sudo reboot')
        return "System reboots"

    def system_info(self, session_id, parameters):
        '''
        Return system info
        '''
        return steelsquid_utils.system_info()

    def upgrade(self, session_id, parameters):
        '''
        Upgrade the system
        '''
        if not steelsquid_utils.has_internet_connection():
            raise Exception("You must be connected to the internet to make an upgrade!")
        self.lock_command('upgrade')
        if parameters[0] == 'small':
            self.execute_system_command(['sudo', 'steelsquid', 'update'], "upgrade")
            self.execute_system_command(['sudo', 'steelsquid', 'update-web'], "upgrade")
            self.execute_system_command(['sudo', 'steelsquid', 'update-python'], "upgrade")
        elif parameters[0] == 'full':
            self.execute_system_command(['sudo', 'steelsquid', 'upgrade'], "upgrade")

    def expand(self, session_id, parameters):
        '''
        Expand-rootfs
        '''
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'expand']) 
        return "Root partition has been resized.<br />The filesystem will be enlarged upon the next reboot."

    def swap_disable(self, session_id, parameters):
        '''
        Get or set the use of swap
        '''
        self.lock_command('swap_disable')
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'swap-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'swap-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return not steelsquid_utils.get_flag("swap")

    def root_on(self, session_id, parameters):
        '''
        Root mode
        '''
        if len(parameters)>0:
            if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
                raise Exception("Incorrect password for user "+USERNAME+"!")
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'root-on']) 
        return steelsquid_utils.get_flag("root")

    def root_off(self, session_id, parameters):
        '''
        Root mode
        '''
        if len(parameters)>0:
            if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
                raise Exception("Incorrect password for user "+USERNAME+"!")
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'root-off']) 
        return steelsquid_utils.get_flag("root")

    def monitor_disable(self, session_id, parameters):
        '''
        Enable or disable monitor
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'display-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'display-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("disable_monitor")

    def camera(self, session_id, parameters):
        '''
        Enable or disable camera
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'camera-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'camera-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("camera")

    def stream(self, session_id, parameters):
        '''
        Enable or disable streamimg
        '''
        if len(parameters) > 0:
            if parameters[0] == "True":
                proc=Popen(['sudo', 'steelsquid', 'stream-on'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'stream-off'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        return steelsquid_utils.get_flag("stream")


    def overclock(self, session_id, parameters):
        '''
        Set and get overklock
        '''
        if len(parameters) > 0:
            if parameters[0] == "over":
                proc=Popen(['sudo', 'steelsquid', 'overclock'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            elif parameters[0] == "under":
                proc=Popen(['sudo', 'steelsquid', 'underclock'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
            else:
                proc=Popen(['sudo', 'steelsquid', 'defaultclock'], stdout = PIPE, stderr = STDOUT)  
                proc.wait()
        if steelsquid_utils.get_flag("overclock"):
            return "over"
        elif steelsquid_utils.get_flag("underclock"):
            return "under"
        else:
            return "default"

    def lcd(self, session_id, parameters):
        '''
        Get the use of lcd to display ip
        '''
        import steelsquid_pi
        if steelsquid_utils.get_flag("lcd_direct"):
            return "direct"
        elif steelsquid_utils.get_flag("lcd_i2c"):
            return "i2c"
        else:
            return "disable"

    def lcd_disable(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        import steelsquid_pi
        steelsquid_utils.del_flag("lcd_direct")
        steelsquid_utils.del_flag("lcd_i2c")
        return self.lcd(parameters)

    def lcd_direct(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            import steelsquid_pi
            steelsquid_utils.set_flag("root")
            steelsquid_utils.set_flag("lcd_direct")
            steelsquid_utils.del_flag("lcd_i2c")
            return self.lcd(parameters)

    def lcd_i2c(self, session_id, parameters):
        '''
        Get and set the use of lcd to display ip
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            import steelsquid_pi
            steelsquid_utils.set_flag("root")
            steelsquid_utils.del_flag("lcd_direct")
            steelsquid_utils.set_flag("lcd_i2c")
            return self.lcd(parameters)

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
        return steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'gpu-mem'])

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
                steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'gpu-mem', str(inte)])
                return "Memory changed"

    def downman(self, session_id, parameters):
        '''
        
        '''
        return steelsquid_utils.get_flag("download")
        


    def downman_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-on']) 
        return steelsquid_utils.get_flag("download")


    def downman_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-off']) 
        return steelsquid_utils.get_flag("dovnload")

    def download_activate(self, session_id, parameters):
        '''
        Add a download link
        '''
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'download-on'])

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
                steelsquid_utils.set_permission(the_file)
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
             
             
    def rover(self, session_id, parameters):
        '''
        
        '''
        enabled = steelsquid_utils.get_flag("rover")
        if enabled:
            answer = steelsquid_utils.execute_system_command(['sudo', 'steelsquid-nm', 'system-status'])
            if answer[0] == 'None':
                return [True, "Not connected!", "---", "---", "---"]
            else:
                ip_wired = steelsquid_utils.network_ip_wired()
                ip_wifi = steelsquid_utils.network_ip_wifi()
                wan_ipp = steelsquid_utils.network_ip_wan()
                return [True, answer[0], ip_wired, ip_wifi, wan_ipp]
        else:
            return enabled
        


    def rover_enable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'rover-on']) 
        return steelsquid_utils.get_flag("rover")


    def rover_disable(self, session_id, parameters):
        '''
        
        '''
        if not steelsquid_utils.authenticate(USERNAME, parameters[0]):
            raise Exception("Incorrect password for user "+USERNAME+"!")
        else:
            steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'rover-off']) 
        return steelsquid_utils.get_flag("rover")


    def rover_stop(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_pi_board
        steelsquid_pi_board.sabertooth_set_speed(0, 0)


    def rover_left(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_pi_board
        steelsquid_pi_board.sabertooth_set_speed(20, -20)


    def rover_right(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_pi_board
        steelsquid_pi_board.sabertooth_set_speed(-20, 20)


    def rover_forward(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_pi_board
        steelsquid_pi_board.sabertooth_set_speed(20, 20)


    def rover_backward(self, session_id, parameters):
        '''
        
        '''
        import steelsquid_pi_board
        steelsquid_pi_board.sabertooth_set_speed(-20, -20)


