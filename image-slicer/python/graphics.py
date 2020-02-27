#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name
from math import sqrt 

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, graphics):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("CharEvent", self.onCharEvent)
        self.graphics = graphics
        self.selected_points = []
        self.sphere = None

    def leftButtonPressEvent(self, obj, event):
        """ 
        Process left mouse button press.
        """
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)

        position = picker.GetPickPosition()

        if self.sphere == None:
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(position[0], position[1], position[2])
            sphere.SetRadius(0.1)
            sphere.Update()
            polydata = sphere.GetOutput()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polydata)
            mapper.ScalarVisibilityOff()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetRepresentationToWireframe()
            actor.GetProperty().SetColor(0.0, 1.0, 0.0)
            self.renderer.AddActor(actor)

        cell_id = picker.GetCellId()

        print("###### cellid: " + str(cell_id))

        if cell_id == -1: 
            return

        return

    def onCharEvent(self, renderer, event):
        """
        Process an on char event.

        This is used to prevent passing the shortcut key 'w' to vtk which we use
        to write selected results and vtk uses to switch to wireframe display. 
        """
        key = self.GetInteractor().GetKeySym()
        if (key != 'w'):
            self.OnChar()
  
    def onKeyPressEvent(self, renderer, event):
        """
        Process a key press event.
        """
        key = self.GetInteractor().GetKeySym()

        if (key == 's'):
            self.leftButtonPressEvent(None, event)
        elif (key == 'f'):
            self.fix()

    #__def onKeyPressEvent

#__class MouseInteractorStyle

class Graphics(object):

    def __init__(self):
        self.renderer = None
        self.window = None
        self.interactor = None
        self.logger = logging.getLogger(get_logger_name())
        self.initialize_graphics()

    def add_actor(self, actor):
        self.renderer.AddActor(actor)

    def initialize_graphics(self):
        """ Create renderer and graphics window.
        """
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(0.5, 0.5, 0.5)
        self.window.SetSize(1000, 1000)
        #self.window.Render()

        # Create a trackball interacter to transoform the geometry using the mouse.
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetRenderWindow(self.window)

        # Add the custom style.
        style = MouseInteractorStyle(self)
        style.renderer = self.renderer
        style.graphics = self
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

    def add_sphere(self, center, color):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(0.0001)
        sphere.Update()
        polydata = sphere.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(0.0, 1.0, 0.0)
        self.renderer.AddActor(actor)

    def add_graphics_geometry(self, poly_data, color, sphere=False):
        gr_geom = self.create_graphics_geometry(poly_data, sphere)
        gr_geom.GetProperty().SetColor(color[0], color[1], color[2])
        #gr_geom.GetProperty().SetRepresentationToWireframe()
        gr_geom.GetProperty().SetEdgeColor(0.0, 0.0, 0.0)
        gr_geom.GetProperty().EdgeVisibilityOn()
        self.renderer.AddActor(gr_geom)
        self.window.Render()
        self.window.SetWindowName("Extract Faces")
        return gr_geom 

    def show(self):
        self.window.Render()
        self.window.SetWindowName("Image Slice")
        self.interactor.Start()

class ClickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, graphics):
        self.graphics = graphics
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)

    def onKeyPressEvent(self, renderer, event):        
        key = self.GetInteractor().GetKeySym()
        if key == 'c':
            pass 


