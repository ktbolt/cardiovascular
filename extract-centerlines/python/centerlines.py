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
    def __init__(self, mesh, graphics, params):
        self.mesh = mesh
        self.params = params
        self.graphics = graphics
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
        source_ids = []
        target_centers = []
        target_ids = []

        ## Get source and target face centers.
        #
        for faceID, face in surface_caps.items():
            self.logger.info(" ")
            self.logger.info("-----  Face ID %d ----- " % int(faceID))
            center = face.get_center()
            ptID, id_center = face.get_id(center)
            if face.source:
                self.logger.info("Source") 
                source_centers.extend(center)
                self.graphics.add_sphere(center, [1.0,0.0,0.0])
                self.graphics.add_sphere(id_center, [1.0,0.0,0.0])
                source_ids.append(ptID)
            else:
                self.logger.info("Target") 
                target_centers.extend(center)
                self.graphics.add_sphere(center, [0.0,1.0,0.0])
                self.graphics.add_sphere(id_center, [0.0,1.0,0.0])
                target_ids.append(ptID)
            self.logger.info("Center ID: %d" % ptID) 
            self.logger.info("Center: %s" % str(center))
            self.logger.info("ID Center: %s" % str(id_center))
        #__for faceID in face_ids

        ## Extract centerlines using vmtk.
        #
        self.logger.info("Calculating surface centerlines ...");
        centerlines = vmtkscripts.vmtkCenterlines()
        centerlines.Surface = mesh.surface
        centerlines.AppendEndPoints = 1

        """
        source_ids = [67628]
        target_ids = [67626, 67627 ,67628 ,67629 ,67630 ,67631 ,67632 ,67633]
        surface.GetPoint(source_ids[0], id_center);
        self.graphics.add_sphere(id_center, [1.0,0.0,0.0])
        """

        use_id_list = True

        if use_id_list:
            self.logger.info("Use source and target IDs")
            self.logger.info("Source IDs: %s" % str(source_ids)) 
            self.logger.info("Target IDs: %s" % str(target_ids)) 
            centerlines.SeedSelectorName = "idlist"
            centerlines.SourceIds = source_ids
            centerlines.TargetIds = target_ids
        else:
            centerlines.SeedSelectorName = "pointlist"
            centerlines.SourcePoints = source_centers
            centerlines.TargetPoints = target_centers

        #centerlines.Execute()
        #self.geometry = centerlines.Centerlines
        #self.logger.info("The surface centerlines have been calculated.");
        #self.graphics.add_graphics_geometry(self.geometry, [0.0,0.0,1.0])


