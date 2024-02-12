#!/usr/bin/env python3

# This script is used to convert VTK VTP file 'ModelFaceID', 'CapID' and 'GlobalElementID' 
# Int64 Cell DataArrays to Int32 Cell DataArrays.
#
# Usage: 
#
#   convert-vtp-to-32.py FILE_NAME.vtp
#
# Output:
#
#   FILE_NAME-convertted.vtp

import os
import sys
import vtk

def replace_cell_data(polydata, data_name):
    ''' Replace the PolyData 'data_name' cell DataArray. 
    '''
    num_cells = polydata.GetNumberOfCells()

    old_data = polydata.GetCellData().GetArray(data_name)
    polydata.GetCellData().RemoveArray(data_name)

    new_data = vtk.vtkIntArray()
    new_data.SetNumberOfValues(num_cells)
    new_data.SetName(data_name)

    for i in range(num_cells):
        value = old_data.GetValue(i)
        new_data.SetValue(i, value)

    polydata.GetCellData().AddArray(new_data)

if __name__ == '__main__':

    file_name = sys.argv[1];
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    polydata = reader.GetOutput()

    # Replace cell arrays.
    #
    data_name = 'ModelFaceID'
    replace_cell_data(polydata, data_name)

    data_name = 'CapID'
    replace_cell_data(polydata, data_name)

    data_name = 'GlobalElementID'
    replace_cell_data(polydata, data_name)

    # Write new PolyData file.
    file_name = file_base_name + "-converted.vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(polydata)
    writer.SetFileName(file_name)
    writer.Update()
    writer.Write()


