#!/bin/bash
# Create, upgrade and configure steelsquid-kiss-os from https://github.com/hifi/raspbian-ua-netinst
#
# Organization: Steelsquid
# Project: Steelsquid-kiss-os
# Licensing: GNU Lesser General Public License v2.1
# Author: Andreas Nilsson
# Contact: steelsquid@gmail.com
# Homepage: http://steelsquid.org/steelsquid-kiss-os
# 
# Revision history:
#  - 2013-10-20  Created
#  - 2014-04-09  New version for raspbian-ua-netinst
#  - 2014-11-09  Rewrite everything a little neater
#                And also simplified a lot.                 



##################################################################################
# Settings (Modify to meet your requirements)
##################################################################################

# In paramater
in_parameter_1=$1
in_parameter_2=$2
in_parameter_3=$3
in_parameter_4=$4

# This script name without suffix (Project name)
project_name="steelsquid-kiss-os"

# steelsquid location
steelsquid_folder=/opt/steelsquid

# Install/execute in this location
home_folder=$steelsquid_folder

# Git url
base=https://raw.githubusercontent.com/steelsquid/steelsquid-kiss-os/master

# Remote server when using commit-remote
base_remote_server=192.168.0.194
base_remote_port=22
base_remote_user=root
base_remote_password=raspberry

# Download new version of this script from this location
download=$base/$project_name.sh

# Download img/iso file from this url
img_iso=https://googledrive.com/host/0B2XmU-Cgji4bcDFmV25xM3Vic3c

# Python downloads (install this pyton scripts)
python_downloads[1]="$base/steelsquid_kiss_boot.py"
python_downloads[2]="$base/steelsquid_nm.py"
python_downloads[3]="$base/steelsquid_pi.py"
python_downloads[4]="$base/steelsquid_piio.py"
python_downloads[5]="$base/steelsquid_synchronize.py"
python_downloads[6]="$base/steelsquid_utils.py"
python_downloads[7]="$base/steelsquid_connection.py"
python_downloads[8]="$base/steelsquid_socket_connection.py"
python_downloads[9]="$base/steelsquid_server.py"
python_downloads[10]="$base/steelsquid_http_server.py"
python_downloads[11]="$base/steelsquid_kiss_global.py"
python_downloads[12]="$base/steelsquid_kiss_http_server.py"
python_downloads[13]="$base/steelsquid_kiss_socket_connection.py"
python_downloads[14]="$base/steelsquid_lcd_hdd44780.py"
python_downloads[15]="$base/steelsquid_omx.py"
python_downloads[16]="$base/steelsquid_sabertooth.py"
python_downloads[17]="$base/steelsquid_trex.py"
python_downloads[18]="$base/steelsquid_oled_ssd1306.py"
python_downloads[19]="$base/steelsquid_bluetooth_connection.py"
python_downloads[20]="$base/steelsquid_i2c.py"
python_downloads[21]="$base/steelsquid_nrf24.py"
python_downloads[22]="$base/MCP23017.py"
python_downloads[23]="$base/nrf24.py"
python_downloads[24]="$base/modules/kiss_expand.py"
python_downloads[25]="$base/modules/kiss_alarm.py"
python_downloads[26]="$base/modules/kiss_piio.py"
python_downloads[27]="$base/modules/kiss_rover.py"
python_downloads[28]="$base/modules/kiss_nrf24rover.py"
python_downloads[29]="$base/modules/kiss_fpvrover.py"
python_downloads[30]="$base/modules/kiss_station.py"
python_downloads[31]="$base/modules/kiss_squidrover.py"
python_downloads[32]="$base/steelsquid_hmtrlrs.py"

# Links to python_downloads
python_links[1]="/usr/bin/steelsquid-boot"
python_links[2]="/usr/bin/net"
python_links[3]="/usr/bin/pi"
python_links[4]="/usr/bin/piio"
python_links[5]="/usr/bin/synchronize"
python_links[6]="/usr/bin/dummy"
python_links[7]="/usr/bin/dummy"
python_links[8]="/usr/bin/dummy"
python_links[9]="/usr/bin/dummy"
python_links[10]="/usr/bin/dummy"
python_links[11]="/usr/bin/dummy"
python_links[12]="/usr/bin/dummy"
python_links[13]="/usr/bin/dummy"
python_links[14]="/usr/bin/dummy"
python_links[15]="/usr/bin/dummy"
python_links[16]="/usr/bin/dummy"
python_links[17]="/usr/bin/dummy"
python_links[18]="/usr/bin/dummy"
python_links[19]="/usr/bin/dummy"
python_links[20]="/usr/bin/dummy"
python_links[21]="/usr/bin/dummy"
python_links[22]="/usr/bin/dummy"
python_links[23]="/usr/bin/dummy"
python_links[24]="/usr/bin/dummy"
python_links[25]="/usr/bin/dummy"
python_links[26]="/usr/bin/dummy"
python_links[27]="/usr/bin/dummy"
python_links[28]="/usr/bin/dummy"
python_links[29]="/usr/bin/dummy"
python_links[30]="/usr/bin/dummy"
python_links[31]="/usr/bin/dummy"
python_links[32]="/usr/bin/hmtrlrs"

# Download to web root folder
web_root_downloads[1]="$base/web/top_bar.html"
web_root_downloads[2]="$base/web/index.html"
web_root_downloads[3]="$base/web/favicon.ico"
web_root_downloads[4]="$base/web/play.html"
web_root_downloads[5]="$base/web/download.html"
web_root_downloads[6]="$base/web/file.html"
web_root_downloads[7]="$base/web/utils.html"
web_root_downloads[8]="$base/web/rover.html"
web_root_downloads[9]="$base/web/nrf24rover.html"
web_root_downloads[10]="$base/web/expand.html"
web_root_downloads[11]="$base/web/template.html"

# Download to web img folder
web_img_downloads[1]="$base/img/back.png"
web_img_downloads[2]="$base/img/bar_admin.png"
web_img_downloads[3]="$base/img/bar_download.png"
web_img_downloads[4]="$base/img/bar_expand.png"
web_img_downloads[5]="$base/img/bar_file.png"
web_img_downloads[6]="$base/img/bar_help.png"
web_img_downloads[7]="$base/img/bar_menu.png"
web_img_downloads[8]="$base/img/bar_play.png"
web_img_downloads[9]="$base/img/bar_power.png"
web_img_downloads[10]="$base/img/bar_reboot.png"
web_img_downloads[11]="$base/img/bar_shutdown.png"
web_img_downloads[12]="$base/img/bar_steelsquid.png"
web_img_downloads[13]="$base/img/bar_utils.png"
web_img_downloads[14]="$base/img/bar_web.png"
web_img_downloads[15]="$base/img/bluetooth.png"
web_img_downloads[16]="$base/img/camera.png"
web_img_downloads[17]="$base/img/display.png"
web_img_downloads[18]="$base/img/download.png"
web_img_downloads[19]="$base/img/electronics.png"
web_img_downloads[20]="$base/img/folder_remote.png"
web_img_downloads[21]="$base/img/gpu.png"
web_img_downloads[22]="$base/img/hostname.png"
web_img_downloads[23]="$base/img/html.png"
web_img_downloads[24]="$base/img/keyboard.png"
web_img_downloads[25]="$base/img/lcd.png"
web_img_downloads[26]="$base/img/mail.png"
web_img_downloads[27]="$base/img/network_wireless.png"
web_img_downloads[28]="$base/img/password.png"
web_img_downloads[29]="$base/img/rover.png"
web_img_downloads[30]="$base/img/samba.png"
web_img_downloads[31]="$base/img/socket.png"
web_img_downloads[32]="$base/img/status.png"
web_img_downloads[33]="$base/img/terminal.png"
web_img_downloads[34]="$base/img/time.png"
web_img_downloads[35]="$base/img/upgrade.png"
web_img_downloads[36]="$base/img/alarm.png"
web_img_downloads[37]="$base/img/alarm-panel.png"


# Must have packages will install if necessary
packages=( wget iputils-ping aptitude tar gzip sed )

# Load settings from config.txt
if [ -f config.txt ]; then
    echo ""
    COUNTER=1
    while read line           
    do           
        if [ "$COUNTER" = "1" ]; then
            base_remote_server=$line
        elif [ "$COUNTER" = "2" ]; then
            base_remote_port=$line
        elif [ "$COUNTER" = "3" ]; then
            base_remote_user=$line
        elif [ "$COUNTER" = "4" ]; then
            base_remote_password=$line
        fi
        COUNTER=$((COUNTER + 1))
    done <config.txt   
fi


##################################################################################
# Functions (Utils)
##################################################################################

# Has this script been updated
function get_uppdated()
{
	if [ "$in_parameter_1" == "skip" ]; then
		echo "true"
	else
		echo "false"
	fi
}

# echo bold
function echb()
{
	tput bold
	echo -e $@
	tput sgr0
}

# Write log post
function log()
{
  echo -e "\n$(date +"%Y-%m-%d") $(date +"%T") $1"
}

# Write command OK log post
function log-ok()
{
  echo -e "\n$(date +"%Y-%m-%d") $(date +"%T") Command executed OK"
}

# Write reboot log post
function log-reboot()
{
  echo -e "\n$(date +"%Y-%m-%d") $(date +"%T") Changes will be implemented at the next reboot"
}

# Exit this script
function do-ok-exit()
{
	log "$1"
	echo -e "\n\n"
	exit 0
}

# Exit this script
function do-err-exit()
{
	log "$1"
	echo -e "\n\n"
	exit 99
}

# If error in last command exit the script
function exit-check()
{
	if [ $? -ne 0 ]; then
        if [ -n "$1" ]; then
            do-err-exit "$1"
        else
            do-err-exit "Unhandled exception, exit script!!!"
        fi
	fi
}

# If last command OK
function has-exit-ok()
{
	if [ $? -ne 0 ]; then
		echo "false"
    else
		echo "true"
	fi
}

# If last command error
function has-exit-err()
{
	if [ $? -ne 0 ]; then
		echo "true"
    else
		echo "false"
	fi
}

# Save flag to disk
function set-flag()
{
	mkdir -p $steelsquid_folder/flags
	echo "" > $steelsquid_folder/flags/$1
}

# Has set flag to disk
function get-flag()
{
	if [ -f "$steelsquid_folder/flags/$1" ]; then
		echo "true"
	else
		echo "false"
	fi
}

# Delete flag from disk
function del-flag()
{
	rm -f $steelsquid_folder/flags/$1 > /dev/null 2>&1
}

# Set that his script is installed
function set_installed()
{
	set-flag "installed_$project_name"
}

# Is this script installed
function get_installed()
{
	if [ $(get-flag "installed_$project_name") == "true" ]; then
		echo "true"
	else
		echo "false"
	fi
}

# Remove that his script is installed
function del_installed()
{
	set-flag "installed_$project_name"
}

# Save paramater to disk
function set-parameter()
{
	mkdir -p $steelsquid_folder/parameters
	echo $2 > $steelsquid_folder/parameters/$1
}

# Get paramater from disk
function get-parameter()
{
	if [ -f "$steelsquid_folder/parameters/$1" ]; then
		cat $steelsquid_folder/parameters/$1
	else
		echo ""
	fi
}

# Has set paramater to disk
function has-parameter()
{
	if [ -f "$steelsquid_folder/parameters/$1" ]; then
		echo "true"
	else
		echo "false"
	fi
}

# Delete paramater from disk
function del-parameter()
{
	rm -f $steelsquid_folder/parameters/$1 > /dev/null 2>&1
}

# Is this a raspberry pi
function is-raspberry-pi()
{
    response=$(cat /proc/cpuinfo | grep BCM270)
    if [ "$response" == "" ]; then
		echo "false"
	else
		echo "true"
	fi
}



##################################################################################
# Help commands
##################################################################################
function help_upgrade()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "How to upgrade the system."
    echb "############################################################################"
    echo 
    echb "steelsquid upgrade"
    echo "Upgrade the whole system."
    echo "Depending on how old the system is, it may take a long time to do the"
    echo "upgrade."
    echo "NOTE! Do not turn off the device while the upgrade is in progress and the "
    echo "      device must have internet connection."
    echo "When the update is complete it should say:"
    echo "Steelsquid-kiss-os executed OK, please reboot :-)"
    echo 
    echb "steelsquid update"
    echo "Only download and update steelsquid-kiss-os script."
    echo 
    echb "steelsquid update-python"
    echo "Download and upgrade python scripts."
    echo 
    echb "steelsquid update-python <script-number>"
    echo "Download and upgrade one python script."
    echo 
    echb "steelsquid list-python"
    echo "List all pyhon scripts."
    echo 
    echb "steelsquid update-web"
    echo "Download and upgrade the web server."
    echo 
    echb "steelsquid update-img"
    echo "Download and upgrade icons and images to the web server."
    echo 
    echb "steelsquid update-all"
    echo "Update steelsquid-kiss-os, python scripts, web files and images"
}
if [ "$in_parameter_1" == "help-upgrade" ]; then
    help_upgrade
    echo
	exit 0
fi
##################################
function help_network()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Network help (connect to wifi, vpn, download manager)."
    echb "############################################################################"
    echo 
    echb "net status"
    echo "See which access point you are connected to"
    echo 
    echb "net list"
    echo "List all wifi network access points"
    echo 
    echb "net connect <number>"
    echo "Connect to open wifi network."
    echo 
    echb "net connect <number> <password>"
    echo "Connect to protected wifi network."
    echo 
    echb "net vpn-openvpn <ovpn_file> <username> <password>"
    echo "Import a .ovpn file (configure vpn)" 
    echo 
    echb "net vpn-status"
    echo "Unconfigured, Configured: <name of vpn>, Connected: <name of vpn>"
    echo 
    echb "net vpn-connect"
    echo "Connect to vpn"
    echo 
    echb "net vpn-disconnect"
    echo "Disconnect from vpn"
    echo 
    echb "hostname"
    echo "Show the hostname of this device"
    echo 
    echb "steelsquid hostname <name>"
    echo "Set the hostname of this device"
    echo "The changes will be implemented after you reboot your device"
    echo 
    echb "steelsquid download"
    echo "Is download manager enabled"
    echo 
    echb "steelsquid download-on"
    echo "Enable aria2 download manager"
    echo 
    echb "steelsquid download-off"
    echo "Disable aria2 download manager"
    echo 
    echb "steelsquid download-start"
    echo "Start aria2 download manager"
    echo 
    echb "steelsquid download-dir"
    echo "Show current download directory for download manager"
    echo 
    echb "steelsquid download-dir <directory>"
    echo "Set download directory for download manager"
    echo 
    echb "steelsquid modem"
    echo "Is USB 3g/4g modem enabled"
    echo 
    echb "steelsquid modem-on"
    echo "Enable USB 3g/4g modem"
    echo 
    echb "steelsquid modem-off"
    echo "Disable USB 3g/4g modem"
    echo 
}
if [ "$in_parameter_1" == "help-network" ]; then
    help_network
    echo
	exit 0
fi
##################################
function help_settings()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "System settings."
    echb "############################################################################"
    echo 
    echb "cat /etc/timezone"
    echo "Show current timezne."
    echo 
    echb "steelsquid timezone"
    echo "Select the geographic area (timezone) in which you live."
    echo 
    echb "steelsquid keyboards"
    echo "List all keyboard layouts."
    echo 
    echb "steelsquid keyboard"
    echo "Show current keyboard layouts."
    echo 
    echb "steelsquid keyboard <layout>"
    echo "Set keyboard layouts."
    echo "Example: keyboard se-latin1"
    echo 
    echb "steelsquid mail"
    echo "Show email notification settings"
    echo 
    echb "steelsquid mail-host <host>"
    echo "Set the SMTP server host."
    echo "Using this to send notification mail."
    echo "Example: teelsquid mail-host smtp.gmail.com:587"
    echo 
    echb "steelsquid mail-username <username>"
    echo "Set the username for the SMTP server"
    echo "Using this to send notification mail."
    echo 
    echb "steelsquid mail-password <password>"
    echo "Set the password for the SMTP server"
    echo "Using this to send notification mail."
    echo 
    echb "steelsquid mail-mail <mail-adress>"
    echo "Email that you want notification sent to"
}
if [ "$in_parameter_1" == "help-settings" ]; then
    help_settings
    echo
	exit 0
fi
##################################
function help_servers()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Servers on this system."
    echb "############################################################################"
    echo 
    echb "steelsquid ssh"
    echo "Status on the SSH-server"
    echo 
    echb "steelsquid ssh-on"
    echo "Enable SSH server."
    echo 
    echb "steelsquid ssh-off"
    echo "Disable SSH server."
    echo 
    echb "steelsquid ssh-keys"
    echo "Generate new keys for ssh"
    echo 
    echb "steelsquid web"
    echo "Status on the web interface."
    echo 
    echb "steelsquid web-on"
    echo "Enable control/configure from web browser"
    echo "http://localhost  or  http://<device ip>"
    echo 
    echb "steelsquid web-off"
    echo "Disable control/configure from web browser"
    echo 
    echb "steelsquid web-aut-on"
    echo "Connections from the network must authenticate"
    echo "Localhost can still connect without authentication"
    echo 
    echb "steelsquid web-aut-off"
    echo "Connections from the network must not authenticate"
    echo 
    echb "steelsquid web-local-on"
    echo "Only possible to control/configure from web browser on this machine."
    echo 
    echb "steelsquid web-local-off"
    echo "Control/configure from any client on the network"
    echo 
    echb "steelsquid web-http"
    echo "Use unecrypted http in the administrator interface"
    echo 
    echb "steelsquid web-https"
    echo "Use encrypted https in the administrator interface"
    echo 
    echb "steelsquid web-port <port>"
    echo "Set the web server port"
    echo 
    echb "steelsquid socket"
    echo "Is socket connection protocol enabled"
    echo 
    echb "steelsquid socket-server"
    echo "Enable socket connection as server"
    echo 
    echb "steelsquid socket-client <addressToServer>"
    echo "Enable socket connection as client"
    echo 
    echb "steelsquid socket-off"
    echo "Disable socket connection"
    echo 
    echb "steelsquid bluetooth"
    echo "Is bluetooth pairing enabled."
    echo 
    echb "steelsquid bluetooth-on"
    echo "Enable bluetooth pairing."
    echo 
    echb "steelsquid bluetooth-off"
    echo "Disable bluetooth pairing."
    echo 
    echb "steelsquid bluetooth-pin <pin>"
    echo "Set the bluetooth pairing PIN (default 1234)."
}
if [ "$in_parameter_1" == "help-servers" ]; then
    help_servers
    echo
	exit 0
fi
##################################
function help_system()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "System and hardware."
    echb "############################################################################"
    if [ $(is-raspberry-pi) == "true" ]; then
        echo 
        echb "steelsquid display"
        echo "Is the display enabled"
        echo 
        echb "steelsquid display-on"
        echo "Enable the display (hdmi and composite)."
        echo 
        echb "steelsquid display-off"
        echo "Disable the monitor (hdmi and composite)."
        echo "This will make any Desktop environment useless."
        echo "On a reboot the display will turned on, but power off after a few seconds."
    fi
    echo 
    echb "steelsquid camera"
    echo "Is the camera enabled"
    echo 
    echb "steelsquid camera-on"
    echo "Enable the raspberry pi camera."
    echo "Will take effect on next reboot...."
    echo 
    echb "steelsquid camera-off"
    echo "Disable the raspberry pi camera."
    echo "Will take effect on next reboot...."
    if [ $(is-raspberry-pi) == "true" ]; then
        echo 
        echb "steelsquid gpu-mem"
        echo "Get the GPU memory (16 to 448) default 64"
        echo 
        echb "steelsquid gpu-mem <mem>"
        echo "Set the GPU memory (16 to 448) default 64"
        echo "ARM (CPU) gets the remaining memory"
        echo "Will take effect on next reboot...."
    fi
}
if [ "$in_parameter_1" == "help-system" ]; then
    help_system
    echo
	exit 0
