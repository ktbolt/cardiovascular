#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

from centerlines import Centerlines
from face import Face

class Mesh(object):

    def __init__(self, params):
        self.params = params
        self.surface = None
        self.centerlines = None
        self.surface_caps = None
        self.renderer = None
        self.window = None
        self.interactor = None
        self.logger = logging.getLogger(get_logger_name())
        self.initialize_graphics()

    def extract_caps(self):
        """ Extract the surface caps.
        """
        self.logger.info("---------- extract caps ---------- ")
        surface = self.surface
        face_ids = self.params.source_face_ids + self.params.target_face_ids
        self.logger.info("Face IDs: %s" % face_ids)

        surface.BuildLinks()
        boundary_regions = surface.GetCellData().GetScalars("ModelFaceID")
        self.logger.info("Extract caps ...")
        self.surface_caps = {}

        for faceID in face_ids:
            source = faceID in self.params.source_face_ids
            face = Face(faceID, surface, source)
            face.cell_ids = []
            self.surface_caps[faceID] = face 
            for cellID in range(surface.GetNumberOfCells()):
                if boundary_regions.GetValue(cellID) == faceID:
                    #self.logger.info("cellID: %d " % cellID)
                    face.cell_ids.append(cellID)
            #__for cellID in range(surface.GetNumberOfCells())
            self.logger.info("Face ID: %d   number of cells: %d   source: %s" % (faceID, len(face.cell_ids), str(source)))
        #__for faceID in face_ids

    def read_mesh(self):
        """ Read in a surface mesh.
        """
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(self.params.surface_file_name)
        reader.Update()
        self.surface = reader.GetOutput()
        num_points = self.surface.GetPoints().GetNumberOfPoints()
        self.logger.info("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        self.logger.info("Number of triangles: %d" % num_polys)
        self.extract_caps()
        self.add_graphics_geometry(self.surface, [0.8, 0.8, 0.8])

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

    def calculate_centerlines(self):
        self.logger.info("---------- calculate centerlines ----------")
        centerlines = Centerlines(self, self.params) 
        centerlines.extract_center_lines()

class ClickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, mesh):
        self.mesh = mesh
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)

    def onKeyPressEvent(self, renderer, event):        
        key = self.GetInteractor().GetKeySym()
        if key == 'c':
            self.mesh.calculate_centerlines()



