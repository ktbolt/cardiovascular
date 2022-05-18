#!/usr/bin/env python

''' 
This script extracts 2D image slices from a 3D image volume. 
'''
import argparse
import sys
import os
import logging

from manage import get_logger_name, init_logging, get_log_file_name
import numpy as np
from parameters import Parameters
from image import Image
from graphics import Graphics
from model import Model  
from path import Path 

logger = logging.getLogger(get_logger_name())

class Args(object):
    ''' This class defines the command line arguments to the generate-1d-mesh script.
    '''
    PREFIX = "--"
    ENABLE_GRAPHICS = "enable_graphics"
    EXTRACT_SLICES = "extract_slices"
    IMAGE_FILE = "image_file_name"
    MODEL_FILE = "model_file_name"
    PATH_FILE = "path_file_name"
    PATH_SAMPLE_METHOD = "path_sample_method"
    RESULTS_DIRECTORY = "results_directory"
    SLICE_INCREMENT = "slice_increment"
    SLICE_WIDTH = "slice_width"

def cmd(name):
    ''' Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    ''' Parse command-line arguments.'''
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.ENABLE_GRAPHICS), help="Enable graphics to show geomemtry in a graphics window.")
    parser.add_argument(cmd(Args.EXTRACT_SLICES), help="Automatically extract slices using the slice increment.")
    parser.add_argument(cmd(Args.IMAGE_FILE), help="The image (.vti) file.")
    parser.add_argument(cmd(Args.MODEL_FILE), help="The model (.vtp) file.")
    parser.add_argument(cmd(Args.PATH_FILE), help="The path (.pth) file.")
    parser.add_argument(cmd(Args.PATH_SAMPLE_METHOD), help="The method used to sample path points: number, distance")
    parser.add_argument(cmd(Args.RESULTS_DIRECTORY), help="The directory to write image slice and model slice files.")
    parser.add_argument(cmd(Args.SLICE_INCREMENT), help="The slice increment along a path.")
    parser.add_argument(cmd(Args.SLICE_WIDTH), help="The width of a slice plane.")

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
    if kwargs.get(Args.ENABLE_GRAPHICS):
        params.enable_graphics = kwargs.get(Args.ENABLE_GRAPHICS) in ['true', 'True']

    if kwargs.get(Args.EXTRACT_SLICES):
        params.extract_slices = kwargs.get(Args.EXTRACT_SLICES) in ['true', 'True']

    if kwargs.get(Args.IMAGE_FILE):
        params.image_file_name = kwargs.get(Args.IMAGE_FILE)
        logger.info("Image file: %s" % params.image_file_name)
        if not os.path.exists(params.image_file_name):
            logger.error("The image file '%s' was not found." % params.image_file_name)
            return None

    if kwargs.get(Args.MODEL_FILE):
        params.model_file_name = kwargs.get(Args.MODEL_FILE)
        logger.info("Model file: %s" % params.model_file_name)
        if not os.path.exists(params.model_file_name):
            logger.error("The model file '%s' was not found." % params.model_file_name)
            return None

    if kwargs.get(Args.PATH_FILE):
        params.path_file_name = kwargs.get(Args.PATH_FILE)
        logger.info("Path file: %s" % params.path_file_name)
        if not os.path.exists(params.path_file_name):
            logger.error("The path file '%s' was not found." % params.path_file_name)
            return None

    if kwargs.get(Args.PATH_SAMPLE_METHOD):
        params.path_sample_method = kwargs.get(Args.PATH_SAMPLE_METHOD)

    if kwargs.get(Args.RESULTS_DIRECTORY):
        params.results_directory = kwargs.get(Args.RESULTS_DIRECTORY)

    if kwargs.get(Args.SLICE_INCREMENT):
        params.slice_increment = int(kwargs.get(Args.SLICE_INCREMENT))
        logger.info("Slice increment:  %d" % params.slice_increment)

    if kwargs.get(Args.SLICE_WIDTH):
        params.slice_width= float(kwargs.get(Args.SLICE_WIDTH))
        logger.info("Slice width:  %g" % params.slice_width)

    return params

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))
    if not params:
        logger.error("Error in parameters.")
        sys.exit(1)

    ## Create graphics interface.   
    graphics = Graphics(params, params.enable_graphics)

    ## Read in the volume image.
    image = Image(params)
    image.graphics = graphics
    image.read_volume()
    image.display_edges()
    graphics.image = image

    ## Show some slices in ijk.
    #image.display_axis_slice('i', 255)
    #image.display_axis_slice('j', 30)
    #image.display_axis_slice('k', 255)

    ## Read in and display paths.
    paths = Path.read_path_file(params, graphics)
    graphics.paths = paths 
    for path in paths:
        path.create_path_geometry()

    ## Read in and display model.
    model = Model(params, graphics)
    model.read_model_file()
    model.create_model_geometry()
    graphics.model = model

    if params.extract_slices:
        graphics.auto_slice()

    ## Show image, paths and model. 
    graphics.show()

