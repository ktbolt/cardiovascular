
import os
import sys
import vtk

if __name__ == '__main__':

    file_name = sys.argv[1]
    file_base_name, ext = os.path.splitext(file_name)

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    polydata = reader.GetOutput()

    append_filter = vtk.vtkAppendFilter()
    append_filter.AddInputData(polydata)
    append_filter.Update()
    ugrid = append_filter.GetOutput()

    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputData(ugrid)
    writer.SetFileName(file_base_name + '.vtu')
    writer.Update()

