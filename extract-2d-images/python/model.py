#!/usr/bin/env python

import math
import sys
import vtk
import logging
from manage import get_logger_name
import numpy as np

class Model(object):
    '''The Model class is used to represent a SimVascular model.
    '''
    def __init__(self, params, graphics):
        self.graphics = graphics
        self.logger = logging.getLogger(get_logger_name())
        self.parameters = params
        self.surface = None 
        self.slice_geometry = None 
        self.results_dir = params.results_directory + "/"

    def read_model_file(self):
        '''Read a model (.vtp) file. 
        '''
        logger = logging.getLogger(get_logger_name())
        file_name = self.parameters.model_file_name

        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        self.surface = reader.GetOutput()
        num_points = self.surface.GetPoints().GetNumberOfPoints()
        self.logger.info("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        self.logger.info("Number of triangles: %d" % num_polys)

    def get_surface(self):
        return self.surface 

    def create_model_geometry(self):
        '''Create geometry for the model.
        '''
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.surface)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(4.0)
        actor.GetProperty().SetColor(0.0, 1.0, 0.0)
        actor.GetProperty().SetOpacity(0.5)
        actor.PickableOff()
        self.graphics.add_actor(actor)

    def extract_slice(self, path_data, verbose=False):
        '''Extract a 2D slice from the model surface.
        '''
        point_id = path_data.id
        origin = path_data.point
        tangent = np.array(path_data.tangent)
        normal = np.array(path_data.rotation)
        binormal = np.cross(tangent, normal)

        if verbose:
            print(" ")
            print("---------- Model Extract Slice ----------")
            print("point id: " + str(point_id))
            print("origin: " + str(origin))
            print("tangent: " + str(tangent))
            print("normal: " + str(normal))
            print("binormal: " + str(binormal))

        ## Slice the model with a plane.
        #
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(origin[0], origin[1], origin[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane);
        cutter.SetInputData(self.surface);
        cutter.Update()
        slice_geometry = cutter.GetOutput()

        ## Check for multiple disjoint slice contours.
        #
        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(slice_geometry)
        conn_filter.SetExtractionModeToSpecifiedRegions()

        components = []
        boundary_faces = {}
        min_d = 1e6
        min_comp = None

        rid = 0
        center = 3*[0.0]

        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break

            conn_filter.DeleteSpecifiedRegion(rid)

            if rid == 0:
                color = [1.0, 0.0, 0.0]
            elif rid == 1:
                color = [0.0, 1.0, 0.0]
            else:
                color = [0.0, 0.0, 1.0]

            clean_filter = vtk.vtkCleanPolyData()
            clean_filter.SetInputData(component)
            clean_filter.Update();
            component = clean_filter.GetOutput()

            comp_points = component.GetPoints()
            num_comp_points = component.GetNumberOfPoints()
            num_comp_cells = component.GetNumberOfCells()

            cx = 0.0
            cy = 0.0
            cz = 0.0
            for i in range(num_comp_points):
                pt = comp_points.GetPoint(i)
                cx += pt[0]
                cy += pt[1]
                cz += pt[2]
            center[0] = cx / num_comp_points
            center[1] = cy / num_comp_points
            center[2] = cz / num_comp_points
            #components.append(component)
            d = sum( [ (center[j]-origin[j])*(center[j]-origin[j])  for j in range(3) ] )
            #print('[extract_slice] num_comp_cells: {0:d}'.format(num_comp_cells))
            #print('[extract_slice] num_comp_points: {0:d}'.format(num_comp_points))
            #print('[extract_slice] center: {0:s}'.format(str(center)))
            #print('[extract_slice] d: {0:g}'.format(d))
            if d < min_d:
                min_d = d
                min_comp = component
            rid += 1

        self.slice_geometry = min_comp 

        ## Show the slice.
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.slice_geometry)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(10.0)
        actor.GetProperty().SetColor(1.0, 0.0, 1.0)
        actor.PickableOff()
        self.graphics.add_actor(actor)

        ## Write the slice to a .vtp file.
        if self.slice_geometry: 
            writer = vtk.vtkXMLPolyDataWriter()
            writer.SetInputData(self.slice_geometry)
            writer.SetFileName(self.results_dir+'model_slice_'+point_id+'.vtp')
            writer.SetCompressorTypeToNone()
            writer.SetDataModeToAscii()
            writer.Write()

