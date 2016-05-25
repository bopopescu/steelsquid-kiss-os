#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This will execute when steelsquid-kiss-os starts.
Execute until system shutdown.
 - Mount and umount drives
 - Start web-server
 - Listening for task events

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''
import sys
if len(sys.argv)==2 and sys.argv[1]=="start":
    from subprocess import Popen, PIPE, STDOUT
    from io import TextIOWrapper, BytesIO
    from importlib import import_module
    import steelsquid_utils
    import steelsquid_kiss_global
    import steelsquid_pi
    import steelsquid_i2c
    import steelsquid_nm
    import steelsquid_kiss_socket_connection
    import steelsquid_kiss_http_server
    import os
    import time
    import thread    
    import getpass
    import subprocess
    import os.path, pkgutil
    import importlib
    import signal
    import modules
    import shlex
    import inotifyx
    import threading
    import steelsquid_nrf24
    import steelsquid_hmtrlrs
    import types    
    import datetime    
else:
    import threading
    import os

# Is the steelsquid program running
running = True

event = threading.Event()
radio_event = threading.Event()    


# Where to look for task events
system_event_dir = "/run/shm/steelsquid"
    
class Logger(object):
    def write(self, message):
        '''
        Redirect sys.stdout to shout
        '''
        if message != None:
            if len(str(message).strip())>0:
                steelsquid_utils.shout(message, always_show=True, to_lcd=False)    


def import_file_dyn(obj):
    '''
    Load custom module
    '''
    try:
        class_settings = steelsquid_kiss_global._get_object(obj, "SETTINGS")
        if class_settings!=None:
            persistent_off=False
            try:
                persistent_off = getattr(class_settings, "_persistent_off")==True
            except:
                pass
            if not persistent_off:
                members = [attr for attr in dir(class_settings) if not callable(getattr(class_settings, attr)) and not attr.startswith("_")]
                for var_name in members:
                    the_var = getattr(class_settings, var_name, None)
                    if isinstance(the_var, (bool)):
                        the_var = steelsquid_utils.get_flag(var_name)
                        setattr(class_settings, var_name, the_var)
                    elif isinstance(the_var, list):
                        the_var = steelsquid_utils.get_list(var_name, the_var)
                        setattr(class_settings, var_name, the_var)
                    elif isinstance(the_var, int):
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, int(the_var))
                    elif isinstance(the_var, float):
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, float(the_var))
                    else:
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, the_var)
        class_system = steelsquid_kiss_global._get_object(obj, "SYSTEM")
        if class_system!=None:
            steelsquid_kiss_global._exec_method_set_started(class_system, "on_start", is_started=True)
            method_event = steelsquid_kiss_global._get_object(class_system, "on_event_data")
            if method_event!=None:
                steelsquid_kiss_global.add_event_data_callback(method_event)
        class_events = steelsquid_kiss_global._get_object(obj, "EVENTS")
        if class_events!=None:
            steelsquid_kiss_global.add_broadcast_event_callback(class_events)
        class_loop = steelsquid_kiss_global._get_object(obj, "LOOP")
        if class_loop!=None:
            for ob in vars(class_loop):
                m = getattr(class_loop, ob, None)
                if callable(m):
                    thread.start_new_thread(do_on_loop, (m,))
    except:
        steelsquid_utils.shout("Fatal error when load module: " +obj.__name__, is_error=True)


