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
            gps_list.append([(t.to_nsec()/1000000000.0)-14400,topic,msg.latitude,msg.longitude,msg.altitude])
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
#dirs2search = "/media/user1/BHG_USMA03/L70_Testcase17/20200713_143510_974"
for root, dirs, files in os.walk(dirs2search, topdown = True):
    if(len(root.split('/')) == 6): # begin at this depth of the directory tree
        dirs[:] = [] # stop from walking any deeper
        for name in files:
            fullname = os.path.join(root, name)
            if (name.endswith('.bag') and ('L7' in fullname)):
            
                # Parse bag file before generating csv file.
                print('***********   ' + fullname)
                (hdg_bags,gps_bags,pos_bags,rchd_bags) = parse_bagfile(fullname)
                        
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
                
                    print(root2)
                    outfilename = 'wrongdata'
                    if ('FLIR' in root2):
                        outfilename = name.split('.')[0][4:] + "_flir.csv"
                    elif ('GOBI' in root2):
                        outfilename = name.split('.')[0][4:] + "_gobi.csv"
                    fulloutfilename = os.path.join(root, outfilename)
                    print("===== Outiflename: =====:",fulloutfilename)
                    outstring = fullname.split('b')[0] + ','
                    with open(fulloutfilename, 'w') as outfile: #use 'w' to start a new file
                        outfile.write('filename,latitude,longitude,gps_altitude,roll,pitch,yaw,rel_altitude,heading\n') #TODO put header here                
                
                    files2 = sorted(files2) 
                    is_valid = False  
                    gps_i = 0
                    pos_i = 0
                    hdg_i = 0
                    next_gpstime = 0
                    next_postime = 0
                    next_hdgtime = 0
                    doexit = False
                    for name2 in files2: 
                        if (name2.startswith('FLIR') or name2.startswith('GOBI')):
                            fullname2=os.path.join(root2, name2)
                            date_strings = make_datetime(name2)
                            crnt_filetime = float(date_strings[0])
                            if (start_time > crnt_filetime):
                                # Delete the file, picture taken before start of mission
                                print("Deleting picture, taken before start of mission:",fullname2)
                                os.remove(fullname2)
                            else: # At this point filetime is after starttime. Begin processing
                                #print('Processing file:',name2)
                                outstring = fullname2 + ','

                                while crnt_filetime > next_gpstime:
                                    gps_i += 1
                                    if gps_i <= len(gps_bags)-1:
                                        next_gpstime = gps_bags[gps_i][0]
                                    else:
                                        gps_i -= 1
                                        break
                                   
                                prev_gpstime = gps_bags[gps_i - 1][0]
                                ratio = (crnt_filetime - prev_gpstime)/(next_gpstime - prev_gpstime)
                                crnt_lat =  ((gps_bags[gps_i][2] - gps_bags[gps_i - 1][2])*ratio) + gps_bags[gps_i - 1][2]
                                crnt_lon =  ((gps_bags[gps_i][3] - gps_bags[gps_i - 1][3])*ratio) + gps_bags[gps_i - 1][3]
                                crnt_galt =  ((gps_bags[gps_i][4] - gps_bags[gps_i - 1][4])*ratio) + gps_bags[gps_i - 1][4]
                                outstring += str(crnt_lat) + ',' + str(crnt_lon) + ',' + str(crnt_galt) + ','
                                
                                while crnt_filetime > next_postime:
                                    pos_i += 1                                    
                                    if pos_i <= len(pos_bags)-1:
                                        next_postime = pos_bags[pos_i][0]
                                    else:
                                        pos_i -= 1
                                        break
                                    
                                prev_postime = pos_bags[pos_i - 1][0]
                                ratio = (crnt_filetime - prev_postime)/(next_postime - prev_postime)
                                crnt_roll =  ((pos_bags[pos_i][2] - pos_bags[pos_i - 1][2])*ratio) + pos_bags[pos_i - 1][2]
                                crnt_pitch =  ((pos_bags[pos_i][3] - pos_bags[pos_i - 1][3])*ratio) + pos_bags[pos_i - 1][3]
                                crnt_yaw =  ((pos_bags[pos_i][4] - pos_bags[pos_i - 1][4])*ratio) + pos_bags[pos_i - 1][4]
                                crnt_ralt =  ((pos_bags[pos_i][5] - pos_bags[pos_i - 1][5])*ratio) + pos_bags[pos_i - 1][5]
                                outstring += str(crnt_roll) + ',' + str(crnt_pitch) + ',' + str(crnt_yaw) + ',' + str(crnt_ralt) + ','
                                
                                while crnt_filetime > next_hdgtime:
                                    hdg_i += 1
                                    
                                    if hdg_i <= len(hdg_bags)-1:
                                        next_hdgtime = hdg_bags[hdg_i][0]
                                    else:
                                        hdg_i -= 1
                                        break                                    
                                    
                                prev_hdgtime = hdg_bags[hdg_i - 1][0]
                                #print(prev_hdgtime,next_hdgtime)
                                ratio = (crnt_filetime - prev_hdgtime)/(next_hdgtime - prev_hdgtime)
                                crnt_hdg =  ((hdg_bags[hdg_i][2] - hdg_bags[hdg_i - 1][2])*ratio) + hdg_bags[hdg_i - 1][2]
                                
                                outstring += str(crnt_hdg)
                                #print(outstring)
                                
                                with open(fulloutfilename, 'a') as outfile:
                                    outfile.write(outstring + '\n') 
                                
                                
                                
                                
#                    if (doexit ):
#                        exit()
                                
                                                             



                
        


# ('/media/user1/BHG_USMA03/L70_Testcase19_GS/20200717_131432_222', ['20200717_131432_222_flir.csv', '20200717_131432_222_gobi.csv', 'bhg_20200717_131432_222.bag'])


