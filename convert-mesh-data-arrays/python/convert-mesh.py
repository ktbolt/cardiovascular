#!/usr/bin/env python

'''This script converts the GlobalNodeID and GlobalElementID data arrys of a 
   .vtp or .vtu file to Int32 data arrays need by SV.  The new int arrays are 
   created and the modified mesh is written to a new file.
'''

from os import path
import vtk
import os
import sys
import xml.etree.ElementTree as et

if __name__ == '__main__':

    file_name = sys.argv[1]

    # Get data types.
    #
    data_types = {}
    doc = et.parse(file_name)
    for element in doc.iter('PolyData'):
        for data_element_t in element.iter('DataArray'):
            name = data_element_t.attrib['Name'] 
            dtype = data_element_t.attrib['type'] 
            #print("Name: {0:s}  type: {1:s}".format(str(name), dtype))
            data_types[name] = dtype
      
    # Read the mesh 
    #
    file_base_name, file_extension = path.splitext(file_name)
    reader = None

    if file_extension == ".vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif file_extension == ".vtu":
        reader = vtk.vtkXMLUnstructuredGridReader()

    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    num_points = mesh.GetNumberOfPoints()
    num_cells = mesh.GetNumberOfCells()

    # Check mesh GlobalNodeID data.
    #
    if data_types['GlobalNodeID'] != 'Int32':
        print("GlobalNodeID is a {0:s} array: convert to Int32.".format(data_types['GlobalNodeID']))
        node_ids = mesh.GetPointData().GetArray("GlobalNodeID")
        node_id = node_ids.GetValue(0)
        int_node_ids = vtk.vtkIntArray()
        int_node_ids.SetNumberOfValues(num_points)
        int_node_ids.SetName('GlobalNodeID')

        for i in range(num_points):
            node_id = int(node_ids.GetValue(i))
            int_node_ids.SetValue(i, node_id)

        mesh.GetPointData().RemoveArray('GlobalNodeID')
        mesh.GetPointData().AddArray(int_node_ids)
        mesh.Modified()
        mesh_modified = True

    # Check mesh GlobalElementID data.
    #
    if data_types['GlobalElementID'] != 'Int32':
        print("GlobalElementIDis a {0:s} array: convert to Int32.".format(data_types['GlobalElementID']))
        elem_ids = mesh.GetCellData().GetArray("GlobalElementID")
        int_elem_ids = vtk.vtkIntArray()
        int_elem_ids.SetNumberOfValues(num_cells)
        int_elem_ids.SetName('GlobalElementID')

        for i in range(num_cells):
            elem_id = int(elem_ids.GetValue(i))
            int_elem_ids.SetValue(i, elem_id)

        mesh.GetCellData().RemoveArray('GlobalElementID')
        mesh.GetCellData().AddArray(int_elem_ids)
        mesh.Modified()
        mesh_modified = True

    # Write a new mesh if that data has been modified.
    #
    if mesh_modified:
        if file_extension == ".vtp":
            writer = vtk.vtkXMLPolyDataWriter()
        elif file_extension == ".vtu":
            writer = vtk.vtkXMLUnstructuredGridWriter() 

        writer.SetFileName(file_base_name + "-modified" + file_extension)
        writer.SetInputData(mesh)
        writer.Write()

