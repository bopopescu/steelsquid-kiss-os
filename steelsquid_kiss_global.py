#!/usr/bin/python -OO


'''
Global stuff for steelsquid kiss os
Reach the http server and Socket connection.
I also add some extra stuff here like events and modules

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_pi
import steelsquid_kiss_boot
import os.path, pkgutil
import time
import threading
import thread
import sys
import importlib
import Queue
import exceptions
import os
import modules
from importlib import import_module


# Number of eventdata and brodecast handler threads
NUMBER_OF_EVENT_HANDLERS = 3

# If more than this events pending for execution dropp new events
MAX_PENDING_EVENTS=128

# All loaded modules (python files in the modules/ directory)
loaded_modules={}

# The socket connection, if enabled (not enabled = None)
# Flag: socket_server
# Parameter: socket_client
socket_connection = None

# The http webserver, if enabled (not enabled = None)
# Flag: web
http_server = None

# Lock object for add to event_data_callback_methods
lock = threading.Lock()

# Global data (key, Value)
event_data={}

# If data is changed in event_data, the methods in the list will fire (one thread will fire all events sequentially)
event_data_callback_methods=[]

# List with events that is to be fire by thread...
event_data_queue=Queue.Queue()

# If broadcast_event is executed, a method with the event name will execute in this class object
broadcast_event_callback_classes=[]

# List with events that is to be fire by thread...
broadcast_event_queue=Queue.Queue()

# Last voltage read (if this is a PIIO board)
last_voltage = None

# Last net (up or down, (True, False))
last_net = False

# Last WIFI name
last_wifi_name = None

# Last WIFI IP
last_wifi_ip = None

# Last LAN IP
last_lan_ip = None

# Last WAN IP
last_wan_ip = None

# Radio
radio_count_max = 30
radio_count = 30


def get_module(name):
    '''
    Get a module from the modules directory
    Only return modules that has bean enabled
    return: The module or None
    '''    
    return loaded_modules.get(name)


def is_module(name):
    '''
    Check if a name is a module
    return: True/False
    '''    
    if steelsquid_utils.get_flag("module_"+name):
        return True
    else:
        return False


def is_module_enabled(name):
    '''
    Check if a module is imported and enabled
    return: True/False
    '''    
    if name in loaded_modules:
        return True
    else:
        return False


def get_modules():
    '''
    Get a dict with all modules
    '''    
    return loaded_modules


def clear_modules_settings(module_name):
    '''
    Clear all settings for a module
    See the SETTINGS class in a module...
    '''    
    mod = import_module('modules.'+module_name)
    class_settings = _get_object(mod, "SETTINGS")
    if class_settings!=None:
        members = [attr for attr in dir(class_settings) if not callable(getattr(class_settings, attr)) and not attr.startswith("_")]
        for var_name in members:
            the_var = getattr(class_settings, var_name, None)
            if isinstance(the_var, (bool)):
                steelsquid_utils.del_flag(var_name)
            elif isinstance(the_var, list):
                steelsquid_utils.del_list(var_name)
            elif isinstance(the_var, int):
                steelsquid_utils.del_parameter(var_name)
            elif isinstance(the_var, float):
                steelsquid_utils.del_parameter(var_name)
            else:
                steelsquid_utils.del_parameter(var_name)


def module_status(name, status, argument = None, restart=True):
    '''
    Enable or disable a module
    name: Name of the mopule
    status: True/False
    argument: Send data to the enable or disable method in the module
              Usually a string to tell the start/stop something
    restart: restart the steelsquid daemon
    Return: Is it found
    '''    
    try:
        pkgpath = os.path.dirname(modules.__file__)
        doit=False
        for f in pkgutil.iter_modules([pkgpath]):
            if f[1]==name:
                doit=True
        if doit:
            try:
                mod = import_module('modules.'+name)
                if status:
                    steelsquid_utils.set_flag("module_"+name)
                    try:
                        mod.enable(argument)
                    except:
                        steelsquid_utils.del_flag("module_"+name)
                        steelsquid_utils.shout(string="Enable module error", is_error=True)
                        return False
                else:
                    steelsquid_utils.del_flag("module_"+name)
                    try:
                        mod.disable(argument)
                    except:
                        steelsquid_utils.set_flag("module_"+name)
                        steelsquid_utils.shout(string="Disable module error", is_error=True)
                        return False
                if restart:
                    os.system('systemctl restart steelsquid')
                return True
            except:
                steelsquid_utils.shout(string="Import module error", is_error=True)
                return False
        else:
            return False
            steelsquid_utils.shout(string="Module not found")
    except:
        steelsquid_utils.shout()
        return False


def broadcast_event(event, parameters_to_event=None):
    '''
    Will broadcast a event, execute methods in the classes inside "broadcast_event_callback_classes"
    OBS! Classes named EVENTS in every module will automatically be added to "broadcast_event_callback_classes"
    event = The name of the method in the EVENT class to execute.
    parameters_to_event = Paramaters to that event (tuple)
    '''    
    if len(broadcast_event_callback_classes)>0 and broadcast_event_queue.qsize() < MAX_PENDING_EVENTS:
        broadcast_event_queue.put((event, parameters_to_event))


def add_broadcast_event_callback(aclass):
    '''
    Add broadcast event callback method
    OBS! Classes named EVENTS in every module will automatically be added to "broadcast_event_callback_classes"
    '''    
    with lock:
        if len(broadcast_event_callback_classes)==0:
            broadcast_event_callback_classes.append(aclass)
            for i in range(NUMBER_OF_EVENT_HANDLERS):
                thread.start_new_thread(_broadcast_event_handler, ()) 
        else:
            broadcast_event_callback_classes.append(aclass)
        

def remove_broadcast_event_callback(aclass):
    '''
    Remove broadcast event callback method
    '''    
    with lock:
        try:
            broadcast_event_callback_classes.remove(aclass)
        except ValueError:
            pass        


def get_event_data(key):
    '''
    Get event data.
    return: The value (None = not found/No value)
    '''    
    try:
        return event_data[key]
    except ValueError:
        return None        


def set_event_data(key, value):
    '''
    Set event data.
    When eventdata is set methods in event_data_callback_methods will fire
    OBS!The method on_event_data(key, value) in the SYSTEM class in all modules is automatically added to event_data_callback_methods
    key: Key for the data
    value: Value for the data
    '''    
    event_data[key]=value
    if len(event_data_callback_methods)>0 and event_data_queue.qsize() < MAX_PENDING_EVENTS:
        event_data_queue.put((key, value))


def del_event_data(key, value):
    '''
    Delete event data.
    When eventdata is deleted methods in event_data_callback_methods will fire (with value=None)
    key: Key for the data
    '''    
    try:
        del event_data[key]
    except:
        pass
    if len(event_data_callback_methods)>0 and event_data_queue.qsize() < MAX_PENDING_EVENTS:
        event_data_queue.put((key, None))


def add_event_data_callback(method):
    '''
    Add event callback method
    This method will fire when data is changed
    def method(key, value):
    OBS!The method on_event_data(key, value) in the SYSTEM class in all modules is automatically added to event_data_callback_methods
    '''    
    with lock:
        if len(event_data_callback_methods)==0:
            event_data_callback_methods.append(method)
            for i in range(NUMBER_OF_EVENT_HANDLERS):
                thread.start_new_thread(_event_data_handler, ()) 
        else:
            event_data_callback_methods.append(method)
        

def remove_event_data_callback(method):
    '''
    Remove event callback method
    '''    
    with lock:
        try:
            event_data_callback_methods.remove(method)
        except ValueError:
            pass        


def stream():
    '''
    Is camera streaming enabled.
    This will trigger a restart of the raspberry Pi
    Return: None=not enabled
            "usb" = USB camera streaming enabled
            "pi" = PI camera streaming enabled
    '''    
    if steelsquid_utils.get_flag("stream"):
        return "usb"
    elif steelsquid_utils.get_flag("stream-pi"):
        return "pi"
    else:
        return None


def save_module_settings():
    '''
    Save varibalesin the module SETYTINGS class
    '''    
    steelsquid_kiss_boot._save_settings()


def reboot():
    '''
    Reboot the computer
    '''    
    try:
        steelsquid_kiss_boot._cleanup()
    except:
        steelsquid_utils.shout()
    os.system("reboot")


def stream_usb():
    '''
    Enable streaming of USB camera
    This will trigger a restart of the raspberry Pi
    '''    
    os.system("steelsquid stream-on")
    os.system("reboot")


def stream_pi():
    '''
    Enable streaming of Raspberry PI camera
    This will trigger a restart of the raspberry Pi
    '''    
    os.system("steelsquid stream-pi-on")
    os.system("reboot")


def stream_off():
    '''
    Disable streaming of camera (Pi or USB)
    This will trigger a restart of the raspberry Pi
    '''    
    os.system("steelsquid stream-off")
    os.system("reboot")


def camera_status(status=None):
    '''
    Enable or disable the Raspberry Pi camera
    This will trigger a restart of the raspberry Pi
    status = True/False  (enable or disable)
    if status = None only return current camera status
    '''    
    if status != None:
        if status:
            os.system("steelsquid camera-on")
        else:
            os.system("steelsquid camera-off")
        os.system("reboot")
    return steelsquid_utils.get_flag("camera")


def nrf24_status(status):
    '''
    Enable nrf24 transmitter on this device
    Must reboot to implement
    status: server=Enable as server
            client=Enable as client
            master=Enable as master
            slave=Enable as slave
            None=Disable
    '''    
    if status==None:
        steelsquid_utils.del_flag("nrf24_server")
        steelsquid_utils.del_flag("nrf24_client")
        steelsquid_utils.del_flag("nrf24_master")
        steelsquid_utils.del_flag("nrf24_slave")
    elif status=="server":
        steelsquid_utils.set_flag("nrf24_server")
        steelsquid_utils.del_flag("nrf24_client")
        steelsquid_utils.del_flag("nrf24_master")
        steelsquid_utils.del_flag("nrf24_slave")
    elif status=="client":
        steelsquid_utils.del_flag("nrf24_server")
        steelsquid_utils.set_flag("nrf24_client")
        steelsquid_utils.del_flag("nrf24_master")
        steelsquid_utils.del_flag("nrf24_slave")
    elif status=="master":
        steelsquid_utils.del_flag("nrf24_server")
        steelsquid_utils.del_flag("nrf24_client")
        steelsquid_utils.set_flag("nrf24_master")
        steelsquid_utils.del_flag("nrf24_slave")
    elif status=="slave":
        steelsquid_utils.del_flag("nrf24_server")
        steelsquid_utils.del_flag("nrf24_client")
        steelsquid_utils.del_flag("nrf24_master")
        steelsquid_utils.set_flag("nrf24_slave")
    
    
def hmtrlrs_status(status):
    '''
    Send and reseive messages with HM-TRLR-S transmitter 
    http://www.digikey.com/product-detail/en/HM-TRLR-S-868/HM-TRLR-S-868-ND/5051756
    Must reboot to implement
    status: server=Enable as server
            client=Enable as client
            None=Disable
    '''    
    if status==None:
        steelsquid_utils.del_flag("hmtrlrs_server")
        steelsquid_utils.del_flag("hmtrlrs_client")
    elif status=="server":
        steelsquid_utils.set_flag("hmtrlrs_server")
        steelsquid_utils.del_flag("hmtrlrs_client")
    elif status=="client":
        steelsquid_utils.del_flag("hmtrlrs_server")
        steelsquid_utils.set_flag("hmtrlrs_client")


def radio_interrupt():
    '''
    If you made changes to the RADIO_SYNC or RADIO_PUSH variables you can fire the sync or push with this method
    Otherwise you must wait about 1 second for it to fire....
    '''    
    global radio_count
    radio_count=radio_count_max
    steelsquid_kiss_boot.radio_event.set()


def _broadcast_event_handler():
    '''
    Fire the broadcast event 
    '''    
    while len(broadcast_event_callback_classes)>0:
        event, parameters_to_event = broadcast_event_queue.get()
        last = "Unknown"
        try:
            for aclass in broadcast_event_callback_classes:
                last = aclass
                if hasattr(aclass, event):
                    m = getattr(aclass, event)
                    if parameters_to_event==None:
                        m()
                    else:
                        m(*parameters_to_event)
        except:
            steelsquid_utils.shout("Fatal error in broadcast_event_handler: "+last, is_error=True)            


def _event_data_handler():
    '''
    Fire the event data events
    '''    
    while len(event_data_callback_methods)>0:
        key, value = event_data_queue.get()
        last = "Unknown"
        try:
            for method in event_data_callback_methods:
                last = method
                method(key, value)
        except:
            steelsquid_utils.shout("Fatal error in event_data_handler: "+last, is_error=True)            


def _get_object(obj, name):
    '''
    Get a class or method from object
    Return None if not found
    '''
    try:
        return getattr(obj, name)
    except:
        pass


def _exec_method(obj, name, method_args=None):
    '''
    Execute a method inside a object
    '''
    try:
        obj = getattr(obj, name)
        try:
            if method_args==None:
                obj()
            else:
                obj(*method_args)
        except:
            steelsquid_utils.shout("Module error: " + name + "("+str(method_args)+")", is_error=True)
    except:
        pass


def _exec_method_set_started(obj, name, method_args=None, is_started=True):
    '''
    Execute a method inside a object
    Also try to set the is_started variable
    '''
    try:
        obj = getattr(obj, name)
        ok = True
        try:
            if method_args==None:
                obj()
            else:
                obj(*method_args)
        except:
            ok=False
            steelsquid_utils.shout("Module error: " + name + "("+str(method_args)+")", is_error=True)
        if ok:
            obj.is_started = is_started
    except:
        pass

def _execute_all_modules(class_name, method_name, method_args=None):
    '''
    Execute on alla available modules (in modules/)
    Execute a method in a module or class(classmethod) if exists
    '''
    for name, mod in loaded_modules.iteritems():
        try:
            if class_name != None:
                mod = getattr(mod, class_name)
            mod = getattr(mod, method_name)
            try:
                if method_args==None:
                    mod()
                else:
                    mod(*method_args)
            except:
                if class_name == None:
                    steelsquid_utils.shout("Module error: " + name+ "." + method_name + "("+str(method_args)+")", is_error=True)
                else:
                    steelsquid_utils.shout("Module error: " + name+ "." + class_name + "." + method_name + "("+str(method_args)+")", is_error=True)
        except:
            pass


def _execute_first_modules_and_return(class_name, method_name, method_args=None):
    '''
    Execute on first available modules (in modules/)
    Execute a method in a module or class(classmethod) if exists
    '''
    for name, mod in loaded_modules.iteritems():
        if class_name != None:
            if hasattr(mod, class_name):
                mod = getattr(mod, class_name)
        if hasattr(mod, method_name):
            mod = getattr(mod, method_name)
            if method_args==None:
                return mod()
            else:
                return mod(*method_args)
    raise Exception("Method not found: "+method_name)
    
    
def _get_first_modules_class(class_name, inner_class_name=None):
    '''
    Get class from first module
    '''
    for name, mod in loaded_modules.iteritems():
        if hasattr(mod, class_name):
            mod = getattr(mod, class_name)
            if inner_class_name!=None:
                mod = getattr(mod, inner_class_name)
            return mod
    return None
        
        
        
def _has_modules_method(class_name, method_name):
    '''
    Check if any modules has a method
    '''
    for name, mod in loaded_modules.iteritems():
        if class_name != None and hasattr(mod, class_name):
            mod = getattr(mod, class_name)
        if hasattr(mod, method_name):
            return True
    return False

