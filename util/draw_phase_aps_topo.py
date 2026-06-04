#!/usr/bin/env python3
"""draw results"""

import os
import sys
import flac
import numpy as np
# --- CLUSTER EXECUTION ---
import matplotlib
matplotlib.use('Agg') 
# -------------------------------------------
from PIL import Image 
from pathlib import Path
from matplotlib.cm import get_cmap
from matplotlib import pyplot as plt
plt.rcParams.update({"font.size": 24})

from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize, BoundaryNorm, ListedColormap

    
"""read data"""

def read_time():
    with open('_contents.0') as contents:
        time = contents.read() #time_step, loop, and time        
    return time
class Read_data:
    
    def read_grid_size(self,frame,sub_xz_id,grid_size):
        self.grid_size = grid_size
        self.sub_xz_left  = sub_xz_id[0]
        self.sub_xz_right = sub_xz_id[1]
        self.sub_xz_bottom = sub_xz_id[2]
        self.sub_xz_top = sub_xz_id[3]
    def slice_array(self,array):
        
        if self.grid_size == 0:
            
            sub_xz_left = max(0, self.sub_xz_left - 1)
            sub_xz_top = max(0, self.sub_xz_top - 1)
            sub_xz_right = self.sub_xz_right +2
            sub_xz_bottom = self.sub_xz_bottom +2
            array = array[sub_xz_left:sub_xz_right, sub_xz_top:sub_xz_bottom]
        return array
    def read_xz(self,frame):
        x,z = fl.read_mesh(frame)
        if self.grid_size != 0:
            x = self.slice_array(x)
            z = self.slice_array(z)
            x = np.pad(x, ((0, 0), (0, 1)), mode='edge')
            z = np.pad(z, ((0, 0), (0, 1)), mode='edge')
            
        return x,z
    def read_flac(self,frame):
        phase = fl.read_phase(frame)
        if self.grid_size != 0:
            phase = self.slice_array(phase)
        return phase

    def read_temperature(self,frame):
        temp = fl.read_temperature(frame)
        if self.grid_size != 0:
            temp = self.slice_array(temp)    
        return temp

    def read_aps(self,frame):
        aps = fl.read_aps(frame)
        if self.grid_size != 0:
            aps = self.slice_array(aps)    
        return aps

"""set parameter"""  
def set_time(time):  
    row_str = time.strip().split('\n')
    time_list = []
    for row in row_str:
        element = row.split()
        time_list.append(element)
    time = np.array(time_list)
    time = time.astype(float)
    
    return time
