'''
This script is used to scale polydata around its center.

Usage:
    
    scale-polydata.py POLYDATA.vtp

        Writes scaled polydata to file named 'scaled_POLYDATA.vtp'
'''
import os
from pathlib import Path
import vtk
import sys

## Set some directory paths.
script_path = Path(os.path.realpath(__file__)).parent

## Read in the .vtp file.
#
file_name = sys.argv[1];  
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()
surface = reader.GetOutput()
points = surface.GetPoints()
num_points = surface.GetPoints().GetNumberOfPoints()
num_polys = surface.GetPolys().GetNumberOfCells()
print("Number of points: %d" % num_points)
print("Number of triangles: %d" % num_polys)

## Get the model center.
#
centerFilter = vtk.vtkCenterOfMass()
centerFilter.SetInputData(surface)
centerFilter.SetUseScalarsAsWeights(False)
centerFilter.Update()
center = centerFilter.GetCenter()

## Scale the model.
#
transform = vtk.vtkTransform()
transform.Translate(center[0], center[1], center[2])
scale_factor = 0.1
transform.Scale(scale_factor, scale_factor, scale_factor)
transform.Translate(-center[0], -center[1], -center[2])
transformFilter = vtk.vtkTransformFilter()
transformFilter.SetInputData(surface)
transformFilter.SetTransform(transform)
transformFilter.Update()

## Write the scaled model.
#
scaled_file_name = str(script_path / ("scaled_" + file_name))
print("Scaled file: {0:s}".format(scaled_file_name))
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(scaled_file_name)
writer.SetInputData(transformFilter.GetOutput())
writer.Update()
writer.Write()


