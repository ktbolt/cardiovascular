#!/usr/bin/env python
'''Convert a DICOM image series into a VTK .vtk image file.

   Usage: 

     dicom-to-vtk.py DICOM_DIRECTORY

'''
import os
from pathlib import Path
import sys 
import SimpleITK as sitk

data_directory = sys.argv[1]
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)

if not series_IDs:
    print("ERROR: given directory \""+data_directory+"\" does not contain a DICOM series.")
    sys.exit(1)
print("DICOM series_IDs: " + str(series_IDs))

## Get the series file names.
#
series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, series_IDs[0])
series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_names)
print("Number of series file names: {0:d}".format(len(series_file_names)))

## Configure the reader to load all of the DICOM tags (public+private):
#
series_reader.MetaDataDictionaryArrayUpdateOn()
series_reader.LoadPrivateTagsOn()
image3D = series_reader.Execute()

## Write the .vtk file.
#
writer = sitk.ImageFileWriter()
writer.SetFileName("volume.vtk")
writer.Execute(image3D)

