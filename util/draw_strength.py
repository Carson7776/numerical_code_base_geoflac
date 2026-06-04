#!/usr/bin/env python3
"""draw strength profile"""
#strength at time frame = 0 will need further improvement! also add temp profile
import re
import math
import glob
import flac 
import pprint
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')

"""read data"""
class Read_data:
    
    def read_subduction(self):    
        try:
            with open('subduction.inp') as f:
                content = f.readlines()   
        except Exception as e:
            print(e)
            print("subduction file not found")
        return content
    def read_flac(self,frame):
        phase = fl.read_phase(frame)
        return phase   
    def read_nxnz(self,frame):
        x,z = fl.read_mesh(frame) #get the x and z coordinate
        x_center = (x[:-1, :-1] + x[1:, :-1] + x[:-1, 1:] + x[1:, 1:]) / 4.0
        z_center = (z[:-1, :-1] + z[1:, :-1] + z[:-1, 1:] + z[1:, 1:]) / 4.0
        return x_center,z_center    
    def read_visc(self,frame):
        visc = fl.read_visc(frame)
        return visc
    def read_aps(self,frame):
        aps = fl.read_aps(frame)
        return aps
    def read_visc(self,frame):
        visc =fl.read_visc(frame)
        return visc
    def read_srII(self,frame):
        srII = fl.read_srII(frame)
        return srII
"""count frame""" 
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
            #print(f"total frame of {frame-1}")
            total_frame = frame #the ammount of total frame equals frame - 1
            break   
    return init_frame, total_frame
 
"""get_material_properties"""   
def get_material_properties(subduction):
    
    phase_dict  = {}    
    keys = ["irheol", "unused", "den", "alfa", "beta", "n", "A", "E", 
        "rl", "rm", "pls1", "pls2", "fric1", "fric2", "coh1", "coh2"]
    try:    
        head_index = next((i for i, line in enumerate(subduction) if "Number of Different Rheologies" in line), None)
        tail_index = next((i for i, line in enumerate(subduction) if " INITIAL PHASE DISTRIBUTION" in line), None)
        
        pattern =  r'^;\((\d+)\)'  
        for i,line in enumerate(subduction[head_index: tail_index]): 
            
            line = line.strip()
            match = re.match(pattern,line)
            
            if match:
                phase_id = int(match.group(1))
                data_id = head_index + i + 1
                parameter = subduction[data_id].strip().split(',')
                phase_dict[phase_id] = {
                    'irhoel': float(parameter[0]),
                    'unused': float(parameter[1]),
                    'den': float(parameter[2]),
                    'alfa': float(parameter[3]),
                    'beta': float(parameter[4]),
                    'n': float(parameter[5]),
                    'A': float(parameter[6]),
                    'E': float(parameter[7]),
                    'rl': float(parameter[8]),
                    'rm': float(parameter[9]),
                    'pls1': float(parameter[10]),
                    'pls2': float(parameter[11]),
                    'fric1': float(parameter[12]),
                    'fric2': float(parameter[13]),
                    'coh1': float(parameter[14]),
                    'coh2': float(parameter[15])
                    }               
    except Exception as e:
        print(e)
        print("rheology parameter not found")
     
    return phase_dict
            
"""set slice profile"""
class Slice_profile:
    
    def __init__(self,phase,x,z,aps):
        self.phase = phase
        self.x = x
        self.z = z
        self.aps = aps
        
    def area_slice(self):
        
        def area():
            interval = int(10)
            return interval
        #strength profile using fix interval
        def x_slice_interval(interval):
            x_slice_id_list = []
            left_end = self.x[0,0]
            right_end = self.x[-1,0]
            x_slice = np.linspace(left_end,right_end,interval)
            
            for i in range(0,interval):
                position_x = x_slice[i]
                x_id = np.abs(self.x[:,0]-position_x).argmin()
                x_id = int(x_id)
                x_slice_id_list.append(x_id)
            return x_slice_id_list
        #strength profile according to distance away from the trench(topo minimum)
        def x_slice_trench():

            trench = {}
            weak_zone = float(500)
            distance = float(200) #km
            x_slice_id_list = []

            trench_id = np.argmin(self.z[:,0])
            trench["pos_x"] = self.x[trench_id,0]
            trench["pos_z"] = self.z[trench_id,0]
            trench_right = trench["pos_x"] + distance
            trench_left = trench["pos_x"] - distance
            weak_zone_right = weak_zone + distance
            weak_zone_left = weak_zone - distance

            if trench_left > self.x[0,0] and trench_right < self.x[-1,0]:
                right_id = np.abs(self.x[:,0] - trench_right).argmin()
                x_slice_id_list.append(right_id)
                left_id = np.abs(self.x[:,0] - trench_left).argmin()
                x_slice_id_list.append(left_id)
            else: 
                right_id = np.abs(self.x[:,0] - weak_zone_right).argmin()
                x_slice_id_list.append(right_id)
                left_id = np.abs(self.x[:,0] - weak_zone_left).argmin()
                x_slice_id_list.append(left_id)
                print(f"trench too close to boundary, set strength profiles to {self.x[left_id,0]:.3f}km and {self.x[right_id,0]:.3f}km")
            return x_slice_id_list
        
        def aps_slice_interval(x_slice_id_list):
            
            aps_rows,aps_cols = np.shape(self.aps)
            aps_slice_array = np.zeros((len(x_slice_id_list),aps_cols))
            
            for i in range(0,len(x_slice_id_list)):
                
                aps_slice_array[i,:] = self.aps[x_slice_id_list[i],:]
            return aps_slice_array
        
        #interval = area()
        #x_slice_id_list = x_slice_interval(interval)
        x_slice_id_list = x_slice_trench()
        aps_slice_array = aps_slice_interval(x_slice_id_list)
        return x_slice_id_list, aps_slice_array
    
