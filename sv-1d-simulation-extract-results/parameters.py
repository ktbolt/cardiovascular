#!/usr/bin/env python

class Parameters():
    """ The Parameter class stores the input parameters.
    """
    FILE_NAME_SEP = "_"
    DATA_FILE_EXTENSION = ".dat"
    def __init__(self):
        self.solver_file_name = None
        self.model_name = None
        self.data_name = None
        self.segments = None
        self.output_directory = None
        self.num_steps = None
        self.time_step = None


