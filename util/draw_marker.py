#!/usr/bin/env python3
"""draw marker """
# look through flac to see how to draw pressure, and modify count frame
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import flac 
import numpy as np

def main():
  
    trace_id = []
    trace_x = []
    trace_z = []
    trace_temp = []
    trace_p = []

    def count_frame():
        max_frame = 1000
        init_frame = 1
        
        for frame in range(init_frame, max_frame + 1): 
            try:
                fl.read_mesh(frame)             
            except Exception:                
                total_frame = frame - 1
                print(f"Total frame of {total_frame}")
                return init_frame, total_frame 

        print(f"Reached maximum frame allowed: {max_frame}")
        return init_frame, last_frame
    
    def read_time():
        with open('_contents.0') as contents:
            time = contents.read() #time_step, loop, and time        
        return time
    
    def set_time(time):  
        row_str = time.strip().split('\n')
        time_list = []
        for row in row_str:
            element = row.split()
            time_list.append(element)
        time = np.array(time_list)
        time = time.astype(float)
        trace_time = time[:,2]
        return trace_time
    
    def AREA(x,z, frame,reset_condition):

        left, right, top, bottom = 275.0, 325.0, 10.0, -1.0
 
        if frame != last_frame:
            bottom = -40.0
        if reset_condition == -1:
                    bottom = -5.0
        area = (x >= left) & (x <= right) & (z >= bottom) & (z <= top) 
        bound = {"left": left, "right": right, "top": top , "bottom": bottom}
        return area, bound

    def select_para(area,para):

        masked_para = np.where(area, para, -np.inf)
        max_para_id = np.argmax(masked_para)

        return max_para_id
        
    def target_frame_id(frame):

        x, z, age, phase, ID, a1, a2, ntriag = fl.read_markers(frame) 
        temp,p = add_marker(frame)
        area, bound  = AREA(x,z,frame,reset_condition)
        max_para_id = select_para(area,para = temp)  
       
        return ID[max_para_id]
    def add_marker(i):
                
        x, z = fl.read_mesh(i)
        T = fl.read_temperature(i)
        ph = fl.read_phase(i)
        xm, zm, age, phase, idm, a1, a2, ntriag = fl.read_markers(i)
        xx = flac.marker_interpolate_node(ntriag, a1, a2, fl.nz, x)
        # nodal field
        Tm = flac.marker_interpolate_node(ntriag, a1, a2, fl.nz, T)
        # elem field
        pm = flac.marker_interpolate_elem(ntriag, fl.nz, ph)
        return Tm, pm
    
    init_frame, last_frame = count_frame()
    reset_condition = int(0)
    tracked_id = target_frame_id(frame = last_frame)
    time = read_time()
    trace_time = set_time(time)
    
    for frame in range(last_frame , init_frame - 1, -1):
        
        x, z, age, phase, ID, a1, a2, ntriag = fl.read_markers(frame)

        area, bound = AREA(x,z,frame,reset_condition)
        valid_id = ID[area]

        if tracked_id not in valid_id: 
            reset_condition = -1
            tracked_id = target_frame_id(frame)

        temp,p = add_marker(frame)   

        current_idx = np.where(ID == tracked_id)[0][0]

        trace_id.append(tracked_id)
        trace_x.append(x[current_idx])
        trace_z.append(z[current_idx])
        trace_temp.append(temp[current_idx])
        trace_p.append(p[current_idx])
        
        reset_condition = 0
        print(f"processing frame : {frame}")

    #foward the time 
    trace_id = trace_id[::-1]
    trace_x = trace_x[::-1]
    trace_z = trace_z[::-1]
    trace_temp = trace_temp[::-1]
    trace_p = trace_p[::-1]

    """plot figure"""   

    #marker position

    margin = int(10)
    box_width = bound["right"] - bound["left"]
    box_height = bound["top"] - bound["bottom"]
    base_figsize = 7.5 
    aspect_ratio = box_height / box_width
    dynamic_height = base_figsize * aspect_ratio

    def plot_by_id(x_data, y_data, id_data):
        
        unique_ids = np.unique(id_data)
        cmap = plt.get_cmap('tab10')
        
        for i, uid in enumerate(unique_ids):
            idx = (np.array(id_data) == uid)
            plt.scatter(np.array(x_data)[idx], np.array(y_data)[idx], 
                        label=str(uid), color=cmap(i%10))

    plt.figure(figsize=(base_figsize, dynamic_height))    
    plt.title("marker position") 
    plot_by_id(trace_x, trace_z, trace_id)
    # plt.legend(title="Marker ID", loc='best')
    plt.xlim(bound["left"] - margin, bound["right"] + margin)
    plt.ylim(bound["bottom"]-  margin, bound["top"])
    plt.xlabel("distance (km)")
    plt.ylabel("depth (km)")
    plt.gca().set_aspect('equal')
    plt.tight_layout()
    plt.savefig("marker_postion_x_z.png")
    plt.clf()

    #pressure-temperature (P-T diagram) 
    plt.figure(figsize=(15, 5))
    plt.title("P-T diagram") 
    plt.scatter(trace_temp, trace_p, c=trace_temp,cmap='tab10')
    plt.ylim(0,1000)
    plt.xlim(0, 1330) # celsius 
    plt.xlabel("temperauture (celsius)")
    plt.ylabel("pressure")
    plt.gca().set_aspect('equal')
    plt.tight_layout()
    plt.savefig("marker_PT_diagram.png")
    plt.clf()

    # marker temp - time
    plot_by_id(trace_time, trace_temp, trace_id)
    plt.title("marker temperature - time")
    # plt.legend(title="Marker ID", loc='best')
    plt.ylim(0,1330)
    plt.xlim(0,trace_time[-1])
    plt.ylabel("temperature (celsius)")
    plt.xlabel("time (Myr)")
    plt.tight_layout()
    plt.savefig("marker_temp_time.png")
    plt.clf()

if __name__ == '__main__':
    
    fl = flac.Flac()
    main()







