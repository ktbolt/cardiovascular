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
        self.boundary_edge_components = list()
        edge_id = 0

        while True:
            conn_filter.AddSpecifiedRegion(edge_id)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            #print("{0:d}: Number of boundary lines: {1:d}".format(edge_id, component.GetNumberOfCells()))
            self.boundary_edge_components.append(component)
            conn_filter.DeleteSpecifiedRegion(edge_id)
            edge_id += 1

        self.logger.info("Number of edges: {0:d}".format(edge_id))
        edge_nodes = set()

        for edge in self.boundary_edge_components:
            #num_lines = edge.GetNumberOfCells()
            edge_num_points = edge.GetNumberOfPoints()
            #edge_points = edge.GetPoints()
            edge_node_ids = edge.GetPointData().GetArray('GlobalNodeID')

            for i in range(edge_num_points):
                nid = edge_node_ids.GetValue(i)
                edge_nodes.add(nid)

            '''
            for i in range(num_lines):
                cell = edge.GetCell(i)
                cell_pids = cell.GetPointIds()
                num_ids = cell_pids.GetNumberOfIds()
                pid1 = cell_pids.GetId(0)
                nid1 = edge_node_ids.GetValue(pid1)
                pid2 = cell_pids.GetId(1)
                nid2 = edge_node_ids.GetValue(pid2)
                #pt1 = edge_points.GetPoint(pid1)
                edge_nodes.add(nid1)
                edge_nodes.add(nid2)
                #print("id {0:d}  pt: {1:s}".format(pid1, str(pt1)))
                #print("id {0:d}  node_id: {1:d}".format(pid1, nid1))
            '''

        surf_points = surface.GetPoints()
        num_cells = surface.GetNumberOfCells()
        surf_node_ids = surface.GetPointData().GetArray('GlobalNodeID')

        cell_mask = vtk.vtkIntArray()
        cell_mask.SetNumberOfValues(num_cells)
        cell_mask.SetName("CellMask")
        for i in range(num_cells):
            cell_mask.SetValue(i,0);
        surface.GetCellData().AddArray(cell_mask)

        for i in range(num_cells):
            cell = surface.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            node_ids = [ surf_node_ids.GetValue(cell_pids.GetId(j)) for j in range(num_ids) ]
            for pid in node_ids:
                if pid in edge_nodes: 
                    cell_mask.SetValue(i,1);

        thresh = vtk.vtkThreshold()
        thresh.SetInputData(surface)
        thresh.ThresholdBetween(1, 1)
        thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", "CellMask")
        thresh.Update()

        surfacefilter = vtk.vtkDataSetSurfaceFilter()
        surfacefilter.SetInputData(thresh.GetOutput())
        surfacefilter.Update()
        geom = surfacefilter.GetOutput()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("edge_cells.vtp");
        writer.SetInputData(geom)
        writer.Write()


        append_filter = vtk.vtkAppendPolyData()
        for i,edge in enumerate(self.boundary_edge_components):
            append_filter.AddInputData(edge)
        append_filter.Update()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("edges.vtp");
        writer.SetInputData(append_filter.GetOutput())
        writer.Write()

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

        self.extract_faces()

        #if self.params.use_feature_angle and self.params.angle != None:
        #    self.extract_faces()
        #else:
        #    self.extract_edges()

