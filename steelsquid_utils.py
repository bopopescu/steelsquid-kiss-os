#!/usr/bin/python -OO


'''
Some useful functions.

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-07-31 Created
'''


import steelsquid_event
import subprocess
from subprocess import Popen, PIPE, STDOUT
import uuid
import os
import pwd
import grp
import urllib
import shutil
import sys
import threading
import thread
import time
import urllib2
import PAM
import hashlib
import datetime
import traceback
import smtplib
import re


lock = threading.Lock()
STEELSQUID_FOLDER = "/opt/steelsquid"
cach_credentionals = []
salt = uuid.uuid4().hex
run_flags = set() 
run_parameters = {}
run_lists = {}
LCD_MESSAGE_TIME = 10
last_shout_message = None
last_shout_time = -1
in_dev = None
VALID_CHARS = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9','_','/','.','-']


def steelsquid_kiss_os_version():
    '''
    '''
    return 1.0, "v1.0"
    

def is_raspberry_pi():
    '''
    Is this a raspberry pi
    '''
    ans = read_from_file("/proc/cpuinfo")
    if "BCM2708" in ans:
        return True
    else:
        return False

def log(message):
    '''
    Log a message.
    @param message: The message to log
    '''
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + message)


def make_log_string(message):
    '''
    Make a log string
    @param message: The message
    '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + message


def write_to_file(filename, text):
    '''
    Write text to a file.
    @param filename: The file
    @param text: The text to write
    '''
    f = open(filename, "w")
    try:
        f.write(text)
    finally:
        try:
            f.close()
        except:
            pass


def append_to_file(filename, text):
    '''
    Append text to a file.
    @param filename: The file
    @param text: The text to write
    '''
    if not os.path.exists(filename):
        f = open(filename, "w")
        try:
            f.write(text)
        finally:
            try:
                f.close()
            except:
                pass
    else:
        if os.stat(filename).st_size > 100000000:
            os.remove(filename)
        f = open(filename, "a")
        try:
            f.write(text)
        finally:
            try:
                f.close()
            except:
                pass


def read_from_file(filename):
    '''
    Read text file.
    @param filename: The file
    @return: The line, if no file it will return ""
    '''
    try:
        f = open(filename, "r")
        line = f.read()
        return line
    except:
        return ""
    finally:
        try:
            f.close()
        except:
            pass


def read_from_file_and_delete(filename):
    '''
    Read text file and delete the file.
    @param filename: The file
    @return: The line, if no file it will return None
    '''
    try:
        f = open(filename, "r")
        line = f.read()
        return line
    except:
        return None
    finally:
        try:
            f.close()
        except:
            pass
        deleteFileOrFolder(filename)


def has_internet_connection():
    '''
    Check if there is internet connection.
    @return: true/False
    '''
    try:
        con = urllib2.urlopen("http://www.google.com")
        con.read()
        return True
    except:
        return False


def make_ok_answer_string(command, parameters=None, long_reply=False):
    '''
    Generate a OK answer string <command_ok|<para1>|para2...>
    @param command: The command name
    @param parameters: Paramater string or list with paramaters
    @return: The answer string
    '''
    answer_string = []
    if long_reply:
        answer_string.append('<')
        answer_string.append(command)
        answer_string.append("_ok")
    if not parameters == None:
        if len(parameters) > 0:
            if isinstance(parameters, basestring):
                if long_reply:
                    answer_string.append('|')
                answer_string.append(encode_string(parameters))
            else:
                show_first = long_reply
                for parameter in parameters:
                    if show_first:
                        answer_string.append('|')
                    else:
                        show_first = True
                    answer_string.append(encode_string(parameter))
    if long_reply:
        answer_string.append('>')
    return ''.join(answer_string)


def make_err_answer_string(command, parameters=None, useStartStop=False):
    '''
    Generate a ERROR answer string <command_err|<para1>|para2...>
    @param command: The command name
    @param parameters: Paramater string or list with paramaters
    @return: The answer string
    '''
    answer_string = []
    if long_reply:
        answer_string.append('<')
        answer_string.append(command)
        answer_string.append("_err")
    if not parameters == None:
        if len(parameters) > 0:
            if isinstance(parameters, basestring):
                if long_reply:
                    answer_string.append('|')
                answer_string.append(encode_string(parameters))
            else:
                show_first = long_reply
                for parameter in parameters:
                    if show_first:
                        answer_string.append('|')
                    else:
                        show_first = True
                    answer_string.append(encode_string(parameter))
    if long_reply:
        answer_string.append('>')
    return ''.join(answer_string)


def execute_system_command(system_command, ok_exit_code=0):
    '''
    Execute a system command 
    Throw exception if exit status from command other than 0
    @param system_command: The system command to execute
    @param ok_exit_code: The exit code that eans the kommand is OK (None = do not check)
    @return: Answer will be returned as a array
    '''
    proc=Popen(system_command, stdout = PIPE, stderr = STDOUT  )
    answer = []
    for line in iter(proc.stdout.readline, b''):
        line = line.strip('\n').strip()
        if len(line) > 0:
            answer.append(line)
    status = proc.wait()
    if ok_exit_code == None or status == ok_exit_code:
        return answer
    else:
        if len(answer) == 0:
            raise RuntimeError("Exception status: " + str(status))
        else:
            raise RuntimeError(str(answer[0]))

            
def execute_system_command_blind(system_command, wait_for_finish=True):
    '''
    Execute a system command and do not read answer or throw exception.
    @param system_command: The system command to execute
    '''
    try:
        if type(system_command) is list:
            proc=Popen(system_command, stdout = PIPE, stderr = STDOUT)
            if wait_for_finish:
                proc.wait()
        else:
            if wait_for_finish:
                os.system(system_command + " >/dev/null 2>&1")
            else:
                os.system(system_command + " >/dev/null 2>&1 &")
    except:
        pass


def encode_string(string):
    '''
    If a paramater contain |, \n it has to be encoded:
    | = #1#
    \n = #2#
    @param string: The string to encode
    @return: The encoded string
    '''
    return string.replace("|", "#1#").replace("\n", "#2#")


def decode_string(string):
    '''
    If a paramater contain |, \n it has to be encoded:
    | = #1#
    \n = #2#
    @param string: The string to decode
    @return: The decoded string
    '''
    return string.replace("#1#", "|").replace("#2#", "\n")


def printb(string):
    '''
    Print bold text to screen
    '''
    print('\033[1m' + string + '\033[0m')


def shout_time(message):
    '''
    Shout with time
    '''
    shout(datetime.datetime.now().strftime("%H:%M:%S") + "\n" + message)


def shout(string=None, to_lcd=True, debug=False, is_error=False, always_show=False):
    '''
    Send message to tty1, wall notify-send
    If a raspberry-pi try to write to LCD
    @param string: The string
    @param to_lcd: If raspberry pitry to print to lcd
    @param debug: True = Only print if in development mode
    @param is_error: Is this a error message
    '''
    if debug==False or development():
        global last_shout_message
        global last_shout_time
        if string == None or is_error==True:
            is_error = True
            exc_type, exc_value, exc_tb = sys.exc_info()
            ex = traceback.format_exception(exc_type, exc_value, exc_tb)
            if string == None:
                string = str(exc_type) + ": " + str(exc_value) +"\n"+str(ex)
            else:
                string = string + "\n" + str(exc_type) + ": " + str(exc_value) +"\n"+str(ex)
            del exc_tb
        string = str(string)
        do_it = True
        now = time.time()
        if last_shout_message != None and last_shout_time != -1:
            diff = now - last_shout_time
            if diff > 60:
                do_it=True
            elif diff <= 60 and last_shout_message!=string:
                do_it=True
            else:
                do_it=False
        if do_it or always_show:
            last_shout_time = now
            last_shout_message = string
            try:
                execute_system_command(['shout', string])
            except:
                pass
            if get_flag("io"):
                import steelsquid_piio
                if is_error:
                    try:
                        steelsquid_piio.led_error_flash_timer(2)
                        steelsquid_piio.sum_flash_timer(1)
                    except:
                        pass
                else:
                    try:
                        steelsquid_piio.led_ok_timer(1)
                    except:
                        pass
            if to_lcd and is_raspberry_pi():
                if get_flag("hdd"):
                    try:
                        steelsquid_pi.hdd44780_write(string, LCD_MESSAGE_TIME, force_setup = False)
                    except:
                        pass
                elif get_flag("nokia"):
                    try:
                        steelsquid_pi.nokia5110_write(string, LCD_MESSAGE_TIME, force_setup = False)
                    except:
                        pass
                elif get_flag("auto"):
                    try:
                        steelsquid_pi.nokia5110_write(string, LCD_MESSAGE_TIME, force_setup = False)
                    except:
                        try:
                            steelsquid_pi.hdd44780_write(string, LCD_MESSAGE_TIME, force_setup = False)
                        except:
                            pass


def notify(string):
    '''
    Same as shout but also try to send mail
    '''
    shout(string)
    mail(string)


def mail(string):
    '''
    Try to send mail message to configured mail
    '''
    try:
        mail_host = get_parameter("mail_host")
        mail_username = get_parameter("mail_username")
        mail_password = get_parameter("mail_password")
        mail_mail = get_parameter("mail_mail")
        send_mail(mail_host, mail_username, mail_password, "do-not-reply@steelsquid.org", mail_mail, os.popen("hostname").read(), string)
    except:
        pass
        

def valid_get_string(string):
    '''
    Do this string only countain a-z A-Z, 0-9, _, /, ., -
    @param string: String
    @return: True/False
    '''
    dott = False
    if ".." in string:
        return False
    for s in string:
        if s not in VALID_CHARS:
            return False
    return True


def memory():
    """
    Get ram information in MByte
    @return: ram_total, ram_free, ram_used
    """
    ram_total = 0
    ram_free = 0
    ram_used = 0
    tmp_buffers = 0
    tmp_cached = 0
    with open('/proc/meminfo') as fp:
        for line in fp:
            sline = line.split()
            if sline[0] == "MemTotal:":
                ram_total = int(sline[1])
            elif sline[0] == "MemFree:":
                ram_free = int(sline[1])
            elif sline[0] == "Buffers:":
                tmp_buffers = int(sline[1])
            elif sline[0] == "Cached:":
                tmp_cached = int(sline[1])
    ram_free = ram_free + tmp_buffers + tmp_cached
    ram_used = ram_total - ram_free
    return ram_total/1024, ram_free/1024, ram_used/1024


def network_info_string():
    """
    Get network information wifi/wired and ip
    @return: string
    """
    output = network_ip_wired()
    if output == '---':
        output = network_ip_wired()
        if output == '---':
            return "No network connection!"
        else:
            return "Wifi network IP: " + network_ip_wifi()
        
    else:
        return "Wired network IP: " + output


def network_ip():
    """
    Get network information wifi/wired
    @return: string
    """
    output = network_ip_wired()
    if output == '---':
        return network_ip_wifi()
    else:
        return output


def network_ip_wired():
    """
    Get network information wired 
    @return: string
    """
    output = subprocess.check_output("/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
    if len(output) < 4 or "eth" in output:
        output = subprocess.check_output("/sbin/ifconfig eth1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
        if len(output) < 4 or "eth" in output:
            output = subprocess.check_output("/sbin/ifconfig eth2 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
            if len(output) < 4 or "eth" in output:
                output = subprocess.check_output("/sbin/ifconfig eth3 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
                if len(output) < 4 or "eth" in output:
                    output = subprocess.check_output("/sbin/ifconfig eth4 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
                    if len(output) < 4 or "eth" in output:
                        return "---"
                    else:
                        return output
                else:
                    return output
            else:
                return output
        else:
            return output
    else:
        return output


def network_ip_wifi():
    """
    Get network information wifi
    @return: string
    """
    output = subprocess.check_output("/sbin/ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
    if len(output) < 4 or "wlan" in output:
        output = subprocess.check_output("/sbin/ifconfig wlan1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
        if len(output) < 4 or "wlan" in output:
            output = subprocess.check_output("/sbin/ifconfig wlan2 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
            if len(output) < 4 or "wlan" in output:
                output = subprocess.check_output("/sbin/ifconfig wlan3 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
                if len(output) < 4 or "wlan" in output:
                    output = subprocess.check_output("/sbin/ifconfig wlan4 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
                    if len(output) < 4 or "wlan" in output:
                        output = subprocess.check_output("/sbin/ifconfig wlan5 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
                        if len(output) < 4 or "wlan" in output:
                            return "---"
                        else:
                            return output
                    else:
                        return output
                else:
                    return output
            else:
                return output
        else:
            return output
    else:
        return output


def network_ip_vpn():
    """
    Get network information vpn
    @return: string
    """
    output = subprocess.check_output("/sbin/ifconfig tun0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
    if len(output) < 4 or "tun" in output:
        output = subprocess.check_output("/sbin/ifconfig tun1 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
        if len(output) < 4 or "tun" in output:
            return "---"
        else:
            return output
    else:
        return output


def network_ip_wan():
    """
    Get wan ip (internet)
    @return: the ip
    """
    try:
        pub_ip = urllib.urlopen('http://curlmyip.com').read().strip('\n')
        return pub_ip
    except:
        return "---"


def send_mail(smtp_host, from_mail, to_mail, subject, message):
    '''
    Send mail by smtp server (gmail: smtp.gmail.com:587)
    '''
    send_mail(smtp_host, None, None, from_mail, to_mail, subject, message)


def send_mail(smtp_host, username, password, from_mail, to_mail, subject, message):
    '''
    Send mail by smtp server (gmail: smtp.gmail.com:587)
    '''
    large_message = []
    large_message.append("From: ")
    large_message.append(from_mail)
    large_message.append("\n")
    large_message.append("To: ")
    large_message.append(to_mail)
    large_message.append("\n")
    large_message.append("Subject: ")
    large_message.append(subject)
    large_message.append("\n\n")
    large_message.append(message)
    large_message.append("\n")
    server = None
    try:
        server = smtplib.SMTP(smtp_host)
        server.starttls()
        if username != None and username != "":
            server.login(username, password)
        server.sendmail(from_mail, to_mail, "".join(large_message))
    finally:
        try:
            server.quit()
        except:
            pass
    

def cpu_freq():
    """
    Get cpu freq
    """
    return read_from_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").replace('\n', ' ').replace('\r', '')


def system_info():
    '''
    Return system info
    '''
    # Datetime
    f = os.popen("date")
    p_date = f.read().replace('\n', '').replace('\r', '')
        
    # Hostname
    f = os.popen("hostname")
    p_hostname = f.read().replace('\n', '').replace('\r', '')
    
    # Development
    if get_flag("development"):
        p_development = "Enabled"
    else:
        p_development = "Disabled"
    
    # Boot time
    f = os.popen("who -b")
    who = f.read().replace('\n', '').replace('\r', '')
    who = who.split()
    p_boot = who[2] + " " + who[3]
    
    # Uptime
    f = os.popen("uptime")
    uptime = f.read().replace('\n', '').replace('\r', '')
    uptime = uptime.split(",")
    if len(uptime) == 6:
        p_up = uptime[0].split("up ")[1]
        p_users = uptime[2].replace("users", "").strip()
        p_load = uptime[3].replace("load average:", "").strip() + ", " + uptime[4].strip() + ", " + uptime[5].strip()
    else:
        p_up = uptime[0].split("up ")[1]
        p_users = uptime[1].replace("users", "").strip()
        p_load = uptime[2].replace("load average:", "").strip() + ", " + uptime[3].strip() + ", " + uptime[4].strip()
    
    # Network 
    p_ip_wired = network_ip_wired()
    p_ip_wifi = network_ip_wifi()
    p_ip_wan = network_ip_wan()
    net = execute_system_command(['steelsquid-nm', 'system-status'])
    if net[0] == 'None':
        p_access_point = "Not connected!"
    else:    
        p_access_point = net[0]

    # CPU
    f = os.popen("mpstat 1 1 | grep Average: | awk '{print $NF}'")
    cpu = f.read().replace('\n', '').replace('\r', '')
    p_cpu = str(float(100) - float(cpu))
    p_cpu_f = cpu_freq()
    
    # Number of proc
    f = os.popen("ps -ef | wc -l")
    p_count = f.read().replace('\n', '').replace('\r', '')
    
    # TEMP
    f = os.popen('vcgencmd measure_temp')
    temp = f.read()
    p_temp = temp.replace('temp=','').replace('\n', '').replace('\r', '')

    # RAM
    p_ram_total, p_ram_free, p_ram_used = memory()
    
    # Disk
    f = os.popen('df -h | grep /dev/root')
    disk = f.read().replace('\n', '').replace('\r', '')
    disk = disk.split()
    p_disk_size = disk[1]
    p_disk_used = disk[2]
    p_disk_aval = disk[3]
    
    # Overclock
    overclock = "None"
    if is_raspberry_pi():
        if get_flag("overclock"):
            overclock = "Overclocked"
        elif get_flag("underclock"):
            overclock = "Underclocked"
        else:
            overclock = "Default"

    # GPU
    p_gpu_mem = str(execute_system_command(['steelsquid', 'gpu-mem'])[0]).replace('\n', '').replace('\r', '')

    # Logging
    if get_flag("log"):
        p_log = "Enabled"
    else:
        p_log = "Disabled"
        
    # Monitor
    if get_flag("disable_monitor"):
        p_disable_monitor = "Disabled"
    else:
        p_disable_monitor = "Enabled"

    # Camera
    if get_flag("camera"):
        p_camera = "Enabled"
    else:
        p_camera = "Disabled"

    # Timezone
    p_timezone = read_from_file("/etc/timezone").replace('\n', '').replace('\r', '')

    # Keyboard
    p_keyb = get_parameter("keyboard")

    # WEB
    p_web = get_flag("web")
    if p_web:
        p_web = "Enabled"
    else:
        p_web = "Disabled"
    p_web_local = get_flag("web_local")
    if p_web_local:
        p_web_local = "Localhost"
    else:
        p_web_local = "All interfaces"
    p_web_https = get_flag("web_https")
    if p_web_https:
        p_web_https = "HTTPS"
    else:
        p_web_https = "HTTP"
    p_web_aut = get_flag("web_authentication")
    if p_web_aut:
        p_web_aut = "Enabled"
    else:
        p_web_aut = "Disabled"

    # SSH
    p_ssh = get_flag("ssh")
    if p_ssh:
        p_ssh = "Enabled"
    else:
        p_ssh = "Disabled"

    # LCD
    p_has_lcd = "Disabled"
    if is_raspberry_pi():
        if get_flag("hdd"):
            p_has_lcd = "Enabled (HDD44780)"
        elif get_flag("nokia"):
            p_has_lcd = "Enabled (Nokia5110)"
        elif get_flag("auto"):
            p_has_lcd = "Automatic"

    # Stream
    if get_flag("stream"):
        p_stream = "Enabled"
    else:
        p_stream = "Disabled"

    # Socket
    if get_flag("socket_connection"):
        p_socket = "Enabled"
    else:
        p_socket = "Disabled"

    # Rover
    if get_flag("rover"):
        p_rover = "Enabled"
    else:
        p_rover = "Disabled"

    # Download
    p_download_dir = get_parameter("download_dir")
    if get_flag("download"):
        p_download = "Enabled"
    else:
        p_download = "Disabled"


    # IO Board
    if get_flag("io"):
        p_io = "Enabled"
    else:
        p_io = "Disabled"

    # clean power off
    if get_flag("power"):
        p_power = "Enabled"
    else:
        p_power = "Disabled"

    # Is USB 3g/4g modem enabled"
    if get_flag("modem"):
        p_modem = "Enabled"
    else:
        p_modem = "Disabled"
        
    return (p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, overclock, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem)


def system_info_array():
    '''
    Return system info array
    '''
    p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, overclock, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem = system_info()
    return [p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, overclock, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem]


def print_system_info():
    '''
    Print system info to screen
    '''
    p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, overclock, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem = system_info()
    print
    printb("Device information (%s)" % p_date)
    print
    print("Hostname: %s" % p_hostname)
    print("Development mode: %s" % p_development)
    print("Booted: %s" % p_boot)
    print("Uptime: %s" % p_up)
    print("Users: %s" % p_users)
    print
    print("Connected to network: %s" % p_access_point)
    print("Network Wired IP: %s" % p_ip_wired)
    print("Network Wifi IP: %s" % p_ip_wifi)
    print("Internet IP: %s" % p_ip_wan)
    print("USB 3g/4g modem: %s" % p_modem)
    print
    print("CPU usage: %s" % p_cpu)
    print("CPU load %s" % p_load)
    print("CPU freq %s" % p_cpu_f)
    print("Processes: %s" % p_count)
    print("Temperatur: %s" % p_temp)
    print
    print("Total RAM: %s" % p_ram_total)
    print("Used RAM: %s" % p_ram_used)
    print("Free RAM: %s" % p_ram_free)
    print
    print("Total root: %s" % p_disk_size)
    print("Used root: %s" % p_disk_used)
    print("Free root: %s" % p_disk_aval)
    print
    print("Overclock: %s" % overclock)
    print("GPU Mem: %s" % p_gpu_mem)
    print
    print("Logging: %s" % p_log)
    print
    print("Display: %s" % p_disable_monitor)
    print("PI camera: %s" % p_camera)
    print
    print("Timezone: %s" % p_timezone)
    print("Keyboard: %s" % p_keyb)
    print
    print("Admin web-interface: %s" % p_web)
    print("Type: %s" % p_web_https)
    print("Authentication: %s" %  p_web_aut)
    print("Listening on: %s" % p_web_local)
    print
    print("SSH-server: %s" % p_ssh)
    print("Socket server: %s" % p_socket)
    print
    print("LCD: %s" % p_has_lcd)
    print("Stream USB camera: %s" % p_stream)
    print("Rover: %s" % p_rover)
    print("Download manager: %s" % p_download)
    print("Download dir: %s" % p_download_dir)
    print("Steelsquid IO Board: %s" % p_io)
    print("Clean power off: %s" % p_power)


def is_video_file(name):
    '''
    Is this a video file
    '''
    name = name.lower()
    for f in [".flv", ".avi", ".mov", ".mp4", ".mp2", ".mpg", ".mpeg", ".wmv", ".3gp", ".asf", ".rm", ".swf", ".mkv",  ".mp4",  ".dts"]:
        if name.endswith(f):
            return True
    return False
    

def clear_authenticate_cache():
    '''
    Clear the cache of users
    '''
    global cach_credentionals
    cach_credentionals = []    


def authenticate(user, password):
    '''
    Check user and password with PAM
    '''
    global cach_credentionals
    global salt
    hash_string = hashlib.sha256(user.encode()+password.encode()+salt.encode()).hexdigest()
    if hash_string in cach_credentionals:
        user=""
        password=""
        return True
    else:
        cach_credentionals = []
        def pam_conv(auth, query_list, userData):
            return [(password, 0)]
        auth = PAM.pam()
        auth.start("passwd")
        auth.set_item(PAM.PAM_USER, user)
        auth.set_item(PAM.PAM_CONV, pam_conv)
        try:
            auth.authenticate()
            user=""
            password=""
            cach_credentionals.append(hash_string)
            return True
        except:
            user=""
            password=""
            return False


def is_mounted(directory):
    '''
    Is anything mounted in this directory
    '''
    try:
        proc = Popen(['mountpoint', directory], stdout = PIPE, stderr = STDOUT)
        proc.wait()
        out = proc.stdout.read()
        if "is a mountpoint" in out:
            return True
    except:
        pass
    return False


def umount(local, the_type="unknown", ip="unknown", remote="unknown"):
    '''
    UMount folder
    '''
    execute_system_command_blind(["umount", local])
    execute_system_command_blind(["umount", "-f", local])
    execute_system_command_blind(["umount", "-f", "-l", local])
    steelsquid_event.broadcast_event("umount", [the_type, ip+remote, local])


def mount_sshfs(ip, port, user, password, remote, local):
    '''
    Mount sshfs
    '''
    cmd = "echo %s | sshfs -o allow_other,nodev,nosuid,noexec,noatime,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no,NumberOfPasswordPrompts=1,password_stdin,umask=077 -p %s %s@%s:%s %s" % (password, port, user, ip, remote, local)
    stdin, stdout_and_stderr = os.popen4(cmd)
    answer = stdout_and_stderr.read()
    if len(answer)>5:
        raise Exception(answer)
    steelsquid_event.broadcast_event("mount", ['ssh', ip+remote, local])


def mount_samba(ip, user, password, remote, local):
    '''
    Mount samba
    '''
    if len(user)==0 and len(password)==0:
        proc = Popen(['mount', '-t', 'cifs', '-o', 'rw,nounix,nodev,nosuid,noexec,iocharset=utf8,file_mode=0700,dir_mode=0700,soft', '//' + ip + '/' + remote, local], stdout = PIPE, stderr = STDOUT)
    elif len(user)!=0 and len(password)==0:
        proc = Popen(['mount', '-t', 'cifs', '-o', 'username=' + user + ',rw,nounix,nodev,nosuid,noexec,iocharset=utf8,file_mode=0700,dir_mode=0700,soft', '//' + ip + '/' + remote, local], stdout = PIPE, stderr = STDOUT)
    else:
        proc = Popen(['mount', '-t', 'cifs', '-o', 'username=' + user + ',password=' + password + ',rw,nounix,nodev,nosuid,noexec,iocharset=utf8,file_mode=0700,dir_mode=0700,soft', '//' + ip + '/' + remote, local], stdout = PIPE, stderr = STDOUT)
    proc.wait()
    out = proc.stdout.read()
    if len(out)>5:
        raise Exception(out)
    steelsquid_event.broadcast_event("mount", ['samba', ip+remote, local])


def list_samba(ip, user, password):
    '''
    List shares from a samba server
    '''
    if len(user)==0 and len(password)==0:
        proc = Popen(['smbclient', '-L', ip, '-N'], stdout = PIPE, stderr = STDOUT)
    elif len(user)!=0 and len(password)==0:
        proc = Popen(['smbclient', '-L', ip, '-N', '-U', user], stdout = PIPE, stderr = STDOUT)
    else:
        proc = Popen(['smbclient', '-L', ip, '-U', user + "\x25" + password], stdout = PIPE, stderr = STDOUT)
    proc.wait()
    out = proc.stdout.read()
    if "NT_STATUS_LOGON_FAILURE" in out:
        raise Exception("Login failure!")
    elif "NT_STATUS_ACCESS_DENIED" in out:
        raise Exception("Access denied!")
    answer = []
    lines = out.split('\n')
    header = False
    for line in lines:
        if "---------" in line:
            header = True
        elif header and line.startswith("   ") and not "$" in line:
            col = line.split()
            answer.append(col[0])
    return answer
        
        
def check_file_path(the_file, root_path, check_if_exist):
    '''
    Check if file is under path
    And also if exsists
    '''
    if len(the_file) == 0:
        raise Exception("File path is empty")
    else:
        the_file = os.path.realpath(the_file)
        the_file = os.path.normpath(the_file)
        if check_if_exist and not os.path.exists(the_file):
            raise Exception("File not found")
        if isinstance(root_path, (list, tuple)):
            for pa in root_path:
                if the_file.startswith(pa):
                    return the_file
            raise Exception("File not inside root path")
        else:
            if the_file.startswith(root_path):
                return the_file
            else:
                raise Exception("File not inside root path")


def is_file_ok(the_file, root_path, check_if_exist=True):
    '''
    Check if file is under other path
    Root path can be a array
    Return True or False
    '''
    if len(the_file) == 0:
        return False
    else:
        the_file = os.path.realpath(the_file)
        the_file = os.path.normpath(the_file)
        if check_if_exist and not os.path.exists(the_file):
            return False
        if isinstance(root_path, (list, tuple)):
            for pa in root_path:
                if the_file.startswith(pa):
                    return True
            return  False
        else:
            if the_file.startswith(root_path):
                return True
            else:
                return False
            

def deleteFileOrFolder(fileOrDir):
    '''
    Delete file or folder (do not throw any exception)
    '''
    try:
        if os.path.exists(fileOrDir):
            if os.path.islink(fileOrDir):
                os.unlink(fileOrDir)
            elif os.path.isdir(fileOrDir):
                shutil.rmtree(fileOrDir)
            else:
                os.remove(fileOrDir)
    except:
        pass


def copyFileOrFolder(from_f, to_f):
    '''
    @param from_f: Path to file or folder
    @param to_f: Path to folder to copy 
    '''
    to_f = to_f + "/" + os.path.basename(from_f)
    if os.path.isdir(from_f):
        shutil.copytree(from_f, to_f)
    else:
        shutil.copy(from_f, to_f)


def moveFileOrFolder(from_f, to_f):
    '''
    @param from_f: Path to file or folder
    @param to_f: Path to folder to copy 
    '''
    to_f = to_f + "/" + os.path.basename(from_f)
    shutil.move(from_f, to_f)


def get_net_interfaces():
    '''
    Get all network interfaces
    '''
    answer = []
    interfaces = steelsquid_utils.execute_system_command(['ifconfig'])
    for inter in interfaces:
        if inter.startswith("eth") or inter.startswith("wlan"):
            answer.append(inter.split()[0])
    return answer
    

def is_valid_hostname(hostname):
    '''
    Is valide hostname
    '''
    if len(hostname) > 255:
        return False
    if hostname.endswith("."):
        hostname = hostname[:-1]
    disallowed = re.compile("[^A-Z\d-]", re.IGNORECASE)
    return all(
        (label and len(label) <= 63
         and not label.startswith("-") and not label.endswith("-")
         and not disallowed.search(label))
        for label in hostname.split("."))


def make_dirs(the_dir):
    '''
    Make a dir and set steelsquid owner
    '''
    try:
        os.makedirs(the_dir)
    except:
        pass


def set_flag(flag):
    '''
    Save flag to disk
    This value is stored on disk so it's persist between reboots
    '''
    write_to_file(STEELSQUID_FOLDER+"/flags/" + flag, "")
    

def get_flag(flag):
    '''
    Get flag from disk
    This value is stored on disk so it's persist between reboots
    @return: True/False
    '''
    return os.path.isfile(STEELSQUID_FOLDER+"/flags/" + flag)
    

def del_flag(flag):
    '''
    Remove flag from disk
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.remove(STEELSQUID_FOLDER+"/flags/" + flag)
    except:
        pass


