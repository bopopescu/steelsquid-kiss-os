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
    import sys
    import steelsquid_kiss_global
    import steelsquid_utils
    import threading
    import os
    from subprocess import Popen, PIPE, STDOUT
    from io import TextIOWrapper, BytesIO
    from importlib import import_module
    import steelsquid_utils
    import steelsquid_pi
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
    import steelsquid_tcp_radio
    import socket

    # Is the steelsquid program running
    running = True

    event = threading.Event()
    has_clean = False

    # Radio
    radio_event = threading.Event()
    radio_event_sync = threading.Event()
    last_sync_send = datetime.datetime.now()-datetime.timedelta(days=1)

    force_push = 0

else:
    import steelsquid_utils
    import threading
    import os
    

# Where to look for task events
system_event_dir = "/run/shm/steelsquid"
try:
    os.makedirs(system_event_dir)
except:
    pass
try:
    os.chmod(system_event_dir, 0777)
except:
    pass

        
class Logger(object):
    def write(self, message):
        '''
        Redirect sys.stdout to shout
        '''
        if message != None:
            if len(str(message))>0:
                subprocess.call(["/usr/bin/shout", message])


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
        class_io = steelsquid_kiss_global._get_object(obj, "IO")
        if class_io!=None:
            suppress_error = False
            m = getattr(class_io, "_suppress_error", None)
            if m != None:
                suppress_error = m
            m = getattr(class_io, "on_start", None)
            if m != None:
                m()
            m = getattr(class_io, "reader", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m,class_io,suppress_error,))
            m = getattr(class_io, "reader_1", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m,class_io,suppress_error,))
            m = getattr(class_io, "reader_2", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m,class_io,suppress_error,))
            m = getattr(class_io, "reader_3", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m,class_io,suppress_error,))
            m = getattr(class_io, "reader_4", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m,class_io,suppress_error,))
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
        class_io = steelsquid_kiss_global._get_object(obj, "IO")
        if class_io!=None:
            suppress_error = False
            m = getattr(class_io, "_suppress_error", None)
            if m != None:
                suppress_error = m
            m = getattr(class_io, "on_start", None)
            if m != None:
                m()
            m = getattr(class_io, "reader", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m, class_io, suppress_error,))
            m = getattr(class_io, "reader_1", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m, class_io, suppress_error,))
            m = getattr(class_io, "reader_2", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m, class_io, suppress_error,))
            m = getattr(class_io, "reader_3", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m, class_io, suppress_error,))
            m = getattr(class_io, "reader_4", None)
            if m != None:
                thread.start_new_thread(io_reader_loop, (m, class_io, suppress_error,))
    except:
        steelsquid_utils.shout("Fatal error when reload module: " + obj.__name__, is_error=True)


def io_reader_loop(t_m_obj, class_io, suppress_error):
    '''
    Execute the io reader loop
    '''
    run = 0
    while run != None and run>=0:
        try:
            run = t_m_obj()
            if run!=None and run>0:
                event.wait(run)
                if event.is_set():
                    run=None
        except:
            if not suppress_error:
                steelsquid_utils.shout()
            time.sleep(1)
        


def do_on_loop(t_m_obj):
    '''
    Execute the on_loop functions
    '''
    run = 0
    while run != None and run>=0:
        try:
            run = t_m_obj()
            if run!=None and run>0:
                event.wait(run)
                if event.is_set():
                    run=None
        except:
            steelsquid_utils.shout()
            time.sleep(1)


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


def on_network(net, wired, usb, wifi, access_point, wan):
    '''
    On network update
    '''
    bluetooth = ""
    stat = net=="up"
    no_net_to_lcd = steelsquid_utils.get_flag("no_net_to_lcd")
    steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_network", (stat, wired, usb, access_point, wifi, wan,))
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
            if usb!="---":
                shout_string.append("\nUSB: ")
                shout_string.append(usb)
            if wan != "---":
                shout_string.append("\nWAN: ")
                shout_string.append(wan)
            if len(bluetooth)!=0:
                shout_string.append(bluetooth)
        else:
            if wired!="---":
                shout_string.append("WIRED: ")
                shout_string.append(wired)
                shout_string.append("\n")
            if usb!="---":
                shout_string.append("USB: ")
                shout_string.append(usb)
                shout_string.append("\n")
            if wan != "---":
                shout_string.append("WAN: ")
                shout_string.append(wan)
                shout_string.append("\n")
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


