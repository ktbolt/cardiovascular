#!/usr/bin/env python

'''
This script is used to merge .vtu and .vtp mesh files defining solid and fluid regions into a single .vtu and .vtp file.

The solid mesh is created in SV using extruded boundary layer meshing, the fluid mesh using interior boundary layer meshing.
The script removes the interior of the solid mesh using a region ID. The fluid and solid volume and surface meshes are then
merged and written to 'fluid_solid_mesh.vtu' and 'fluid_solid_mesh.vtp' files. 

An SV model .mdl file can be created by importing the 'fluid_solid_mesh.vtp' file as a model into SV. Each face can then be 
named and classified as a cap or wall. 

The .vtu, .vtp, and .mdl files can then be used by the 'create-fsi-mesh-complete.py' script to create the mesh files needed
for an FSI simulation.. 
'''

import argparse
import os
import sys
import vtk

class Args(object):
    '''This class defines the command line arguments to the script.
    '''
    PREFIX = "--"
    FLUID_MESH = "fluid_mesh"
    SOLID_MESH = "solid_mesh"
    SOLID_REGION_ID = "solid_region_id"

def cmd(name):
    '''Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    '''Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.FLUID_MESH),    help="The name of the fluid volume and surface meshes files.", required=True)
    parser.add_argument(cmd(Args.SOLID_MESH),    help="The name of the solid volume and surface meshes files.", required=True)
    parser.add_argument(cmd(Args.SOLID_REGION_ID), help="The solid region ID.", type=int, required=True)

    return parser.parse_args(), parser.print_help

def read_surface_mesh(file_name):
    print("[read_surface_mesh] file_name: " + file_name)
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    return reader.GetOutput()

def read_volume_mesh(file_name):
    print("[read_voluem_mesh] file_name: " + file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    return reader.GetOutput()

def write_surface_mesh(file_name, mesh):
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

def write_volume_mesh(file_name, mesh):
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

if __name__ == '__main__':

    args, print_help = parse_args()

    ## Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    # Read solid mesh and surface.
    solid_file_name = args.solid_mesh
    solid_mesh = read_volume_mesh(solid_file_name+'.vtu')
    solid_surf = read_surface_mesh(solid_file_name+'.vtp')

    # Extract solid extruded boundary layer (should be region ID 2).
    #
    region_id = int(args.solid_region_id)
    threshold = vtk.vtkThreshold()
    threshold.SetInputData(solid_mesh)
    threshold.SetInputArrayToProcess(0,0,0,1,"ModelRegionID")
    threshold.SetLowerThreshold(region_id)
    threshold.SetUpperThreshold(region_id)
    threshold.Update();
    solid_mesh_bl = threshold.GetOutput()
    write_volume_mesh('solid_mesh_bl.vtu', solid_mesh_bl)

    surf_threshold = vtk.vtkThreshold()
    surf_threshold.SetInputData(solid_surf)
    surf_threshold.SetInputArrayToProcess(0,0,0,1,"ModelRegionID")
    surf_threshold.SetLowerThreshold(region_id)
    surf_threshold.SetUpperThreshold(region_id)
    surf_threshold.Update();

    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(surf_threshold.GetOutput())
    surface_filter.Update()
    solid_surf_bl = surface_filter.GetOutput()
    write_surface_mesh('solid_mesh_bl.vtp', solid_surf_bl)

    # Read fluid mesh and surface.
    fluid_file_name = args.fluid_mesh
    fluid_mesh = read_volume_mesh(fluid_file_name+'.vtu')
    fluid_surf = read_surface_mesh(fluid_file_name+'.vtp')

    # Combine the solid and fluid meshes. 
    append_filter = vtk.vtkAppendFilter()
    append_filter.AddInputData(fluid_mesh)
    append_filter.AddInputData(solid_mesh_bl)
    append_filter.Update()
    fluid_solid_mesh = append_filter.GetOutput()
    write_volume_mesh('fluid_solid_mesh.vtu', fluid_solid_mesh)

    surf_append_filter = vtk.vtkAppendFilter()
    surf_append_filter.AddInputData(fluid_surf)
    surf_append_filter.AddInputData(solid_surf_bl)
    surf_append_filter.Update()

    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(surf_append_filter.GetOutput())
    surface_filter.Update()

    fluid_solid_surf = surface_filter.GetOutput()
    write_surface_mesh('fluid_solid_surf.vtp', fluid_solid_surf)


