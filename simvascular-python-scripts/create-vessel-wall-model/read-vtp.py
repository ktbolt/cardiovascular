import vtk


file_name = "/home/davep/software/ktbolt/cardiovascular/simvascular-python-scripts/create-vessel-wall-model/aorta-inner.vtp"

reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()

surface = reader.GetOutput()
num_points = surface.GetPoints().GetNumberOfPoints()
num_polys = surface.GetPolys().GetNumberOfCells()
print("Number of triangles: %d" % num_polys)