def broadcast_task_event(event, parameters_to_event=None):
    '''
    Broadcast a event to the steelsquid daemon (steelsquid program)
    Will first try all system events, like mount, umount, shutdown...
    and then send the event to the modules...
    
    @param event: The event name
    @param parameters_to_event: List of parameters that accompany the event (None or 0 length list if no paramaters)
    '''
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

def _cleanup():
    '''
    Clean
    '''
    global has_clean
    if not has_clean:
        has_clean = True
        global running
        running = False
        _save_settings()
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
            steelsquid_utils.execute_system_command_blind(["sync"], wait_for_finish=True)
        except:
            steelsquid_utils.shout()
        if steelsquid_utils.get_flag("nrf24_master") or steelsquid_utils.get_flag("nrf24_slave"):
            try:
                steelsquid_nrf24.stop()
            except:
                steelsquid_utils.shout()
        if steelsquid_utils.get_flag("radio_hmtrlrs_server") or steelsquid_utils.get_flag("radio_hmtrlrs_client"):
            try:
                steelsquid_hmtrlrs.stop()
            except:
                pass
                #steelsquid_utils.shout()
        if steelsquid_utils.get_flag("radio_tcp_server") or steelsquid_utils.get_flag("radio_tcp_client"):
            try:
                steelsquid_tcp_radio.close()
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


def _save_settings():
    '''
    Save settings
    '''
    try:
        for obj in steelsquid_kiss_global.loaded_modules.itervalues():
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
        steelsquid_utils.execute_system_command_blind(["sync"], wait_for_finish=True)
    except:
        steelsquid_utils.shout()


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
            _save_settings()
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
            steelsquid_kiss_global.last_lan_ip = steelsquid_utils.network_ip_wired()
            steelsquid_kiss_global.last_usb_ip = steelsquid_utils.network_ip_usb()
            steelsquid_kiss_global.last_wifi_ip = steelsquid_utils.network_ip_wifi()
            if steelsquid_kiss_global.last_wifi_ip != "---":
                try:
                    steelsquid_kiss_global.last_wifi_name = steelsquid_nm.get_connected_access_point_name()
                except:
                    steelsquid_kiss_global.last_wifi_name = "---"
            else:
                steelsquid_kiss_global.last_wifi_name = "---"
            if steelsquid_kiss_global.last_lan_ip == "---" and steelsquid_kiss_global.last_wifi_ip == "---" and steelsquid_kiss_global.last_usb_ip == "---":
                steelsquid_kiss_global.last_net = False
            else:
                steelsquid_kiss_global.last_net = True
                thread.start_new_thread(wan_background_stuff, ())
            if steelsquid_kiss_global.last_net:
                on_network("up", steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_usb_ip, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wan_ip)
            else:
                on_network("down", steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_usb_ip, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wan_ip)
        elif command == "network-wan":
            steelsquid_kiss_global.last_lan_ip = steelsquid_utils.network_ip_wired()
            steelsquid_kiss_global.last_usb_ip = steelsquid_utils.network_ip_usb()
            steelsquid_kiss_global.last_wifi_ip = steelsquid_utils.network_ip_wifi()
            if steelsquid_kiss_global.last_wifi_ip != "---":
                try:
                    steelsquid_kiss_global.last_wifi_name = steelsquid_nm.get_connected_access_point_name()
                except:
                    steelsquid_kiss_global.last_wifi_name = "---"
            else:
                steelsquid_kiss_global.last_wifi_name = "---"
            if steelsquid_kiss_global.last_lan_ip == "---" and steelsquid_kiss_global.last_wifi_ip == "---" and steelsquid_kiss_global.last_usb_ip == "---":
                steelsquid_kiss_global.last_net = False
            else:
                steelsquid_kiss_global.last_net = True
            if steelsquid_kiss_global.last_net:
                on_network("up", steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_usb_ip, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wan_ip)
            else:
                on_network("down", steelsquid_kiss_global.last_lan_ip, steelsquid_kiss_global.last_usb_ip, steelsquid_kiss_global.last_wifi_ip, steelsquid_kiss_global.last_wifi_name, steelsquid_kiss_global.last_wan_ip)
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
        elif command == "xkey":
            the_key = parameters[0]
            steelsquid_kiss_global._execute_all_modules("SYSTEM", "on_xkey", (the_key,))
        # Try to broadcast the event to alla modules
        else:
            steelsquid_kiss_global._execute_all_modules("EVENTS", command, parameters)
    except:
        steelsquid_utils.shout()


