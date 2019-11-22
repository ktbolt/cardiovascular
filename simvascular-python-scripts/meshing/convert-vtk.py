
'''
This script is used to convert vtk files from old format to new. 
'''
import os
import sys
import vtk

reader = vtk.vtkDataSetReader()
reader.SetFileName("aorta-small-mesh.vtp")
reader.ReadAllScalarsOn()  
reader.Update()

writer = vtk.vtkXMLUnstructuredGridWriter()
writer.SetFileName("aorta-small-mesh-converted.vtu")
writer.SetInputData(reader.GetOutput())
writer.Update()
writer.Write()

