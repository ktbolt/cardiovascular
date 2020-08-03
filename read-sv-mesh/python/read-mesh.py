import os
import sys
import vtk

file_name = "cylinder.vtu"
file_name = "mesh-complete.mesh.vtu"
file_name = "mesh.vtu"
reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName(file_name)
reader.Update()
mesh = reader.GetOutput()

num_points = mesh.GetNumberOfPoints()
points = mesh.GetPoints()
point_ids = mesh.GetPointData().GetArray("GlobalNodeID")
print("Number of points: {0:d}".format(num_points))

num_cells = mesh.GetNumberOfCells()
print("Number of cells: {0:d}".format(num_cells))
cells = mesh.GetCells()

'''
for i in range(num_cells): 
    cell = mesh.GetCell(i)
    s = " "
    for j in range(4): 
        k = cell.GetPointId(j)
        nid = point_ids.GetValue(k)
        s += str(nid) + " "
    print("Cell {0:d} {1:s}".format(i, s))
'''

qualityFilter = vtk.vtkMeshQuality()
qualityFilter.SetInputData(mesh)
qualityFilter.SetTetQualityMeasureToVolume()
qualityFilter.Update()

qualityMesh = qualityFilter.GetOutput()
qualityArray = qualityMesh.GetCellData().GetArray("Quality")

for i in range(num_cells): 
    val = qualityArray.GetValue(i)
    print("Cell {0:d} {1:f}".format(i, val))




