#!/usr/bin/env python

'''This script extracts boundary faces from a surface geometry. 
'''
import argparse
import sys
import os
import logging

from manage import get_logger_name, init_logging, get_log_file_name
from parameters import Parameters
from mesh import Mesh
from graphics import Graphics

logger = logging.getLogger(get_logger_name())

class Args(object):
    '''This class defines the command line arguments to the generate-1d-mesh script.
    '''
    PREFIX = "--"
    SURFACE_FILE = "surface_file_name"
    ANGLE = "angle" 
    USE_FEATURE_ANGLE = "use-feature-angle" 

def cmd(name):
    '''Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    '''Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.SURFACE_FILE),
      help="The surface (.vtp) file.")

    parser.add_argument(cmd(Args.ANGLE), type=float,
      help="The face angle.")

    parser.add_argument(cmd(Args.USE_FEATURE_ANGLE), type=bool,
      help="The face feature angle.")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    '''Set the values of parameters input from the command line.
    '''
    print(kwargs)
    logger.info("Parse arguments ...")

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.SURFACE_FILE):
        params.surface_file_name = kwargs.get(Args.SURFACE_FILE)
        logger.info("Surface file: %s" % params.surface_file_name)
        if not os.path.exists(params.surface_file_name):
            logger.error("The surface file '%s' was not found." % params.surface_file_name)
            return None

    params.angle = kwargs.get(Args.ANGLE)
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

    ## Read in the surface mesh.
    mesh = Mesh(params)
    mesh.graphics = graphics
    mesh.read_mesh()
    graphics.mesh = mesh
    graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8])
    graphics.add_graphics_face_components(mesh.boundary_edge_components, [1.0, 0.0, 0.0])

    graphics.mesh = mesh
    #graphics.show()


