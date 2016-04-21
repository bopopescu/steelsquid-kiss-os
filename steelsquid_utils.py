#!/usr/bin/python -OO


'''
Some useful functions.

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-07-31 Created
'''


import subprocess
from subprocess import Popen, PIPE, STDOUT
import uuid
import os
import pwd
import grp
import shutil
import sys
import threading
import thread
import time
import urllib2
import hashlib
import datetime
import traceback
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders
import re
from sets import Set
import types


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
cache_flag = {}
cache_para = {}
delay_name_list =[]
flash_name_list =[]
lock = threading.Lock()
on_ok_callback_method = None
on_err_callback_method = None


def get_pi_revision():
    '''
    Gets the version number of the Raspberry Pi board
    '''
    try:
        with open('/proc/cpuinfo', 'r') as infile:
            for line in infile:
                match = re.match('Revision\s+:\s+.*(\w{4})$', line)
                if match and match.group(1) in ['0000', '0002', '0003']:
                    return 1
                elif match:
                    return 2
            return 0
    except:
        return 0


def get_pi_i2c_bus_number():
    '''
    Gets the I2C bus number /dev/i2c
    '''
    return 1 if get_pi_revision() > 1 else 0


def steelsquid_kiss_os_version():
    '''
    '''
    return 1.1, "v1.1"
    

def is_raspberry_pi():
    '''
    Is this a raspberry pi
    '''
    ans = read_from_file("/proc/cpuinfo")
    if "BCM270" in ans:
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


def get_time():
    '''
    Get time in string
    '''
    return datetime.datetime.now().strftime("%H:%M:%S")


