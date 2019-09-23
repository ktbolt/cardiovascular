#!/usr/bin/env python
"""
This program is used to visualize paths created by SimVascular. 
"""
import argparse
import logging
import sys
import xml.etree.ElementTree as et
import vtk
from math import sqrt

class PathElement(object):
    """
    The PathElement class is used to represent a SimVascular path element.
    """
    def __init__(self, path_name):
        self.id = path_name
        self.points = []
        self.control_points = []

class Path(object):
    """
    The Path class is used to represent a SimVascular path.
    """
    def __init__(self, id):
        self.id = id
        self.elements = []

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

def parse_args():
    """ 
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",   "--surface-file",   help="Input surface (.vtp) file.")
    parser.add_argument("-p",   "--path-file",      help="Input path(.pth) file.")
    args = parser.parse_args()

    if len(sys.argv) == 1:
       parser.print_help()
       sys.exit(1)

    return args


def init_logging():
    logger_name = 'sv-paths'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger 

def read_path_file(args, logger):
    """ 
    Read a path (.pth) file. 
    """
    file_name = args.path_file

    if file_name == None:
        logger.error("No input path file name given.")
        sys.exit(1)
    else:
        logger.info("Input path file name: %s" % file_name)

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
        path = Path(path_id)

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


def read_vtp_file(args, logger):
    """ 
    Read a vtp file. 
    """
    file_name = args.surface_file

    if file_name == None:
        logger.error("No input surface file name given.")
        sys.exit(1)
    else:
        logger.info("Input surface file name: %s" % file_name)

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    poly_data = reader.GetOutput()

    points = poly_data.GetPoints()
    num_points = points.GetNumberOfPoints()
    logger.info("Number of points %d" % num_points)

    polygons = poly_data.GetPolys()
    num_polys = polygons.GetNumberOfCells()
    logger.info("Number of polygons %d" % num_polys)

    return poly_data

def create_path_geometry(renderer, path):
    """ 
    Create geometry for the path.
    """

    ## Show path points.
    #
    for element in path.elements:
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
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(geom)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(4.0)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        renderer.AddActor(actor)

    ## Show control points.
    #
    for element in path.elements:
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
        renderer.AddActor(actor)


def create_graphics_geometry(geom):
    """ 
    Create geometry for display.
    """
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    mapper.SetScalarVisibility(False)
    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    actor.GetProperty().SetOpacity(0.5)
    actor.GetProperty().BackfaceCullingOn()
    actor.SetMapper(mapper)
    return actor

def main():
    logger = init_logging()

    # Get command-line arguments.
    args = parse_args()

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer_win.SetSize(1500, 1500)

    # Read surface .vtp file and create render geometry.
    if args.surface_file:
        surface = read_vtp_file(args, logger)
        surface_geom = create_graphics_geometry(surface)
        renderer.AddActor(surface_geom)

    # Read the contours .ctgr file.
    paths = read_path_file(args, logger)

    # Create path geometry.
    for path in paths:
        create_path_geometry(renderer, path)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()

if __name__ == "__main__":
    main()