def wan_background_stuff():
    '''
    Do wan background stuff thread
    '''
    for i in range(20):
        steelsquid_kiss_global.last_wan_ip = steelsquid_utils.network_ip_wan()
        if steelsquid_kiss_global.last_wan_ip != "---":
            # Execute a network event so the IP is shown
            execute_task_event("network-wan")
            return
        time.sleep(2)


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


def get_radio_data():
    '''
    get_radio_data
    '''
    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
    request = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "REQUEST")
    local = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "LOCAL")
    local_members = []
    for attr in dir(local):
        if not attr.startswith("_"):
            local_members.append(attr)
    remote = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "REMOTE")
    remote_members = []
    for attr in dir(remote):
        if not attr.startswith("_"):
            remote_members.append(attr)
    push_1 = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_1")
    push_1_members = None
    if push_1!=None:
        push_1_members = []
        for attr in dir(push_1):
            if not attr.startswith("_") and not attr=="on_push":
                push_1_members.append(attr)
    push_2 = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_2")
    push_2_members = None
    if push_2!=None:
        push_2_members = []
        for attr in dir(push_2):
            if not attr.startswith("_") and not attr=="on_push":
                push_2_members.append(attr)
    push_3 = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_3")
    push_3_members = None
    if push_3!=None:
        push_3_members = []
        for attr in dir(push_3):
            if not attr.startswith("_") and not attr=="on_push":
                push_3_members.append(attr)
    push_4 = steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_4")
    push_4_members = None
    if push_4!=None:
        push_4_members = []
        for attr in dir(push_4):
            if not attr.startswith("_") and not attr=="on_push":
                push_4_members.append(attr)
    return radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members


def radio_hmtrlrs_client_thread():
    '''
    Start client thread for the HM-TRLR-S transiver
    '''
    try:
        global last_sync_send
        config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
        reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
        hmtrlrs_serial_port = steelsquid_utils.get_parameter("hmtrlrs_serial_port", "/dev/ttyS0")
        steelsquid_hmtrlrs.setup(serial_port=hmtrlrs_serial_port, config_gpio=config_gpio, reset_gpio=reset_gpio, mode=steelsquid_hmtrlrs.MODE_FAST)
        radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
        steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_HMTRLRS)
        if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_HMTRLRS and radio!=None:
            radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
            # Wait for modules to start
            #time.sleep(2)
            while running:
                try:
                    do_sleep = True
                    # The sync, about every second
                    if (datetime.datetime.now() - last_sync_send).total_seconds()>=1:
                        last_sync_send = datetime.datetime.now()
                        # Get local valuest
                        local_values = []
                        for varible in local_members:
                            varible = getattr(local, varible)
                            if isinstance(varible, (bool)):
                                local_values.append(steelsquid_utils.to_bin(varible))
                            else:
                                local_values.append(varible)
                        # Send to server
                        remote_values = steelsquid_hmtrlrs.request_sync(local_values)
                        for i in range(len(remote_members)):
                            name = remote_members[i]
                            varible = getattr(remote, name)
                            value = remote_values[i]
                            if isinstance(varible, (bool)):
                                value = steelsquid_utils.from_bin(value)
                            elif isinstance(varible, int):
                                value = int(value)
                            elif isinstance(varible, float):
                                value = float(value)
                            setattr(remote, name, value)
                        # Execute on_sync method
                        diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                        radio.on_sync(diff.total_seconds())
                    # Execute push
                    sleep = 0.1
                    # Execute the push 1...
                    '''
                    if push_1_members!=None:
                        do_push, sleep = radio.PUSH_1.on_push()
                        if do_push:
                            values = []
                            for variable in push_1_members:
                                variable = getattr(push_1, variable)
                                if isinstance(variable, (bool)):
                                    values.append(steelsquid_utils.to_bin(variable))
                                else:
                                    values.append(variable)
                            steelsquid_hmtrlrs.broadcast_push(1, values)
                    # Execute the push 2...
                    if push_2_members!=None:
                        do_push, sleep = radio.PUSH_2.on_push()
                        if do_push:
                            values = []
                            for variable in push_2_members:
                                variable = getattr(push_2, variable)
                                if isinstance(variable, (bool)):
                                    values.append(steelsquid_utils.to_bin(variable))
                                else:
                                    values.append(variable)
                            steelsquid_hmtrlrs.broadcast_push(2, values)
                    # Execute the push 3...
                    if push_3_members!=None:
                        do_push, sleep = radio.PUSH_3.on_push()
                        if do_push:
                            values = []
                            for variable in push_3_members:
                                variable = getattr(push_3, variable)
                                if isinstance(variable, (bool)):
                                    values.append(steelsquid_utils.to_bin(variable))
                                else:
                                    values.append(variable)
                            steelsquid_hmtrlrs.broadcast_push(3, values)
                    # Execute the push 4...
                    if push_4_members!=None:
                        do_push, sleep = radio.PUSH_4.on_push()
                        if do_push:
                            values = []
                            for variable in push_4_members:
                                variable = getattr(push_4, variable)
                                if isinstance(variable, (bool)):
                                    values.append(steelsquid_utils.to_bin(variable))
                                else:
                                    values.append(variable)
                            steelsquid_hmtrlrs.broadcast_push(4, values)
                    '''
                    radio_event.wait(sleep)
                    radio_event.clear()
                except Exception, err:
                    if running:
                        try:
                            diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                            radio.on_sync(diff.total_seconds())
                        except:
                            steelsquid_utils.shout()
                        radio_event.wait(0.1)
                        radio_event.clear()
    except:
        steelsquid_utils.shout()


