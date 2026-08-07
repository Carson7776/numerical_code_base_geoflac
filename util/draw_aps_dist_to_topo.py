#!/usr/bin/env python3
"""draw results"""
import os
import sys
import glob
import flac
import numpy as np
# --- CLUSTER EXECUTION ---
import matplotlib
matplotlib.use('Agg')
# -------------------------------------------
from matplotlib import pyplot as plt
plt.rcParams.update({"font.size": 8})

from matplotlib.gridspec import GridSpec
from scipy.signal import find_peaks

ROOT_DIR = "/scratch2/humaorong"

fl = None

"""read data"""

def resolve_model_dir(model_code):

    pattern = os.path.join(ROOT_DIR, f"{model_code}*")
    matches = sorted(glob.glob(pattern))

    if len(matches) == 0:
        print(f"no folder found for model code {model_code}")
        return None

    if len(matches) > 1:
        print(f"multiple folders found for model code {model_code}, using {matches[0]}")

    return matches[0]

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
def set_models():

    model_list = sys.argv[1:]

    return model_list

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

        return  self.canvas_position_counter, self.slab_depth

    def plot_aps_distance(self, frame):

        def fault(self):

            peak_aps = {} #fault position
            peak_aps_id, _  = find_peaks(self.aps[:,0], height = 0.1)

            peak_aps['pos_x'] = self.x[peak_aps_id, 0]
            peak_aps['pos_z'] = self.z[peak_aps_id, 0]

            return peak_aps

        def reference_points(self):

            z_max_id = np.argmax(self.z[:,0])
            z_min_id = np.argmin(self.z[:,0])

            highest = {'x': self.x[z_max_id,0], 'z': self.z[z_max_id,0]}
            lowest  = {'x': self.x[z_min_id,0], 'z': self.z[z_min_id,0]}

            return highest, lowest

        peak_aps = fault(self)
        highest, lowest = reference_points(self)

        horizontal_to_highest = peak_aps['pos_x'] - highest['x']
        vertical_to_highest = peak_aps['pos_z'] - highest['z']

        horizontal_to_lowest = peak_aps['pos_x'] - lowest['x']
        vertical_to_lowest = peak_aps['pos_z'] - lowest['z']

        np.savez(f"aps_distance_frame_{frame}.npz",
                 frame = frame,
                 time = self.t,
                 horizontal_to_highest = horizontal_to_highest,
                 vertical_to_highest = vertical_to_highest,
                 horizontal_to_lowest = horizontal_to_lowest,
                 vertical_to_lowest = vertical_to_lowest)

        fig_highest, ax_highest = plt.subplots(figsize=(6,6))
        ax_highest.scatter(horizontal_to_highest, vertical_to_highest, color='blue', marker='^', s=20, label='fault')
        ax_highest.set_xlabel('horizontal distance to highest point (km)')
        ax_highest.set_ylabel('vertical distance to highest point (km)')
        ax_highest.text(0.02, 0.95, f"Time = {self.t:.3f}Ma", color='black', fontsize=self.font_size, transform=ax_highest.transAxes)
        ax_highest.legend(loc='upper right', fontsize=self.font_size)
        fig_highest.savefig(f"aps_dist_to_highest_frame_{frame}.png", pad_inches=0.1, bbox_inches='tight')
        plt.close(fig_highest)

        fig_lowest, ax_lowest = plt.subplots(figsize=(6,6))
        ax_lowest.scatter(horizontal_to_lowest, vertical_to_lowest, color='red', marker='^', s=20, label='fault')
        ax_lowest.set_xlabel('horizontal distance to lowest point (km)')
        ax_lowest.set_ylabel('vertical distance to lowest point (km)')
        ax_lowest.text(0.02, 0.95, f"Time = {self.t:.3f}Ma", color='black', fontsize=self.font_size, transform=ax_lowest.transAxes)
        ax_lowest.legend(loc='upper right', fontsize=self.font_size)
        fig_lowest.savefig(f"aps_dist_to_lowest_frame_{frame}.png", pad_inches=0.1, bbox_inches='tight')
        plt.close(fig_lowest)
"add"

"""check values"""

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

def process_model(model_dir):

    global fl

    os.chdir(model_dir)
    fl = flac.Flac()

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
        g = None

        figure = Plot(phase,temp,canvas_grid_position,canvas_position_counter,fig_large,shrink_size,aspect_size,sub_xz,grid_size,gs,x,z,aps,g, font_size,t)

        #plot diagram

        canvas_position_counter,slab_depth  = figure.plot_phase()

        if 20 < abs(slab_depth) < 22:

             figure.plot_aps_distance(frame)

             fig_large.clf() #clear legend to avoid stacking


             print(f"saved frame_{frame}_aps_distance")
             break

    print(f"finish saving frame, total of {total_frame} frame")

"""main"""
def main():

    original_dir = os.getcwd()
    model_list = set_models()

    for model_code in model_list:
        model_dir = resolve_model_dir(model_code)
        if model_dir is None:
            continue

        process_model(model_dir)
        os.chdir(original_dir)

if __name__ == '__main__':

    main()
