#!/usr/bin/env python

import argparse
import sys

from manage import get_logger_name, init_logging
from parameters import Parameters
from centerlines import *

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--boundary-surfaces-directory", help="Directory containing the boundary (inlet/outlet) surface files")
    parser.add_argument("--surface-model", help="The surface model used to compute centerlines.")
    parser.add_argument("--uniformBC",  help = "If set to (true,1,on) then read BC files")
    return parser.parse_args(), parser.print_help

def run(**kwargs):
    """ Execute the 1D mesh generation using passed parameters.
    """
    init_logging()
    logger = logging.getLogger(get_logger_name())
    logger.info("Parse arguments")
    true_values = ["on", "true", "1"]

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Parse arguments.
    for key, value in kwargs.items():
        logger.info("key %s  value %s " % (key, value))
        if value == None:
            continue
        if key == "boundary_surfaces_directory":
            params.boundary_surfaces_dir = value
            logger.info("Surface directory: %s" % value)
        elif key == "surface_model":
            params.surface_model = value
            logger.info("Surface model : %s" % value)
        elif key == "uniformBC":
            params.uniformBC = (value in true_values)
        else:
            logger.error("Unknown parameter name %s" % key)
            return False
    #__for key, value in kwargs.items

    ## Extract surface centerlines.
    extract_center_lines(params)

    return True

if __name__ == '__main__':
    args, print_help = parse_args()
    if not run(**vars(args)):
        print_help()
        sys.exit(1)

