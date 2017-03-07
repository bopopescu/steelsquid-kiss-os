#!/usr/bin/python -OO


'''
Use this to communicate with i2c devices.
I have just simplified it a little.

I have also added some synchronization that can be activated 
if there would be problems when there are many devices on the bus.

If you want to lock multiple commands:
with steelsquid_i2c.Lock():
   ...

This will only lock if use_lock(True) (default false)

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-10-25 Created
'''

import steelsquid_utils
import smbus
import re


bus = smbus.SMBus(steelsquid_utils.get_pi_i2c_bus_number())


def read_8_bit_raw(address, signed=False):
    '''
    Read signed or unsigned 8-bit from a device, without specifying a device register.
    '''
    value = bus.read_byte(address)
    if signed:
        if result > 127: result -= 256
    return value


def read_8_bit(address, register, signed=False):
    '''
    Read signed or unsigned 8-bit from a device register
    '''
    result = bus.read_byte_data(address, register)
    if signed:
        if result > 127: result -= 256
    return result


def read_16_bit(address, register, signed=False, little_endian=True):
    '''
    Read signed or unsigned 16-bit from a device register
    Swap bytes if using big endian because read_word_data assumes little 
    endian on ARM (little endian) systems.    

    Big Endian: Most significant byte in the smallest address
    Little Endian: Least significant byte in the smallest address
    '''
    result = bus.read_word_data(address, register)
    if not little_endian:
        result = ((result << 8) & 0xFF00) + (result >> 8)
    if signed:
        if result > 32767: result -= 65536
    return result


def read_16_bit_command(address, register, command_bytes, signed=False, little_endian=True):
    '''
    Read signed or unsigned 16-bit from the device register
    With this you can also send a command.
    First the register is sent then the command_bytes
    command_bytes = Byte list
    number_of_bytes_to_read = Number of bytes to read
    Return = 16-bit
    Big Endian: Most significant byte in the smallest address
    Little Endian: Least significant byte in the smallest address
    '''
    by = read_bytes_command(address, register, command_bytes, 2)
    if little_endian:
        result = steelsquid_utils.hight_low_byte_to_int(by[1], by[0])
    else:
        result = steelsquid_utils.hight_low_byte_to_int(by[0], by[1])
    if signed:
        if result > 32767: result -= 65536
    return result        


def read_bytes(address, register, number_of_bytes_to_read, signed=False):
    '''
    Read signed or unsigned byte list from the device register
    number_of_bytes_to_read = Number of bytes to read
    Return = a list of bytes
    '''
    result = bus.read_i2c_block_data(address, register, number_of_bytes_to_read)
    if signed:
        for i, b in result:
            if b > 127:
                result[i] = b - 256
    return result


def read_bytes_command(address, register, command_bytes, number_of_bytes_to_read, signed=False):
    '''
    Read signed or unsigned byte list from the device register
    With this you can also send a command.
    First the register is sent then the command_bytes
    command_bytes = Byte list
    number_of_bytes_to_read = Number of bytes to read
    Return = a list of bytes
    '''
    write_bytes(address, register, command_bytes)
    byte_l = []
    for i in range(number_of_bytes_to_read):
        byte_l.append(read_8_bit_raw(address, signed))
    return byte_l


def write_8_bit_raw(address, byte):
    '''
    Writes an 8-bit value to a device, without specifying a device register.
    '''
    bus.write_byte(address, byte)


def write_8_bit(address, register, byte):
    '''
    Writes an 8-bit value to a device register
    '''
    bus.write_byte_data(address, register, byte)


def write_16_bit(address, register, char_to_send, reverse_byte_order=False):
    '''
    Writes an 16-bit value to a device register
    '''
    if reverse_byte_order:
        char_to_send = steelsquid_utils.reverse_byte_order(char_to_send)
    return bus.write_word_data(address, register, char_to_send)


def write_bytes(address, register, bytes_to_send):
    '''
    Writes several bytes to a device register
    '''
    bus.write_i2c_block_data(address, register, bytes_to_send)


    