def get_date():
    '''
    Get time in string
    '''
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_date_time():
    '''
    Get time in string
    '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def has_internet_connection(timeout = 4):
    '''
    Check if there is internet connection.
    @return: true/False
    '''
    try:
        con = urllib2.urlopen("http://www.google.com", timeout = timeout)
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


def shout_time(message, to_lcd=True, debug=False, is_error=False, always_show=False, leave_on_lcd = False, wait_for_finish=True):
    '''
    Shout with time
    '''
    message = str(message)
    shout(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + message, to_lcd, debug, is_error, always_show, leave_on_lcd, wait_for_finish)


def debug(message):
    '''
    Shout a debug message with timestamp
    Not print to LCD and byepass check for sam message in a row
    '''
    message = str(message)
    shout(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + message, to_lcd=False, debug=True, is_error=False, always_show=True, leave_on_lcd = False)


def shout(string=None, to_lcd=True, debug=False, is_error=False, always_show=False, leave_on_lcd = False, wait_for_finish=True):
    '''
    Send message to tty1, wall notify-send
    If a raspberry-pi try to write to LCD
    @param string: The string
    @param to_lcd: If raspberry pitry to print to lcd
    @param debug: True = Only print if in development mode
    @param is_error: Is this a error message
    @param always_show: Always show this message
                        If false the sam message within 1 minut will not be shown
    @param leave_on_lcd: Leave the message on the LCD
                         If False the message will disepare after 10 seconds (last permanent message shows) 
    @param wait_for_finish: Wait for the system command to exit
    '''
    if debug==False or development() or always_show:
        global last_shout_message
        global last_shout_time
        global on_ok_callback_method
        global on_err_callback_method
        if string == None or is_error==True:
            is_error = True
            exc_type, exc_value, exc_tb = sys.exc_info()
            ex = traceback.format_exception(exc_type, exc_value, exc_tb)
            if string == None:
                if exc_type==None:
                    string = repr(traceback.format_stack())
                else:
                    string = str(exc_type) + ": " + str(exc_value) +"\n"+str(ex)
            else:
                string = str(string)
                if exc_type==None:
                    string = string + "\n" + repr(traceback.format_stack())
                else:
                    string = string + "\n" + str(exc_type) + ": " + str(exc_value) +"\n"+str(ex)
            del exc_tb
        elif string != None:
            string = str(string)
        do_it = True
        now = time.time()
        if not always_show:
            if last_shout_message != None and last_shout_time != -1:
                diff = now - last_shout_time
                if diff > 60:
                    do_it=True
                elif diff <= 60 and last_shout_message!=string:
                    do_it=True
                else:
                    do_it=False
        if do_it:
            last_shout_time = now
            last_shout_message = string
            execute_system_command_blind(['shout', string], wait_for_finish=wait_for_finish)
            if to_lcd:
                if leave_on_lcd:
                    mestime = 0
                else:
                    mestime = LCD_MESSAGE_TIME
                if get_flag("hdd"):
                    try:
                        steelsquid_pi.hdd44780_write(string, mestime, force_setup = False)
                    except:
                        pass
                elif get_flag("nokia"):
                    try:
                        steelsquid_pi.nokia5110_write(string, mestime, force_setup = False)
                    except:
                        pass
                elif get_flag("ssd"):
                    try:
                        steelsquid_pi.ssd1306_write(string, mestime)
                    except:
                        pass
                elif get_flag("auto"):
                    steelsquid_pi.lcd_auto_write(string, mestime, force_setup = False)
            try:
                if not is_error and on_ok_callback_method!=None:
                    on_ok_callback_method()
                if is_error and on_err_callback_method!=None:
                    on_err_callback_method()
                if get_flag("module_steelsquid_kiss_piio"):
                    import steelsquid_piio
                    if is_error:
                        steelsquid_piio.error_flash(None, 0.1)
                        steelsquid_piio.buz_flash(None, 0.1)
                    else:
                        steelsquid_piio.ok_flash(None, 0.1)
            except:
                pass


def notify(string, attachment=None):
    '''
    Same as shout but also try to send mail with attachment
    '''
    shout(string)
    mail(string, attachment)


def mail(string, attachment=None):
    '''
    Try to send mail message to configured mail
    Also with a file
    '''
    try:
        mail_host = get_parameter("mail_host")
        mail_username = get_parameter("mail_username")
        mail_password = get_parameter("mail_password")
        mail_mail = get_parameter("mail_mail")
        if attachment==None:
            send_mail(mail_host, mail_username, mail_password, "do-not-reply@steelsquid.org", mail_mail, os.popen("hostname").read(), string)
        else:
            send_mail_attachment(mail_host, mail_username, mail_password, "do-not-reply@steelsquid.org", mail_mail, os.popen("hostname").read(), string, attachment)        
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
    for i in range(20):
        output = subprocess.check_output("/sbin/ifconfig eth"+str(i)+" | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
        if len(output) > 4 and "eth" not in output:
            return output
    return "---"


def network_ip_wifi():
    """
    Get network information wifi
    @return: string
    """
    for i in range(20):
        output = subprocess.check_output("/sbin/ifconfig wlan"+str(i)+" | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True, stderr=subprocess.STDOUT).strip('\n')
        if len(output) > 4 and "wlan" not in output:
            return output
    return "---"


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


def network_ip_wan(timeout = 4):
    """
    Get wan ip (internet)
    @return: the ip
    """
    try:
        req = urllib2.Request('http://ipecho.net/plain')
        response = urllib2.urlopen(req, timeout = timeout)
        the_page = response.read()        
        return the_page.strip('\n')
    except:
        return "---"

def network_ip_test_all(timeout = 4):
    """
    Get wan/lan/wifi ip 
    @return: the ip
    """
    ip = network_ip_wan(timeout)
    if ip == "---":
        ip = network_ip()
    return ip
        

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

def send_mail_attachment(smtp_host, username, password, from_mail, to_mail, subject, message, attachment):
    '''
    Send mail with attachment
    '''
    msg = MIMEMultipart()
    msg['Subject'] = subject 
    msg['From'] = from_mail
    msg['To'] = to_mail
    msg.attach(MIMEText(message))
    if isinstance(attachment, (list, tuple)):
        for att in attachment:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(att, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="'+os.path.basename(att)+'"')
            msg.attach(part)
    else:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(attachment, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="'+os.path.basename(attachment)+'"')
        msg.attach(part)

    server = None
    try:
        server = smtplib.SMTP(smtp_host)
        server.starttls()
        if username != None and username != "":
            server.login(username, password)
        server.sendmail(from_mail, to_mail, msg.as_string())    
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
    net = execute_system_command(['net', 'system-status'])
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
        elif get_flag("ssd"):
            p_has_lcd = "Enabled (ssd1306)"

    # Stream
    if get_flag("stream"):
        p_stream = "USB camera"
    elif get_flag("stream-pi"):
        p_stream = "Raspberry PI camera"
    else:
        p_stream = "Disabled"

    # Socket
    if get_flag("socket_server"):
        p_socket = "Server"
    elif has_parameter("socket_client"):
        p_socket = "Client ("+get_parameter("socket_client")+")"
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


    # PIIO Board
    if get_flag("module_steelsquid_kiss_piio"):
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

    #Voltage
    if get_flag("module_steelsquid_kiss_piio"):
        import steelsquid_piio
        p_io_voltage = steelsquid_piio.voltage()
    else:
        p_io_voltage = "---"
        
    return (p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem, p_io_voltage)


def system_info_array():
    '''
    Return system info array
    '''
    p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem, p_io_voltage = system_info()
    return [p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem, p_io_voltage]


def print_system_info():
    '''
    Print system info to screen
    '''
    p_date, p_hostname, p_development, p_boot, p_up, p_users, p_load, p_ip_wired, p_ip_wifi, p_ip_wan, p_access_point, p_cpu, p_cpu_f, p_count, p_temp, p_ram_total, p_ram_free, p_ram_used, p_disk_size, p_disk_used, p_disk_aval, p_gpu_mem, p_log, p_disable_monitor, p_camera, p_timezone, p_keyb, p_web, p_web_local, p_web_https, p_web_aut, p_ssh, p_has_lcd, p_stream, p_socket, p_rover, p_download, p_download_dir, p_io, p_power, p_modem, p_io_voltage = system_info()
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
    print("Clean power off: %s" % p_power)
    print
    print("Steelsquid PIIO Board: %s" % p_io)
    print("Voltage: %s" % p_io_voltage)


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
    Check user and password.
    Im using this bash script instead of PAM.
    If i use python-pam the GPIO.add_event_detect stop working for some reason...
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
        if execute_system_command(["checkuser", user, password]) == ["true"]:
            user=""
            password=""
            cach_credentionals.append(hash_string)
            return True
        else:
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
    broadcast_task_event("umount", [the_type, ip+remote, local])


def mount_sshfs(ip, port, user, password, remote, local):
    '''
    Mount sshfs
    '''
    cmd = "echo %s | sshfs -o allow_other,nodev,nosuid,noexec,noatime,UserKnownHostsFile=/dev/null,StrictHostKeyChecking=no,NumberOfPasswordPrompts=1,password_stdin,umask=077 -p %s %s@%s:%s %s" % (password, port, user, ip, remote, local)
    stdin, stdout_and_stderr = os.popen4(cmd)
    answer = stdout_and_stderr.read()
    if len(answer)>5:
        raise Exception(answer)
    broadcast_task_event("mount", ["ssh", ip+remote, local])


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
    broadcast_task_event("mount", ["samba", ip+remote, local])


def broadcast_task_event(event, parameters_to_event=None):
    '''
    Broadcast a event to the steelsquid daemon (steelsquid program)
    Will first try all system events, like mount, umount, shutdown...
    and then send the event to the modules...
    
    @param event: The event name
    @param parameters_to_event: List of parameters that accompany the event (None or 0 length list if no paramaters)
    '''
    try:
        os.makedirs("/run/shm/steelsquid")
    except:
        pass
    if parameters_to_event != None:
        pa = os.path.join("/run/shm/steelsquid", event)
        f = open(pa, "w")
        try:
            f.write("\n".join(parameters_to_event))
        finally:
            try:
                f.close()
            except:
                pass
    else:
        pa = os.path.join("/run/shm/steelsquid", event)
        f = open(pa, "w")
        try:
            f.write("")
        finally:
            try:
                f.close()
            except:
                pass


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
    interfaces = execute_system_command(['ifconfig'])
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
    cache_flag[flag] = True
    write_to_file(STEELSQUID_FOLDER+"/flags/" + flag, "")
    

def get_flag(flag):
    '''
    Get flag from disk
    This value is stored on disk so it's persist between reboots
    @return: True/False
    '''
    is_set = cache_flag.get(flag, None)
    if is_set == None:
        is_set = os.path.isfile(STEELSQUID_FOLDER+"/flags/" + flag)
        cache_flag[flag] = is_set
        return is_set
    else:
        return is_set
    

def del_flag(flag):
    '''
    Remove flag from disk
    This value is stored on disk so it's persist between reboots
    '''
    cache_flag[flag] = False
    try:
        os.remove(STEELSQUID_FOLDER+"/flags/" + flag)
    except:
        pass


def set_parameter(name, value):
    '''
    Save parameter to disk
    This value is stored on disk so it's persist between reboots
    '''
    value = str(value)
    cache_para[name] = value
    write_to_file(STEELSQUID_FOLDER+"/parameters/" + name, value)
    

def get_parameter(name, default_value=""):
    '''
    Get parameter from disk
    This value is stored on disk so it's persist between reboots
    @return: parameter
    '''
    is_set = cache_para.get(name, None)
    if is_set == None:
        val = read_from_file(STEELSQUID_FOLDER+"/parameters/" + name).replace('\n', '').replace('\r', '')
        if val == "" and default_value != None:
            val = default_value
        cache_para[name] = val
        return val
    else:
        return is_set


def has_parameter(name):
    '''
    Has parameter on disk
    This value is stored on disk so it's persist between reboots
    @return: True/False
    '''
    is_set = cache_para.get(name, None)
    if is_set == None:
        val = read_from_file(STEELSQUID_FOLDER+"/parameters/" + name).replace('\n', '').replace('\r', '')
        cache_para[name] = val
        if val == "":
            return False
        else:
            return True
    elif is_set == "":
        return False
    else:
        return True


def del_parameter(name):
    '''
    Remove parameter from disk
    This value is stored on disk so it's persist between reboots
    '''
    cache_para[name] = ""
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


def set_list(name, list_to_save):
    '''
    Set a list
    This value is stored on disk so it's persist between reboots
    '''
    write_to_file(STEELSQUID_FOLDER+"/lists/" + name, "\n".join(list_to_save))


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
    

def get_list(name, default_value=[]):
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
    if len(array)==0:
        return default_value
    elif len(array) == 1 and array[0] == '':
        return default_value
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


def execute_delay(seconds, function, paramters, name=None, print_error=True, dummy=False):
    '''
    Execute a function after number of seconds
    @param seconds: Delay for this number of seconds
    @param function: Execute this funcyion
    @param paramters: Paramater to the function (tuple)
    @param name: If delay starts within a noter delay with the same name, it will not be executed
    @param name: If delay starts within a noter delay with the same name, it will not be executed
    '''
    global delay_name_list
    try:
        if dummy:
            time.sleep(seconds)
            if name!=None:
                try:
                    delay_name_list.remove(name)
                except:
                    pass
            if isinstance(paramters, tuple):
                function(*paramters)
            else:
                function()
        else:
            if name==None:
                thread.start_new_thread(execute_delay, (seconds, function, paramters, name, print_error, True)) 
            else:
                if not name in delay_name_list:
                    delay_name_list.append(name)
                    thread.start_new_thread(execute_delay, (seconds, function, paramters, name, print_error, True)) 
    except:
        if print_error:
            shout()
        
        
def execute_flash(name, status, seconds, function1, paramters1, function2, paramters2):
    '''
    Execute a 2 functions alternately to to achieve a flashing
    @param name: Give this a name so you can enable or disable it.
    @param status: Start or stop the flashing (None = only flash ones).
    @param seconds: Delay between function execution
    @param function1: First function to execute
    @param paramters1: Paramater to the first function (tuple)
    @param function2: Second function to execute
    @param paramters2: Paramater to the second function (tuple)
    '''
    global flash_name_list
    if status==None and name not in flash_name_list:
        def method_thread():
            try:
                if isinstance(paramters1, tuple):
                    function1(*paramters1)
                else:
                    function1()
                time.sleep(seconds)
                if isinstance(paramters2, tuple):
                    function2(*paramters2)
                else:
                    function2()
            except:
                shout()
        thread.start_new_thread(method_thread, ()) 
    elif status and name not in flash_name_list:
        def method_thread():
            try:
                first_time=True
                while(name in flash_name_list):
                    if first_time:
                        first_time=False
                    else:
                        time.sleep(seconds)
                    if isinstance(paramters1, tuple):
                        function1(*paramters1)
                    else:
                        function1()
                    time.sleep(seconds)
                    if isinstance(paramters2, tuple):
                        function2(*paramters2)
                    else:
                        function2()
            except:
                shout()
        flash_name_list.append(name)
        thread.start_new_thread(method_thread, ()) 
    elif not status:
        try:
            flash_name_list.remove(name)
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
        

def median(data_list):
	'''
	Finds the median in a list of numbers.
	'''
	data_list = map(float, data_list)
	n = len(data_list)
	data_list.sort()
	if n & 1:
		index = n / 2 
		return data_list[index]
	else:
		low_index = n / 2 - 1
		high_index = n / 2
		average = (data_list[low_index] + data_list[high_index]) / 2
		return average


def to_boolean(value):
    '''
    conver a value to boolean
    '''
    if value == None:
        return False
    elif type(value) == types.BooleanType:
        return value
    elif value == 0:
        return False
    elif value == 1:
        return True
    else:
        value = str(value)
        value = value.lower()
        if value == "false" or value == "off" or value == "no" or value == "n" or value == "0":
            return False
        elif value == "true" or value == "on" or value == "yes" or value == "y" or value == "1":
            return True
        else:
            raise RuntimeError("Unable to convert to boolean: " + str(value))


if is_raspberry_pi():
    import steelsquid_pi


def get_hight_byte(integer):
    '''
    Get the hight byte from a int
    '''
    return integer >> 8


def get_low_byte(integer):
    '''
    Get the low byte from a int
    '''
    return integer & 0xFF


def hight_low_byte_to_int(hight_byte, low_byte):
    '''
    Convert low and hight byte to int
    '''
    return (hight_byte << 8) + low_byte


def reverse_byte_order(data):
    '''
    Reverses the byte order of an int (16-bit) or long (32-bit) value
    '''
    byteCount = len(hex(data)[2:].replace('L','')[::2])
    val = 0
    for i in range(byteCount):
        val    = (val << 8) | (data & 0xff)
        data >>= 8
    return val


def split_chunks(arr, chunk_size):
    '''
    Split a array into chunks
    '''
    return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]


def remap( x, oMin, oMax, nMin, nMax ):
    '''
    Convert a number range to another range, maintaining ratio
    '''
    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result


def to_bin(boolean):
    '''
    to 1 and 0 from boolean
    '''
    if boolean:
        return "1"
    else:
        return "0"
        
        
def from_bin(v):
    '''
    to boolean from 1 and 0 
    '''
    if v==1 or v=="1":
        return True
    elif v==0 or v=="0":
        return False
    else:
        raise RuntimeError("Could not convert to boolean: "+ v)    
