#!/usr/bin/env python

'''This script is used to display the files associated with each series 
   defined for a group of DICOM files.

   This can be used to separate the DICOM files into individual directories by series. 
'''

import os
from pathlib import Path
import sys
import SimpleITK as sitk

data_directory = "./data"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
#print("DICOM series_IDs: " + str(series_IDs))

## Get the series file names.
#
for seriesID in series_IDs:
    print("---------- series {0:s} ---------- ".format(seriesID))
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, seriesID)
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    print("Number of series file names: {0:d}".format(len(series_file_names)))
    print("Series file names: ")
    for file_name in series_file_names:
        print("  file names: {0:s}".format(file_name))