def radio_hmtrlrs_server_thread():
    '''
    Start server for the HM-TRLR-S transiver
    '''
    try:
        config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
        reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
        hmtrlrs_serial_port = steelsquid_utils.get_parameter("hmtrlrs_serial_port", "/dev/ttyS0")
        steelsquid_hmtrlrs.setup(serial_port=hmtrlrs_serial_port, config_gpio=config_gpio, reset_gpio=reset_gpio, mode=steelsquid_hmtrlrs.MODE_FAST)
        radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
        if radio!=None:
            steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_HMTRLRS)
            radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
            # Wait for modules to start
            #time.sleep(2)
            while running:
                try:
                    # Listen for request from the client
                    command, data = steelsquid_hmtrlrs.listen()
                    # Execute the on_sync every second
                    if command==None and steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_HMTRLRS:
                        diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                        radio.on_sync(diff.total_seconds())
                    # A Sync or Push
                    elif type(command) == types.IntType and steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_HMTRLRS:
                        # A sync request
                        if command==0:
                            for i in range(len(remote_members)):
                                name = remote_members[i]
                                varible = getattr(remote, name)
                                value = data[i]
                                if isinstance(varible, (bool)):
                                    value = steelsquid_utils.from_bin(value)
                                elif isinstance(varible, int):
                                    value = int(value)
                                elif isinstance(varible, float):
                                    value = float(value)
                                setattr(remote, name, value)
                            answer = []
                            for varible in local_members:
                                varible = getattr(local, varible)
                                if isinstance(varible, (bool)):
                                    answer.append(steelsquid_utils.to_bin(varible))
                                else:
                                    answer.append(varible)
                            # Execute sync
                            steelsquid_hmtrlrs.response_sync(answer)
                            diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                            radio.on_sync(diff.total_seconds())
                        # A push request
                        '''
                        else:
                            p = None
                            if command==1:
                                push_members = push_1_members
                                p = radio.PUSH_1
                            elif command==2:
                                push_members = push_2_members
                                p = radio.PUSH_2
                            elif command==3:
                                push_members = push_3_members
                                p = radio.PUSH_3
                            else:
                                push_members = push_4_members
                                p = radio.PUSH_4
                            for i in range(len(push_members)):
                                name = push_members[i]
                                varible = getattr(p, name)
                                value = data[i]
                                if isinstance(varible, (bool)):
                                    value = steelsquid_utils.from_bin(value)
                                elif isinstance(varible, int):
                                    value = int(value)
                                elif isinstance(varible, float):
                                    value = float(value)
                                setattr(p, name, value)
                            # Execute push
                            p.on_push()
                        '''
                    # Execute a method with the same name as the command i module RADIO class
                    elif command!=None:
                        met = getattr(request, command)
                        try:
                            if data == None:
                                answer = met([])
                                if answer!=None:
                                    steelsquid_hmtrlrs.response(answer)
                            else:
                                answer = met(data)
                                if answer!=None:
                                    steelsquid_hmtrlrs.response(answer)
                        except Exception, e:
                            if running:
                                s = str(e)
                                if chr(16) not in s:
                                    steelsquid_utils.shout()
                                    steelsquid_hmtrlrs.error(e.message)
                except Exception, err:
                    if running:
                        if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_HMTRLRS:
                            try:
                                diff = datetime.datetime.now()-steelsquid_hmtrlrs.last_sync
                                radio.on_sync(diff.total_seconds())
                            except:
                                steelsquid_utils.shout()
    except:
        steelsquid_utils.shout()


