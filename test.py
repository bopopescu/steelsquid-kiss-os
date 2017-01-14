#!/usr/bin/python -OO
import os
import sys
import time
import thread
import serial
import datetime
import threading
import steelsquid_pi
import steelsquid_piio
import steelsquid_utils
import steelsquid_kiss_global
import steelsquid_nrf24
import steelsquid_nm
import steelsquid_tcp_radio
import socket
import steelsquid_ht16k33 as lmatrix


st = os.statvfs('/media/9936-9676')

total = st.f_blocks * st.f_frsize
used = (st.f_blocks - st.f_bfree) * st.f_frsize
free = st.f_bavail * st.f_frsize


print str(int(round(float(used)/float(total)*100, 0)))