def set_grid(frame):
    
    #set the grid size of the specific area of interst 
    grid_size = int(2)
    x,z = fl.read_mesh(frame) #get the x and z coordinate
    
    if grid_size == 0:
       print("whole grid") 
       row_x,col_x = x.shape
       row_z,col_z = z.shape
       
       sub_xz_left_id = int(1)
       sub_xz_right_id = row_x - 1
       sub_xz_bottom_id = int(0)
       sub_xz_top_id = col_z -1
       sub_xz = [float(x[0,0]),float(x[-1,0]),float(z[0,-1]),float(z[0,0])]
       sub_xz_id = [int(sub_xz_left_id), int(sub_xz_right_id),int(sub_xz_bottom_id),int(sub_xz_top_id)]
       print(sub_xz_id)
    
    elif grid_size == 1:
        print("sub grid")
        sub_xz = [700,800,-30.0,0.0] #(left,right,bottom,top) km
       
        sub_xz_left_id = (np.abs((x[:,0]) - sub_xz[0])).argmin()   # left boundary for sub xz
        sub_xz_right_id = (np.abs((x[:,0]) - sub_xz[1])).argmin()  # right boundary for sub xz
        sub_xz_bottom_id = (np.abs(z[0,:] - sub_xz[2])).argmin() #bottom boundary for sub xz
        sub_xz_top_id =(np.abs(z[0,:]-sub_xz[3])).argmin() #top boundary for sub xz
        sub_xz_id = [int(sub_xz_left_id), int(sub_xz_right_id),int(sub_xz_bottom_id),int(sub_xz_top_id)]
    
    elif grid_size == 2:

        print("topo grid")

        middle = 0.5 * x[-1, 0] 
        half_width = 112.5 
        fix_depth = -30    
        surface = 0        
        limit = 75
        left_bound = 150
        right_bound = 75

        sub_xz = [middle - half_width, middle + half_width, fix_depth, surface]

        z_max_id = np.argmax(z[:, 0])
        z_max_pos_x = x[z_max_id, 0]
        
        z_max_to_left_bound = z_max_pos_x - x[0, 0]
        z_max_to_right_bound = x[-1, 0] - z_max_pos_x

        if z_max_pos_x + right_bound > x[-1, 0]: #highest topo close to right boundary
            sub_xz = [x[-1,0] - (left_bound +right_bound), x[-1,0], fix_depth, surface]
            
        if left_bound > z_max_pos_x: 
            sub_xz = [x[0,0] , left_bound + right_bound - z_max_pos_x, fix_depth, surface]
            
        if z_max_to_left_bound > left_bound and z_max_to_right_bound > right_bound: 
            
            sub_xz = [z_max_pos_x - left_bound, z_max_pos_x + right_bound, fix_depth, surface]

        sub_xz_left_id = (np.abs((x[:,0]) - sub_xz[0])).argmin()   
        sub_xz_right_id = (np.abs((x[:,0]) - sub_xz[1])).argmin()  
        sub_xz_bottom_id = (np.abs(z[0,:] - sub_xz[2])).argmin()   
        sub_xz_top_id = (np.abs(z[0,:]-sub_xz[3])).argmin()        

        sub_xz_id = [int(sub_xz_left_id), int(sub_xz_right_id),int(sub_xz_bottom_id),int(sub_xz_top_id)]
        
    return x,z,sub_xz,sub_xz_id,grid_size

def set_canvas():
    shrink_col = int(30) #whole grid = 30
    shrink_row = int(7) #whole grid = 10
    canvas_col = int(1)
    canvas_row = int(3)
    total_position = canvas_row * canvas_col
    canvas_row_init = int(0)
    canvas_col_init = int(0)
    canvas_grid_position = []
    
    for j in range(canvas_row_init,canvas_row):
        for i in range(canvas_col_init,canvas_col):
            grid_position = (j,i)
            canvas_grid_position.append(grid_position)
    GRID_DIMS = (canvas_row,canvas_col) 
    fig_large = plt.figure(figsize=(canvas_col * shrink_col , canvas_row * shrink_row ))  #figure_large is the large canvas that figure is putting on
    gs = GridSpec(*GRID_DIMS, figure = fig_large)

    shrink_size = float(0.3)
    aspect_size = float(4.5)
    return gs, canvas_grid_position, total_position,fig_large, shrink_size, aspect_size

def set_color():
    phase = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]) 
    all_phase_color = [
        "lightblue",        #phase1: basalt(anhydrate)
        "darkgreen",        #phase2: continental  crust
        "blue",             #phase3: basalt(ocean crust)
        "white",            #phase4: olvine(mantle)
        "limegreen",        #phase5: schist, transformed from #17    
        "olivedrab",        #phase6: continental crust, same as #2
        "cyan",             #phase7: basalt (oceanic crust), same as #3
        "gray",             #phase8: olivine (mantle), same as #4.
        "darkred",          #phase9: serpentinite (weak mantle), transformed from mantle (#4, #8) if residing above subducted oceanic crust and sediment (#3, #7, #10). Will transform to hydrated mantle (#16) when T-P conditions are high enough.c
        "teal",             #phase10: sedimentary rock, compacted from (#11)
        "green",            #phase11: weak continental crust, transformed from continental crust (#2, #6) if residing above oceanic crust, sediment, or arc (#3, #7, #10, #14).
        "aqua",             #phase12: eclogite, transformed from basal (#1, #3, #7) when T-P conditions are high enough.
        "pink",             #phase13: arc crust, generated by arc volcanism
        "black",            #phase14: weak middle crust, transformed from continental crust (#3, #7) if stressed and heated. Disabled.
        "lightgray",        #phase15: hydrated mantle, will transform (partially melt) to mantle (#4) if warmer than olivine wet solidus and generate arc (#14) at surface.
        "darkslategrey",    #phase16: metamormpic sedimentary rock, transformed from (#10)
        "darkgray",         #phase17: dry mantle, stronger than (#4)
        "black",            #phase18: custom
        "black",            #phase19: custom
        ]
    
    phase_color = all_phase_color[:17] #select phase color with in all_phase_color
        
    return phase_color
