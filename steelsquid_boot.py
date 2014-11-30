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
import steelsquid_kiss_socket_expand
import steelsquid_kiss_http_expand
import os.path, pkgutil
import importlib
import run


try:
    import steelsquid_kiss_global
except:
    steelsquid_utils.shout("Fatal error when import steelsquid_kiss_global", is_error=True)

if steelsquid_utils.is_raspberry_pi:
    import steelsquid_pi

if steelsquid_utils.get_flag("io"):
    import steelsquid_io

def print_help():
    '''
    Print help to the screen
    '''
    from steelsquid_utils import printb
    print("")
    printb("DESCRIPTION")
    print("On start, stop")
    print("")
    printb("steelsquid-boot start")
    print("On system start")
    print("")
    printb("steelsquid-boot stop")
    print("On system shutdown")
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
    if steelsquid_utils.is_raspberry_pi() and  steelsquid_utils.get_flag("lcd"):
        try:
            steelsquid_pi.hdd44780_status(False)
        except:
            pass


def on_daily(args, para):
    '''
    Do daily work
    '''
    pass     


def on_vpn(args, para):
    '''
    On vpn up/down
    '''
    stat = para[0]
    name = para[1]
    ip = para[2]
    shout_string = []
    if stat == "up":
        steelsquid_utils.shout("Connected to VPN: " + name + "\nIP: " + ip, False)
    else:
        steelsquid_utils.shout("Disconnected from VPN: " + name, False)
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.get_flag("lcd"):
        try:
            if stat == "up":
                steelsquid_pi.hdd44780_write("VPN: "+name + "\n" + ip, steelsquid_utils.LCD_MESSAGE_TIME)
            else:
                steelsquid_pi.hdd44780_write("Disconnected VPN\n"+name, steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            steelsquid_utils.shout()


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
        shout_string = []
        if access_point != "---":
            shout_string.append("Connected to network: ")
            shout_string.append(access_point)
            shout_string.append("\n")
        if wired != "---":
            shout_string.append("Network Wired IP: ")
            shout_string.append(wired)
            shout_string.append("\n")
        if wifi != "---":
            shout_string.append("Network Wifi IP: ")
            shout_string.append(wifi)
            shout_string.append("\n")
        if wan != "---":
            shout_string.append("Internet IP: ")
            shout_string.append(wan)
        mes = "".join(shout_string)
        steelsquid_utils.shout(mes, to_lcd=False)
        if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.get_flag("lcd"):
            try:
                if wifi != "---":
                    steelsquid_pi.hdd44780_write("Wifi network IP\n"+wifi)
                elif wired != "---":
                    steelsquid_pi.hdd44780_write("Wired network IP \n"+wired)
            except:
                steelsquid_utils.shout()
        do_mount()
    else:
        steelsquid_utils.shout("No network!", to_lcd=False)
        if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.get_flag("lcd"):
            try:
                steelsquid_pi.hdd44780_write("No network!")
            except:
                steelsquid_utils.shout()
        do_umount()



def on_mount(args, para):
    '''
    On ssh, samba, usv or cd mount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("Mount %s %s on %s" %(service, remote, local), False)      
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.get_flag("lcd"):
        try:
            steelsquid_pi.hdd44780_write("Mount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            steelsquid_utils.shout()


def on_umount(args, para):
    '''
    On ssh, samba, usv or cd umount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("Umount %s %s from %s" %(service, remote, local), False)      
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.get_flag("lcd"):
        try:
            steelsquid_pi.hdd44780_write("Umount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            steelsquid_utils.shout()

def on_shout(args, para):
    '''
    Shout message
    '''
    steelsquid_utils.shout(" ".join(para))


def on_button_1():
    steelsquid_event.broadcast_event("button", [1])


def on_button_2():
    steelsquid_event.broadcast_event("button", [2])


def on_button_3():
    steelsquid_event.broadcast_event("button", [3])


def on_button_4():
    steelsquid_event.broadcast_event("button", [4])


def on_dip_1(status):
    steelsquid_event.broadcast_event("dip", [1, status])


def on_dip_2(status):
    steelsquid_event.broadcast_event("dip", [2, status])


def on_dip_3(status):
    steelsquid_event.broadcast_event("dip", [3, status])


def on_dip_4(status):
    steelsquid_event.broadcast_event("dip", [4, status])


def dev_button(args, para):
    steelsquid_utils.shout_time("Button " + str(para[0]) + " pressed!")
    

def dev_dip(args, para):
    steelsquid_utils.shout_time("DIP " + str(para[0]) +": "+ str(para[1]))


def on_shutdown(gpio):
    steelsquid_utils.execute_system_command_blind(['shutdown', '-h', 'now'], wait_for_finish=False)


def import_file_dyn(name):
    try:
        steelsquid_utils.shout("Load run module: " + 'run.'+name, debug=True)
        importlib.import_module('run.'+name)
    except:
        steelsquid_utils.shout("Fatal error when load run module: " + 'run.'+name, is_error=True)


def main():
    '''
    The main function
    '''    
    global running
    try:
        if len(sys.argv) < 2:
            print_help()
        elif sys.argv[1] == "start":
            steelsquid_event.broadcast_event("network", ())
            if steelsquid_utils.is_raspberry_pi():
                try:
                    if steelsquid_utils.get_flag("lcd"):
                        steelsquid_pi.hdd44780_status(True)
                    else:
                        steelsquid_pi.hdd44780_status(False)
                except:
                    pass
            steelsquid_utils.shout("Welcome :-)")
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
                if steelsquid_utils.get_flag("io"):
                    steelsquid_utils.shout("Steelsquid IO board enabled", debug=True)
                    steelsquid_io.button_click(1, on_button_1)
                    steelsquid_io.button_click(2, on_button_2)
                    steelsquid_io.button_click(3, on_button_3)
                    steelsquid_io.button_click(4, on_button_4)
                    steelsquid_io.dip_event(1, on_dip_1)
                    steelsquid_io.dip_event(2, on_dip_2)
                    steelsquid_io.dip_event(3, on_dip_3)
                    steelsquid_io.dip_event(4, on_dip_4)
                if steelsquid_utils.get_flag("power"):
                    steelsquid_utils.shout("Listen for clean shutdown", debug=True)
                    steelsquid_pi.gpio_set_gnd(24, True)
                    steelsquid_pi.gpio_click_gnd(23, on_shutdown)
            if steelsquid_utils.get_flag("download"):
                if steelsquid_utils.get_parameter("download_dir") == "":
                    steelsquid_utils.set_parameter("download_dir", "/home/steelsquid")
                steelsquid_utils.execute_system_command_blind(['steelsquid', 'download-on'], wait_for_finish=False)
            steelsquid_utils.shout("Subscribe to events", debug=True)
            steelsquid_event.subscribe_to_event("shutdown", on_shutdown, ())
            steelsquid_event.subscribe_to_event("daily", on_daily, ())
            steelsquid_event.subscribe_to_event("network", on_network, ())
            steelsquid_event.subscribe_to_event("vpn", on_vpn, ())
            steelsquid_event.subscribe_to_event("mount", on_mount, ())
            steelsquid_event.subscribe_to_event("umount", on_umount, ())
            steelsquid_event.subscribe_to_event("shout", on_shout, ())
            if steelsquid_utils.get_flag("io") and steelsquid_utils.get_flag("development"):
                steelsquid_event.subscribe_to_event("button", dev_button, ())
                steelsquid_event.subscribe_to_event("dip", dev_dip, ())
            pkgpath = os.path.dirname(run.__file__)
            for name in pkgutil.iter_modules([pkgpath]):
                thread.start_new_thread(import_file_dyn, (name[1],)) 
            steelsquid_utils.shout("Listen for events (all is OK)", debug=True)
            steelsquid_event.activate_event_handler(create_ner_thread=False)
        elif sys.argv[1] == "stop":
            steelsquid_utils.shout("Goodbye :-(")
            try:
                steelsquid_pi.hdd44780_status(False)
            except:
                pass
            steelsquid_utils.execute_system_command_blind(["steelsquid-event", "shutdown"])
    except:
        steelsquid_utils.shout()
        os._exit(0)


if __name__ == '__main__':
    main()

