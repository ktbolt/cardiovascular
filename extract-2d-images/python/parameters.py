#!/usr/bin/env python

class Parameters():
    '''The Parameter class stores the input parameters.
    '''
    def __init__(self):
        self.enable_graphics = False
        self.extract_slices = False
        self.image_file_name = None
        self.model_file_name = None
        self.path_file_name = None
        self.results_directory = "./"
        self.slice_increment = 10
        self.slice_width = 5

