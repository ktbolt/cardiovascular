#!/usr/bin/env python
"""This script is used to create a series of SV segmentations from a surface. 
"""
import argparse
import os
import sys

from centerlines import Centerlines
from surface import Surface
import graphics as gr

def parse_args():
    '''Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("--centerline-file",  help="Input centerline .vtp file.")

    parser.add_argument("--sample-distance", type=float, default=1.0,
        help="The distance used to sample points along a centerline.")

    parser.add_argument('--average-normals', action="store_true", help="Average normals along sampling distance.")

    parser.add_argument("--surface-file",  required=True, help="Input surface (.stl or .vtp) file.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
       parser.print_help()
       sys.exit(1)

    return args

def main():
    # Get command-line arguments.
    args = parse_args()

    # Create renderer and graphics window.
    win_width = 1500
    win_height = 1500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    # Read in the segmentation surface.
    surface_file_name = args.surface_file 
    surface = Surface(gr, renderer_window, renderer)
    surface.read(surface_file_name)
    gr_geom = gr.add_geometry(renderer, surface.geometry, color=[0.8, 0.8, 1.0])
    surface.vtk_actor = gr_geom 
    #gr_geom.GetProperty().SetOpacity(0.5)
    surface.sample_distance = args.sample_distance 
    surface.average_normals = args.average_normals

    # Create a Centerlines object used to clip the surface.
    centerlines = Centerlines()
    centerlines.graphics = gr
    centerlines.surface = surface
    centerlines.window = renderer_window 
    centerlines.renderer = renderer

    if args.centerline_file != None:
        centerlines.read(args.centerline_file)

    print("\n")
    print("---------- Alphanumeric Keys ----------")
    print("c - Compute centerlines.")
    print("e - Extract surface slices along centerlines.")
    print("q - Quit")
    print("s - Select a centerline source point.")
    print("t - Select a centerline target point.")
    print("u - Undo the selection of a centerline source or target point.")
    print("\n")

    # Create a mouse interactor for selecting points on the surface 
    # used to compute a centerline.
    picking_keys = ['s', 't']
    event_table = {
        'c': (surface.compute_centerlines, surface),
        'e': (surface.extract_slices, surface),
        's': surface.add_centerlines_source_node,
        't': surface.add_centerlines_target_node
    }
    interactor = gr.init_picking(renderer_window, renderer, surface.geometry, picking_keys, event_table)

    # Display window.
    interactor.Start()

if __name__ == '__main__':
    main()

