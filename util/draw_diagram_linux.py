#!/usr/bin/env python3
"""draw results"""
#the following files(draw_diagram,flac) must exist in the same level as the reading files


"""problem with fmelt, grid issue"""
"""problem with figure size of full size grid, array size miss by 1"""


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
        if self.grid_size == 0:
            x = self.slice_array(x)
            z = self.slice_array(z)
            x = np.pad(x, ((0, 0), (0, 1)), mode='edge')
            z = np.pad(z, ((0, 0), (0, 1)), mode='edge')
            
        return x,z
    def read_flac(self,frame):
        phase = fl.read_phase(frame)
        if self.grid_size == 0:
            phase = self.slice_array(phase)
        return phase

    def read_temperature(self,frame):
        temp = fl.read_temperature(frame)
        if self.grid_size == 0:
            temp = self.slice_array(temp)    
        return temp
    def read_srII(self,frame): #strain rate
        srII = fl.read_srII(frame)
        if self.grid_size == 0:
            srII = self.slice_array(srII)
        return srII
    def read_aps(self,frame):
        aps = fl.read_aps(frame)
        if self.grid_size == 0:
            aps = self.slice_array(aps)    
        return aps
    def read_visc(self,frame):
        visc = fl.read_visc(frame)
        if self.grid_size == 0:
           visc = self.slice_array(visc) 
        return visc
    def read_sxx(self,frame):
        sxx = fl.read_sxx(frame)
        if self.grid_size == 0:
           sxx = self.slice_array(sxx) 
        return sxx
    def read_sII(self,frame):
        sII = fl.read_sII(frame)
        if self.grid_size == 0:
           sII = self.slice_array(sII)
        return sII
    def read_vel(self,frame):
        vx, vz = fl.read_vel(frame)
        if self.grid_size == 0:
           vx = self.slice_array(vx)
           vz = self.slice_array(vz)
        return vx, vz
    def read_syy(self,frame):
        syy = fl.read_syy(frame)
        if self.grid_size == 0:
           syy = self.slice_array(syy)
        return syy
    def read_sxz(self,frame):
        sxz = fl.read_sxz(frame)
        if self.grid_size == 0:
           sxz = self.slice_array(sxz)
        return sxz
    def read_szz(self,frame):
        szz = fl.read_szz(frame)
        if self.grid_size == 0:
           szz = self.slice_array(szz)
        return szz
    def read_eII(self,frame):
        eII = fl.read_eII(frame)
        if self.grid_size == 0:
           eII = self.slice_array(eII)
        return eII
    def read_strain(self,frame):
        exx, ezz, exz = fl.read_strain(frame)
        if self.grid_size == 0:
           exx = self.slice_array(exx)
           ezz = self.slice_array(ezz)
           exz = self.slice_array(exz)
        return exx, ezz, exz
    def read_density(self,frame):
        density = fl.read_density(frame)
        if self.grid_size == 0:
           density = self.slice_array(density)
        return density
    def read_pres(self,frame):
        pres = fl.read_pres(frame)
        if self.grid_size == 0:
           pres = self.slice_array(pres)
        return pres
    def read_fmelt(self,frame):
        fmelt = fl.read_fmelt(frame)
        if self.grid_size == 0:
           fmelt = self.slice_array(fmelt)
        return fmelt

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
    grid_size = int(0)
    x,z = fl.read_mesh(frame) #get the x and z coordinate
    
    if grid_size != 0:
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
    else:
        print("sub grid")
        sub_xz = [250,1250,-100.0,10.0] #(left,right,bottom,top) km
       
        sub_xz_left_id = (np.abs((x[:,0]) - sub_xz[0])).argmin()   # left boundary for sub xz
        sub_xz_right_id = (np.abs((x[:,0]) - sub_xz[1])).argmin()  # right boundary for sub xz
        sub_xz_bottom_id = (np.abs(z[0,:] - sub_xz[2])).argmin() #bottom boundary for sub xz
        sub_xz_top_id =(np.abs(z[0,:]-sub_xz[3])).argmin() #top boundary for sub xz
        sub_xz_id = [int(sub_xz_left_id), int(sub_xz_right_id),int(sub_xz_bottom_id),int(sub_xz_top_id)]
    return x,z,sub_xz,sub_xz_id,grid_size