"""calculate strenght"""    
class Strength:
    
    def __init__(self,frame,phase_dict,phase,x,z,x_slice_id_list,visc,aps,srII,aps_slice_array):
        self.frame = frame
        self.phase_dict = phase_dict
        self.phase = phase
        self.x = x
        self.z = z
        self.x_slice_id_list = x_slice_id_list
        self.visc = visc
        self.aps = aps
        self.srII =srII
        self.aps_slice_array = aps_slice_array
        
    def run_through_all_slice(self):
        
        def fricition_strength(slice, fricition , cohesion):

            
            #mohr-Colomb failure criterion
            g =float(9.8) #gravity
            normal_stress = []

            z_slice = self.z[slice, :] * 1000.0 #km change to meter
            initial_depth = float(0.0)
            z_diff = np.diff(z_slice) #calculate the distance between each cell center
            depth = np.cumsum(z_diff) #calculate the depth of boundary of two nearby cells 
            depth = np.insert(depth,0,initial_depth) 
            depth_diff = np.diff(depth)
            phases = self.phase[slice, :len(depth_diff)] #check if miss end element of phases(107,), depth_diff(106,)
            
            #density * g * depth 
            densities = np.array([self.phase_dict[i]["den"] for i in phases])
            increments = densities * g * np.abs(depth_diff)
            normal_stress = np.cumsum(increments)
            normal_stress = np.insert(normal_stress, 0, 0.0) #surface, normal stress equals 0
            #tan(phi)
            fric = np.array([self.phase_dict[i][fricition] for i in phases])
            fric = np.insert(fric,0, 0.0) #surface, fric_1s equals 0
            tan_fric = np.tan(np.radians(fric))
            #cohesion
            coh = np.array([self.phase_dict[i][cohesion] for i in phases])
            coh = np.insert(coh,0,0.0) #surface, coh_1s equals 0
            
            #fricition strength
            normal_stress_tan_fric_1 = normal_stress * tan_fric            
            fric_strength =  coh + normal_stress_tan_fric_1
            
            return fric_strength
        def strength_weaking(slice,before_weak_fric_strength,after_weak_fric_strength ):
            weak_max = float(2) #maximum fricitional strength weaking for all phases
            weak_ratio = abs(1-(self.aps[slice,:] / weak_max)) 
            fric_strength = np.zeros_like(self.z[slice, :]) #initialize

            fric_strength = weak_ratio * before_weak_fric_strength - after_weak_fric_strength
            fully_weak_strength_id = self.aps[slice,:] >= weak_max 
            fric_strength[fully_weak_strength_id] = after_weak_fric_strength[fully_weak_strength_id]  #fricitional strength including strength weakening
            return fric_strength

        def viscosity_strength(slice):
            char_strain_rate = 10**-15 
            visc_strength = 2 * (10**self.visc[slice, :]) * char_strain_rate
            return visc_strength
        def total_strength(slice, visc_strength, before_weak_fric_strength, after_weak_fric_strength):
            strength = np.min([visc_strength, before_weak_fric_strength, after_weak_fric_strength], axis=0) #yields at the weakest maximim strengths
            return strength
        
        for i in range(0,len(self.x_slice_id_list)):
            
            slice = self.x_slice_id_list[i]
            print(f"time_frame:{self.frame}, slice_profile: {i} at {self.x[slice,0]:.3f}km ")

            before_weak_fric_strength = fricition_strength(slice, fricition = "fric1", cohesion = "coh1") #before weakening
            after_weak_fric_strength = fricition_strength(slice, fricition = "fric2", cohesion = "coh2") #after weakening
            #fric_strength = strength_weaking(slice, before_weak_fric_strength,after_weak_fric_strength) #don't use right now
            visc_strength = viscosity_strength(slice)
            strength =total_strength(slice, visc_strength, before_weak_fric_strength, after_weak_fric_strength)

            """plot"""
            meter = float(1000)
            plt.plot(visc_strength, meter*self.z[slice,:], label ="viscosity strength")
            plt.plot(before_weak_fric_strength, meter *self.z[slice, :], label ="fricitional strength before weakening")
            plt.plot(after_weak_fric_strength, meter *self.z[slice, :], label ="fricitional strength after weakening")
            plt.plot(strength, meter *self.z[slice, :], label ="stength")
            plt.title(f"Strength profile at x = {self.x[slice,0]:.3f} (km), time_frame_{self.frame}")
            plt.xlabel("strength(Pa)")
            plt.ylabel("depth(m)")
            plt.legend()
            plt.xlim(0,10**9)
            plt.ylim(-1 *meter*100,0)
            plt.savefig(f"time_frame_{self.frame}_strength_profile_{i}.png",bbox_inches='tight') 
            plt.close() 
            

def main():
    
    data = Read_data()  
    subduction = data.read_subduction()
    phase_dict = get_material_properties(subduction)
    init_frame, total_frame = count_frame()
    
    for frame in range(init_frame,total_frame):
        
        phase = data.read_flac(frame)
        x,z = data.read_nxnz(frame)
        visc = data.read_visc(frame)
        aps = data.read_aps(frame)
        visc = data.read_visc(frame)
        srII = data.read_srII(frame)

        profile = Slice_profile(phase,x,z,aps)
        x_slice_id_list,aps_slice_array = profile.area_slice()
        time_step = Strength(frame,phase_dict,phase,x,z,x_slice_id_list,visc,aps,srII,aps_slice_array)
        time_step.run_through_all_slice()
        print("-" *50)
        
if __name__ == '__main__':
    
    fl = flac.Flac()
    main()
    
