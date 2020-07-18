#! /usr/bin/python2
"""
This module walks data dir and builds a log of data collected

"""
import os
import numpy as np
import math
import rosbag
from tf.transformations import euler_from_quaternion

os.chdir("/media/user1/BHG_USMA04")
for root, dirs, files in os.walk(".", topdown = False):
    for name in files:
        outstring = ''
        if (name.endswith('.bag')):
            fullname = os.path.join(root, name)
            messages = rosbag.Bag(fullname).read_messages()
            i = 0
            sum_hdg = 0
            for topic, msg, t in rosbag.Bag(fullname).read_messages():  
                if('/mavros/global_position/compass_hdg' == topic):
                    if(i > 100): 
                        sum_hdg += msg.data      
                    i += 1
                if(i > 200):
                    break 
                if('/mavros/imu/data' == topic):
                    quaternion = [msg.orientation.x,msg.orientation.y,msg.orientation.z,msg.orientation.w]
                    (roll,pitch,yaw) = euler_from_quaternion(quaternion)

            outstring += str(sum_hdg/(i-100))    

#            (roll,pitch,yaw) = euler_from_quaternion(quaternion)
#            yaw = yaw * 180 / 3.14
#            roll = roll * 180 / 3.14
#            pitch = pitch * 180 / 3.14
#            outstring +=  ", " + str(roll)  + ", " + str(pitch)  + ", " + str(yaw)   
            print(outstring)

            exit(0)
            
'''            
        if (name.endswith('flir.csv')):
            fullname = os.path.join(root, name)
            with open(fullname, 'r') as f:
                lines = f.readlines()
                count = len(lines)
                mdcnt = int(count/2)
                start_line = lines[20].split(',')
                midle_line = lines[mdcnt].split(',')
                endrn_line = lines[count-50].split(',')
                start_LL = (start_line[8],start_line[9])
                midle_LL = (midle_line[8],midle_line[9])
                endrn_LL = (endrn_line[8],endrn_line[9])
                #outstring = fullname,count,start_LL,midle_LL,endrn_LL
                if (start_LL < endrn_LL):
                    outstring += ',w2e,'
                else:
                    outstring += ',e2w,'
                # get avarage magnetometer readings 
                sum_mag_x = 0
                sum_mag_y = 0 
                sum_mag_z = 0        
                #print(midle_line[10],midle_line[11],midle_line[12],midle_line[13],midle_line[14])   
                for i in range(mdcnt - 100, mdcnt + 100):
                    sum_mag_x =+ (int)((float)(midle_line[11]))
                    sum_mag_y =+ (int)((float)(midle_line[12]))
                    sum_mag_z =+ (int)((float)(midle_line[13]))
                avg_mag_x = sum_mag_x / 200
                avg_mag_y = sum_mag_y / 200
                avg_mag_z = sum_mag_z / 200
                    
                heading = quaternion_to_euler_angle_vectorized1((float)(midle_line[14]),(float)(midle_line[15]),(float)(midle_line[16]),(float)(midle_line[17]))[2]

                if (avg_mag_y > 0):
                    angle = 90 - math.atan2(avg_mag_x,avg_mag_y) * 180 / 3.14
                elif (avg_mag_y < 0):
                    angle = 270 - math.atan2(avg_mag_x,avg_mag_y) * 180 / 3.14
                elif (avg_mag_y == 0 and avg_mag_x < 0):
                    angle = 180.0
                else: # (avg_mag_y = 0 and avg_mag_x > 0)
                    angle = 0.0
                print(f'{heading:3.2f},{angle:3.2f}    {fullname}')

    #for name in dirs:
        #print(os.path.join(root, name))
        
'''