def set_parameter(name, value):
    '''
    Save parameter to disk
    This value is stored on disk so it's persist between reboots
    '''
    write_to_file(STEELSQUID_FOLDER+"/parameters/" + name, value)
    

def get_parameter(name, default_value=""):
    '''
    Get parameter from disk
    This value is stored on disk so it's persist between reboots
    @return: parameter
    '''
    val = read_from_file(STEELSQUID_FOLDER+"/parameters/" + name).replace('\n', '').replace('\r', '')
    if val == "":
        return default_value
    else:
        return val


def has_parameter(name):
    '''
    Has parameter on disk
    This value is stored on disk so it's persist between reboots
    @return: True/False
    '''
    return os.path.isfile(STEELSQUID_FOLDER+"/parameters/" + name)
    

def del_parameter(name):
    '''
    Remove parameter from disk
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.remove(STEELSQUID_FOLDER+"/parameters/" + name)
    except:
        pass


def add_to_list(name, value):
    '''
    Add to list
    This value is stored on disk so it's persist between reboots
    '''
    append_to_file(STEELSQUID_FOLDER+"/lists/" + name, value + "\n")


def del_from_list(name, row):
    '''
    Delte row number from list
    row = 0,1,2...
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.makedirs(STEELSQUID_FOLDER+"/lists")
    except:
        pass
    array = []
    try:
        ins = open(STEELSQUID_FOLDER+"/lists/" + name, "r")
        count = 0;
        for line in ins:
            line = line.rstrip('\r\n')
            if line != '':
                if count != row:
                    array.append(line)
                count = count + 1
        try:
            ins.close()
        except:
            pass
    except:
        try:
            ins.close()
        except:
            pass
    write_to_file(STEELSQUID_FOLDER+"/lists/" + name, "\n".join(array) + "\n")    


