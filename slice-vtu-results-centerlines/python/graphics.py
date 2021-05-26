#!/usr/bin/env python

from os import path
from math import sqrt 

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, pick_geometry=None, picking_keys=None, event_table=None):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("CharEvent", self.onCharEvent)
        self.graphics = None
        self.pick_geometry = pick_geometry
        self.event_table = event_table
        self.selected_point = None
        self.selected_node_id = None
        self.selected_cell_id = None
        self.picking_keys = picking_keys 
        self.picked_actor = None

    def select_event(self, key, obj, event):
        '''Process a select event. 
        '''
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        # picker = vtk.vtkCellPicker()
        #picker.SetTolerance(0.0005)
        #picker.SetTolerance(1.0)
        #picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        picker.Pick(clickPos[0], clickPos[1], 0, self.graphics.renderer)

        # Get selected geometry. 
        self.picked_actor = picker.GetActor()
        if self.picked_actor == None:
            #print("[select_event] No picked actor.")
            #self.OnLeftButtonDown()
            return
        position = picker.GetPickPosition()

        #cell_id = picker.GetCellId()
        #if cell_id == -1: 
        #    return

        print("select_event] ")
        print("select_event] Picked position: {0:g} {1:g} {2:g} ".format(position[0], position[1], position[2]))
        #print("select_event] Cell id is: {0:d}".format(cell_id))

        min_i = -1
        min_d = 1e5
        min_p = 3*[0.0]
        pick_geometry = self.pick_geometry
        points = pick_geometry.GetPoints()

        min_d = 1e6
        for i in range(points.GetNumberOfPoints()):
            p = 3*[0.0]
            points.GetPoint(i,p)
            dx = p[0] - position[0]
            dy = p[1] - position[1]
            dz = p[2] - position[2]
            d = sqrt(dx*dx + dy*dy + dz*dz)
            if d < min_d:
                min_d = d
                min_p[0] = p[0]
                min_p[1] = p[1]
                min_p[2] = p[2]
                min_i = i  

        print("[select_event] Picked node: {0:d} {1:g} {2:g} {3:g} ".format(min_i, min_p[0], min_p[1], min_p[2]))
        self.selected_node_id = min_i

        self.graphics.add_sphere(position, [1,1,0], radius=0.2, wire=True)
        #self.graphics.add_sphere(min_cell_pt1 , [1,1,0], radius=0.2, wire=True)
        #self.graphics.add_sphere(min_cell_pt2 , [1,0,0], radius=0.2, wire=False)

        ## Show picked point.
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(1)
        #points.SetPoint(0, cell_pick_pos[0], cell_pick_pos[1], cell_pick_pos[2])
        points.SetPoint(0, min_p[0], min_p[1], min_p[2])
        #points.SetPoint(0, position[0], position[1], position[2])
        geom = vtk.vtkPolyData()
        geom.SetPoints(points)
        glyphFilter = vtk.vtkVertexGlyphFilter()
        glyphFilter.SetInputData(geom)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyphFilter.GetOutputPort())
        actor = vtk.vtkActor()
        if key == 's':
            actor.GetProperty().SetColor(0.0, 1.0, 0.0)
        elif key == 't':
            actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        else:
            actor.GetProperty().SetColor(1.0, 1.0, 1.0)
        actor.GetProperty().SetPointSize(10)
        actor.SetMapper(mapper)
        self.graphics.renderer.AddActor(actor)

        #self.window.Render()

    def onKeyPressEvent(self, renderer, event):
        '''Process a key press event.
        '''
        key = self.GetInteractor().GetKeySym()

        if key == 'u' and len(self.method_queue) != 0:
            last_method = self.method_queue.pop()
            last_method(undo=True) 
            last_actor = self.pick_glyph_actor_queue.pop()
            last_actor.SetVisibility(False)

        if (key in self.picking_keys):
            self.select_event(key, None, event)

        if self.event_table == None:
            return

        if (key in self.event_table):
            value = self.event_table[key]
            if type(value) == tuple:
                method = value[0]
                data = value[1]
            else:
                method = value
                data = None

            # Call the method with selected node/cell and any data.
            method(pick_geometry=self.pick_geometry, node_id=self.selected_node_id, cell_id=self.selected_cell_id, data=data, 
                   graphics=self.graphics)

        self.graphics.window.Render()

    def onCharEvent(self, renderer, event):
        '''Process an on char event.

        This is used to prevent passing the shortcut key 'w' to vtk which we use
        to write selected results and vtk uses to switch to wireframe display. 
        '''
        key = self.GetInteractor().GetKeySym()
        if (key != 'w'):
            self.OnChar()

class Graphics(object):

    def __init__(self, width=1000, height=1000):
        self.window = None
        self.renderer = None
        self.interactor = None
        self.pick_face = None
        self.face_actors = {}
        self.initialize_graphics(width, height)

    def init_picking(self, pick_geometry, picking_keys, event_table=None):

        # Create a trackball interacter to transoform the geometry using the mouse.
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        interactor.SetRenderWindow(self.window)
        self.interactor = interactor 

        # Add the custom style.
        style = MouseInteractorStyle(pick_geometry, picking_keys, event_table)
        style.graphics = self
        interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

    def create_graphics_geometry(self, poly_data, sphere=False):
        '''Create geometry for display.
        '''
        mapper = vtk.vtkPolyDataMapper()
        if sphere:
            mapper.SetInputConnection(poly_data)
        else:
            mapper.SetInputData(poly_data)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    def initialize_graphics(self, width=500, height=500):
        ''' Create renderer and graphics window.
        '''
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(0.8, 0.8, 0.8)
        self.window.SetSize(width, height)

        # Create a trackball interacter to transoform the geometry using the mouse.
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetRenderWindow(self.window)

        # Add the custom style.
        '''
        style = MouseInteractorStyle(self)
        style.renderer = self.renderer
        style.graphics = self
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)
        '''

    def add_sphere(self, center, color, radius=1.0, wire=False):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(radius)
        sphere.SetPhiResolution(16)
        sphere.SetThetaResolution(16)
        sphere.Update()

        polydata = sphere.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if wire:
            actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(0.5)
        self.renderer.AddActor(actor)

    def add_line(self, pt1, pt2, color=[1.0, 1.0, 1.0], width=2):
        line = vtk.vtkLineSource()
        line.SetPoint1(pt1);
        line.SetPoint2(pt2)
        line.Update()
        polydata = line.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        actor.GetProperty().SetLineWidth(width)
        self.renderer.AddActor(actor)

    def add_geometry(self, poly_data, color, wire=False, edges=False, sphere=False, line_width=1.0):
        gr_geom = self.create_graphics_geometry(poly_data, sphere)
        gr_geom.GetProperty().SetColor(color[0], color[1], color[2])

        if wire:
            gr_geom.GetProperty().SetRepresentationToWireframe()
            gr_geom.GetProperty().SetLineWidth(1.0)
        else:
            gr_geom.GetProperty().SetLineWidth(line_width)

        if edges:
            gr_geom.GetProperty().EdgeVisibilityOn();

        #gr_geom.GetProperty().SetRepresentationToWireframe()
        #gr_geom.GetProperty().SetEdgeColor(0.0, 0.0, 0.0)
        #gr_geom.GetProperty().EdgeVisibilityOn()
        self.renderer.AddActor(gr_geom)
        self.window.Render()
        self.window.SetWindowName("Explore Model")
        return gr_geom 

    def show(self):
        self.interactor.Start()


