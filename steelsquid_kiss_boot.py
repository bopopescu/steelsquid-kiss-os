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
    event = threading.Event()
else:
    import os


# Is the steelsquid program running
running = True

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
        reload(obj)
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
        steelsquid_utils.shout(mes, leave_on_lcd = True)
        do_mount()
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
            steelsquid_kiss_global.module_status(parameters[0], True, restart=True)
        # Disable a module
        elif command == "module_off":
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
                # Set keyboard to use
                steelsquid_utils.execute_system_command_blind(["steelsquid", "keyboard", steelsquid_utils.get_parameter("keyboard")], wait_for_finish=False)
                # Disable the monitor
                if steelsquid_utils.get_flag("disable_monitor"):
                    steelsquid_utils.execute_system_command_blind(["/opt/vc/bin/tvservice", "-o"], wait_for_finish=False)
                # Listen for shutdown on GPIO
                if steelsquid_utils.has_parameter("power_gpio"):
                    gpio = steelsquid_utils.get_parameter("power_gpio")
                    steelsquid_utils.shout("Listen for clean shutdown on GPIO " + gpio)
                    steelsquid_pi.gpio_click(gpio, poweroff, steelsquid_pi.PULL_DOWN)
                # Enable the download manager
                if steelsquid_utils.get_flag("download"):
                    if steelsquid_utils.get_parameter("download_dir") == "":
                        steelsquid_utils.set_parameter("download_dir", "/root")
                    steelsquid_utils.execute_system_command_blind(['steelsquid', 'download-on'], wait_for_finish=False)
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
                # Init to listen for events
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


if __name__ == '__main__':
    main()

