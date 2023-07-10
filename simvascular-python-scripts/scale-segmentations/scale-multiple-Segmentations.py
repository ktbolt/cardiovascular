import os
from pathlib import Path

# This script is used to scale the x,y,z and resclice sizes of
# existing .ctgr segmentation files by a user set scale factor.
# 
# Edit the values below and then run the script. E.g:
# >py scale-multiple-segmentations.py 
# $python3 scale-multiple-segmentations.py
# 
# Edit this section:
#   data_loc:
#       Directory containg the segmentations you wish to scale.
#       Windows users: Replace "\" with "/" or use "\\".
#   scale_factor:
#       The scale factor which you wish to scale the points around the origin.
#
data_loc = "Relative/path/to/segmentations/directory/"
data_loc = "C:\\Absolute\\path\\to\\segmentations\\directory\\"
scale_factor = 0.1

# Do not edit this section.
#
def indentation(line_text, tabsize=4):
    line_expanded = line_text.expandtabs(tabsize)
    if line_expanded.isspace():
        return 0
    else:
        return(len(line_expanded) - len(line_expanded.lstrip()))


out_dir = data_loc + "Scaled/"
os.makedirs(Path(out_dir), exist_ok=True)

sv_seg_list = Path(data_loc).glob('**/*.ctgr')
for sv_seg in sv_seg_list:
    if str(sv_seg).endswith(".ctgr") == True and str(sv_seg).endswith("_scaled.ctgr") == False:
        seg_name = str(sv_seg).replace(str(Path(data_loc)), '').replace('\\','').replace('.ctgr', '')
        sv_scaled_seg = Path(out_dir + seg_name + "_scaled.ctgr")
        print(f"Beginning to scale {seg_name}.")

        with open(sv_seg, 'r', encoding = 'utf-8') as data:
            print("Opened input file.")
            with open(sv_scaled_seg, 'w', encoding = 'utf-8') as scaled_data:
                print("Generated empty output file.")
                
                for line in data:
                    if '<point id="' in line:                
                        values = line.split()
                        values[2] = 'x="' + str(float(values[2][3:-1])*scale_factor) + '"'
                        values[3] = 'y="' + str(float(values[3][3:-1])*scale_factor) + '"'
                        values[4] = 'z="' + str(float(values[4][3:-1])*scale_factor) + '"'
                        scaled_line = indentation(line)*' ' + ' '.join(values) + '\n'
                        scaled_data.write(scaled_line)
                    
                    elif '<pos x="' in line:
                        values = line.split()
                        values[1] = 'x="' + str(float(values[1][3:-1])*scale_factor) + '"'
                        values[2] = 'y="' + str(float(values[2][3:-1])*scale_factor) + '"'
                        values[3] = 'z="' + str(float(values[3][3:-1])*scale_factor) + '"'
                        scaled_line = indentation(line)*' ' + ' '.join(values) + '\n'
                        scaled_data.write(scaled_line)
                    
                    elif '<contourgroup path_name="' in line:
                        values = line.split()
                        values[3] = 'reslice_size="' + str(round(int(values[3][14:-1])*scale_factor)) + '"'
                        values[4] = 'point_2D_display_size=""'
                        values[5] = 'point_size=""'
                        scaled_line = indentation(line)*' ' + ' '.join(values) + '\n'
                        scaled_data.write(scaled_line)

                    else:
                        scaled_data.write(line)
                    
            print("Filled output file with scaled content.")
            print(f"{seg_name} has been scaled by factor {scale_factor}.\n")