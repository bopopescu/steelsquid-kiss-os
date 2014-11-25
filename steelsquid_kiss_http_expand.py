#!/usr/bin/python -OO


'''
Use this to implement HTTP stuff, will execute on boot
Do not execute long running stuff or the system won't start properly.
This will always execute with root privilege.

Use this to expand the capabilities of the webserver.
The web-server will be started by steelsquid_boot.py
See steelsquid-kiss-http-server.py for example

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import steelsquid_kiss_http_server
import steelsquid_utils
import steelsquid_event
import os
import time


class SteelsquidKissExpandHttpServer(steelsquid_kiss_http_server.SteelsquidKissHttpServer):
    
    __slots__ = []

    def __init__(self, port, root, authorization, only_localhost, local_web_password, use_https):
        super(SteelsquidKissExpandHttpServer, self).__init__(port, root, authorization, only_localhost, local_web_password, use_https)





