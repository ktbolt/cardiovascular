#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This script reads in an image from a VTI file, resets its origin and writes out a new image to new-origin.vti.

   Usage:

       python set-origin.py IMAGE.vti
'''

import sys
import vtk

file_name = sys.argv[1]
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(file_name)
reader.Update()
image = reader.GetOutput()

origin = image.GetOrigin()
print(f"Current image origin: {str(origin)}")

new_origin = [0.0, 0.0, 0.0]
image.SetOrigin(new_origin)

origin = image.GetOrigin()
print(f"New image origin: {str(origin)}")

writer = vtk.vtkXMLImageDataWriter()
writer.SetInputData(image)
writer.SetFileName("new-origin.vti")
writer.Write()

