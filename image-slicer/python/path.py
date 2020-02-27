#!/usr/bin/env python
import sys
import xml.etree.ElementTree as et
import vtk
from math import sqrt
import logging
from manage import get_logger_name

class PathElement(object):
    '''
    The PathElement class is used to represent a SimVascular path element.
    '''
    def __init__(self, path_name):
        self.id = path_name
        self.points = []
        self.control_points = []

class Path(object):
    '''
    The Path class is used to represent a SimVascular path.
    '''
    def __init__(self, id, graphic):
        self.id = id
        self.elements = []
        self.graphics = graphic
        self.logger = logging.getLogger(get_logger_name())

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

    @classmethod
    def read_path_file(cls, params, graphics):
        """ 
        Read a path (.pth) file. 
        """
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
               id = path_element_t.attrib["id"]
               path_element = PathElement(id)
               logger.info("  Element ID: %s" % id)
               
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
                       id = path_pt.attrib['id']
                       for pos in path_pt.iter('pos'):
                           x = pos.attrib['x']
                           y = pos.attrib['y']
                           z = pos.attrib['z']
                           path_element.points.append([float(x),float(y),float(z)])
                       #_for pos in path_pt.iter('pos')
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


    def create_path_geometry(self):
       """ 
       Create geometry for the path.
       """

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



