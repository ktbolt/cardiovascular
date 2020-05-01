from writeStenosisFile import writeStenosisFile

# Stenosis levels (by area) to write out
stenosis = [0.9,0.75,0.5,0.25,0.1];

# Filename of segmentation group you want to add stenosis to (omit .ctgr suffix)
filename_prefix = "PT1_6M/Segmentations/SVC"

# Contour number in the segmentation group you want to add stenosis to
contourGroup = 9

for st in stenosis:
    writeStenosisFile(filename_prefix, contourGroup, st)