def set_canvas():
    shrink_col = int(32) #whole grid = 30
    shrink_row = int(8) #whole grid = 10
    canvas_row = int(2)
    canvas_col = int(8)
    total_position = canvas_row * canvas_col
    canvas_row_init = int(0)
    canvas_col_init = int(0)
    canvas_grid_position = []
    
    
    for j in range( canvas_col_init,canvas_col):
        for i in range(canvas_row_init,canvas_row):
            grid_position = (i,j)
            canvas_grid_position.append(grid_position)       
    GRID_DIMS = (canvas_row,canvas_col) #draw to graph only right know, 
    fig_large = plt.figure(figsize=(canvas_col * shrink_col , canvas_row * shrink_row ))  #figure_large is the large canvas that figure is putting on
    gs = GridSpec(*GRID_DIMS, figure = fig_large)
    font_size = int(20) #change fontsize, whole grid = 40
    label_size =int(20) #change labelsize, whole_grid = 20
    shrink_size = int(1)
    aspect_size = int(15)
    return gs, canvas_grid_position, total_position,fig_large, font_size, label_size, shrink_size, aspect_size

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
        "green",           #phase11: weak continental crust, transformed from continental crust (#2, #6) if residing above oceanic crust, sediment, or arc (#3, #7, #10, #14).
        "aqua",             #phase12: eclogite, transformed from basal (#1, #3, #7) when T-P conditions are high enough.
        "pink",             #phase13: arc crust, generated by arc volcanism
        "black",            #phase14: weak middle crust, transformed from continental crust (#3, #7) if stressed and heated. Disabled.
        "lightgray",        #phase15: hydrated mantle, will transform (partially melt) to mantle (#4) if warmer than olivine wet solidus and generate arc (#14) at surface.
        "darkslategrey",    #phase16: metamormpic sedimentary rock, transformed from (#10)
        "darkgray",         #phase17: dry mantle, stronger than (#4)
        "black",            #phase18: custom
        "black",            #phase19: custom
        ]
    phase_color = all_phase_color[:] #select phase color with in all_phase_color
        
    return phase_color