def set_phase_names():
    phase = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]) 
    all_phase_names = [
        "anhydrate",
        "C.C.",
        "O.C.",
        "mantle",
        "schist",
        "C.C.",
        "O.C.",
        "mantle",
        "serpentinite ",
        "sed rock",
        "weak C.C.",
        "eclogite",
        "arc crust",
        "weak middle crust",
        "hydrated mantle",
        "meta sed rock",
        "dry mantle",
        "custom",
        "custom"
    ]
    phase_names = all_phase_names[:17]

    return phase_names

""" plot diagram """
class Plot:
    def __init__(self,phase,temp,canvas_grid_position,canvas_position_counter,fig_large,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps):
    
        self.phase = phase
        self.temp =temp
        self.aps =aps
        self.canvas_grid_position = canvas_grid_position
        self.canvas_position_counter =canvas_position_counter
        self.fig_large = fig_large
        self.shrink_size = shrink_size
        self.aspect_size = aspect_size
        self.sub_xz = sub_xz
        self.grid_size = grid_size
        self.gs = gs
        self.x = x
        self.z = z
        self.sub_xz_left  = sub_xz[0]
        self.sub_xz_right = sub_xz[1]
        self.sub_xz_bottom = sub_xz[2]
        self.sub_xz_top = sub_xz[3]
        self.height = float(10)
        self.shading = str('flat')

    
    def plot_phase(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        ax = self.fig_large.add_subplot(self.gs[row,col])
        
        self.phase_color = set_color() #custom the phase color
        self.phase_names = set_phase_names() #custom the phase names
        self.phase_cmap = ListedColormap(self.phase_color)
        bounds = np.arange(0.5, 17.5 + 1, 1)   
        norm = BoundaryNorm(bounds, self.phase_cmap.N)
        rows, cols = self.phase.shape
        plot_x = self.x[:rows+1, :cols+1]
        plot_z = self.z[:rows+1, :cols+1]
        phase_mesh = ax.pcolormesh(plot_x, plot_z, self.phase,cmap=self.phase_cmap,norm = norm, shading = self.shading) #plot phase
        phase_mesh = add_temp(phase_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        x_range = self.sub_xz_right - self.sub_xz_left
        y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
        ax.set_aspect('auto')
        ax.set_box_aspect(y_range / x_range)
        # colorbar = self.fig_large.colorbar(phase_mesh,ax = ax,label='phase',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        # cbar_ax = colorbar.ax
        # cbar_ax.set_xlabel('phase')
        # colorbar.set_ticks(np.arange(1,18))
        # colorbar.set_ticklabels(self.phase_names)
        # colorbar.ax.tick_params(axis='x',rotation=85)
    
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return  self.canvas_position_counter

    def plot_aps(self): 
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_aps = 2.0
        min_aps = 0.0
    
        ax = self.fig_large.add_subplot(self.gs[row,col])
        rows, cols = self.aps.shape
        plot_x = self.x[:rows+1, :cols+1]
        plot_z = self.z[:rows+1, :cols+1]
        aps_mesh = ax.pcolormesh(plot_x, plot_z,self.aps,cmap = 'Blues',vmax = max_aps, vmin = min_aps, shading= self.shading)
        aps_mesh = add_temp(aps_mesh,self.temp,self.x,self.z,self.fig_large,ax, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        x_range = self.sub_xz_right - self.sub_xz_left
        y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
        ax.set_aspect('auto')
        ax.set_box_aspect(y_range / x_range)
        
        # colorbar = self.fig_large.colorbar(aps_mesh,ax = ax,label='plastic strain',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        # cbar_ax = colorbar.ax
        # cbar_ax.set_xlabel('plastic strain')
        # colorbar.ax.tick_params(axis='x')
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
        return self.canvas_position_counter
    def plot_topo(self):

            row,col = self.canvas_grid_position[self.canvas_position_counter]
            
            meter = float(1000)
            max_allowed_topo = 5 #km
            min_allowed_topo = -5 #km

            ax = self.fig_large.add_subplot(self.gs[row,col])
            
            ax.plot(self.x[:,0], self.z[:,0] * meter)

            ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
            # ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
            ax.set_ylim(min_allowed_topo * meter , max_allowed_topo * meter )
            x_range = self.sub_xz_right - self.sub_xz_left
            y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
            ax.set_aspect('auto')
            ax.set_box_aspect(y_range / x_range)
            
            self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
            return self.canvas_position_counter
"add"

def add_temp(mesh,temp,x,z,fig_large,ax,aspect_size, shrink_size):
    
    temp_level = np.arange(0, 1400, 200)
    temp_cmap = plt.get_cmap('gist_gray')
    temp_contourf = ax.contour(x[:, :-1],z[:, :-1],temp,levels = temp_level,cmap = temp_cmap)
    # cax = fig_large.add_axes([0.95, 0.75, 0.02, 0.15])
    # cbar = fig_large.colorbar(temp_contourf, ax=ax, shrink = shrink_size, aspect = aspect_size, cax=cax)
    # cbar.set_label("temperature (C)", rotation=90, labelpad=10)
    # ax.clabel(temp_contourf, fmt='')

    return mesh
  
"""check values"""    

def position_counter(canvas_position_counter,canvas_grid_position):
             
    canvas_position_counter = canvas_position_counter + 1
    
    return canvas_position_counter

def count_frame():
    
    max_frame = int(1000)
    init_frame = int(1)
    total_frame = int(0)
    for frame in range(init_frame, max_frame):
        if frame > max_frame:
            print(f"reach maximum frame allowed,maximum of {max_frame}")
            break
        try:
            fl.read_mesh(frame) 
            pass
        except Exception as e:
            print(f"total frame of {frame-1}")
            total_frame = frame #the ammount of total frame equals frame - 1
            break   
    return init_frame, total_frame

"""main"""    
def main(): 
    
    data = Read_data()
    init_frame, total_frame = count_frame()
    gs,canvas_grid_position,total_position,fig_large, shrink_size, aspect_size = set_canvas()
    time = read_time()
    time = set_time(time)
    
    for frame in range(init_frame,total_frame):
        
        canvas_position_counter = 0
        t = time[frame-1,2] #get the corresponding time of the time_step
        
        #set parameter
        x,z,sub_xz,sub_xz_id,grid_size = set_grid(frame)
        
        #read data

        data.read_grid_size(frame,sub_xz_id,grid_size)
        x,z = data.read_xz(frame)
        phase = data.read_flac(frame)
        temp = data.read_temperature(frame)
        aps = data.read_aps(frame)
        
        figure = Plot(phase,temp,canvas_grid_position,canvas_position_counter,fig_large,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps)
        
        #plot diagram
        
        canvas_position_counter = figure.plot_phase()
        canvas_position_counter = figure.plot_aps()
        canvas_position_counter = figure.plot_topo()
        
        

        font_size = 32
        plt.tight_layout(rect = [0,0,1,0.95], h_pad=3.0)
        # #parameter
        fig_large.text(0.07, 0.70, f"Phase",fontsize =font_size+3, ha='left', va='top')
        fig_large.text(0.07, 0.39, f"plastic strain",fontsize =font_size+3, ha='left', va='top')
        fig_large.text(0.07, 0.08, f"relief",fontsize =font_size+3, ha='left', va='top')
        # #time
        fig_large.text(0.85, 0.70, f"Time ={t:.3f}Myr",fontsize =font_size, ha='left', va='top')
        fig_large.text(0.85, 0.39, f"Time ={t:.3f}Myr",fontsize =font_size, ha='left', va='top')
        fig_large.text(0.85, 0.08, f"Time ={t:.3f}Myr",fontsize =font_size, ha='left', va='top')
        plt.savefig(f"phase_aps_topo_frame_{frame}",pad_inches=0.1)
        fig_large.clf() #clear legend to avoid stacking
        
        print(f"saved frame_{frame}_phase_aps_topo")
    print(f"finish saving frame, total of {total_frame} frame")
    
if __name__ == '__main__':
    
    fl = flac.Flac()
    main()
