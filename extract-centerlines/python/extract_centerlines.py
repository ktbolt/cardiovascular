#!/usr/bin/env python

""" 
This module provides the interface to the modules creating a 1D mesh used for 1D simulations. 

Centerlines can be computed or read in. If centerline are read from a file then they must have 
been split and grouped along branches. If you are reading the centerlines computed by the SimVascular 
Models plugin then the Full_Centerlines.vtp file must be used.
"""
import argparse
import sys
import os
import logging

from manage import get_logger_name, init_logging, get_log_file_name
from parameters import Parameters
from mesh import Mesh

logger = logging.getLogger(get_logger_name())

class Args(object):
    """ This class defines the command line arguments to the generate-1d-mesh script.
    """
    PREFIX = "--"
    SURFACE_FILE = "surface_file_name"
    SOURCE_FACE_IDS = "source_face_ids" 
    TARGET_FACE_IDS = "target_face_ids" 

def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.SURFACE_FILE),
      help="The surface (.vtp) file.")

    parser.add_argument(cmd(Args.SOURCE_FACE_IDS),
      help="The source face IDs.")

    parser.add_argument(cmd(Args.TARGET_FACE_IDS),
      help="The target face IDs.")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    """ Set the values of parameters input from the command line.
    """
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

    params.source_face_ids = [int(id) for id in kwargs.get(Args.SOURCE_FACE_IDS).strip().split()]
    logger.info("Source face ids: %s" % params.source_face_ids)

    params.target_face_ids = [int(id) for id in kwargs.get(Args.TARGET_FACE_IDS).strip().split(',')]
    logger.info("Target face ids: %s" % params.target_face_ids)

    return params

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))
    if not params:
        logger.error("Error in parameters.")
        sys.exit(1)

    mesh = Mesh(params)
    mesh.read_mesh()
    #mesh.calculate_centerlines()
    mesh.show()


