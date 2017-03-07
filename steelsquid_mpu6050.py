#!/usr/bin/python -OO


'''
Read values from mpu-6050

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

import steelsquid_utils
import thread
import smbus
import math
import time
import numpy
import datetime

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

gyro_scale = 131.0
accel_scale = 16384.0
address = 0x68
now = time.time()
K = 0.98
K1 = 1 - K

gyro_offset_x = None
gyro_offset_y = None
gyro_offset_z = None
    
zero_it = False
calibrate_it = True
samples = 201
x=-1
y=-1
z=-1

last_x = None
last_y = None
gyro_total_x = None
gyro_total_y = None
gyro_total_z = None
gyro_mean_x = [None]*samples
gyro_mean_y = [None]*samples
gyro_mean_z = [None]*samples        
accel_mean_x = [None]*samples
accel_mean_y = [None]*samples
accel_mean_z = [None]*samples   
drift_mean = [None]*(samples-1)
drift = 0    
last = 0

def _thread():
    '''
    Thread read from mpu6050
    '''
    while True:
        try:
            _worker()
        except:
            steelsquid_utils.shout()


def _worker():
    '''
    Read from mpu6050
    '''
    global x
    global y
    global z
    global zero_it
    global calibrate_it
    global gyro_offset_x
    global gyro_offset_y
    global gyro_offset_z    
    global last_x
    global last_y
    global gyro_total_x
    global gyro_total_y
    global gyro_total_z
    global gyro_mean_x
    global gyro_mean_y
    global gyro_mean_z      
    global accel_mean_x
    global accel_mean_y
    global accel_mean_z 
    global drift_mean
    global drift
    global last    
    if calibrate_it:
        last_z = None
        # Calculate the offset and z drift
        for i in range(samples):
            time.sleep(0.02) 
            gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z = read_all()
            last = datetime.datetime.now()
            gyro_mean_x[i] = gyro_x
            gyro_mean_y[i] = gyro_y
            gyro_mean_z[i] = gyro_z
            accel_mean_x[i] = accel_x
            accel_mean_y[i] = accel_y
            accel_mean_z[i] = accel_z
            # Drift for Z
            if last_z==None:
                last_z = gyro_z
            else:
                drift_mean[i-1] = last_z - gyro_z
                last_z = gyro_z
        # Get mean value for gyro and accel
        gyro_x = numpy.mean(gyro_mean_x)
        gyro_y = numpy.mean(gyro_mean_y)
        gyro_z = numpy.mean(gyro_mean_z)
        accel_x = numpy.mean(accel_mean_x)
        accel_y = numpy.mean(accel_mean_y)
        accel_z = numpy.mean(accel_mean_z)
        # Get mean value for drift of Z
        drift = numpy.mean(drift_mean)
        # Save the offset
        gyro_offset_x = gyro_x 
        gyro_offset_y = gyro_y
        gyro_offset_z = gyro_z
        # Save last value
        last_x = get_x_rotation(accel_x, accel_y, accel_z)
        last_y = get_y_rotation(accel_x, accel_y, accel_z)
        # Set all angeles to 0
        gyro_total_x = 0.0
        gyro_total_y = 0.0
        gyro_total_z  = 0.0
        calibrate_it=False
    else:
        # Read values
        gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z = read_all()
        new = datetime.datetime.now()
        time_diff = (new - last).total_seconds()
        last = new
        # Zero Z axis
        if zero_it:
            zero_it=False
            gyro_offset_z = gyro_z
            gyro_total_z  = 0.0
        # Calculate from offset
        gyro_x -= gyro_offset_x
        gyro_y -= gyro_offset_y
        gyro_z -= gyro_offset_z
        # Add the drift to Z
        gyro_z = gyro_z + drift
        # Make some magic
        gyro_x_delta = gyro_x * time_diff
        gyro_y_delta = gyro_y * time_diff
        gyro_z_delta = gyro_z * time_diff
        gyro_total_x += gyro_x_delta
        gyro_total_y += gyro_y_delta
        gyro_total_z += gyro_z_delta
        rotation_x = get_x_rotation(accel_x, accel_y, accel_z)
        rotation_y = get_y_rotation(accel_x, accel_y, accel_z)
        last_x = K * (last_x + gyro_x_delta) + (K1 * rotation_x)
        last_y = K * (last_y + gyro_y_delta) + (K1 * rotation_y)
        # Set the finished values
        x=last_x
        y=last_y
        z=gyro_total_z



def read_all():
    raw_gyro_data = bus.read_i2c_block_data(address, 0x43, 6)
    raw_accel_data = bus.read_i2c_block_data(address, 0x3b, 6)
    gyro_scaled_x = twos_compliment((raw_gyro_data[0] << 8) + raw_gyro_data[1]) / gyro_scale
    gyro_scaled_z = twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / gyro_scale
    gyro_scaled_y = twos_compliment((raw_gyro_data[4] << 8) + raw_gyro_data[5]) / gyro_scale
    accel_scaled_x = twos_compliment((raw_accel_data[0] << 8) + raw_accel_data[1]) / accel_scale
    accel_scaled_z = twos_compliment((raw_accel_data[2] << 8) + raw_accel_data[3]) / accel_scale
    accel_scaled_y = twos_compliment((raw_accel_data[4] << 8) + raw_accel_data[5]) / accel_scale
    return (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z)


def read_gyro_z():
    raw_gyro_data = bus.read_i2c_block_data(address, 0x43, 6)
    gyro_scaled_z = twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / gyro_scale
    return gyro_scaled_z
    
    
def twos_compliment(val):
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
    
    
def get_angle():
    '''
    Get x and y angle
    '''
    return x, y, z
    
    
def calibrate():
    '''
    Current postition is zero and messure drift
    Takes about 10 seconds
    '''
    global calibrate_it
    calibrate_it=True


def zero():
    '''
    Set Current postition is zero
    '''
    global zero_it
    zero_it=True
    

def start(start_thread = True):
    '''
    Start the reader thread
    '''
    global bus
    bus = smbus.SMBus(1)
    bus.write_byte_data(address, power_mgmt_1, 0)
    if start_thread:
        thread.start_new_thread(_thread, ())




