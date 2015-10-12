#!/usr/bin/python -OO


'''
Use this to implement HTTP stuff, will execute on boot
Do not execute long running stuff or the system won't start properly.
This will always execute with root privilege.

Use this to expand the capabilities of the webserver.
Handle stuff in expand.html
- Your stuff....

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''


import sys
import steelsquid_kiss_http_utils
import steelsquid_utils
import steelsquid_event
import steelsquid_kiss_global
import steelsquid_kiss_expand


class SteelsquidKissHttpServerExpand(steelsquid_kiss_http_utils.SteelsquidKissHttpServerUtils):
    
    __slots__ = []

    def __init__(self, port, root, authorization, only_localhost, local_web_password, use_https):
        super(SteelsquidKissHttpServerExpand, self).__init__(port, root, authorization, only_localhost, local_web_password, use_https)


