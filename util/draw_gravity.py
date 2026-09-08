#!/usr/bin/env python3
import flac 
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from flac_gravity import compute_gravity

fl = flac.Flac()          
total_frame = fl.nrec

for fr in range(1, total_frame + 1):
    
    px, topo, topomod, grav = compute_gravity(frame=fr) 

    itrench = topo.argmin()
    ipeak = topo.argmax()
    trench_x = px[itrench] #meter
    trench_z = topo[itrench] #meter
    peak_x = px[ipeak]
    peak_z = topo[ipeak]

    t = fl.time[fr - 1]

    fig, ax1 = plt.subplots(figsize=(12, 4))

    ax1.plot(px, topo, color='tab:blue')
    ax1.scatter(trench_x, trench_z, color='blue', marker='v',zorder=5, label='Lowest point')
    ax1.scatter(peak_x, peak_z, color='blue',marker='^', zorder=5, label='Highest point')
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('Topography (m)')
    ax1.tick_params(axis='y')
    ax1.set_xlim(trench_x - 100000, trench_x + 100000) 
    ax1.set_ylim(trench_z - 10000, trench_z + 10000)
    ax1.legend(loc='upper right')
    ax1.set_title(f'frame {fr:02d} at {t:.2f} Myr')

    ax2 = ax1.twinx()
    ax2.plot(px, grav, color='tab:orange')
    ax2.set_ylabel('Gravity')
    ax2.tick_params(axis='y')

    plt.savefig(f"topo_grav_frame_{fr}.png")
    plt.close(fig)