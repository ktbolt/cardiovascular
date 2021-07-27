#!/usr/bin/env python

from collections import defaultdict
from collections import deque 
import logging
from manage import get_logger_name
from math import cos
from math import pi as MATH_PI 
from os import path
import sys 
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
        '''Extract the surface faces.
        '''
        self.logger.info("---------- extract faces ---------- ")

        ## Compute edges separating cells by the angle set in 'self.params.angle'.
        #
        self.logger.info("Compute feature edges ...")
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

        ## Identify the cells incident on the feature edges.
        #
        self.logger.info("Identify edge cells ...")

        # Create a set of edge nodes.
        edge_nodes = set()
        for edge in self.boundary_edge_components:
            edge_num_points = edge.GetNumberOfPoints()
            edge_node_ids = edge.GetPointData().GetArray('GlobalNodeID')
            for i in range(edge_num_points):
                nid = edge_node_ids.GetValue(i)
                edge_nodes.add(nid)

        # Create a set of cell IDs incident to the edge nodes.
        surf_points = surface.GetPoints()
        num_cells = surface.GetNumberOfCells()
        surf_node_ids = surface.GetPointData().GetArray('GlobalNodeID')

        ''' 
        cell_mask = vtk.vtkIntArray()
        cell_mask.SetNumberOfValues(num_cells)
        cell_mask.SetName("CellMask")
        for i in range(num_cells):
            cell_mask.SetValue(i,0);
        surface.GetCellData().AddArray(cell_mask)
        '''
        edge_cell_ids = set()

        for i in range(num_cells):
            cell = surface.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            node_ids = [ surf_node_ids.GetValue(cell_pids.GetId(j)) for j in range(num_ids) ]
            for pid in node_ids:
                if pid in edge_nodes: 
                    #cell_mask.SetValue(i,1);
                    edge_cell_ids.add(i)
                    break

        '''
        thresh = vtk.vtkThreshold()
        thresh.SetInputData(surface)
        thresh.ThresholdBetween(1, 1)
        thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", "CellMask")
        thresh.Update()

        surfacefilter = vtk.vtkDataSetSurfaceFilter()
        surfacefilter.SetInputData(thresh.GetOutput())
        surfacefilter.Update()
        edge_cells = surfacefilter.GetOutput()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("edge_cells.vtp");
        writer.SetInputData(edge_cells)
        writer.Write()

        append_filter = vtk.vtkAppendPolyData()
        for i,edge in enumerate(self.boundary_edge_components):
            append_filter.AddInputData(edge)
        append_filter.Update()

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("edges.vtp");
        writer.SetInputData(append_filter.GetOutput())
        writer.Write()
        '''

        ## Traverse edge cells.
        #
        cell_visited = set()
        cell_normals = surface.GetCellData().GetArray('Normals')
        feature_angle = cos((MATH_PI/180.0) * self.params.angle)
        self.logger.info("feature_angle: {0:g}".format(feature_angle))
        #num_edge_cells = edge_cells.GetNumberOfCells()
        #self.logger.info("Number of edge cells: {0:d}".format(num_edge_cells))
        new_cells = deque()
        faces = defaultdict(list)
        face_id = 0
        self.logger.info("Traverse edge cells ...")

        for cell_id in edge_cell_ids:
            if cell_id in cell_visited:
                continue
            #self.logger.info("----- Edge cell ID: {0:d} -----".format(cell_id))
            self.add_new_cell(surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces[face_id])
            faces[face_id].append(cell_id)
            while len(new_cells) != 0:
              #self.logger.info("  new_cells: {0:s}".format(str(new_cells)))
              new_cell_id = new_cells.pop()
              if new_cell_id not in cell_visited:
                  faces[face_id].append(new_cell_id)
              self.add_new_cell(surface, cell_normals, edge_cell_ids, cell_visited, new_cell_id, new_cells, feature_angle, faces[face_id])
            face_id += 1

        self.logger.info("Number of cells visited: {0:d}".format(len(cell_visited)))
        self.logger.info("Number of faces: {0:d}".format(face_id))
        self.logger.info("Faces: ")
        faces_size = 0
        for face_id in faces:
            cell_list = faces[face_id]
            #self.logger.info("  Face ID: {0:d}  num cells: {1:d}".format(face_id, len(cell_list)))
            faces_size += len(cell_list)
        self.logger.info("Number of faces cells: {0:d}".format(faces_size))
        '''

        for face_id in faces:
            if face_id > 5:
                break;
            for i in range(num_cells):
                cell_mask.SetValue(i,0);
            cell_list = faces[face_id]
            for cell_id in cell_list: 
                cell_mask.SetValue(cell_id,1);
            thresh = vtk.vtkThreshold()
            thresh.SetInputData(surface)
            thresh.ThresholdBetween(1, 1)
            thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", "CellMask")
            thresh.Update()

            surfacefilter = vtk.vtkDataSetSurfaceFilter()
            surfacefilter.SetInputData(thresh.GetOutput())
            surfacefilter.Update()
            edge_cells = surfacefilter.GetOutput()

            writer = vtk.vtkXMLPolyDataWriter()
            writer.SetFileName("face_" + str(face_id) + ".vtp");
            writer.SetInputData(edge_cells)
            writer.Write()
        '''

    def add_new_cell(self, surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces):
        #self.logger.info("  add new cell: {0:d}".format(cell_id))
        #faces.append(cell_id)
        cell = surface.GetCell(cell_id)
        cell_visited.add(cell_id)
        num_edges = cell.GetNumberOfEdges()
        #self.logger.info("  num edges {0:d}".format(num_edges))
        cell_normal = [ cell_normals.GetComponent(cell_id,j) for j in range(3)]

        for i in range(num_edges):
            edge = cell.GetEdge(i)
            edge_ids = edge.GetPointIds()
            pid1 = edge_ids.GetId(0)
            pid2 = edge_ids.GetId(1)
            #self.logger.info("  edge {0:d} {1:d}".format(pid1, pid2))
            adj_cell_ids = vtk.vtkIdList()
            surface.GetCellEdgeNeighbors(cell_id, pid1, pid2, adj_cell_ids)

            for j in range(adj_cell_ids.GetNumberOfIds()):
                adj_cell_id = adj_cell_ids.GetId(j)
                if adj_cell_id not in cell_visited:
                    add_cell = True
                    if adj_cell_id in edge_cell_ids:
                        dp = sum([ cell_normal[k] * cell_normals.GetComponent(adj_cell_id,k) for k in range(3)] )
                        if dp < feature_angle:
                            #self.logger.info("  adj cell {0:d} is in separate face cell dp {1:g}".format(adj_cell_id, dp))
                            add_cell = False
                    if add_cell: 
                        new_cells.append(adj_cell_id)
                        cell_visited.add(cell_id)

        #self.logger.info("  new cells {0:s}".format(str(new_cells)))
        #for cell_id in new_cells:
        #    self.add_new_cell(surface, cell_visited, cell_id)


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

        self.surface.BuildLinks()
        self.extract_faces()

        #if self.params.use_feature_angle and self.params.angle != None:
        #    self.extract_faces()
        #else:
        #    self.extract_edges()