fi
##################################
function help_other()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Some other useful commands"
    echb "############################################################################"
    echo 
    echb "shout <message>"
    echo "Send message to user on ssh, terminal and desktop"
    echo 
    echb "notify <message>"
    echo "Send message to user on ssh, terminal and desktop."
    echo "Will also try to send mail if it is configured."
    echo 
    echb "is-raspberry-pi"
    echo "Is this device a raspberry pi"
    echo 
    echb "mail <message>"
    echo "Will try to send mail if it is configured."
    echo 
    echb "ff '<directory>' '<partOfFileName>"
    echo "search for file recursively by name"
    echo 
    echb "ff '<directory>' '<partOfFileName> '<partOfTextInFile>'"
    echo "search for file recursively by name and content in file"
    echo 
    echb "mem"
    echo "Show system memory use"
    echo 
    echb "ps-cpu"
    echo "List process from lowest to highest cpu use"
    echo 
    echb "ps-cpu <partOfProcessName>"
    echo "List process from lowest to highest cpu use, filter by name"
    echo 
    echb "ps-mem"
    echo "List process from lowest to highest mem use"
    echo 
    echb "ps-mem <partOfProcessName>"
    echo "List process from lowest to highest mem use, filter by name"
    echo 
    echb "netstat -tulpn"
    echo "List port that the system is listening on."
    echo 
    echb "lsof -i"
    echo "List open ports."
    echo 
    echb "pkill -f my_pattern"
    echo "Kill process by part of name."
    echo 
    echb "lsof|grep xxx"
    echo "Find open files."
    echo 
    echb "mc"
    echo "Midnight Commander (File manager)."
    echo 
    echb "htop"
    echo "Interactive process viewer"
    echo 
    echb "amixer"
    echo "Sound settings"
    echo 
    echb "elinks"
    echo "Text WWW Browser"
    echo 
    echb "screenie"
    echo "Screen wrapper"
    echo 
    echb "nload"
    echo "Displays the current network usage"
    echo 
    echb "mtr"
    echo "Combines traceroute and ping"
    echo 
    echb "echb <text>"
    echo "Echo bold text"
    echo 
    echb "log <text>"
    echo "Echo in the form: <date> <time> <text>"
    echo 
    echb "telnet <host>"
    echo "Make telnet (socket) connection to host"
    echo 
    echb "ssh <user>@<host>"
    echo "Connect to server with SSH."
    echo 
    echb "wget <url>"
    echo "Download file from web"
    echo 
    echb "compress <file_or_folder>"
    echo "Compress a file or folder using LZMA"
    echo 
    echb "decompress <compressed_folder>"
    echo "Decompress a file using LZMA"
    echo 
    echb "encrypt <file_or_folder>"
    echo "Encrypt a file or folder with aes-256-cbc"
    echo 
    echb "decrypt <encrypted_file>"
    echo "Decrypt a file using aes-256-cbc"
}
if [ "$in_parameter_1" == "help-other" ]; then
    help_other
    echo
	exit 0
fi
##################################
function help_files()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Description of some files and folders."
    echb "############################################################################"
    echo 
    echb "$steelsquid_folder/flags/"
    echo "Configuration flags"
    echo 
    echb "$steelsquid_folder/lists/"
    echo "Configuration lists"
    echo 
    echb "$steelsquid_folder/parameters/"
    echo "Configuration parameters"
    echo 
    echb "$steelsquid_folder/pem/"
    echo "HTTPS cerificate files"
    echo "Will be created when https is enabled"
    echo 
    echb "$steelsquid_folder/web/"
    echo "Web root"
    echo 
    echb "/root"
    echo "Home folder (root user)"
    echo 
    echb "/root/Media"
    echo "Link to /media"
    echo 
    echb "/media"
    echo "USB disks will automatically be installed here."
    echo 
    echb "/root/test.py"
    echo "A python file to test stuff in..."
    echo 
    echb "/opt/steelsquid/steelsquid-kiss-os.sh"
    echo "The steelsquid install and update script"
    echo 
    echb "/etc/init.d/steelsquid"
    echo "Init script for /usr/bin/steelsquid-boot"
    echo 
    echb "/etc/NetworkManager/dispatcher.d/99steelsquid.sh"
    echo "Fire network status"
    echo 
    echb "/usr/bin/steelsquid -> /opt/steelsquid/steelsquid-kiss-os.sh"
    echo "The steelsquid script"
    echo 
    echb "/opt/steelsquid/python"
    echo "Home for all python files"
    echo 
    echb "/usr/bin/steelsquid-boot -> /opt/steelsquid/python/steelsquid_kiss_boot.py"
    echo "Python script that execute on boot and shutdown"
    echo 
    echb "/usr/bin/event -> /opt/steelsquid/python/steelsquid_kiss_boot.py"
    echo "The steelsquid_kiss_boot.py also handles events from the OS...(using the name event in some old scripts)"
    echo 
    echb "/opt/steelsquid/python/modules"
    echo "All python scrips in this folder will be imported (executed) on boot."
    echo "Use this to inmplement your own stuff."
    echo 
    echb "/usr/local/lib/python2.7/dist-packages"
    echo "External python 2 libraries (Adafruit, RPi, picamera, wiringpi2)"
    echo 
    echb "/usr/lib/python3/dist-packages"
    echo "External python 3 libraries (quick2wire)"
    echo 
    echb "/opt/steelsquid/web/top_bar.html"
    echo "The black top bar that is on most pages"
    echo 
    echb "/opt/steelsquid/web/download.html"
    echo "HTML-file for the download manager"
    echo 
    echb "/opt/steelsquid/web/expand.html"
    echo "Use this to create your own stuff..."
    echo 
    echb "/opt/steelsquid/web/file.html"
    echo "HTML-file for the filemanager"
    echo 
    echb "/opt/steelsquid/web/index.html"
    echo "HTML-file for the web start page (settings)"
    echo 
    echb "/opt/steelsquid/web/play.html"
    echo "HTML-file for the mediaplayer"
    echo 
    echb "/opt/steelsquid/web/utils.html"
    echo "HTML-file for different utils (Camera streaming, alarm and rover)"
    echo 
    echb "/opt/steelsquid/python/MCP23017.py"
    echo "Use the mcp23017 16-bit input/output port expander with interrupt output"
    echo 
    echb "/opt/steelsquid/python/steelsquid_bluetooth_connection.py"
    echo "Bluetooth implementation of steelsquid_connection..."
    echo 
    echb "/opt/steelsquid/python/steelsquid_kiss_boot.py"
    echo "This will execute when steelsquid-kiss-os starts"
    echo "Also listen for events from the OS"
    echo 
    echb "/opt/steelsquid/python/steelsquid_connection.py"
    echo "A simple module that i use to sen async command to and from client/server."
    echo 
    echb "/opt/steelsquid/python/steelsquid_http_server.py"
    echo "This server will listen for http requests."
    echo 
    echb "/opt/steelsquid/python/steelsquid_i2c.py"
    echo "Use this to communicate with i2c devices."
    echo 
    echb "/opt/steelsquid/python/modules/kiss_expand.py"
    echo "Use this file to implement you own stuff..."
    echo 
    echb "/opt/steelsquid/python/steelsquid_kiss_global.py"
    echo "Global stuff for steelsquid kiss os"
    echo 
    echb "/opt/steelsquid/python/steelsquid_kiss_http_server.py"
    echo "Handles requests from index.html, download.html, file.html, play.html, utils.html"
    echo 
    echb "/opt/steelsquid/python/steelsquid_kiss_socket_connection.py"
    echo "Controll steelsquid kiss os with simle socket commands"
    echo 
    echb "/opt/steelsquid/python/steelsquid_lcd_hdd44780.py"
    echo "Print text on a HDD44780 compatible LCD from Raspberry Pi"
    echo 
    echb "/opt/steelsquid/python/steelsquid_nm.py"
    echo "List and connect to wifi network using network manager"
    echo 
    echb "/opt/steelsquid/python/steelsquid_oled_ssd1306.py"
    echo "Write text to a ssd1306 oled display"
    echo 
    echb "/opt/steelsquid/python/steelsquid_omx.py"
    echo "Simple python interface for the omxplayer"
    echo 
    echb "/opt/steelsquid/python/steelsquid_pi.py"
    echo "Some useful stuff for Raspberry Pi"
    echo 
    echb "/opt/steelsquid/python/steelsquid_piio.py"
    echo "Mostly wrapper functions (hard coded adresses and pins) for my steelsquid PIIO board"
    echo 
    echb "/opt/steelsquid/python/steelsquid_sabertooth.py"
    echo "A simple serial interface for Sabertooth motor controller."
    echo 
    echb "/opt/steelsquid/python/steelsquid_server.py"
    echo "A simple module that i use to listen for command and then execute stuff."
    echo 
    echb "/opt/steelsquid/python/steelsquid_socket_connection.py"
    echo "Socket implementation of steelsquid_connection..."
    echo 
    echb "/opt/steelsquid/python/steelsquid_synchronize.py"
    echo "Automatic listen for changes abd commit changes to a nother system via ssh (install on remote system)"
    echo 
    echb "/opt/steelsquid/python/steelsquid_trex.py"
    echo "Controll the Trex robot controller"
    echo 
    echb "/opt/steelsquid/python/steelsquid_utils.py"
    echo "Some useful functions."
    echo 
    echb "/opt/steelsquid/python/modules/kiss_alarm.py"
    echo "This is functionality for my alarm."
    echo 
    echb "/opt/steelsquid/python/modules/kiss_rover.py"
    echo "Fuctionality for my rover controller"
    echo 
    echb "/opt/steelsquid/python/modules/kiss_piio.py"
    echo "Fuctionality for my PIIO board"
}
if [ "$in_parameter_1" == "help-files" ]; then
    help_files
    echo
	exit 0
fi
##################################
function help_develop()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Commands for development."
    echb "############################################################################"
    echo 
    echb "steelsquid restart"
    echo "Restart the steelsquid daemon"
    echo 
    echb "steelsquid dev"
    echo "Is the system in development mode"
    echo 
    echb "steelsquid dev-on"
    echo "Enable development mode"
    echo 
    echb "steelsquid dev-off"
    echo "Disable development mode"
    echo 
    echb "set-flag expanded"
    echo "It will tell the upgrade script not to overwrite:"
    echo " - kiss_expand.py"
    echo " - expand.html"
    echo " - test.py"
    echo "This is useful if you have expanded functionality. otherwise, the changes will be overwritten when you execute upgrade."
    echo 
    echb "steelsquid module-list"
    echo "List all modules in modules direcory"
    echo 
    echb "steelsquid module <name>"
    echo "Is a module activated."
    echo "A module is the python files under modules directory"
    echo "name = The name of the file in modules directory"
    echo 
    echb "steelsquid module <name> <on/off>"
    echo "Enable or disable a module."
    echo "When a module is enabled it will start on boot."
    echo "A module is the python files under modules directory"
    echo "name = The name of the file in modules directory"
    echo "on/off = On enable the module and off will disable"
    echo 
    echb "steelsquid module <name> <on/off> <argument>"
    echo "Enable or disable a module."
    echo "When a module is enabled it will start on boot."
    echo "A module is the python files under modules directory"
    echo "name = The name of the file in modules directory"
    echo "on/off = On enable the module and off will disable"
    echo "argument = Send a argument to the module (one word)"
    echo 
    echb "steelsquid download-img"
    echo "Download a steelsquid-kiss-os.img file."
    echo 
    echb "steelsquid read </dev/sdX>"
    echo "Create a steelsquid-kiss-os.img from drive."
    echo 
    echb "steelsquid write </dev/sdX>"
    echo "Write steelsquid-kiss-os.img to drive."
    echo  
    echb "steelsquid archive"
    echo "Create a steelsquid-kiss-os.gz file of the content in the folder this script is in."
    echo "Will ignore .img, .iso and .gz files"
    echo 
    echb "steelsquid compress"
    echo "Create a steelsquid-kiss-os.gz file of the steelsquid-kiss-os.img or steelsquid-kiss-os.iso files in the folder this script is in."
    echo 
    echb "steelsquid extract"
    echo "Extract a steelsquid-kiss-os.gz file in the folder this script is in."
    echo 
    echb "steelsquid remote-restart"
    echo "Restart steelsquid service on remote system."
    echo "Set paramaters in this script:"
    echo "  base_remote_server=192.168.0.199"
    echo "  base_remote_port=22"
    echo "  base_remote_user=steelsquid"
    echo "Or add 4 rows to config.txt"    
    echo "  ip"
    echo "  port"
    echo "  user"
    echo "  password"
    echo 
    echb "steelsquid commit-git"
    echo "Commit changes to the GIT and push to github"
    echo 
    echb "steelsquid commit-local"
    echo "Commit changes to the local system (install on local system)"
    echo "Will commit (install) the steelsquid script, python files and web files"
    echo 
    echb "steelsquid commit-remote"
    echo "Commit changes to a nother system via ssh (install on remote system)"
    echo "Will commit (install) the steelsquid script, python files and web files"
    echo "Set paramaters in this script:"
    echo " base_remote_server=192.168.0.199"
    echo " base_remote_port=22"
    echo " base_remote_user=steelsquid"
    echo "Or add 4 rows to config.txt"    
    echo "  ip"
    echo "  port"
    echo "  user"
    echo "  password"
    echo 
    echb "steelsquid commit-remote-restart"
    echo "Commit changes to a nother system via ssh (install on remote system)"
    echo "Will commit (install) the steelsquid script, python files and web files"
    echo "After installation is done the steelsquid service will restart."
    echo "Set paramaters in this script:"
    echo "  base_remote_server=192.168.0.199"
    echo "  base_remote_port=22"
    echo "  base_remote_user=steelsquid"
    echo "Or add 4 rows to config.txt"    
    echo "  ip"
    echo "  port"
    echo "  user"
    echo "  password"
    echo 
    echb "steelsquid synchronize"
    echo "Automatic listen for changes abd commit changes to a nother system via ssh (install on remote system)"
    echo 
    echb "is-raspberry-pi"
    echo "Is this device a raspberry pi"
    echo 
    echb "lcd"
    echo "Is LCD disabled/nokia5110/HDD44780/ssd1306"
    echo 
    echb "lcd-hdd"
    echo "Enable the LCD via HDD44780 (i2c)"
    echo 
    echb "lcd-nokia"
    echo "Enable the LCD via nokia5110 (spi)"
    echo 
    echb "lcd-ssd"
    echo "Enable the LCD via ssd1306 oled (02c)"
    echo 
    echb "lcd-auto"
    echo "Try to use nokia5110/HDD44780/ssd1306"
    echo 
    echb "lcd-off"
    echo "Disable the LCD"
    echo 
    echb "lcd-contrast"
    echo "Get contrast on nokia5110 LCD (0 to 100)."
    echo 
    echb "lcd-contrast <value>"
    echo "Set contrast on nokia5110 LCD (0 to 100)."
    echo 
    echb "steelsquid log"
    echo "Is logging enabled"
    echo 
    echb "steelsquid log-on"
    echo "Enable logging"
    echo "Will take effect on next reboot...."
    echo 
    echb "steelsquid log-off"
    echo "Disable logging"
    echo "Will take effect on next reboot...."
    echo 
    echb "list-flags"
    echo "Set flag"
    echo 
    echb "set-flag <flagName>"
    echo "Set flag"
    echo "The steelsquid daemon must be running for this to work"
    echo 
    echb "get-flag <flagName>"
    echo "Has flag"
    echo 
    echb "del-flag <flagName>"
    echo "Delete flag"
    echo "The steelsquid daemon must be running for this to work"
    echo 
    echb "list-parameters"
    echo "Set flag"
    echo 
    echb "set-parameter <name> <value>"
    echo "Set paramater value"
    echo "The steelsquid daemon must be running for this to work"
    echo 
    echb "get-parameter <name>"
    echo "Get paramater value"
    echo 
    echb "has-parameter <name>"
    echo "Has a paramater"
    echo 
    echb "del-parameter <name>"
    echo "Delete a parameter"
    echo "The steelsquid daemon must be running for this to work"
    echo 
    echb "event <event>"
    echo "Broadcast event without parameters"
    echo 
    echb "event <event> <parameter1> <parameter2>..."
    echo "Broadcast event with paramaters"
    echo 
    echb "steelsquid power-gpio"
    echo "Is the power off functionality enabled"
    echo "Connect a button to the raspberry to shut down cleanly"
    echo 
    echb "steelsquid power-gpio <gpio>"
    echo "Enable power off functionality"
    echo "<gpio> = use this GPIO (connect button to 3V3, using PULL_DOWN)"
    echo 
    echb "steelsquid power-gpio-off"
    echo "Disable power off functionality"
    echo 
    echb "steelsquid i2c-lock"
    echo "Is i2c lock/syncronization enabled"
    echo "If many devices and strange errors from I2C, try to enabler this."
    echo 
    echb "steelsquid i2c-lock-on"
    echo "Enable i2c lock/syncronization"
    echo "If many devices and strange errors from I2C, try to enabler this."
    echo 
    echb "steelsquid i2c-lock-off"
    echo "Disable i2c lock/syncronization"
    echo "If many devices and strange errors from I2C, try to enabler this."
}
if [ "$in_parameter_1" == "help-dev" ]; then
    help_develop
    echo
	exit 0
fi
##################################
function help_io()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    pi
    echo 

}

if [ "$in_parameter_1" == "help-pi" ]; then
    help_io
    echo
	exit 0
fi
##################################
function help_piio()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    piio
    echo 

}

if [ "$in_parameter_1" == "help-piio" ]; then
    help_piio
    echo
	exit 0
fi
##################################
function help_utils()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "Extra utils: stream USB camera, Alarm/Surveillance..."
    echb "############################################################################"
    echo 
    echb "steelsquid stream"
    echo "Is camera streaming enabled."
    echo 
    echb "steelsquid stream-frames <frames>"
    echo "Set Frames per second."
    echo 
    echb "steelsquid stream-port <port>"
    echo "Set port to listen for connections on."
    echo 
    echb "steelsquid stream-on"
    echo "Enable http streaming of USB camera."
    echo 
    echb "steelsquid stream-pi-on"
    echo "Enable http streaming of Raspberry PI camera."
    echo 
    echb "steelsquid stream-off"
    echo "Disable streaming of camera."
    echo 
    echb "steelsquid alarm"
    echo "Is the Alarm/Surveillance functionality enabled."
    echo "For this to work you need a Raspberry PI camera connected."
    echo "Also a PIR sensor conneted to GPIO04 and a siren conencted to GPIO17."
    echo "See http://www.steelsquid.org/alarm"
    echo 
    echb "steelsquid alarm-on"
    echo "Enable the Alarm/Surveillance functionality."
    echo "For this to work you need a Raspberry PI camera connected."
    echo "Also a PIR sensor conneted to GPIO04 and a siren conencted to GPIO17."
    echo "See http://www.steelsquid.org/alarm"
    echo 
    echb "steelsquid alarm-off"
    echo "Disable the Alarm/Surveillance functionality."
    echo 
    echb "steelsquid rover"
    echo "Is rover functionality enabled."
    echo 
    echb "steelsquid rover-on"
    echo "Enable rover functionality."
    echo 
    echb "steelsquid rover-off"
    echo "Disable rover functionality."
    echo 
    echb "steelsquid browser-on <url>"
    echo "When system boot, start a browser in fullscreen."
    echo "Need to install alot of stuff, will take several minutes to finish."
    echo "url = URL to load"
    echo 
    echb "steelsquid browser-off"
    echo "Desable the browser start when system boot"
    echo 
    echb "steelsquid browser-restart"
    echo "If the browser in fullscreen is activated use this to restart it."
}
if [ "$in_parameter_1" == "help-utils" ]; then
    help_utils
    echo
	exit 0