def radio_tcp_connection_check():
    '''
    Check connection for tcp radio connection
    I a connection has no communication in 10 seconds, close the connection...it is probably hanged...
    This can happen if the interface on the remote side is disabled...this side will think the connection is still open...and the socket will not throw exception....
    This also execute the syn method
    '''
    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
    steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_TCP)
    if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_TCP and radio!=None:
        radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
        # Max seconds, then close connection
        max_seconds = 10
        command_count = 0
        sync_count = 0
        push_count = [0, 0, 0, 0, 0]
        push = [None, push_1, push_2, push_3, push_4]
        median_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        median_count = 0
        median_value = 0
        # Wait for modules to start
        #time.sleep(4)
        steelsquid_tcp_radio.ping_time=-1
        no = datetime.datetime.now()
        steelsquid_tcp_radio.last_sync = no
        steelsquid_tcp_radio.last_command = no
        steelsquid_tcp_radio.last_push = [no, no, no, no, no, no]
        radio.on_check(-1, -1, -1)
        last_command_time = -1
        while running:
            try:
                last_sync = datetime.datetime.now()
                # Execute the on_sync metod
                radio.on_sync()
                # Check if NTP has update the time
                last_com = steelsquid_tcp_radio.get_last_command()
                do_it = True
                if last_command_time != -1:
                    te = abs(last_com - last_command_time)
                    do_it = te < 10000
                # Execute the on_check metod
                if do_it and steelsquid_kiss_global.seconds_since_start()>10:
                    pt = steelsquid_tcp_radio.get_last_ping_time()
                    median_list[median_count] = pt
                    median_count = median_count + 1
                    if median_count >= 11:
                        median_value = steelsquid_utils.median(median_list)
                        median_count = 0
                    radio.on_check(last_com, pt, median_value)
                else:
                    steelsquid_tcp_radio.ping_time=-1
                    no = datetime.datetime.now()
                    steelsquid_tcp_radio.last_sync = no
                    steelsquid_tcp_radio.last_command = no
                    steelsquid_tcp_radio.last_push = [no, no, no, no, no, no]
                    radio.on_check(-1, -1, -1)
                last_command_time = last_com
                # Do the command connection checks
                if steelsquid_tcp_radio.get_last_command() >= max_seconds:
                    if command_count==0:
                        command_count = command_count + 1 
                        #print "Force disconnect command"
                        steelsquid_tcp_radio.command_disconnect()
                    elif command_count>=max_seconds:
                        command_count=0
                    else:
                        command_count = command_count + 1 
                else:
                    command_count=0
                # Do the sync connection checks
                if steelsquid_tcp_radio.get_last_sync() >= max_seconds:
                    if sync_count==0:
                        sync_count = sync_count + 1 
                        #print "Force disconnect sync"
                        steelsquid_tcp_radio.sync_disconnect()
                    elif sync_count>=max_seconds:
                        sync_count=0
                    else:
                        sync_count = sync_count + 1 
                else:
                    sync_count=0
                # Do the push_1 connection checks
                for nr in range(1, 5):
                    if push[nr]!=None and steelsquid_tcp_radio.get_last_push(nr) >= max_seconds:
                        cou = push_count[nr]
                        if cou==0:
                            push_count[nr] = cou + 1 
                            #print "Force disconnect push_1"
                            steelsquid_tcp_radio.push_disconnect(nr)
                        elif cou>=max_seconds:
                            push_count[nr]=0
                        else:
                            push_count[nr] = cou + 1 
                    else:
                        push_count[nr]=0
            except:
                steelsquid_utils.shout()                
            radio_event_sync.wait(0.5)
            radio_event_sync.clear()


