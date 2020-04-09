#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk

file_name = '/Users/parkerda/SimVascular/DemoProject/Images/sample_data-cm.vti'
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(file_name)

# Create the mapper that creates graphics elements
mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Create the Actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
# show the edges of the image grid
actor.GetProperty().SetRepresentationToWireframe()
colors = vtk.vtkNamedColors()
actor.GetProperty().SetColor(colors.GetColor3d("DarkSalmon"))

# Create the Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.ResetCamera()
renderer.SetBackground(colors.GetColor3d("Silver"))

# Create the RendererWindow
renderer_window = vtk.vtkRenderWindow()
renderer_window.AddRenderer(renderer)

# Create the RendererWindowInteractor and display the vti file
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderer_window)
interactor.Initialize()
interactor.Start()

