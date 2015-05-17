#!/usr/bin/python -OO


'''
Bluetooth implementation of steelsquid_connection...
UNDER CONSTRUCTION

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2015-03-17 Created
'''


import steelsquid_connection
import steelsquid_utils
import bluetooth
import sys
import select


class SteelsquidBluetoothConnection(steelsquid_connection.SteelsquidConnection):

    __slots__ = ['port', 'host']

    def __init__(self, is_server, host, port=1):
        '''
        Constructor
        '''
        super(SteelsquidBluetoothConnection, self).__init__(is_server)
        self.host = host
        self.port = port


    def on_setup_client(self):
        '''
        Override this to setup the client.
        Example setup socket
        Will loop until server is stopped.
        @return: Connection object (example socket)
        '''
        sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        steelsquid_utils.shout("Bluettoth Connection: Client\n"+self.host +":"+ str(self.port), debug=True)
        return sock


    def on_setup_server(self):
        '''
        Override this to setup the server.
        Example setup the serversocket
        Will loop until server is stopped.
        @return: Listener object (example serversocket)
        '''
        server_sock.bind(("", self.port))
        server_sock.listen(3)
        steelsquid_utils.shout("Bluetooth Connection: Server "+str(self.port), debug=True)
        return s


    def on_connect(self, connection_object):
        '''
        Override this to connect to a server.
        Example connect to a socket.
        Will loop until server is stopped.
        @param connection_object: The object from on_setup_client
        @return: connection_object (the connection_object object)
        '''
        sock.connect((self.host, self.port))
        steelsquid_utils.shout("Bluetooth Connection: Connected to server", debug=True)
        return connection_object


    def on_listen(self, listener_object):
        '''
        Override this to start the server listen for connection functionality.
        Example listen for clients on a socket.
        Will loop until server is stopped.
        @param listener_object: The object from on_setup_server
        @return: connection_object (None = do nothing)
        '''
        try:
            sock, _ = listener_object.accept()
            steelsquid_utils.shout("Bluetooth Connection: Client connected", debug=True)
            return sock
        except socket.timeout:
            return None


    def on_read(self, connection_object):
        '''
        Override this to listen for data.
        Example listen for requests on socket
        @param connection_object: Read from this client
        @return: (type, command, parameters) 
                 (type = request, response, error)
                 command = None (do nothing)
        '''
        ready_to_read, ready_to_write, in_error = select.select([connection_object], [], [], 2)
        if ready_to_read:
            data = connection_object.makefile().readline()
            if not data:
                raise IOError("Connection lost")
            else:
                data_array = data.rstrip().split("|")
                if len(data_array) >= 2:
                    typ = data_array[0]
                    command = data_array[1]
                    para = data_array[2:]
                    return typ, command, para
                else:
                    return None, None, None
        else:        
            return None, None, None


    def on_write(self, the_type, connection_object, command, parameters):
        '''
        Override this to send data to host.
        Example write request on socket
        @param the_type: "request", "response", "error"
        @param connection_object: Write to this client
        @param command: The command
        @param answer_list: parameters
        @return: True = Continue
                 False = Close connection
        '''
        answ = "|".join(parameters)
        connection_object.sendall(the_type+ "|" + command + "|" + answ + "\n")
        return True


    def on_close_connection(self, connection_object, error_message):
        '''
        Override this to close the connection.
        Will also execute on connection lost or no connection
        @param server_object: The connection (Can be None)
        @param error_message: I a error (Can be None)
        '''
        steelsquid_utils.shout("Bluetooth Connection: Connection closed\n"+ error_message, debug=True)
        connection_object.close()

    
    def on_close_listener(self, listener_object, error_message):
        '''
        Override this to close the listener.
        Will also execute on unable to listen
        @param listener_object: The listener (Can be None)
        @param error_message: I a error (Can be None)
        '''
        steelsquid_utils.shout("Bluetooth Connection: Listener closed: " + error_message, debug=True)
        listener_object.close()





    def test_request(self, parameters):
        print "REQUEST"
        print parameters

    def test_response(self, parameters):
        print "RESPONSE"
        print parameters

    def test_error(self, parameters):
        print "ERROR"
        print parameters


if __name__ == "__main__":
    steelsquid_utils.set_development()
    if sys.argv[1] == "client":
        rover = SteelsquidBluetoothConnection(False)
        rover.start()
        try:
            raw_input("Press Enter to send")
            rover.send_request("test", ["kalle", "kula"])
        except:
            print sys.exc_info()        
        raw_input("Press Enter to exit server...")
        rover.stop()
    elif sys.argv[1] == "server":
        rover = SteelsquidBluetoothConnection(True)
        rover.start()
        try:
            raw_input("Press Enter to send")
            rover.send_request("test", ["kalle", "kula"])
        except:
            print sys.exc_info()        
        raw_input("Press Enter to exit server...")
        rover.stop()

