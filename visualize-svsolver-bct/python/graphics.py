#!/usr/bin/env python

import vtk
from math import sqrt
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Graphics(object):

    def __init__(self):
        self.renderer = None
        self.window = None
        self.interactor = None
        self.mesh = None
        self.time_step = 1
        self.arrow_actor = None
        self.velocity_scale = None
        self.initialize_graphics()

    def create_graphics_geometry(self, poly_data, sphere=False):
        ''' Create geometry for display.
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

    def initialize_graphics(self):
        ''' Create renderer and graphics window.
        '''
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(0.3, 0.5, 0.7)
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
        #gr_geom.GetProperty().SetOpacity(0.5)
        gr_geom.GetProperty().EdgeVisibilityOn();
        self.renderer.AddActor(gr_geom)
        self.window.Render()

    def show_velocity(self):
        time = self.mesh.velocity_data[self.time_step][0]
        mesh_velocity = self.mesh.velocity_data[self.time_step][1]
        surface = self.mesh.surface
        print("Show velocity at time step {0:d} time {1:s}".format(self.time_step, time))
        num_data = mesh_velocity.GetNumberOfTuples()
        #print("  Number of vectors: {0:d}".format(num_data))
        num_points = surface.GetNumberOfPoints()
        surf_points = surface.GetPoints()

        ## Copy velocity (not sure why I need to do this).
        velocity = vtk.vtkDoubleArray()
        velocity.SetName("velocity")
        velocity.SetNumberOfComponents(3)
        velocity.SetNumberOfTuples(num_points)
        for i in range(num_points):
            vel = mesh_velocity.GetTuple(i)
            velocity.SetTuple(i, vel)

        magnitude = vtk.vtkDoubleArray()
        magnitude.SetNumberOfValues(num_points)
        magnitude.SetName("magnitude")
        for i in range(num_points):
            vel = velocity.GetTuple(i)
            mag = sqrt(vel[0]*vel[0] + vel[1]*vel[1] + vel[2]*vel[2])
            magnitude.SetValue(i, mag)

        arrow_mesh = vtk.vtkPolyData()
        arrow_mesh.DeepCopy(surface)
        arrow_mesh.GetPointData().AddArray(velocity)
        arrow_mesh.GetPointData().SetActiveVectors("velocity")
        arrow_mesh.GetPointData().AddArray(magnitude)
        arrow_mesh.GetPointData().SetActiveScalars("magnitude")

        ## Create arrows.
        #
        arrow_source = vtk.vtkArrowSource()
        arrow_source.Update()
        #arrow_source.SetShaftRadius(1.0)
        #arrow_source.SetTipLength(.9)

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(arrow_mesh)
        glyph.SetSourceConnection(arrow_source.GetOutputPort())
        glyph.SetScaleFactor(self.velocity_scale)
        #glyph.SetScaleModeToScaleByScalar()
        #glyph.OrientOn()
        glyph.SetVectorModeToUseVector()
        glyph.SetColorModeToColorByScalar()
        glyph.Update()
  
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(glyph.GetOutput())
        actor = vtk.vtkActor()
        self.arrow_actor = actor
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        self.window.Render()

    def show(self):
        self.interactor.Start()

class ClickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, graphics):
        self.graphics = graphics
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)

    def onKeyPressEvent(self, renderer, event):        
        key = self.GetInteractor().GetKeySym()
        graphics = self.graphics
        #print(key)
        set_time = False

        if key in ["plus", "Up"]:
            graphics.time_step += 1
            set_time = True 
        elif key in ["minus", "Down"]:
            graphics.time_step -= 1
            set_time = True 

        if set_time:
            if graphics.time_step > graphics.mesh.num_time_steps:
                print("No more time steps")
                graphics.time_step = graphics.mesh.num_time_steps
            elif graphics.time_step < 1: 
                print("Time step is 1")
                graphics.time_step = 1 
            else:
                graphics.renderer.RemoveActor(graphics.arrow_actor)
                graphics.show_velocity()


