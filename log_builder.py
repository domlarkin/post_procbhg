#! /usr/bin/python2
"""
This module walks data dir and builds a log of data collected
find . -maxdepth 4 -name "2020*"  | sort >> ~/Desktop/usma04d_sorted.txt

"""
import os
import numpy as np
import math
import rosbag
from tf.transformations import euler_from_quaternion


outfilename = '/home/user1/Data/flightlogs_dbocheck.csv'
with open(outfilename, 'w') as outfile:
    outfile.write('filename,hdg,s_lat,s_lon,m_lat,m_lon,e_lat,e_lon,dir,cog\n')
os.chdir("/media/user1/BHG_USMA04")
for root, dirs, files in os.walk(".", topdown = False):
    for name in files:
        outstring = ''
        fullname = os.path.join(root, name)
        if (name.endswith('.bag') and ('L7' in fullname)):
            outfilename = name.split('.')[0] + ".csv"
            fulloutfilename = os.path.join(root, outfilename)
            start_time = name.split('.')[0][4:]
            hdg_list = []
            ll_list = []
            pose_list = []
            rel_alt=[]
            glbl_pos=[]
            lcl_pos=[]
            with open(fulloutfilename, 'w') as outfile:
                outfile.write('TODO: Header goes here,Directory,\n')
            outstring += fullname.split('b')[0]
            for topic, msg, t in rosbag.Bag(fullname).read_messages():   
                if('/mavros/global_position/compass_hdg' == topic):
                    hdg_list.append([t,msg.data])
                if('/mavros/global_position/global' == topic):
                    ll_list.append([t,msg.latitude,msg.longitude,msg.altitude])   
                if('/mavros/local_position/pose' == topic):  
                    quaternion = (msg.pose.orientation.x,msg.pose.orientation.y,msg.pose.orientation.z,msg.pose.orientation.w)
                    (roll, pitch, yaw) = euler_from_quaternion(quaternion)
                    pose_list.append([t,roll, pitch, yaw,msg.pose.position.z]) 
                if('/mavros/global_position/rel_alt' == topic):  
                    rel_alt.append([t,msg.data])
                if('/mavros/global_position/local' == topic):  
                    glbl_pos.append([t,msg.pose.pose.position.z])
                if('/mavros/local_position/pose' == topic):  
                    lcl_pos.append([t,msg.pose.position.z])
                    
                

                        
            exit(0)       
                         
'''                
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
'''
