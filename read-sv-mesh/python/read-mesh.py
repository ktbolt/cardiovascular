'''This script prints out information for a SimVascular mesh stored in a .vtu file.
'''
import os
import sys
import vtk

if __name__ == '__main__':

    # Read the mesh .vtu file.
    file_name = sys.argv[1]
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()

    # Print mesh nodal coordinates.
    num_points = mesh.GetNumberOfPoints()
    points = mesh.GetPoints()
    point_ids = mesh.GetPointData().GetArray("GlobalNodeID")
    print("Number of coordinates: {0:d}".format(num_points))

    print("Coordinates:  'Node ID' 'Node coordinates'")
    pt = 3*[0.0]
    for i in range(num_points): 
        point = points.GetPoint(i, pt)
        pid = point_ids.GetValue(i)
        print("{0:d} {1:s}".format(pid, str(pt)))

    num_cells = mesh.GetNumberOfCells()
    print("Number of elements: {0:d}".format(num_cells))
    cells = mesh.GetCells()
    element_ids = mesh.GetCellData().GetArray("GlobalElementID")

    print("Elements: 'Element ID'  'Element connectivity'")
    for i in range(num_cells): 
        cell = mesh.GetCell(i)
        elem_id = element_ids.GetValue(i)
        s = " "
        for j in range(4): 
            k = cell.GetPointId(j)
            nid = point_ids.GetValue(k)
            s += str(nid) + " "
        print("{0:d} {1:s}".format(elem_id, s))


