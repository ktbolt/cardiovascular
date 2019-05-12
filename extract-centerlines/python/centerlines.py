#!/usr/bin/env python

"""
The module is used to extact centerlines from a surface mesh. 
"""

import os
from pathlib import Path
import numpy as np

import logging
from manage import get_logger_name
from face import Face
import numpy as np

import vtk
try:
    from vmtk import vtkvmtk,vmtkscripts
except ImportError:
    print("vmtk not found.")

# from utils import SurfaceFileFormats, read_surface, get_polydata_centroid, read_polydata

class Centerlines(object):
    """ The Centerlines class is used to encapsulate centerline calculations.

    Attributes:
    """
    def __init__(self, mesh, params):
        self.mesh = mesh
        self.params = params
        self.geometry = None
        self.branch_geometry = None
        self.logger = logging.getLogger(get_logger_name())

    def extract_center_lines(self):
        """ Extract the centerlines of a surface.

           The centerline geometry is returned as a vtkPolyData object.
        """
        self.logger.info("---------- Extract Centerlines ---------- ")
        mesh = self.mesh
        surface = mesh.surface
        surface_caps = mesh.surface_caps
        source_centers = []
        target_centers = []

        ## Get source and target face centers.
        #
        for faceID, face in surface_caps.items():
            self.logger.info("-----  Face ID %d ----- " % int(faceID))
            center = face.get_center()
            if face.source:
                source_centers.extend(center)
                mesh.add_sphere(center, [1.0,0.0,0.0])
            else:
                target_centers.extend(center)
                mesh.add_sphere(center, [0.0,1.0,0.0])
            self.logger.info("Center: %s" % str(center))
        #__for faceID in face_ids

        ## Extract centerlines using vmtk.
        #
        self.logger.info("Calculating surface centerlines ...");
        centerlines = vmtkscripts.vmtkCenterlines()
        centerlines.Surface = mesh.surface
        centerlines.SeedSelectorName = "pointlist"
        centerlines.AppendEndPoints = 1
        centerlines.SourcePoints = source_centers
        centerlines.TargetPoints = target_centers
        centerlines.Execute()
        self.geometry = centerlines.Centerlines
        self.logger.info("The surface centerlines have been calculated.");
        mesh.add_graphics_geometry(self.geometry, [0.0,0.0,1.0])


