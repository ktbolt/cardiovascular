#!/usr/bin/env python

from os import path
import sys
import logging
from manage import get_logger_name
from node import Node
from segment import Segment 
from math import pi, sqrt

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Mesh(object):

    def __init__(self, params):
        self.params = params
        self.nodes = {}
        self.segments = {}
        self.graphics = None
        self.logger = logging.getLogger(get_logger_name())

        self.points = vtk.vtkPoints()
        self.vertices = vtk.vtkCellArray()
        self.points_polydata = None
        self.lines_polydata = None
        self.num_elements = 0

    def read_solver_file(self):
        """ Read in a solver.in file.
        """
        self.logger.info("---------- Read solver file ----------")
        #self.logger.info("Number of points: %d" % num_points)

        with open(self.params.solver_file_name) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                print("Line {}: {}".format(cnt, line.strip()))
                line = fp.readline()
                tokens = line.split()
                if len(tokens) == 0: 
                    continue
                if tokens[0] == 'NODE':
                    self.add_node(tokens)
                elif tokens[0] == 'SEGMENT':
                    self.add_segment(tokens)
            #__while line
        #__with open(self.params.solver_file_name) as fp:
        self.logger.info("Number of segments: {0:d}".format(len(self.segments)))
        self.logger.info("Number of elements: {0:d}".format(self.num_elements))

        # Create a points polydata object
        self.points_polydata = vtk.vtkPolyData()
        self.points_polydata.SetPoints(self.points)
        self.points_polydata.SetVerts(self.vertices)

        # Create a lines polydata object
        self.lines_polydata = vtk.vtkPolyData()
        self.lines_polydata.SetPoints(self.points)
        lines = vtk.vtkCellArray()
        for sid, segment in self.segments.items():
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, segment.node1)
            line.GetPointIds().SetId(1, segment.node2)
            lines.InsertNextCell(line)
        self.lines_polydata.SetLines(lines)

    def add_node(self, tokens):
        """ Add a node..
        """
        nid = int(tokens[1])
        x = float(tokens[2])
        y = float(tokens[3])
        z = float(tokens[4])
        pid = self.points.InsertNextPoint([x, y, z])
        self.vertices.InsertNextCell(1)
        self.vertices.InsertCellPoint(pid)
        self.nodes[nid] = Node(nid,x,y,z)

    def add_segment(self, tokens):
        """ Add a segment.
        """
        sid = tokens[1]
        node1 = int(tokens[5])
        node2 = int(tokens[6])
        inlet_area = float(tokens[7])
        outlet_area = float(tokens[8])
        self.segments[sid] = Segment(sid,node1,node2,inlet_area,outlet_area)
        self.num_elements += int(tokens[4])

    def show_nodes(self):
        radius = self.params.radius
        for nid,node in self.nodes.items():
            center = [node.x, node.y, node.z]
            self.graphics.node_actors[node.id] = (self.graphics.add_sphere(radius, center, [0.0, 1.0, 0.0]),node)

    def show_segments(self):
        radius = self.params.radius
        for sid, segment in self.segments.items():
            node1 = self.nodes[segment.node1]
            pt1 = [node1.x, node1.y, node1.z]
            radius1 = sqrt(segment.inlet_area / pi)

            node2 = self.nodes[segment.node2]
            pt2= [node2.x, node2.y, node2.z]
            radius2 = sqrt(segment.outlet_area / pi)

            radius = min(radius1, radius2)
            #print("segment: {0:s}  radius1: {1:g}  radius2: {2:g}".format(segment.id,radius1, radius2))

            #self.graphics.segment_actors[sid] = (self.graphics.add_tapered_cyl( pt1, radius1, pt2, radius2), segment)
            self.graphics.segment_actors[sid] = (self.graphics.add_cyl( pt1, pt2, radius, [0.8, 0.8, 0.8]), segment)
            self.graphics.add_sphere(radius1, pt1, [0.0, 1.0, 0.0])
            self.graphics.add_sphere(radius2, pt2, [1.0, 0.0, 1.0])