def reload_file_dyn(obj):
    '''
    Reload custom module
    '''
    try:
        event.set()
        steelsquid_utils.shout("Reload module: " + obj.__name__)
        class_system = steelsquid_kiss_global._get_object(obj, "SYSTEM")
        if class_system!=None:
            method_event = steelsquid_kiss_global._get_object(class_system, "on_event_data")
            if method_event!=None:
                steelsquid_kiss_global.remove_event_data_callback(method_event)
        class_events = steelsquid_kiss_global._get_object(obj, "EVENTS")
        if class_events!=None:
            steelsquid_kiss_global.remove_broadcast_event_callback(class_events)
        if class_system!=None:
            steelsquid_kiss_global._exec_method_set_started(class_system, "on_stop", is_started=False)
        class_settings = steelsquid_kiss_global._get_object(obj, "SETTINGS")
        if class_settings!=None:
            persistent_off=False
            try:
                persistent_off = getattr(class_settings, "_persistent_off")==True
            except:
                pass
            if not persistent_off:
                members = [attr for attr in dir(class_settings) if not callable(getattr(class_settings, attr)) and not attr.startswith("_")]
                for var_name in members:
                    the_var = getattr(class_settings, var_name, None)
                    if isinstance(the_var, (bool)):
                        if the_var:
                            steelsquid_utils.set_flag(var_name)
                        else:
                            steelsquid_utils.del_flag(var_name)
                    elif isinstance(the_var, list):
                        steelsquid_utils.set_list(var_name, the_var)
                    else:
                        steelsquid_utils.set_parameter(var_name, str(the_var))
        reload(obj)
        class_settings = steelsquid_kiss_global._get_object(obj, "SETTINGS")
        if class_settings!=None:
            persistent_off=False
            try:
                persistent_off = getattr(class_settings, "_persistent_off")==True
            except:
                pass
            if not persistent_off:
                members = [attr for attr in dir(class_settings) if not callable(getattr(class_settings, attr)) and not attr.startswith("_")]
                for var_name in members:
                    the_var = getattr(class_settings, var_name, None)
                    if isinstance(the_var, (bool)):
                        the_var = steelsquid_utils.get_flag(var_name)
                        setattr(class_settings, var_name, the_var)
                    elif isinstance(the_var, list):
                        the_var = steelsquid_utils.get_list(var_name, the_var)
                        setattr(class_settings, var_name, the_var)
                    elif isinstance(the_var, int):
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, int(the_var))
                    elif isinstance(the_var, float):
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, float(the_var))
                    else:
                        the_var = steelsquid_utils.get_parameter(var_name, str(the_var))
                        setattr(class_settings, var_name, the_var)
        class_system = steelsquid_kiss_global._get_object(obj, "SYSTEM")
        if class_system!=None:
            steelsquid_kiss_global._exec_method_set_started(class_system, "on_start", is_started=True)
            method_event = steelsquid_kiss_global._get_object(class_system, "on_event_data")
            if method_event!=None:
                steelsquid_kiss_global.add_event_data_callback(method_event)
        class_events = steelsquid_kiss_global._get_object(obj, "EVENTS")
        if class_events!=None:
            steelsquid_kiss_global.add_broadcast_event_callback(class_events)
        class_loop = steelsquid_kiss_global._get_object(obj, "LOOP")
        event.clear()
        if class_loop!=None:
            for ob in vars(class_loop):
                m = getattr(class_loop, ob, None)
                if callable(m):
                    thread.start_new_thread(do_on_loop, (m,))
    except:
        steelsquid_utils.shout("Fatal error when reload module: " + obj.__name__, is_error=True)

                
def do_on_loop(t_m_obj):
    '''
    Execute the on_loop functions
    '''
    run = 0
    try:
        while run != None and run>=0:
            run = t_m_obj()
            if run!=None and run>0:
                event.wait(run)
                if event.is_set():
                    run=None
    except:
        steelsquid_utils.shout("Fatal error in LOOP", is_error=True)            


def bluetooth_agent():
    '''
    Start the bluetooth_agent (enable pairing)
    '''
    steelsquid_utils.execute_system_command_blind(["hciconfig", "hci0", "piscan"], wait_for_finish=False)
    while True:
        answer = steelsquid_utils.execute_system_command(["hciconfig", "-a"])
        bluetooth = None
        for line in answer:
            if "Name: " in line:
                line = line.replace("Name: '","")
                line = line.replace("'","")
                bluetooth = line
                break
        if bluetooth == None:
            steelsquid_utils.shout("No local bluetooth device found!")
        else:
            steelsquid_utils.shout("Start bluetooth: " + bluetooth)
            steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_bluetooth", (True,))
            execute_task_event("network") 
            try:
                proc=Popen("bluetoothctl", stdout=PIPE, stdin=PIPE, stderr=PIPE)
                proc.stdin.write('power on\n')
                proc.stdin.flush()
                time.sleep(1)
                proc.stdin.write('discoverable on\n')
                proc.stdin.flush()
                time.sleep(1)
                proc.stdin.write('pairable on\n')
                proc.stdin.flush()
                time.sleep(1)
                proc.stdin.write('agent on\n')
                proc.stdin.flush()
                time.sleep(1)
                proc.stdin.write('default-agent\n')
                proc.stdin.flush()
                while True:
                    proc_read = proc.stdout.readline()
                    if proc_read:
                        if "Request PIN code" in proc_read:
                            proc.stdin.write(steelsquid_utils.get_parameter("bluetooth_pin")+"\n")
                            proc.stdin.flush()
            except:
                steelsquid_utils.shout("Error on start bluetoothctl", is_error=True)
        steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_bluetooth", (False,))
        execute_task_event("network")
        time.sleep(20)    


def do_mount():
    '''
    Mount sshfs and samba
    '''
    mount_list = steelsquid_utils.get_list("sshfs")
    for row in mount_list:
        row = row.split("|")
        ip = row[0]
        port = row[1]
        user = row[2]
        password = row[3]
        local = row[4]
        remote = row[5]
        if len(password) > 0 and not steelsquid_utils.is_mounted(local):
            try:
                steelsquid_utils.mount_sshfs(ip, port, user, password, remote, local)
            except:
                steelsquid_utils.shout()
    mount_list = steelsquid_utils.get_list("samba")
    for row in mount_list:
        row = row.split("|")
        ip = row[0]
        user = row[1]
        password = row[2]
        local = row[3]
        remote = row[4]
        if not steelsquid_utils.is_mounted(local):
            try:
                steelsquid_utils.mount_samba(ip, user, password, remote, local)
            except:
                steelsquid_utils.shout()