""" plot diagram """
class Plot:
    def __init__(self,phase,temp,srII,vx,vz,syy,sxz,szz,eII,exx,ezz,exz,density,pres,fmelt,canvas_grid_position,canvas_position_counter,fig_large,font_size,label_size,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps,visc,sxx,sII):
    
        self.phase = phase
        self.temp =temp
        self.srII =srII
        self.vx =vx
        self.vz =vz
        self.syy =syy
        self.sxz =sxz
        self.szz =szz
        self.eII =eII
        self.exx =exx
        self.ezz =ezz
        self.density =density
        self.pres = pres
        self.fmelt = fmelt
        self.canvas_grid_position = canvas_grid_position
        self.canvas_position_counter =canvas_position_counter
        self.fig_large = fig_large
        self.font_size =font_size
        self.label_size = label_size
        self.shrink_size = shrink_size
        self.aspect_size = aspect_size
        self.sub_xz = sub_xz
        self.grid_size = grid_size
        self.gs = gs
        self.x = x
        self.z = z
        self.aps =aps
        self.visc = visc
        self.sxx = sxx
        self.sII =sII
        self.exz =exz
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
        self.phase_cmap = ListedColormap(self.phase_color)
        bounds = np.arange(1, 20)   
        norm = BoundaryNorm(bounds, self.phase_cmap.N)
        phase_mesh = ax.pcolormesh(self.x, self.z, self.phase,cmap=self.phase_cmap,norm = norm, shading = self.shading) #plot phase
        phase_mesh = add_temp(phase_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        #phase_mesh = add_fmelt(phase_mesh,self.fmelt,self.x,self.z,self.fig_large,ax,self.label_size)
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(phase_mesh,label='phase',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('phase', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
    
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return  self.canvas_position_counter

    def plot_srII(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
    
        max_srII = -(12.5)
        min_srII = -(15.0)
    
        ax = self.fig_large.add_subplot(self.gs[row,col])
        srII_mesh = ax.pcolormesh(self.x,self.z,self.srII,cmap = 'jet',vmax = max_srII,vmin = min_srII,shading = self.shading)

        srII_mesh = add_temp(srII_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
    
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(srII_mesh,label='strainrate',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('strain rate', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
        return self.canvas_position_counter

    def plot_aps(self): 
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
    
        max_aps = 2.0
        min_aps = 0.0
    
        ax = self.fig_large.add_subplot(self.gs[row,col])
        aps_mesh = ax.pcolormesh(self.x,self.z,self.aps,cmap = 'Blues',vmax = max_aps, vmin = min_aps, shading= self.shading)
        aps_mesh = add_temp(aps_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(aps_mesh,label='plastic strain',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('plastic strain', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
            
        return self.canvas_position_counter

    def plot_visc(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_visc = 25.0
        min_visc = 19.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        visc_mesh = ax.pcolormesh(self.x,self.z,self.visc,cmap = 'jet',vmax = max_visc, vmin = min_visc,shading= self.shading)
        visc_mesh = add_temp(visc_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(visc_mesh,label='viscosity',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('viscosity', fontsize= self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return self.canvas_position_counter

    def plot_sxx(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_sxx = 15.0
        min_sxx = -15.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        sxx_mesh = ax.pcolormesh(self.x,self.z,self.sxx,cmap = 'bwr',vmax = max_sxx, vmin = min_sxx,shading= self.shading)
        sxx_mesh = add_temp(sxx_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(sxx_mesh,label='sxx',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('sxx', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return self.canvas_position_counter
    def plot_sII(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
    
        max_sII = 10.0
        min_sII = 0.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        sII_mesh = ax.pcolormesh(self.x,self.z,self.sII,cmap = 'Purples',vmax = max_sII, vmin = min_sII,shading= self.shading)
        canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        sII_mesh = add_temp(sII_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        sII_mesh = add_velocity(sII_mesh,self.fig_large,ax,self.label_size,self.vx,self.vz,self.x,self.z) #add velocity to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(sII_mesh,label='stress',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('stress', fontsize = self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        
        return self.canvas_position_counter
    
    def plot_syy(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
    
        max_syy = 5.0
        min_syy = -5.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        syy_mesh = ax.pcolormesh(self.x,self.z,self.syy,cmap = 'bwr',vmax = max_syy, vmin = min_syy,shading= self.shading)
        syy_mesh = add_temp(syy_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(syy_mesh,label='syy',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('syy', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_sxz(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
    
        max_sxz = 10.0
        min_sxz = -10.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        sxz_mesh = ax.pcolormesh(self.x,self.z,self.sxz,cmap = 'bwr',vmax = max_sxz, vmin = min_sxz,shading= self.shading)
        sxz_mesh = add_temp(sxz_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(sxz_mesh,label='sxz',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('sxz', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_szz(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_szz = 15.0
        min_szz = -15.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        szz_mesh = ax.pcolormesh(self.x,self.z,self.szz,cmap = 'bwr',vmax = max_szz, vmin = min_szz,shading= self.shading)
        szz_mesh = add_temp(szz_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(szz_mesh,label='szz',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('szz', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_eII(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_eII = 0.0
        min_eII = 5.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        eII_mesh = ax.pcolormesh(self.x,self.z,self.eII,cmap = 'Greens',vmax = max_eII, vmin = min_eII,shading= self.shading)
        eII_mesh = add_temp(eII_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(eII_mesh,label='eII',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('eII', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_exx(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_exx =  5.0
        min_exx = -5.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        exx_mesh = ax.pcolormesh(self.x,self.z,self.exx,cmap = 'seismic',vmax = max_exx, vmin = min_exx,shading= self.shading)
        exx_mesh = add_temp(exx_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(exx_mesh,label='exx',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('exx', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_ezz(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_ezz =  5.0
        min_ezz = -5.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        ezz_mesh = ax.pcolormesh(self.x,self.z,self.ezz,cmap = 'seismic',vmax = max_ezz, vmin = min_ezz,shading= self.shading)
        ezz_mesh = add_temp(ezz_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(ezz_mesh,label='ezz',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('ezz', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_exz(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_exz =  5.0
        min_exz = -5.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        exz_mesh = ax.pcolormesh(self.x,self.z,self.exz,cmap = 'seismic',vmax = max_exz, vmin = min_exz,shading= self.shading)
        exz_mesh = add_temp(exz_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(exz_mesh,label='exz',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('exz', fontsize= self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_mesh(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        ax = self.fig_large.add_subplot(self.gs[row,col])
        
        dummy_data = np.zeros_like(self.phase) #to avoid rendering the mesh
        
        mesh = ax.pcolormesh(self.x,self.z,np.zeros_like(self.phase),edgecolors='black', facecolor='none',shading= self.shading) 
        mesh = add_temp(mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
       
        ax.set_aspect('equal')
        dummy_cbar = self.fig_large.colorbar(mesh, label='mesh',orientation='horizontal', shrink = self.shrink_size, aspect = self.aspect_size)
        dummy_cbar.ax.set_visible(False)
    
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
    
        return self.canvas_position_counter
    def plot_density(self):
    
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_density =  10000.0
        min_density =  0.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        density_mesh = ax.pcolormesh(self.x,self.z,self.density,cmap = 'viridis',vmax = max_density, vmin = min_density,shading= self.shading)
        density_mesh = add_temp(density_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(density_mesh,label='density',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('density', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter
    def plot_pres(self):
        
        row,col = self.canvas_grid_position[self.canvas_position_counter]
        
        max_pres =  1.0
        min_pres =  -100.0
        ax = self.fig_large.add_subplot(self.gs[row,col])
        pres_mesh = ax.pcolormesh(self.x,self.z,self.pres,cmap = 'hot',vmax = max_pres, vmin = min_pres,shading= self.shading)
        pres_mesh = add_temp(pres_mesh,self.temp,self.x,self.z,self.fig_large,ax,self.label_size, self.aspect_size, self.shrink_size) #add temp to figure
        ax.tick_params(axis='x',labelsize = self.font_size)
        ax.tick_params(axis='y',labelsize = self.font_size)
        ax.set_xlim(self.sub_xz_left, self.sub_xz_right)
        ax.set_ylim(self.sub_xz_bottom,self.sub_xz_top + self.height)
        
        ax.set_aspect('equal')
        colorbar = self.fig_large.colorbar(pres_mesh,label='density',orientation='horizontal',shrink = self.shrink_size,aspect = self.aspect_size)
        cbar_ax = colorbar.ax
        cbar_ax.set_xlabel('pres', fontsize=self.font_size)
        colorbar.ax.tick_params(axis='x',labelsize =self.label_size)
        self.canvas_position_counter = position_counter(self.canvas_position_counter,self.canvas_grid_position)
        return self.canvas_position_counter

"add"

def add_temp(mesh,temp,x,z,fig_large,ax,label_size, aspect_size, shrink_size):
    
    temp_level = np.arange(0, 1400, 200)
    temp_cmap = plt.get_cmap('gray')
    temp_contourf = ax.contour(x[:, :-1],z[:, :-1],temp,levels = temp_level,cmap = temp_cmap)
    cbar = fig_large.colorbar(temp_contourf, ax=ax, shrink = shrink_size, aspect = aspect_size, pad = 0.05)
    cbar.ax.tick_params(labelsize = label_size)
    ax.clabel(temp_contourf)
    return mesh
def add_velocity(mesh,fig_large,ax,label_size,vx,vz,x,z):
    
    stride_x = int(50)
    stride_z = int(10)  
    velocity_quiver = ax.quiver(x[:, :-1][::stride_x, ::stride_z],z[:, :-1][::stride_x, ::stride_z],vx[::stride_x, ::stride_z],vz[::stride_x, ::stride_z],scale=50,width=0.003)
    ax.quiverkey(velocity_quiver,X = 0.05,Y= -0.40,U = 1.0, label='3.17E-11 m/s', fontproperties={'size': label_size} )
    return mesh
def add_fmelt(mesh,fmelt,x,z,fig_large,ax,label_size):
    fmelt_min_cutoff = float(0.01)   
    #label issue, not aline with other graph
    fmelt_level = np.arange(0.0,0.11,0.01)
    fmelt_cmap = plt.get_cmap('gist_rainbow')
    
    
    if np.max(fmelt) < fmelt_min_cutoff:      
        pass
        #set minimum cutoff fmelt to draw, to avoid countour error in old python code on linux system(3.6.8)
    else:
        
        fmelt_contourf = ax.contour(x,z,fmelt,levels = fmelt_level,cmap = fmelt_cmap)
        cbar = fig_large.colorbar(fmelt_contourf, ax=ax,shrink=1,pad=0)
        cbar.ax.tick_params(labelsize = label_size)
        ax.clabel(fmelt_contourf)
        
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
def trim_diagram(frame):
    full_path = f"frame_{frame}.png"
    left = int(0)
    right = int(0)
    top = int(0)
    bottom = int(0)
    
    try:
        img = Image.open(full_path)
        width, height = img.size
        right = width * 0.49
        bottom = height 
    except Exception as e:
        print(f"Error processing {full_path}: {e}")
    
    #trim figure
    trim_box  = (left, top, right, bottom)
    trim_img = img.crop(trim_box)
    trim_img.save(f"trimed_frame_{frame}.png")
    print(f"saved trimed_frame_{frame}")
"""main"""    
def main(): 
    
    data = Read_data()
    init_frame, total_frame = count_frame()
    gs,canvas_grid_position,total_position,fig_large,font_size, label_size, shrink_size, aspect_size = set_canvas()
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
        srII = data.read_srII(frame)
        aps = data.read_aps(frame)
        visc = data.read_visc(frame)
        sxx = data.read_sxx(frame)
        sII = data.read_sII(frame)
        vx,vz = data.read_vel(frame) 
        syy = data.read_syy(frame)
        sxz = data.read_sxz(frame)
        szz = data.read_szz(frame)
        eII = data.read_eII(frame)
        exx, ezz, exz = data.read_strain(frame)
        density = data.read_density(frame)
        pres = data.read_pres(frame)
        fmelt = data.read_fmelt(frame)
        figure = Plot(phase,temp,srII,vx,vz,syy,sxz,szz,eII,exx,ezz,exz,density,pres,fmelt,canvas_grid_position,canvas_position_counter,fig_large,font_size,label_size,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps,visc,sxx,sII)
        
        #plot diagram
        
        canvas_position_counter = figure.plot_phase()
        canvas_position_counter = figure.plot_srII()
        canvas_position_counter = figure.plot_aps()
        canvas_position_counter = figure.plot_visc()
        canvas_position_counter = figure.plot_sxx()
        canvas_position_counter = figure.plot_sII()
        canvas_position_counter = figure.plot_exx()
        canvas_position_counter = figure.plot_mesh()
        
        canvas_position_counter = figure.plot_syy()
        canvas_position_counter = figure.plot_sxz()
        canvas_position_counter = figure.plot_szz()
        canvas_position_counter = figure.plot_eII()
        canvas_position_counter = figure.plot_ezz()
        canvas_position_counter = figure.plot_exz()
        canvas_position_counter = figure.plot_density()
        canvas_position_counter = figure.plot_pres()
        
        plt.tight_layout(rect = [0,0,1,0.95])
        fig_large.suptitle(f"frame_{frame} at {t}Myr",fontsize=50)
        fig_large.text(0.25, 0.98, f"frame_{frame} at {t}Myr", fontsize=50, ha='left', va='top')
        fig_large.text(0.75, 0.98, f"frame_{frame} at {t}Myr", fontsize=50, ha='right', va='top')
        plt.savefig(f'frame_{frame}')
        trim_diagram(frame)
        fig_large.clf() #clear legend to avoid stacking
        
        print(f"saved frame_{frame}")
    print(f"finish saving frame, total of {total_frame} frame")
    
if __name__ == '__main__':
    
    fl = flac.Flac()
    main()
