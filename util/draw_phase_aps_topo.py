#!/usr/bin/env python3
"""draw results"""
#fix plot_topo gravity optinal issue!
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
plt.rcParams.update({"font.size": 8})
import matplotlib.ticker as ticker

from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize, BoundaryNorm, ListedColormap
from scipy.signal import find_peaks
    
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
    def read_grav(self,frame):

        g = None
        file_name = f'gravity_frame_{frame}.csv'        

        if os.path.exists(file_name):
            g = np.loadtxt(f'gravity_frame_{frame}.csv', delimiter=',')
        
        return g
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
        print("sub grid topo grid")
        sub_xz = [600,800,-30.0,0.0] #(left,right,bottom,top) km

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

        z_max_id = np.argmax(z[:, 0])
        
        def specific_region(x, z, z_max_id):

            region_start=700
            region_end=800

            specific_region_mask = (x[:, 0] > region_start) & (x[:, 0] < region_end)    
            specific_region_id_list = np.where(specific_region_mask)[0]      
            specific_region_z = z[specific_region_id_list, 0]    
            local_z_max_id = int(np.argmax(specific_region_z))       
            z_max_id = specific_region_id_list[local_z_max_id]

            return z_max_id
                          
        z_max_id = specific_region(x, z, z_max_id) #use when topo max at werid position
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
    shrink_col = int(12) #whole grid = 30
    shrink_row = int(2.6) #whole grid = 10
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
    def __init__(self,phase,temp,canvas_grid_position,canvas_position_counter,fig_large,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps,g, font_size,t ):
    
        self.phase = phase
        self.temp =temp
        self.aps =aps
        self.g = g
        self.t = t
        self.canvas_grid_position = canvas_grid_position
        self.canvas_position_counter =canvas_position_counter
        self.font_size = font_size
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
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))

        def subduct_depth(self):

            oceanic_crust_depth = float(-7.5)
            oceanic_crust_depth_id = (np.abs(self.z[0, :] - oceanic_crust_depth)).argmin()
            mantle_phase = int(4)

            self.slab_depth =  oceanic_crust_depth
            total_depth_steps = self.phase.shape[1]

            for i in range(total_depth_steps - 1, oceanic_crust_depth_id - 1, -1):

                phase_slice = self.phase[:, i]
                diff_phase = np.where(phase_slice != mantle_phase)[0]

                if diff_phase.size > 0 :
                    self.slab_depth = self.z[0, i]
                    break              
            
        subduct_depth(self)
    
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
        ax.set_xlabel('distance(km)')
        ax.set_ylabel('km')
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        ax.text(self.sub_xz_left + 2, self.sub_xz_top + 5, f"Phase", color='black', fontsize=self.font_size, fontweight='bold')
        ax.text(self.sub_xz_left + 2, self.sub_xz_bottom + 3, f"Time = {self.t:.3f}Ma", color='black', fontsize=self.font_size)
        ax.text(self.sub_xz_right-48, self.sub_xz_top + 5, f"slab depth = {self.slab_depth:.3f}km", color='black', fontsize=self.font_size)
        x_range = self.sub_xz_right - self.sub_xz_left
        y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
        ax.set_aspect('auto')
        ax.set_box_aspect(y_range / x_range)
        tick_step = 10
        first_tick = np.ceil(self.sub_xz_left / tick_step) * tick_step
        x_ticks = np.arange(first_tick, self.sub_xz_right, tick_step)
        ax.set_xticks(x_ticks)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        ax.tick_params(axis='x', labelbottom=True)
        ax.set_xlabel('distance(km)')
    
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return  self.canvas_position_counter, self.slab_depth

    def plot_aps(self): 
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        
        ax = self.fig_large.add_subplot(self.gs[row,col])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
        
        max_aps = 2.0
        min_aps = 0.0

        def fault(self):
            
            peak_aps = {} #fault position
            peak_aps_id, _  = find_peaks(self.aps[:,0], height = 0.1)

            peak_aps['pos_x'] = self.x[peak_aps_id, 0]
            peak_aps['pos_z'] = self.z[peak_aps_id, 0]

            return peak_aps
            
        peak_aps = fault(self)
        rows, cols = self.aps.shape
        plot_x = self.x[:rows+1, :cols+1]
        plot_z = self.z[:rows+1, :cols+1]
        aps_mesh = ax.pcolormesh(plot_x, plot_z,self.aps,cmap = 'Blues',vmax = max_aps, vmin = min_aps, shading= self.shading)
        ax.scatter(peak_aps['pos_x'],peak_aps['pos_z'],color='blue',marker='^', s=8,label='fault')
        aps_mesh = add_temp(aps_mesh,self.temp,self.x,self.z,self.fig_large,ax, self.aspect_size, self.shrink_size) #add temp to figure
        ax.legend(loc='upper right', fontsize=self.font_size)
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        ax.set_xlabel('distance(km)')
        ax.set_ylabel('km')
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        ax.text(self.sub_xz_left + 2, self.sub_xz_top + 5, f"Plastic Strain", color='black', fontsize=self.font_size, fontweight='bold')
        ax.text(self.sub_xz_left + 2, self.sub_xz_bottom + 3, f"Time = {self.t:.3f}Ma", color='black', fontsize=self.font_size)

        x_range = self.sub_xz_right - self.sub_xz_left
        y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
        ax.set_aspect('auto')
        ax.set_box_aspect(y_range / x_range)
        tick_step = 10
        first_tick = np.ceil(self.sub_xz_left / tick_step) * tick_step
        x_ticks = np.arange(first_tick, self.sub_xz_right, tick_step)
        ax.set_xticks(x_ticks)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        ax.tick_params(axis='x', labelbottom=True)
        ax.set_xlabel('distance(km)')
        
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
        return self.canvas_position_counter
        
    def plot_topo(self):

            row,col = self.canvas_grid_position[self.canvas_position_counter]
            
            
            ax = self.fig_large.add_subplot(self.gs[row,col])
            
            
            def add_grav(self, ax):
                
                mutiply = float(10**5)
                kilo = float(10**3)
                min_g = -80
                max_g = 0
                if self.g is None:
                    return
                
                self.g[:,0] = self.g[:,0] / kilo
                self.g[:,2] = mutiply * self.g[:,2]
    
            meter = float(1000)
            max_allowed_topo = 7 #km
            min_allowed_topo = -7 #km
            max_allowed_grav = 300
            min_allowed_grav = -400

            add_grav(self,ax)
            ax.plot(self.x[:,0], self.z[:,0] * meter,label='relief')

            ax2 = ax.twinx()
            ax2.plot(self.g[:,0], self.g[:,2], color='tab:orange',label='gravity')
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax2.set_xlim(self.sub_xz_left, self.sub_xz_right)
            ax2.set_ylim(min_allowed_grav, max_allowed_grav)
            ax2.set_ylabel('mGal')

            ax.set_xlabel('distance(km)')
            ax.set_ylabel('m')
            ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
            ax.set_ylim(min_allowed_topo * meter , max_allowed_topo * meter )
            ax.yaxis.set_major_locator(ticker.MultipleLocator(2000))

            handles1, labels1 = ax.get_legend_handles_labels()
            ax.legend(handles1 + handles2, labels1 + labels2, loc='upper right', fontsize = self.font_size)
            
            ax.text(self.sub_xz_left + 2, meter * (max_allowed_topo - 2), f"Relief", color='black', fontsize=self.font_size, fontweight='bold')
            ax.text(self.sub_xz_left + 2, meter * (min_allowed_topo + 1.5), f"Time = {self.t:.3f}Ma", color='black', fontsize=self.font_size)
            x_range = self.sub_xz_right - self.sub_xz_left
            y_range = (self.sub_xz_top + self.height) - self.sub_xz_bottom
            ax.set_aspect('auto')
            ax.set_box_aspect(y_range / x_range)
            tick_step = 10
            first_tick = np.ceil(self.sub_xz_left / tick_step) * tick_step
            x_ticks = np.arange(first_tick, self.sub_xz_right, tick_step)
            ax.set_xticks(x_ticks)
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
            ax.tick_params(axis='x', labelbottom=True)
            ax.set_xlabel('distance(km)')
            
            self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
            return self.canvas_position_counter
