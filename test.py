#!/usr/bin/python -OO
# -*- coding: latin-1 -*-
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
import steelsquid_hmtrlrs
import logging
import sys
import time

import steelsquid_bno0055



while True:
    heading, roll, pitch = steelsquid_bno0055.read(switch_roll_pitch=True)
    #if steelsquid_bno0055.is_initialized():
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}'.format(heading, roll, pitch))
    time.sleep(0.01)
