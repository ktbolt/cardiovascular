#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, graphics):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("CharEvent", self.onCharEvent)
        self.graphics = graphics

    def leftButtonPressEvent(self, obj, event):
        """ 
        Process left mouse button press.
        """
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)

        position = picker.GetPickPosition()
        cell_id = picker.GetCellId()

        if cell_id == -1: 
            return

        print(" ")
        print("Picked position: {0:f} {1:f} {2:f} ".format(position[0], position[1], position[2]))
        print("Cell id is: {0:d}".format(cell_id))

        self.graphics.add_sphere(position, [0.0, 1.0, 0.0])

        self.OnLeftButtonDown()
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

    #__def onKeyPressEvent

#__class MouseInteractorStyle

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
        mapper.ScalarVisibilityOff()
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

        # Add the custom style.
        style = MouseInteractorStyle(self)
        style.renderer = self.renderer
        style.graphics = self
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

    def add_sphere(self, center, color):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(0.001)
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

    def add_graphics_edges(self, boundary_edges, color):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(boundary_edges)
        actor = vtk.vtkActor()
        #actor.GetProperty().SetColor(color[0], color[1], color[2])
        actor.GetProperty().SetLineWidth(3.0)
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)

    def add_graphics_face_components(self, boundary_face_components, color):
        if boundary_face_components == None: 
            return
        for component in boundary_face_components:
            mapper = vtk.vtkPolyDataMapper()
            mapper.ScalarVisibilityOff()
            mapper.SetInputData(component)
            actor = vtk.vtkActor()
            if component.GetNumberOfCells() == 16:
                width = 3.0
                color[0] = 0.0
                color[1] = 0.8
                color[2] = 0.0
            elif component.GetNumberOfCells() < 3:
                width = 5.0
                color[0] = 1.0
                color[1] = 0.0
                color[2] = 0.0
            else:
                width = 3.0
                color[0] = 0.0
                color[1] = 0.0
                color[2] = 0.8
            actor.GetProperty().SetLineWidth(width)
            actor.GetProperty().SetColor(color[0], color[1], color[2])
            actor.SetMapper(mapper)
            self.renderer.AddActor(actor)

    def add_graphics_edge_components(self, boundary_edge_components, color):
        if boundary_edge_components == None: 
            return
        for component in boundary_edge_components: 
            mapper = vtk.vtkPolyDataMapper()
            mapper.ScalarVisibilityOff()
            mapper.SetInputData(component)
            actor = vtk.vtkActor()
            if component.GetNumberOfCells() == 16: 
                width = 3.0
                color[0] = 0.0
                color[1] = 1.0
                color[2] = 0.0
            elif component.GetNumberOfCells() == 3: 
                width = 5.0
                color[0] = 1.0
                color[1] = 0.0
                color[2] = 0.0
            else:
                width = 3.0
                color[0] = 0.0
                color[1] = 1.0
                color[2] = 0.8
            actor.GetProperty().SetLineWidth(width)
            actor.GetProperty().SetColor(color[0], color[1], color[2])
            actor.SetMapper(mapper)
            self.renderer.AddActor(actor)

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



