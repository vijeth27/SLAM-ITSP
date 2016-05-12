#!/usr/bin/python
import smbus
import math
import time

# Power management registers

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val
 
def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_z_rotation(x,y,z):
    radians = math.atan2(dist(x,y),z)
    return radians

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)
 
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards

address = 0x68       # This is the address value read via the i2cdetect command
G_GAIN = 0.02
DT=0.05
gyroXangle = 0
gyroYangle = 0
gyroZangle = 0
M_PI = 3.14
RAD_TO_DEG = 57.29578 
AA = 0.98
CFangleX = 0
CFangleY = 0
CFangleZ = 0
# Now wake the 6050 up as it starts in sleep mode
while True:
    bus.write_byte_data(address, power_mgmt_1, 0)

    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
#  print  "gyro data "" x: ",(gyro_xout / 131)," y: ",(gyro_yout / 131)," z: ",(gyro_zout / 131)
        
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
     
    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0
    rate_gyr_x = float(gyro_xout * G_GAIN)
    rate_gyr_y = float(gyro_yout * G_GAIN)
    rate_gyr_z = float(gyro_zout * G_GAIN)
    gyroXangle+=rate_gyr_x*DT
    gyroYangle+=rate_gyr_y*DT
    gyroZangle+=rate_gyr_z*DT
    AccXangle = float(math.atan2(accel_yout, accel_zout_scaled )+M_PI)*RAD_TO_DEG
    AccYangle = float(math.atan2(accel_zout_scaled, accel_xout_scaled)+M_PI)*RAD_TO_DEG
    AccZangle = float(math.atan2(accel_xout_scaled, accel_yout_scaled)+M_PI)*RAD_TO_DEG
    CFangleX=AA*(CFangleX+rate_gyr_x*DT) +(1 - AA) * AccXangle;
    CFangleY=AA*(CFangleY+rate_gyr_y*DT) +(1 - AA) * AccYangle;
    CFangleZ=AA*(CFangleZ+rate_gyr_z*DT) +(1 - AA) * AccZangle;
    print CFangleZ
    time.sleep(0.2)
    