def do_umount():
    '''
    Umount sshfs and samba
    '''
    mount_list = steelsquid_utils.get_list("sshfs")
    for row in mount_list:
        row = row.split("|")
        ip = row[0]
        local = row[4]
        remote = row[5]
        steelsquid_utils.umount(local, "ssh", ip, remote)
    mount_list = steelsquid_utils.get_list("samba")
    for row in mount_list:
        row = row.split("|")
        ip = row[0]
        local = row[3]
        remote = row[4]
        steelsquid_utils.umount(local, "samba", ip, remote)


def on_network(net, wired, wifi, access_point, wan):
    '''
    On network update
    '''
    bluetooth = ""
    stat = net=="up"
    steelsquid_kiss_global.last_net = stat
    steelsquid_kiss_global.last_lan_ip = wired
    steelsquid_kiss_global.last_wifi_name = access_point
    steelsquid_kiss_global.last_wifi_ip = wifi
    steelsquid_kiss_global.last_wan_ip = wan
    no_net_to_lcd = steelsquid_utils.get_flag("no_net_to_lcd")
    steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_network", (stat, wired, access_point, wifi, wan,))
    if steelsquid_utils.get_flag("bluetooth_pairing"):
        answer = steelsquid_utils.execute_system_command(["hciconfig", "-a"])
        for line in answer:
            if "Name: " in line:
                line = line.replace("Name: '","")
                line = line.replace("'","")
                bluetooth = line
                break
        if bluetooth == "":
            bluetooth = "\nBT: No local device"
        else:
            bluetooth = "\nBT:" + bluetooth
    if net == "up":            
        shout_string = []
        if access_point != "---":
            shout_string.append("WIFI: ")
            shout_string.append(access_point)
            shout_string.append("\n")
            shout_string.append(wifi)
            if wired!="---":
                shout_string.append("\nWIRED: ")
                shout_string.append(wired)
            if wan != "---":
                shout_string.append("\nWAN: ")
                shout_string.append(wan)
            if len(bluetooth)!=0:
                shout_string.append(bluetooth)
        else:
            shout_string.append("WIRED: ")
            shout_string.append(wired)
            if wan != "---":
                shout_string.append("\nWAN: ")
                shout_string.append(wan)
            if len(bluetooth)!=0:
                shout_string.append(bluetooth)
        if steelsquid_kiss_global.is_module_enabled("kiss_piio"):
            shout_string.append("\nVOLTAGE: ")
            import steelsquid_piio
            shout_string.append(str(steelsquid_piio.volt(2, 4)))
            shout_string.append("\n")
        mes = "".join(shout_string)
        if no_net_to_lcd:
            steelsquid_utils.shout(mes, to_lcd=False)
        else:
            steelsquid_utils.shout(mes, leave_on_lcd = True)
        do_mount()
    else:
        if no_net_to_lcd:
            if len(bluetooth)==0:
                steelsquid_utils.shout("No network!", to_lcd=False)
            else:
                steelsquid_utils.shout("No network!"+bluetooth, to_lcd=False)
        else:
            if len(bluetooth)==0:
                steelsquid_utils.shout("No network!", leave_on_lcd = True)
            else:
                steelsquid_utils.shout("No network!"+bluetooth, leave_on_lcd = True)
        do_umount()

            
def poweroff(gpio=None):
    '''
    Power of the system
    Send command to OS
    '''
    steelsquid_utils.execute_system_command_blind(['shutdown', '-h', 'now'], wait_for_finish=False)
        
        
def shutdown():
    '''
    Shutdown the system
    Terminate this program
    Use this from within this program
    '''
    broadcast_task_event("stop")
    

