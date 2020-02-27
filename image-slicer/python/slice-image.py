#!/usr/bin/env python

""" 
This script extracts slices from a 3D image volume. 

"""
import argparse
import sys
import os
import logging

from manage import get_logger_name, init_logging, get_log_file_name
from parameters import Parameters
from image import Image
from graphics import Graphics
from path import Path 

logger = logging.getLogger(get_logger_name())

class Args(object):
    """ This class defines the command line arguments to the generate-1d-mesh script.
    """
    PREFIX = "--"
    IMAGE_FILE = "image_file_name"
    PATH_FILE = "path_file_name"

def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.IMAGE_FILE), help="The image (.vti) file.")
    parser.add_argument(cmd(Args.PATH_FILE), help="The path (.pth) file.")

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
    if kwargs.get(Args.IMAGE_FILE):
        params.image_file_name = kwargs.get(Args.IMAGE_FILE)
        logger.info("Image file: %s" % params.image_file_name)
        if not os.path.exists(params.image_file_name):
            logger.error("The image file '%s' was not found." % params.image_file_name)
            return None

    if kwargs.get(Args.PATH_FILE):
        params.path_file_name = kwargs.get(Args.PATH_FILE)
        logger.info("Path file: %s" % params.path_file_name)
        if not os.path.exists(params.path_file_name):
            logger.error("The path file '%s' was not found." % params.path_file_name)
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

    ## Read in the volume image.
    #
    image = Image(params)
    image.graphics = graphics
    image.read_volume()
    image.display_edges()
    # Extract an isosurface.
    #image.extract_isosurface(110)
    # Show some slices in ijk.
    #image.display_axis_slice('i', 255)
    #image.display_axis_slice('j', 30)
    #image.display_axis_slice('k', 255)

    ## Read in the paths.
    #
    paths = Path.read_path_file(params, graphics)
    for path in paths:
        path.create_path_geometry()

    graphics.show()


