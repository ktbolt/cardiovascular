#!/usr/bin/env python
import os
from pathlib import Path
import sys 
import SimpleITK as sitk

home = str(Path.home())
data_directory = home+"/SimVascular/data/OSMSC0005-pulmonary/image_data/volume/"

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
#series_reader.ReadImageInformation()()
image3D = series_reader.Execute()
print(type(image3D))

direction = image3D.GetDirection()
print("direction: {0:s}".format(str(direction))) 

writer = sitk.ImageFileWriter()
writer.SetFileName("volume.vtk")
writer.Execute(image3D)

'''
for k in series_reader.GetMetaDataKeys():
    v = series_reader.GetMetaData(k)
    print("({0}) = = \"{1}\"".format(k, v))
'''

