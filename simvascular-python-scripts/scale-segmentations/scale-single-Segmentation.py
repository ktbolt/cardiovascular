from pathlib import Path

# Edit this section:
#   data_loc:
#       Directory containg the segments you wish to scale.
#       Windows users: Either replace "\" with "/" or use "\\".
#   path_name:
#       The name of the path you wish to scale.
#   scale_factor:
#       The scale factor which you wish to scale the points around the origin.
#
data_loc = "Relative/path/to/directory/"
data_loc = "C:\\Absolute\\path\\to\\Directory\\"
seg_name = "example"
scale_factor = 0.1

# Do not edit this section.
#
def indentation(line_text, tabsize=4):
    line_expanded = line_text.expandtabs(tabsize)
    if line_expanded.isspace():
        return 0
    else:
        return(len(line_expanded) - len(line_expanded.lstrip()))

sv_seg = Path(data_loc + seg_name + ".ctgr")
sv_scaled_seg = Path(data_loc + seg_name + "_scaled.ctgr")

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
        print(f"{seg_name} has been scaled by factor {scale_factor}.")