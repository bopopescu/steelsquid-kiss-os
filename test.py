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


ser = serial.Serial('/dev/ttyAMA0', parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=8, writeTimeout=0, dsrdtr=True)
ser.write('S0\r')
#print ser.readline()

#steelsquid_pi.gpio_setup_in(2, steelsquid_pi.PULL_UP)
#steelsquid_pi.gpio_setup_in(3, steelsquid_pi.PULL_UP)