"add"

def add_temp(mesh,temp,x,z,fig_large,ax,aspect_size, shrink_size):
    
    temp_level = np.arange(0, 1400, 200)
    temp_cmap = plt.get_cmap('gist_gray')
    temp_contourf = ax.contour(x[:, :-1],z[:, :-1],temp,levels = temp_level, linewidths = 1,cmap = temp_cmap)

    return mesh
 
"""check values"""    

def position_counter(canvas_position_counter,canvas_grid_position):
             
    canvas_position_counter = canvas_position_counter + 1
    
    return canvas_position_counter

def count_frame():
    
    max_frame = int(2000)
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
        fig_large.clf()
        canvas_position_counter = 0
        t = time[frame-1,2] #get the corresponding time of the time_step
        
        #set parameter
        font_size = 6
        x,z,sub_xz,sub_xz_id,grid_size = set_grid(frame)
        
        #read data

        data.read_grid_size(frame,sub_xz_id,grid_size)
        x,z = data.read_xz(frame)
        phase = data.read_flac(frame)
        temp = data.read_temperature(frame)
        aps = data.read_aps(frame)
        g = data.read_grav(frame) #optinal

        figure = Plot(phase,temp,canvas_grid_position,canvas_position_counter,fig_large,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps,g, font_size,t)
                
        #plot diagram
        
        canvas_position_counter,slab_depth  = figure.plot_phase()
        canvas_position_counter = figure.plot_aps()
        canvas_position_counter = figure.plot_topo()

        if 20 < abs(slab_depth) < 22:   
             
            plt.tight_layout(rect = [0,0,1,0.95], h_pad=3.0)
            plt.savefig(f"phase_aps_topo_frame_{frame}.png",pad_inches=0.1 ,bbox_inches='tight',dpi = 1200)
           
            fig_large.clf() #clear legend to avoid stacking
            
            
            print(f"saved frame_{frame}_phase_aps_topo")
            break
            
    print(f"finish saving frame, total of {total_frame} frame")
    
if __name__ == '__main__':
    
    fl = flac.Flac()
    main()