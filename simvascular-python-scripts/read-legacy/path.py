'''
Convert legacy paths to current XML format .pth files.
'''
import sv 

file_name = "./legacy-paths/0005_1001-cm.paths"

sv.PathLegacyIO.Convert(file_name=file_name, output_dir="./converted-paths")


