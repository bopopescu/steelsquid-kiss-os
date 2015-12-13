#!/usr/bin/python -OO


'''
Global stuff for steelsquid kiss os
Reach the http server and Socket connection.
I also add some extra stuff here like data events

Use this to add functionality that my be used from different part of the system... example http server and socket server...

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_utils
import steelsquid_event
import steelsquid_pi
import steelsquid_boot
import time
import threading
import thread
import sys
import importlib
import expand
import Queue
from importlib import import_module


# All loaded custom expand files (python module names in the expand directory that has bean imported)
expand_modules=[]

# The socket connection, if enabled (not enabled = None)
# Flag: socket_server
# Parameter: socket_client
socket_connection = None

# The http webserver, if enabled (not enabled = None)
# Flag: web
http_server = None

# Global data (key, Value)
event_data={}

# If data is changed in event_data, the methods in the list will fire (one thread will fire all events sequentially)
event_data_callback_methods=[]

# List with events that is to be fire by thread...
event_data_queue=Queue.Queue()

# Lock object for add to event_data_callback_methods
lock = threading.Lock()

# If more than this events pending for execution dropp new events
max_pending_events=128


def get_expand_module(name):
    '''
    Get a module from the expand directory
    Only return modules that has bean activated
    return: The module
    '''    
    return sys.modules['expand.'+name]


def is_expand_module(name):
    '''
    Check if a module is imported and active
    return: True/False
    '''    
    if 'expand.'+name in sys.modules:
        mod = sys.modules['expand.'+name]
        return hasattr(mod, "activate") and mod.activate() and mod.is_enabled
    else:
        return False

       
def add_event_data_callback(method):
    '''
    Add event callback method
    This method will fire when data is changed
    def method(key, value):
    '''    
    with lock:
        if len(event_data_callback_methods)==0:
            thread.start_new_thread(__event_data_handler, ()) 
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
    key: Key for the data
    value: Value for the data
    '''    
    event_data[key]=value
    if len(event_data_callback_methods)>0 and event_data_queue.qsize() < max_pending_events:
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
    if event_data_queue.qsize() < max_pending_events:
        event_data_queue.put((key, None))


def __event_data_handler():
    '''
    Fire the event data events
    '''    
    while True:
        key, value = event_data_queue.get()
        try:
            for method in event_data_callback_methods:
                method(key, value)
        except:
            steelsquid_utils.shout("Fatal error in event_data_handler: "+key, is_error=True)            

    
    
def __get_expand_module(module_name, class_name=None, method_name=None):
    '''
    Get a module or class(classmethod) if exists
    Will also check if method activate return true on the module
    Return None if method not found or activate=False
    '''
    import steelsquid_kiss_expand
    try:
        mod = None
        if module_name == steelsquid_kiss_expand:
            mod = steelsquid_kiss_expand
        else:
            mod = import_module('expand.'+module_name)
        if mod.activate():
            if class_name!=None and method_name!=None:
                m = getattr(mod, class_name)
                getattr(m, method_name)
            elif class_name!=None:
                getattr(mod, class_name)
            return mod
        else:
            return None
    except:
        return None


def __get_expand_module_class(module_name, class_name):
    '''
    Get a module or class(classmethod) if exists
    Will also check if method activate return true on the module
    Return None if method not found or activate=False
    '''
    import steelsquid_kiss_expand
    try:
        mod = None
        if module_name == steelsquid_kiss_expand:
            mod = steelsquid_kiss_expand
        else:
            mod = import_module('expand.'+module_name)
        if mod.activate():
            mod = getattr(mod, class_name)
            return mod
        else:
            return None
    except:
        return None
    

def __get_expand_module_method(module_name, class_name, method_name):
    '''
    Get a method in a module or class(classmethod) if exists
    Will also check if method activate return true on the module
    Return None if method not found or activate=False
    '''
    import steelsquid_kiss_expand
    try:
        mod = None
        if module_name == steelsquid_kiss_expand:
            mod = steelsquid_kiss_expand
        else:
            mod = import_module('expand.'+module_name)
        if mod.activate():
            mod = getattr(mod, class_name)
            return getattr(mod, method_name)
        else:
            return None
    except:
        return None


def __execute_expand_module_method(module_name, class_name, method_name, method_args):
    '''
    Execute a method in a module or class(classmethod) if exists
    Will also check if method activate return true on the module
    '''
    mod = __get_expand_module_method(module_name, class_name, method_name)
    if mod != None:
        try:
            mod(*method_args)
        except:
            steelsquid_utils.shout()
    
                

