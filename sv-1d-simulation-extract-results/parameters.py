#!/usr/bin/env python

class Parameters():
    """ The Parameter class stores the input parameters.
    """
    FILE_NAME_SEP = "_"
    DATA_FILE_EXTENSION = ".dat"
    def __init__(self):
        self.data_names = None
        self.data_location = None

        self.output_directory = None
        self.results_directory = None

        ## Solver parameters.
        self.solver_file_name = None
        self.model_name = None
        self.segments = None
        self.num_steps = None
        self.time_step = None

        self.output_file_name = None
        self.output_format = None 

