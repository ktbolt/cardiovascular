'''
Convert legacy segmenations to the current XML format .ctgr files.
'''

import sv 

file_name = "./legacy-segmentations/aorta"
out_dir = "./converted-segmentations"

sv.SegmentationLegacyIO.Convert(file_name=file_name, output_dir=out_dir)

