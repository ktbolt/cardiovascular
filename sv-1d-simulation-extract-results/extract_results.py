#!/usr/bin/env python

""" 
This script is used to extract data from 1D solver results files. 
"""
import argparse
import os 
import sys
import logging

from manage import get_logger_name, init_logging
from parameters import Parameters
from solver import Solver

logger = logging.getLogger(get_logger_name())

class Args(object):
    """ This class defines the command line arguments to the vis script.
    """
    PREFIX = "--"
    DATA_NAME = "data_name"
    OUTPUT_DIRECTORY  = "output_directory"
    SEGMENTS = "segments"
    SOLVER_FILE = "solver_file_name"
    
def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.DATA_NAME),
      help="Data name.")

    parser.add_argument(cmd(Args.OUTPUT_DIRECTORY), required=True,
      help="Output directory.")

    parser.add_argument(cmd(Args.SEGMENTS), 
      help="Segment names.")

    parser.add_argument(cmd(Args.SOLVER_FILE), required=True,
      help="Solver .in file.")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    """ Set the values of parameters input from the command line.
    """
    logger.info("Parse arguments ...")

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.OUTPUT_DIRECTORY):
        params.output_directory = kwargs.get(Args.OUTPUT_DIRECTORY)
        if not os.path.exists(params.output_directory):
            logger.error("The output directory '%s' was not found." % params.output_directory)
            return None
        logger.info("Output directory: '%s'." % params.output_directory)

    params.solver_file_name = kwargs.get(Args.SOLVER_FILE)
    logger.info("Solver file name: %s" % params.solver_file_name)

    params.data_name = kwargs.get(Args.DATA_NAME)
    logger.info("Data name: %s" % params.data_name)

    params.segments = kwargs.get(Args.SEGMENTS)
    logger.info("Segments: %s" % params.segments)

    return params 

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))

    if params == None:
        sys.exit()

    ## Read in the solver file.
    solver = Solver(params)
    solver.read_solver_file()

    ## Read segment data.
    for segment in params.segments.split():
        solver.read_segment_data_file(segment, params.data_name)


