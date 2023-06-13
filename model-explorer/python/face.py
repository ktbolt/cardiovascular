#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Face(object):

    def __init__(self, model_faceID, surface):
        self.model_face_id = model_faceID
        self.surface = surface
        self.cell_ids = None

    def get_area(self):
        area = 0.0
        points = self.surface.GetPoints()

        for i in range(self.surface.GetNumberOfCells()):
            cell = self.surface.GetCell(i)
            dim = cell.GetCellDimension()
            num_cell_nodes = cell.GetNumberOfPoints()
            tri = vtk.vtkTriangle()
            tri_points = []

            for j in range(0, num_cell_nodes):
                node_id = cell.GetPointId(j)
                pt = points.GetPoint(node_id)
                tri_points.append(pt)

            area += vtk.vtkTriangle.TriangleArea(tri_points[0], tri_points[1], tri_points[2])
           
        return area

    def get_center(self):
        ''' Get the center of the face.
        '''
        surface = self.surface
        cx = 0.0;
        cy = 0.0;
        cz = 0.0;
        point = [0.0, 0.0, 0.0]
        num_face_pts = 0
        for cellID in range(self.surface.GetNumberOfCells()):
            pointIdList = vtk.vtkIdList()
            surface.GetCellPoints(cellID, pointIdList)
            num_pts = pointIdList.GetNumberOfIds()
            num_face_pts += num_pts 
            for i in range(num_pts):
                pid = pointIdList.GetId(i);
                surface.GetPoint(pid, point);
                cx += point[0]
                cy += point[1]
                cz += point[2]
            #__for i in range(num_pts)
        #__for cellID in self.cell_ids

        return [cx/num_face_pts, cy/num_face_pts, cz/num_face_pts]

    def get_id(self, point):
        ''' Get the point ID closests to the potint.
        '''
        surface = self.surface
        cell_point = [0.0, 0.0, 0.0]
        min_dist = 1e9
        min_id = -1

        for cellID in self.cell_ids:
            pointIdList = vtk.vtkIdList()
            surface.GetCellPoints(cellID, pointIdList)
            num_pts = pointIdList.GetNumberOfIds()
            for i in range(num_pts):
                pid = pointIdList.GetId(i);
                surface.GetPoint(pid, cell_point);
                dist = sum([(cell_point[j]-point[j])*(cell_point[j]-point[j]) for j in range(3)]) 
                if dist < min_dist:
                    min_dist = dist
                    min_id = pid
            #__for i in range(num_pts):
        #__for cellID in self.cell_ids

        surface.GetPoint(min_id, cell_point);
        return min_id, cell_point