def radio_tcp_command_thread():
    '''
    Listen for command socket connections from client
    '''
    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
    steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_TCP)
    if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_TCP and radio!=None:
        radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
        # Wait for modules to start
        #time.sleep(2)
        # Check if server or client
        while running:
            try:
                # Is this a server or client
                if steelsquid_tcp_radio.is_server():
                    # Listen for connections
                    steelsquid_tcp_radio.command_listen()
                    # Start worker thread with new connection
                    thread.start_new_thread(radio_tcp_command_work, (radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members,))
                else:
                    if not steelsquid_tcp_radio.command_connected():
                        # Try to connect
                        steelsquid_tcp_radio.command_connect()
                    # Connection made...do the work
                    radio_tcp_command_work(radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members)
            except socket.timeout:
                pass
            except:
                steelsquid_tcp_radio.command_disconnect()
                if running:
                    radio_event.wait(0.5)
                    radio_event.clear()


def radio_tcp_command_work(radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members):
    '''
    Do the work
    '''
    try:
        while running:
            try:
                # This is the remote control
                if steelsquid_tcp_radio.is_remote():
                    # Just send ping
                    radio_event.wait(0.5)
                    radio_event.clear()
                    steelsquid_tcp_radio.command_ping()
                # This is the rover
                else:
                    # Read command and execute...then reply with answer
                    command, data = steelsquid_tcp_radio.command_read()
                    has_e = None
                    answer = None
                    try:
                        if command==None:
                            has_e = "CRC error"
                        else:
                            met = getattr(request, command)
                            answer = met(data)
                    except Exception as e:
                        has_e = e.message
                    if has_e == None:
                        # OK response
                        steelsquid_tcp_radio.command_response_ok(answer)                        
                    else:
                        # Error response
                        steelsquid_tcp_radio.command_response_err(has_e)
            except socket.timeout:
                pass
    except:
        steelsquid_tcp_radio.command_disconnect()


def radio_tcp_sync_thread():
    '''
    Listen/send for command socket connections from client
    '''
    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
    steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_TCP)
    if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_TCP and radio!=None:
        radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
        # Wait for modules to start
        #time.sleep(2)
        # Check if server or client
        while running:
            try:
                # Is this a server or client
                if steelsquid_tcp_radio.is_server():
                    # Listen for connections
                    steelsquid_tcp_radio.sync_listen()
                    # Start worker thread with new connection
                    thread.start_new_thread(radio_tcp_sync_work, (radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members,))
                else:
                    if not steelsquid_tcp_radio.sync_connected():
                        # Try to connect
                        steelsquid_tcp_radio.sync_connect()
                    # Connection made...do the work
                    radio_tcp_sync_work(radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members)
            except socket.timeout:
                pass
            except:
                steelsquid_tcp_radio.sync_disconnect()
                if running:
                    # Fire on_sync method
                    radio_event_sync.set()
                    radio_event.wait(0.5)
                    radio_event.clear()


def radio_tcp_sync_work(radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members):
    '''
    Do the work
    '''
    try:
        while running:
            try:
                # This is the remote control
                if steelsquid_tcp_radio.is_remote():
                    # Get local valuest
                    local_data = []
                    for varible in local_members:
                        varible = getattr(local, varible)
                        if isinstance(varible, (bool)):
                            local_data.append(steelsquid_utils.to_bin(varible))
                        else:
                            local_data.append(varible)
                    # Send to host
                    remote_data = steelsquid_tcp_radio.sync_request(local_data)
                    if remote_data != None:
                        # Set the values from host
                        rle = len(remote_members)
                        if len(remote_data) == rle:
                            for i in range(rle):
                                name = remote_members[i]
                                varible = getattr(remote, name)
                                value = remote_data[i]
                                if isinstance(varible, (bool)):
                                    value = steelsquid_utils.from_bin(value)
                                elif isinstance(varible, int):
                                    value = int(value)
                                elif isinstance(varible, float):
                                    value = float(value)
                                setattr(remote, name, value)
                    # Fire on_sync method
                    radio_event_sync.set()
                    # Wait for next sync
                    radio_event.wait(0.5)
                    radio_event.clear()
                # This is the rover
                else:
                    # Read sync...then reply with answer
                    remote_data = steelsquid_tcp_radio.sync_read()
                    if remote_data != None:
                        rle = len(remote_members)
                        if len(remote_data) == rle:
                            # Set
                            for i in range(len(remote_members)):
                                name = remote_members[i]
                                varible = getattr(remote, name)
                                value = remote_data[i]
                                if isinstance(varible, (bool)):
                                    value = steelsquid_utils.from_bin(value)
                                elif isinstance(varible, int):
                                    value = int(value)
                                elif isinstance(varible, float):
                                    value = float(value)
                                setattr(remote, name, value)
                    # Fire on_sync method
                    radio_event_sync.set()
                    # Get
                    local_data = []
                    for varible in local_members:
                        varible = getattr(local, varible)
                        if isinstance(varible, (bool)):
                            local_data.append(steelsquid_utils.to_bin(varible))
                        else:
                            local_data.append(varible)
                    # Reply with data
                    steelsquid_tcp_radio.sync_response(local_data)
            except socket.timeout:
                pass
    except:
        # Fire on_sync method
        radio_event_sync.set()
        steelsquid_tcp_radio.sync_disconnect()
        
        
