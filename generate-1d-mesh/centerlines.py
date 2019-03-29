#!/usr/bin/env python

"""
The module is used to extact centerlins from a surface mesh. 
"""
import logging
import os
from pathlib import Path

from manage import get_logger_name
import vtk

def extract_center_lines(params):

    logger = logging.getLogger(get_logger_name())
    surf_mesh_dir = Path(params.surface_mesh_dir)
    outlet_face_names = []

    for face_file in surf_mesh_dir.iterdir():
        file_name = face_file.name
        logger.info("Surface file name: %s" % file_name) 
        file_suffix = face_file.suffix.lower()

        if not file_name.lower().startswith('wall'):
          if ((face_file.stem == "inflow") and (file_suffix in [".vtk",".vtp"])):
            #((file_suffix == ".vtk") or (file_suffix ==".vtp"))):
              inlet_path = str(face_file.absolute())
              logger.info("inlet: %s" % inlet_path)
              polydata = read_polydata(face_file)
              #polydata = read_polydata(inlet_path)
              #inlet_center_=_centroid(inlet_path)
          if face_file.stem!="inflow" and (face_file.suffix ==".vtk" or face_file.suffix ==".vtp"):
              outlet_path = str(face_file.absolute())
              outlet_face_names.append(face_file.stem)
              print( "outlet= %s" %file_name)
              #outlet_centers.extend(centroid(outletpath))

    #__for face_file in surf_mesh_dir.iterdir()



def read_polydata(poly_file, datatype=None):
    """
    Read VTK .vtp file. 

    Args:
        filename (str): Path to input file.
        datatype (str): Additional parameter for vtkIdList objects.

    Returns:
        polyData (vtkSTL/vtkPolyData/vtkXMLStructured/
                    vtkXMLRectilinear/vtkXMLPolydata/vtkXMLUnstructured/
                    vtkXMLImage/Tecplot): Output data.
    """

    # Check if file exists
    if not Path.exists(poly_file):
        raise RuntimeError("Could not find file: %s" % poly_file.name)

    # Check filename format
    file_name = poly_file.name
    fileType = file_name.split(".")[-1]
    if fileType == '':
        raise RuntimeError('The file does not have an extension')

    # Get reader
    if fileType == 'stl':
        reader = vtk.vtkSTLReader()
        reader.MergingOn()
    elif fileType == 'vtk':
        reader = vtk.vtkPolyDataReader()
    elif fileType == 'vtp':
        reader = vtk.vtkXMLPolyDataReader()
    elif fileType == 'vts':
        reader = vtk.vtkXMinkorporereLStructuredGridReader()
    elif fileType == 'vtr':
        reader = vtk.vtkXMLRectilinearGridReader()
    elif fileType == 'vtu':
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif fileType == "vti":
        reader = vtk.vtkXMLImageDataReader()
    elif fileType == "np" and datatype == "vtkIdList":
        result = np.load(filename).astype(np.int)
        id_list = vtk.vtkIdList()
        id_list.SetNumberOfIds(result.shape[0])
        for i in range(result.shape[0]):
            id_list.SetId(i, result[i])
        return id_list
    else:
        raise RuntimeError('Unknown file type %s' % fileType)

    # Read
    reader.SetFileName(file_name)
    reader.Update()
    polydata = reader.GetOutput()

    return polydata