def del_values_from_list(name, value):
    '''
    Delete all occurrences if value from list
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.makedirs(STEELSQUID_FOLDER+"/lists")
    except:
        pass
    array = []
    try:
        ins = open(STEELSQUID_FOLDER+"/lists/" + name, "r")
        for line in ins:
            line = line.rstrip('\r\n')
            if line != '':
                if line != value:
                    array.append(line)
        try:
            ins.close()
        except:
            pass
    except:
        try:
            ins.close()
        except:
            pass
    write_to_file(STEELSQUID_FOLDER+"/lists/" + name, "\n".join(array) + "\n")   


def get_from_list(name, row):
    '''
    Get value from list
    row = 0,1,2...
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.makedirs(STEELSQUID_FOLDER+"/lists")
    except:
        pass
    try:
        ins = open(STEELSQUID_FOLDER+"/lists/" + name, "r")
        count = 0;
        for line in ins:
            line = line.rstrip('\r\n')
            if line != '':
                if count == row:
                    return line
                count = count + 1
        try:
            ins.close()
        except:
            pass
    except:
        try:
            ins.close()
        except:
            pass
    return ""
    

def get_list(name):
    '''
    get list
    @return: the array
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.makedirs(STEELSQUID_FOLDER+"/lists")
    except:
        pass
    array = []
    try:
        ins = open(STEELSQUID_FOLDER+"/lists/" + name, "r")
        for line in ins:
            line = line.rstrip('\r\n')
            if line != '':
                array.append(line)
        try:
            ins.close()
        except:
            pass
    except:
        try:
            ins.close()
        except:
            pass
    if len(array) == 1 and array[0] == '':
        return []
    return array


def del_list(name):
    '''
    Delete a list
    This value is stored on disk so it's persist between reboots
    '''
    try:
        os.remove(STEELSQUID_FOLDER+"/lists/" + name)
    except:
        pass


def clear_tmp():
    '''
    Clear all tmp data
    '''
    with lock:
        run_flags.clear()
        run_parameters.clear()
        run_lists.clear()


def set_flag_tmp(flag):
    '''
    Save flag
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    run_flags.add(flag)
    

