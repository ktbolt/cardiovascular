#!/usr/bin/env python
''' Print the DICOM tags for a file.
'''
from __future__ import print_function

import SimpleITK as sitk
import sys

reader = sitk.ImageFileReader()
reader.SetFileName(sys.argv[1])
reader.LoadPrivateTagsOn()
reader.ReadImageInformation()

for k in reader.GetMetaDataKeys():
    v = reader.GetMetaData(k)
    print("({0}) = = \"{1}\"".format(k, v))
