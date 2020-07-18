#!/usr/bin/python2
# Ref: https://stackoverflow.com/a/45769740
 
import matplotlib
matplotlib.use('Agg') # Bypass the need to install Tkinter GUI framework
 
import numpy as np
import matplotlib.pyplot as plt
 
# Use cross product to determine whether a point lies above or below a line.
#   Math: https://math.stackexchange.com/a/274728
#   English: "above" means that looking from point a towards point b, 
#               the point p lies to the left of the line.
is_above = lambda p,a,b: np.cross(p-a, b-a) < 0
 
# Data.
a = np.array([1.234,2.4353]) # [x,y]
b = np.array([3.564,5.546]) # [x,y]
 
p1 = np.array([2.5657,4.234]) # [x,y]
p2 = np.array([2.5673,3.679]) # [x,y]
 

l70_nw = np.array([32.848635, -114.273121])
l70_sw = np.array([32.848492, -114.273110])
l72_nw = np.array([32.847735, -114.273058])
l72_sw = np.array([32.847575, -114.273050])
l70_ne = np.array([32.848710, -114.253374])
l70_se = np.array([32.848573, -114.253368])
l72_ne = np.array([32.847798, -114.253402])
l72_se = np.array([32.847671, -114.253389])


p1 = np.array([32.84813 , -114.263411]) # North of L72
p2 = np.array([ 32.846569, -114.265073]) # South of L72
 
# Draw a b line.
(fig, ax) = plt.subplots()
data_points = np.array([a,b]) # Add points: (1,2) , (3,5)
data_points_x = data_points[:,0] # For every point, get 1st value, which is x.
data_points_y = data_points[:,1] # For every point, get 2nd value, which is y.
ax.plot(data_points_x, data_points_y, marker="o", color="k")
 
# Draw point: color point if it is above or below line.
# Point 1:
if is_above(p1,a,b):
    ax.scatter(p1[0], p1[1], color='green')
else:
    ax.scatter(p1[0], p1[1], color='red')
 
# Point 2:
if is_above(p2,a,b):
    ax.scatter(p2[0], p2[1], color='green')
else:
    ax.scatter(p2[0], p2[1], color='red')
 
# Save result to file.
plt.savefig('is-point-above-below-line.png')
