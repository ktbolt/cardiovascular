#!/usr/bin/env python

""" 
"""
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
    """ This class defines the command line arguments to the script.
    """
    PREFIX = "--"
    SOLVER_FILE = "solver_file_name"

def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.SOLVER_FILE),
      help="The solver (.in) file.")

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
    if kwargs.get(Args.SOLVER_FILE):
        params.solver_file_name = kwargs.get(Args.SOLVER_FILE)
        logger.info("Solver file: %s" % params.solver_file_name)
        if not os.path.exists(params.solver_file_name):
            logger.error("The solver file '%s' was not found." % params.solver_file_name)
            return None

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

    ## Read in the solver file.
    mesh = Mesh(params)
    mesh.graphics = graphics
    mesh.read_solver_file()
    graphics.add_graphics_points(mesh.points_polydata, [0.8, 0.8, 0.8])
    graphics.add_graphics_edges(mesh.lines_polydata, [0.8, 0.8, 0.8])

    graphics.mesh = mesh
    graphics.show()


