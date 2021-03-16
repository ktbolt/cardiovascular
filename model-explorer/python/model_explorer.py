#!/usr/bin/env python

''' This script is used to explore an SV model.  
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
    ''' This class defines the command line arguments to the generate-1d-mesh script.
    '''
    PREFIX = "--"

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

    ## Show faces with the number of cells.
    if params.filter_faces:
        mesh.filter_faces(params.filter_faces)
        show_wire = True
    else:
        show_wire = False

    if params.show_edges:
        mesh.show_edges()

    graphics.mesh = mesh

    '''
    if params.show_faces:
        mesh.show_faces()
    else:
        #graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], wire=show_wire)
        graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], edges=True)
    '''
    graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8], edges=True)

    graphics.mesh = mesh
    graphics.show()


