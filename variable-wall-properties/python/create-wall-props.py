#!/usr/bin/env python

'''This script is used to create a 'wallproperty' point data array for a volume mesh.

   Usage:

       create-wall-props.py mesh-complete.mesh.vtu walls_combined.vtp

'''
import os
import sys
import vtk

def write_volume_mesh(mesh, file_name):
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

def read_volume_mesh(file_name):
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    return mesh

def read_surface_mesh(file_name):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    return mesh

def add_wall_property_array(volume_mesh, surface_mesh):
    num_vol_points = volume_mesh.GetNumberOfPoints()
    vol_points = volume_mesh.GetPoints()
    vol_point_ids = volume_mesh.GetPointData().GetArray("GlobalNodeID")
    print("Number of volume points: {0:d}".format(num_vol_points))

    xmin = ymin = zmin = 1e6
    xmax = ymax = zmax = -1e6

    for i in range(num_vol_points):
        point = vol_points.GetPoint(i)
        if point[0] < xmin: 
           xmin = point[0] 
        if point[0] > xmax: 
           xmax = point[0] 

        if point[1] < ymin: 
           ymin = point[1] 
        if point[1] > ymax: 
           ymax = point[1] 

        if point[2] < zmin: 
           zmin = point[2] 
        if point[2] > zmax: 
           zmax = point[2] 

    print("Volume mesh extent: ")
    print("  xmin: {0:g}  xmax: {1:g}".format(xmin, xmax))
    print("  ymin: {0:g}  ymax: {1:g}".format(ymin, ymax))
    print("  zmin: {0:g}  zmax: {1:g}".format(zmin, zmax))
    z_middle = (zmax + zmin) / 2.0

    num_surf_points = surface_mesh.GetNumberOfPoints()
    surf_points = surface_mesh.GetPoints()
    surf_point_ids = surface_mesh.GetPointData().GetArray("GlobalNodeID")
    print("Number of surface points: {0:d}".format(num_surf_points))

    node_id_map = set()
    for i in range(num_surf_points):
        nid = surf_point_ids.GetValue(i)
        node_id_map.add(nid)

    wall_property = vtk.vtkDoubleArray()
    wall_property.SetName("wallproperty")
    wall_property.SetNumberOfComponents(6)
    wall_property.SetNumberOfTuples(num_vol_points)

    n = 0
    for i in range(num_vol_points):
        nid = vol_point_ids.GetValue(i)
        point = vol_points.GetPoint(i)
        value = 6*[0.0]
        if nid in node_id_map:
            if point[2] > z_middle:
                value[0] = 0.115445 
                value[1] = 3.47979e+06
            else:
                value[0] = 0.271 
                value[1] = 1e+10
            n += 1
        wall_property.SetTuple(i, value)

    print("Added {0:d} wall prop values.".format(n))

    new_volume_mesh = vtk.vtkUnstructuredGrid()
    new_volume_mesh.DeepCopy(volume_mesh)
    new_volume_mesh.GetPointData().AddArray(wall_property)

    return new_volume_mesh 

if __name__ == '__main__':

    # Read volume mesh.
    file_name = sys.argv[1]
    volume_mesh = read_volume_mesh(file_name)

    # Read surface mesh.
    file_name = sys.argv[2]
    surface_mesh = read_surface_mesh(file_name)

    new_volume_mesh = add_wall_property_array(volume_mesh, surface_mesh)

    write_volume_mesh(new_volume_mesh, "wallprop.vtu")


