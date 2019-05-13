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
        self.graphics = None
        self.logger = logging.getLogger(get_logger_name())

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

    def calculate_centerlines(self):
        self.logger.info("---------- calculate centerlines ----------")
        centerlines = Centerlines(self, self.graphics, self.params) 
        centerlines.extract_center_lines()


