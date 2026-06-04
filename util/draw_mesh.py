#!/usr/bin/env python3
"""draw mesh"""
#this folder is for drawing how the mesh looks like
#the required files are the following: mesh.0, flac.py

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import flac
def main(axis):
    
    frame = int(1) #frame starts from 1
    
    if axis == "x":
        mesh,z = fl.read_mesh(frame)
        grid_cord[axis] = mesh[:,0]
        diff_mesh = np.diff(mesh[:,0])
        max_diff = np.max(diff_mesh)
        pos_mesh = mesh[:-1,0] #left node, drop last x element
        #draw mesh density
        plt.figure(figsize = (7,4))
        plt.plot(pos_mesh,diff_mesh)
        plt.xlabel("x distance(km)")
        plt.xlim(left = 0)
        plt.ylabel("grid_size(km)")
        plt.ylim(bottom = 0)
        plt.yticks(np.arange(0, max_diff, 0.5))
        
    if axis == "z":
        x,mesh = fl.read_mesh(frame)
        mesh = abs(mesh)
        grid_cord[axis] = mesh[0,:]
        diff_mesh = np.diff(mesh[0,:])
        max_diff = np.max(diff_mesh)
        pos_mesh = mesh[0,1:] #bottom node, drop top z element
        #draw mesh density
        plt.figure(figsize = (6,7))
        plt.plot(diff_mesh,pos_mesh)
        plt.xlabel("grid_size(km)")
        plt.xticks(np.arange(0,max_diff, 0.5))
        plt.ylabel("z depth(km)")
        plt.ylim(bottom = 0,top = 150)
        plt.gca().invert_yaxis()
        

    plt.title("grid size - distance")
    plt.savefig(f"grid_{axis}_width_per_distance.png",bbox_inches='tight')

    
    
if __name__ == '__main__':

    fl = flac.Flac()
    mesh_arr = ["x","z"]
    grid_cord = {}

    for i in range(0,2):
        axis = mesh_arr[i]
        main(axis)
        
    
    combine_grid = pd.concat([pd.Series(grid_cord["x"], name='x_cord'), pd.Series(grid_cord["z"], name='z_cord')], axis=1)
    combine_grid.to_csv('grid_cord.csv',index = False)