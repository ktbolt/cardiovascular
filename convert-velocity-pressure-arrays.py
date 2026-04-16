#!/usr/bin/env python3

# This script is used to convert multiple 'velocity' and 'pressure' data arrays 
# in a VTU file to a single 'Pressure' and 'Velocity' arrays so it can be used 
# as initial state data for svMultiPhysics.
#
# All of the 'velocity', 'pressure', 'flow' and othe misc ROM 
# arrays will be removed.
# 
# Usage: 
#
#   convert-velocity-pressure-arrays.py FILE_NAME.vtu
#
# Output:
#
#   FILE_NAME-renamed.vtu

import os
import sys
import vtk

def add_point_data(mesh):
    '''Add the Velocity and Pressure data.'''
    num_points = mesh.GetNumberOfPoints()
    num_point_arrays = mesh.GetPointData().GetNumberOfArrays()
    print(f"[replace_point_data] num_point_arrays {num_point_arrays}")

    velocity_name = 'velocity'
    velocity_array_name = ''
    max_velocity_time = 0.0
    flow_name = 'flow'

    pressure_name = 'pressure'
    pressure_array_name = ''
    max_pressure_time = 0.0

    array_names_to_keep = ['GlobalNodeID', 'GlobalElementID']
    array_names_to_remove = []

    # Find the array names for the largest velocity and pressure
    # data arrays and create a list of array names to removed later.
    #
    for i in range(num_point_arrays):
        array_name = mesh.GetPointData().GetArrayName(i)
        if array_name == None:
            continue
        if velocity_name in array_name:
            tokens = array_name.split('_')
            time = float(tokens[1])
            if time > max_velocity_time:
                velocity_array_name = array_name
                max_velocity_time = time
            array_names_to_remove.append(array_name)
        elif pressure_name in array_name:
            tokens = array_name.split('_')
            time = float(tokens[1])
            if time > max_pressure_time:
                pressure_array_name = array_name
                max_pressure_time = time
            array_names_to_remove.append(array_name)
        elif flow_name in array_name:
            array_names_to_remove.append(array_name)
        elif array_name not in array_names_to_keep:
            array_names_to_remove.append(array_name)

    # Add Velocity data.
    print(f"[replace_point_data] Velocity array name {velocity_array_name}")
    new_velocity = vtk.vtkDoubleArray()
    new_velocity.SetNumberOfComponents(3)
    new_velocity.SetNumberOfTuples(num_points)
    new_velocity.SetName('Velocity')
    velocity_data = mesh.GetPointData().GetArray(velocity_array_name)
    for i in range(num_points):
        value = velocity_data.GetTuple(i)
        new_velocity.SetTuple(i, value)
    mesh.GetPointData().AddArray(new_velocity)
    mesh.Modified()

    # Add Pressure data.
    print(f"[replace_point_data] Pressure array name {pressure_array_name}")
    new_pressure = vtk.vtkDoubleArray()
    new_pressure.SetNumberOfValues(num_points)
    new_pressure.SetName('Pressure')
    pressure_data = mesh.GetPointData().GetArray(pressure_array_name)
    for i in range(num_points):
        value = pressure_data.GetValue(i)
        new_pressure.SetValue(i, value)
    mesh.GetPointData().AddArray(new_pressure)
    mesh.Modified()

    # Remove velocity, pressure, flow and other arrays.
    for i in range(len(array_names_to_remove)):
        array_name = array_names_to_remove[i]
        if array_name == None:
            continue
        mesh.GetPointData().RemoveArray(array_name)

    mesh.Modified()
    return mesh

if __name__ == '__main__':

    file_name = sys.argv[1];
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()

    # Remove velocity, pressure, flow and other arrays used
    # for ROM data.
    mesh = add_point_data(mesh)

    # Write new mesh file.
    file_name = file_base_name + "-converted.vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputData(mesh)
    writer.SetFileName(file_name)
    writer.Update()
    writer.Write()
    print(f"Converted file is {file_name}")

