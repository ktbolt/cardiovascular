#!/usr/bin/env python
import os
import sys 
import SimpleITK as sitk

data_directory = "/home/davep/SimVascular/data/alex-dicom/00" 
data_directory = "/home/davep/software/itk/examples/python/out"

series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)

if not series_IDs:
    print("ERROR: given directory \""+data_directory+"\" does not contain a DICOM series.")
    sys.exit(1)

series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, series_IDs[0])
series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_names)

# Configure the reader to load all of the DICOM tags (public+private):
# By default tags are not loaded (saves time).
# By default if tags are loaded, the private tags are not loaded.
# We explicitly configure the reader to load tags, including the
# private ones.
series_reader.MetaDataDictionaryArrayUpdateOn()
series_reader.LoadPrivateTagsOn()
image3D = series_reader.Execute()

direction = image3D.GetDirection()
print("direction: {0:s}".format(str(direction))) 

