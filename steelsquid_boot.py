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
@license: GNU General Public License
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
import steelsquid_kiss_global


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
    Mount
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
                pass
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
                pass


def do_umount():
    '''
    Mount
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


def do_ssh():
    '''
    Start ssh server
    '''
    global connected_ip
    try:
        try:
            os.mkdir("/var/run/sshd")
        except:
            pass              
        try:
            steelsquid_utils.write_to_file("/var/log/lastlog", "")
        except:
            pass              
        if not steelsquid_utils.get_flag("ssh_key_generated"):
            steelsquid_utils.shout("Generate SSH keys...")
            steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'ssh-keys'])         
        port = steelsquid_utils.get_parameter("ssh_port")
        if port == "":
            steelsquid_utils.set_parameter("ssh_port", "22")
            port="22"
        if steelsquid_utils.get_flag("ssh_openssh"):
            openssh = True
            cmd = ["sudo", "/usr/sbin/sshd", "-D", "-e"]
        else:
            cmd = ['sudo', '/usr/sbin/dropbear', '-d', '/etc/dropbear/dropbear_dss_host_key', '-r', '/etc/dropbear/dropbear_rsa_host_key', '-p', port, '-W', '65536', '-w', '-E', '-F', '-m']
            openssh = False
        steelsquid_utils.shout("SSH port "+port)
        openssh_ok_string = "Accepted password for "
        dropbear_ok_string = "Password auth succeeded for '"
        while True:
            steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'ssh-kill'])         
            time.sleep(1)
            proc=Popen(cmd, stdout = PIPE, stderr = STDOUT)  
            answer = []
            for line in iter(proc.stdout.readline, b''):
                line = line.strip('\n')
                if openssh_ok_string in line or dropbear_ok_string in line:
                    sline = line.split(" ")
                    last_was_from = False
                    the_user = "---"
                    for word in sline:
                        if last_was_from:
                            the_user = word.strip('\'')
                            last_was_from=False
                        elif "for" in word:
                            last_was_from=True
                        else:
                            word = word.split(":")[0]
                            if steelsquid_utils.is_ip(word):
                                steelsquid_event.broadcast_event("login", [True, word, the_user])
                                break
                else:
                    sline = line.split(" ")
                    last_was_from = False
                    the_user = "---"
                    for word in sline:
                        if last_was_from:
                            the_user = word.strip('\'')
                            last_was_from=False
                        elif "for" in word:
                            last_was_from=True
                        else:
                            word = word.split(":")[0]
                            if word != "0.0.0.0" and steelsquid_utils.is_ip(word):
                                steelsquid_event.broadcast_event("login", [False, word, the_user])
                                break
            proc.wait()
    except:
        steelsquid_utils.shout()


def on_button_shutdown(gpio):
    on_shutdown(None, None)
    if not steelsquid_utils.get_flag("development"):
        steelsquid_utils.execute_system_command_blind(['sudo', 'shutdown', '-h', 'now'])


def on_shutdown(args, para):
    '''
    Shutdown system
    '''
    try:
        steelsquid_kiss_global.socket_connection.stop()
    except:
        pass
    global server
    steelsquid_utils.execute_system_command_blind(['killall', 'aria2c'])
    steelsquid_utils.shout("Goodbye :-(")
    try:
        import steelsquid_pi
        steelsquid_pi.lcd_off()
    except:
        pass
    steelsquid_event.deactivate_event_handler()
    if not steelsquid_utils.get_flag("disable_web"):
        try:
            steelsquid_kiss_global.http_server.stop_server()
        except:
            pass

def on_daily(args, para):
    '''
    Do daily work
    '''
    try:
        steelsquid_utils.execute_system_command(['sudo', 'steelsquid', 'trim'])         
    except:
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
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.is_root():
        try:
            import steelsquid_pi
            if stat == "up":
                if steelsquid_utils.get_flag("lcd_direct"):
                    steelsquid_pi.lcd_write_text("VPN: "+name + "\n" + ip, steelsquid_utils.LCD_MESSAGE_TIME, is_i2c=False)
                elif steelsquid_utils.get_flag("lcd_i2c"):
                    steelsquid_pi.lcd_write_text("VPN: "+name + "\n" + ip, steelsquid_utils.LCD_MESSAGE_TIME)
            else:
                if steelsquid_utils.get_flag("lcd_direct"):
                    steelsquid_pi.lcd_write_text("Disconnected VPN\n"+name, steelsquid_utils.LCD_MESSAGE_TIME, is_i2c=False)
                elif steelsquid_utils.get_flag("lcd_i2c"):
                    steelsquid_pi.lcd_write_text("Disconnected VPN\n"+name, steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            pass


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
        
        rows, columns = steelsquid_utils.console_size()
        steelsquid_utils.console_white()
        steelsquid_utils.console_location(rows-4, 0)
        steelsquid_utils.console_write(mes)
        
        if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.is_root():
            try:
                import steelsquid_pi
                if wifi != "---":
                    if steelsquid_utils.get_flag("lcd_direct"):
                        steelsquid_pi.lcd_write_text("Wifi network IP\n"+wifi, is_i2c=False)
                    elif steelsquid_utils.get_flag("lcd_i2c"):
                        steelsquid_pi.lcd_write_text("Wifi network IP\n"+wifi)
                elif wired != "---":
                    if steelsquid_utils.get_flag("lcd_direct"):
                        steelsquid_pi.lcd_write_text("Wired network IP \n"+wired, is_i2c=False)
                    elif steelsquid_utils.get_flag("lcd_i2c"):
                        steelsquid_pi.lcd_write_text("Wired network IP \n"+wired)
            except:
                pass
        do_mount()
    else:
        steelsquid_utils.shout("No network!", to_lcd=False)

        rows, columns = steelsquid_utils.console_size()
        steelsquid_utils.console_white()
        steelsquid_utils.console_location(rows-4, 0)
        steelsquid_utils.console_write("No network!")

        if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.is_root():
            try:
                import steelsquid_pi
                if steelsquid_utils.get_flag("lcd_direct"):
                    steelsquid_pi.lcd_write_text("No network!", is_i2c=False)
                elif steelsquid_utils.get_flag("lcd_i2c"):
                    steelsquid_pi.lcd_write_text("No network!")
            except:
                pass
        do_umount()


def on_priv(args, para):
    '''
    Execute when system drop or not drop privilege
    '''
    steelsquid_event.broadcast_event("network", ())


def on_login(args, para):
    '''
    Ban a ip
    '''
    status = para[0]
    ip = para[1]
    user = para[2]
    if status == True:
        steelsquid_utils.shout("%s logged in from\n%s" %(user, ip))      
    else:
        steelsquid_utils.firewall_deny(ip)
        steelsquid_utils.notify("%s failed login, banning\n%s" %(user, ip))      


def on_mount(args, para):
    '''
    On ssh, samba, usv or cd mount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("Mount %s %s on %s" %(service, remote, local), False)      
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.is_root():
        try:
            import steelsquid_pi
            if steelsquid_utils.get_flag("lcd_direct"):
                steelsquid_pi.lcd_write_text("Mount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME, is_i2c=False)
            elif steelsquid_utils.get_flag("lcd_i2c"):
                steelsquid_pi.lcd_write_text("Mount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            pass


def on_umount(args, para):
    '''
    On ssh, samba, usv or cd umount
    '''
    service = para[0]
    remote = para[1]
    local = para[2]
    steelsquid_utils.shout("Umount %s %s from %s" %(service, remote, local), False)      
    if steelsquid_utils.is_raspberry_pi() and steelsquid_utils.is_root():
        try:
            import steelsquid_pi
            if steelsquid_utils.get_flag("lcd_direct"):
                steelsquid_pi.lcd_write_text("Umount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME, is_i2c=False)
            elif steelsquid_utils.get_flag("lcd_i2c"):
                steelsquid_pi.lcd_write_text("Umount %s \n%s" %(remote, local), steelsquid_utils.LCD_MESSAGE_TIME)
        except:
            pass

def on_shout(args, para):
    '''
    Shout message
    '''
    steelsquid_utils.shout(" ".join(para))


def login():
    '''
    Handle login
    '''
    while True:
        if (steelsquid_utils.get_flag("autologin")):
            if (steelsquid_utils.get_flag("desktop")):
                try:
                    #os.system("sudo nice --10 su -c \"xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null\" steelsquid")
                    if (steelsquid_utils.is_root()):
                        os.system("su -c \"xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null\" steelsquid")
                    else:
                        os.system("xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null")
                except:
                    pass
            else:
                try:
                    os.system("sudo /sbin/agetty -i -a steelsquid tty2")
                    os.system("sudo /bin/chvt 2")
                except:
                    pass
        else:
            rows, columns = steelsquid_utils.console_size()

            steelsquid_utils.console_clear()
            steelsquid_utils.console_black()
            steelsquid_utils.console_bold(True)

            text = []
            text.append("███████ ████████ ███████ ███████ ██      ███████  ██████  ██    ██ ██ ██████ ")
            text.append("██         ██    ██      ██      ██      ██      ██    ██ ██    ██ ██ ██   ██")
            text.append("███████    ██    █████   █████   ██      ███████ ██    ██ ██    ██ ██ ██   ██")
            text.append("     ██    ██    ██      ██      ██           ██ ██ ▄▄ ██ ██    ██ ██ ██   ██")
            text.append("███████    ██    ███████ ███████ ███████ ███████  ██████   ██████  ██ ██████ ")
            text.append("                                                     ▀▀                      ")
            text.append("██   ██ ██ ███████ ███████      ██████  ███████")
            text.append("██  ██  ██ ██      ██          ██    ██ ██     ")
            text.append("█████   ██ ███████ ███████     ██    ██ ███████")
            text.append("██  ██  ██      ██      ██     ██    ██      ██")
            text.append("██   ██ ██ ███████ ███████      ██████  ███████")
            text.append("")
            text.append("┌┬┐┬ ┬┌─┐┌─┐  ┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐┬─┐┌┬┐    ┌─┐┬─┐┌─┐┌─┐┌─┐  ┌─┐┌┐┌┌┬┐┌─┐┬─┐")
            text.append(" │ └┬┘├─┘├┤   ├─┘├─┤└─┐└─┐││││ │├┬┘ ││    ├─┘├┬┘├┤ └─┐└─┐  ├┤ │││ │ ├┤ ├┬┘")
            text.append(" ┴  ┴ ┴  └─┘  ┴  ┴ ┴└─┘└─┘└┴┘└─┘┴└──┴┘ ┘  ┴  ┴└─└─┘└─┘└─┘  └─┘┘└┘ ┴ └─┘┴└─")
            text.append("")
            text.append("")
            text.append("")
            text.append("")
            text.append("")
            text.append("")
            text.append("")
            steelsquid_utils.console_write_center(text, rows, columns)
            steelsquid_event.broadcast_event("network", ())
            loop=True
            while loop:
                steelsquid_utils.console_white()
                steelsquid_utils.console_location(((rows-20)/2)+16, (columns/2)-23)
                steelsquid_utils.console_write("Nothing will appear on the screen while typing.")
                pw = getpass.getpass(prompt='')
                if pw=="kill!":
                    on_shutdown(None, None)
                else:
                    is_ok = steelsquid_utils.authenticate("steelsquid", pw)
                    if is_ok:
                        if (steelsquid_utils.get_flag("desktop")):
                            try:
                                #os.system("sudo nice --10 su -c \"xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null\" steelsquid")
                                if (steelsquid_utils.is_root()):
                                    os.system("su -c \"xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null\" steelsquid")
                                else:
                                    os.system("xinit /usr/bin/jwm -- -nolisten tcp -quiet vt1 > /dev/null 2> /dev/null")
                            except:
                                pass
                        else:
                            try:
                                os.system("sudo chvt 2")
                                os.system("sudo /sbin/agetty -i -a steelsquid tty2")
                            except:
                                pass
                            os.system("sudo chvt 1")
                        loop=False
                    else:
                        steelsquid_utils.console_location(((rows-20)/2)+16, (columns/2)-24)
                        steelsquid_utils.console_write("           The password is incorrect!           ")
                        time.sleep(4)


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


def main():
    '''
    The main function
    '''    
    import subprocess
    global running
    global server
    try:
        if len(sys.argv) < 2:
            print_help()
        elif sys.argv[1] == "start" or sys.argv[1] == "root":
            if steelsquid_utils.get_flag("socket_connection"):
                import steelsquid_kiss_socket_expand
                steelsquid_kiss_global.socket_connection = steelsquid_kiss_socket_expand.SteelsquidKissSocketExpand(True)
                steelsquid_kiss_global.socket_connection.start()
            thread.start_new_thread(login, ()) 
            steelsquid_utils.firewall_clear()
            steelsquid_utils.execute_system_command_blind(steelsquid_utils.STEELSQUID_FOLDER+"/nullit")
            if steelsquid_utils.is_raspberry_pi():
                import steelsquid_pi
                if steelsquid_utils.get_flag("disable_monitor"):
                    steelsquid_utils.execute_system_command_blind(["/opt/vc/bin/tvservice", "-o"])
                if steelsquid_utils.get_flag("lcd_direct"):
                    steelsquid_pi.gpio_set_gnd(14, False)
                else:
                    steelsquid_pi.gpio_set_gnd(14, True)
                if steelsquid_utils.is_root():
                    import steelsquid_pi_board
                    steelsquid_pi_board.button_click(1, on_button_1)
                    steelsquid_pi_board.button_click(2, on_button_2)
                    steelsquid_pi_board.button_click(3, on_button_3)
                    steelsquid_pi_board.button_click(4, on_button_4)
                    steelsquid_pi_board.dip_event(1, on_dip_1)
                    steelsquid_pi_board.dip_event(2, on_dip_2)
                    steelsquid_pi_board.dip_event(3, on_dip_3)
                    steelsquid_pi_board.dip_event(4, on_dip_4)
            steelsquid_utils.shout("Welcome :-)")
            try:
                import steelsquid_kiss_http_expand
                if not steelsquid_utils.get_flag("disable_web"):
                    if steelsquid_utils.get_parameter("web_port") == "":
                        steelsquid_utils.set_parameter("web_port", "80")
                    steelsquid_kiss_global.http_server = steelsquid_kiss_http_expand.SteelsquidKissExpandHttpServer(int(steelsquid_utils.get_parameter("web_port")), steelsquid_utils.STEELSQUID_FOLDER+"/web/", not steelsquid_utils.get_flag("web_no_password"), steelsquid_utils.get_flag("local_web"), steelsquid_utils.get_flag("local_web_password"), True, steelsquid_utils.get_flag("use_https"), False)
                    steelsquid_kiss_global.http_server.start_server()
            except:
                steelsquid_utils.shout()
            if not steelsquid_utils.get_flag("disable_ssh"):
                if not steelsquid_utils.get_flag("development"):
                    thread.start_new_thread(do_ssh, ()) 
            if steelsquid_utils.get_flag("download"):
                if steelsquid_utils.get_parameter("download_dir") == "":
                    steelsquid_utils.set_parameter("download_dir", "/home/steelsquid")
                steelsquid_utils.execute_system_command_blind(['sudo', 'steelsquid', 'download-on'], wait_for_finish=False)
            steelsquid_event.subscribe_to_event("shutdown", on_shutdown, ())
            steelsquid_event.subscribe_to_event("daily", on_daily, ())
            steelsquid_event.subscribe_to_event("network", on_network, ())
            steelsquid_event.subscribe_to_event("vpn", on_vpn, ())
            steelsquid_event.subscribe_to_event("login", on_login, ())
            steelsquid_event.subscribe_to_event("mount", on_mount, ())
            steelsquid_event.subscribe_to_event("umount", on_umount, ())
            steelsquid_event.subscribe_to_event("shout", on_shout, ())
            if steelsquid_utils.get_flag("development"):
                steelsquid_event.subscribe_to_event("button", dev_button, ())
                steelsquid_event.subscribe_to_event("dip", dev_dip, ())
            if sys.argv[1] != "root" and not steelsquid_utils.get_flag("root"):
                steelsquid_event.subscribe_to_event("drop", on_priv, ())
                steelsquid_event.activate_event_handler(create_ner_thread=False, max_countt=32, drop_privilegee=True)
            else:
                steelsquid_event.subscribe_to_event("keep", on_priv, ())
                steelsquid_event.activate_event_handler(create_ner_thread=False, max_countt=32, drop_privilegee=False)
        elif sys.argv[1] == "stop":
            steelsquid_utils.shout("Goodbye :-(")
            try:
                import steelsquid_pi
                steelsquid_pi.lcd_off()
            except:
                pass
            steelsquid_utils.execute_system_command_blind(["sudo", "steelsquid-event", "shutdown"])
    except:
        steelsquid_utils.shout()
        os._exit(0)


if __name__ == '__main__':
    main()

