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


#Enter a dir with a bagfile then begin
def parse_bagfile(bagfilename):
    hdg_list = []
    ll_list = []
    pose_list = []
    rel_alt=[]
    glbl_pos=[]
    lcl_pos=[]
    outlist = []
    for topic, msg, t in rosbag.Bag(fullname).read_messages():   
        if('/mavros/global_position/compass_hdg' == topic):
            outlist.append([t.to_nsec(),topic,msg.data])
        elif('/mavros/global_position/global' == topic):
            outlist.append([t.to_nsec(),topic,msg.latitude,msg.longitude,'','',msg.altitude])   
        elif('/mavros/local_position/pose' == topic):  
            quaternion = (msg.pose.orientation.x,msg.pose.orientation.y,msg.pose.orientation.z,msg.pose.orientation.w,msg.pose.position.z)
            (roll, pitch, yaw) = euler_from_quaternion(quaternion)
            outlist.append([t.to_nsec(),topic,roll, pitch, yaw,'',msg.pose.position.z]) 
        elif('/mavros/global_position/rel_alt' == topic):  
            outlist.append([t.to_nsec(),topic,'','','','',msg.data])
        elif('/mavros/global_position/local' == topic):  
            outlist.append([t.to_nsec(),topic,'','','','',msg.pose.pose.position.z])
    return(outlist)




dirs2search = "/media/user1/BHG_USMA03"
for root, dirs, files in os.walk(dirs2search, topdown = True):
    if(len(root.split('/')) == 6): # begin at this depth of the directory tree
        #print(root,files)
        dirs[:] = [] # stop from walking any deeper
        for name in files:
            fullname = os.path.join(root, name)
            if (name.endswith('.bag') and ('L7' in fullname)):
                print('***********   ' + fullname)
                bagfile_results = parse_bagfile(fullname)
                outstring = ''
                outfilename = name.split('.')[0] + ".csv"
                fulloutfilename = os.path.join(root, outfilename)
                start_time = name.split('.')[0][4:]
                outstring += fullname.split('b')[0]
                #outstring += bagfile_results
                with open(fulloutfilename, 'w') as outfile:
                    outfile.write('\n') #TODO put header here
                     
                for line in bagfile_results:

                    outstring = ''
                    for item in line:   
                        outstring += str(item) + ','
                    print(outstring)  
                    with open(fulloutfilename, 'a') as outfile:
                        outfile.write(outstring + '\n') 
                        
        exit()
                
        


# ('/media/user1/BHG_USMA03/L70_Testcase19_GS/20200717_131432_222', ['20200717_131432_222_flir.csv', '20200717_131432_222_gobi.csv', 'bhg_20200717_131432_222.bag'])


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