def radio_tcp_push_thread(nr):
    '''
    Listen/send push messages
    '''
    steelsquid_kiss_global.radio_type = steelsquid_utils.get_parameter("radio_type", steelsquid_kiss_global.TYPE_TCP)
    if steelsquid_kiss_global.radio_type==steelsquid_kiss_global.TYPE_TCP:
        radio, request, local, local_members, remote, remote_members, push_1, push_1_members, push_2, push_2_members, push_3, push_3_members, push_4, push_4_members = get_radio_data()
        if nr == 1:
            push = push_1
            push_members = push_1_members
        elif nr == 2:
            push = push_2
            push_members = push_2_members
        elif nr == 3:
            push = push_3
            push_members = push_3_members
        else:
            push = push_4
            push_members = push_4_members
        # Wait for modules to start
        #time.sleep(2)
        # Check if server or client
        while running:
            try:
                # Is this a server or client
                if steelsquid_tcp_radio.is_server():
                    # Listen for connections
                    steelsquid_tcp_radio.push_listen(nr)
                    # Start worker thread with new connection
                    thread.start_new_thread(radio_tcp_push_work, (nr, push, push_members,))
                else:
                    if not steelsquid_tcp_radio.push_connected(nr):
                        # Try to connect
                        steelsquid_tcp_radio.push_connect(nr)
                    # Connection made...do the work
                    radio_tcp_push_work(nr, push, push_members)
            except socket.timeout:
                pass
            except:
                steelsquid_tcp_radio.push_disconnect(nr)


