'''Read in an STL file, clean it and write out an VTP file.
'''
import vtk

reader = vtk.vtkSTLReader()
reader.SetFileName('mesh_stl.stl')
reader.Update()
polydata = reader.GetOutput()

# Merge duplicate points, eliminate points that are not used in any cell, etc.
clean_filter = vtk.vtkCleanPolyData()
clean_filter.SetInputData(polydata)
clean_filter.Update();
cleaned_polydata = clean_filter.GetOutput()

# Remove duplicate faces.
remove_dupe_filter = vtk.vtkRemoveDuplicatePolys()
remove_dupe_filter.SetInputData(cleaned_polydata)
remove_dupe_filter.Update();

model = remove_dupe_filter.GetOutput()
model.BuildLinks()

# Translate the model to (0,0,0) and scale it.
com_filter = vtk.vtkCenterOfMass()
com_filter.SetInputData(model)
com_filter.Update()
center = com_filter.GetCenter()
print("Model center: {0:s}".format(str(center)))

scale = 10.0
transform = vtk.vtkTransform()
transform.Identity()
transform.Scale(scale, scale, scale)
transform.Translate(-center[0], -center[1], -center[2])
transform.Update()

transform_filter = vtk.vtkTransformFilter()
transform_filter.SetInputData(model)
transform_filter.SetTransform(transform)
transform_filter.Update()

model = transform_filter.GetOutput()
model.Modified()

writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName("mesh_stl.vtp")
writer.SetInputData(model)
writer.Update()
writer.Write()


