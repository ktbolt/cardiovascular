#!/usr/bin/env python

import logging
from manage import get_logger_name
import numpy as np
from os import path
from path import Path
import vtk

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, graphics):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("CharEvent", self.onCharEvent)
        self.graphics = graphics
        self.selected_points = []
        self.sphere = None

    def leftButtonPressEvent(self, obj, event):
        ''' 
        Process left mouse button press.
        '''
        print("leftButtonPressEvent: ")
        clickPos = self.GetInteractor().GetEventPosition()

        # vtk.vtkCellPicker() does not select path lines.
        #picker = vtk.vtkCellPicker()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        #picker.SetTolerance(0.0001)
        if picker.GetActor() == None:
            return

        position = picker.GetPickPosition()
        print("  position: " + str(position))

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
            self.graphics.add_actor(actor)
            self.sphere = sphere

        self.sphere.SetCenter(position[0], position[1], position[2])
        self.sphere.Update()

        ## Get path data at the selected point.
        for path in self.graphics.paths:
            path_data = path.select(position)
            print("  path data: ")
            print("    id: %s" %  path_data.id)
            print("    index: %d" %  path_data.index)
            print("    point: %s" %  str(path_data.point))
            print("    tangent: %s" %  str(path_data.tangent))
            print("    rotation: %s" %  str(path_data.rotation))

            # Show tangent.
            s = 1.0
            pt1 = path_data.point
            tangent = path_data.tangent
            tangent = np.array(path_data.tangent)
            pt2 = [(pt1[j]+s*tangent[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, width=5)

            # Show normal.
            normal = np.array(path_data.rotation)
            pt2 = [(pt1[j]+s*normal[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, color=[0.0,1.0,0.0], width=5)

            # Show binormal.
            binormal = np.cross(tangent, normal)
            pt2 = [(pt1[j]+s*binormal[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)

            self.graphics.image.extract_slice(pt1, tangent, normal, binormal)

        self.graphics.window.Render()

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
        self.image = None
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

    def add_line(self, pt1, pt2, color=[1.0, 1.0, 1.0], width=2):
        lineSource = vtk.vtkLineSource()
        lineSource.SetPoint1(pt1);
        lineSource.SetPoint2(pt2)
        lineSource.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(lineSource.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(width)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        self.add_actor(actor)

    def add_sphere(self, center, radius=1.0, color=[1.0,1.0,1.0]):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(radius)
        sphere.Update()
        polydata = sphere.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(color[0], color[1], color[2])
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