def _cleanup():
    '''
    Clean
    '''
    global running
    running = False
    event.set()
    try:
        for obj in steelsquid_kiss_global.loaded_modules.itervalues():
            class_system = steelsquid_kiss_global._get_object(obj, "SYSTEM")
            if class_system!=None:
                method_event = steelsquid_kiss_global._get_object(class_system, "on_event_data")
                if method_event!=None:
                    steelsquid_kiss_global.remove_event_data_callback(method_event)
            class_events = steelsquid_kiss_global._get_object(obj, "EVENTS")
            if class_events!=None:
                steelsquid_kiss_global.remove_broadcast_event_callback(class_events)
            if class_system!=None:
                steelsquid_kiss_global._exec_method_set_started(class_system, "on_stop", is_started=False)
            class_settings = steelsquid_kiss_global._get_object(obj, "SETTINGS")
            if class_settings!=None:
                persistent_off=False
                try:
                    persistent_off = getattr(class_settings, "_persistent_off")==True
                except:
                    pass
                if not persistent_off:
                    members = [attr for attr in dir(class_settings) if not callable(getattr(class_settings, attr)) and not attr.startswith("_")]
                    for var_name in members:
                        the_var = getattr(class_settings, var_name, None)
                        if isinstance(the_var, (bool)):
                            if the_var:
                                steelsquid_utils.set_flag(var_name)
                            else:
                                steelsquid_utils.del_flag(var_name)
                        elif isinstance(the_var, list):
                            steelsquid_utils.set_list(var_name, the_var)
                        else:
                            steelsquid_utils.set_parameter(var_name, str(the_var))
    except:
        steelsquid_utils.shout()
    if steelsquid_utils.get_flag("nrf24_master") or steelsquid_utils.get_flag("nrf24_slave"):
        try:
            steelsquid_nrf24.stop()
        except:
            steelsquid_utils.shout()
    if steelsquid_utils.get_flag("hmtrlrs_server") or steelsquid_utils.get_flag("hmtrlrs_client"):
        try:
            steelsquid_hmtrlrs.stop()
        except:
            steelsquid_utils.shout()
    if steelsquid_utils.get_flag("socket_connection"):
        try:
            steelsquid_kiss_global.socket_connection.stop()
        except:
            pass
    if steelsquid_utils.get_flag("web"):
        try:
            steelsquid_kiss_global.http_server.stop_server()
        except:
            pass
    steelsquid_utils.execute_system_command_blind(['killall', 'aria2c'])
    steelsquid_utils.shout("Goodbye :-(")


def read_task_event(the_file):
    '''
    Read a task event from system_event_dir
    '''
    try:
        f = open(system_event_dir+"/"+the_file, "r")
        array = f.read().split('\n')
        if len(array)>0 and array[0]!="":
            parameters = tuple(array)
        else:
            parameters = None
        execute_task_event(the_file, parameters)
    except:
        steelsquid_utils.shout()
    finally:
        try:
            f.close()
        except:
            pass              
        steelsquid_utils.deleteFileOrFolder(system_event_dir+"/"+the_file)


def execute_task_event(command, parameters=None):
    '''
    Execute a task event
    command= The command to execute
    parameters= Tuple with the parameters
    '''
    thread.start_new_thread(task_event_thread, (command, parameters)) 


def task_event_thread(command, parameters=None):
    '''
    execute a event
    '''
    try:
        # Shutdown the system
        if command == "shutdown" or command == "stop":
            global running
            running = False
            event.set()
        # Enable a module
        elif command == "module_on":
            if len(parameters)>1:
                steelsquid_kiss_global.module_status(parameters[0], True, argument=parameters[1], restart=True)
            else:
                steelsquid_kiss_global.module_status(parameters[0], True, restart=True)
        # Disable a module
        elif command == "module_off":
            if len(parameters)>1:
                steelsquid_kiss_global.module_status(parameters[0], False, argument=parameters[1], restart=True)
            else:
                steelsquid_kiss_global.module_status(parameters[0], False, restart=True)
        # Set or del flag
        elif command == "flag":
            if parameters[0]=="set":
                steelsquid_utils.set_flag(parameters[1])
            elif parameters[0]=="del":
                steelsquid_utils.del_flag(parameters[1])
        # Set or del parameter
        elif command == "parameter":
            if parameters[0]=="set":
                steelsquid_utils.set_parameter(parameters[1], parameters[2])
            elif parameters[0]=="del":
                steelsquid_utils.del_parameter(parameters[1])
        # Reload modules
        elif command == "reload":
            if parameters!=None:
                for name, obj in steelsquid_kiss_global.loaded_modules.iteritems():
                    if name == parameters[0]:
                        thread.start_new_thread(reload_file_dyn, (obj,))
            else:
                for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                    thread.start_new_thread(reload_file_dyn, (obj,))
            # Execute a network event so the IP is shown
            execute_task_event("network")
        # Shout
        elif command == "shout":
            steelsquid_utils.shout(" ".join(parameters))
        # VPN event
        elif command == "vpn":
            if parameters[0] == "up":
                name = "unknown"
                try:
                    name = steelsquid_nm.vpn_configured()
                except:
                    pass
                ip = steelsquid_utils.network_ip_vpn()
                steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_vpn", (True, name, ip,))
                steelsquid_utils.shout("VPN ENABLED\n"+name + "\nIP\n" + ip)
            else:
                steelsquid_utils.shout("VPN DISABLED")
                steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_vpn", (False, None, None,))
        # Network event
        elif command == "network":
            wired = steelsquid_utils.network_ip_wired()
            wifi = steelsquid_utils.network_ip_wifi()
            wan = "---"
            net = "---"
            access = "---"
            if wired == "---" and wifi == "---":
                net = "down"
            else:
                net = "up"
                wan = steelsquid_utils.network_ip_wan()
            if wifi != "---":
                try:
                    access = steelsquid_nm.get_connected_access_point_name()
                except:
                    pass
            on_network(net, wired, wifi, access, wan)
        elif command == "mount":
            the_type = parameters[0]
            the_remote = parameters[1]
            the_local = parameters[2]
            steelsquid_utils.shout("MOUNT %s\n%s\nTO\n%s" %(the_type, the_remote, the_local))
            steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_mount", (the_type, the_remote, the_local))
        elif command == "umount":
            the_type = parameters[0]
            the_remote = parameters[1]
            the_local = parameters[2]
            steelsquid_utils.shout("UMOUNT %s\n%s\nFROM\n%s" %(the_type, the_remote, the_local))
            steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_umount", (the_type, the_remote, the_local))
        # Try to broadcast the event to alla modules
        else:
            steelsquid_kiss_global._execute_all_modules("EVENTS", command, parameters)    
    except:
        steelsquid_utils.shout()


