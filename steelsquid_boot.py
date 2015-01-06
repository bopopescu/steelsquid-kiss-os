#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

'''
This will execute when steelsquid-kiss-os starts.
Execute until system shutdown.
 - Mount and umount drives
 - Monitor ssh
 - Start web-server
 - Start event handler
@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''
import sys
import steelsquid_event
import steelsquid_utils
import os
import time
import thread    
import getpass
from subprocess import Popen, PIPE, STDOUT
import subprocess
import os.path, pkgutil
import importlib
import run


try:
    import steelsquid_kiss_global
except:
    steelsquid_utils.shout("Fatal error when import steelsquid_kiss_global", is_error=True)


try:
    import steelsquid_kiss_socket_expand
except:
    steelsquid_utils.shout("Fatal error when import steelsquid_kiss_socket_expand", is_error=True)


try:
    import steelsquid_kiss_http_expand
except:
    steelsquid_utils.shout("Fatal error when import steelsquid_kiss_http_expand", is_error=True)


if steelsquid_utils.is_raspberry_pi:
    try:
        import steelsquid_pi
    except:
        steelsquid_utils.shout("Fatal error when import steelsquid_pi", is_error=True)


if steelsquid_utils.get_flag("piio"):
    try:
        import steelsquid_piio
    except:
        steelsquid_utils.shout("Fatal error when import steelsquid_piio", is_error=True)


def print_help():
    '''
    Print help to the screen
    '''
    from steelsquid_utils import printb
    print("")
    printb("DESCRIPTION")
    print("Start and stop the Steelsquid daemon")
    print("")
    printb("steelsquid-boot start")
    print("Start the deamon")
    print("")
    printb("steelsquid-boot stop")
    print("Stop the daemon")
    print("\n")
    

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


def on_mount(args, para):
    '''
    On ssh, samba, usv or cd mount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("MOUNT %s\n%s\nTO\n%s" %(service, remote, local))


