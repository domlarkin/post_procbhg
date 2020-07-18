#! /usr/bin/python2
"""
This module walks data dir and builds a log of data collected

"""
 
import matplotlib
matplotlib.use('Agg') # Bypass the need to install Tkinter GUI framework

import os
import numpy as np
import math
import rosbag
from tf.transformations import euler_from_quaternion

import matplotlib.pyplot as plt


# https://openwritings.net/pg/python-find-whether-point-above-or-below-line
is_above = lambda p,a,b: np.cross(p-a, b-a) > 0


l70_nw = np.array([32.848635, -114.273121])
l70_sw = np.array([32.848492, -114.273110])
l72_nw = np.array([32.847735, -114.273058])
l72_sw = np.array([32.847575, -114.273050])
l70_ne = np.array([32.848710, -114.253374])
l70_se = np.array([32.848573, -114.253368])
l72_ne = np.array([32.847798, -114.253402])
l72_se = np.array([32.847671, -114.253389])

def find_cog(ll_in):
    pnt = np.array([ll_in[0],ll_in[1]])
    #print(pnt,l70_nw,l70_ne)
    if is_above(pnt, l70_nw,l70_ne):
        outstring='north of L70'
    elif is_above(pnt, l70_sw,l70_se):
        outstring='over L70'
    elif is_above(pnt, l72_nw,l72_ne):
        outstring='between L70 and L72'
    elif is_above(pnt, l72_sw,l72_se):
        outstring='over L72'
    else:
        outstring='south of L72'
    return outstring


outfilename = '/home/user1/Data/flightlogs_dbocheck.csv'
with open(outfilename, 'w') as outfile:
    outfile.write('filename,hdg,s_lat,s_lon,m_lat,m_lon,e_lat,e_lon,dir,cog\n')
os.chdir("/media/user1/BHG_USMA04")
for root, dirs, files in os.walk(".", topdown = False):
    for name in files:
        outstring = ''
        fullname = os.path.join(root, name)
        if (name.endswith('.bag') and ('L7' in fullname)):
            fullname = os.path.join(root, name)
            outstring = fullname + ','
            messages = rosbag.Bag(fullname).read_messages()
            i = 0
            hdg_list = []
            ll_list = []
            for topic, msg, t in rosbag.Bag(fullname).read_messages():  
                if('/mavros/global_position/compass_hdg' == topic):
                    hdg_list.append(float(msg.data))

                if('/mavros/global_position/global' == topic):
                    ll_list.append([msg.header.stamp.to_sec(),(msg.latitude,msg.longitude),msg.altitude])
            avg_start = len(hdg_list)/2
            avg_stop = avg_start + 100
            sum_hdg = 0 
            for i in range(avg_start,avg_stop):
                sum_hdg += hdg_list[i]
            avg_hdg = sum_hdg/100
            outstring += str(avg_hdg) + ','
            start_ll = ll_list[20]
            outstring += str(start_ll[1][0]) + "," + str(start_ll[1][1]) + ","
            mid_ll = ll_list[int(len(ll_list)/2)]
            outstring += str(mid_ll[1][0]) + "," + str(mid_ll[1][1]) + ","
            end_ll = ll_list[int(len(ll_list)-20)]
            outstring += str(end_ll[1][0]) + "," + str(end_ll[1][1])
            if (start_ll[1][1] < end_ll[1][1]):
                outstring += ',w2e,'
            else:
                outstring += ',e2w,'
            outstring += find_cog(mid_ll[1])    
            print(outstring)
            with open(outfilename, 'a') as outfile:
                outfile.write(outstring+'\n')
#            for item in ll_list:
#                print(item)
#            exit(0)
            
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
