#!/usr/bin/env python

import argparse
import sys

from manage import get_logger_name, init_logging
from parameters import Parameters
from centerlines import *
from utils import write_polydata, read_polydata

logger = logging.getLogger(get_logger_name())

class Args(object):
    """ This class defines the valid command line arguments to the generate-1d-mesh script.
    """
    PREFIX = "--"
    BOUNDARY_SURFACE_DIR = "boundary_surfaces_directory"
    CENTERLINE_INPUT_FILE = "centerlines_input_file"
    CENTERLINE_OUTPUT_FILE = "centerlines_output_file"
    COMPUTE_CENTERLINES = "compute_centerlines"
    SURFACE_MODEL = "surface_model"
    UNIFORM_BC = "uniform_bc"
    
def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.BOUNDARY_SURFACE_DIR), 
      help="Directory containing the boundary (inlet/outlet) surface files")

    parser.add_argument(cmd(Args.CENTERLINE_INPUT_FILE), 
      help="The name of the file to read centerline geometry from.")

    parser.add_argument(cmd(Args.CENTERLINE_OUTPUT_FILE), 
      help="The name of the file to write centerline geometry to.")

    parser.add_argument(cmd(Args.COMPUTE_CENTERLINES), const=1, type=int, nargs='?', default=0, 
      help="If given or value is set to 1 then compute centerlines.")

    parser.add_argument(cmd(Args.SURFACE_MODEL), 
      help="The surface model used to compute centerlines.")

    parser.add_argument(cmd(Args.UNIFORM_BC),
      help = "If set to (true,1,on) then read BC files")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    """ Set the values of parameters input from the command line.
    """
    logger.info("Parse arguments ...")
    true_values = ["on", "true", "1"]

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.BOUNDARY_SURFACE_DIR): 
        params.boundary_surfaces_dir = kwargs.get(Args.BOUNDARY_SURFACE_DIR)
        logger.info("Surface directory: %s" % params.boundary_surfaces_dir)

    if kwargs.get(Args.CENTERLINE_INPUT_FILE):
        params.centerlines_input_file = kwargs.get(Args.CENTERLINE_INPUT_FILE)
        logger.info("Centerlines input file: %s" % params.centerlines_input_file)

    if kwargs.get(Args.CENTERLINE_OUTPUT_FILE): 
        params.centerlines_output_file = kwargs.get(Args.CENTERLINE_OUTPUT_FILE)
        logger.info("Centerlines output file: %s" % params.centerlines_output_file)

    params.compute_centerlines = kwargs.get(Args.COMPUTE_CENTERLINES)
    logger.info("Compute centerlines: %s" % ('true' if params.compute_centerlines else 'false'))

    if kwargs.get(Args.SURFACE_MODEL):
        params.surface_model = kwargs.get(Args.SURFACE_MODEL)
        logger.info("Surface model: %s" % params.surface_model)

    if params.compute_centerlines and params.centerlines_input_file: 
        logger.error("Both compute centerlines and read centerlines are specifed.")
        return None

    return params 

def read_centerlines(params):
    """ Read centerlines for a surface model from a file.
    """
    centerlines = Centerlines()
    centerlines.geometry = read_polydata(params.centerlines_input_file)

    logger.info("Read centerlines input from file: %s", params.centerlines_input_file) 
    logger.info("  Number of points: %d ", centerlines.geometry.GetNumberOfPoints())
    logger.info("  Number of arrays: %d", centerlines.geometry.GetCellData().GetNumberOfArrays())

    return centerlines

def compute_centerlines(params):
    """ Compute the centerlines for a surface model.
    """

    ## Check input parameters.
    #
    if not params.surface_model:
        logger.error("No surface model has been specified.")
        return

    if not params.centerlines_output_file:
        logger.error("No centerlines output file has been specified.")
        return

    # Create Centerlines object that encapsulats centerline calculations. 
    centerlines = Centerlines()

    # Extract centerlines.
    centerlines.extract_center_lines(params)

    # Split and group centerlines along branches. 
    centerlines.extract_branches(params)

    # Write the centerlines branches to a file.
    if centerlines.branch_geometry:
        write_polydata(params.centerlines_output_file, centerlines.branch_geometry)

    return centerlines

def run(**kwargs):
    """ Execute the 1D mesh generation using passed parameters.
    """

    ## Set input parameters.
    params = set_parameters(**kwargs)
    if not params:
        return False

    ## Extract surface centerlines.
    if params.compute_centerlines:
        centerlines = compute_centerlines(params)

    ## Read surface centerlines.
    elif params.centerlines_input_file:
        centerlines = read_centerlines(params)

    return True

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    if not run(**vars(args)):
        print_help()
        sys.exit(1)