def get_flag_tmp(flag):
    '''
    Get flag 
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    @return: True/False
    '''
    return flag in run_flags
    

def del_flag_tmp(flag):
    '''
    Remove flag
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    run_flags.discard(flag)


def set_parameter_tmp(name, value):
    '''
    Save parameter
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    run_parameters[name] = value
    

def get_parameter_tmp(name):
    '''
    Get parameter
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    @return: parameter (None not found)
    '''
    return run_parameters.get(name)


def has_parameter_tmp(name):
    '''
    Has parameter
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    @return: True/False
    '''
    return run_parameters.has_key(name)
    

def del_parameter_tmp(name):
    '''
    Remove parameter
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    try:
        del run_parameters[name] 
    except:
        pass


def add_to_list_tmp(name, row):
    '''
    Add to list
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    with lock:
        li = run_lists.get(name)
        if li == None:
            li = []
        li.append(row)
        run_lists[name] = li


def del_from_list_tmp(name, row):
    '''
    Delte row numer from list
    row = 0,1,2...
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    with lock:
        try:
            li = run_lists[name]
            del li[row]
        except:
            pass


def del_values_from_list_tmp(name, value):
    '''
    Delete all occurrences if value from list
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    with lock:
        try:
            li = run_lists[name]
            count = li.count(value)
            if count > 0:
                for i in range(count):
                    li.remove(value)
        except:
            pass


