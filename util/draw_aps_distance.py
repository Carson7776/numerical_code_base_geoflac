#!/usr/bin/env python3
"""read aps distance results"""
import os
import sys
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

ROOT_DIR = "/scratch2/humaorong"
OUTPUT_DIR = "/scratch2/humaorong/results/fault_distance_to_peak_and_trench"

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

def find_aps_distance_files(model_dir):

    pattern = os.path.join(model_dir, "aps_distance_frame_*.npz")
    files = sorted(glob.glob(pattern))

    return files

def read_npz(file_path, keys=None):

    npz = np.load(file_path)

    if keys is None:
        keys = npz.files

    record = {key: npz[key] for key in keys}

    return record

def read_model_aps_distance(model_dir, keys=None):

    files = find_aps_distance_files(model_dir)
    model_name = os.path.basename(os.path.normpath(model_dir))

    records = []
    for file_path in files:
        record = read_npz(file_path, keys)
        record['model'] = model_name
        record['file'] = os.path.basename(file_path)
        records.append(record)

    return records

"""set parameter"""

def set_models():

    model_list = sys.argv[1:]

    return model_list

def set_keys():

    keys = [
        'frame',
        'time',
        'horizontal_to_highest',
        'vertical_to_highest',
        'horizontal_to_lowest',
        'vertical_to_lowest',
    ]

    return keys

"""check values"""

def check_records(records, model_dir):

    if not records:
        print(f"no aps_distance files found in {model_dir}")

    return records

"""analyze data"""

def find_farthest_from_peak(record):

    horizontal = record['horizontal_to_highest']
    vertical = record['vertical_to_highest']

    if horizontal.size == 0:
        return None

    farthest_id = np.argmax(np.abs(horizontal))

    farthest_point = {
        'model': record['model'],
        'horizontal_to_highest': horizontal[farthest_id],
        'vertical_to_highest': vertical[farthest_id],
    }

    return farthest_point

def find_farthest_points(all_records):

    farthest_points = []
    for record in all_records:
        farthest_point = find_farthest_from_peak(record)
        if farthest_point is not None:
            farthest_points.append(farthest_point)

    return farthest_points

def find_farthest_from_lowest(record):

    horizontal = record['horizontal_to_lowest']
    vertical = record['vertical_to_lowest']

    if horizontal.size == 0:
        return None

    farthest_id = np.argmax(np.abs(horizontal))

    farthest_point = {
        'model': record['model'],
        'horizontal_to_lowest': horizontal[farthest_id],
        'vertical_to_lowest': vertical[farthest_id],
    }

    return farthest_point

def find_farthest_points_lowest(all_records):

    farthest_points = []
    for record in all_records:
        farthest_point = find_farthest_from_lowest(record)
        if farthest_point is not None:
            farthest_points.append(farthest_point)

    return farthest_points

""" plot diagram """

def plot_farthest_points(farthest_points):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6,6))

    cmap = plt.get_cmap('tab20')

    for i, point in enumerate(farthest_points):
        color = cmap(i % 20)
        ax.scatter(point['horizontal_to_highest'], point['vertical_to_highest'], marker='^', s=20, color=color, label=point['model'])

    ax.set_xlabel('horizontal distance to highest point (km)')
    ax.set_ylabel('vertical distance to highest point (km)')
    ax.legend(loc='upper right', fontsize=6)
    fig.savefig(os.path.join(OUTPUT_DIR, "aps_farthest_from_peak.png"), pad_inches=0.1, bbox_inches='tight')
    plt.close(fig)

def plot_farthest_points_lowest(farthest_points):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6,6))

    cmap = plt.get_cmap('tab20')

    for i, point in enumerate(farthest_points):
        color = cmap(i % 20)
        ax.scatter(point['horizontal_to_lowest'], point['vertical_to_lowest'], marker='^', s=20, color=color, label=point['model'])

    ax.set_xlabel('horizontal distance to lowest point (km)')
    ax.set_ylabel('vertical distance to lowest point (km)')
    ax.legend(loc='upper right', fontsize=6)
    fig.savefig(os.path.join(OUTPUT_DIR, "aps_farthest_from_lowest.png"), pad_inches=0.1, bbox_inches='tight')
    plt.close(fig)

"""main"""

def main():

    model_list = set_models()
    keys = set_keys()

    all_records = []

    for model_code in model_list:
        model_dir = resolve_model_dir(model_code)
        if model_dir is None:
            continue
        records = read_model_aps_distance(model_dir, keys)
        check_records(records, model_dir)
        all_records.extend(records)

    print(f"loaded {len(all_records)} aps_distance record(s) from {len(model_list)} model(s)")

    farthest_points = find_farthest_points(all_records)
    plot_farthest_points(farthest_points)

    farthest_points_lowest = find_farthest_points_lowest(all_records)
    plot_farthest_points_lowest(farthest_points_lowest)

    return all_records

if __name__ == '__main__':

    all_records = main()
