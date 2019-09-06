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
    DATA_NAMES = "data_names"
    DATA_LOCATION = "data_location"
    OUTPUT_DIRECTORY  = "output_directory"
    OUTPUT_FILE = "output_file_name"
    OUTPUT_FORMAT = "output_format"
    RESULTS_DIRECTORY  = "results_directory"
    SEGMENTS = "segments"
    SOLVER_FILE = "solver_file_name"
    
def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.DATA_LOCATION),
      help="Data location.")

    parser.add_argument(cmd(Args.DATA_NAMES),
      help="Data name.")

    parser.add_argument(cmd(Args.OUTPUT_DIRECTORY), 
      help="Output directory.")

    parser.add_argument(cmd(Args.OUTPUT_FILE), 
      help="Output file name.")

    parser.add_argument(cmd(Args.OUTPUT_FORMAT), 
      help="Output format.")

    parser.add_argument(cmd(Args.RESULTS_DIRECTORY), required=True,
      help="Results directory.")

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

    if kwargs.get(Args.RESULTS_DIRECTORY):
        params.results_directory = kwargs.get(Args.RESULTS_DIRECTORY)
        if not os.path.exists(params.results_directory):
            logger.error("The results directory '%s' was not found." % params.results_directory)
            return None
        logger.info("Results directory: '%s'." % params.results_directory)

    params.output_file_name = kwargs.get(Args.OUTPUT_FILE)
    logger.info("Output file name: %s" % params.output_file_name)

    params.output_format = kwargs.get(Args.OUTPUT_FORMAT)
    logger.info("Output format: %s" % params.output_format)

    params.solver_file_name = kwargs.get(Args.SOLVER_FILE)
    logger.info("Solver file name: %s" % params.solver_file_name)

    params.data_names = kwargs.get(Args.DATA_NAMES).split(",")
    logger.info("Data names: %s" % ','.join(params.data_names))

    params.data_location = kwargs.get(Args.DATA_LOCATION)
    logger.info("Data location: %s" % params.data_location)

    params.segments = kwargs.get(Args.SEGMENTS).split(",")
    logger.info("Segments: %s" % ','.join(params.segments))

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
    for segment in params.segments:
        solver.read_segment_data_file(segment, params.data_names)

    ## Write segment data.
    if params.output_file_name:
        solver.write_segment_data()

