#!/usr/bin/env python
''' This program is used to scale contour data created by SimVascular and stored in .ctgr files. 
'''
import argparse
import logging
import os
import sys
import xml.etree.ElementTree as et
import vtk

class ContourGroup(object):
    ''' The ContourGroup class is used to represent a SimVascular contour group.
    '''
    def __init__(self, path_name):
        self.id = path_name
        self.contours = []

class Contour(object):
    ''' The Contour class is used to represent a SimVascular contour.
    '''
    def __init__(self, cid):
        self.id = cid
        self.coordinates = []

def parse_args():
    ''' Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--contour-file",    help="Input contour (.ctr) file.")
    parser.add_argument("--surface-file",    help="Input surface (.vtp) file.")
    parser.add_argument("--scale",           help="Contour scale.")
    parser.add_argument("--contour-ids",     help="Contour IDs (optional).")
    args = parser.parse_args()

    if len(sys.argv) == 1:
       parser.print_help()
       sys.exit(1)

    return args

def init_logging():
    logger_name = 'scale-contours'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger 

def read_ctgr_file(args, contour_scale, contour_ids, logger):
    ''' Read a ctgr file. 
    '''
    file_name = args.contour_file

    if file_name == None:
        logger.error("No input contour file name given.")
        sys.exit(1)
    else:
        logger.info("Input contour file name: %s" % file_name)

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

    ## Create contour groups.
    #
    contour_groups = []
    scaled_contour_groups = []
    for contour_group_t in root.iter('contourgroup'):
        path_name = contour_group_t.attrib["path_name"]
        logger.info("Contour group: %s" % path_name)
        contour_group = ContourGroup(path_name)
        scaled_contour_group = ContourGroup(path_name)

        for contour_t in contour_group_t.iter('contour'):
            cid = contour_t.attrib["id"]
            #logger.info("   Contour id: %s" % cid)
            contour = Contour(cid)
            scaled_contour = Contour(cid)
            if (len(contour_ids) != 0) and (cid not in contour_ids):
                scale = 1.0 
            else:
                scale = contour_scale 

            ## Iterate over control points. 
            #
            # The first control point is the contour center.
            #
            for control_pts in contour_t.iter('control_points'):
                for i,point in enumerate(control_pts.iter('point')):
                    x = float(point.attrib['x'])
                    y = float(point.attrib['y'])
                    z = float(point.attrib['z'])
                    if i == 0:
                        cx = x
                        cy = y
                        cz = z
                        xs = x 
                        ys = y 
                        zs = z 
                    else:
                        xs = scale * (x - cx) + cx
                        ys = scale * (y - cy) + cy
                        zs = scale * (z - cz) + cz
                    point.attrib['x'] = str(xs)
                    point.attrib['y'] = str(ys)
                    point.attrib['z'] = str(zs)
                #_for i,point in enumerate(control_pts.iter('point'))
            #_for control_pts in contour_t.iter('control_points')
            
            ## Iterate over contour points. 
            #
            for contour_pts in contour_t.iter('contour_points'):
                #logger.info("      Contour points ")
                for point in contour_pts.iter('point'):
                    x = float(point.attrib['x'])
                    y = float(point.attrib['y'])
                    z = float(point.attrib['z'])
                    xs = scale * (x - cx) + cx
                    ys = scale * (y - cy) + cy
                    zs = scale * (z - cz) + cz
                    point.attrib['x'] = str(xs)
                    point.attrib['y'] = str(ys)
                    point.attrib['z'] = str(zs)
                    contour.coordinates.append([x,y,z])
                    scaled_contour.coordinates.append([xs,ys,zs])
                #_for point in control_pts
            #_for control_pts in contour_t
            contour_group.contours.append(contour)
            scaled_contour_group.contours.append(scaled_contour)
        #_for contour_t in contour_group_t
        logger.info("   Number of contours %d" % len(contour_group.contours))
        contour_groups.append(contour_group)
        scaled_contour_groups.append(scaled_contour_group)
    #_for contour_group_t 

    # Write the scaled file name.
    scaled_file_name = os.path.splitext(file_name)[0] + "-scaled.ctgr" 
    tree.write(scaled_file_name)

    return contour_groups, scaled_contour_groups

def read_vtp_file(args, logger):
    ''' Read a vtp file. 
    '''
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

def create_contour_geometry(renderer, contour_group, color):
    ''' Create geometry for the contours in a contour group.
    '''
    for contour in contour_group.contours:
        coords = contour.coordinates
        num_pts = len(coords)

        # Create contour geometry points and line connectivity.
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(num_pts+1)
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
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        renderer.AddActor(actor)

def create_graphics_geometry(geom):
    ''' Create geometry for display.
    '''
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    mapper.SetScalarVisibility(False)
    actor = vtk.vtkActor()
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
    renderer.SetBackground(0.5, 0.8, 0.8)
    renderer_win.SetSize(1000, 1000)
    renderer_win.Render()
    renderer_win.SetWindowName("Scale Contours")

    # Read surface .vtp file and create render geometry.
    surface = read_vtp_file(args, logger)
    surface_geom = create_graphics_geometry(surface)
    surface_geom.GetProperty().SetOpacity(0.5)
    surface_geom.GetProperty().SetColor(0.8, 0.8, 0.8)
    renderer.AddActor(surface_geom)

    # Read the contours .ctgr file.
    scale = float(args.scale)
    contour_ids = {}
    if args.contour_ids != None:
        contour_ids = set([s for s in args.contour_ids.split(",")])
    contour_groups, scaled_contour_groups = read_ctgr_file(args, scale, contour_ids, logger)

    # Create contour geometry.
    for contour_group in contour_groups:
        create_contour_geometry(renderer, contour_group, color=[0.0, 1.0, 0.0])
    for contour_group in scaled_contour_groups:
        create_contour_geometry(renderer, contour_group, color=[1.0, 0.0, 0.0])

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()

if __name__ == "__main__":
    main()



