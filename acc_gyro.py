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
    radians = math.atan2(x, z)
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, z)
    return math.degrees(radians)

def get_z_rotation(x,y,z):
    radians = math.atan2(y, x)
    return math.degrees(radians)    
 
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
gyro_cummu=0.0
address = 0x68       # This is the address value read via the i2cdetect command
count =0
counter_offset=0
corr=[]

# Now wake the 6050 up as it starts in sleep mode
print "Calibrating Sensors"
for i in range(3):
    j=0
    while (j<48):
        bus.write_byte_data(address, power_mgmt_1, 0)
        gyro_yout = read_word_2c(0x45)
        gyro_cummu=gyro_yout/115*0.07 + gyro_cummu
        corr.append(gyro_cummu)
        j+=1
        time.sleep(0.07)
       
correction=(corr[47] + corr[95] + corr[143])/3 
print correction

while True:
    bus.write_byte_data(address, power_mgmt_1, 0)
#   gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
#   gyro_zout = read_word_2c(0x47)
#  print  "gyro data "" x: ",(gyro_xout / 131)," y: ",(gyro_yout / 131)," z: ",(gyro_zout / 131)
        
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
     
    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0
    
    gyro_cummu=gyro_yout/115*0.07 + gyro_cummu

    y_rot=0.98*(gyro_cummu) + 0.02*get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    #print "gyro data "" x: ",(gyro_xout / 131)," y: ",(gyro_yout / 131)," z: ",(gyro_zout / 131), "accelerometer data "," x: ", (accel_xout / 16384.0)," y: ",(accel_yout / 16384.0)," z: ", (accel_zout / 16384.0)
    # print "x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    # print "y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    time.sleep(0.07)
    count=count+1
    counter_offset=counter_offset+1
    if counter_offset == 48:
        counter_offset = 0
        gyro_cummu=gyro_cummu-correction
    if count == 14:
        count = 0
        print y_rot