def nrf24_server_thread():
    '''
    Start server for the NRF24L01 radio transiver
    '''
    while running:
        try:
            # Listen for request from the client
            command, data = steelsquid_nrf24.listen(timeout=2)
            if command!=None:
                # Execute a method with the sam ename as the command i module RADIO class
                try:
                    answer = steelsquid_kiss_global._execute_first_modules_and_return("RADIO", command, (data,))
                    steelsquid_nrf24.response(answer)
                except Exception, e:
                    steelsquid_nrf24.error(e.message)
        except:
            if running:
                steelsquid_utils.shout()


def nrf24_slave_thread():
    '''
    Start slave thread for the NRF24L01 radio transiver
    listen for data from the master and execute method in RADIO class
    '''
    while running:
        try:
            # Listen for data from master
            data = steelsquid_nrf24.receive(timeout=2)
            if data!=None:
                # Execute method on_receive in module RADIO class
                steelsquid_kiss_global._execute_first_modules_and_return("RADIO", "on_receive", (data,))
        except:
            steelsquid_utils.shout()


def nrf24_callback(command):
    '''
    Master get a command from the slave
    '''
    try:
        # Execute method on_receive in module RADIO class
        com = command.split("|")
        if len(com)>1:
            steelsquid_kiss_global._execute_first_modules_and_return("RADIO", com[0], (com[1:],))
        else:
            steelsquid_kiss_global._execute_first_modules_and_return("RADIO", com[0], ([],))
    except:
        steelsquid_utils.shout()
    


def broadcast_task_event(event, parameters_to_event=None):
    '''
    Broadcast a event to the steelsquid daemon (steelsquid program)
    Will first try all system events, like mount, umount, shutdown...
    and then send the event to the modules...
    
    @param event: The event name
    @param parameters_to_event: List of parameters that accompany the event (None or 0 length list if no paramaters)
    '''
    try:
        os.makedirs(system_event_dir)
    except:
        pass
    if parameters_to_event != None:
        pa = os.path.join(system_event_dir, event)
        f = open(pa, "w")
        try:
            f.write("\n".join(parameters_to_event))
        finally:
            try:
                f.close()
            except:
                pass
    else:
        pa = os.path.join(system_event_dir, event)
        f = open(pa, "w")
        try:
            f.write("")
        finally:
            try:
                f.close()
            except:
                pass