def on_umount(args, para):
    '''
    On ssh, samba, usv or cd umount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("UMOUNT %s\n%s\nFROM\n%s" %(service, remote, local))
                

def on_vpn(args, para):
    '''
    On vpn up/down
    '''
    stat = para[0]
    name = para[1]
    ip = para[2]
    shout_string = []
    if stat == "up":
        steelsquid_utils.shout("VPN ENABLED\n"+name + "\nIP\n" + ip)
    else:
        steelsquid_utils.shout("VPN DISABLED\n"+name)


def on_network(args, para):
    '''
    On network update
    '''
    net = para[0]
    wired = para[1]
    wifi = para[2]
    access_point = para[3]
    wan = para[4]
    if net == "up":
        try:
            shout_string = []
            if access_point != "---":
                shout_string.append("WIFI\n")
                shout_string.append(access_point)
                shout_string.append("\n")
                shout_string.append(wifi)
                if wan != "---":
                    shout_string.append("\nWAN IP\n")
                    shout_string.append(wan)
            else:
                shout_string.append("WIRED\n")
                shout_string.append(wired)
                if wan != "---":
                    shout_string.append("\nWAN IP\n")
                    shout_string.append(wan)
            mes = "".join(shout_string)
            steelsquid_utils.shout(mes, leave_on_lcd = True)
        except:
            steelsquid_utils.shout()
        do_mount()
    else:
        steelsquid_utils.shout("No network!", leave_on_lcd = True)
        do_umount()


def on_shutdown(args, para):
    '''
    Shutdown system
    '''
    steelsquid_utils.shout("Goodbye :-(")
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
    steelsquid_event.deactivate_event_handler()


def on_shout(args, para):
    '''
    Shout message
    '''
    steelsquid_utils.shout(" ".join(para))


def on_button_up(address, pin):
    steelsquid_event.broadcast_event("button", [steelsquid_piio.BUTTON_UP])


def on_button_down(address, pin):
    steelsquid_event.broadcast_event("button", [steelsquid_piio.BUTTON_DOWN])


def on_button_left(address, pin):
    steelsquid_event.broadcast_event("button", [steelsquid_piio.BUTTON_LEFT])


def on_button_right(address, pin):
    steelsquid_event.broadcast_event("button", [steelsquid_piio.BUTTON_RIGHT])


def on_button_select(address, pin):
    steelsquid_event.broadcast_event("button", [steelsquid_piio.BUTTON_SELECT])


def on_dip_1(address, pin, status):
    steelsquid_event.broadcast_event("dip", [1, status])


def on_dip_2(address, pin, status):
    steelsquid_event.broadcast_event("dip", [2, status])


def on_dip_3(address, pin, status):
    steelsquid_event.broadcast_event("dip", [3, status])


def on_dip_4(address, pin, status):
    steelsquid_event.broadcast_event("dip", [4, status])


def dev_button(args, para):
    bu = int(para[0])
    if bu == steelsquid_piio.BUTTON_UP:
        steelsquid_utils.shout_time("Button UP pressed!")
    elif bu == steelsquid_piio.BUTTON_DOWN:
        steelsquid_utils.shout_time("Button DOWN pressed!")
    elif bu == steelsquid_piio.BUTTON_LEFT:
        steelsquid_utils.shout_time("Button LEFT pressed!")
    elif bu == steelsquid_piio.BUTTON_RIGHT:
        steelsquid_utils.shout_time("Button RIGHT pressed!")
    elif bu == steelsquid_piio.BUTTON_SELECT:
        steelsquid_utils.shout_time("Button SELECT pressed!")
    

def dev_dip(args, para):
    steelsquid_utils.shout_time("DIP " + str(para[0]) +": "+ str(para[1]))


def on_shutdown_button(gpio):
    on_shutdown(None, None)
    steelsquid_utils.execute_system_command_blind(['shutdown', '-h', 'now'], wait_for_finish=False)


def import_file_dyn(name):
    try:
        steelsquid_utils.shout("Load custom module: " + 'run.'+name, debug=True)
        importlib.import_module('run.'+name)
    except:
        steelsquid_utils.shout("Fatal error when load custom module: " + 'run.'+name, is_error=True)


def reload_file_dyn(name):
    try:
        steelsquid_utils.shout("Reload custom module: " + 'run.'+name)
        the_lib = importlib.import_module('run.'+name)
        reload(the_lib)
    except:
        steelsquid_utils.shout("Fatal error when reload custom module: " + 'run.'+name, is_error=True)


def on_reload(args, para):
    if para[0] == "server":
        if steelsquid_utils.get_flag("web"):
            try:
                steelsquid_kiss_global.http_server.stop_server()
                steelsquid_utils.shout("Restart steelsquid_kiss_http_expand", debug=True)
                reload(steelsquid_kiss_http_expand)
                steelsquid_kiss_global.http_server = steelsquid_kiss_http_expand.SteelsquidKissExpandHttpServer(None, steelsquid_utils.STEELSQUID_FOLDER+"/web/", steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_local"), steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_https"))
                steelsquid_kiss_global.http_server.start_server()
            except:
                steelsquid_utils.shout("Fatal error when restart steelsquid_kiss_http_expand", is_error=True)
        if steelsquid_utils.get_flag("socket_connection"):
            try:
                steelsquid_kiss_global.socket_connection.stop()
                steelsquid_utils.shout("Restart steelsquid_kiss_socket_expand", debug=True)
                reload(steelsquid_kiss_socket_expand)
                steelsquid_kiss_global.socket_connection = steelsquid_kiss_socket_expand.SteelsquidKissSocketExpand(True)
                steelsquid_kiss_global.socket_connection.start()
            except:
                steelsquid_utils.shout("Fatal error when sestart steelsquid_kiss_socket_expand", is_error=True)
    elif para[0] == "custom":
        pkgpath = os.path.dirname(run.__file__)
        for name in pkgutil.iter_modules([pkgpath]):
            thread.start_new_thread(reload_file_dyn, (name[1],))
    

def enable_rover():
    '''
    Enable the rover functionality
    '''    
    import steelsquid_piio
    steelsquid_piio.servo_position = steelsquid_utils.get_parameter("servo_position", steelsquid_piio.servo_position)
    steelsquid_piio.servo_position_max = steelsquid_utils.get_parameter("servo_position_max", steelsquid_piio.servo_position_max)
    steelsquid_piio.servo_position_min = steelsquid_utils.get_parameter("servo_position_min", steelsquid_piio.servo_position_min)
    steelsquid_piio.motor_forward = steelsquid_utils.get_parameter("motor_forward", steelsquid_piio.motor_forward)
    steelsquid_piio.motor_backward = steelsquid_utils.get_parameter("motor_backward", steelsquid_piio.motor_backward)
    steelsquid_piio.servo(1, steelsquid_piio.servo_position)                


def main():
    '''
    The main function
    '''    
    try:
        if len(sys.argv) < 2: 
            print_help()
        elif sys.argv[1] == "start":
            steelsquid_utils.execute_system_command_blind(["steelsquid", "keyboard", steelsquid_utils.get_parameter("keyboard")], wait_for_finish=False)
            steelsquid_utils.shout("Steelsquid Kiss OS "+steelsquid_utils.steelsquid_kiss_os_version()[1], False)
            if steelsquid_utils.get_flag("web"):
                try:
                    steelsquid_utils.shout("Start steelsquid_kiss_http_expand", debug=True)
                    steelsquid_kiss_global.http_server = steelsquid_kiss_http_expand.SteelsquidKissExpandHttpServer(None, steelsquid_utils.STEELSQUID_FOLDER+"/web/", steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_local"), steelsquid_utils.get_flag("web_authentication"), steelsquid_utils.get_flag("web_https"))
                    steelsquid_kiss_global.http_server.start_server()
                except:
                    steelsquid_utils.shout("Fatal error when start steelsquid_kiss_http_expand", is_error=True)
            if steelsquid_utils.get_flag("socket_connection"):
                try:
                    steelsquid_utils.shout("Start steelsquid_kiss_socket_expand", debug=True)
                    steelsquid_kiss_global.socket_connection = steelsquid_kiss_socket_expand.SteelsquidKissSocketExpand(True)
                    steelsquid_kiss_global.socket_connection.start()
                except:
                    steelsquid_utils.shout("Fatal error when start steelsquid_kiss_socket_expand", is_error=True)
            if steelsquid_utils.is_raspberry_pi():
                if steelsquid_utils.get_flag("disable_monitor"):
                    steelsquid_utils.execute_system_command_blind(["/opt/vc/bin/tvservice", "-o"])
                if steelsquid_utils.get_flag("piio"):
                    steelsquid_utils.shout("Steelsquid IO board enabled", debug=True)
                    steelsquid_piio.button_click(steelsquid_piio.BUTTON_UP, on_button_up)
                    steelsquid_piio.button_click(steelsquid_piio.BUTTON_DOWN, on_button_down)
                    steelsquid_piio.button_click(steelsquid_piio.BUTTON_LEFT, on_button_left)
                    steelsquid_piio.button_click(steelsquid_piio.BUTTON_RIGHT, on_button_right)
                    steelsquid_piio.button_click(steelsquid_piio.BUTTON_SELECT, on_button_select)
                    steelsquid_piio.dip_event(1, on_dip_1)
                    steelsquid_piio.dip_event(2, on_dip_2)
                    steelsquid_piio.dip_event(3, on_dip_3)
                    steelsquid_piio.dip_event(4, on_dip_4)
                if steelsquid_utils.get_flag("power"):
                    steelsquid_utils.shout("Listen for clean shutdown", debug=True)
                    steelsquid_pi.gpio_set_gnd(24, True)
                    steelsquid_pi.gpio_click_gnd(23, on_shutdown_button)
            if steelsquid_utils.get_flag("download"):
                if steelsquid_utils.get_parameter("download_dir") == "":
                    steelsquid_utils.set_parameter("download_dir", "/home/steelsquid")
                steelsquid_utils.execute_system_command_blind(['steelsquid', 'download-on'], wait_for_finish=False)
            steelsquid_utils.shout("Subscribe to events", debug=True)
            steelsquid_event.subscribe_to_event("shutdown", on_shutdown, ())
            steelsquid_event.subscribe_to_event("network", on_network, ())
            steelsquid_event.subscribe_to_event("vpn", on_vpn, ())
            steelsquid_event.subscribe_to_event("mount", on_mount, ())
            steelsquid_event.subscribe_to_event("umount", on_umount, ())
            steelsquid_event.subscribe_to_event("shout", on_shout, ())
            steelsquid_event.subscribe_to_event("reload", on_reload, ())
            if steelsquid_utils.get_flag("piio") and steelsquid_utils.get_flag("development"):
                steelsquid_event.subscribe_to_event("button", dev_button, ())
                steelsquid_event.subscribe_to_event("dip", dev_dip, ())
            if steelsquid_utils.get_flag("rover"):
                enable_rover()
            pkgpath = os.path.dirname(run.__file__)
            for name in pkgutil.iter_modules([pkgpath]):
                thread.start_new_thread(import_file_dyn, (name[1],)) 
            steelsquid_utils.shout("Listen for events", debug=True)
            steelsquid_event.broadcast_event("network", ())
            steelsquid_event.activate_event_handler(create_ner_thread=False)
        elif sys.argv[1] == "stop":
            steelsquid_utils.shout("Goodbye :-(")
            try:
                steelsquid_pi.hdd44780_status(False)
            except:
                pass
            steelsquid_utils.execute_system_command_blind(["steelsquid-event", "shutdown"])
    except:
        steelsquid_utils.shout("Fatal error when on boot steelsquid service", is_error=True)
        os._exit(0)


if __name__ == '__main__':
    main()

