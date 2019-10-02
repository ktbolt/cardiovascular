#!/usr/bin/env python

"""
This script is an example of how to create a cylinder aligned with an axix.
"""

import math
import vtk
from vtk.util.colors import tomato

def create_cylinder(pt1, pt2, radius):
    """
    Create a cylinder aligned between two points.
    """

    ## Compute the cylinder axis and center.
    axis = [pt1[i] - pt2[i] for i in range(0,3)]
    length = vtk.vtkMath.Normalize(axis)
    center = [(pt1[i] + pt2[i])/2.0 for i in range(0,3)]

    cylinder = vtk.vtkCylinderSource()
    cylinder.SetCenter(0.0,0.0,0.0);
    cylinder.SetHeight(length);
    cylinder.SetRadius(radius);
    cylinder.SetResolution(32)
    cylinder.Update()

    # Set up transofrm to rotate given axis
    vec = [ 0.0, 1.0, 0.0 ]
    rotate_axis = 3*[0.0]
    tmp_cross = 3*[0.0]
    #print(tmp_cross)
    vtk.vtkMath.Cross(vec, axis, rotate_axis)
    vtk.vtkMath.Cross(vec, axis, tmp_cross)

    radangle = math.acos(vtk.vtkMath.Dot(axis,vec))
    #radangle = math.atan2(vtk.vtkMath.Norm(rotate_axis), vtk.vtkMath.Dot(axis,vec))
    degangle = vtk.vtkMath.DegreesFromRadians(radangle)

    # Transform
    transformer = vtk.vtkTransform()
    transformer.Translate(center[0], center[1], center[2])
    transformer.RotateWXYZ(degangle,rotate_axis)

    polyDataTransformer = vtk.vtkTransformPolyDataFilter()
    polyDataTransformer.SetInputData(cylinder.GetOutput())
    polyDataTransformer.SetTransform(transformer)
    polyDataTransformer.Update()
    return polyDataTransformer.GetOutput()


radius = 1.0

pt1 = [0.0, 0.0, 0.0]
pt2 = [10.0, 10.0, 0.0]

pt1 = [-0.138486, 1.017057, 0.335150]
pt2 = [-0.241842, 1.740550, -1.930475]

cylinder = create_cylinder( pt1, pt2, radius)

cylinderMapper = vtk.vtkPolyDataMapper()
cylinderMapper.SetInputData(cylinder)

cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.GetProperty().SetColor(tomato)
#cylinderActor.RotateX(30.0)
#cylinderActor.RotateY(-45.0)

sphere1 = vtk.vtkSphereSource()
sphere1.SetCenter(pt1[0], pt1[1], pt1[2])
sphere1.SetRadius(radius/10.0)
sphere1.SetThetaResolution(64)
sphere1.SetPhiResolution(64)
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(sphere1.GetOutputPort())
actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

sphere2 = vtk.vtkSphereSource()
sphere2.SetCenter(pt2[0], pt2[1], pt2[2])
sphere2.SetRadius(radius/10.0)
sphere2.SetThetaResolution(64)
sphere2.SetPhiResolution(64)
mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(sphere2.GetOutputPort())
actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
iren.SetRenderWindow(renWin)

ren.AddActor(cylinderActor)
ren.AddActor(actor1)
ren.AddActor(actor2)

ren.SetBackground(0.1, 0.2, 0.4)
renWin.SetSize(1000, 1000)

iren.Initialize()

#ren.ResetCamera()
#ren.GetActiveCamera().Zoom(1.5)

renWin.Render()

iren.Start()

