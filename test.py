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


print steelsquid_pi._dht11_temp_hum(10)
