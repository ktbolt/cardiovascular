#!/usr/bin/env python

""" 
This script is used to compare and visualize 1D solver results. 
"""
import argparse
import sys
import os 

from manage import get_logger_name, init_logging
from parameters import Parameters
from centerlines import *
from mesh import *
from utils import write_polydata, read_polydata

from matplotlib import pyplot as plt

logger = logging.getLogger(get_logger_name())

class Results():
    def __init__(self):
        self.file_name = None 
        self.data_name = None 
        self.time_step = None
        self.data = None
        self.compare_data = None
        self.time = None
        self.save_freq = 20
        self.vis_block_id = 0

    def read_data(self, file_name, data_name, time_step, compare=False):
        """ Read in data.
        """
        self.file_name = file_name 
        self.data_name = data_name
        self.time_step = time_step
        data = []
        with open(self.file_name) as dfile:
            for line in dfile:
                data.append([float(v) for v in line.strip().split()])
        #__with open(file_name) as file
        self.data = data
        dt = self.time_step * self.save_freq
        self.time = [i*dt for i in range(len(data[0]))] 
        logger.info("Time size: %d" % (len(self.time)))
        logger.info("Time range: %g  %g" % (self.time[0], self.time[-1]))
        logger.info("Read %d data blocks from '%s'" % (len(data), self.file_name))
        logger.info("Data block size: %d" % (len(data[0])))

    def read_compare_data(self, file_name):
        """ Read in data to compare to first data read.
        """
        data = []
        with open(file_name) as dfile:
            for line in dfile:
                data.append([float(v) for v in line.strip().split()])
        #__with open(file_name) as file
        self.compare_data = data
        logger.info("Read compare %d data blocks from '%s'" % (len(data), self.file_name))
        logger.info("Compare data block size: %d" % (len(data[0])))

    def press_key(self, event):
        """ Add key events.

        Keys:
           q: key to quit.
        """
        if event.key == 'q':
            plt.close(event.canvas.figure)
        elif event.key.isdigit():
            self.vis_block_id = int(event.key)
            logger.info("Block number: %d" % self.vis_block_id)
            self.plot(self.vis_block_id)

    def plot(self, block_id):
        """ Plot data for the given block.
        """
        t = self.time
        v = self.data[block_id]
        ylabel = self.data_name
        title = self.data_name + " : block " + str(block_id)

        fig, ax = plt.subplots()
        ax.plot(t, v, 'r')
        #ax.plot(t, v, 'r', label='first')

        if self.compare_data:
            ax.plot(t, self.compare_data[block_id], 'b.', label='compare')

        ax.set(xlabel='time (s)', ylabel=ylabel, title=title)
        ax.grid()
        ax.legend()

        # Set the figure window position.
        plt.get_current_fig_manager().window.wm_geometry("+200+100")

        # Add key events.
        cid = plt.gcf().canvas.mpl_connect('key_press_event', self.press_key)

        plt.show() 

class Parameters():
    """ The Parameter class stores the input parameters.
    """
    class Units(object):
        MM = "mm"
        CM = "cm"

    def __init__(self):
        self.compare_file_name = None
        self.data_name = None
        self.file_name = None
        self.time_step = 0.000588 
 
class Args(object):
    """ This class defines the command line arguments to the vis script.
    """
    PREFIX = "--"
    COMPARE_FILE_NAME = "compare_file_name"
    DATA_NAME = "data_name"
    FILE_NAME = "file_name"
    TIME_STEP = "time_step"
    
def cmd(name):
    """ Create an argparse command argument.
    """
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    """ Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.COMPARE_FILE_NAME), 
      help="Compare file name.")

    parser.add_argument(cmd(Args.DATA_NAME), required=True,
      help="Data name.")

    parser.add_argument(cmd(Args.FILE_NAME), required=True,
      help="File name.")

    parser.add_argument(cmd(Args.TIME_STEP), 
      help="Time step.")

    return parser.parse_args(), parser.print_help

def set_parameters(**kwargs):
    """ Set the values of parameters input from the command line.
    """
    logger.info("Parse arguments ...")
    print(kwargs)

    ## Create a Parameters object to store parameters.
    params = Parameters()

    ## Process arguments.
    #
    if kwargs.get(Args.COMPARE_FILE_NAME):
        params.compare_file_name = kwargs.get(Args.COMPARE_FILE_NAME)
        if not os.path.exists(params.compare_file_name):
            logger.error("The file name '%s' was not found." % params.compare_file_name)
            return None
        logger.info("Compare file name: '%s'." % params.compare_file_name)

    params.data_name = kwargs.get(Args.DATA_NAME)
    logger.info("Data name: %s" % params.data_name)

    params.file_name = kwargs.get(Args.FILE_NAME)
    if not os.path.exists(params.file_name):
        logger.error("The file name '%s' was not found." % params.file_name)
        return None

    if kwargs.get(Args.TIME_STEP): 
        params.time_step = float(kwargs.get(Args.TIME_STEP))
    logger.info("Time step: %g" % params.time_step)

    return params 

if __name__ == '__main__':
    init_logging()
    args, print_help = parse_args()
    params = set_parameters(**vars(args))

    if params == None:
        sys.exit()

    results = Results()
    results.read_data(params.file_name, params.data_name, params.time_step)

    if params.compare_file_name: 
        results.read_compare_data(params.compare_file_name)
    results.plot(0)

