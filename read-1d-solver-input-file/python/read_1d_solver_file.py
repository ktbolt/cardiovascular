#!/usr/bin/env python

""" 
"""
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
    """ This class defines the command line arguments to the script.
    """
    PREFIX = "--"
    CENTERLINES_FILE = "centerlines_file_name"
    RADIUS = "radius"
    SOLVER_FILE = "solver_file_name"
    SURFACE_FILE = "surface_file_name"

def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.CENTERLINES_FILE), help="The centerlines .vtp file name.")
    parser.add_argument(cmd(Args.RADIUS), help="The radius used to display nodes and segments.")
    parser.add_argument(cmd(Args.SOLVER_FILE), help="The solver (.in) file.")
    parser.add_argument(cmd(Args.SURFACE_FILE), help="The surface (.vtp) file.")

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
    if kwargs.get(Args.CENTERLINES_FILE):
        params.centerlines_file_name = kwargs.get(Args.CENTERLINES_FILE)
        logger.info("Centerlines file: %s" % params.centerlines_file_name)
        if not os.path.exists(params.centerlines_file_name):
            logger.error("The centerlines file '%s' was not found." % params.centerlines_file_name)
            return None

    if kwargs.get(Args.RADIUS):
        params.radisu = float(kwargs.get(Args.radius))

    if kwargs.get(Args.SOLVER_FILE):
        params.solver_file_name = kwargs.get(Args.SOLVER_FILE)
        logger.info("Solver file: %s" % params.solver_file_name)
        if not os.path.exists(params.solver_file_name):
            logger.error("The solver file '%s' was not found." % params.solver_file_name)
            return None

    if kwargs.get(Args.SURFACE_FILE):
        params.surface_file_name = kwargs.get(Args.SURFACE_FILE)
        logger.info("Surface file: %s" % params.surface_file_name)
        if not os.path.exists(params.surface_file_name):
            logger.error("The surface file '%s' was not found." % params.surface_file_name)
            return None

    return params

def read_surface(file_name, graphics):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update();
    polydata = reader.GetOutput();
    geom = graphics.add_graphics_geometry(polydata, [0.5,0.5,0.5])
    geom.GetProperty().SetOpacity(0.5)
    geom.PickableOff()

def read_centerlines(file_name, graphics):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update();
    polydata = reader.GetOutput();
    geom = graphics.add_graphics_geometry(polydata, [0.0,0.5,0.0], 4.0)
    geom.PickableOff()

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
    graphics.mesh = mesh

    mesh.show_nodes()
    mesh.show_segments()
    #radius = params.radius
    #graphics.add_graphics_points(mesh.points_polydata, [0.8, 0.8, 0.8], radius)
    #graphics.add_graphics_edges(mesh.lines_polydata, [0.8, 0.8, 0.8], radius)

    if params.centerlines_file_name != None:
        read_centerlines(params.centerlines_file_name, graphics)

    if params.surface_file_name!= None:
        read_surface(params.surface_file_name, graphics)

    graphics.show()


