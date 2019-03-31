#!/usr/bin/env python

"""
The Parameter class stores the input parameters for a 1D mesh generation.
"""

class Parameters():
    def __init__(self):

        # Surface mesh.
        self.surface_mesh_dir = ''

        self.inlet_center = None
        self.outlet_centers = []

        # Physical parameters.
        self.density = 1.055
        self.viscosity = 0.04
        self.mattype = "OLUFSEN"
        self.c1 = 0.0e7
        self.c2 = -22.5267
        self.c3 = 2.65e5

