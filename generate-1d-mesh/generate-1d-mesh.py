#!/usr/bin/env python

import argparse
#import logging
from manage import get_logger_name, init_logging
from parameters import Parameters
from centerlines import *

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface-directory",    help="Directory containing the surface files")
    return parser.parse_args(), parser.print_help

def run(**kwargs):
    """ Execute the 1D mesh generation using passed parameters.
    """
    init_logging()
    logger = logging.getLogger(get_logger_name())
    logger.info("Parse arguments")

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Parse arguments.
    for key, value in kwargs.items():
        logger.info("key %s  value %s " % (key, value))
        if value == None:
            continue
        if key == "surface_directory":
            params.surface_mesh_dir = value
            logger.info("Surface directory: %s" % value)
        else:
            logger.error("Unknown parameter name %s" % key)
            return False
    #__for key, value in kwargs.items

    extract_center_lines(params)

    return True

if __name__ == '__main__':
    args, print_help = parse_args()
    if not run(**vars(args)):
        print_help()
        sys.exit(1)