def get_from_list_tmp(name, row):
    '''
    Get value from list
    row = 0,1,2...
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    return None = not found
    '''
    with lock:
        try:
            li = run_lists[name]
            return li[row]
        except:
            return None
    

def get_list_tmp(name):
    '''
    get whole list
    This value is stored in RAM memory so it is deleted between reboots
    The information will also be cleaned daily if steelsquid_event is configured
    @return: the list (None=not found)
    '''
    with lock:
        return run_lists.get(name)


def del_list_tmp(name):
    '''
    Delete a list
    The information will also be cleaned daily if steelsquid_event is configured
    '''
    try:
        with lock:
            del run_lists[name]
    except:
        pass


def execute_delay(seconds, function, paramters, dummy=False):
    '''
    Execute a function after number of seconds
    @param seconds: Delay for this number of seconds
    @param function: Execute this funcyion
    @param paramters: Paramater to the function (tuple)
    '''
    try:
        if dummy:
            time.sleep(seconds)
            function(paramters)
        else:
            thread.start_new_thread(execute_delay, (seconds, function, paramters, True)) 
    except:
        pass
        

def is_ip(string):
    '''
    Check if string is a ip number (xxx.xxx.xxx.xxx)
    @param string: String
    @return: True/False
    '''
    found1 = False
    found2 = False
    li = ['.','0','1','2','3','4','5','6','7','8','9']
    for s in string:
        if s not in li:
            return False
        elif s=='.':
            found1 = True
        else:
            found2 = True
    return found1 and found2
        

