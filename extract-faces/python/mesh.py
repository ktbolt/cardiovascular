#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

try:
    from vmtk import vtkvmtk,vmtkscripts
except ImportError:
    print("vmtk not found.")

from face import Face

class Mesh(object):

    def __init__(self, params):
        self.params = params
        self.surface = None
        self.surface_caps = None
        self.graphics = None
        self.boundary_faces = None
        self.boundary_edges = None
        self.boundary_edge_components = None
        self.boundary_face_components = None
        self.logger = logging.getLogger(get_logger_name())

    def extract_faces(self):
        """ Extract the surface faces.
        """
        self.logger.info("---------- extract faces ---------- ")
        surface = self.surface
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOff();
        feature_edges.ManifoldEdgesOff();
        feature_edges.NonManifoldEdgesOff();
        feature_edges.FeatureEdgesOn();
        feature_edges.SetFeatureAngle(self.params.angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        self.boundary_face_components = list()
        id = 0

        while True:
            conn_filter.AddSpecifiedRegion(id)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            print("{0:d}: Number of boundary lines: {1:d}".format(id, component.GetNumberOfCells()))
            self.boundary_face_components.append(component)
            conn_filter.DeleteSpecifiedRegion(id)
            id += 1


    def extract_edges(self):
        """ Extract the surface boundary edges.
        """
        self.logger.info("---------- extract edges ---------- ")
        surface = self.surface
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOn()
        feature_edges.FeatureEdgesOff()
        feature_edges.ManifoldEdgesOff()
        feature_edges.NonManifoldEdgesOff()
        feature_edges.ColoringOn()
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData() 
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update(); 
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        self.boundary_edge_components = list()
        id = 0

        while True:
            conn_filter.AddSpecifiedRegion(id)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            print("{0:d}: Number of boundary lines: {1:d}".format(id, component.GetNumberOfCells()))
            self.boundary_edge_components.append(component)
            conn_filter.DeleteSpecifiedRegion(id)
            id += 1

        self.boundary_edges = cleaned_edges
        #self.boundary_edges = feature_edges.GetOutput()
        self.boundary_edges.BuildLinks()
        #print(str(self.boundary_edges))

 
    def read_mesh(self):
        """ Read in a surface mesh.
        """
        filename, file_extension = path.splitext(self.params.surface_file_name)
        reader = None
        if file_extension == ".vtp":
            reader = vtk.vtkXMLPolyDataReader()
        elif file_extension == ".stl":
            reader = vtk.vtkSTLReader()
        reader.SetFileName(self.params.surface_file_name)
        reader.Update()
        self.surface = reader.GetOutput()
        num_points = self.surface.GetPoints().GetNumberOfPoints()
        self.logger.info("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        self.logger.info("Number of triangles: %d" % num_polys)

        if self.params.use_feature_angle and self.params.angle != None:
            self.extract_faces()
        else:
            self.extract_edges()

