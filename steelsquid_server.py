#!/usr/bin/python -OO


'''
A simple module that i use to listen for command and then execute stuff.
If the command is abcde then the method abcde(paramaters) will get executed.
All you can do is to send a command with a list of parameters.
If the command executet OK a list can be answered back if error a error message.
Override this and create a function like this
def test_command(self, parameters):
  .....
  .....
  return answer_paramaters

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

import subprocess
from subprocess import Popen, PIPE, STDOUT
import threading
import thread
import time
import steelsquid_utils


class SteelsquidServer(object):
    '''
    The server
    '''
    __slots__ = ['listen_thread', 'executing_command', 'executing_lock', 'async_response', 'async_response_err', 'async_has_executed', 'external_objects']

    #Execute the command on this objects as well
    external_objects=[]
    

    def __init__(self):
        '''
        Constructor.
        '''
        self.executing_command = []
        self.executing_lock = []
        self.async_has_executed = []
        self.async_response = {}
        self.async_response_err = {}

    def on_listen_setup(self):
        '''
        Override this to listen for clients.
        Example listen for clients on a socket.
        Will loop until server is stopped.
        @return: A listener
        '''
        pass

    def on_listen(self, listener):
        '''
        Override this to listen for clients.
        Example listen for clients on a socket.
        Will loop until server is stopped.
        @param listener: Use this object to listen
        @return: A client (None = do nothing)
        '''
        time.sleep(1)
        return None
    
    def on_listen_close(self, listener, error):
        '''
        Close the listener.
        Will also execute on error in listener
        Override this to log or other thing
        @param listener: The listener (Can be None)
        @param error: The error (Can be None)
        '''
        steelsquid_utils.shout("Server: Listener closed", debug=True)

    def on_client_command(self, client):
        '''
        Override this to read command from client.
        Example listen for command on socket
        @param client: Read command from this client
        @return: (command, parameters) 
                 command = None, parameters=None (disconnect client)
                 command = None, parameters!=None (do nothing)
        '''
        return None, None

    def on_client_answer(self, client, command, is_ok, answer_list):
        '''
        Override this to write to client.
        Example write answer on socket
        @param client: Write to this client
        @param command: The command
        @param is_ok: Has command executed OK
        @param answer_list: Answer list
        @return: True = Continue to listen for command
                 False = Close connection
        '''
        return False

    def on_client_close(self, client, error):
        '''
        Override this to close connection to client.
        This will also execute if error in connection to client
        @param client: Close this client
        @param error: optionally error (Can be None)
        '''
        steelsquid_utils.shout("Server: Client closed\n" + str(client), debug=True)


    def start_server(self):
        '''
        Start this server
        '''
        self.listen_thread = ListenThread(self)
        self.listen_thread.start()


    def stop_server(self):
        '''
        Stop this server
        '''
        try:
            self.listen_thread.stop_thread()
        except:
            pass

    def lock_command(self, command):
        '''
        Lock command until execut finished
        '''
        self.executing_lock.append(command)

    def is_locked(self, command):
        '''
        Is this command locked.
        '''
        return command in self.executing_lock

    def is_executing(self, command):
        '''
        Is a command executing.
        '''
        return command in self.executing_command

    def has_executed(self, command):
        '''
        Has command executed.
        '''
        return command in self.async_has_executed

    def get_async_answer(self, command):
        '''
        Get the async answer.
        '''
        try:
            return list(self.async_response[command])
        except:
            return []

    def get_async_answer_err(self, command):
        '''
        Get the async answer error (None = no error).
        '''
        try:
            return self.async_response_err[command]
        except:
            return None

    def clear_async_answer(self, command):
        '''
        Clear the async answer.
        '''
        self.async_response[command] = []
        self.async_response_err[command] = None
        try:
            self.async_has_executed.remove(command)
        except:
            pass
        
        
    def add_async_answer(self, command, parameters):
        '''
        Add paramater to async answer.
        paramater can be (bool, int, float, string) or a list of (bool, int, float, string)
        '''
        the_answer = self.async_response[command]
        
        if isinstance(parameters, (list)):
            for string in parameters:
                if isinstance(string, basestring):
                    the_answer.append(steelsquid_utils.decode_string(string))
                elif isinstance(string, (int, long, float)):
                    the_answer.append(str(string))
                elif isinstance(string, bool):
                    if string:
                        the_answer.append("True")
                    else:
                        the_answer.append("False")
                else:
                    raise RuntimeError("Unknown paramater type, must be (bool, int, float, string) or a list of (bool, int, float, string)")
        elif isinstance(parameters, basestring):
            the_answer.append(parameters)
        elif isinstance(parameters, (int, long, float)):
            the_answer.append(str(parameters))
        elif isinstance(parameters, bool):
            if parameters:
                the_answer.append("True")
            else:
                the_answer.append("False")
        else:
            raise RuntimeError("Unknown paramater type, must be (bool, int, float, string) or a list of (bool, int, float, string)")

        if len(the_answer)>256:
            the_answer = the_answer[:256]
        
        self.async_response[command] = the_answer


    def execute_system_command(self, system_command, command=None):
        '''
        Execute a system command 
        @param system_command: The system command to execute
        @param command: If this is set the answer will be appended to async answer string.
        @return: If command==None the answer will be returned as a array
        '''
        proc=Popen(system_command, stdout = PIPE, stderr = STDOUT)  
        answer = []
        for line in iter(proc.stdout.readline, b''):
            line = line.strip('\n').strip()
            if len(line) > 0:
                if command == None:
                    answer.append(line)
                else:
                    self.add_async_answer(command, line)
        status = proc.wait()
        if status == 0:
            return answer
        else:
            if line != None and len(line) != 0:
                raise RuntimeError(line)
            else:
                raise RuntimeError("Exception status: " + str(status))


    def execute_system_command_blind(self, system_command):
        '''
        Execute a system command and do not read answer or throw exception.
        @param system_command: The system command to execute
        '''
        try:
            proc=Popen(system_command, stdout = PIPE, stderr = STDOUT)  
            proc.wait()
        except:
            pass

    def execute(self, command, session_id=None, parameters=None):
        '''
        Execute the command (method with same name as the command)
        Will raise a RuntimeError on error
        The parameters will be convertet to a list of strings before sent to command.
        String => [String]
        int => [String]
        bool => [True/False]
        @param command: Command to execute
        @param session_id: send a session_id with the command
        @param paramaters: Paramaters (list of bool, int, float, string or a single bool, int, float, string)
        @return: Answer list
        '''
        if command in self.executing_lock:
            raise RuntimeError("Work in progress, please wait!")
        else:
            try:
                self.executing_command.append(command)
                self.async_response[command] = []
                self.async_response_err[command] = None
                if not parameters == None:
                    if isinstance(parameters, (list)):
                        count = 0
                        for string in parameters:
                            if isinstance(string, basestring):
                                parameters[count] = steelsquid_utils.decode_string(string)
                            elif isinstance(string, bool):
                                if string:
                                    parameters[count] = "True"
                                else:
                                    parameters[count] = "False"
                            else:
                                parameters[count] = str(string)
                            count = count + 1
                    elif isinstance(parameters, basestring):
                        parameters = [steelsquid_utils.decode_string(parameters)]
                    elif isinstance(parameters, bool):
                        if parameters:
                            parameters = ["True"]
                        else:
                            parameters = ["False"]
                    else:
                        parameters = [str(parameters)]
                else:
                    parameters = []
                
                the_answer = None
                is_found=False
                if hasattr(self, command):
                    is_found=True
                    fn = getattr(self, command)
                    if session_id!=None:
                        the_answer = fn(session_id, parameters)
                    else:
                        the_answer = fn(parameters)
                else:
                    for o in self.external_objects:
                        if hasattr(o, command):
                            is_found=True
                            fn = getattr(o, command)
                            if session_id!=None:
                                the_answer = fn(session_id, parameters)
                            else:
                                the_answer = fn(parameters)
                if not is_found:
                    raise RuntimeError("Command "+command+" not found!")
                self.async_has_executed.append(command)
                if the_answer == None:
                    return []
                elif isinstance(the_answer, (list)):
                    count = 0
                    for string in the_answer:
                        if isinstance(string, basestring):
                            the_answer[count] = steelsquid_utils.encode_string(string)
                        elif isinstance(string, bool):
                            if string:
                                the_answer[count] = "True"
                            else:
                                the_answer[count] = "False"
                        elif string == None:
                                the_answer[count] = "None"
                        else:
                            the_answer[count] = str(string)
                        count = count + 1
                    return the_answer
                elif isinstance(the_answer, basestring):
                    return [steelsquid_utils.encode_string(the_answer)]
                elif isinstance(parameters, bool):
                    if parameters:
                        return ["True"]
                    else:
                        return ["False"]
                elif parameters == None:
                    return ["None"]
                else:
                    return [str(the_answer)]
            except RuntimeError, err:
                self.async_response_err[command] = str(err)
                raise err
            except:
                import traceback                
                import sys
                exc_type, exc_value, exc_traceback = sys.exc_info()
                self.async_response_err[command] = str(exc_value)
                raise RuntimeError, (exc_value), exc_traceback
            finally:
                self.executing_command.remove(command)
                try:
                    self.executing_lock.remove(command)
                except:
                    pass


class ListenThread(threading.Thread):
    '''
    Thread that listens for clients.
    '''

    __slots__ = ['running', 'server', 'listener', 'clients']

    def __init__(self, server):
        '''
        Constructor.
        '''
        self.running = True
        self.server = server
        self.clients = []
        threading.Thread.__init__(self)

    def run(self):
        '''
        Thread main method
        '''
        while self.running:
            self.listener = None
            error = None
            try:
                self.listener = self.server.on_listen_setup()
                while self.running:
                    client = self.server.on_listen(self.listener)
                    if client == self.listener:
                        self.handle(client)
                    elif client != None:
                        thread.start_new_thread(self.handle, (client,))
            except Exception, err:
                error = err
            try:
                self.server.on_listen_close(self.listener, error)
            except Exception, e:
                pass
            time.sleep(1)

    def handle(self, client):
        '''
        Handle a client.
        '''
        self.clients.append(client)
        error = None
        connected = True
        try:
            while connected:
                command, parameters = self.server.on_client_command(client)
                if not self.running:
                    connected = False
                elif command == None and parameters == None:
                    connected = False
                elif command == None and parameters != None:
                    pass
                else:
                    answer_list = None
                    is_ok = True
                    try:
                        answer_list = self.server.execute(command, None, parameters)
                    except:
                        is_ok = False
                        import traceback
                        import sys
                        exc_type, exc_var, exc_traceback = sys.exc_info()            
                        answer_list = [str(exc_var)]
                        del exc_traceback
                    connected = self.server.on_client_answer(client, command, is_ok, answer_list)
        except:
            try:
                import sys
                error = sys.exc_info()[0]
            except:
                pass
        self.clients.remove(client)
        try:
            self.server.on_client_close(client, error)
        except:
            pass
            

    def stop_thread(self):
        '''
        Stop this thread.
        '''
        self.running = False
        try:
            self.server.on_listen_close(self.listener, None)
        except:
            pass
