
import os
import sys
import vtk

if __name__ == '__main__':

    ## Read surface mesh.
    file_name = sys.argv[1]
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    surface = reader.GetOutput()

    model_face_id_data = surface.GetCellData().GetArray('ModelFaceID')
    face_ids_range = 2*[0]
    model_face_id_data.GetRange(face_ids_range, 0)
    min_id = int(face_ids_range[0])
    max_id = int(face_ids_range[1])
    print("Face IDs range: {0:d} {1:d}".format(min_id, max_id))

    face_ids = set()

    for i in range(0,surface.GetNumberOfPolys()):
      face_id = model_face_id_data.GetValue(i)
      face_ids.add(face_id)

    print("Face IDs: {0:s}".format(str(sorted(face_ids))))