fi
##################################
function help_build()
{
    echo 
    echo 
    echo 
    echb "############################################################################"
    echb "How to build a steelsquid-kiss img (reminder for me)"
    echb "############################################################################"
    echo 
    echb "1.  Download and extract the installer image"
    echo "wget https://github.com/debian-pi/raspbian-ua-netinst/releases/download/v1.0.8.1/raspbian-ua-netinst-v1.0.8.1.img.xz"
    echo "unxz raspbian-ua-netinst-v1.0.8.1.img.xz"
    echo 
    echb "2.  Copy to sdcard"
    echo "dd bs=4M if=raspbian-ua-netinst-v1.0.8.1.img of=/dev/sdb"
    echo 
    echb "3.  Insert sdcard into raspberry and boot"
    echo "Must have the networkcabel connected (internet access)"
    echo "The installation process will start automatically."
    echo "It takes about 15 minutes"
    echo 
    echb "4.  SSH or use terminal to the new system"
    echo "ssh root@192.168.0.xxx"
    echo "password = raspbian"
    echo 
    echb "5.  Set password"
    echo "passwd  (raspberry)"
    echo 
    echb "7.  Change to 4.1 and uppgrade"
    echo "echo \"deb http://mirrordirector.raspbian.org/raspbian/ jessie main contrib non-free rpi\" > /etc/apt/sources.list"
    echo "echo \"deb http://archive.raspberrypi.org/debian/ jessie main ui untested staging\" >> /etc/apt/sources.list"
    echo "apt-get update"
    echo "apt-get purge linux-image-rpi-rpfv linux-image-rpi2-rpfv libraspberrypi0 libraspberrypi-{bin,dev} raspberrypi-bootloader-nokernel"
    echo "apt-get --no-install-recommends install sudo nano aptitude"
    echo "apt-get install raspberrypi-bootloader libraspberrypi0 libraspberrypi-{bin,dev}"
    echo "cd /boot/"
    echo "rm initrd.img-3.18.0-trunk-rpi2 config-3.18.0-trunk-rpi2 kernel-rpi1_install.img kernel-rpi2_install.img"
    echo "aptitude update"
    echo "aptitude full-upgrade"
    echo "dpkg --configure -a"
    echo 
    echb "8.  Fix config"
    echb "echo \"\" > /boot/config.txt"
    echo 
    echb "9.  "
    echb ""
    echo 
    echb "10.  Clean"
    echo "aptitude autoclean"
    echo "aptitude clean"
    echo "apt-get clean"
    echo "apt-get -y autoremove"
    echo "rm /root/.bash_history"
    echo "rm /root/.nano_history"
    echo 
    echb "11. Shutdown and mount on computer"
    echo 
    echb "12. Resize to 3.4G with gparted"
    echo 
    echb "13. Boot the raspberry pi again."
    echo 
    echb "14. Download script"
    echo "wget --no-check-certificate http://www.steelsquid.org/steelsquid-kiss-os.sh"
    echo 
    echb "15. Make executable"
    echo "chmod +x steelsquid-kiss-os.sh"
    echo 
    echb "16. Execute the stcript"
    echo "./steelsquid-kiss-os.sh upgrade"
    echo 
    echb "17. Take a nap :-)"
    echo "May have to answer some questions"
    echo 
    echb "18. Remove script"
    echo "rm steelsquid-kiss-os.sh"
    echo 
    echb "19. Shutdown raspberry"
    echo 
    echb "20. Insert sdcard in other computer and mount"
    echo "rm -R var/log/*"
    echo "rm -R var/tmp/*"
    echo "rm -R tmp/*"
    echo 
    echb "21. Make a img of it"
    echo "./steelsquid-kiss-os.sh read /dev/sdb"
    echo 
    echb "22. Compress image to gz"
    echo "./steelsquid-kiss-os.sh compress"
    echo 
    echb "23. On new image remember to:"
    echo "Upload steelsquid-kiss-os.sh to http://www.steelsquid.org"
    echo "Clear the ssh keys"
    echo 
    echb "24. GIT and github"
    echo "git init"
    echo "git add *.html"
    echo "git commit -m \"Initial commit\""
    echo "git remote add steelsquidkissos https://github.com/steelsquid/steelsquid-kiss-os.git"
    echo "git commit -a -m \"-\""
    echo "git push steelsquidkissos master"
}
if [ "$in_parameter_1" == "help-build" ]; then
    help_build
    echo
	exit 0
fi
##################################
function help_top()
{
    echo 
    echo 
    echb "############################################################################"
    echb "Create, upgrade, configure and develop steelsquid-kiss-os."
    echb "http://www.steelsquid.org/steelsquid-kiss-os"
    echb "############################################################################"
    echo 
    echb "reboot"
    echo "Reboot the system"
    echo 
    echb "shutdown now -h"
    echo "Shutdown the system"
    echo 
    echb "sudo su"
    echo "Get root privilege"
    echo 
    echb "steelsquid download"
    echo "Download a steelsquid-kiss-os.img file."
    echo "Use this to download a image to your computer, which you can then write to the sd-card."
    echo 
    echb "steelsquid write </dev/sdX>"
    echo "Write steelsquid-kiss-os.img to a sd-card."
    echo 
    echb "steelsquid status"
    echo "Print information about the device."
    echo "CPU, MEM, IP, Temp, Settings..."
    echo 
    echb "steelsquid search <text>"
    echo "Search for a text in all help."
    echo 
    echb "steelsquid help"
    echo "Display this help."
    echo 
    echb "steelsquid help-all"
    echo "Display help from all help categories."
    echo 
    echb "steelsquid help-network"
    echo "Show help about network (connect to wifi)"
    echo 
    echb "steelsquid help-settings"
    echo "Show help about settings and configurations"
    echo 
    echb "steelsquid help-servers"
    echo "Status of servers on this system"
    echo 
    echb "steelsquid help-system"
    echo "Show help about system and hardware"
    echo 
    echb "steelsquid help-upgrade"
    echo "Show help how to upgrade the system"
    echo 
    echb "steelsquid help-utils"
    echo "Extra utils: stream USB camera, rover..."
    echo 
    echb "steelsquid help-other"
    echo "Show some other useful commands"
    echo 
    echb "steelsquid help-pi"
    echo "IO commands for Steelsquid Kiss OS. Commands to get/set gpio and other stuff."
    echo 
    echb "steelsquid help-piio"
    echo "Send commands to the Steelsquid PIIO board from the command line."
    echo 
    echb "steelsquid help-files"
    echo "Description of some files and folders."
    echo 
    echb "steelsquid help-dev"
    echo "Commands for development."
    echo 
    echb "steelsquid help-build"
    echo "How to build a steelsquid-kiss img (reminder for me)."
}
if [ "$in_parameter_1" == "help-all" ]; then
    help_top
    help_network
    help_settings
    help_servers
    help_system
    help_upgrade
    help_utils
    help_other
    help_files
    help_develop
    help_io
    help_build
    echo 
    exit 0
fi
if [ "$in_parameter_1" == "help" ]; then
    help_top
    echo 
    exit 0
fi

if [ "$in_parameter_1" == "search" ]; then
    echo
    steelsquid help-all | grep -A 4 -B 1 $in_parameter_2
    echo 
    exit 0
fi


##################################################################################
# Check that some packages is installed 
##################################################################################
if [ $(get_uppdated) == "false" ]; then
    if [ "$in_parameter_1" == "upgrade" ] ; then
        log "Check for necessary packages"
        apt-get update
        dpkg -s sudo  > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            if [[ $EUID -ne 0 ]]; then
                do-err-exit "Sudo must be installed or this script must be executed as root."
            else
                log "Installing package sudo"
                apt-get install sudo
                if [ $(has-exit-err) == "true" ]; then
                    sleep 1
                    apt-get -f --no-install-recommends install sudo
                    exit-check "Unable to install sudo!"
                fi
            fi
        fi
        echo packages[@]
        for var in "${packages[@]}"
        do
            dpkg -s ${var}  > /dev/null 2>&1
            if [ $? -ne 0 ]; then
                log "Installing package ${var}"
                sudo apt-get -f --no-install-recommends install ${var}
                if [ $(has-exit-err) == "true" ]; then
                    sleep 1
                    sudo apt-get install ${var}
                    exit-check "Unable to install ${var}!"
                fi
            fi
        done
        log "All necessary packages installed"
    fi
fi


##################################################################################
# Is the clean power off enabled
##################################################################################
function power_info()
{

    if [ "$in_parameter_2" == "" ]; then
        if [ $(has-parameter "power_gpio") == "true" ]; then
            dat=$(get-parameter "power_gpio")
            echo
            echo "Clean power off: Eabled ($dat)"
            echo
        else
            echo
            echo "Clean power off: Disabled"
            echo
        fi
    else
        set-parameter "power_gpio" $in_parameter_2
        systemctl restart steelsquid
    fi
}
if [ "$in_parameter_1" == "power-gpio" ]; then
	power_info
	exit 0
fi


##################################################################################
# Disable clean power off enabled
##################################################################################
function power_off()
{
	log "Disable clean power off"
    del-parameter "power_gpio"
    systemctl restart steelsquid
}
if [ "$in_parameter_1" == "power-gpio-off" ]; then
	power_off
	exit 0
fi


