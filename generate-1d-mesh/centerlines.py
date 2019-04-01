#!/usr/bin/env python

"""
The module is used to extact centerlins from a surface mesh. 
"""
import logging
import os
from pathlib import Path
import numpy as np

from manage import get_logger_name
import vtk

from vmtk import vtkvmtk,vmtkscripts

SurfaceFileFormats = ["vtk", "vtp"] 

logger = logging.getLogger(get_logger_name())

def extract_center_lines(params):
    """ Extract the centerlines of a surface.
    """
    ## Read surface model.
    read_surfaces(params)

    ## Read surface used for centerline calculation.
    logger.info("Read surface model from %s" % params.surface_model)
    surface_mesh = read_surface(params.surface_model)
    #print(surface_mesh)

    ## Extract centerlines using vmtk.
    centerlines = vmtkscripts.vmtkCenterlines()
    centerlines.Surface = surface_mesh 
    centerlines.SeedSelectorName = "pointlist"
    centerlines.AppendEndPoints = 1
    centerlines.SourcePoints = params.inlet_center
    centerlines.TargetPoints = params.outlet_centers
    centerlines.Execute()
    #centerlines_output = centerlines.Centerlines

def read_surfaces(params):
    """ Read surface data and calculate inlet/outlet ceneters.

        Surface inlet and outlet faces are identifed by their file name. 
    """
    surf_mesh_dir = Path(params.boundary_surfaces_dir)
    params.outlet_face_names = []

    for face_file in surf_mesh_dir.iterdir():
        file_name = face_file.name
        logger.debug("Surface file name: %s" % file_name)
        file_suffix = face_file.suffix.lower()[1:]

        if file_suffix not in SurfaceFileFormats or file_name.lower().startswith('wall'):
            continue

        if (face_file.stem == "inflow"):
            inlet_path = str(face_file.absolute())
            logger.info("Inlet file: %s" % inlet_path)
            polydata = read_surface(inlet_path, file_suffix)
            params.inlet_center = get_polydata_centroid(polydata)
        else:
            outlet_path = str(face_file.absolute())
            params.outlet_face_names.append(face_file.stem)
            logger.info("Outlet: %s" % file_name)
            polydata = read_surface(outlet_path, file_suffix)
            params.outlet_centers.extend(get_polydata_centroid(polydata))
    #__for face_file in surf_mesh_dir.iterdir()

    logger.info("Number of outlet faces: %d" % len(params.outlet_centers))


def get_polydata_centroid(poly_data):
    """ Calculate the centroid of polydata.
    """
    x_list = []
    y_list = []
    z_list = []
    cx = 0.0;
    cy = 0.0;
    cz = 0.0;
    num_pts = poly_data.GetNumberOfPoints()

    for i in range(num_pts): 
        point = poly_data.GetPoints().GetPoint(i)
        cx += point[0]
        cy += point[1]
        cz += point[2]

    return [cx/num_pts, cy/num_pts, cz/num_pts]


def read_surface(file_name, file_format="vtp", datatype=None):
    """
    Read surface geometry from a file.

    Args:
        file_name (str): Path to input file.
        file_format (str): File format (.vtp, .stl, etc.). 
        datatype (str): Additional parameter for vtkIdList objects.

    Returns:
        polyData (vtkSTL/vtkPolyData/vtkXMLStructured/
                    vtkXMLRectilinear/vtkXMLPolydata/vtkXMLUnstructured/
                    vtkXMLImage/Tecplot): Output data.
    """

    # Check if file exists
    if not os.path.exists(file_name):
        raise RuntimeError("Could not find file: %s" % file_name)

    # Get reader
    if file_format == 'stl':
        reader = vtk.vtkSTLReader()
        reader.MergingOn()
    elif file_format == 'vtk':
        reader = vtk.vtkPolyDataReader()
    elif file_format == 'vtp':
        reader = vtk.vtkXMLPolyDataReader()
    elif file_format == 'vts':
        reader = vtk.vtkXMinkorporereLStructuredGridReader()
    elif file_format == 'vtr':
        reader = vtk.vtkXMLRectilinearGridReader()
    elif file_format == 'vtu':
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif file_format == "vti":
        reader = vtk.vtkXMLImageDataReader()
    elif file_format == "np" and datatype == "vtkIdList":
        result = np.load(filename).astype(np.int)
        id_list = vtk.vtkIdList()
        id_list.SetNumberOfIds(result.shape[0])
        for i in range(result.shape[0]):
            id_list.SetId(i, result[i])
        return id_list
    else:
        raise RuntimeError('Unknown file type %s' % file_format)

    # Read surface geometry.
    reader.SetFileName(file_name)
    reader.Update()
    polydata = reader.GetOutput()
    polygons = polydata.GetPolys()
    num_polys = polygons.GetNumberOfCells()
    logger.info("Read surface from %s" % file_name)
    logger.info("  Number of polygons %d" % num_polys)

    return polydata

def read_bc(params):
    """ Read BC files.
    
    """
    BClist = []

    with open(BCfile) as file:
        if outflowBC == "RESISTANCE":
            for line in file:
                #print "line=",line
                BClist.append(float(line))
            #__for line in file

            if len(BClist)!=len(outletfacename):
                logger.error("The number of BC values %d  is not consistant with the number of outlets %d",
                  len(BClist), len(outletfacename))
                exit()

        elif outflowBC == "RCR":
            keyword = file.readline()
            # print"keyword=",keyword
            while True:
                tmp = file.readline()
                if tmp == keyword:
                    RCRval=[]
                    RCRval.append(float(file.readline()))
                    RCRval.append(float(file.readline()))
                    RCRval.append(float(file.readline()))
                    BClist.append(RCRval)
                if len(tmp) == 0:
                    break
           #__while True
        #__if outflowBC=="RCR"
    #__with open(BCfile) as file
  
    user_outlet_names = []

    with open(useroutletfile) as file:
        for line in file:
            useroutletname.extend(line.splitlines())

    logger.info("Number of user provided model outlet names: %d" % len(useroutletname))

    if len(useroutletname)!=len(outletfacename):
        logger.error("The number of user provided outlets is not consistant with the number of outlets in mesh-surfaces. Exit.")
        exit()

