#!/usr/bin/env python

''' This script is used to explore an SV model.  
'''
import argparse
import sys
import os
import logging
import vtk 

from manage import get_logger_name, init_logging, get_log_file_name
from parameters import Parameters
from mesh import Mesh
from graphics import Graphics

logger = logging.getLogger(get_logger_name())

class Args(object):
    ''' This class defines the command line arguments to the generate-1d-mesh script.
    '''
    PREFIX = "--"

    CHECK_AREA = "check_area"
    AREA_TOLERANCE = "area_tolerance"
    ANGLE = "angle"
    FILTER_FACES = "filter_faces"
    MODEL_FILE = "model_file_name"
    SHOW_EDGES = "show_edges"
    SHOW_FACES = "show_faces"
    USE_FEATURE_ANGLE = "use-feature-angle"

def cmd(name):
    ''' Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    ''' Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.CHECK_AREA), type=bool, help="Check the area of surface triangles.") 
    parser.add_argument(cmd(Args.AREA_TOLERANCE), help="The tolerance for checking for the area of surface triangles.") 

    parser.add_argument(cmd(Args.ANGLE), type=float, help="The face angle.") 
    parser.add_argument(cmd(Args.FILTER_FACES), help="Filter faces with the number of cells. ")
    parser.add_argument(cmd(Args.MODEL_FILE), help="The model (.vtp) file.")
    parser.add_argument(cmd(Args.SHOW_EDGES), help="Show edges.")
    parser.add_argument(cmd(Args.SHOW_FACES), help="Show faces.")
    parser.add_argument(cmd(Args.USE_FEATURE_ANGLE), type=bool, help="The face feature angle.") 

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    ''' Set the values of parameters input from the command line.
    '''
    print(kwargs)
    logger.info("Parse arguments ...")

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.MODEL_FILE):
        params.model_file_name = kwargs.get(Args.MODEL_FILE)
        logger.info("Model file: %s" % params.model_file_name)
        if not os.path.exists(params.model_file_name):
            logger.error("The model file '%s' was not found." % params.model_file_name)
            return None

    if kwargs.get(Args.CHECK_AREA):
        params.check_area = int(kwargs.get(Args.CHECK_AREA))

    if kwargs.get(Args.AREA_TOLERANCE):
        params.area_tolerance = float(kwargs.get(Args.AREA_TOLERANCE))

    if kwargs.get(Args.FILTER_FACES):
        params.filter_faces = int(kwargs.get(Args.FILTER_FACES))

    params.angle = kwargs.get(Args.ANGLE)

    params.show_edges = kwargs.get(Args.SHOW_EDGES)
    params.show_faces = kwargs.get(Args.SHOW_FACES)

    params.use_feature_angle = kwargs.get(Args.USE_FEATURE_ANGLE)

    return params

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))
    if not params:
        logger.error("Error in parameters.")
        sys.exit(1)

    ## Create graphics interface.   
    graphics = Graphics()

    ## Read in the model. 
    mesh = Mesh(params)
    mesh.graphics = graphics
    mesh.read_mesh()
    graphics.mesh = mesh

    if params.check_area:
      mesh.check_area(params.area_tolerance)
      '''
      mapper = vtk.vtkPolyDataMapper()
      mapper.SetInputData(mesh.surface)
      mapper.SetScalarVisibility(True)
      mapper.SetScalarModeToUseCellFieldData()
      mapper.SetScalarRange(mesh.scalar_range)
      mapper.SetScalarModeToUseCellData()
      mapper.SetLookupTable(mesh.hue_lut)

      actor = vtk.vtkActor()
      actor.SetMapper(mapper)
      actor.GetProperty().EdgeVisibilityOn();
      graphics.renderer.AddActor(actor)
      '''
      graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], wire=True)
      graphics.add_graphics_geometry(mesh.area_surface, [1.0, 0.0, 0.0])

      color = [1.0, 0.0, 0.0]
      radius = 1.0
      for pt in mesh.failed_area_check_list:
        graphics.add_sphere(pt, color, radius)

    ## Show faces with the number of cells.
    '''
    if params.filter_faces:
        mesh.filter_faces(params.filter_faces)
        show_wire = True
    else:
        show_wire = False

    if params.show_edges:
        mesh.show_edges()


    if params.show_faces:
        mesh.show_faces()
    else:
        #graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], wire=show_wire)
        graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], edges=True)
    '''
    #graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], edges=True)

    graphics.mesh = mesh
    graphics.show()


