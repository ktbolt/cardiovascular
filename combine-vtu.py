#!/usr/bin/env python3

# This script is used to combine 'Velocity' data arrays from multiple  
# VTU files into a single VTU file.
#
# Usage:
#
#   combine-vtu.py PATH 
#
#   PATH: Path to the VTU files.
#
# Output:
#
#   results-combined.vtu in current directory

import glob
import os
import sys
import vtk
from pathlib import Path

def remove_arrays(mesh):
  '''Remove all data arrays from the mesh.
  '''
  array_names_to_keep = ['GlobalNodeID', 'GlobalElementID']

  point_data = mesh.GetPointData()
  if point_data:
    for i in range(point_data.GetNumberOfArrays() - 1, -1, -1):
      name = point_data.GetArrayName(i)
      if name and name not in array_names_to_keep:
        point_data.RemoveArray(name)

  cell_data = mesh.GetCellData()
  if cell_data:
    for i in range(cell_data.GetNumberOfArrays() - 1, -1, -1):
      name = cell_data.GetArrayName(i)
      if name and name not in array_names_to_keep:
        cell_data.RemoveArray(name)

  field_data = mesh.GetFieldData()
  if field_data:
    for i in range(field_data.GetNumberOfArrays() - 1, -1, -1):
      name = field_data.GetArrayName(i)
      field_data.RemoveArray(name)

  mesh.Modified()


def read_mesh(file_name):
    '''Read a mesh from a VTU file.'''
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    return mesh

def add_data(new_mesh, step_num, file_name):
    '''Add velocity data from a mesh to the new mesh.
    '''
    mesh = read_mesh(file_name)
    velocity = mesh.GetPointData().GetArray("Velocity")
    if not velocity:
      print(f"Mesh {file_name} does not contain data named 'Velocity'.")
      sys.exit(1)

    velocity.SetName('Velocity_'+str(step_num))
    new_mesh.GetPointData().AddArray(velocity)
    new_mesh.Modified()

def create_new_mesh(mesh, num_time_steps):
    '''Create a new mesh from 'mesh' with all data removed.
    '''
    new_mesh = vtk.vtkUnstructuredGrid()
    new_mesh.DeepCopy(mesh)

    remove_arrays(new_mesh)

    '''
    time_array = vtk.vtkDoubleArray()
    time_array.SetName("TimeValue")
    time_array.SetNumberOfTuples(num_time_steps)

    time = 0.0
    dt = 0.1
    for i in range(num_time_steps):
      time_array.SetValue(i, time)
      time ++ dt

    new_mesh.GetFieldData().AddArray(time_array)
    new_mesh.Modified()
    '''

    return new_mesh

if __name__ == '__main__':
    directory = Path(sys.argv[1])
    sorted_files = sorted(directory.glob("*.vtu"), key=lambda p: p.name)
    first_file = sorted_files[0]
    mesh = read_mesh(first_file)
    print(f'first files: {first_file}')

    num_time_steps = len(sorted_files)
    new_mesh = create_new_mesh(mesh, num_time_steps)

    step_num = 1
    for file_path in sorted_files:
        print(f"Reading file: {file_path}")
        add_data(new_mesh, step_num, file_path)
        step_num += 1

    # Write new mesh file.
    file_name = "results-combined.vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputData(new_mesh)
    writer.SetFileName(file_name)
    writer.Update()
    writer.Write() 
    print(f"Converted file is {file_name}")


