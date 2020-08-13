#!/usr/bin/env python

''' This script is used to visualize a bct.vtp file.  

    It prints out the node IDs and coordinates for each entry in the file.
'''
import os
import sys
import vtk
from graphics import Graphics
from mesh import Mesh 

def print_data(mesh):
    num_points = mesh.GetNumberOfPoints()
    points = mesh.GetPoints()
    num_cells = mesh.GetNumberOfCells()

    print("Nodel coordinates: ") 
    node_ids = mesh.GetPointData().GetArray('GlobalNodeID')
    pt = 3*[0.0]
    for i in range(num_points):
        nid = node_ids.GetValue(i)
        points.GetPoint(i, pt)
        print("i:{0:d} nodeID:{1:d}  point:{2:s}".format(i, nid, str(pt)))

if __name__ == '__main__':

    ## Read vtp file.
    file_name = sys.argv[1]

    if len(sys.argv) == 3:
       scale = float(sys.argv[2])
    else:
       scale = 1.0

    print("Scale: {0:f}".format(scale))

    ## Create graphics interface.   
    graphics = Graphics()

    ## Read in the surface mesh.
    mesh = Mesh()
    mesh.graphics = graphics
    mesh.read_mesh(file_name)
    graphics.add_graphics_geometry(mesh.surface, [0.8, 0.8, 0.8])

    graphics.mesh = mesh
    graphics.velocity_scale = scale
    graphics.show_velocity()

    graphics.show()


