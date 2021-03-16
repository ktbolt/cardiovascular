''' This script is used to identify cap faces for a POLYDATA model.

    Note: This is not completed.
'''
import sv
import sys
import vtk
import math
import numpy as np 

def classify_face(face_id, polydata):
    print("========== classify_face ==========")
    print("Face ID: " + str(face_id))
    points = polydata.GetPoints()
    num_points = points.GetNumberOfPoints()
    num_cells = polydata.GetNumberOfCells()
    print("Num points: " + str(num_points))

    cx = 0.0
    cy = 0.0
    cz = 0.0
    point = 3*[0.0]
    for i in range(num_points):
      points.GetPoint(i,point)
      cx += point[0]
      cy += point[1]
      cz += point[2]

    cx /= num_points
    cy /= num_points
    cz /= num_points
    com = [ cx, cy, cz ]

    csum = 3*[0.0]
    for i in range(num_points):
        points.GetPoint(i,point)
        csum[0] += point[0] - com[0]
        csum[1] += point[1] - com[1]
        csum[2] += point[2] - com[2]

    v0 = [0.0, 0.0, 0.0] 
    v1 = [0.0, 0.0, 0.0] 
    v2 = [0.0, 0.0, 0.0]
    var = [ v0, v1, v2 ]
    var = np.array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])

    for k in range(num_points):
        for i in range(3):
            for j in range(3):
                points.GetPoint(k,point)
                var[i][j] += (point[i] - com[i]) * (point[j] - com[j])

    for i in range(3):
        for j in range(3):
            var[i][j] = (var[i][j] - csum[i]*csum[j] / num_points) / (num_points-1)

    w, v = np.linalg.eig(var)
    print(w)
    print(v)

    min_val = 1e6
    min_vec = []

    for i in range(3):
        if w[i] < min_val:
            min_val = w[i]
            min_vec = v[:,i]

    print("Min eigenval: " + str(min_val))
    normal = min_vec
    print("Normal: " + str(normal))

    tol = 1e-4
    if min_val < tol:
        is_cap = True
    else:
        is_cap = False

    print("is_cap: " + str(is_cap))

    return com, normal, is_cap

## Create a modeler.
file_name = "demo.vtp"

## Classify faces using Python code.
#
'''
num_caps = 0
for face_id in face_ids:
    face_polydata = model.get_face_polydata(face_id=face_id)
    center, normal, is_cap = classify_face(face_id, face_polydata)
    if is_cap:
        num_caps += 1
print("Number of caps: " + str(num_caps))
'''


