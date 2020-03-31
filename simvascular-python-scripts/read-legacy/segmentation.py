'''
Convert legacy segmenations to the current XML format .ctgr files.
'''

import sv 

file_name = "./osmc-legacy-segmentations/0001_0001_groups-cm/lt_sbclvn_FINAL"
path_file_name = "./osmc-legacy-paths/0001_0001-cm.paths"
out_dir = "./osmc-converted-segmentations/0001_0001"

sv.SegmentationLegacyIO.Convert(file_name=file_name, path_file=path_file_name, output_dir=out_dir)

#help(sv.SegmentationLegacyIO)