def hmtrlrs_client_thread():
    '''
    Start client thread for the HM-TRLR-S transiver 
    '''
    sync_class = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC")
    if sync_class!=None:
        sync_class_client = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC", "CLIENT")
        sync_class_client_members = [attr for attr in dir(sync_class_client) if not attr.startswith("_")]
        sync_class_server = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC", "SERVER")
        sync_class_server_members = [attr for attr in dir(sync_class_server) if not attr.startswith("_")]
    push_classes = []
    pc = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_1")
    if pc!=None:
        members = [attr for attr in dir(pc) if attr!="on_push" and not attr.startswith("_")]
        push_classes.append([1, pc, members])
    pc = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_2")
    if pc!=None:
        members = [attr for attr in dir(pc) if attr!="on_push" and not attr.startswith("_")]
        push_classes.append([2, pc, members])
    pc = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_3")
    if pc!=None:
        members = [attr for attr in dir(pc) if attr!="on_push" and not attr.startswith("_")]
        push_classes.append([3, pc, members])
    pc = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_4")
    if pc!=None:
        members = [attr for attr in dir(pc) if attr!="on_push" and not attr.startswith("_")]
        push_classes.append([4, pc, members])
    # nothing to do...stop thread...
    if sync_class==None and push_classes[0]==None and push_classes[1]==None and push_classes[2]==None and push_classes[3]==None:
        return
    while running:
        do_sleep = True
        # Execute the push...
        for pc in push_classes:
            push_class_nr = pc[0]
            push_class = pc[1]
            members = pc[2]
            try:
                # Check if send the push
                do_push = False
                try:
                    do_push = push_class.on_push()
                except:
                    if running:
                        steelsquid_utils.shout()
                # Send push broadcast
                if do_push:
                    values = []
                    for name in members:
                        member = getattr(push_class, name)
                        if isinstance(member, (bool)):
                            values.append(steelsquid_utils.to_bin(member))
                        else:
                            values.append(member)
                    steelsquid_hmtrlrs.broadcast_push(push_class_nr, values)
                    do_sleep = False
            except:
                pass
        # The sync
        if sync_class != None:
            # Execute about every second
            if steelsquid_kiss_global.radio_count >= steelsquid_kiss_global.radio_count_max:
                steelsquid_kiss_global.radio_count = 0
                do_sleep = False
                try:
                    # Get Client valuest
                    client_values = []
                    for name in sync_class_client_members:
                        member = getattr(sync_class_client, name)
                        if isinstance(member, (bool)):
                            client_values.append(steelsquid_utils.to_bin(member))
                        else:
                            client_values.append(member)
                    # Send to server
                    server_values = steelsquid_hmtrlrs.request_sync(client_values)
                    i = 0
                    for name in sync_class_server_members:
                        v_local = getattr(sync_class_server, name)
                        v_server = server_values[i]
                        if isinstance(v_local, (bool)):
                            v_server = steelsquid_utils.from_bin(v_server)
                        elif isinstance(v_local, int):
                            v_server = int(v_server)
                        elif isinstance(v_local, float):
                            v_server = float(v_server)
                        setattr(sync_class_server, name, v_server)
                        i = i + 1
                except:
                    pass
                # Execute on_sync method
                try:
                    diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                    sync_class.on_sync(diff.total_seconds())
                except:
                    if running:
                        steelsquid_utils.shout()
            elif not do_sleep:
                steelsquid_kiss_global.radio_count = steelsquid_kiss_global.radio_count + 2
            else:
                steelsquid_kiss_global.radio_count = steelsquid_kiss_global.radio_count + 1
        if do_sleep:
            radio_event.wait(0.01)



def hmtrlrs_server_thread():
    '''
    Start server for the HM-TRLR-S transiver 
    '''
    push_class_1 = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_1")
    if push_class_1!=None:
        members_class_1 = [attr for attr in dir(push_class_1) if attr!="on_push" and not attr.startswith("_")]
    push_class_2 = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_2")
    if push_class_2!=None:
        members_class_2 = [attr for attr in dir(push_class_2) if attr!="on_push" and not attr.startswith("_")]
    push_class_3 = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_3")
    if push_class_3!=None:
        members_class_3 = [attr for attr in dir(push_class_3) if attr!="on_push" and not attr.startswith("_")]
    push_class_4 = steelsquid_kiss_global._get_first_modules_class("RADIO_PUSH_4")
    if push_class_4!=None:
        members_class_4 = [attr for attr in dir(push_class_4) if attr!="on_push" and not attr.startswith("_")]
    sync_class = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC")
    if sync_class!=None:
        sync_class_client = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC", "CLIENT")
        sync_class_client_members = [attr for attr in dir(sync_class_client) if not attr.startswith("_")]
        sync_class_server = steelsquid_kiss_global._get_first_modules_class("RADIO_SYNC", "SERVER")
        sync_class_server_members = [attr for attr in dir(sync_class_server) if not attr.startswith("_")]
    while running:
        try:
            # Listen for request from the client
            command, data = steelsquid_hmtrlrs.listen()
            # Execute the on_sync every second
            if command==None:
                if sync_class!=None:
                    diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                    sync_class.on_sync(diff.total_seconds())
            else:
                # A Sync or Push
                if type(command) == types.IntType:
                    # A sync request
                    if sync_class!=None and command==0:
                        i = 0
                        for name in sync_class_client_members:
                            v_local = getattr(sync_class_client, name)
                            v_client = data[i]
                            if isinstance(v_local, (bool)):
                                v_client = steelsquid_utils.from_bin(v_client)
                            elif isinstance(v_local, int):
                                v_client = int(v_client)
                            elif isinstance(v_local, float):
                                v_client = float(v_client)
                            setattr(sync_class_client, name, v_client)
                            i = i + 1
                        values = []
                        for name in sync_class_server_members:
                            member = getattr(sync_class_server, name)
                            if isinstance(member, (bool)):
                                values.append(steelsquid_utils.to_bin(member))
                            else:
                                values.append(member)
                        diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                        try:
                            sync_class.on_sync(diff.total_seconds())
                        except:
                            if running:
                                steelsquid_utils.shout()
                        steelsquid_hmtrlrs.response_sync(values)
                    # A push broadcast
                    else:
                        push_class= None
                        if push_class_1!=None and command==1:
                            push_class = push_class_1
                            members = members_class_1
                        if push_class_2!=None and command==2:
                            push_class = push_class_2
                            members = members_class_2
                        if push_class_3!=None and command==3:
                            push_class = push_class_3
                            members = members_class_3
                        if push_class_4!=None and command==4:
                            push_class = push_class_4
                            members = members_class_4
                        if push_class!=None:
                            i = 0
                            for name in members:
                                old = getattr(push_class, name)
                                if isinstance(old, (bool)):
                                     setattr(push_class, name, steelsquid_utils.from_bin(data[i]))
                                elif isinstance(old, int):
                                    setattr(push_class, name, int(data[i]))
                                elif isinstance(old, float):
                                    setattr(push_class, name, float(data[i]))
                                else:
                                    setattr(push_class, name, data[i])
                                i = i + 1
                            push_class.on_push()
                else:
                    # Execute a method with the same name as the command i module RADIO class
                    try:
                        if data == None:
                            answer = steelsquid_kiss_global._execute_first_modules_and_return("RADIO", command, ([],))
                            if answer!=None:
                                steelsquid_hmtrlrs.response(answer)
                        else:
                            answer = steelsquid_kiss_global._execute_first_modules_and_return("RADIO", command, (data,))
                            if answer!=None:
                                steelsquid_hmtrlrs.response(answer)
                    except Exception, e:
                        if running:
                            steelsquid_utils.shout()
                            steelsquid_hmtrlrs.error(e.message)
        except:
            if running:
                steelsquid_utils.shout()


