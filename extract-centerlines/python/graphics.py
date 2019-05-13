#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Graphics(object):

    def __init__(self):
        self.renderer = None
        self.window = None
        self.interactor = None
        self.logger = logging.getLogger(get_logger_name())
        self.initialize_graphics()

    def create_graphics_geometry(self, poly_data, sphere=False):
        """ Create geometry for display.
        """
        mapper = vtk.vtkPolyDataMapper()
        if sphere:
            mapper.SetInputConnection(poly_data)
        else:
            mapper.SetInputData(poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    def initialize_graphics(self):
        """ Create renderer and graphics window.
        """
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.window.SetSize(1000, 1000)

        # Create a trackball interacter to transoform the geometry using the mouse.
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetRenderWindow(self.window)

        style = ClickInteractorStyle(self)
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

    def add_sphere(self, center, color):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(0.2)
        poly_data = sphere.GetOutputPort()
        self.add_graphics_geometry(poly_data, color, True)

    def add_graphics_geometry(self, poly_data, color, sphere=False):
        gr_geom = self.create_graphics_geometry(poly_data, sphere)
        gr_geom.GetProperty().SetColor(color[0], color[1], color[2])
        self.renderer.AddActor(gr_geom)
        self.window.Render()

    def show(self):
        self.interactor.Start()

class ClickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, graphics):
        self.graphics = graphics
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)

    def onKeyPressEvent(self, renderer, event):        
        key = self.GetInteractor().GetKeySym()
        if key == 'c':
            self.graphics.mesh.calculate_centerlines()



