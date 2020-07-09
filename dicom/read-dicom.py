#!/usr/bin/env python
import os
import sys 
import SimpleITK as sitk

data_directory = "/home/davep/SimVascular/data/alex-dicom/00" 
data_directory = "/home/davep/software/itk/examples/python/out"
data_directory = "/Users/parkerda/SimVascular/erica-schwarz/data/8"

series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)

if not series_IDs:
    print("ERROR: given directory \""+data_directory+"\" does not contain a DICOM series.")
    sys.exit(1)

print("series_IDs: " + str(series_IDs))

series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, series_IDs[0])
series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_names)
#print("series_file_names: " + str(series_file_names))

# Configure the reader to load all of the DICOM tags (public+private):
series_reader.MetaDataDictionaryArrayUpdateOn()
series_reader.LoadPrivateTagsOn()
series_reader.ReadImageInformation()()
image3D = series_reader.Execute()

direction = image3D.GetDirection()
print("direction: {0:s}".format(str(direction))) 

for k in series_reader.GetMetaDataKeys():
    v = series_reader.GetMetaData(k)
    print("({0}) = = \"{1}\"".format(k, v))