def development():
    '''
    Is in development mode (chach value from disk)
    '''
    global in_dev
    if in_dev == None:
        in_dev = get_flag("development")   
    return in_dev


def set_development():
    '''
    Set development mode
    '''
    global in_dev
    in_dev = True


def console_clear():
    '''
    
    '''
    os.system('setterm -term linux -foreground black -background white -clear -cursor off -store')


def console_location(row, col):
    '''
    
    '''
    sys.stdout.write("\033["+str(row)+";"+str(col)+"H")
    sys.stdout.flush()


def console_size():
    '''
    
    '''
    r, c = os.popen('stty size', 'r').read().split()
    r=int(r)
    c=int(c)
    return r, c


def console_write(string):
    '''
    
    '''
    sys.stdout.write(string)
    sys.stdout.flush()


def console_write_center(row_list, rows, columns):
    '''
    
    '''
    row_nr = (rows-len(row_list))/2
    first=True
    for row in row_list:
        col_nr = ((columns-len(row.decode("utf-8")))/2)+1
        row_nr = row_nr + 1
        console_location(row_nr, col_nr)
        sys.stdout.write(row)           
    sys.stdout.flush()


def console_bold(enable):
    '''
    
    '''
    if enable:
        sys.stdout.write("\x1b[1m")
    else:
        sys.stdout.write("\x1b[22m")
    
    
def console_black():
    '''
    
    '''
    sys.stdout.write("\x1b[30m")
    
    
def console_red():
    '''
    
    '''
    sys.stdout.write("\x1b[31m")
    
    
def console_green():
    '''
    
    '''
    sys.stdout.write("\x1b[32m")
    
    
def console_yellow():
    '''
    
    '''
    sys.stdout.write("\x1b[33m")
    
    
def console_blue():
    '''
    
    '''
    sys.stdout.write("\x1b[34m")
    
    
def console_purple():
    '''
    
    '''
    sys.stdout.write("\x1b[35m")
    
    
def console_cyan():
    '''
    
    '''
    sys.stdout.write("\x1b[36m")
    
    
def console_white():
    '''
    
    '''
    sys.stdout.write("\x1b[37m")


def console_read(text):
    '''
    
    '''
    return raw_input(make_log_string(text)+"$ ")
        
    
if is_raspberry_pi():
    import steelsquid_pi


