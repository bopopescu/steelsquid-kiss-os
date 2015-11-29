#!/usr/bin/python -OO


'''
Broadcast and subscribe to events, to use this you first must execute activate_event_handler(...)

=======================================================================

First activate the event handler:
activate_event_handler()

Then create the function to execute:
def function_to_execute(args_from_subscription..., parameters_from_trigger):
    print args_from_subscription
    print parameters_from_trigger

parameters_from_trigger is a tuple

Then subscribe the event:
subscribe_to_event("name_of_event", function_to_execute, args_from_subscription)

args_from_subscription is a list

If the function is long running use (The function will execute in new thread):
subscribe_to_event("name_of_event", function_to_execute, args_from_subscription, True)

Then you can trigger the event from other part of the system:
broadcast_event("name_of_event", parameters_from_trigger)

=======================================================================

There are some built-in events that you dont need to create your self:
startup     Execute when system starts  (You must subscribe to this befor execute activate_event_handler)
second      Execute every second
seconds     Execute every 10 second
minute      Execute every minute
minutes     Execute every 10 minutes
hourly      Execute hourly
daily       Execute Daily
shutdown    Stop this eventhandler
poweroff    If it is a Steelsquid PIIO board this event will shutdown linux and power off the system
shout       Will execute steelsquid_utils.shout()
            First paramater is the message
flag        Set/Delete a flag
            Parameter 1: set or del
            Parameter 2: Flag name
parameter   Set/Delete a paramater
            Parameter 1: set or del
            Parameter 2: Paramater name
            Parameter 3: Paramater value
network     Will fire on network upp and down
            Parameter 1: up/down
            if Parameter 1 = up:
              Para2: Fixed IP
              Para3: Wifi IP
              Para4: Wifi acces pont
              Para5: Internet IP
vpn         Will fire on vpn up/down
            Parameter 1: up/down
            Parameter 2: name of vpn
            Parameter 3: VPN ip
mount       Will fire on mount
            Parameter 1: usb, ssh, samba
            Parameter 2: Remote host and directory
            Parameter 3: Local directory
umount      Will fire on umount
            Parameter 1: usb, ssh, samba
            Parameter 2: Remote host and directory
            Parameter 3: Local directory

To subscribe to seconds (the method function_to_execute will execute every 10 seconds):
subscribe_to_event("seconds", function_to_execute, args_from_subscription)

Shutdown will stop this event handler:
subscribe_to_event("shutdown", function_to_execute, args_from_subscription)

=======================================================================

Two additional special events are:
start    Start to execute a event
         This will create a new thread and execute the function in a loop
         The function should not hang for a long time or the stop will not work
         The first paramater will be the name of the function to loop
stop     Stop execute a event
         This will stop the looping

First activate the event handler:
activate_event_handler()

Then create the function to execute (Return True = continue looping, False = Stop looping):
def function_to_execute(args_from_subscription..., parameters_from_trigger):
    print args_from_subscription
    print parameters_from_trigger
    return True

Then subscribe the event:
subscribe_to_event("start", function_to_execute, args_from_subscription)

To start the event:
broadcast_event("start", ["function_to_execute"])

To stop the looping event:
broadcast_event("stop", ["function_to_execute"])

To stop all looping events:
broadcast_event("stop")

=======================================================================

You can also trigger events by executing this python script (see __main__)

=======================================================================

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import thread
import Queue
import os
import shlex
import threading
import sys
import subprocess
import steelsquid_http_server

running = True
system_event_dir = "/run/shm/steelsquid"
queue = Queue.Queue(0)
subscribers = []
subscribers_second = []
subscribers_seconds = []
subscribers_loop = []
lock = threading.Lock()
lock_s = threading.Lock()


def subscribe_to_event(event, function, args, long_running=False):
    '''
    Subscribed to a event
    Add a function to execute on event 
    Make a new event or use one of the built in
        
    See top of this file for example...
    
    @param event: The event name
    @param function: The function to execute
    @param args: Arguments to the function (tuple)
    @param long_running: If the function is long running execute in new thread
    '''
    with lock_s:
        if args == None:
            args = ()
        if event == "second":
            subscribers_second.append((event, function, args, long_running))
        elif event == "seconds":
            subscribers_seconds.append((event, function, args, long_running))
        elif event == "start":
            subscribers_loop.append([function, args, False])
        else:
            subscribers.append((event, function, args, long_running))


def unsubscribe_to_event(event=None, function=None):
    '''
    Unsubscribed to a event.
    Matching separately or together.
    @param event: The event name 
    @param function: The function (can be the fuction or name of the function)
    '''
    global subscribers
    global subscribers_second
    global subscribers_seconds
    global subscribers_loop
    with lock_s:
        is_str = isinstance(function, basestring)
        for i in xrange(len(subscribers) - 1, -1, -1):
            func = subscribers[i][1]
            ev = subscribers[i][0]
            check_it(subscribers, i, func, ev, is_str, function, event)
        for i in xrange(len(subscribers_second) - 1, -1, -1):
            func = subscribers_second[i][1]
            ev = subscribers_second[i][0]
            check_it(subscribers_second, i, func, ev, is_str, function, event)
        for i in xrange(len(subscribers_seconds) - 1, -1, -1):
            func = subscribers_seconds[i][1]
            ev = subscribers_seconds[i][0]
            check_it(subscribers_seconds, i, func, ev, is_str, function, event)
        for i in xrange(len(subscribers_loop) - 1, -1, -1):
            func = subscribers_loop[i][0]
            subscribers_loop[i][2] = False
            ev = None
            check_it(subscribers_loop, i, func, ev, is_str, function, event)
 

def check_it(subscribers, i, func, ev, is_str, function, event):
    if event != None and ev != None and function != None:
        if ev == event:
            if is_str and func.__name__ == function:
                del subscribers[i]
                return
            elif func == function:
                del subscribers[i]
                return
    if event != None and ev != None and function == None:
        if ev == event:
            del subscribers[i]
            return
    if function != None:
        if is_str and func.__name__ == function:
            del subscribers[i]
            return
        elif func == function:
            del subscribers[i]
            return


def broadcast_event(event, parameters=None):
    '''
    Broadcast a event
    See top of this file for example...
    
    @param event: The event name
    @param parameters: List of parameters that accompany the event (None or 0 length list if no paramaters)
    '''
    if running:
        if event == "start":
            if len(parameters[0])==1:
                broadcast_loop(parameters[0])
            else:
                broadcast_loop(parameters[0], parameters[1:])
        elif event == "stop":
            if parameters == None or len(parameters) == 0:
                broadcast_stop()
            else:
                broadcast_stop(parameters[0])
        else:
            queue.put((event, parameters))
    
    
def broadcast_event_external(event, parameters=None):
    '''
    Broadcast a event outside Steelsquid daemon
    See top of this file for example...
    
    @param event: The event name
    @param parameters: List of parameters that accompany the event (None or 0 length list if no paramaters)
    '''
    steelsquid_utils.make_dirs(system_event_dir)
    if parameters != None:
        nl = []
        for s in parameters:
            s = str(s)
            nl.append("\"")
            nl.append(s)
            nl.append("\" ")
        pa = os.path.join(system_event_dir, event)
        steelsquid_utils.write_to_file(pa, "".join(nl))
    else:
        pa = os.path.join(system_event_dir, event)
        steelsquid_utils.write_to_file(pa, "")
    
       
def start_thread(obj, paramaters):
    '''
    obj [function, args, False]
    '''
    try:
        while obj[2]==True:
            retur = obj[0](obj[1], paramaters)
            if retur == False:
                obj[2]==False
    except:
        steelsquid_utils.shout()
    finally:
        obj[2]==False
        

def broadcast_loop(function_name, paramaters=None):
    '''
    Start a event loop
    '''
    with lock:
        for obj in subscribers_loop: #[function, args, False]
            if obj[2]==False and function_name == obj[0].__name__:
                obj[2]=True
                thread.start_new_thread(start_thread, (obj, paramaters))


def broadcast_stop(function_name=None):
    '''
    Stop event looping
    '''
    with lock:
        if function_name == None:
            for obj in subscribers_loop: #[function, args, False]
                obj[2]=False
        else:
            for obj in subscribers_loop: #[function, args, False]
                if function_name == obj[0].__name__:
                    obj[2]=False
        
    
def event_work():
    '''
    Listen for events
    '''
    global running
    running = True
    event_executer("startup", subscribers, [])
    counter_10 = 0
    counter_60 = 0
    counter_600 = 0
    counter_3600 = 0
    counter_86400 = 0
    while running:
        try:
            for f in os.listdir(system_event_dir):
                prop =  steelsquid_utils.read_from_file_and_delete(os.path.join(system_event_dir, f))
                if len(prop)>0:
                    propSp = shlex.split(prop)
                    broadcast_event(f, propSp)
                else:
                    broadcast_event(f, [])
            if len(subscribers_second)>0:
                    event_executer("second", subscribers_second, [])
            if len(subscribers_seconds)>0:
                if counter_10 >= 10:
                    counter_10 = 0
                    event_executer("seconds", subscribers_seconds, [])
                else:
                    counter_10 = counter_10 + 1
            if len(subscribers)>0:
                if counter_60 >= 60:
                    counter_60 = 0
                    event_executer("minute", subscribers, [])
                else:
                    counter_60 = counter_60 + 1
                if counter_600 >= 600:
                    counter_600 = 0
                    event_executer("minutes", subscribers, [])
                else:
                    counter_600 = counter_600 + 1
                if counter_3600 >= 3600:
                    counter_3600 = 0
                    event_executer("hourly", subscribers, [])
                else:
                    counter_3600 = counter_3600 + 1
                if counter_86400 >= 86400:
                    counter_86400 = 0
                    steelsquid_utils.clear_tmp()
                    event_executer("daily", subscribers, [])
                else:
                    counter_86400 = counter_86400 + 1
            event, parameters = queue.get(timeout=1)
            if event == "shutdown" or len(subscribers)>0:
                event_executer(event, subscribers, parameters)
        except Queue.Empty:
            pass
        except:
            steelsquid_utils.shout()


def event_executer(event, subs, parameters):
    '''
    Execute the events
    '''
    try:
        do_fire = True
        if event=="network":
            thread.start_new_thread(__event_executer_network, (subs, parameters))
            return
        elif event=="vpn":
            name = "unknown"
            try:
                import steelsquid_nm
                name = steelsquid_nm.vpn_configured()
            except:
                pass
            parameters.append(name)
            parameters.append(steelsquid_utils.network_ip_vpn())
        for e, function, args, long_running in subs:
            if e == event:
                if long_running:
                    thread.start_new_thread(function, (args, parameters))
                else:
                    function(args, parameters)
        if event == "shutdown":
            __deactivate_event_handler()
    except:
        if event != "shout":
            steelsquid_utils.shout()
                
                
def __event_executer_network(subs, parameters):
    '''
    Execute network event in thread
    '''
    parameters = []
    wired = steelsquid_utils.network_ip_wired()
    wifi = steelsquid_utils.network_ip_wifi()
    wan = "---"
    if wired == "---" and wifi == "---":
        net = "down"
    else:
        net = "up"
        wan = steelsquid_utils.network_ip_wan()
    parameters.append(net)
    parameters.append(wired)
    parameters.append(wifi)
    if wifi == "---":
        parameters.append("---")
    else:
        try:
            import steelsquid_nm
            parameters.append(steelsquid_nm.get_connected_access_point_name())
        except:
            parameters.append("---")
    parameters.append(wan)
    for e, function, args, long_running in subs:
        if e == "network":
            function(args, parameters)
        

def activate_event_handler(create_ner_thread=True):
    '''
    Start the event handler
    @param create_ner_thread: Run this is new thread
    '''
    steelsquid_utils.make_dirs(system_event_dir)
    steelsquid_utils.deleteFileOrFolder(system_event_dir + "/shutdown")
    if create_ner_thread:
        thread.start_new_thread(event_work, ())
    else:
        event_work()


def __deactivate_event_handler():
    '''
    Stop the event handler (if get shutdown event)
    '''
    try:
        global running
        running = False
        for sub in subscribers_loop:
            sub[2] = False
        del subscribers_loop[:]
        del subscribers_second[:]
        del subscribers_seconds[:]
        del subscribers[:]
    except:
        pass


def deactivate_event_handler():
    '''
    Stop the event handler
    '''
    try:
        for e, function, args, long_running in subscribers:
            if e == "shutdown":
                if long_running:
                    thread.start_new_thread(function, (args, None))
                else:
                    function(args, None)
    except:
        pass
    try:
        global running
        running = False
        for sub in subscribers_loop:
            sub[2] = False
        del subscribers_loop[:]
        del subscribers_second[:]
        del subscribers_seconds[:]
        del subscribers[:]
    except:
        pass


if __name__ == '__main__':
    '''
    The main
    '''
    if len(sys.argv) == 1:
        print("")
        steelsquid_utils.printb("DESCRIPTION")
        print("Broadcast event to the python program.")
        print("The python program steelsquid_event must listen for event for this to work...")
        print("")
        steelsquid_utils.printb("steelsquid-event <event>")
        print("Broadcast event without parameters")
        print("")
        steelsquid_utils.printb("steelsquid-event <event> <parameter1> <parameter2>...")
        print("Broadcast event with paramaters")
        print("")
        steelsquid_utils.printb("steelsquid-event start <name>")
        print("Start execute (loop) a function with name <name>")
        print("")
        steelsquid_utils.printb("steelsquid-event stop")
        print("Stop execute (loop) all functions")
        print("")
        steelsquid_utils.printb("steelsquid-event stop <name>")
        print("Stop execute (loop) a function with name <name>")
        print("")
        steelsquid_utils.printb("steelsquid-event shutdown")
        print("Stop the event handler (shutdown system)")
        print("")
    elif len(sys.argv) == 2:
        steelsquid_utils.make_dirs(system_event_dir)
        pa = os.path.join(system_event_dir, sys.argv[1])
        steelsquid_utils.write_to_file(pa, "")
    else:
        steelsquid_utils.make_dirs(system_event_dir)
        nl = []
        for s in sys.argv[2:]:
            nl.append("\"")
            nl.append(s)
            nl.append("\" ")
        pa = os.path.join(system_event_dir, sys.argv[1])
        steelsquid_utils.write_to_file(pa, "".join(nl))
