import cv2
import glob
import os
import sys

# --- 1. Dynamically receive target directory path ---
# Check if the user provided a directory path when executing the command
if len(sys.argv) > 1:
    target_directory = sys.argv[1]
else:
    target_directory = './' # Safely fallback to current directory

# Check if the path actually exists
if not os.path.exists(target_directory):
    print(f"Error: Directory not found '{target_directory}'")
    sys.exit(1)

output_filename = 'trimmed_frame_movie.avi'

# --- 2. Set paths ---
file_pattern = os.path.join(target_directory, 'trimed_frame_*.png')
files = glob.glob(file_pattern)
output_path = os.path.join(target_directory, output_filename)

# --- 3. Sort and verify ---
files.sort(key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0]))

if not files:
    print(f"Error: No images found in {target_directory}!")
    sys.exit(1)

# --- 4. Build video ---
first_frame = cv2.imread(files[0])
original_height, original_width, layers = first_frame.shape

# --- 5. Shrink Size Feature ---
# Set the scaling factor (e.g., 0.5 means both width and height are reduced by half)
scale_factor = 0.25 
width = int(original_width * scale_factor)
height = int(original_height * scale_factor)
size = (width, height)

fps = 5
fourcc = cv2.VideoWriter_fourcc(*'XVID') 
video = cv2.VideoWriter(output_path, fourcc, fps, size)

print(f"Found {len(files)} images in {target_directory}. Starting video generation...")
print(f"Original size: {original_width}x{original_height} -> Resizing to: {width}x{height}")

for file in files:
    img = cv2.imread(file)
    
    # Resize the image to prevent the "dimensions too large" error
    resized_img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    video.write(resized_img)

video.release()
print(f"Video saved to: {output_path}")