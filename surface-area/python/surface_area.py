'''Compute the surface area PolyData geometry.
'''
import sys 
import vtk

file_name = sys.argv[1]
print("File: {0:s}".format(file_name))

reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()
surface = reader.GetOutput()

mass_props = vtk.vtkMassProperties()
mass_props.SetInputData(surface)
mass_props.Update()
    
surf_area = mass_props.GetSurfaceArea()
print("Surface area: {0:f}".format(surf_area))

