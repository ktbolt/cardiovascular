#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name
from math import sqrt
import random

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

try:
    from vmtk import vtkvmtk,vmtkscripts
except ImportError:
    print("vmtk not found.")

from face import Face

class VtkDataNames(object):
    GlobalElementID = "GlobalElementID"
    ModelRegionID = "ModelRegionID"
    ModelFaceID = "ModelFaceID"

class Mesh(object):

    def __init__(self, params):
        self.params = params
        self.surface = None
        self.center = None
        self.mesh_from_vtp = None 
        self.graphics = None
        self.boundary_faces = None
        self.boundary_edges = None
        self.boundary_edge_components = None
        self.boundary_face_components = None
        self.hue_lut = None 
        self.area_list = None 
        self.non_manifold_components = {}
        self.scalar_range = None 
        self.logger = logging.getLogger(get_logger_name())

    def create_hue_lut(self, scalar_range):
        '''create a lookup table that consists of the full hue circle (from HSV).
        '''
        vmin = scalar_range[0]
        vmax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(vmin, vmax)
        table.SetHueRange(0, 1)
        table.SetSaturationRange(1, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.hue_lut = table

    def check_area(self, tol=1e-4):
        print("[checl_ara] ---------- check area ---------- ")
        print("[check_area] tolerace: {0:g}".format(tol))
        max_area = -1e9
        min_area = 1e9
        avg_area = 0.0
        points = self.surface.GetPoints()
        num_cells = self.surface.GetNumberOfCells()

        area_property = vtk.vtkDoubleArray()
        area_property.SetName("cell_area")
        area_property.SetNumberOfComponents(1)
        area_property.SetNumberOfTuples(num_cells)
        self.failed_area_check_list = []
        num_failed_check = 0

        for i in range(num_cells):
            cell = self.surface.GetCell(i)
            dim = cell.GetCellDimension()
            num_cell_nodes = cell.GetNumberOfPoints()
            #print("Cell: {0:d}".format(cell_id))
            #print("    dim: {0:d}".format(dim))
            #print("    cell_num_nodes: {0:d}".format(num_cell_nodes))
            tri = vtk.vtkTriangle()
            tri_points = []
            center = [0.0, 0.0, 0.0]
            for j in range(0, num_cell_nodes):
                node_id = cell.GetPointId(j)
                pt = points.GetPoint(node_id)
                tri_points.append(pt)
                center[0] += pt[0]
                center[1] += pt[1]
                center[2] += pt[2]
            area = vtk.vtkTriangle.TriangleArea(tri_points[0], tri_points[1], tri_points[2])
            center[0] /= 3.0
            center[1] /= 3.0
            center[2] /= 3.0

            #area = tri.ComputeArea()            
            if area < min_area:
                min_area = area
            if area > max_area:
                max_area = area
            if area < tol:
                area_property.SetValue(i, 0.0)
                self.failed_area_check_list.append(center)
                num_failed_check += 1
                print("[check_area] area {0:g} < tolerance".format(area))
            else:
                area_property.SetValue(i, area)
            avg_area += area

        avg_area /= num_cells 
        print("[check_area] Max area: {0:g}".format(max_area))
        print("[check_area] Min area: {0:g}".format(min_area))
        print("[check_area] Avg area: {0:g}".format(avg_area))
        print("[check_area] Number of surface trangles < tolerance: {0:d}".format(num_failed_check))

        self.avg_area = avg_area 
        self.max_area = max_area 
        self.surface.GetCellData().AddArray(area_property)
        self.scalar_range = [min_area, max_area]
        self.create_hue_lut( self.scalar_range ) 

        threshold = vtk.vtkThreshold()
        threshold.SetInputData(self.surface)
        threshold.SetInputArrayToProcess(0,0,0,1,'cell_area')
        threshold.ThresholdBetween(0.0,0.0)
        threshold.Update();

        surfacer = vtk.vtkDataSetSurfaceFilter()
        surfacer.SetInputData(threshold.GetOutput())
        surfacer.Update()
        self.area_surface = surfacer.GetOutput()

    def extract_faces(self):
        '''Extract the surface faces using an angle between faces.

          [TODO:DaveP] This is not finished.
        '''
        self.logger.info("========== extract faces ========== ")
        angle = self.params.angle
        surface = self.surface
        self.logger.info("Angle: {0:f}".format(angle))

        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOff();
        feature_edges.ManifoldEdgesOff();
        feature_edges.NonManifoldEdgesOff();
        feature_edges.FeatureEdgesOn();
        feature_edges.SetFeatureAngle(angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()

        self.boundary_face_components = {}
        self.boundary_faces = {}

        rid = 0
        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            #print("{0:d}: Number of boundary lines: {1:d}".format(rid, component.GetNumberOfCells()))
            self.boundary_face_components[rid] = component
            self.boundary_faces[rid] = Face(rid, component)
            #self.boundary_face_components[rid] = component
            conn_filter.DeleteSpecifiedRegion(rid)
            rid += 1

        self.logger.info("Number of connected edges: {0:d}".format(rid))

    #_extract_faces(self):

    def extract_nonmanifold_edges(self):
        self.logger.info("========== extract_nonmanifold_edges ========== ")
        angle = self.params.angle
        surface = self.surface
        self.logger.info("Angle: {0:f}".format(angle))

        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOff();
        feature_edges.ManifoldEdgesOff();
        feature_edges.NonManifoldEdgesOn();
        feature_edges.FeatureEdgesOff();
        feature_edges.SetFeatureAngle(angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        if cleaned_edges.GetNumberOfCells() == 0: 
            self.logger.info("Number of non-manifold edges: {0:d}".format(0))
            return

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()

        self.non_manifold_components = {}

        rid = 0
        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            print("{0:d}: Number of lines: {1:d}".format(rid, component.GetNumberOfCells()))
            if component.GetNumberOfCells() <= 0:
                break
            self.non_manifold_components[rid] = component
            conn_filter.DeleteSpecifiedRegion(rid)
            rid += 1

        self.logger.info("Number of non-manifold edges: {0:d}".format(rid))

    def get_surface_faces(self):
        '''Get the faces from the surface mesh using the ModelFaceID data array.
     
           The faces are vtkPolyData objects with cell data arrays.
        '''
        self.logger.info("========== get_surface_faces ==========")
        face_ids = self.surface.GetCellData().GetArray(VtkDataNames.ModelFaceID)
        if face_ids == None:
            self.logger.error("No ModelFaceID data.")
            return;
        face_ids_range = 2*[0]
        face_ids.GetRange(face_ids_range, 0)
        min_id = int(face_ids_range[0])
        max_id = int(face_ids_range[1])
        self.logger.info("Face IDs range: {0:d} {1:d}".format(min_id, max_id))

        ## Extract face geometry.
        #
        mesh_faces = {}

        for i in range(min_id, max_id+1):
            #print("[Mesh.get_surface_faces] ---------- ID {0:d} ---------".format(i))
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(self.surface)
            threshold.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelFaceID)
            threshold.ThresholdBetween(i,i)
            threshold.Update();

            surfacer = vtk.vtkDataSetSurfaceFilter()
            surfacer.SetInputData(threshold.GetOutput())
            surfacer.Update()
            mesh_faces[i] = Face(i, surfacer.GetOutput())
            #print("Mesh.[get_surface_faces] Face number of points: %d" % mesh_faces[i].GetNumberOfPoints())
            #print("Mesh.[get_surface_faces] Face number of cells: %d" % mesh_faces[i].GetNumberOfCells())
            #write_surface_mesh("surface", mesh_faces[i], str(i))
        #_for i in range(min_id, max_id+1)

        self.boundary_faces = mesh_faces
        center = [0.0,0.0,0.0]
        total_num_pts = 0
        for fid,face in self.boundary_faces.items():
            npts = face.surface.GetNumberOfPoints()
            ncells = face.surface.GetNumberOfCells()
            self.logger.info("  id:{0:d} num cells: {1:d}".format(face.model_face_id, ncells))
            for i in range(0, npts):
                point = face.surface.GetPoint(i)
                center[0] += point[0]
                center[1] += point[1]
                center[2] += point[2]
            total_num_pts += npts 
        center[0] /= total_num_pts 
        center[1] /= total_num_pts
        center[2] /= total_num_pts
        self.center = center

    def show_edges(self):
        self.logger.info("========== show_edges ==========")
        for rid,edge in self.boundary_edges.items():
            self.logger.info("rid: {0:d}".format(rid))
            color = []
            if rid == 0:
                color = [0,1,1]
            else:
                color = [1,1,0]
            self.graphics.add_graphics_geometry(edge, color, line_width=4.0)

    def show_nonmanifold_edges(self):
        self.logger.info("========== show_nonmanifold_edges ==========")
        for rid,edge in self.non_manifold_components.items():
            self.logger.info("rid: {0:d}".format(rid))
            self.graphics.add_graphics_geometry(edge, [1.0,0.0,1.0], line_width=8.0)

    def show_faces(self):
        self.logger.info("========== show_faces ==========")
        self.logger.info("Number of faces: {0:d}".format(len(self.boundary_faces)))
        num_faces = len(self.boundary_faces)
        max_face = None
        max_ncells = 0

        for fid,face in self.boundary_faces.items():
            ncells = face.surface.GetNumberOfCells()
            if ncells > max_ncells:
                max_ncells = ncells
                max_face = face

        for fid,face in self.boundary_faces.items():
            self.logger.info("Face {0:d}".format(fid))
            npts = face.surface.GetNumberOfPoints()
            ncells = face.surface.GetNumberOfCells()
            self.logger.info("  id:{0:d} num cells: {1:d}".format(face.model_face_id, ncells))
            if ncells == 0:
                continue
            if face == max_face:
                color = [0.8, 0.8, 0.8]
            else:
                color = [1.0, 0.0, 0.0]
            actor = self.graphics.add_graphics_geometry(face.surface, color)
            #self.graphics.face_actors[fid] = (actor, color)
            center = face.get_center()
            area = face.get_area()
            self.logger.info("  area: {0:g}".format(area))
            color = [1,1,1]
            radius = 0.25
            if ncells == 1:
                color = [1,1,0]
                actor = self.graphics.add_sphere(center, color, radius)

    def filter_faces(self, min_num_cells):
        self.logger.info("========== filter_faces ==========")
        self.logger.info("Number of faces: {0:d}".format(len(self.boundary_faces)))
        self.logger.info("min_num_cells: {0:d}".format(min_num_cells))
        for fid,face in self.boundary_faces.items():
            npts = face.surface.GetNumberOfPoints()
            ncells = face.surface.GetNumberOfCells()
            if ncells > min_num_cells:
                continue
            self.logger.info("  id:{0:d} num cells: {1:d}".format(face.model_face_id, ncells))
            self.graphics.add_graphics_geometry(face.surface, [1.0,0.0,0.0])
            points = face.surface.GetPoints()
            center = [0.0,0.0,0.0]
            num_pts = face.surface.GetNumberOfPoints()
            for i in range(0, num_pts):
                point = face.surface.GetPoint(i)
                center[0] += point[0]
                center[1] += point[1]
                center[2] += point[2]
            center[0] /= num_pts 
            center[1] /= num_pts
            center[2] /= num_pts
            dx = 0.0
            dy = 0.0
            dz = 0.0
            max_r = 0.0
            for i in range(0, num_pts):
                point = face.surface.GetPoint(i)
                dx = point[0] - center[0]
                dy = point[1] - center[1]
                dz = point[2] - center[2]
                d = sqrt(dx*dx + dy*dy + dz*dz)
                if d > max_r:
                    max_r = d
            self.logger.info("  max_r:{0:f} ".format(max_r))
            self.graphics.add_sphere(center, [0.0, 1.0, 0.0], radius=max_r)
            self.graphics.add_sphere(center, [1.0, 0.0, 0.0], radius=1000.0*max_r)
            self.graphics.add_line(self.center, center, color=[1.0, 0.0, 0.0], width=4)
            pto = [2.0*center[i] - self.center[i] for i in range(3) ]
            self.graphics.add_line(pto, center, color=[0.0, 1.0, 0.0], width=4)
  
    def extract_edges(self):
        ''' Extract the surface boundary edges.
        '''
        self.logger.info("========== extract edges ========== ")
        angle = 50.0
        surface = self.surface
        self.logger.info("Angle: {0:f}".format(angle))

        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(surface)
        feature_edges.BoundaryEdgesOff();
        feature_edges.ManifoldEdgesOff();
        feature_edges.NonManifoldEdgesOff();
        feature_edges.FeatureEdgesOn();
        feature_edges.SetFeatureAngle(angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()

        self.boundary_edges = {}
        rid = 0
        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            print("{0:d}: Number of edge points: {1:d}".format(rid, component.GetNumberOfCells()))
            if component.GetNumberOfCells() <= 0:
                break
            self.boundary_edges[rid] = component
            conn_filter.DeleteSpecifiedRegion(rid)
            rid += 1

        self.logger.info("Number of connected edges: {0:d}".format(rid))

    def read_mesh(self):
        ''' Read in a surface mesh.
        '''
        filename, file_extension = path.splitext(self.params.model_file_name)
        reader = None
        if file_extension == ".vtp":
            reader = vtk.vtkXMLPolyDataReader()
            self.mesh_from_vtp = True
        elif file_extension == ".stl":
            reader = vtk.vtkSTLReader()
            self.mesh_from_vtp = False 
        reader.SetFileName(self.params.model_file_name)
        reader.Update()
        self.surface = reader.GetOutput()
        num_points = self.surface.GetPoints().GetNumberOfPoints()
        self.logger.info("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        self.logger.info("Number of triangles: %d" % num_polys)

        self.extract_edges()
        self.extract_nonmanifold_edges()

        if self.mesh_from_vtp:
            self.get_surface_faces()
        else:
            self.extract_faces()


