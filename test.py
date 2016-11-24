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

start = time.time()

time.sleep(2)  # or do something more productive

done = time.time()
elapsed = done - start
print(elapsed)
