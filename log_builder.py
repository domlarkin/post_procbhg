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
from datetime import datetime

# Parses the bagfile for the relevant information and puts it into a list
# Relevant info is: Heading, Latitude, Longitude, GPS_Altitude, Roll, Pitch, Yaw, Relative_Altitude
# Relative altitude assumes a altitude of zero at the time the UAS was armed for takeoff.
def parse_bagfile(bagfilename):
    hdg_list = []
    ll_list = []
    pose_list = []
    rel_alt=[]
    glbl_pos=[]
    lcl_pos=[]
    hdg_list = []
    gps_list = []
    pos_list = []
    rchd_list = []
    for topic, msg, t in rosbag.Bag(fullname).read_messages():  
        # In the below code the expression: (t.to_nsec()/1000000000.0)-14400 converts time to seconds and Eastern timezone 
        if('/mavros/global_position/compass_hdg' == topic):               
            hdg_list.append([(t.to_nsec()/1000000000.0)-14400,topic,msg.data])   
        elif('/mavros/global_position/global' == topic):
            gps_list.append([(t.to_nsec()/1000000000.0)-14400,topic,msg.latitude,msg.longitude,'','',msg.altitude])
        elif('/mavros/global_position/local' == topic):  
            msg_pose = msg.pose.pose
            quaternion = (msg_pose.orientation.x,msg_pose.orientation.y,msg_pose.orientation.z,msg_pose.orientation.w)
            (roll,pitch,yaw) = euler_from_quaternion(quaternion, axes="sxyz")
            pos_list.append([(t.to_nsec()/1000000000.0)-14400,topic,roll,pitch,yaw,msg_pose.position.z])
        elif('/mavros/mission/reached' == topic): # we are only interested in points between wp2 and wp3
            rchd_list.append([(t.to_nsec()/1000000000.0)-14400,topic,msg.wp_seq])
            print(">>>>>>>>>>>>>>>>>>>",t.to_nsec(),topic,msg.wp_seq)
    return(hdg_list,gps_list,pos_list,rchd_list)


def make_datetime(name):
    '''
    Converts the date time in the filename into 2 outputs. 
    Output 1 is the epoch time for mathmatical comparison
    Output 2 is a human readable string that matches the one used by ardupilot
    '''
    fname_split=name.split('_')  
    m_sec = str((int(fname_split[3][:6])/1000000.0))
    #print(fname_split,str(m_sec))  
    outstring = fname_split[1][:4]+'-'+fname_split[1][4:6]+'-'+fname_split[1][6:8]+' '+fname_split[2][:2]+':'
    outstring += fname_split[2][2:4]+':'+fname_split[2][4:6]+m_sec[1:]

    utc_time = datetime.strptime(outstring, "%Y-%m-%d %H:%M:%S.%f")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return (epoch_time,outstring)



dirs2search = "/media/user1/BHG_USMA03"
dirs2search = "/media/user1/BHG_USMA03/L70_Testcase17/20200713_143510_974"
for root, dirs, files in os.walk(dirs2search, topdown = True):
    if(len(root.split('/')) == 6): # begin at this depth of the directory tree
        dirs[:] = [] # stop from walking any deeper
        for name in files:
            fullname = os.path.join(root, name)
            if (name.endswith('.bag') and ('L7' in fullname)):
            
                # Parse bag file before generating csv file.
                print('***********   ' + fullname)
                (hdg_bags,gps_bags,pos_bags,rchd_bags) = parse_bagfile(fullname)
#                outstring = ''
#                outfilename = 'bagdata_'+name.split('.')[0] + ".csv"
#                fulloutfilename = os.path.join(root, outfilename)
#                outstring += fullname.split('b')[0]
#                with open(fulloutfilename, 'w') as outfile: #use 'w' to start a new file
#                    outfile.write('\n') #TODO put header here                     
#                for line in bagfile_results:
#                    outstring = ''
#                    for item in line:   
#                        outstring += str(item) + ','
#                    #print(outstring)  
#                    with open(fulloutfilename, 'a') as outfile:
#                        outfile.write(outstring + '\n') 
                        
                # Move the bagfile pointer to the start of valid collect                        
                i = 0  
                cont = True
                start_time = 0.0
                prev_hdg = []
                prev_gps = []
                prev_pos = []
                while cont:
                    bag_topic = rchd_bags[i][1] 
                    if '/mavros/mission/reached' ==  bag_topic:
                        #print("=============================")
                        if 2 == rchd_bags[i][2]:
                            start_time = rchd_bags[i][0]
                            cont = False
                            print(rchd_bags[i])
                    i += 1
                print("=============================",start_time) 
                
                
                # Begin parsing files and making usable csv file.
                # Walk the directory starting from the directory with the bag file in it.
                for root2, dirs2, files2 in os.walk(root):
                    files2 = sorted(files2) 
                    is_valid = False  
                    for name2 in files2:
                        outstring = '' 
                        if (name2.startswith('FLIR')):
                            fullname2=os.path.join(root2, name2)
                            date_strings = make_datetime(name2)
                            crnt_filetime = float(date_strings[0])
                            if (start_time > crnt_filetime):
                                # Delete the file, picture taken before start of mission
                                print("Deleting picture, taken before start of mission:",fullname2)
                                os.remove(fullname2)
                            else: # At this point filetime is after starttime. Begin processing
                                print('Processing file:',name2)
                                crnt_bagtime = start_time
#TODO XXXXXX get prev and next reading to determine current reading.
                                while crnt_filetime > crnt_bagtime: # Move bagtime forward to after startime
                                    if('/mavros/global_position/compass_hdg' == bagfile_results[i][1]):
                                        prev_hdg = bagfile_results[i]
                                    elif('/mavros/global_position/global' == bagfile_results[i][1]): 
                                        prev_gps = bagfile_results[i] 
                                    elif('/mavros/global_position/local' == bagfile_results[i][1]):  
                                        prev_pos = bagfile_results[i]     
                                    crnt_bagtime = bagfile_results[i][0]
                                    i += 1
                                print("PREV_TIMES:",crnt_filetime,prev_hdg[0],prev_gps[0],prev_pos[0])
                                
                exit()                                
                                    
'''                                    
                                    crnt_bagtime = bagfile_results[i][0]
                                    print("currents",crnt_filetime,bagfile_results[i])
                                    if('/mavros/global_position/compass_hdg' == bagfile_results[i][1]):
                                        nxt_hdg = bagfile_results[i]
                                        # ratio of time where file time is between prev and next bagtime
                                        print("hdg_times",crnt_filetime,prev_hdg[0],nxt_hdg[0])
                                        ratio = (crnt_filetime - prev_hdg[0])/(nxt_hdg[0] - prev_hdg[0])
                                        log_hdg = ((nxt_hdg[2] - prev_hdg[2])*ratio) + prev_hdg[2]
                                        print("heading:",ratio,prev_hdg[2],log_hdg,nxt_hdg[2])
                                    elif('/mavros/global_position/global' == bagfile_results[i][1]): 
                                        nxt_gps = bagfile_results[i] 
                                    elif('/mavros/global_position/local' == bagfile_results[i][1]):  
                                        nxt_pos = bagfile_results[i]
                                    
   '''                                 
                                                             



                
        


# ('/media/user1/BHG_USMA03/L70_Testcase19_GS/20200717_131432_222', ['20200717_131432_222_flir.csv', '20200717_131432_222_gobi.csv', 'bhg_20200717_131432_222.bag'])


