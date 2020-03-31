'''
Convert legacy paths to current XML format .pth files.
'''
import sv 

file_name = "./legacy-paths/0005_1001-cm.paths"
out_dir = "./converted-segmentations"

file_name = "./osmc-legacy-paths/0110_0001-cm.paths"
file_name = "./osmc-legacy-paths/0001_0001-cm.paths"
out_dir = "./osmc-converted-paths/0001_0001"

sv.PathLegacyIO.Convert(file_name=file_name, output_dir=out_dir)


