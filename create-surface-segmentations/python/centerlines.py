#!/usr/bin/env python

from collections import defaultdict
from math import sqrt
from math import pi
from math import acos
from os import path
import vtk

class Centerlines(object):
    '''The Centerlines class defines methods for operations based on centerlines geometry.

       Attributes:
         surface: The Surface object from which the centerlines where computed.
    '''
    def __init__(self):
        self.cids_array_name = "CenterlineId"
        self.max_radius_array_name = "MaximumInscribedSphereRadius"
        self.normal_array_name = "CenterlineSectionNormal"
        self.graphics = None
        self.renderer = None
        self.geometry = None
        self.surface = None
        self.ends_node_ids = None    # The centerlines ends node IDs.
        self.length_scale = 1.0
        self.max_radius = 0.0
        self.min_radius = 0.0

    def read(self, file_name):
        '''Read a centerlines geometry file created using SV.
        '''
        print("[centerlines] ========== read ==========")
        print(f"[centerlines] file_name: {file_name}")
        filename, file_extension = path.splitext(file_name)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        self.geometry = reader.GetOutput()
        print(f"[centerlines] Number of centerline points: {self.geometry.GetNumberOfPoints()}")

        self.compute_length_scale()
        print(f"[centerlines] Average distance between points: {self.length_scale}")

        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        value_range = max_radius_data.GetRange()
        self.min_radius = value_range[0]
        self.max_radius = value_range[1]
        print(f"[centerlines] Minimum radius: {self.min_radius}")
        print(f"[centerlines] Maximum radius: {self.max_radius}")
 
        self.surface.add_centerlines(self.geometry)

    def compute_length_scale(self):
        pt1 = 3*[0.0]
        pt2 = 3*[0.0]
        avg_d = 0.0
        num_pts = self.geometry.GetNumberOfPoints()
        points = self.geometry.GetPoints()
        for i in range(num_pts-1):
            points.GetPoint(i,pt1)
            points.GetPoint(i+1,pt2)
            dx = pt1[0] - pt2[0]
            dy = pt1[1] - pt2[1]
            dz = pt1[2] - pt2[2]
            d = sqrt(dx*dx + dy*dy + dz*dz)
            avg_d += d
        self.length_scale = avg_d / num_pts

