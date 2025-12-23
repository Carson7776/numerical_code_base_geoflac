"force on the boundary - timerelationship"
import numpy as np
import matplotlib.pyplot as plt


"opening files"
with open("forc.0","r") as file:
    
    content = file.read()
    lines = content.strip().split("\n")
    strip_line = [line.split() for line in lines]
    forc = [[float(value) for value in line]for line in strip_line]
    
"writing files into arrays"
forc_np = np.array(forc)

"extract for foc_np array"
time = forc_np[:,1]

force_l = forc_np[:,2]  
force_r = forc_np[:,3] 

vl = forc_np[:,5]
vr = forc_np[:,6]

"plot"

"force_left boundary"
plt.figure()
plt.plot(time, force_l)
plt.xlabel("time")
plt.ylabel("force - left boundary")
plt.savefig("force_left_boundary")

"force_right boundary"
plt.figure()
plt.plot(time, force_r)
plt.xlabel("time")
plt.ylabel("force - right boundary")
plt.savefig("force_right_boundary")

"velocity_left boundary"
plt.figure()
plt.plot(time, vl)
plt.xlabel("time")
plt.ylabel("velocity - right boundary")
plt.savefig("velocity_left_boundary")

"velocity_right boundary"
plt.figure()
plt.plot(time, vr)
plt.xlabel("time")
plt.ylabel("velocity - right boundary")
plt.savefig("velocity_right_boundary") 
