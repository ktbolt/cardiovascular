#!/usr/bin/env python

'''Convert a surface model defined in a .obj file into a model.vtp file. 

   The faces grouped by ID are converted into the 'ModelFaceID' cell array needed by SV.

   Usage:

     convert-obj.py OBJ_FILE
'''

import sys
import vtk

# Read .obj file.
file_name = sys.argv[1]
reader = vtk.vtkOBJReader()
reader.SetFileName(file_name)
reader.Update()
surface = reader.GetOutput()
num_cells = surface.GetNumberOfCells()

# Find face group IDs.
group_ids = surface.GetCellData().GetArray('GroupIds')
group_ids_range = 2*[0]
group_ids.GetRange(group_ids_range, 0)
min_id = int(group_ids_range[0])
max_id = int(group_ids_range[1])
print("Face IDs range: {0:d} {1:d}".format(min_id, max_id))

# Add ModelFaceID array.
face_ids = vtk.vtkIntArray()
face_ids.SetNumberOfValues(num_cells)
face_ids.SetName('ModelFaceID')

for i in range(num_cells):
  face_id = int(group_ids.GetValue(i)) + 1
  face_ids.SetValue(i, face_id)

surface.GetCellData().AddArray(face_ids)
surface.Modified()
surface.GetCellData().RemoveArray('GroupIds')

# Write vtp file.
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName("model.vtp");
writer.SetInputData(surface)
writer.Write()