def radio_tcp_push_work(nr, push, push_members):
    '''
    Do the work
    '''
    global force_push
    try:
        last_p = datetime.datetime.now()
        while running:
            try:
                # This is the remote control
                if steelsquid_tcp_radio.is_remote():
                    do_push = False
                    sleep = 1
                    # Fire on_push method
                    if force_push==0:
                        try:
                            do_push, sleep = push.on_push()
                        except:
                            steelsquid_utils.shout()
                    if do_push or force_push>0:
                        if force_push>0:
                            force_push = force_push - 1
                        ping_count = 0
                        # Get local valuest
                        local_data = []
                        for varible in push_members:
                            varible = getattr(push, varible)
                            if isinstance(varible, (bool)):
                                local_data.append(steelsquid_utils.to_bin(varible))
                            else:
                                local_data.append(varible)
                        # Send to host
                        steelsquid_tcp_radio.push_request(nr, local_data)
                    else:
                        # Send ping every 2 seconds
                        if (datetime.datetime.now() - last_p).total_seconds()>2:
                            last_p = datetime.datetime.now()
                            steelsquid_tcp_radio.push_ping(nr)
                    # sleep
                    time.sleep(sleep)
                # This is the rover
                else:
                    # Read push
                    remote_data = steelsquid_tcp_radio.push_read(nr)
                    if remote_data != None:
                        rle = len(push_members)
                        if len(remote_data) == rle:
                            # Set
                            for i in range(len(push_members)):
                                name = push_members[i]
                                varible = getattr(push, name)
                                value = remote_data[i]
                                if isinstance(varible, (bool)):
                                    value = steelsquid_utils.from_bin(value)
                                elif isinstance(varible, int):
                                    value = int(value)
                                elif isinstance(varible, float):
                                    value = float(value)
                                setattr(push, name, value)
                            # Fire on_push method
                            try:
                                push.on_push()
                            except:
                                steelsquid_utils.shout()
            except socket.timeout:
                pass
    except:
        steelsquid_tcp_radio.push_disconnect(nr)
            
               



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
                # Fix gstreamer
                steelsquid_utils.execute_system_command_blind(["ln", "-s", "-f", "/opt/vc/lib/libGLESv2.s" ,"/usr/lib/arm-linux-gnueabihf/libGLESv2.so.2"], wait_for_finish=False)
                steelsquid_utils.execute_system_command_blind(["ln", "-s", "-f", "/opt/vc/lib/libEGL.so" ,"/usr/lib/arm-linux-gnueabihf/libEGL.so.1"], wait_for_finish=False)
                # Disable powermanagenemt
                steelsquid_utils.execute_system_command_blind(["iwconfig", "wlan0", "power", "off"], wait_for_finish=False)
                # Set keyboard to use
                steelsquid_utils.execute_system_command_blind(["/usr/bin/termfix", steelsquid_utils.get_parameter("keyboard")], wait_for_finish=True)
                # Redirect sys.stdout to shout
                sys.stdout = Logger()
                # Create the task event dir
                steelsquid_utils.make_dirs(system_event_dir)
                # Print welcome message
                steelsquid_utils.shout("Steelsquid Kiss OS "+steelsquid_utils.steelsquid_kiss_os_version()[1], to_lcd=False, wait_for_finish=False)
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
                # Start the modules
                for obj in steelsquid_kiss_global.loaded_modules.itervalues():
                    thread.start_new_thread(import_file_dyn, (obj,))
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
                # Enable HM-TRLR-S as server (the new functionality)
                if steelsquid_utils.get_flag("radio_hmtrlrs_server"):
                    config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
                    reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
                    steelsquid_utils.shout("Enable HM-TRLR-S radio server ("+str(config_gpio)+":"+str(reset_gpio)+")")
                    #thread.start_new_thread(radio_hmtrlrs_server_thread, ())
                # Enable HM-TRLR-S as client (the new functionality)
                elif steelsquid_utils.get_flag("radio_hmtrlrs_client"):
                    config_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_config_gpio", "25"))
                    reset_gpio = int(steelsquid_utils.get_parameter("hmtrlrs_reset_gpio", "23"))
                    steelsquid_utils.shout("Enable HM-TRLR-S radio client ("+str(config_gpio)+":"+str(reset_gpio)+")")
                    #thread.start_new_thread(radio_hmtrlrs_client_thread, ())
                # Enable TCP-radio as server (the new functionality)
                if steelsquid_utils.get_flag("radio_tcp_server"):
                    is_remote = steelsquid_utils.get_flag("radio_tcp_remote")
                    steelsquid_utils.shout("Enable TCP radio server")
                    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
                    if radio==None:
                        steelsquid_utils.shout("Unable to start TCP radio (No radio class in modules)")
                    else:
                        steelsquid_tcp_radio.setup_server(is_remote)                    
                        thread.start_new_thread(radio_tcp_sync_thread, ())
                        thread.start_new_thread(radio_tcp_command_thread, ())
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_1") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (1,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_2") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (2,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_3") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (3,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_4") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (4,))
                        thread.start_new_thread(radio_tcp_connection_check, ())                    
                # Enable TCP-radioas client (the new functionality)
                elif steelsquid_utils.get_flag("radio_tcp_client"):
                    ip = steelsquid_utils.get_parameter("radio_tcp_host", "---")
                    is_remote = steelsquid_utils.get_flag("radio_tcp_remote")
                    steelsquid_utils.shout("Enable TCP radio client ("+ip+")")
                    radio = steelsquid_kiss_global._get_first_modules_class("RADIO")
                    if radio==None:
                        steelsquid_utils.shout("Unable to start TCP radio (No radio class in modules)")
                    else:
                        steelsquid_tcp_radio.setup_client(is_remote, ip)
                        thread.start_new_thread(radio_tcp_sync_thread, ())
                        thread.start_new_thread(radio_tcp_command_thread, ())
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_1") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (1,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_2") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (2,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_3") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (3,))
                        if steelsquid_kiss_global._get_first_modules_inner_class("RADIO", "PUSH_4") != None:
                            thread.start_new_thread(radio_tcp_push_thread, (4,))
                        thread.start_new_thread(radio_tcp_connection_check, ())                    
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
                # Set start time
                steelsquid_kiss_global.start_time = datetime.datetime.now()
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
                except:
                    pass
                try:
                    os.close(fd)
                except:
                    pass
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



