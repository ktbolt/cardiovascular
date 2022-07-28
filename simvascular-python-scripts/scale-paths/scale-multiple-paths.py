import os
from pathlib import Path

# This script is used to scale the x,y,z and resclice sizes of
# existing .pth path files by a user set scale factor.
# 
# Edit the values below and then run the script. E.g:
# >py scale-multiple-paths.py 
# $python3 scale-multiple-paths.py
# 
# Edit this section:
#   data_loc:
#       Directory containg the paths you wish to scale.
#       Windows users: Replace "\" with "/" or use "\\".
#   scale_factor:
#       The scale factor which you wish to scale the points around the origin.
#
data_loc = "Relative/path/to/paths/directory/"
data_loc = "C:\\Absolute\\path\\to\\paths\\directory\\"
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

sv_path_list = Path(data_loc).glob('**/*.pth')
for sv_path in sv_path_list:
     if str(sv_path).endswith(".pth") == True and str(sv_path).endswith("_scaled.pth") == False:
          path_name = str(sv_path).replace(str(Path(data_loc)), '').replace('\\','').replace('.pth', '')
          sv_scaled_path = Path(out_dir + path_name + "_scaled.pth")
          print(f"Beginning to scale {path_name}.")
          
          with open(sv_path, 'r', encoding = 'utf-8') as data:
               print("Opened input file.")
               with open(sv_scaled_path, 'w', encoding = 'utf-8') as scaled_data:
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
                         
                         elif '<path id="' in line:
                              values = line.split()
                              
                              for i in range(len(values)):
                                   if values[i].startswith('reslice_size="'):
                                        values[i] = 'reslice_size="' + str(round(int(values[i][14:-1])*scale_factor)) + '"'
                                   elif values[i].startswith('point_2D_display_size="'):
                                        values[i] = 'point_2D_display_size=""'
                                   elif values[i].startswith('point_size"'):
                                        values[i] = 'point_size="">'
                              
                              scaled_line = indentation(line)*' ' + ' '.join(values) + '\n'
                              scaled_data.write(scaled_line)
                         
                         else:
                              scaled_data.write(line)
                         
                    print("Filled output file with scaled content.")
                    print(f"{path_name} has been scaled by factor {scale_factor}.\n")