##################################################################################
# Is USB 3g/4g modem enabled
##################################################################################
function modem_info()
{
    if [ $(get-flag "modem") == "true" ]; then
        echo
        echo "USB 3g/4g modem: Eabled"
        echo
    else
        echo
        echo "USB 3g/4g modem: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "modem" ]; then
	modem_info
	exit 0
fi


##################################################################################
# Enable USB 3g/4g modem 
##################################################################################
function modem_on()
{
	log "Enable USB 3g/4g modem"
    aptitude update
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install usb-modeswitch modemmanager
    set-flag "modem"
	log-reboot
}
if [ "$in_parameter_1" == "modem-on" ]; then
	modem_on
	exit 0
fi


##################################################################################
# Disable USB 3g/4g modem enabled
##################################################################################
function modem_off()
{
	log "Disable USB 3g/4g modem"
    aptitude -y purge usb-modeswitch modemmanager
    del-flag "modem"
	log-reboot
}
if [ "$in_parameter_1" == "modem-off" ]; then
	modem_off
	exit 0
fi


##################################################################################
# Is systemd logging enabled or disabled
##################################################################################
function log_info()
{
    if [ $(get-flag "log") == "true" ]; then
        echo
        echo "Systemd logging: Eabled"
        echo
    else
        echo
        echo "Systemd logging: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "log" ]; then
	log_info
	exit 0
fi


##################################################################################
# Enable systemd logging
##################################################################################
function log_on()
{
	log "Enable systemd logging"
    set-flag "log"
    sed -i '/VERBOSE=/c\VERBOSE=yes' /etc/default/rcS
    echo "dwc_otg.fiq_fix_enable dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootfstype=ext4 rootflags=commit=1 elevator=noop noatime nodiratime rootwait logo.nologo" > /boot/cmdline.txt
    sed -i 's/^Storage.*/Storage=persistent/' /etc/systemd/journald.conf
    sed -i 's/^LogLevel.*/#LogLevel=/' /etc/systemd/system.conf
    sed -i 's/^LogTarget.*/#LogTarget=/' /etc/systemd/system.conf
    sed -i 's/^DefaultStandardOutput.*/#DefaultStandardOutput=/' /etc/systemd/system.conf
    sed -i 's/^LogLevel.*/#LogLevel=/' /etc/systemd/user.conf
    sed -i 's/^LogTarget.*/#LogTarget=/' /etc/systemd/user.conf
    sed -i 's/^DefaultStandardOutput.*/#DefaultStandardOutput=/' /etc/systemd/user.conf    
    sed -i 's/^#ForwardToConsole.*/ForwardToConsole=yes/' /etc/systemd/journald.conf
    systemctl enable systemd-journald.service    
    systemctl start systemd-journald.service
    sed -i 's/errors=remount-ro,defaults,noatime,nodiratime /errors=remount-ro,defaults,noatime,sync,nodiratime /g' /etc/fstab
    sed -i '/tmpfs/d' /etc/fstab
    sed -i '/none /d' /etc/fstab
	log-reboot
}
if [ "$in_parameter_1" == "log-on" ]; then
	log_on
	exit 0
fi


##################################################################################
# Disable systemd logging
##################################################################################
function log_off()
{
	log "Disable systemd logging"
    del-flag "log"
    sed -i '/VERBOSE=/c\VERBOSE=no' /etc/default/rcS
    echo "dwc_otg.fiq_fix_enable dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootfstype=ext4 rootflags=commit=10,data=writeback elevator=noop noatime nodiratime data=writeback rootwait quiet loglevel=0 logo.nologo consoleblank=0" > /boot/cmdline.txt
    sed -i 's/^Storage.*/Storage=none/' /etc/systemd/journald.conf
    sed -i 's/^#LogLevel.*/LogLevel=emerg/' /etc/systemd/system.conf
    sed -i 's/^#LogTarget.*/LogTarget=null/' /etc/systemd/system.conf
    sed -i 's/^#DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/system.conf
    sed -i 's/^#LogLevel.*/LogLevel=crit/' /etc/systemd/user.conf
    sed -i 's/^#LogTarget.*/LogTarget=null/' /etc/systemd/user.conf
    sed -i 's/^#DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/user.conf    
    sed -i 's/^Storage.*/Storage=none/' /etc/systemd/journald.conf
    sed -i 's/^LogLevel.*/LogLevel=emerg/' /etc/systemd/system.conf
    sed -i 's/^LogTarget.*/LogTarget=null/' /etc/systemd/system.conf
    sed -i 's/^DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/system.conf
    sed -i 's/^LogLevel.*/LogLevel=crit/' /etc/systemd/user.conf
    sed -i 's/^LogTarget.*/LogTarget=null/' /etc/systemd/user.conf
    sed -i 's/^DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/user.conf    
    sed -i 's/^ForwardToConsole.*/#ForwardToConsole=no/' /etc/systemd/journald.conf  
    systemctl stop systemd-journald.service
    systemctl disable systemd-journald.service    
    sed -i '/tmpfs/d' /etc/fstab
    sed -i '/none /d' /etc/fstab
    sed -i 's/errors=remount-ro,defaults,noatime,sync,nodiratime /errors=remount-ro,defaults,noatime,nodiratime /g' /etc/fstab
    echo "none   /var/log   tmpfs   noatime,nodiratime,rw,mode=1777,nodev,nosuid,noexec,size=32m    0   0" >> /etc/fstab
    echo "none   /tmp       tmpfs   noatime,nodiratime,rw,mode=1777,nodev,nosuid,size=256m   0   0" >> /etc/fstab
    echo "/tmp   /var/tmp   none    noatime,nodiratime,rw,mode=1777,nodev,nosuid,bind        0   0" >> /etc/fstab
	log-reboot
}
if [ "$in_parameter_1" == "log-off" ]; then
	log_off
	exit 0
fi


##################################################################################
# lcd info
##################################################################################
function lcd_info()
{
    if [ $(get-flag "nokia") == "true" ]; then
        echo
        echo "LCD is enabled (nokia5101)"
        echo
    elif [ $(get-flag "hdd") == "true" ]; then
        echo
        echo "LCD is enabled (HDD44780)"
        echo
    elif [ $(get-flag "ssd") == "true" ]; then
        echo
        echo "LCD is enabled (ssd1306)"
        echo
    elif [ $(get-flag "auto") == "true" ]; then
        echo
        echo "LCD in automatic mode"
        echo
    else
        echo
        echo "LCD is disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "lcd" ]; then
	lcd_info
	exit 0
fi



##################################################################################
# Enable print IP to lcd
##################################################################################
function enable_lcd_nokia()
{
	log "Enable print IP and messges to nokia5110 LCD"
	set-flag "nokia"
	del-flag "hdd"
	del-flag "auto"
	del-flag "ssd"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "lcd-nokia" ]; then
	enable_lcd_nokia
	exit 0
fi


##################################################################################
# Enable print IP to lcd
##################################################################################
function enable_lcd_auto()
{
	log "Enable print IP and messges to nokia5110 or HDD44780 LCD"
	set-flag "auto"
	del-flag "nokia"
	del-flag "hdd"
	del-flag "ssd"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "lcd-auto" ]; then
	enable_lcd_auto
	exit 0
fi


##################################################################################
# Enable print IP to lcd
##################################################################################
function enable_lcd_hdd()
{
	log "Enable print IP and messges to HDD44780 LCD"
	set-flag "hdd"
	del-flag "nokia"
	del-flag "auto"
	del-flag "ssd"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "lcd-hdd" ]; then
	enable_lcd_hdd
	exit 0
fi


##################################################################################
# Enable print IP to lcd
##################################################################################
function enable_lcd_ssd()
{
	log "Enable print IP and messges to ssd1306 oled LCD"
	del-flag "hdd"
	del-flag "nokia"
	del-flag "auto"
	set-flag "ssd"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "lcd-ssd" ]; then
	enable_lcd_ssd
	exit 0
fi


##################################################################################
# Disable print IP to lcd
##################################################################################
function disable_lcd()
{
	log "Disable print IP and messges to LCD"
	del-flag "nokia"
	del-flag "hdd"
	del-flag "auto"
	del-flag "ssd"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "lcd-off" ]; then
	disable_lcd
	exit 0
fi


##################################################################################
# Set get contrast for nokia lcd
##################################################################################
function contrast_lcd()
{
    if [ "$in_parameter_2" == "" ]; then
        echo "Contrast: "$(get-parameter "nokia_contrast")
    else
        set-parameter "nokia_contrast" $in_parameter_2
        systemctl restart steelsquid
        log-ok
    fi
}
if [ "$in_parameter_1" == "lcd-contrast" ]; then
	contrast_lcd
	exit 0
fi



##################################################################################
# Camera info
##################################################################################
function camera_info()
{
    if [ $(get-flag "camera") == "true" ]; then
        echo
        echo "Camera enabled"
        echo
    else
        echo
        echo "camera disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "camera" ]; then
	camera_info
	exit 0
fi



##################################################################################
# Enable Camera
##################################################################################
function enable_camera()
{
	log "Enable camera"
	set-flag "camera"
    sed -i '/^gpu_mem/ d' /boot/config.txt
    sed -i '/^start_x/ d' /boot/config.txt
    sed -i '/^start_file/ d' /boot/config.txt
    sed -i '/^fixup_file/ d' /boot/config.txt
    sed -i '/^disable_camera_led/ d' /boot/config.txt
    echo "gpu_mem=128" >> /boot/config.txt
    echo "start_x=1" >> /boot/config.txt
    echo "start_file=start_x.elf" >> /boot/config.txt
    echo "fixup_file=fixup_x.dat" >> /boot/config.txt 
    echo "disable_camera_led=1" >> /boot/config.txt 
    set-parameter "gpu_mem" "128"
    log-reboot
}
if [ "$in_parameter_1" == "camera-on" ]; then
	enable_camera
	exit 0
fi




##################################################################################
# Disable Camera
##################################################################################
function disable_camera()
{
	log "Disable camera"
	del-flag "camera"
    sed -i '/^gpu_mem/ d' /boot/config.txt
    sed -i '/^start_x/ d' /boot/config.txt
    sed -i '/^start_file/ d' /boot/config.txt
    sed -i '/^fixup_file/ d' /boot/config.txt
    sed -i '/^disable_camera_led/ d' /boot/config.txt
    echo "gpu_mem=64" >> /boot/config.txt
    set-parameter "gpu_mem" "64"
    log-reboot
}
if [ "$in_parameter_1" == "camera-off" ]; then
	disable_camera
	exit 0
fi



##################################################################################
# Show status streaming of USB camera
##################################################################################
function stream_info()
{
    if [ $(get-flag "stream") == "true" ]; then
        echo
        echo "USB camera streaming: Enabled"
        echo "WEB: http://xxx.xxx.xxx.xxx/utils"
        echo "The Stream: http://xxx.xxx.xxx.xxx:8080/?action=stream"
        echo
    elif [ $(get-flag "stream-pi") == "true" ]; then
        echo
        echo "Raspberry PI camera streaming: Enabled"
        echo "WEB: http://xxx.xxx.xxx.xxx/utils"
        echo "The Stream: http://xxx.xxx.xxx.xxx:8080/?action=stream"
        echo
    else
        echo
        echo "Camera streaming: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "stream" ]; then
	stream_info
	exit 0
fi


##################################################################################
# Set stream frame rate
##################################################################################
function stream_frames()
{
    set-parameter "stream_frames" $in_parameter_2
}
if [ "$in_parameter_1" == "stream-frames" ]; then
	stream_frames
	exit 0
fi


##################################################################################
# Enable or disable a module
##################################################################################
function module()
{
    if [[ $in_parameter_3 == "" ]]; then
        if [[ $(get-flag "module_$in_parameter_2") == "true" ]]; then
            log "Enabled"
        else
            log "Disabled"
        fi
    else
        if [[ $in_parameter_3 == "on" ]]; then
            if [ "$in_parameter_4" == "" ]; then                
                log "Enable module $in_parameter_2"
                event module_on $in_parameter_2
            else
                log "Enable module $in_parameter_2 $in_parameter_4"
                event module_on $in_parameter_2  $in_parameter_4
            fi
        else
            if [ "$in_parameter_4" == "" ]; then                
                log "Disable module $in_parameter_2"
                event module_off $in_parameter_2
            else
                log "Disable module $in_parameter_2 $in_parameter_4"
                event module_off $in_parameter_2 $in_parameter_4
            fi
        fi
    fi
}
if [ "$in_parameter_1" == "module" ]; then
	module
	exit 0
fi


##################################################################################
# List modules
##################################################################################
function module_list()
{
    echo ""
    echo "STATUS     MODULE NAME"
    echo "-----------------------------------------------"
    for f in /opt/steelsquid/python/modules/*.py
    do
        f=$(basename "$f")
        f="${f%.*}"
        if [[ $f != "__init__" ]]; then
            if [[ $(get-flag "module_$f") == "true" ]]; then
                echo "[Enabled]  $f"
            else
                echo "[Disabled] $f"
            fi
        fi
    done
}
if [ "$in_parameter_1" == "module-list" ]; then
	module_list
	exit 0
fi


##################################################################################
# List modules
##################################################################################
function module_list_nr()
{
    echo ""
    echo "  STATUS     MODULE NAME"
    echo "-----------------------------------------------"
    COUNTER=1
    for f in /opt/steelsquid/python/modules/*.py
    do
        f=$(basename "$f")
        f="${f%.*}"
        if [[ $f != "__init__" ]]; then
            if [[ $(get-flag "module_$f") == "true" ]]; then
                echo "$COUNTER [Enabled]  $f"
            else
                echo "$COUNTER [Disabled] $f"
            fi
            COUNTER=$[$COUNTER +1]
        fi
    done
}
if [ "$in_parameter_1" == "module-list-nr" ]; then
	module_list_nr
	exit 0
fi


##################################################################################
# Set stream port
##################################################################################
function stream_port()
{
    set-parameter "stream_port" $in_parameter_2
    if [ $(get-flag "stream") == "true" ]; then
        stream_on
    fi
    if [ $(get-flag "stream-pi") == "true" ]; then
        stream_on_pi
    fi
}
if [ "$in_parameter_1" == "stream-port" ]; then
	stream_port
	exit 0
fi


##################################################################################
# Enable streaming of USB camera
##################################################################################
function stream_on()
{
	log "Enable streaming of USB camera"
    dat=$(get-parameter "stream_frames")
        
    set-flag "stream"
    del-flag "stream-pi"
    systemctl stop mjpgstreamerpi
    systemctl disable mjpgstreamerpi

    rm -r /opt/mjpg-streamer/mjpg-streamer/www
    echo "[Unit]" > /etc/systemd/system/mjpgstreamer.service
    echo "Description=Mjpg" >> /etc/systemd/system/mjpgstreamer.service
    echo "" >> /etc/systemd/system/mjpgstreamer.service
    echo "[Service]" >> /etc/systemd/system/mjpgstreamer.service
    echo "Environment=\"LD_LIBRARY_PATH=/opt/mjpg-streamer/mjpg-streamer\"" >> /etc/systemd/system/mjpgstreamer.service
    echo "ExecStart=/opt/mjpg-streamer/mjpg-streamer/mjpg_streamer -i \"input_uvc.so -f ${dat} -r 640x480 --led off\" -o \"output_http.so -w www\"" >> /etc/systemd/system/mjpgstreamer.service
    echo "Restart=always" >> /etc/systemd/system/mjpgstreamer.service
    echo "RestartSec=5" >> /etc/systemd/system/mjpgstreamer.service
    echo "KillMode=process" >> /etc/systemd/system/mjpgstreamer.service
    echo "" >> /etc/systemd/system/mjpgstreamer.service
    echo "[Install]" >> /etc/systemd/system/mjpgstreamer.service
    echo "WantedBy=multi-user.target" >> /etc/systemd/system/mjpgstreamer.service
    systemctl --system daemon-reload
    systemctl enable mjpgstreamer
    systemctl start mjpgstreamer
    log-reboot
}
if [ "$in_parameter_1" == "stream-on" ]; then
	stream_on
	exit 0
fi

##################################################################################
# Enable streaming of USB camera
##################################################################################
function stream_on_pi_no_restart()
{
    dat=$(get-parameter "stream_frames")
    del-flag "stream"
    set-flag "stream-pi"
    systemctl stop mjpgstreamer
    systemctl disable mjpgstreamer

    enable_camera 
    
    rm -r /opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/www
    echo "[Unit]" > /etc/systemd/system/mjpgstreamerpi.service
    echo "Description=Mjpg" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "[Service]" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "Environment=\"LD_LIBRARY_PATH=/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental\"" >> /etc/systemd/system/mjpgstreamerpi.service
    if [ $(get-flag "stream_low") == "true" ]; then
        echo "ExecStart=/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer -i \"/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/input_raspicam.so -vf -hf -x 320 -y 240 -quality 12 -fps ${dat}\" -o \"/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/output_http.so -w www\"" >> /etc/systemd/system/mjpgstreamerpi.service
    else
        echo "ExecStart=/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer -i \"/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/input_raspicam.so -x 640 -y 480 -fps ${dat}\" -o \"/opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental/output_http.so -w www\"" >> /etc/systemd/system/mjpgstreamerpi.service
    fi
    echo "Restart=always" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "RestartSec=5" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "KillMode=process" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "[Install]" >> /etc/systemd/system/mjpgstreamerpi.service
    echo "WantedBy=multi-user.target" >> /etc/systemd/system/mjpgstreamerpi.service
    systemctl --system daemon-reload
    systemctl enable mjpgstreamerpi
    systemctl start mjpgstreamerpi
}


##################################################################################
# Enable streaming of USB camera
##################################################################################
function stream_on_pi()
{
	log "Enable streaming of Raspberry PI camera"
    stream_on_pi_no_restart
    log-reboot
}
if [ "$in_parameter_1" == "stream-pi-on" ]; then
	stream_on_pi
	exit 0
fi


##################################################################################
# Disable streaming of USB camera
##################################################################################
function stream_off_no_restart()
{
    del-flag "stream"
    del-flag "stream-pi"
    systemctl stop mjpgstreamer
    systemctl disable mjpgstreamer
    systemctl stop mjpgstreamerpi
    systemctl disable mjpgstreamerpi
}

##################################################################################
# Disable streaming of USB camera
##################################################################################
function stream_off()
{
	log "Disable streaming of USB camera"
    stream_off_no_restart
    log-reboot
}
if [ "$in_parameter_1" == "stream-off" ]; then
	stream_off
	exit 0
fi


##################################################################################
# Enable start browser  in fullscreen
##################################################################################
function browser_on()
{
	log "Enable start browser  in fullscreen"
    useradd browser
    mkhomedir_helper browser
    aptitude install -R xserver-xorg-video-fbturbo xserver-xorg xinit gconf-service libgconf-2-4 libgnome-keyring0 libxss1 xserver-xorg-input-multitouch xdg-utils lsb-release libexif12 libexif-gtk5 nodm
    wget http://ftp.us.debian.org/debian/pool/main/libg/libgcrypt11/libgcrypt11_1.5.0-5+deb7u3_armhf.deb
    wget http://launchpadlibrarian.net/218525709/chromium-browser_45.0.2454.85-0ubuntu0.14.04.1.1097_armhf.deb
    wget http://launchpadlibrarian.net/218525711/chromium-codecs-ffmpeg-extra_45.0.2454.85-0ubuntu0.14.04.1.1097_armhf.deb
    dpkg -i libgcrypt11_1.5.0-5+deb7u3_armhf.deb
    dpkg -i chromium-codecs-ffmpeg-extra_45.0.2454.85-0ubuntu0.14.04.1.1097_armhf.deb
    dpkg -i chromium-browser_45.0.2454.85-0ubuntu0.14.04.1.1097_armhf.deb
    
    echo "#"\!"/bin/bash" > /home/browser/.xsession
    echo "xset s off &" >> /home/browser/.xsession
    echo "xset dpms 0 0 0 &" >> /home/browser/.xsession
    echo "exec /usr/bin/chromium-browser --noerrdialogs --incognito --touch-events=enabled --enable-pinch --kiosk $in_parameter_2" >> /home/browser/.xsession
    chmod +x /home/browser/.xsession
    
    sed -i 's/.*NODM_ENABLED=.*/NODM_ENABLED=true/' /etc/default/nodm
    sed -i 's/.*NODM_USER=.*/NODM_USER=browser/' /etc/default/nodm
    systemctl enable nodm
    systemctl start nodm
        
    del-flag "web_authentication"
    set-parameter "browser" $in_parameter_2
    log-reboot
}
if [ "$in_parameter_1" == "browser-on" ]; then
	browser_on
	exit 0
fi


##################################################################################
# Disable start browser  in fullscreen
##################################################################################
function browser_off()
{
	log "Disable start browser  in fullscreen"
    systemctl stop nodm
    systemctl disable nodm
        
    set-flag "web_authentication"
    del-parameter "browser"
    log-reboot
}
if [ "$in_parameter_1" == "browser-off" ]; then
	browser_off
	exit 0
fi


##################################################################################
# Disable start browser  in fullscreen
##################################################################################
function browser_restart()
{
	log "Restart fullscreen browser"
    systemctl stop nodm
    sleep 2
    systemctl start nodm
}
if [ "$in_parameter_1" == "browser-restart" ]; then
	browser_restart
	exit 0
fi


##################################################################################
# Show status Alarm/Surveillance
##################################################################################
function alarm_info()
{
    if [ $(get-flag "module_kiss_alarm") == "true" ]; then
        echo
        echo "Alarm/Surveillance: Enabled"
        echo "For this to work you need a Raspberry PI camera connected."
        echo "Also a PIR sensor conneted to GPIO04 and a siren conencted to GPIO17."
        echo "WEB: http://xxx.xxx.xxx.xxx/utils"
        echo
    else
        echo
        echo "Alarm/Surveillance: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "alarm" ]; then
	alarm_info
	exit 0
fi


##################################################################################
# Enable Alarm/Surveillance
##################################################################################
function alarm_on()
{
	log "Enable Alarm/Surveillance"
    steelsquid module kiss_alarm on
	log-ok
}
if [ "$in_parameter_1" == "alarm-on" ]; then
	alarm_on
	exit 0
fi


##################################################################################
# Disable Alarm/Surveillance
##################################################################################
function alarm_off()
{
	log "Disable Alarm/Surveillance"
    steelsquid module kiss_alarm off
	log-ok
}
if [ "$in_parameter_1" == "alarm-off" ]; then
	alarm_off
	exit 0
fi


##################################################################################
# Is socket connection enabled or disabled
##################################################################################
function socket_info()
{
    if [ $(get-flag "socket_server") == "true" ]; then
        echo
        echo "Socket connection as server enabled (Port=22222)"
        echo
    elif [ $(get-parameter "socket_client") != "" ]; then
        dat=$(get-parameter "socket_client")
        echo
        echo "Socket connection as client enabled (Adress to server=${dat}:22222)"
        echo
    else
        echo
        echo "Socket connection: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "socket" ]; then
	socket_info
	exit 0
fi


##################################################################################
# Socket connection server
##################################################################################
function socket_server()
{
	log "Enable socket connection as server"
    set-flag "socket_server"
    del-parameter "socket_client"
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "socket-server" ]; then 
	socket_server
	exit 0
fi



##################################################################################
# Socket connection client
##################################################################################
function socket_client()
{
	log "Enable socket connection as client"
    del-flag "socket_server"
    set-parameter "socket_client" $in_parameter_2
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "socket-client" ]; then
	socket_client
	exit 0
fi


##################################################################################
#  off
##################################################################################
function socket_off()
{
	log "Disable socket connection"
    del-flag "socket_server"
    del-parameter "socket_client"
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "socket-off" ]; then
	socket_off
	exit 0
fi


##################################################################################
# Is bluetooth pairing enabled or disabled
##################################################################################
function bluetooth_info()
{
    if [ $(get-flag "bluetooth_pairing") == "true" ]; then
        echo
        echo "Bluetooth pairing: Enabled"
        echo
    else
        echo
        echo "Bluetooth pairing: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "bluetooth" ]; then
	bluetooth_info
	exit 0
fi


##################################################################################
# bluetooth pairing on
##################################################################################
function bluetooth_on()
{
	log "Enable bluetooth pairing"
    set-flag "bluetooth_pairing"
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "bluetooth-on" ]; then
	bluetooth_on
	exit 0
fi


##################################################################################
#  bluetooth pairing off
##################################################################################
function bluetooth_off()
{
	log "Disable bluetooth pairing"
    del-flag "bluetooth_pairing"
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "bluetooth-off" ]; then
	bluetooth_off
	exit 0
fi


##################################################################################
# Set bluetooth pairing PIN
##################################################################################
function bluetooth_pin()
{
	log "Set bluetooth pairing PIN"
    set-parameter "bluetooth_pin" $in_parameter_2
	systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "bluetooth-pin" ]; then
	bluetooth_pin
	exit 0
fi


##################################################################################
# Is rover enabled or disabled
##################################################################################
function rover_info()
{
    if [ $(get-flag "module_kiss_rover") == "true" ]; then
        echo
        echo "Rover functionality: Enabled"
        echo
    else
        echo
        echo "Rover functionality: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "rover" ]; then
	rover_info
	exit 0
fi


##################################################################################
# Rover on
##################################################################################
function rover_on()
{
	log "Enable rover"
    steelsquid module kiss_rover on
    log-ok
}
if [ "$in_parameter_1" == "rover-on" ]; then
	rover_on
	exit 0
fi


##################################################################################
# Rover off
##################################################################################
function rover_off()
{
	log "Disable rover"
    steelsquid module kiss_rover off
    log-ok
}
if [ "$in_parameter_1" == "rover-off" ]; then
	rover_off
	exit 0
fi


##################################################################################
# Is Steelsquid PIIO Board enabled or disabled
##################################################################################
function piio_info()
{
    if [ $(get-flag "module_kiss_piio") == "true" ]; then
        echo
        echo "Steelsquid PIIO Board: Enabled"
        echo
    else
        echo
        echo "Steelsquid PIIO Board: Disabled"
        echo
    fi
}
if [ "$in_parameter_1" == "piio" ]; then
	piio_info
	exit 0
fi


##################################################################################
# Steelsquid PIIO Board on
##################################################################################
function piio_on()
{
	log "Enable Steelsquid PIIO Board"
    steelsquid module kiss_piio on
    log-ok
}
if [ "$in_parameter_1" == "piio-on" ]; then
	piio_on
	exit 0
fi


##################################################################################
# Steelsquid PIIO Board off
##################################################################################
function piio_off()
{
	log "Disable Steelsquid PIIO Board"
    steelsquid module kiss_piio off
    log-ok
}
if [ "$in_parameter_1" == "piio-off" ]; then
	piio_off
	exit 0
fi


##################################################################################
# Restart service
##################################################################################
function restart_s()
{
    echo "Restart steelsquid service"
    systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "restart" ]; then
	restart_s
	exit 0
fi


    
##################################################################################
# SSH info
##################################################################################
function ssh_info()
{
    echo 
    if [ $(get-flag "ssh") == "false" ]; then
        echo "SSH-server: Disabled"
    else
        echo "SSH-server: Enabled"
    fi
    echo 
}

if [ "$in_parameter_1" == "ssh" ]; then
	ssh_info
	exit 0
fi

    

##################################################################################
# Enable ssh
##################################################################################
function ssh_on()
{
	log "Enable SSH"
    sed -i "/PermitRootLogin /c\PermitRootLogin yes" /etc/ssh/sshd_config
    sed -i "/PrintLastLog /c\PrintLastLog no" /etc/ssh/sshd_config
    sed -i "/Protocol /c\Protocol 2" /etc/ssh/sshd_config
    sed -i "/IgnoreRhosts /c\IgnoreRhosts yes" /etc/ssh/sshd_config
    systemctl unmask ssh
    systemctl enable ssh
    systemctl stop ssh
    systemctl start ssh
	set-flag "ssh"
    log-ok
}

if [ "$in_parameter_1" == "ssh-on" ]; then
	ssh_on
	exit 0
fi


##################################################################################
# Disable ssh
##################################################################################
function ssh_off()
{
	log "Disable SSH server"
    systemctl stop ssh
    systemctl disable ssh
    systemctl mask ssh
	del-flag "ssh"
    log-ok
}

if [ "$in_parameter_1" == "ssh-off" ]; then
	ssh_off
	exit 0
fi


##################################################################################
# Generate SSH keys
##################################################################################
function ssh_keys()
{
    echo "Generating keys for ssh"
    rm /etc/ssh/ssh_host_*
    dpkg-reconfigure openssh-server
    systemctl restart ssh
    log-ok
}
if [ "$in_parameter_1" == "ssh-keys" ]; then
	ssh_keys
	exit 0
fi


##################################################################################
# Download server info
##################################################################################
function download_info()
{
    echo 
    if [ $(get-flag "download") == "true" ]; then
        echo "Download server: Eanbled"
    else
        echo "Download server: Disabled"
    fi
    echo 
}

if [ "$in_parameter_1" == "download" ]; then
	download_info
	exit 0
fi


##################################################################################
# Start download server
##################################################################################
function download_start()
{
	log "start download server"
    killall aria2c > /dev/null 2>&1
    aria2c -D --enable-rpc --listen-port=6881 --on-download-complete=aria2shoutok  --on-download-error=aria2shouterr --dir=$download_dir
    log-ok
}
if [ "$in_parameter_1" == "download-start" ]; then
	download_start
	exit 0
fi


##################################################################################
# Enable download server
##################################################################################
function download_on()
{
	log "Enable download server"
    download_dir=$(get-parameter "download_dir")
    if [ -z "$download_dir" ]; then
        download_dir="/root/Downloads"
        set-parameter "download_dir" "/root/Downloads"
    fi
	set-flag "download"
    download_start
}
if [ "$in_parameter_1" == "download-on" ]; then
	download_on
	exit 0
fi



##################################################################################
# Disable download server
##################################################################################
function download_off()
{
	log "Disable download server"
    killall aria2c > /dev/null 2>&1
	del-flag "download"
    log-ok
}
if [ "$in_parameter_1" == "download-off" ]; then
	download_off
	exit 0
fi


##################################################################################
# Set download directory
##################################################################################
function download_dirr()
{
    if [ "$in_parameter_2" == "" ]; then
        echo $(get-parameter "download_dir")
    else
        mkdir -p $in_parameter_2 > /dev/null 2>&1
        set-parameter "download_dir" "$in_parameter_2"
        download_off
        download_on      
    fi
}
if [ "$in_parameter_1" == "download-dir" ]; then
	download_dirr
	exit 0
fi


##################################################################################
# web info
##################################################################################
function web_info()
{
    echo
    if [ $(get-flag "web") == "false" ]; then
        echo "WEB-interface: Disabled"
    else
        if [ $(get-flag "web_https") == "true" ]; then
            echo "WEB-interface: HTTPS"
        else
            echo "WEB-interface: HTTP"
        fi
        if [ $(get-flag "web_authentication") == "true" ]; then
            echo "Authentication: Enabled"
        else
            echo "Authentication: Disabled"
        fi
        if [ $(get-flag "web_local") == "true" ]; then
            echo "Listening: Localhost"
        else
            echo "Listening: All interfaces"
        fi
    fi
    echo
}

if [ "$in_parameter_1" == "web" ]; then
	web_info
	exit 0
fi


##################################################################################
# set web server port
##################################################################################
function web_port()
{
	log "Set webserver port"
	$(set-parameter "web_port" $in_parameter_2)
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-port" ]; then
	web_port
	exit 0
fi



##################################################################################
# Enable web server
##################################################################################
function web_on()
{
	log "Enable web server"
	set-flag "web"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-on" ]; then
	web_on
	exit 0
fi


##################################################################################
# Disable web server
##################################################################################
function web_off()
{
	log "Disable web server"
	del-flag "web"
    systemctl restart steelsquid
    log-ok
}

if [ "$in_parameter_1" == "web-off" ]; then
	web_off
	exit 0
fi



##################################################################################
# Web only listen on localhost
##################################################################################
function web_local_on()
{
	set-flag "web_local"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-local-on" ]; then
	web_local_on
	exit 0
fi




##################################################################################
# Web listen on all
##################################################################################
function web_local_off()
{
	del-flag "web_local"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-local-off" ]; then
	web_local_off
	exit 0
fi


##################################################################################
# Use http in web interface
##################################################################################
function web_http()
{
	log "Use http in web interface"  
	del-flag "web_https"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-http" ]; then
	web_http
	exit 0
fi


##################################################################################
# Use https in web interface
##################################################################################
function web_https()
{
	log "Use https in web interface"   
	set-flag "web_https"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-https" ]; then
	web_https
	exit 0
fi


##################################################################################
# Use web authentication
##################################################################################
function web_aut_on()
{
	log "Web authentication on"
	set-flag "web_authentication"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-aut-on" ]; then
	web_aut_on
	exit 0
fi


##################################################################################
# No Use web authentication
##################################################################################
function web_aut_off()
{
	log "Web authentication off"
	del-flag "web_authentication"
    systemctl restart steelsquid
	log-ok
}
if [ "$in_parameter_1" == "web-aut-off" ]; then
	web_aut_off
	exit 0
fi


##################################################################################
# List parameters and flags
##################################################################################
if [ "$in_parameter_1" == "list-flags" ]; then
    echo "power                Clean power off"
    echo "modem                USB 3g/4g modem"
    echo "log                  Systemd logging"
    echo "nokia                Print text to nokia5101 LCD"
    echo "hdd                  Print text to HDD44780 LCD"
    echo "sdd                  Print text to ssd1306 OLED LCD"
    echo "auto                 Automtic select lcd display"
    echo "camera               Raspberry PI camera enabled"
    echo "stream               Stream USB camera"
    echo "stream-pi            Stream the Raspberry PI camera"
    echo "socket_server        Socket connection as server enabled"
    echo "bluetooth_pairing    Bluetooth pairing is enabled"
    echo "rover                Rover functionality"
    echo "io                   Steelsquid IO Board is enabled"
    echo "ssh                  SSH server enabled"
    echo "download             Download manager enabled"
    echo "web                  WEB-interface enabled"
    echo "web_https            Use HTTPS on the web server"
    echo "web_authentication   Must login to WEB-server"
    echo "web_local            Only listen on localhost"
    echo "development          Is development mode enabled"
    echo "disable_monitor      Disable the monitor"
    echo "no_net_to_lcd        Do not print network ip to LCD"
    exit 0
fi
if [ "$in_parameter_1" == "list-parameters" ]; then
    echo "nokia_contrast  Nokia LCD contrast"
    echo "gpu_mem         GPU mem"
    echo "bluetooth_pin   PIN code for bluetooth pairing"
    echo "download_dir    Download dir for download manager"
    echo "mail_host       Mail server to send notifications"
    echo "mail_username   Mail server username to send notifications"
    echo "mail_password   Mail server password to send notifications"
    echo "mail_mail       Notifications email"
    echo "socket_client   Socket connection as client enabled (this is the address to the server)"
    exit 0
fi


##################################################################################
# Print informaqtion about the system
##################################################################################
if [ "$in_parameter_1" == "status" ]; then
    python -c "import steelsquid_utils; steelsquid_utils.print_system_info()"
    exit 0
fi


##################################################################################
# Create a <project_name>.gz file of the content in the folder this script is in.
# Will ignore .img and .gz files
##################################################################################
if [ "$in_parameter_1" == "archive" ]; then
	log "Start to make gz file of content of current folder"
	tar -czf $project_name.gz * --exclude='*.img' --exclude='*.gz' --exclude='*.iso'
	exit-check
	do-ok-exit "File created: $project_name.gz"
fi




##################################################################################
# Create a <project_name>.gz file of the <project_name>.img or <project_name>.iso files in the folder this script is in. 
##################################################################################
if [ "$in_parameter_1" == "compress" ]; then
	log "Start to make gz file of .img file in current folder"
	tar -czf $project_name.gz $project_name.img
	if [ $? -ne 0 ]; then
		tar -czf $project_name.gz $project_name.iso
		exit-check
	fi
	do-ok-exit "File created: $project_name.gz"
fi



##################################################################################
# Extract a <project_name>.gz file in the folder this script is in. 
##################################################################################
if [ "$in_parameter_1" == "extract" ]; then
	log "Start to extract"
	tar -zxf $project_name.gz -C ./
	exit-check
	do-ok-exit "Extract finished"
fi




##################################################################################
# Download and extract a *.gz file from $img_iso. 
##################################################################################
if [ "$in_parameter_1" == "download-img" ]; then
	log "Start to download"
	wget --progress=dot:giga --no-check-certificate -O ${project_name}_download.gz $img_iso
	if [ $? -ne 0 ]; then
		rm ${project_name}_download.gz > /dev/null 2>&1
		do-err-exit "Unable to download from $img_iso"
	else
		log "Start to extract"
		tar -zxf ${project_name}_download.gz -C ./
		exit-check
		rm ${project_name}_download.gz > /dev/null 2>&1
		exit-check
	fi
	do-ok-exit "Download and extract finished"
fi



##################################################################################
# Create a <project_name>.img from drive.
##################################################################################
if [ "$in_parameter_1" == "read" ]; then
	log "Start to create a <project name>.img from drive"
	dd if=$in_parameter_2 of=./$project_name.img bs=4M count=875
	exit-check
	do-ok-exit "Img created: $project_name.img"
fi




##################################################################################
# Write <project_name>.img to drive.
##################################################################################
if [ "$in_parameter_1" == "write" ]; then
	log "Start to write a <project name>.img to drive"
	dd bs=4M if=$project_name.img of=$in_parameter_2
	exit-check
	do-ok-exit "Write finished: $project_name.img"
fi




##################################################################################
# Download and install python scripts
##################################################################################
function install_steelsquid_python()
{
	log "Download and install python scripts"
    mkdir -p /opt/steelsquid/python/
    mkdir -p /opt/steelsquid/python/modules/
	index=1
	for var in "${python_downloads[@]}"
	do
        expandf=""
        if [[ $var == */modules/* ]]; then
            expandf="/modules"
        fi
        
        if [ $(get-flag "expanded") == "true" ]; then
            if [[ $var != *_expand* ]]; then
                sudo wget --progress=dot:giga --no-check-certificate -O /opt/steelsquid/python$expandf/$(basename $var) $var
                if [ $? -ne 0 ]; then
                    do-err-exit "Unable to download from $var"
                else
                    sudo chmod 755 /opt/steelsquid/python$expandf/$(basename $var)
                    rm ${python_links[$index]} > /dev/null 2>&1
                    sudo ln -s /opt/steelsquid/python$expandf/$(basename $var) ${python_links[$index]}
                    index=$[$index +1]
                    log "$var downloaded and installed"
                fi
            fi        
        else
            sudo wget --progress=dot:giga --no-check-certificate -O /opt/steelsquid/python$expandf/$(basename $var) $var
            if [ $? -ne 0 ]; then
                do-err-exit "Unable to download from $var"
            else
                sudo chmod 755 /opt/steelsquid/python$expandf/$(basename $var)
                rm ${python_links[$index]} > /dev/null 2>&1
                sudo ln -s /opt/steelsquid/python$expandf/$(basename $var) ${python_links[$index]}
                index=$[$index +1]
                log "$var downloaded and installed"
            fi
        fi
	done
	log "Python scripts installed"
}
function install_steelsquid_python_one()
{
	log "Download and install python script"
    var=${python_downloads[$in_parameter_2]}
    expandf=""
    if [[ $var == */modules/* ]]; then
        expandf="/modules"
    fi
    sudo wget --progress=dot:giga --no-check-certificate -O /opt/steelsquid/python$expandf/$(basename $var) $var
    if [ $? -ne 0 ]; then
        do-err-exit "Unable to download from $var"
    else
        sudo chmod 755 /opt/steelsquid/python$expandf/$(basename $var)
        rm ${python_links[$in_parameter_2]} > /dev/null 2>&1
        sudo ln -s /opt/steelsquid/python$expandf/$(basename $var) ${python_links[$in_parameter_2]}
        log "$var downloaded and installed"
    fi
	log "Python script installed"
}
function python_list()
{
	log "Python scripts"
	index=1
    line='    '
    echo
	for var in "${python_downloads[@]}"
	do
        echo "$index${line:${#index}}$(basename $var)"
		index=$[$index +1]
	done
    echo
}


##################################################################################
# Download and install web root
##################################################################################
function install_web_files()
{
	log "Download and install web files"
    mkdir -p $steelsquid_folder/web
    
    index=0
	for var in "${web_root_downloads[@]}"
	do
        if [ $(get-flag "expanded") == "true" ]; then
            if [[ $var != *expand.html* ]]; then
                sudo wget --progress=dot:giga --no-check-certificate -O $steelsquid_folder/web/$(basename $var) $var
                index=$[$index +1]
                if [ $? -ne 0 ]; then
                    do-err-exit "Unable to download from $var"
                else
                    log "$var downloaded and installed"
                fi
            fi
        else
            sudo wget --progress=dot:giga --no-check-certificate -O $steelsquid_folder/web/$(basename $var) $var
            index=$[$index +1]
            if [ $? -ne 0 ]; then
                do-err-exit "Unable to download from $var"
            else
                log "$var downloaded and installed"
            fi
        fi
	done
	log "Web files installed"
}
function install_web_files_first()
{
	log "Download and install first web files"
    var=${web_root_downloads[0]}
    sudo wget --progress=dot:giga --no-check-certificate -O $steelsquid_folder/web/$(basename $var) $var
    if [ $? -ne 0 ]; then
        do-err-exit "Unable to download from $var"
    else
        log "$var downloaded and installed"
    fi
}

if [ "$in_parameter_1" == "update-web" ]; then
	install_web_files
	exit 0
fi
if [ "$in_parameter_1" == "update-web-first" ]; then
	install_web_files_first
	exit 0
fi
if [ "$in_parameter_1" == "update-python" ]; then
    if [ "$in_parameter_2" == "" ]; then
        install_steelsquid_python
        exit 0
    else
        install_steelsquid_python_one
        exit 0
    fi
    
fi
if [ "$in_parameter_1" == "list-python" ]; then
    python_list
    exit 0
fi



##################################################################################
# Download and install img root
##################################################################################
function install_img_files()
{
	log "Download and install img files"
    mkdir -p $steelsquid_folder/web/img
    
    index=0
	for var in "${web_img_downloads[@]}"
	do
        sudo wget --progress=dot:giga --no-check-certificate -O $steelsquid_folder/web/img/$(basename $var) $var
        index=$[$index +1]
        if [ $? -ne 0 ]; then
            do-err-exit "Unable to download from $var"
        else
            log "$var downloaded and installed"
        fi
	done
	log "Img files installed"
}
if [ "$in_parameter_1" == "update-img" ]; then
	install_img_files
	exit 0
fi


##################################################################################
# Download and install all
##################################################################################
function install_all_files()
{
	log "Download and install all steelsquid files"
    version_check
    install_steelsquid_python
    install_web_files
    install_img_files
	log "OK"
}
if [ "$in_parameter_1" == "update-all" ]; then
	install_all_files
	exit 0
fi



##################################################################################
# mail
##################################################################################
if [ "$in_parameter_1" == "mail" ]; then
    echo 
    dat=$(get-parameter "mail_host")
    echo "SMTP-server: ${dat}"
    dat=$(get-parameter "mail_username")
    echo "Username: ${dat}"
    echo "Password: *******"
    dat=$(get-parameter "mail_mail")
    echo "Notification mail: ${dat}"
    echo 
    exit 0
fi
if [ "$in_parameter_1" == "mail-host" ]; then
    $(set-parameter "mail_host" $in_parameter_2)
    exit 0
fi
if [ "$in_parameter_1" == "mail-username" ]; then
    $(set-parameter "mail_username" $in_parameter_2)
    exit 0
fi
if [ "$in_parameter_1" == "mail-password" ]; then
    $(set-parameter "mail_password" $in_parameter_2)
    exit 0
fi
if [ "$in_parameter_1" == "mail-mail" ]; then
    $(set-parameter "mail_mail" $in_parameter_2)
    exit 0
fi



##################################################################################
# Select the model of the keyboard of this machine.
##################################################################################
if [ "$in_parameter_1" == "keyboards" ]; then
    echo
    echo "ar"
    echo "bg-cp1251"
    echo "bg"
    echo "br-abnt2"
    echo "br-latin1"
    echo "by"
    echo "ca-multi"
    echo "cf"
    echo "cz-lat2-prog"
    echo "cz-lat2"
    echo "cz-us-qwerty"
    echo "defkeymap"
    echo "defkeymap_V1.0"
    echo "dk-latin1"
    echo "dk"
    echo "emacs"
    echo "emacs2"
    echo "es-cp850"
    echo "es"
    echo "et-nodeadkeys"
    echo "et"
    echo "fa"
    echo "fi-latin1"
    echo "fi"
    echo "gr-pc"
    echo "gr-utf8"
    echo "gr"
    echo "hebrew"
    echo "hu101"
    echo "il-heb"
    echo "il-phonetic"
    echo "il"
    echo "is-latin1-us"
    echo "is-latin1"
    echo "it-ibm"
    echo "it"
    echo "it2"
    echo "jp106"
    echo "kg"
    echo "kk"
    echo "la-latin1"
    echo "lisp-us"
    echo "lk201-us"
    echo "lt"
    echo "lt.l4"
    echo "lv-latin4"
    echo "lv-latin7"
    echo "mac-usb-dk-latin1"
    echo "mac-usb-es"
    echo "mac-usb-euro"
    echo "mac-usb-fi-latin1"
    echo "mac-usb-se"
    echo "mac-usb-uk"
    echo "mac-usb-us"
    echo "mk"
    echo "nl"
    echo "no-latin1"
    echo "no-standard"
    echo "no"
    echo "pc110"
    echo "pl"
    echo "pl1"
    echo "pt-latin1"
    echo "pt-old"
    echo "ro-academic"
    echo "ro-comma"
    echo "ro"
    echo "ru-cp1251"
    echo "ru-ms"
    echo "ru-yawerty"
    echo "ru"
    echo "ru1"
    echo "ru2"
    echo "ru3"
    echo "ru4"
    echo "ru_win"
    echo "se-fi-ir209"
    echo "se-fi-lat6"
    echo "se-ir209"
    echo "se-lat6"
    echo "se-latin1"
    echo "sk-prog-qwerty"
    echo "sk-prog"
    echo "sk-qwerty"
    echo "sr-cy"
    echo "th-tis"
    echo "tr_q-latin5"
    echo "tralt"
    echo "trq"
    echo "trqu"
    echo "ua-utf-ws"
    echo "ua-utf"
    echo "ua-ws"
    echo "ua"
    echo "uaw"
    echo "uaw_uni"
    echo "uk"
    echo "us-intl.iso01"
    echo "us-intl.iso15"
    echo "us-latin1"
    echo "us"
    echo
    exit 0
fi


##################################################################################
# Select the model of the keyboard of this machine.
##################################################################################
if [ "$in_parameter_1" == "keyboard" ]; then
    if [ "$in_parameter_2" == "" ]; then
        cur=$(get-parameter "keyboard")
        echo
        echo "Current: $cur"
        echo
        exit 0
    else
        $(set-parameter "keyboard" $in_parameter_2)
        loadkeys $in_parameter_2
        do-ok-exit "Keybor layout changed."
    fi
fi



##################################################################################
# Select the geographic area in which you live.
##################################################################################
if [ "$in_parameter_1" == "timezone" ]; then
	log "Select the geographic area in which you live."
	sudo dpkg-reconfigure tzdata
	do-ok-exit "Geographic area selected."
fi


##################################################################################
# Select the geographic area in which you live.
##################################################################################
if [ "$in_parameter_1" == "timezone-set" ]; then
    cp -f /usr/share/zoneinfo/$in_parameter_2 /etc/localtime
    echo $in_parameter_2 > /etc/timezone
    exit 0
fi


##################################################################################
# Set host name
##################################################################################
if [ "$in_parameter_1" == "hostname" ]; then
    echo $in_parameter_2 > /etc/hostname
    sed -i "/$(hostname)/d" /etc/hosts
    echo "127.0.0.1       $in_parameter_2" >> /etc/hosts
    exit 0
fi


##################################################################################
# development
##################################################################################
function development()
{
    if [ $(get-flag "development") == "true" ]; then
        echo
        echo "Development mode on"
        echo
    else
        echo
        echo "Development mode off"
        echo
    fi
}
if [ "$in_parameter_1" == "dev" ]; then
	development
	exit 0
fi


##################################################################################
# development
##################################################################################
function development_on()
{
    set-flag "development"
    log-ok
}
if [ "$in_parameter_1" == "dev-on" ]; then
	development_on
	exit 0
fi


##################################################################################
# development
##################################################################################
function development_off()
{
    del-flag "development"
    log-ok
}
if [ "$in_parameter_1" == "dev-off" ]; then
	development_off
	exit 0
fi



##################################################################################
# i2c-lock
##################################################################################
function i2c_lock()
{
    if [ $(get-flag "i2c_lock") == "true" ]; then
        echo
        echo "I2C lock on"
        echo
    else
        echo
        echo "I2C lock off"
        echo
    fi
}
if [ "$in_parameter_1" == "i2c-lock" ]; then
	i2c_lock
	exit 0
fi


##################################################################################
# i2c-lock
##################################################################################
function i2c_lock_on()
{
    set-flag "i2c_lock"
    systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "i2c-lock-on" ]; then
	i2c_lock_on
	exit 0
fi


##################################################################################
# i2c-lock
##################################################################################
function i2c_lock_off()
{
    del-flag "i2c_lock"
    systemctl restart steelsquid
    log-ok
}
if [ "$in_parameter_1" == "i2c-lock-off" ]; then
	i2c_lock_off
	exit 0
fi




##################################################################################
# monitor info
##################################################################################
function monitor_info()
{
    if [ $(get-flag "disable_monitor") == "true" ]; then
        echo
        echo "Display disabled"
        echo
    else
        echo
        echo "Display enabled"
        echo
    fi
}
if [ "$in_parameter_1" == "display" ]; then
	monitor_info
	exit 0
fi



##################################################################################
# Enable monitor
##################################################################################
function enable_monitor()
{
	log "Enable display"
	del-flag "disable_monitor"
    /opt/vc/bin/tvservice -p
    log-ok
}
if [ "$in_parameter_1" == "display-on" ]; then
	enable_monitor
	exit 0
fi




##################################################################################
# Disable monitor
##################################################################################
function disable_monitor()
{
	log "Disable display"
	set-flag "disable_monitor"
    /opt/vc/bin/tvservice -o
    log-ok
}
if [ "$in_parameter_1" == "display-off" ]; then
	disable_monitor
	exit 0
fi



##################################################################################
# Set/get gpu mem
##################################################################################
function gpu_mem()
{
    mem=$(get-parameter "gpu_mem")
    if [ -z "$mem" ]; then
        mem="64"
        set-parameter "gpu_mem" "64"
        sed -i '/^gpu_mem/ d' /boot/config.txt
        echo "gpu_mem=$mem" >> /boot/config.txt
    fi
    if [ "$in_parameter_2" == "" ]; then
        echo $mem
    else
        set-parameter "gpu_mem" $in_parameter_2
        sed -i '/^gpu_mem/ d' /boot/config.txt
        echo "gpu_mem=$in_parameter_2" >> /boot/config.txt
    fi
}
if [ "$in_parameter_1" == "gpu-mem" ]; then
	gpu_mem
	exit 0
fi




##################################################################################
# Trim the filesystem (SSD)
##################################################################################
if [ "$in_parameter_1" == "trim" ]; then
	for i in $(mount -l | awk '{ print $3; }'); do fstrim -v  ${i}; done
	exit 0
fi


##################################################################################
# Kill all omxplayer
##################################################################################
function omxplayer_kill()
{
    kill `ps -ax | grep 'omxplayer' | awk '{print $1}'`
    kill -9 `ps -ax | grep 'omxplayer' | awk '{print $1}'`
}
if [ "$in_parameter_1" == "omxplayer-kill" ]; then
    omxplayer_kill
	exit 0
fi

##################################################################################
# Commit to GIT and push to github
##################################################################################
function git_commit()
{
    git commit -a -m "-"
    git push steelsquidkissos master
}
if [ "$in_parameter_1" == "commit-git" ]; then
    git_commit
	exit 0
fi


##################################################################################
# Commit to this local system
# Will commit (install) the steelsquid script, python files and web files
##################################################################################
function local_commit()
{
    cp steelsquid-kiss-os.sh $steelsquid_folder/steelsquid-kiss-os.sh
    chmod 755 $steelsquid_folder/steelsquid-kiss-os.sh

	for var in "${web_root_downloads[@]}"
	do
        cp web/$(basename $var) $steelsquid_folder/web/$(basename $var)
	done

	index=1
	for var in "${python_downloads[@]}"
	do
        expand_folder=""
        if [[ $var == */modules/* ]]; then
            expand_folder="modules/"
        fi
        cp $expandf/$(basename $var) /opt/steelsquid/python$expandf/$(basename $var)
        chmod 755 /opt/steelsquid/python$expandf/$(basename $var)
        rm ${python_links[$index]} > /dev/null 2>&1
        ln -s /opt/steelsquid/python$expandf/$(basename $var) ${python_links[$index]}
        index=$[$index +1]
	done
}
if [ "$in_parameter_1" == "commit-local" ]; then
    local_commit
	exit 0
fi


##################################################################################
# Commit to this remote system
# Will commit (install) the steelsquid script, python files and web files
##################################################################################
function remote_commit()
{
    extra_array=()
    if [ -f config.txt ]; then
        log "Reading config.txt"
        echo ""
        COUNTER=1
        while read line           
        do           
            if [ "$COUNTER" = "1" ]; then
                base_remote_server=$line
            elif [ "$COUNTER" = "2" ]; then
                base_remote_port=$line
            elif [ "$COUNTER" = "3" ]; then
                base_remote_user=$line
            elif [ "$COUNTER" = "4" ]; then
                base_remote_password=$line
            elif [ "$COUNTER" = "5" ]; then
                COUNTER=5
            else
                extra_array+=("$line")
            fi
            COUNTER=$((COUNTER + 1))
        done <config.txt   
    fi
    echo "Please enter password or enter for default"
    read -s -p "$base_remote_user@$base_remote_server ($base_remote_password): " tmp_pass
    echo
    if [ "$tmp_pass" != "" ]; then
        base_remote_password=tmp_pass
    fi
    
    cstring="steelsquid-kiss-os.sh" 
    for var in "${web_root_downloads[@]}"
	do
        cstring="$cstring web/$(basename $var)"
    done

    for var in "${python_downloads[@]}"
	do
        if [[ $var != */modules/* ]]; then
            cstring="$cstring $(basename $var)"
        fi
    done
    
	log "Transmitting files"
    sshpass -p $base_remote_password scp -o StrictHostKeyChecking=no -P $base_remote_port $cstring $base_remote_user@$base_remote_server:/var/tmp

	log "Installing files"
    sshpass -p $base_remote_password ssh -o StrictHostKeyChecking=no -p $base_remote_port $base_remote_user@$base_remote_server 'sudo steelsquid commit-remote-install'

    for var in "${extra_array[@]}"
    do        
        local=${var%|*}
        remote=${var##*|}
        local="${local#"${local%%[![:space:]]*}"}"
        local="${local%"${local##*[![:space:]]}"}"
        remote="${remote#"${remote%%[![:space:]]*}"}"
        remote="${remote%"${remote##*[![:space:]]}"}"
        log "Installing extra file: $remote"
        sshpass -p $base_remote_password scp -o StrictHostKeyChecking=no -P $base_remote_port ./$local $base_remote_user@$base_remote_server:$remote
    done 

}
if [ "$in_parameter_1" == "commit-remote" ]; then
    remote_commit
	exit 0
fi
if [ "$in_parameter_1" == "commit-remote-restart" ]; then
    remote_commit
	log "Restarting service"
    sshpass -p $base_remote_password ssh -o StrictHostKeyChecking=no -p $base_remote_port $base_remote_user@$base_remote_server 'sudo steelsquid restart'
	exit 0
fi
if [ "$in_parameter_1" == "remote-restart" ]; then
	log "Restarting service"
    sshpass -p $base_remote_password ssh -o StrictHostKeyChecking=no -p $base_remote_port $base_remote_user@$base_remote_server 'sudo steelsquid restart'
	exit 0
fi


##################################################################################
# commit-remote using this to install on the local system
##################################################################################
function remote_commit_install()
{
    cp /var/tmp/steelsquid-kiss-os.sh $steelsquid_folder/steelsquid-kiss-os.sh
    chmod 755 $steelsquid_folder/steelsquid-kiss-os.sh

	for var in "${web_root_downloads[@]}"
	do
        cp /var/tmp/$(basename $var) $steelsquid_folder/web/$(basename $var)
	done

	index=1
	for var in "${python_downloads[@]}"
	do
        expand_folder=""
        if [[ $var != */modules/* ]]; then
            cp /var/tmp/$(basename $var) /opt/steelsquid/python/$(basename $var)
            chmod 755 /opt/steelsquid/python/$(basename $var)
            rm ${python_links[$index]} > /dev/null 2>&1
            ln -s /opt/steelsquid/python/$(basename $var) ${python_links[$index]}
        fi
        index=$[$index +1]
	done
}
if [ "$in_parameter_1" == "commit-remote-install" ]; then
    remote_commit_install
	exit 0
fi

##################################################################################
# commit-remote using this to install on the local system
##################################################################################
function remote_synchronize()
{
    ./steelsquid_synchronize.py
}
if [ "$in_parameter_1" == "synchronize" ]; then
    remote_synchronize
	exit 0
fi



##################################################################################
# Download and intall new version of steelsquid script
##################################################################################
function version_check()
{
	log "Version check $project_name"
	sudo mkdir -p $steelsquid_folder
	exit-check
	sudo mkdir -p $home_folder
	exit-check
    case $download in
        *.sh)
            log "Download and copy $project_name to $download"
            sudo wget --progress=dot:giga --no-check-certificate -O $home_folder/$project_name.sh_down $download
            if [ $? -ne 0 ]; then
                sudo rm $home_folder/$project_name.sh_down > /dev/null 2>&1
                do-err-exit "Unable to download from $download"
            else
                sudo mv -f $home_folder/$project_name.sh_down $home_folder/$project_name.sh
                exit-check
                sudo chown root $home_folder/$project_name.sh
                exit-check
                sudo chgrp root $home_folder/$project_name.sh
                exit-check
                sudo chmod +x $home_folder/$project_name.sh
                exit-check
                sudo rm /usr/bin/do-upgrade > /dev/null 2>&1
                sudo rm /usr/bin/steelsquid > /dev/null 2>&1
                sudo ln -s $home_folder/$project_name.sh /usr/bin/steelsquid
                exit-check
                log "Version check OK"
            fi
        ;;
        *.gz)
            log "Download, extract and copy $project_name to $download"
            sudo wget --progress=dot:giga --no-check-certificate -O $project_name.gz $download
            if [ $? -ne 0 ]; then
                sudo rm $project_name.gz > /dev/null 2>&1
                do-err-exit "Unable to download from $download"
            else
                sudo tar -zxf $project_name.gz -C $home_folder
                exit-check
                sudo chown -R root $home_folder
                exit-check
                sudo chgrp -R root $home_folder
                exit-check
                sudo chmod +x $home_folder/$project_name.sh
                exit-check
                sudo rm /usr/bin/do-upgrade > /dev/null 2>&1
                sudo rm /usr/bin/steelsquid > /dev/null 2>&1
                sudo ln -s $home_folder/$project_name.sh /usr/bin/steelsquid
                exit-check
                log "Version check OK"
            fi
        ;;
        *)
            do-err-exit "Unknown file type ($download) must be sh or gz"
        ;;
    esac
}

##################################################################################
# Update the steelsquid script
##################################################################################
if [ "$in_parameter_1" == "update" ]; then
	version_check
    echo
	exit 0
fi


##################################################################################
# Install/upgrade the system
##################################################################################
if [ "$in_parameter_1" == "upgrade" ]; then
	version_check
	sudo $home_folder/$project_name.sh skip
    echo
	exit 0
fi



##################################################################################
# Only continue if script is upgraded
##################################################################################
if [ $(get_uppdated) == "true" ]; then
	cd $home_folder
else
    help_top
    echo 
    exit 0
fi



##################################################################################
# Starting to do the job
##################################################################################
if [ $(get_installed) == "true" ]; then
	log "Upgrade $project_name"
else
	log "Install $project_name"
    set-flag "web"
    set-flag "web_authentication"
    set-flag "ssh"
    enable_lcd_auto
fi



##################################################################################
# Install python, web and img
##################################################################################
install_steelsquid_python
install_web_files
install_img_files




##################################################################################
# Update repository
##################################################################################
log "Update repository"
aptitude -y update
log "Repository updated"




##################################################################################
# Remove and install packages
##################################################################################
if [ $(get_installed) == "false" ]; then
	log "Remove and install packages"
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install systemd systemd-sysv i2c-tools alsa-firmware-loaders alsa-firmware-loaders atmel-firmware bluez-firmware dahdi-firmware-nonfree expeyes-firmware-dev firmware-adi firmware-atheros firmware-bnx2 firmware-bnx2x firmware-brcm80211 firmware-crystalhd firmware-intelwimax firmware-ipw2x00 firmware-ivtv firmware-iwlwifi firmware-libertas firmware-linux firmware-linux-free firmware-linux-nonfree firmware-myricom firmware-netxen firmware-qlogic firmware-ralink firmware-realtek firmware-samsung firmware-ti-connectivity firmware-zd1211 libertas-firmware linux-wlan-ng-firmware midisport-firmware prism2-usb-firmware-installer sigrok-firmware-fx2lafw libraspberrypi-bin libraspberrypi-dev fonts-freefont-ttf libjpeg8-dev imagemagick libv4l-dev build-essential cmake subversion dnsutils fping usbutils lshw console-data read-edid apt-utils libraspberrypi0 python-spidev
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install systemd systemd-sysv i2c-tools alsa-firmware-loaders alsa-firmware-loaders atmel-firmware bluez-firmware dahdi-firmware-nonfree expeyes-firmware-dev firmware-adi firmware-atheros firmware-bnx2 firmware-bnx2x firmware-brcm80211 firmware-crystalhd firmware-intelwimax firmware-ipw2x00 firmware-ivtv firmware-iwlwifi firmware-libertas firmware-linux firmware-linux-free firmware-linux-nonfree firmware-myricom firmware-netxen firmware-qlogic firmware-ralink firmware-realtek firmware-samsung firmware-ti-connectivity firmware-zd1211 libertas-firmware linux-wlan-ng-firmware midisport-firmware prism2-usb-firmware-installer sigrok-firmware-fx2lafw libraspberrypi-bin libraspberrypi-dev fonts-freefont-ttf libjpeg8-dev imagemagick libv4l-dev build-essential cmake subversion dnsutils fping usbutils lshw console-data read-edid apt-utils libraspberrypi0 python-spidev
    exit-check 
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install build-essential python-dbus python-pexpect python-dev python-setuptools python-pip python-pam python-smbus psmisc git libudev-dev libmount-dev python-imaging pkg-config libglib2.0-dev whois
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install build-essential python-dbus python-pexpect python-dev python-setuptools python-pip python-pam python-smbus psmisc git libudev-dev libmount-dev python-imaging pkg-config libglib2.0-dev whois
    exit-check 
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install deborphan network-manager network-manager-openvpn dash nano sudo aptitude udev ntfs-3g console-setup beep ecryptfs-utils alsa-utils alsa-base va-driver-all vdpau-va-driver
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install deborphan network-manager network-manager-openvpn dash nano sudo aptitude udev ntfs-3g console-setup beep ecryptfs-utils alsa-utils alsa-base va-driver-all vdpau-va-driver
    exit-check 
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install telnet secure-delete beep sysstat openssh-client cifs-utils smbclient keyutils sshfs curl samba-common lsof mc fgetty ftp htop elinks screenie nload mtr-tiny lzma zip unzip unrar-free p7zip-full bzip2 whiptail parted lua5.1 aria2 python-serial python-numpy python2.7-numpy python-paramiko zlib1g zlib1g-dev libfreetype6-dev ttf-anonymous-pro python-picamera
    aptitude -R -o Aptitude::Cmdline::ignore-trust-violations=true -y install telnet secure-delete beep sysstat openssh-client cifs-utils smbclient keyutils sshfs curl samba-common lsof mc fgetty ftp htop elinks screenie nload mtr-tiny lzma zip unzip unrar-free p7zip-full bzip2 whiptail parted lua5.1 aria2 python-serial python-numpy python2.7-numpy python-paramiko zlib1g zlib1g-dev libfreetype6-dev ttf-anonymous-pro python-picamera
    exit-check 
    aptitude -y purge cron ifupdown rsyslog vim-common vim-tiny hdparm keyboard-configuration console-setup console-setup-linux
    aptitude -y purge cron ifupdown rsyslog vim-common vim-tiny hdparm keyboard-configuration console-setup console-setup-linux
    exit-check 
	log "Packages removed and installed"
fi



##################################################################################
# Upgrade System
##################################################################################
log "Upgrade system"
aptitude -y -o Dpkg::Options::="--force-confnew" full-upgrade
exit-check
dpkg --configure -a
exit-check
log "System upgraded"



##################################################################################
# Update firmware
##################################################################################
#aptitude install -y raspberrypi-bootloader libraspberrypi0 libraspberrypi-{bin,dev}
#aptitude reinstall -y linux-image-rpi-rpfv raspberrypi-bootloader-nokernel libraspberrypi0 libraspberrypi-{bin,dev,doc}
#apt-get install --reinstall linux-image-rpi-rpfv raspberrypi-bootloader-nokernel libraspberrypi0 libraspberrypi-{bin,dev,doc}
#if [ $(is-raspberry-pi) == "true" ]; then
#    log "Update firmware"
#    sudo curl -L --output /usr/bin/rpi-update https://raw.github.com/Hexxeh/rpi-update/master/rpi-update && sudo chmod +x /usr/bin/rpi-update
#    rpi-update
#fi




##################################################################################
# Install rpi GPIO
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Install rpi GPIO"
    easy_install -U distribute
    pip install rpi.gpio
    pip install --upgrade rpi.gpio
    log "Rpi GPIO installed"
fi


##################################################################################
# Install PIL
##################################################################################
log "Install PIL"
easy_install -U distribute
pip install pillow 
pip install --upgrade pillow 


##################################################################################
# Install inotifyx
##################################################################################
log "Install inotifyx"
pip install inotifyx



##################################################################################
# event link
##################################################################################
log "event link"
rm /usr/bin/event
ln -s /opt/steelsquid/python/steelsquid_kiss_boot.py /usr/bin/event



##################################################################################
# Install Adafruit-Raspberry-Pi-Python-Code
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Install Adafruit-Raspberry-Pi-Python-Code"
    cd /usr/local/lib/python2.7/dist-packages
    rm Adafruit_I2C.py
    wget https://raw.githubusercontent.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/master/Adafruit_I2C/Adafruit_I2C.py
    rm Adafruit_PWM_Servo_Driver.py
    wget https://raw.githubusercontent.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/master/Adafruit_PWM_Servo_Driver/Adafruit_PWM_Servo_Driver.py
    rm Adafruit_MCP230xx.py
    wget https://raw.githubusercontent.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/master/Adafruit_MCP230xx/Adafruit_MCP230xx.py
    rm Adafruit_ADS1x15.py
    wget https://raw.githubusercontent.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/master/Adafruit_ADS1x15/Adafruit_ADS1x15.py
    rm Adafruit_MCP4725.py
    wget https://raw.githubusercontent.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/master/Adafruit_MCP4725/Adafruit_MCP4725.py
    cd /tmp
    git clone https://github.com/adafruit/Adafruit_Nokia_LCD.git
    cd Adafruit_Nokia_LCD
    python setup.py install -f -O2
    log "Adafruit-Raspberry-Pi-Python-Code installed"
fi


##################################################################################
# Install Piborg diable
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Install Piborg diable"
    cd /usr/local/lib/python2.7/dist-packages
    wget http://www.piborg.org/downloads/diablo/examples.zip
    unzip examples.zip
    log "Piborg diable installed"
fi

##################################################################################
# Install picamera
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Install picamera"
    easy_install -U distribute
    pip install picamera
    pip install --upgrade picamera
fi


##################################################################################
# Install RPIO
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Install RPIO"
    easy_install -U RPIO
    pip install RPIO
    pip install --upgrade RPIO
fi


##################################################################################
# Set pythonpath
##################################################################################
log "Set pythonpath"
mkdir /opt/steelsquid/python
echo "export PYTHONPATH=/opt/steelsquid/python:/usr/lib/python3/dist-packages" > /etc/profile.d/pythonpath.sh
mkdir /opt/steelsquid/python/modules
echo "" >> /opt/steelsquid/python/modules/__init__.py



##################################################################################
# Download and install WiringPi
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Download and install WiringPi"
    pip install wiringpi2
    git clone git://git.drogon.net/wiringPi
    cd wiringPi
    ./build
fi


##################################################################################
# Create direcorys and links
##################################################################################
log "Create direcorys and links"
mkdir $steelsquid_folder/flags
mkdir $steelsquid_folder/lists
mkdir $steelsquid_folder/parameters
mkdir $steelsquid_folder/pem
mkdir $steelsquid_folder/web
mkdir $steelsquid_folder/web/img
mkdir $steelsquid_folder/web/css
mkdir $steelsquid_folder/web/js
mkdir $steelsquid_folder/web/font
mkdir $steelsquid_folder/web/snapshots
mkdir $steelsquid_folder/vpn
chmod -R 755 /opt/steelsquid/python/
chmod 755 $steelsquid_folder/steelsquid-kiss-os.sh
mkdir /mnt/network
mkdir /mnt/network/Documents
mkdir /mnt/network/Downloads
mkdir /mnt/network/Music
mkdir /mnt/network/Pictures
mkdir /mnt/network/Videos
mkdir /root/Documents
mkdir /root/Downloads
mkdir /root/Music
mkdir /root/Pictures
mkdir /root/Videos
ln -s /media /root/Media


##################################################################################
# Download and install ldm
##################################################################################
log "Download and install ldm"
cd /tmp
git clone https://github.com/LemonBoy/ldm
cd ldm
make
make install
systemctl enable ldm
sed -i "/ExecStart/c\ExecStart=\/usr\/bin\/ldm -u root -p \/media -c \/usr\/bin\/ldm-shout" /usr/lib/systemd/system/ldm.service
sed -i '/EnvironmentFile/d' /usr/lib/systemd/system/ldm.service
systemctl --system daemon-reload
systemctl enable ldm
echo "#"\!"/bin/bash" > /usr/bin/ldm-shout
echo "if [ \"\$LDM_ACTION\" == \"mount\" ]; then" >> /usr/bin/ldm-shout
echo "sudo event mount usb \"\$LDM_NODE\" \"\$LDM_MOUNTPOINT\"" >> /usr/bin/ldm-shout
echo "else" >> /usr/bin/ldm-shout
echo "sudo event umount usb \"\$LDM_NODE\" \"\$LDM_MOUNTPOINT\"" >> /usr/bin/ldm-shout
echo "fi" >> /usr/bin/ldm-shout
chmod +x /usr/bin/ldm-shout



##################################################################################
# Camera sreaming
##################################################################################
log "Download and install camera streaming"
cd /opt
rm -r mjpg-streamer*
sudo ln -s /usr/include/linux/videodev2.h /usr/include/linux/videodev.h
svn co https://svn.code.sf.net/p/mjpg-streamer/code mjpg-streamer
cd mjpg-streamer/mjpg-streamer
make
mkdir /opt/mjpg-streamer-pi
cd /opt/mjpg-streamer-pi
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd /opt/mjpg-streamer-pi/mjpg-streamer/mjpg-streamer-experimental
make
if [ $(has-parameter "stream_frames") == "false" ]; then
    $(set-parameter "stream_frames" "8")
fi


##################################################################################
# Fix KBD
##################################################################################
log "Fix KBD"
sed -i '/^BLANK_TIME/ d' /etc/kbd/config
sed -i '/^BLANK_DPMS/ d' /etc/kbd/config
sed -i '/^POWERDOWN_TIME/ d' /etc/kbd/config
echo "BLANK_TIME=0" >> /etc/kbd/config
echo "BLANK_DPMS=off" >> /etc/kbd/config
echo "POWERDOWN_TIME=0" >> /etc/kbd/config



##################################################################################
# Download and install omxplayer
##################################################################################
if [ $(is-raspberry-pi) == "true" ]; then
    log "Download and install omxplayer"
    wget --progress=dot:giga --no-check-certificate -O /tmp/omxplayer.deb http://omxplayer.sconde.net/builds/omxplayer_0.3.5~git20140409~46616c5_armhf.deb
    if [ $? -ne 0 ]; then
        do-err-exit "Unable to download omxplayer"
    fi
    dpkg -i /tmp/omxplayer.deb
fi



##################################################################################
# Optimize fstab (noatime,nodiratime)
##################################################################################
log "Optimize fstab (noatime,nodiratime)"
mkdir -p /opt/steelsquid/web/tmpfs
sed -i 's/errors=remount-ro,noatime /errors=remount-ro,defaults,noatime,nodiratime /g' /etc/fstab
sed -i '/tmpfs/d' /etc/fstab
sed -i '/none /d' /etc/fstab
echo "none   /var/log   tmpfs   noatime,nodiratime,rw,mode=1777,nodev,nosuid,noexec,size=32m    0   0" >> /etc/fstab
echo "none   /tmp       tmpfs   noatime,nodiratime,rw,mode=1777,nodev,nosuid,size=256m   0   0" >> /etc/fstab
echo "none   /opt/steelsquid/web/tmpfs       tmpfs   noatime,nodiratime,rw,mode=1777,nodev,nosuid,size=256m   0   0" >> /etc/fstab
echo "/tmp   /var/tmp   none    noatime,nodiratime,rw,mode=1777,nodev,nosuid,bind        0   0" >> /etc/fstab
log "Fstab Optimized"



##################################################################################
# Fix bluetooth
##################################################################################
log "Fix bluetooth"
sed -i 's/.*DiscoverableTimeout.*/DiscoverableTimeout = 0/g' /etc/bluetooth/main.conf
sed -i 's/.*PairableTimeout.*/PairableTimeout = 0/g' /etc/bluetooth/main.conf



##################################################################################
# Fix apt
##################################################################################
log "Fix noexec apt"
echo "DPkg::Pre-Invoke{\"mount -o remount,exec /tmp\";};" > /etc/apt/apt.conf
echo "DPkg::Post-Invoke {\"mount -o remount,rw,noexec,nosuid,nodev /tmp\";};" >> /etc/apt/apt.conf



##################################################################################
# Some optimization
##################################################################################
log "Some optimization"
sed -i '/vm.dirty/d' /etc/sysctl.conf
sed -i '/vm.overcommit_ratio/d' /etc/sysctl.conf
sed -i '/vm.laptop_mode/d' /etc/sysctl.conf
sed -i '/fs.file-max/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_synack_retries/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_rfc1337/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_fin_timeout/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_keepalive_time/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_keepalive_probes/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_keepalive_intvl/d' /etc/sysctl.conf
sed -i '/net.core.rmem_default/d' /etc/sysctl.conf
sed -i '/net.core.rmem_max/d' /etc/sysctl.conf
sed -i '/net.core.wmem_default/d' /etc/sysctl.conf
sed -i '/net.core.wmem_max /d' /etc/sysctl.conf
sed -i '/net.core.somaxconn/d' /etc/sysctl.conf
sed -i '/net.core.netdev_max_backlog/d' /etc/sysctl.conf
sed -i '/net.core.optmem_max/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_mem/d' /etc/sysctl.conf
sed -i '/net.ipv4.udp_mem/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_rmem/d' /etc/sysctl.conf
sed -i '/net.ipv4.udp_rmem_min/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_wmem/d' /etc/sysctl.conf
sed -i '/net.ipv4.udp_wmem_min/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_max_tw_buckets/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_tw_recycle/d' /etc/sysctl.conf
sed -i '/net.ipv4.tcp_tw_reuse/d' /etc/sysctl.conf
sed -i '/net.ipv4.icmp_echo_ignore_all/d' /etc/sysctl.conf
sed -i '/net.ipv4.icmp_echo_ignore_broadcasts/d' /etc/sysctl.conf
echo "vm.dirty_background_ratio = 5" >> /etc/sysctl.conf
echo "vm.dirty_ratio = 20" >> /etc/sysctl.conf
echo "vm.dirty_expire_centisecs = 1000" >> /etc/sysctl.conf
echo "vm.overcommit_ratio = 2" >> /etc/sysctl.conf
echo "vm.laptop_mode = 5" >> /etc/sysctl.conf
echo "fs.file-max = 2097152" >> /etc/sysctl.conf
echo "net.ipv4.tcp_synack_retries = 2" >> /etc/sysctl.conf
echo "net.ipv4.tcp_rfc1337 = 1" >> /etc/sysctl.conf
echo "net.ipv4.tcp_fin_timeout = 15" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_time = 300" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_probes = 5" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_intvl = 15" >> /etc/sysctl.conf
echo "net.core.rmem_default = 31457280" >> /etc/sysctl.conf
echo "net.core.rmem_max = 12582912" >> /etc/sysctl.conf
echo "net.core.wmem_default = 31457280" >> /etc/sysctl.conf
echo "net.core.wmem_max = 12582912" >> /etc/sysctl.conf
echo "net.core.somaxconn = 6553" >> /etc/sysctl.conf
echo "net.core.netdev_max_backlog = 65536" >> /etc/sysctl.conf
echo "net.core.optmem_max = 25165824" >> /etc/sysctl.conf
echo "net.ipv4.tcp_mem = 65536 131072 262144" >> /etc/sysctl.conf
echo "net.ipv4.udp_mem = 65536 131072 262144" >> /etc/sysctl.conf
echo "net.ipv4.tcp_rmem = 8192 87380 16777216" >> /etc/sysctl.conf
echo "net.ipv4.udp_rmem_min = 16384" >> /etc/sysctl.conf
echo "net.ipv4.tcp_wmem = 8192 65536 16777216" >> /etc/sysctl.conf
echo "net.ipv4.udp_wmem_min = 16384" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_tw_buckets = 1440000" >> /etc/sysctl.conf
echo "net.ipv4.tcp_tw_recycle = 1" >> /etc/sysctl.conf
echo "net.ipv4.tcp_tw_reuse = 1" >> /etc/sysctl.conf
echo "net.ipv4.icmp_echo_ignore_all = 1" >> /etc/sysctl.conf
echo "net.ipv4.icmp_echo_ignore_broadcasts = 1" >> /etc/sysctl.conf
echo "*         hard    nofile      500000" > /etc/security/limits.conf
echo "*         soft    nofile      500000" >> /etc/security/limits.conf
echo "root      hard    nofile      500000" >> /etc/security/limits.conf
echo "root      soft    nofile      500000" >> /etc/security/limits.conf
sed -i '/pam_limits.so/d' /etc/pam.d/sshd
echo "session    required   pam_limits.so" >> /etc/pam.d/sshd
sed -i '/pam_limits.so/d' /etc/pam.d/su
echo "session    required   pam_limits.so" >> /etc/pam.d/su
sed -i '/session required pam_limits.so/d' /etc/pam.d/common-session
echo "session required pam_limits.so" >> /etc/pam.d/common-session
sed -i '/session required pam_limits.so/d' /etc/pam.d/common-session-noninteractive
echo "session required pam_limits.so" >> /etc/pam.d/common-session-noninteractive
sed -i '/kernel.printk/d' /etc/sysctl.conf
echo "kernel.printk = 3 3 3 3" >> /etc/sysctl.conf
log "Some optimization done"



##################################################################################
# Boot fix
##################################################################################
log "Boot fix"
sed -i '/TMPTIME=/c\TMPTIME=-1' /etc/default/rcS
sed -i '/VERBOSE=/c\VERBOSE=no' /etc/default/rcS
sed -i 's|\tclean_tmp |\t#clean_tmp |g' /lib/init/bootclean.sh
sed -i 's|\tclean /run/shm |\t#clean /run/shm |g' /lib/init/bootclean.sh



##################################################################################
# WIFI sleep
##################################################################################
log "WIFI sleep fix"
echo "options 8192cu rtw_power_mgnt=0" > /etc/modprobe.d/8192cu.conf



##################################################################################
# Create /etc/environment
##################################################################################
log "Create /etc/environment"
echo "LANGUAGE=en_US.UTF-8" > /etc/environment
echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "LANG=en_US.UTF-8" >> /etc/environment
echo "LC_TYPE=en_US.UTF-8" >> /etc/environment




##################################################################################
# Optimize boot
##################################################################################
log "Optimize boot"
rm /boot/cmdline.txt > /dev/null 2>&1
echo "dwc_otg.fiq_fix_enable dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootfstype=ext4 rootflags=commit=10,data=writeback elevator=noop noatime nodiratime data=writeback rootwait quiet loglevel=0 logo.nologo consoleblank=0" >> /boot/cmdline.txt
log "Boot optimized"



##################################################################################
# Change to from bash to dash
##################################################################################
log "Change to from bash to dash"
dpkg-reconfigure -f noninteractive dash
log "Change from bash to dash done"



#################################################################################
# Generate locale
##################################################################################
log "Generate locale"
echo "LANG=en_US.UTF-8" > /etc/default/locale
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
log "Generate locale"



##################################################################################
# Generate locale
##################################################################################
log "Set keymap"
if [ $(has-parameter "keyboard") == "false" ]; then
    $(set-parameter "keyboard" "se-latin1")
    loadkeys se-latin1
fi


##################################################################################
# Change host name to steelsquid-kiss-os
##################################################################################
response=$(grep -lir "pi" /etc/hostname)
if [ "$response" == "/etc/hostname" ]; then
    log "Change host name to steelsquid-kiss-os"
    sed -i 's/pi/steelsquid-kiss-os/g' /etc/hostname
    sed -i 's/pi/steelsquid-kiss-os/g' /etc/hosts
    log "Hostname changed to steelsquid-kiss-os"
fi



##################################################################################
# Enable root login
##################################################################################
log "Enable root login"
sed -i '/PermitRootLogin /c\PermitRootLogin yes' /etc/ssh/sshd_config



##################################################################################
# Enable i2c
##################################################################################
log "Enable i2c"
response=$(grep -lir "i2c-bcm2708" /etc/modules)
if [ "$response" != "/etc/modules" ]; then
	echo "i2c-bcm2708" >> /etc/modules
	echo "i2c-dev" >> /etc/modules
fi
log "I2c enabled"


##################################################################################
# disable ipv6
##################################################################################
echo "alias net-pf-10 off" > /etc/modprobe.d/ipv6.conf
echo "alias ipv6 off" >> /etc/modprobe.d/ipv6.conf



##################################################################################
# Setting up fuse
##################################################################################
log "Setting up fuse"
sed -i '/user_allow_other/ d' /etc/fuse.conf
echo "user_allow_other" >> /etc/fuse.conf



##################################################################################
# Removing some logsave stuff
##################################################################################
log "Removing some logsave stuff"
response=$(grep -lir "killall -9 logsave" /etc/init.d/sendsigs)
if [ "$response" != "/etc/init.d/sendsigs" ]; then
	sed -i '/Asking all remaining processes to terminate/ a\        killall -9 logsave' /etc/init.d/sendsigs
fi
log "Removing some logsave stuff fixed"


##################################################################################
# Set volume and store
##################################################################################
log "Set volume and store"
amixer set PCM unmute
amixer set PCM 90%
alsactl store
log "Volume stored"



##################################################################################
# Blank screen fix
##################################################################################
log "Blank screen fix"
sed -i '/BLANK_TIME=/c\BLANK_TIME=0' /etc/kbd/config
sed -i '/POWERDOWN_TIME=/c\POWERDOWN_TIME=0' /etc/kbd/config


##################################################################################
# Configure systemd
##################################################################################
log "Configure systemd"
sed -i 's/^#Storage.*/Storage=none/' /etc/systemd/journald.conf
sed -i 's/^#Compress.*/Compress=no/' /etc/systemd/journald.conf
sed -i 's/^#Seal.*/Seal=no/' /etc/systemd/journald.conf
sed -i 's/^#SplitMode.*/SplitMode=none/' /etc/systemd/journald.conf
sed -i 's/^#LogLevel.*/LogLevel=emerg/' /etc/systemd/system.conf
sed -i 's/^#LogTarget.*/LogTarget=null/' /etc/systemd/system.conf
sed -i 's/^#LogColor.*/LogColor=no/' /etc/systemd/system.conf
sed -i 's/^#ShowStatus.*/ShowStatus=no/' /etc/systemd/system.conf
sed -i 's/^#DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/system.conf
sed -i 's/^#LogLevel.*/LogLevel=crit/' /etc/systemd/user.conf
sed -i 's/^#LogTarget.*/LogTarget=null/' /etc/systemd/user.conf
sed -i 's/^#LogColor.*/LogColor=no/' /etc/systemd/user.conf
sed -i 's/^#DefaultStandardOutput.*/DefaultStandardOutput=null/' /etc/systemd/user.conf
sed -i 's/^#NAutoVTs.*/NAutoVTs=1/' /etc/systemd/logind.conf
sed -i 's/^#ReserveVT.*/ReserveVT=1/' /etc/systemd/logind.conf
sed -i '/StandardOutput/d' /lib/systemd/system/systemd-fsck-root.service
sed -i '/StandardError/d' /lib/systemd/system/systemd-fsck-root.service
echo "StandardOutput=null" >> /lib/systemd/system/systemd-fsck-root.service
echo "StandardError=null" >> /lib/systemd/system/systemd-fsck-root.service
sed -i '/StandardOutput/d' /lib/systemd/system/systemd-fsck@.service
sed -i '/StandardError/d' /lib/systemd/system/systemd-fsck@.service
echo "StandardOutput=null" >> /lib/systemd/system/systemd-fsck@.service
echo "StandardError=null" >> /lib/systemd/system/systemd-fsck@.service
log_off


##################################################################################
# Disable services
##################################################################################
log "Disable services"
update-rc.d -f bootlogs remove
update-rc.d -f motd remove
update-rc.d -f pppd-dns remove   
update-rc.d -f rpcbind remove
update-rc.d -f rsync remove
update-rc.d -f mountnfs-bootclean.sh remove
update-rc.d -f mountnfs.sh remove
update-rc.d -f umountnfs.sh remove
update-rc.d -f triggerhappy remove
systemctl mask polkitd.servic
systemctl disable systemd-journald.service
systemctl mask console-setup.service
systemctl mask systemd-logind.service
systemctl mask sys-kernel-debug.mount
systemctl mask cryptsetup.target
systemctl mask graphical.target
systemctl mask remote-fs-pre.target
systemctl mask remote-fs.target
systemctl mask alsa-restore.service
systemctl mask sysstat.service
systemctl mask kbd.service
log "Services disabled"



##################################################################################
# Remove tty2 to 6 and remove getty on Raspberry Pi serial line
##################################################################################
log "Remove tty2 to 6"
sed -i '/23:respawn:\/sbin\/getty 38400 tty/d' /etc/inittab
sed -i 's/1:2345:respawn:\/bin\/login -f root tty1 <\/dev\/tty1 >\/dev\/tty1 2>&1 # RPICFG_TO_DISABLE/1:2345:respawn:\/sbin\/getty --noclear 38400 tty1/g' /etc/inittab
sed -i '/T0:23:respawn:\/sbin\/getty -L ttyAMA0 115200 vt100/d' /etc/inittab



##################################################################################
# Enable startup service
##################################################################################
log "Enable startup service"
echo "[Unit]" > /etc/systemd/system/steelsquid.service
echo "Description=Steelsquid" >> /etc/systemd/system/steelsquid.service
echo "Before=shutdown.target reboot.target halt.target" >> /etc/systemd/system/steelsquid.service
echo "" >> /etc/systemd/system/steelsquid.service
echo "[Service]" >> /etc/systemd/system/steelsquid.service
echo "ExecStart=/usr/bin/steelsquid-boot start" >> /etc/systemd/system/steelsquid.service
echo "ExecStopPost=/usr/bin/shout \"Steelsquid service closed.\nIf you shutdown the computer or restart the steelsquid service this is OK.\nIf this is a error (nothing more happens) it is probably in steelsquid-boot.py\nYou can enable logging for more info: steelsquid log-on\nAlso sheck if steelsquid-boot proces is running: ps -ef|grep steelsquid-boot\nIf not try: steelsquid-boot start\nAnd check for errors...\"" >> /etc/systemd/system/steelsquid.service
echo "KillSignal=SIGINT" >> /etc/systemd/system/steelsquid.service
echo "TimeoutStopSec=4" >> /etc/systemd/system/steelsquid.service
echo "" >> /etc/systemd/system/steelsquid.service
echo "[Install]" >> /etc/systemd/system/steelsquid.service
echo "WantedBy=multi-user.target" >> /etc/systemd/system/steelsquid.service
systemctl --system daemon-reload
systemctl enable steelsquid


##################################################################################
# Enable networkmanager
##################################################################################
log "Enable networkmanager"
rm /etc/network/interfaces > /dev/null 2>&1
echo "auto lo" >> /etc/network/interfaces
echo "iface lo inet loopback" >> /etc/network/interfaces
echo "[Adding or changing system-wide NetworkManager connections]" > /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
echo "Identity=unix-group:netdev;unix-group:sudo" >> /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
echo "Action=org.freedesktop.NetworkManager.*" >> /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
echo "ResultAny=yes" >> /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
echo "ResultInactive=yes" >> /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
echo "ResultActive=yes" >> /etc/polkit-1/localauthority/10-vendor.d/org.freedesktop.NetworkManager.pkla
log "Networkmanager enabled"


##################################################################################
# Configure network manager dispatch script
##################################################################################
log "Configure network manager dispatch script"
echo "#! /bin/sh" > /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "if [ \"\$2\" = \"up\" ]; then" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "event network" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "fi" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "if [ \"\$2\" = \"down\" ]; then" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "event network" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "fi" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "if [ \"\$2\" = \"vpn-up\" ]; then" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "event vpn up" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "fi" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "if [ \"\$2\" = \"vpn-down\" ]; then" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "event vpn down" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
echo "fi" >> /etc/NetworkManager/dispatcher.d/99steelsquid.sh
chmod 755 /etc/NetworkManager/dispatcher.d/99steelsquid.sh



##################################################################################
# Configure network manager logging
##################################################################################
log "Configure network manager logging"
echo "[main]" > /etc/NetworkManager/NetworkManager.conf
echo "plugins=ifupdown,keyfile" >> /etc/NetworkManager/NetworkManager.conf
echo "" >> /etc/NetworkManager/NetworkManager.conf
echo "[ifupdown]" >> /etc/NetworkManager/NetworkManager.conf
echo "managed=false" >> /etc/NetworkManager/NetworkManager.conf
echo "" >> /etc/NetworkManager/NetworkManager.conf
echo "[logging]" >> /etc/NetworkManager/NetworkManager.conf
echo "level=ERR" >> /etc/NetworkManager/NetworkManager.conf



##################################################################################
# Fix config.txt
##################################################################################
log "Fix config.txt"
echo "disable_overscan=1" > /boot/config.txt
echo "disable_splash=1" >> /boot/config.txt
echo "boot_delay=0" >> /boot/config.txt
echo "dtparam=i2c_arm=on" >> /boot/config.txt
echo "dtparam=spi=on" >> /boot/config.txt
#echo "dtparam=i2s=on" >> /boot/config.txt

if [ $(get-flag "camera") == "true" ]; then
    enable_camera
else
    disable_camera
fi
if [ $(get-flag "disable_monitor") == "true" ]; then
    disable_monitor
else
    enable_monitor
fi



##################################################################################
# Configure pam
##################################################################################
log "Configure PAM"
sed -i "/FAILLOG_ENAB\t/c\FAILLOG_ENAB\tno" /etc/login.defs
sed -i "/SYSLOG_SU_ENAB\t/c\FAILLOG_ENAB\tno" /etc/login.defs
sed -i "/SYSLOG_SG_ENAB\t/c\FAILLOG_ENAB\tno" /etc/login.defs
sed -i '/pam_lastlog.so/d' /etc/pam.d/login
sed -i '/pam_motd.so/d' /etc/pam.d/login
sed -i '/pam_mail.so/d' /etc/pam.d/login
sed -i '/pam_lastlog.so/d' /etc/pam.d/sshd
sed -i '/pam_motd.so/d' /etc/pam.d/sshd
sed -i '/pam_mail.so/d' /etc/pam.d/sshd



##################################################################################
# Configure user/groups
##################################################################################
log "Configure user/groups"
groupadd admin > /dev/null 2>&1
groupadd samba > /dev/null 2>&1
groupadd wheel > /dev/null 2>&1
groupadd network > /dev/null 2>&1
groupadd fuse > /dev/null 2>&1
groupadd plugdev > /dev/null 2>&1
groupadd sudo > /dev/null 2>&1
usermod -a -G admin root
usermod -a -G samba root
usermod -a -G wheel root
usermod -a -G network root
usermod -a -G audio root
usermod -a -G netdev root
usermod -a -G plugdev root
usermod -a -G fuse root
usermod -a -G sudo root
usermod -a -G video root


##################################################################################
# Disable swap
##################################################################################
log "Disable swap"
swapoff -a
echo "0" > /proc/sys/vm/swappiness
sed -i '/vm.swappiness=/d' /etc/sysctl.conf
echo "vm.swappiness=0" >> /etc/sysctl.conf
dphys-swapfile swapoff > /dev/null 2>&1
dphys-swapfile uninstall > /dev/null 2>&1
sed -i '/CONF_SWAPSIZE=/d' /etc/dphys-swapfile
echo "CONF_SWAPSIZE=0" >> /etc/dphys-swapfile
aptitude -y purge dphys-swapfile > /dev/null 2>&1
rm /etc/dphys-swapfile



##################################################################################
# Fix video
##################################################################################
echo 'SUBSYSTEM=="vchiq",GROUP="video",MODE="0660"' > /etc/udev/rules.d/10-vchiq-permissions.rules



##################################################################################
# Generate aria2 shout ok command
##################################################################################
log "Generate aria2 shout ok command"
echo "#"\!"/bin/bash" > /usr/bin/aria2shoutok
echo "event shout \"Download complete\\n\$3\"" >> /usr/bin/aria2shoutok
echo "exit 0" >> /usr/bin/aria2shoutok
chmod +x /usr/bin/aria2shoutok


##################################################################################
# Generate termfix script
##################################################################################
log "Generate termfix script"
echo "#"\!"/bin/bash" > /usr/bin/termfix
echo "export TERM=\"linux\"" >> /usr/bin/termfix
echo "setterm --reset > /dev/tty1" >> /usr/bin/termfix
#echo "setterm --powersave off > /dev/tty1" >> /usr/bin/termfix
echo "setterm --blank 0 > /dev/tty1" >> /usr/bin/termfix
echo "setterm --powerdown 0 > /dev/tty1" >> /usr/bin/termfix
echo "setterm --bold on > /dev/tty1" >> /usr/bin/termfix
echo "setterm --cursor off > /dev/tty1" >> /usr/bin/termfix
echo "loadkeys \$1" >> /usr/bin/termfix
echo "exit 0" >> /usr/bin/termfix
chmod +x /usr/bin/termfix


##################################################################################
# Generate test python file
##################################################################################
log "Generate test python file"
if [ $(get-flag "expanded") == "false" ]; then
    echo "#"\!"/usr/bin/python -OO" > /root/test.py
    echo "import steelsquid_kiss_global" >> /root/test.py
    echo "import steelsquid_utils" >> /root/test.py
    echo "import steelsquid_pi" >> /root/test.py
    echo "import thread" >> /root/test.py
    echo "import time" >> /root/test.py
    echo "import sys" >> /root/test.py
    echo "import os" >> /root/test.py
    echo "" >> /root/test.py
    echo "" >> /root/test.py
    chmod +x /root/test.py
fi


##################################################################################
# Generate aria2 shout err command
##################################################################################
log "Generate aria2 shout err command"
echo "#"\!"/bin/bash" > /usr/bin/aria2shouterr
echo "event shout \"Download error\\n\$3\"" >> /usr/bin/aria2shouterr
echo "exit 0" >> /usr/bin/aria2shouterr
chmod +x /usr/bin/aria2shouterr



##################################################################################
# Generate shout command
##################################################################################
log "Generate shout command"
echo "#"\!"/bin/bash" > /usr/bin/shout
echo "export aa=\"\$@\"" >> /usr/bin/shout
echo "echo -e \"\$aa\" | wall -n > /dev/null 2>&1" >> /usr/bin/shout
echo "echo -e \"\\n\$aa\" | tee /dev/tty1" >> /usr/bin/shout
echo "exit 0" >> /usr/bin/shout
chmod +x /usr/bin/shout



##################################################################################
# Generate notify command
##################################################################################
log "Generate notify command"
echo "#"\!"/bin/bash" > /usr/bin/notify
echo "export aa=\"\$@\"" >> /usr/bin/notify
echo "shout \"\$aa\"" >> /usr/bin/notify
echo "python -c \"import steelsquid_utils; steelsquid_utils.mail('\$aa')\"" >> /usr/bin/notify
echo "exit 0" >> /usr/bin/notify
chmod +x /usr/bin/notify


##################################################################################
# Generate mail command
##################################################################################
log "Generate mail command"
echo "#"\!"/bin/bash" > /usr/bin/mail
echo "python -c \"import steelsquid_utils; steelsquid_utils.mail('\$aa')\"" >> /usr/bin/mail
echo "exit 0" >> /usr/bin/mail
chmod +x /usr/bin/mail


##################################################################################
# Generate ff
##################################################################################
log "Generate ff command"
echo "#"\!"/bin/bash" > /usr/bin/ff
echo "function echb()" >> /usr/bin/ff
echo "{" >> /usr/bin/ff
echo "    tput bold" >> /usr/bin/ff
echo "    echo -e \$@" >> /usr/bin/ff
echo "    tput sgr0" >> /usr/bin/ff
echo "}" >> /usr/bin/ff
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/ff
echo "    echo " >> /usr/bin/ff
echo "    echb \"search for file recursively by name\"" >> /usr/bin/ff
echo "    echo \"ff '<directory>' '<partOfFileName>'\"" >> /usr/bin/ff
echo "    echo " >> /usr/bin/ff
echo "    echb \"search for file recursively by name and content in file\"" >> /usr/bin/ff
echo "    echo \"ff '<directory>' '<partOfFileName>' '<partOfTextInFile>'\"" >> /usr/bin/ff
echo "    echo" >> /usr/bin/ff
echo "elif [ -z \"\$3\" ]; then" >> /usr/bin/ff
echo "    find \$1 -iname \"\$2\"" >> /usr/bin/ff
echo "else" >> /usr/bin/ff
echo "    find \$1 -type f -iname \"\$2\" -exec grep -l \"\$3\" {} + 2>/dev/null" >> /usr/bin/ff
echo "fi" >> /usr/bin/ff
echo "exit 0" >> /usr/bin/ff
chmod +x /usr/bin/ff


##################################################################################
# Generate ps-cpu
##################################################################################
log "Generate ps-cpu command"
echo "#"\!"/bin/bash" > /usr/bin/ps-cpu
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/ps-cpu
echo "    ps -eo sid,user,nice,rss,pcpu,command --sort pcpu" >> /usr/bin/ps-cpu
echo "else" >> /usr/bin/ps-cpu
echo "    ps -eo sid,user,nice,rss,pcpu,command --sort pcpu | grep -i \"SID USER\\|\$1\"" >> /usr/bin/ps-cpu
echo "fi" >> /usr/bin/ps-cpu
echo "exit 0" >> /usr/bin/ps-cpu
chmod +x /usr/bin/ps-cpu


##################################################################################
# Generate ps-mem
##################################################################################
log "Generate ps-mem command"
echo "#"\!"/bin/bash" > /usr/bin/ps-mem
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/ps-mem
echo "    ps -eo sid,user,nice,rss,pcpu,command --sort rss" >> /usr/bin/ps-mem
echo "else" >> /usr/bin/ps-mem
echo "    ps -eo sid,user,nice,rss,pcpu,command --sort rss | grep -i \"SID USER\\|\$1\"" >> /usr/bin/ps-mem
echo "fi" >> /usr/bin/ps-mem
echo "exit 0" >> /usr/bin/ps-mem
chmod +x /usr/bin/ps-mem



##################################################################################
# Generate mem
##################################################################################
log "Generate mem command"
echo "#"\!"/bin/bash" > /usr/bin/mem
echo "ram_total=\$(cat /proc/meminfo | grep MemTotal: | awk '{print \$2}')" >> /usr/bin/mem
echo "ram_free=\$(cat /proc/meminfo | grep MemFree: | awk '{print \$2}')" >> /usr/bin/mem
echo "tmp_buffers=\$(cat /proc/meminfo | grep Buffers: | awk '{print \$2}')" >> /usr/bin/mem
echo "tmp_cached=\$(cat /proc/meminfo | grep Cached: | awk 'NR == 1'  | awk '{print \$2}')" >> /usr/bin/mem
echo "ram_free=\$(( \$ram_free + \$tmp_buffers + \$tmp_cached ))" >> /usr/bin/mem
echo "ram_used=\$(( (\$ram_total - \$ram_free)/1000 ))" >> /usr/bin/mem
echo "ram_free=\$(( \$ram_free/1000 ))" >> /usr/bin/mem
echo "ram_total=\$(( \$ram_total/1000 ))" >> /usr/bin/mem
echo "echo " >> /usr/bin/mem
echo "echo \"Total RAM: \$ram_total MB\"" >> /usr/bin/mem
echo "echo \"Used RAM: \$ram_used MB\"" >> /usr/bin/mem
echo "echo \"Free RAM: \$ram_free MB\"" >> /usr/bin/mem
echo "echo " >> /usr/bin/mem
echo "exit 0" >> /usr/bin/mem
chmod +x /usr/bin/mem



##################################################################################
# Generate echb
##################################################################################
log "Generate echb command"
echo "#"\!"/bin/bash" > /usr/bin/echb
echo "tput bold" >> /usr/bin/echb
echo "echo -e \$@" >> /usr/bin/echb
echo "tput sgr0" >> /usr/bin/echb
echo "exit 0" >> /usr/bin/echb
chmod +x /usr/bin/echb


##################################################################################
# Generate log
##################################################################################
log "Generate log command"
echo "#"\!"/bin/bash" > /usr/bin/log
echo "echo -e \"\\n\$(date +\"%Y-%m-%d\") \$(date +\"%T\") \$1\"" >> /usr/bin/log
echo "exit 0" >> /usr/bin/log
chmod +x /usr/bin/log


##################################################################################
# Generate list-flags
##################################################################################
log "Generate list-flags command"
echo "#"\!"/bin/bash" > /usr/bin/list-flags
echo "steelsquid list-flags" >> /usr/bin/list-flags
echo "exit 0" >> /usr/bin/list-flags
chmod +x /usr/bin/list-flags



##################################################################################
# Generate set-flag
##################################################################################
log "Generate set-flag command"
echo "#"\!"/bin/bash" > /usr/bin/set-flag
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/set-flag
echo "    echo " >> /usr/bin/set-flag
echo "    echb \"set-flag <name-of-flag>\"" >> /usr/bin/set-flag
echo "    echo \"Set a system flag\"" >> /usr/bin/set-flag
echo "    echo \"The steelsquid daemon must be running for this to work\"" >> /usr/bin/set-flag
echo "    echo" >> /usr/bin/set-flag
echo "    exit 0" >> /usr/bin/set-flag
echo "fi" >> /usr/bin/set-flag
echo "event flag set \$1" >> /usr/bin/set-flag
echo "exit 0" >> /usr/bin/set-flag
chmod +x /usr/bin/set-flag


##################################################################################
# Generate get-flag
##################################################################################
log "Generate get-flag command"
echo "#"\!"/bin/bash" > /usr/bin/get-flag
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/get-flag
echo "    echo " >> /usr/bin/get-flag
echo "    echb \"get-flag <name-of-flag>\"" >> /usr/bin/get-flag
echo "    echo \"Check if a flag is set\"" >> /usr/bin/get-flag
echo "    echo" >> /usr/bin/get-flag
echo "    exit 0" >> /usr/bin/get-flag
echo "fi" >> /usr/bin/get-flag
echo "if [ -f \"$steelsquid_folder/flags/\$1\" ]; then" >> /usr/bin/get-flag
echo "    echo \"true\"" >> /usr/bin/get-flag
echo "else" >> /usr/bin/get-flag
echo "    echo \"false\"" >> /usr/bin/get-flag
echo "fi" >> /usr/bin/get-flag
echo "exit 0" >> /usr/bin/get-flag
chmod +x /usr/bin/get-flag


##################################################################################
# Generate del-flag
##################################################################################
log "Generate del-flag command"
echo "#"\!"/bin/bash" > /usr/bin/del-flag
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/del-flag
echo "    echo " >> /usr/bin/del-flag
echo "    echb \"del-flag <name-of-flag>\"" >> /usr/bin/del-flag
echo "    echo \"Delete a flag\"" >> /usr/bin/del-flag
echo "    echo \"The steelsquid daemon must be running for this to work\"" >> /usr/bin/set-flag
echo "    echo" >> /usr/bin/del-flag
echo "    exit 0" >> /usr/bin/del-flag
echo "fi" >> /usr/bin/del-flag
echo "event flag del \$1" >> /usr/bin/del-flag
echo "exit 0" >> /usr/bin/del-flag
chmod +x /usr/bin/del-flag


##################################################################################
# Generate list-parameters
##################################################################################
log "Generate list-parameters command"
echo "#"\!"/bin/bash" > /usr/bin/list-parameters
echo "steelsquid list-parameters" >> /usr/bin/list-parameters
echo "exit 0" >> /usr/bin/list-parameters
chmod +x /usr/bin/list-parameters



##################################################################################
# Generate set-parameter
##################################################################################
log "Generate set-parameter command"
echo "#"\!"/bin/bash" > /usr/bin/set-parameter
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/set-parameter
echo "    echo " >> /usr/bin/set-parameter
echo "    echb \"set-parameter <name> <value>\"" >> /usr/bin/set-parameter
echo "    echo \"Set a parameter\"" >> /usr/bin/set-parameter
echo "    echo \"The steelsquid daemon must be running for this to work\"" >> /usr/bin/set-flag
echo "    echo" >> /usr/bin/set-parameter
echo "    exit 0" >> /usr/bin/set-parameter
echo "fi" >> /usr/bin/set-parameter
echo "event parameter set \$1 \$2" >> /usr/bin/set-parameter
echo "exit 0" >> /usr/bin/set-parameter
chmod +x /usr/bin/set-parameter


##################################################################################
# Generate get-parameter
##################################################################################
log "Generate get-parameter command"
echo "#"\!"/bin/bash" > /usr/bin/get-parameter
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/get-parameter
echo "    echo " >> /usr/bin/get-parameter
echo "    echb \"get-parameter <name>\"" >> /usr/bin/get-parameter
echo "    echo \"Get parameter value\"" >> /usr/bin/get-parameter
echo "    echo" >> /usr/bin/get-parameter
echo "    exit 0" >> /usr/bin/get-parameter
echo "fi" >> /usr/bin/get-parameter
echo "if [ -f \"$steelsquid_folder/parameters/\$1\" ]; then" >> /usr/bin/get-parameter
echo "    cat $steelsquid_folder/parameters/\$1" >> /usr/bin/get-parameter
echo "    echo \"\"" >> /usr/bin/get-parameter
echo "else" >> /usr/bin/get-parameter
echo "    echo \"\"" >> /usr/bin/get-parameter
echo "fi" >> /usr/bin/get-parameter
echo "exit 0" >> /usr/bin/get-parameter
chmod +x /usr/bin/get-parameter


##################################################################################
# Generate has-parameter
##################################################################################
log "Generate has-parameter command"
echo "#"\!"/bin/bash" > /usr/bin/has-parameter
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/has-parameter
echo "    echo " >> /usr/bin/has-parameter
echo "    echb \"has-parameter <name-of-paramater>\"" >> /usr/bin/has-parameter
echo "    echo \"Check if paramater is set\"" >> /usr/bin/has-parameter
echo "    echo" >> /usr/bin/has-parameter
echo "    exit 0" >> /usr/bin/has-parameter
echo "fi" >> /usr/bin/has-parameter
echo "if [ -f \"$steelsquid_folder/parameters/\$1\" ]; then" >> /usr/bin/has-parameter
echo "    echo \"true\"" >> /usr/bin/has-parameter
echo "else" >> /usr/bin/has-parameter
echo "    echo \"false\"" >> /usr/bin/has-parameter
echo "fi" >> /usr/bin/has-parameter
echo "exit 0" >> /usr/bin/has-parameter
chmod +x /usr/bin/has-parameter


##################################################################################
# Generate del-parameter
##################################################################################
log "Generate del-parameter command"
echo "#"\!"/bin/bash" > /usr/bin/del-parameter
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/del-parameter
echo "    echo " >> /usr/bin/del-parameter
echo "    echb \"del-parameter <name-of-paramater>\"" >> /usr/bin/del-parameter
echo "    echo \"Delete a parameter\"" >> /usr/bin/del-parameter
echo "    echo \"The steelsquid daemon must be running for this to work\"" >> /usr/bin/set-flag
echo "    echo" >> /usr/bin/del-parameter
echo "    exit 0" >> /usr/bin/del-parameter
echo "fi" >> /usr/bin/del-parameter
echo "event parameter del \$1" >> /usr/bin/del-parameter
echo "exit 0" >> /usr/bin/del-parameter
chmod +x /usr/bin/del-parameter


##################################################################################
# Generate is-raspberry-pi
##################################################################################
log "Generate is-raspberry-pi command"
echo "#"\!"/bin/bash" > /usr/bin/is-raspberry-pi
echo "response=\$(cat /proc/cpuinfo | grep BCM270)" >> /usr/bin/is-raspberry-pi
echo "if [ \"\$response\" != \"\" ]; then" >> /usr/bin/is-raspberry-pi
echo "    echo \"true\"" >> /usr/bin/is-raspberry-pi
echo "else" >> /usr/bin/is-raspberry-pi
echo "    echo \"false\"" >> /usr/bin/is-raspberry-pi
echo "fi" >> /usr/bin/is-raspberry-pi
echo "exit 0" >> /usr/bin/is-raspberry-pi
chmod +x /usr/bin/is-raspberry-pi


##################################################################################
# Generate compress
##################################################################################
log "Generate compress command"
echo "#"\!"/bin/bash" > /usr/bin/compress
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/compress
echo "    echo " >> /usr/bin/compress
echo "    echb \"compress <file-or-dir>\"" >> /usr/bin/compress
echo "    echo \"Compress a file or directory with LZMA\"" >> /usr/bin/compress
echo "    echo" >> /usr/bin/compress
echo "    exit 0" >> /usr/bin/compress
echo "fi" >> /usr/bin/compress
echo "tar -c \$1 | lzma -6f | > \$1.tar.lzma" >> /usr/bin/compress
echo "exit 0" >> /usr/bin/compress
chmod +x /usr/bin/compress


##################################################################################
# Generate decompress
##################################################################################
log "Generate decompress command"
echo "#"\!"/bin/bash" > /usr/bin/decompress
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/decompress
echo "    echo " >> /usr/bin/decompress
echo "    echb \"decompress <file-or-dir>\"" >> /usr/bin/decompress
echo "    echo \"Decompress a file using LZMA\"" >> /usr/bin/decompress
echo "    echo" >> /usr/bin/decompress
echo "    exit 0" >> /usr/bin/decompress
echo "fi" >> /usr/bin/decompress
echo "lzma -dk --stdout \$1 | tar -x" >> /usr/bin/decompress
echo "exit 0" >> /usr/bin/decompress
chmod +x /usr/bin/decompress


##################################################################################
# Generate encrypt
##################################################################################
log "Generate encrypt command"
echo "#"\!"/bin/bash" > /usr/bin/encrypt
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/encrypt
echo "    echo " >> /usr/bin/encrypt
echo "    echb \"encrypt <file-or-dir>\"" >> /usr/bin/encrypt
echo "    echo \"Encrypt a file or directory using aes-256-cbc\"" >> /usr/bin/encrypt
echo "    echo" >> /usr/bin/encrypt
echo "    exit 0" >> /usr/bin/encrypt
echo "fi" >> /usr/bin/encrypt
echo "tar -c \$1 | lzma -6f | openssl enc -aes-256-cbc -e > \$1.tar.lzma.aes256" >> /usr/bin/encrypt
echo "exit 0" >> /usr/bin/encrypt
chmod +x /usr/bin/encrypt


##################################################################################
# Generate decrypt
##################################################################################
log "Generate decrypt command"
echo "#"\!"/bin/bash" > /usr/bin/decrypt
echo "if [ -z \"\$1\" ]; then" >> /usr/bin/decrypt
echo "    echo " >> /usr/bin/decrypt
echo "    echb \"decrypt <file-or-dir>\"" >> /usr/bin/decrypt
echo "    echo \"Decrypt a file using aes-256-cbc\"" >> /usr/bin/decrypt
echo "    echo" >> /usr/bin/decrypt
echo "    exit 0" >> /usr/bin/decrypt
echo "fi" >> /usr/bin/decrypt
echo "tar -c \$1 | lzma -6f | openssl enc -aes-256-cbc -e > \$1.tar.lzma.aes256" >> /usr/bin/decrypt
echo "exit 0" >> /usr/bin/decrypt
chmod +x /usr/bin/decrypt



##################################################################################
# Generate user password check script
##################################################################################
log "Generate user password check script"
echo "#"\!"/bin/bash" > /usr/bin/checkuser
echo "username=\$1" >> /usr/bin/checkuser
echo "password=\$2" >> /usr/bin/checkuser
echo "salt=\$(sudo getent shadow \$username | cut -d\$ -f3)" >> /usr/bin/checkuser
echo "epassword=\$(sudo getent shadow \$username | cut -d: -f2)" >> /usr/bin/checkuser
echo "match=\$(python -c 'import crypt; print crypt.crypt(\"'\"\${password}\"'\", \"\$6\$'\${salt}'\")')" >> /usr/bin/checkuser
echo "[ \${match} == \${epassword} ] && echo \"true\" || echo \"false\"" >> /usr/bin/checkuser
chmod +x /usr/bin/checkuser



##################################################################################
# Web
##################################################################################
if [ $(get-flag "web") == "true" ]; then
    web_on
else
    web_off
fi




##################################################################################
# GPU
##################################################################################
mem=$(get-parameter "gpu_mem")
if [ -z "$mem" ]; then
    mem="64"
    set-parameter "gpu_mem" "64"
fi
sed -i '/^gpu_mem/ d' /boot/config.txt
echo "gpu_mem=$mem" >> /boot/config.txt




##################################################################################
# Enable disable ssh
##################################################################################
if [ $(get-flag "ssh") == "true" ]; then
	ssh_on
else
	ssh_off
fi


##################################################################################
# Enable disable development
##################################################################################
if [ $(get-flag "development") == "true" ]; then
	development_on
else
	development_off
fi



##################################################################################
# Clean
##################################################################################
log "Clean files and history"
aptitude -y autoclean
aptitude -y clean
apt-get -y remove --purge $(deborphan)
apt-get -y remove --purge $(deborphan)
apt-get -y remove --purge $(deborphan)
rm /root/steelsquid-kiss-os.sh
find / -type f -name "*-old" |xargs sudo rm -rf
rm -rf /var/backups/* /var/lib/apt/lists/* ~/.bash_history
find /var/log/ -type f |xargs sudo rm -rf
cp /dev/null /etc/resolv.conf
log "History and files clean"


##################################################################################
# End
##################################################################################
set_installed
do-ok-exit "$project_name executed OK, please reboot :-)"

