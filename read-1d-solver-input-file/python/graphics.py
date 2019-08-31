#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
from vtk.util.colors import tomato
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Graphics(object):

    def __init__(self):
        self.renderer = None
        self.window = None
        self.interactor = None
        self.colors = vtk.vtkNamedColors()
        self.logger = logging.getLogger(get_logger_name())
        self.initialize_graphics()

    def create_graphics_geometry(self, poly_data):
        """ Create geometry for display.
        """
        mapper = vtk.vtkPolyDataMapper()
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

    def add_cyl(self, pt1, pt2):
        cyl = vtk.vtkCylinderSource()
        cyl.SetRadius(0.2)
        cyl.SetResolution(15)
        x = [0,0,0]
        y = [0,0,0]
        z = [0,0,0]
        vtk.vtkMath.Subtract(pt2, pt1, x)
        length = vtk.vtkMath.Norm(x)
        vtk.vtkMath.Normalize(x)
        #print("length: " + str(length))

        arbitrary = [0,0,0]
        arbitrary[0] = vtk.vtkMath.Random(-10,10)
        arbitrary[1] = vtk.vtkMath.Random(-10,10)
        arbitrary[2] = vtk.vtkMath.Random(-10,10)
        vtk.vtkMath.Cross(x, arbitrary, z)
        vtk.vtkMath.Normalize(z)

        vtk.vtkMath.Cross(z, x, y)
        matrix = vtk.vtkMatrix4x4()
        matrix.Identity()

        for i in range(3):
            matrix.SetElement(i, 0, x[i])
            matrix.SetElement(i, 1, y[i])
            matrix.SetElement(i, 2, z[i])

        #print("x: " + str(x))
        #print("y: " + str(y))
        #print("z: " + str(z))

        transform = vtk.vtkTransform()
        transform.Translate(pt1) 
        transform.Concatenate(matrix); 
        transform.RotateZ(-90.0)      
        transform.Scale(1.0, length, 1.0)
        transform.Translate(0, 0.5, 0)  

        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(cyl.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()

        #mapper.SetInputConnection(transformPD.GetOutputPort())
        mapper.SetInputConnection(cyl.GetOutputPort())
        actor.SetUserMatrix(transform.GetMatrix())

        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)


        
        """
        sphereStartSource = vtk.vtkSphereSource()
        sphereStartSource.SetCenter(pt1)
        sphereStartMapper = vtk.vtkPolyDataMapper()
        sphereStartMapper.SetInputConnection(sphereStartSource.GetOutputPort())
        sphereStart = vtk.vtkActor()
        sphereStart.SetMapper(sphereStartMapper)
        sphereStart.GetProperty().SetColor(1.0, 1.0, .3)
        self.renderer.AddActor(sphereStart)

        sphereStartSource1 = vtk.vtkSphereSource()
        sphereStartSource1.SetCenter(pt2)
        sphereStartMapper1 = vtk.vtkPolyDataMapper()
        sphereStartMapper1.SetInputConnection(sphereStartSource1.GetOutputPort())
        sphereStart1 = vtk.vtkActor()
        sphereStart1.SetMapper(sphereStartMapper1)
        sphereStart1.GetProperty().SetColor(1.0, 1.0, .3)
        self.renderer.AddActor(sphereStart1)
        """


    def add_graphics_geometry(self, poly_data, color):
        gr_geom = self.create_graphics_geometry(poly_data)
        gr_geom.GetProperty().SetColor(color[0], color[1], color[2])
        gr_geom.GetProperty().SetPointSize(20)
        self.renderer.AddActor(gr_geom)
        self.window.Render()

    def add_graphics_points(self, poly_data, color):
        ball = vtk.vtkSphereSource()
        ball.SetRadius(0.2)
        ball.SetThetaResolution(12)
        ball.SetPhiResolution(12)
        balls = vtk.vtkGlyph3D()
        balls.SetInputData(poly_data)
        balls.SetSourceConnection(ball.GetOutputPort())

        mapBalls = vtk.vtkPolyDataMapper()
        mapBalls.SetInputConnection(balls.GetOutputPort())
        ballActor = vtk.vtkActor()
        ballActor.SetMapper(mapBalls)
        #ballActor.GetProperty().SetColor(tomato)
        #ballActor.GetProperty().SetColor([1.0, 1.0, 1.0])
        ballActor.GetProperty().SetSpecularColor(1, 1, 1)
        ballActor.GetProperty().SetSpecular(0.3)
        ballActor.GetProperty().SetSpecularPower(20)
        ballActor.GetProperty().SetAmbient(0.2)
        ballActor.GetProperty().SetDiffuse(0.8)
        self.renderer.AddActor(ballActor)

        """
        extract = vtk.vtkExtractEdges()
        extract.SetInputData(poly_data)
        extract.Update()
        num_edges = extract.GetOutput().GetNumberOfCells()
        print(">>> num edges:" + str(num_edges))
        tubes = vtk.vtkTubeFilter()
        tubes.SetInputConnection(extract.GetOutputPort())
        tubes.SetRadius(0.1)
        tubes.SetNumberOfSides(6)

        mapEdges = vtk.vtkPolyDataMapper()
        mapEdges.SetInputConnection(tubes.GetOutputPort())
        edgeActor = vtk.vtkActor()
        edgeActor.SetMapper(mapEdges)
        edgeActor.GetProperty().SetColor(self.colors.GetColor3d('peacock'))
        edgeActor.GetProperty().SetSpecularColor(1, 1, 1)
        edgeActor.GetProperty().SetSpecular(0.3)
        edgeActor.GetProperty().SetSpecularPower(20)
        edgeActor.GetProperty().SetAmbient(0.2)
        edgeActor.GetProperty().SetDiffuse(0.8)
        self.renderer.AddActor(edgeActor)
        """

        self.window.Render()

    def add_graphics_edges(self, poly_data, color):
        pt1 = [0,0,0]
        pt2 = [0,0,0]
        points = poly_data.GetPoints();
        """
        for i in range(points.GetNumberOfPoints()-1):
            points.GetPoint(i,pt1)
            points.GetPoint(i+1,pt2)
            self.add_cyl(pt1, pt2)
        """
        poly_data.GetLines().InitTraversal()
        idList = vtk.vtkIdList()
        while poly_data.GetLines().GetNextCell(idList):
            #print(">> Line has " + str(idList.GetNumberOfIds()) + " points." )
            node1 = idList.GetId(0)
            node2 = idList.GetId(1)
            points.GetPoint(node1,pt1)
            points.GetPoint(node2,pt2)
            self.add_cyl(pt1, pt2)
  

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



