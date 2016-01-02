<b>You can extend the functionality of Steelsquid Kiss OS in 3 ways</b>
<br>
I recommend that you use the syncrionisation script.
 - Start a syncrionisation script on a separate computer.<br>
   When you edit files on that computer they will be uploaded to SteelsquidKissOS automatically.<br>
   (There is now also a Windows exe file for easy syncrionistion on windows ...)
 - Edit files on separate computer and upload them manually.
 - Edit files on SteelsquidKissOS

<b>Automatic upload changes to Steelsquid Kiss OS (syncrionisation script)</b>
<br>
You can start a program on the development machine that listen for changes on files and upload to Steelsquid Kiss OS automatically.<br>
Move to the directory where you cloned from git (or extracted ZIP-file).<br>
Change IP number in the file config.txt to the ip number to Steelsquid Kiss OS.<br>
The 4 first row in the file contains this:<br>
IP<br>
PORT<br>
USER<br>
PASSWORD<br>
<br>
You can also add multiple server if you want to deploy the same to multiple servers.<br>
Use comma to separate like this: IP, IP, IP<br>
Port, user and password must be the same on all servers.<br>
More info on config.txt see Add custom files below.<br>

 - Then execute: ./steelsquid_synchronize.py
 - Windows users: steelsquid_synchronize.exe

When the program starts it will sync all files.<br>
You should see something like this:<br>
2015-06-05 18:31:20 Load settings from steelsquid-kiss-os.sh<br>
2015-06-05 18:31:20 Load settings from config.txt<br>
2015-06-05 18:31:20 Connecting to: 192.168.0.102<br>
<br>
------------------------------------------------------------------------------<br>
Listen for changes and commit to following server(s)<br>
192.168.0.108<br>
------------------------------------------------------------------------------<br>
 H : help    : Show this help<br>
 Q : quit    : This program will terminate<br>
 T : test    : Execute the /root/test.py script<br>
 M : module  : Reload the modules (/opt/steelsquid/python/modules/...)<br>
 S : service : Start/Restart steelsquid service (implememt all changes)<br>
 K : kill    : Stop steelsquid service<br>
 R : reboot  : Reboot the remote machine<br>
 L : list    : List modules in modules/ (see if enabled or not)<br>
 N : new     : Create new module in modules/ (copy kiss_expand.py)<br>
 A : annul   : Delete a module in modules/ (You can not undo this!!!)<br>
 E : enable  : Enable a module in modules/ (will start on boot)<br>
 D : disable : Disable a module in modules/ (will not start on boot)<br>
 W : web     : Create new HTML-file in web/ (copy template.html)<br>
 V : delweb  : Delete a HTML-file in web/ (You can not undo this!!!)<br>
------------------------------------------------------------------------------<br>
You can also send any other simple terminal line command (ls, pwd, mkdir...)<br>
But you can not use any commands that read input (nano, read, passwd)<br>
------------------------------------------------------------------------------<br>
<br>
2015-06-05 18:31:21 SYNC: steelsquid-kiss-os.sh<br>
2015-06-05 18:31:21 SYNC: steelsquid_boot.py<br>
2015-06-05 18:31:21 SYNC: steelsquid_event.py<br>
...........<br>
<br>
If you edit one of the monitored files it will be uploaded to Steelsquid Kiss OS automatically.<br>
A new row will show. example: 2014-12-07 19:29:50 SYNC: steelsquid_boot.py<br>
<br>
Messages and errors on the Steelsquid Kiss OS will also appear on the development machine.<br>
If you for example execute print Olle on Steelsquid KISS OS the text "Olle" will appear on the development machine.<br>
<br>
<b>Make stuff execute on boot</b><br>
If you want to implement new functionality I suggest you do it in the following files
 - Python files added under /opt/steelsquid/python/modules/ is imported (executed) automatically when the steelsquid service     starts (system boots).<br>
   This execute in its own thread so no problem with long running stuff.
 - /opt/steelsquid/python/modules/kiss_expand.py<br>
   To execute stuff at boot you can use this file. It will be imported (executed) in its own thread.
The intention is that if you want to quickly add a feature do that in kiss_expand.py.<br>
But if you want to add several different features, create a new file in modules/ for every feature.
 - I suggest that if you want to create a new feature copy the kiss_expand.py and give it a suitable name (You will then get     all the help comments in kiss_expand.py to your new file).<br>
   You do this in the synchronization program by press N and then enter the name of the new module.
 - Then you need to enable that module:<br>
   Command line: steelsquid module kiss_expand on<br>
   Python: steelsquid_kiss_global.module_status("kiss_expand", True)<br>
   Syncrinization program: Press E and then select the module.<br>
<br>
The files under modules/ can also listen to events and handle web requests.<br>
 - If the module have 2 methods enable and disable this will execute when the module is enabled /disabled.
 - If the module have 6 different classes: SYSTEM, LOOP, EVENTS, WEB, SOCKET och GLOBAL you get a lot of extra stuff...
 - When module is enabled (Method: enable) is executed
 - When module is disabled (Method: disable) is executed
 - System events (Class: SYSTEM)
   Execute static methods when system start, network connect...
 - Threads (Class: LOOP)
   Every static method in the class will be executed in a thread
 - Your own events (Class: EVENTS)
   Create staticmethods in this class to listen for asynchronous events....
 - Built in webserver (Class: WEB)
   Execute static methods on request from the webserver...
 - Built in Socket server (Class: SOCKET)
   Execute static methods on request from the socket server...
 - Logic used from different places (Class: GLOBAL)
   Put global staticmethods in this class, methods you use from different part of the system.

More info see https://sites.google.com/site/steelsquid/extend