def main():
    '''
    The main function
    '''    
    try:
        if len(sys.argv) < 2: 
            print_help()
        else:
            command = sys.argv[1]
            # Start the system
            if command == "start":
                # Set keyboard to use
                steelsquid_utils.execute_system_command_blind(["/usr/bin/termfix", steelsquid_utils.get_parameter("keyboard")], wait_for_finish=True)
                # Redirect sys.stdout to shout
                sys.stdout = Logger()
                # Create the task event dir 
                steelsquid_utils.make_dirs(system_event_dir)
                # Print welcome message
                steelsquid_utils.shout("Steelsquid Kiss OS "+steelsquid_utils.steelsquid_kiss_os_version()[1], to_lcd=False, wait_for_finish=False)
                # Use locking on the I2C bus
                if steelsquid_utils.get_flag("i2c_lock"):
                    steelsquid_i2c.enable_locking(True)
                else:
                    steelsquid_i2c.enable_locking(False)
                # Disable the monitor
                if steelsquid_utils.get_flag("disable_monitor"):
                    steelsquid_utils.execute_system_command_blind(["/opt/vc/bin/tvservice", "-o"], wait_for_finish=False)
                # Listen for shutdown on GPIO
                if steelsquid_utils.has_parameter("power_gpio"):
                    gpio = steelsquid_utils.get_parameter("power_gpio")
                    steelsquid_utils.shout("Listen for clean shutdown on GPIO " + gpio)
                    steelsquid_pi.gpio_click(gpio, poweroff, steelsquid_pi.PULL_DOWN)
                # Load all modules
                pkgpath = os.path.dirname(modules.__file__)
                for name in pkgutil.iter_modules([pkgpath]):
                    if steelsquid_utils.get_flag("module_"+name[1]):
                        steelsquid_utils.shout("Load module: " +name[1], debug=True)    
                        n = name[1]
                        steelsquid_kiss_global.loaded_modules[n]=import_module('modules.'+n)
                # Enable the download manager
                if steelsquid_utils.get_flag("download"):
                    if steelsquid_utils.get_parameter("download_dir") == "":
                        steelsquid_utils.set_parameter("download_dir", "/root")
                    steelsquid_utils.execute_system_command_blind(['steelsquid', 'download-on'], wait_for_finish=False)
                # Enable NRF24L01+ as server
                if steelsquid_utils.get_flag("nrf24_server"):
                    steelsquid_utils.shout("Enable NRF24L01+ server")
                    steelsquid_nrf24.server()
                    thread.start_new_thread(nrf24_server_thread, ())
                # Enable NRF24L01+ as client
                elif steelsquid_utils.get_flag("nrf24_client"):
                    steelsquid_utils.shout("Enable NRF24L01+ client")
                    steelsquid_nrf24.client()
                # Enable NRF24L01+ as master
                if steelsquid_utils.get_flag("nrf24_master"):
                    steelsquid_utils.shout("Enable NRF24L01+ master")
                    steelsquid_nrf24.master(nrf24_callback)
                # Enable NRF24L01+ as slave
                elif steelsquid_utils.get_flag("nrf24_slave"):
                    steelsquid_utils.shout("Enable NRF24L01+ slave")
                    steelsquid_nrf24.slave()
                    thread.start_new_thread(nrf24_slave_thread, ())
                # Enable HM-TRLR-S as server
                if steelsquid_utils.get_flag("hmtrlrs_server"):
                    config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
                    reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
                    steelsquid_utils.shout("Enable HM-TRLR-S server")
                    steelsquid_hmtrlrs.setup(config_gpio=config_gpio, reset_gpio=reset_gpio)
                    thread.start_new_thread(hmtrlrs_server_thread, ())
                # Enable HM-TRLR-S as client
                elif steelsquid_utils.get_flag("hmtrlrs_client"):
                    config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
                    reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
                    steelsquid_utils.shout("Enable HM-TRLR-S client")
                    steelsquid_hmtrlrs.setup(config_gpio=config_gpio, reset_gpio=reset_gpio)
                    thread.start_new_thread(hmtrlrs_client_thread, ())
                # Start the modules
                for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                    thread.start_new_thread(import_file_dyn, (obj,)) 
                # Enable the webserver
                if steelsquid_utils.get_flag("web"):
                    port = None
                    if steelsquid_utils.has_parameter("web_port"):
                        port = steelsquid_utils.get_parameter("web_port")
                    steelsquid_kiss_global.http_server = steelsquid_kiss_http_server.SteelsquidKissHttpServer(port, steelsquid_utils.STEELSQUID_FOLDER+"/web/", steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_local"), steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_https"))
                    for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                        if hasattr(obj, "WEB"):
                            steelsquid_kiss_global.http_server.external_objects.append(getattr(obj, "WEB"))
                    steelsquid_kiss_global.http_server.start_server()
                # Enable the socket server as server
                if steelsquid_utils.get_flag("socket_server"):
                    steelsquid_kiss_global.socket_connection = steelsquid_kiss_socket_connection.SteelsquidKissSocketConnection(True)
                    for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                        if hasattr(obj, "SOCKET"):
                            steelsquid_kiss_global.socket_connection.external_objects.append(getattr(obj, "SOCKET"))
                    steelsquid_kiss_global.socket_connection.start()
                # Enable the socket server as client
                elif steelsquid_utils.has_parameter("socket_client"):
                    steelsquid_kiss_global.socket_connection = steelsquid_kiss_socket_connection.SteelsquidKissSocketConnection(False, steelsquid_utils.get_parameter("socket_client"))
                    for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                        if hasattr(obj, "SOCKET"):
                            steelsquid_kiss_global.socket_connection.external_objects.append(getattr(obj, "SOCKET"))
                    steelsquid_kiss_global.socket_connection.start()
                # Enable the bluetooth
                if steelsquid_utils.get_flag("bluetooth_pairing"):
                    if not steelsquid_utils.has_parameter("bluetooth_pin"):
                        steelsquid_utils.set_parameter("bluetooth_pin", "1234")
                    thread.start_new_thread(bluetooth_agent, ()) 
                fd = inotifyx.init()
                inotifyx.add_watch(fd, system_event_dir, inotifyx.IN_CLOSE_WRITE)
                # Execute a network event so the IP is shown
                execute_task_event("network")
                # Delete old stop eventa and execute others...
                for f in os.listdir(system_event_dir):
                    if f=="stop" or f=="shutdown":
                        steelsquid_utils.deleteFileOrFolder(system_event_dir+"/"+f)
                    else:
                        read_task_event(f)
                # Listen for events
                try:
                    while running:
                        events = inotifyx.get_events(fd)
                        for event in events:
                            read_task_event(event.name)
                except KeyboardInterrupt:
                    pass
                os.close(fd)
                _cleanup()
                # Delete old eventa
                for f in os.listdir(system_event_dir):
                    steelsquid_utils.deleteFileOrFolder(system_event_dir+"/"+f)
            # Broadcast the event
            else:
                if len(sys.argv)>2:
                    broadcast_task_event(command, sys.argv[2:])
                else:
                    broadcast_task_event(command)
    except:
        steelsquid_utils.shout("Fatal error when on boot steelsquid service", is_error=True)
        os._exit(0)


def print_help():
    '''
    Print help to the screen
    '''
    from steelsquid_utils import printb
    print("")
    printb("DESCRIPTION")
    print("Start and stop the Steelsquid daemon")
    print("Also send task events (send event to the steelsquid daemon from other task)")
    print("")
    printb("steelsquid-boot start")
    print("Start the deamon")
    print("")
    printb("steelsquid-boot stop")
    printb("steelsquid-boot shutdown")
    print("Stop the daemon")
    print("")
    printb("steelsquid-boot <event>")
    printb("event <event>")
    print("Broadcast event without parameters")
    print("")
    printb("steelsquid-boot <event> <parameter1> <parameter2>...")
    printb("event <event> <parameter1> <parameter2>...")
    print("Broadcast event with paramaters")
    print("")
    print("\n")



