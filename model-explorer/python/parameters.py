#!/usr/bin/env python

class Parameters():
    ''' The Parameter class stores the input parameters.
    '''
    def __init__(self):
        self.model_file_name = None
        self.check_area = None
        self.angle = None
        self.area_tolerance = 1e-4
        self.use_feature_angle = False
        self.show_faces = None
        self.show_edges = None
        self.filter_faces = None

