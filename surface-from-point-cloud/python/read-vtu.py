import os
import sys
import vtk

file_name = 'shapeSnakeDiaSmooth_capped_mesh.vtu'

# Read in old format.
reader = vtk.vtkUnstructuredGridReader()
reader.SetFileName(file_name)
reader.Update()
mesh = reader.GetOutput()

## Print node coordinates.
#
num_points = mesh.GetNumberOfPoints()
points = mesh.GetPoints()
print("Number of points: {0:d}".format(num_points))
for i in range(0, num_points):
    point = mesh.GetPoint(i)
    print("Point {0:d}: {1:f}  {2:f}  {3:f} ".format(i, point[0], point[1], point[2]))

## Print cell connectivity.
#
num_cells = mesh.GetNumberOfCells()
print("Number of cells: {0:d}".format(num_cells))
cells = mesh.GetCells()
for cell_id in range(0, num_cells): 
    cell = mesh.GetCell(cell_id)
    dim = cell.GetCellDimension()
    cell_num_nodes = cell.GetNumberOfPoints()
    print("Cell: {0:d}".format(cell_id))
    print("    dim: {0:d}".format(dim))
    print("    cell_num_nodes: {0:d}".format(cell_num_nodes))
    for i in range(0, cell_num_nodes): 
        node_id = cell.GetPointId(i)
        print("    node id: {0:d}".format(node_id))
    #_for i in range(0, cell_num_nodes)
#_for cell_id in range(0, num_cells)
   
