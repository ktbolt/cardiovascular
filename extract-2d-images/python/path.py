#!/usr/bin/env python
import sys
import xml.etree.ElementTree as et
import vtk
from math import sqrt
import logging
from manage import get_logger_name

class PathSampleMethod:
    CONTROL_POINTS = "control_points"
    DISTANCE = "distance"
    NUMBER = "number"

class PathData(object):
    def __init__(self, pid, index, point, tangent, rotation):
        self.id = pid
        self.index = index
        self.point = point
        self.tangent = tangent 
        self.rotation = rotation

class PathElement(object):
    '''The PathElement class is used to represent a SimVascular path element.
    '''
    def __init__(self, path_name):
        self.id = path_name
        self.ids = []
        self.points = []
        self.control_points = []
        self.tangents = []
        self.rotations = []

class Path(object):
    '''The Path class is used to represent a SimVascular path.
    '''
    def __init__(self, pid, graphic):
        self.id = pid
        self.elements = []
        self.graphics = graphic
        self.logger = logging.getLogger(get_logger_name())

    def select(self, position):
        '''Select a path given a 3D point.
        '''
        path_data = {}
        min_dist = 1e9
        min_pt = None
        min_i = None
        for elem_i, element in enumerate(self.elements):
            pts = element.points
            for i in range(0, len(pts)):
                pt = pts[i]
                dist = sqrt(sum([(pt[j]-position[j])*(pt[j]-position[j]) for j in range(0,3)]))
                if dist < min_dist:
                    min_dist = dist
                    min_element = element
                    min_i = i
                    min_element_i = elem_i
            #_for i in range(0, len(pts)-1)
        #_for element in self.elements
        
        #print("[Path.select] index: {0:d}".format(min_i))
        #print("[Path.select] min_element_i: {0:d}".format(min_element_i))
        pid = min_element.ids[min_i]
        index = min_i
        point = min_element.points[min_i]
        tangent = min_element.tangents[min_i]
        rotation = min_element.rotations[min_i]
        return PathData(pid, index, point, tangent, rotation)

    def get_data(self, element_id, index):
        element = self.elements[element_id]
        path_data = {}
        pid = element.ids[index]
        point = element.points[index]
        tangent = element.tangents[index]
        rotation = element.rotations[index]
        return PathData(pid, index, point, tangent, rotation)

    def get_point_ids(self, parameters, element):
        '''Get the list of element point IDs used to create slices along a path.
        '''
        
        # Sample every parameters.slice_increment path points.
        #
        if parameters.path_sample_method == PathSampleMethod.NUMBER:
            point_ids = element.ids[::parameters.slice_increment]

        # Sample path at parameters.slice_increment points equidistance along the path.
        #
        elif parameters.path_sample_method == PathSampleMethod.DISTANCE:
            path_length = 0.0
            pt1 = element.points[0]

            for i in range(1, len(element.points)):
                pt2 = element.points[i]
                path_length += sqrt(sum([(pt1[j]-pt2[j])*(pt1[j]-pt2[j]) for j in range(0,3)]))
                pt1 = pt2

            dist_inc = path_length / parameters.slice_increment
            point_ids = [ element.ids[0] ]
            path_dist = 0.0
            pt1 = element.points[0]

            for i in range(1, len(element.points)):
                pt2 = element.points[i]
                path_dist += sqrt(sum([(pt1[j]-pt2[j])*(pt1[j]-pt2[j]) for j in range(0,3)]))
                if path_dist >= dist_inc: 
                    point_ids.append(element.ids[i])
                    path_dist = 0.0
                    pt1 = element.points[i]

        # Sample path at every parameters.slice_increment control points. 
        #
        elif parameters.path_sample_method == PathSampleMethod.CONTROL_POINTS:
            point_ids = [] 
            for cpt in element.control_points[::parameters.slice_increment]:
                path_data = self.select(cpt)
                point_ids.append(path_data.index)

        else:
            raise Exception("Unknown path sample method '{0:s}'".format(parameters.path_sample_method))
  
        return point_ids 

    @classmethod
    def read_path_file(cls, params, graphics):
        '''Read a path (.pth) file. 
        '''
        logger = logging.getLogger(get_logger_name())
        file_name = params.path_file_name

        # Remove 'format' tag from xml file.
        f = open(file_name, "r")
        lines = f.readlines()
        new_lines = []
        for line in lines:
          if '<format' not in line:
            new_lines.append(line)

        # Create string from xml file and parse it.
        xml_string = "".join(new_lines)
        tree = et.ElementTree(et.fromstring(xml_string))
        #tree = et.parse(file_name)
        root = tree.getroot()

        ## Create paths.
        #
        paths = []
        for path_t in root.iter('path'):
           path_id = path_t.attrib["id"]
           logger.info("Path ID: %s" % path_id)
           path = Path(path_id, graphics)

           for path_element_t in path_t.iter('path_element'):
               eid = 1
               if "id" in path_element_t.attrib:
                   eid = path_element_t.attrib["id"]
               path_element = PathElement(eid)
               logger.info("  Element ID: %s" % eid)
               
               for control_pts in path_element_t.iter('control_points'):
                   for point in control_pts.iter('point'):
                       x = point.attrib['x']
                       y = point.attrib['y']
                       z = point.attrib['z']
                       path_element.control_points.append([float(x),float(y),float(z)])
                   #_for point in control_pts
                   logger.info("    Number of control points: %d" % len(path_element.control_points))
               #_for control_pts in path_element_t.iter('control_points'):

               for path_pts in path_element_t.iter('path_points'):
                   for path_pt in path_pts.iter('path_point'):
                       pid = path_pt.attrib['id']
                       path_element.ids.append(pid)
                       for pos in path_pt.iter('pos'):
                           x = pos.attrib['x']
                           y = pos.attrib['y']
                           z = pos.attrib['z']
                           path_element.points.append([float(x),float(y),float(z)])
                       for tangent in path_pt.iter('tangent'):
                           x = tangent.attrib['x']
                           y = tangent.attrib['y']
                           z = tangent.attrib['z']
                           path_element.tangents.append([float(x),float(y),float(z)])
                       for rotation in path_pt.iter('rotation'):
                           x = rotation.attrib['x']
                           y = rotation.attrib['y']
                           z = rotation.attrib['z']
                           path_element.rotations.append([float(x),float(y),float(z)])
                   #_for path_pt in path_pts.iter('path_point')
               #_for path_pts in path_element_t.iter('path_points')

               logger.info("    Number of path points: %d" % len(path_element.points))
               path.elements.append(path_element)
           #_for path_element_t in path_t.iter('path_element')

           length = path.get_length()
           logger.info("Path length: %g" % length)
           paths.append(path)
       #_for path_t in root.iter('path')

        return paths
    #_read_path_file(cls, file_name)

    def get_length(self):
        length = 0.0
        for element in self.elements:
            pts = element.points
            for i in range(0, len(pts)-1):
              pt1 = pts[i]
              pt2 = pts[i+1]
              dist = sqrt(sum([(pt1[j]-pt2[j])*(pt1[j]-pt2[j]) for j in range(0,3)]))
              length += dist
            #_for i in range(0, len(pts)-1)
        #_for element in self.elements
        return length 

    def create_path_geometry(self):
       '''Create geometry for the path.
       '''
       ## Show path points.
       #
       for element in self.elements:
           coords = element.points
           num_pts = len(coords)

           # Create path geometry points and line connectivity.
           points = vtk.vtkPoints()
           points.SetNumberOfPoints(num_pts)
           lines = vtk.vtkCellArray()
           lines.InsertNextCell(num_pts)
           #lines.InsertNextCell(num_pts+1)
           n = 0
           for pt in coords:
               points.SetPoint(n, pt[0], pt[1], pt[2])
               lines.InsertCellPoint(n)
               n += 1
           #_for pt in coords
           lines.InsertCellPoint(0)

           geom = vtk.vtkPolyData()
           geom.SetPoints(points)
           geom.SetLines(lines)
           #geom.BuildLinks()
           mapper = vtk.vtkPolyDataMapper()
           mapper.SetInputData(geom)
           actor = vtk.vtkActor()
           actor.SetMapper(mapper)
           actor.GetProperty().SetLineWidth(4.0)
           actor.GetProperty().SetColor(1.0, 0.0, 0.0)
           self.graphics.add_actor(actor)

       ## Show control points.
       #
       for element in self.elements:
           coords = element.control_points
           points = vtk.vtkPoints()
           points.SetNumberOfPoints(len(coords))
           n = 0
           for pt in coords:
               points.SetPoint(n, pt[0], pt[1], pt[2])
               n += 1
           #_for pt in coords

           geom = vtk.vtkPolyData()
           geom.SetPoints(points)
           glyphFilter = vtk.vtkVertexGlyphFilter()
           glyphFilter.SetInputData(geom)
           mapper = vtk.vtkPolyDataMapper()
           mapper.SetInputConnection(glyphFilter.GetOutputPort())
           actor = vtk.vtkActor()
           actor.GetProperty().SetColor(0.0, 0.0, 0.8)
           actor.GetProperty().SetPointSize(10)
           actor.SetMapper(mapper)
           self.graphics.add_actor(actor)
    #_create_path_geometry(path)


