#!/usr/bin/env python

# This script is used to set face nodal coordinates to be equal to
# the volume mesh nodal coordinates.
#
# The original face.vtp file will be overwritten.

from os import path
import vtk
import os
import sys
from math import sqrt

def reset_nodes(vol_mesh, surf_mesh):
    num_vol_points = vol_mesh.GetNumberOfPoints()
    vol_points = vol_mesh.GetPoints()

    locator = vtk.vtkStaticPointLocator()
    locator.SetDataSet(vol_mesh)
    locator.BuildLocator()

    num_points = surf_mesh.GetNumberOfPoints()
    points = surf_mesh.GetPoints()
    pt1 = 3*[0.0]
    pt2 = 3*[0.0]

    new_points = vtk.vtkPoints()

    for i in range(num_points):
        points.GetPoint(i, pt1)
        #print("----- {0:d}  {1:s} -----".format(i+1, str(pt1)))
        min_d = 1e9
        min_i = -1
        min_pt = None

        closest_id = locator.FindClosestPoint(pt1)
        #print("closest_id: {0:d}".format(closest_id))

        pt2 = vol_points.GetPoint(closest_id)
        print("point: {0:s}".format(str(pt2)))
        diff = sqrt(sum((pt1[j] - pt2[j])*(pt1[j] - pt2[j]) for j in range(3)))
        #print("diff: {0:f}".format(diff))
        pid = new_points.InsertNextPoint(pt2)

    surf_mesh.SetPoints(new_points)
    surf_mesh.Modified()

def read_mesh(file_name):
  file_base_name, file_extension = path.splitext(file_name)
  reader = None
  is_vtp_file = True

  if file_extension == ".vtp":
    reader = vtk.vtkXMLPolyDataReader()
  elif file_extension == ".vtu":
    reader = vtk.vtkXMLUnstructuredGridReader()
    is_vtp_file = False

  reader.SetFileName(file_name)
  reader.Update()
  mesh = reader.GetOutput()

  return mesh, is_vtp_file

if __name__ == '__main__':

  file_name = sys.argv[1]
  vol_mesh,vtp_file = read_mesh(file_name)

  if vtp_file:
      print("The first mesh needs to be a VTU file.")
      sys.exit(0)

  file_name = sys.argv[2]
  surf_mesh,vtp_file = read_mesh(file_name)

  reset_nodes(vol_mesh, surf_mesh)

  writer = vtk.vtkXMLPolyDataWriter()
  writer.SetFileName(file_name)
  writer.SetInputData(surf_mesh)
  writer.Write()



