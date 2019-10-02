#!/usr/bin/env python

"""
This script is used to fit a cylinder to two control points on a path.

A Path name corresponds to a data node under the SimVascular 
'SV Data Manager' 'Paths' node. 

Example: SimVascular DemoProject

    aorta = PathFitCyl('aorta')

    id1 = 7
    id2 = 8
    radius = 1.0
    aorta.fit(id1, id2, radius)

    PathFitCyl] Repository name: aortaRepo
    [PathFitCyl] Add aortaRepo to the repository.
    [PathFitCyl] Number of control points:  27
    [PathFitCyl] Number of path points: 616
    [PathFitCyl] Distance between control points 7 8 : 2.38058
    [PathFitCyl] Point1: [-0.138486 1.017057 0.335150]
    [PathFitCyl] Point2: [-0.241842 1.740550 -1.930475]
    [PathFitCyl] Axis: [0.043416 -0.303914 0.951710]
    [PathFitCyl] Center: [-0.190164 1.378804 -0.797662]
"""

from sv import *
import math
import os
import vtk

class PathFitCyl(object):
    """ 
    This class is used to fit a cylinder to a path at a given point.
    """
    def __init__(self, path_name):
        """ 
        Initialize the PathFitCylobject

        Args:
            path_name (string): The name of a SimVascular Path data node.
        """
        self.path_name = path_name
        self.repo_path_name = path_name + 'Repo'
        print('[PathFitCyl] Repository name: {0:s}'.format(self.repo_path_name))
        self.write_directory = os.getcwd()
        print('[PathFitCyl] Writing to default directory {0:s} '.format(self.write_directory))
        if not os.access(self.write_directory, os.W_OK):
            print("[PathFitCyl] **** ERROR: Can't write to directory: {0:s}".format(self.write_directory))
            print("[PathFitCyl]             Set directory using the 'set_write_directory' method.")

        # Add the Path to the Repository.
        if int(Repository.Exists(self.repo_path_name)):
            print('[PathFitCyl] {0:s} is already in the repository.'.format(self.repo_path_name))
        else:
            GUI.ExportPathToRepos(self.path_name, self.repo_path_name)
            print('[PathFitCyl] Add {0:s} to the repository.'.format(self.repo_path_name))

        self.path = Path.pyPath()
        self.path.GetObject(self.repo_path_name)

        # Get the path's control points.
        self.control_points = self.path.GetControlPts()
        self.num_control_points = len(self.control_points)
        print('[PathFitCyl] Number of control points: {0:3d}'.format(self.num_control_points))

        # Get the path's points.
        self.points = self.path.GetPathPosPts()
        self.num_points = len(self.points)
        print('[PathFitCyl] Number of path points: {0:3d}'.format(self.num_points))

    def set_write_directory(self, path):
        """
        Set the directory to write cylinder polygon mesh data.
        """
        if not os.path.isdir(path):
            print("[PathFitCyl] **** ERROR: '{0:s}' is not a directory.".format(path))
            return

        if not os.path.exists(path):
            print("[PathFitCyl] **** ERROR: Directory '{0:s}' does not exist.".format(path))
            return

        if not os.access(path, os.W_OK):
            print("[PathFitCyl] **** ERROR: Can't write to directory: {0:s}".format(path))
            return
     
        self.write_directory = path 

    def fit(self, id1, id2, radius):
        """ 
        Fit a cylinder between two control points.

        The cylinder axis and length is defined by two control points on a path.

        Args:
            id1 (int): First control point ID. 
            id2 (int): Second control point ID. 
            radius (float): Cylinder radius.
        """
        pt1 = self.control_points[id1];
        pt2 = self.control_points[id2];
        dist_squared = vtk.vtkMath.Distance2BetweenPoints(pt1,pt2)
        dist = math.sqrt(dist_squared)
        print('[PathFitCyl] Distance between control points {0:d} {1:d} : {2:g}'.format(id1, id2, dist))

        ## Compute the cylinder axis and center.
        #
        axis = [pt1[i] - pt2[i] for i in range(0,3)]
        vtk.vtkMath.Normalize(axis)
        center = [(pt1[i] + pt2[i])/2.0 for i in range(0,3)]
        print('[PathFitCyl] Point1: [{0:f} {1:f} {2:f}]'.format(pt1[0], pt1[1], pt1[2]))
        print('[PathFitCyl] Point2: [{0:f} {1:f} {2:f}]'.format(pt2[0], pt2[1], pt2[2]))
        print('[PathFitCyl] Axis: [{0:f} {1:f} {2:f}]'.format(axis[0], axis[1], axis[2]))
        print('[PathFitCyl] Center: [{0:f} {1:f} {2:f}]'.format(center[0], center[1], center[2]))

        ## Create the cylinder.
        #
        # For now create a cylinder using create_cylinder() 
        # as a work around for a bug in solid.Cylinder().
        #
        # A cylinder geometry is created using VTK and written to a file
        # named 'cylinder.vtp'. It is then read back in so it can be 
        # displayed in SV. This is another work around for a missing
        # function in the SV Python API.
        #
        use_solid = False
        cyl_name = self.path_name + '_fit_cylinder_' + str(id1) + '_' + str(id2)
        cyl_pdname = cyl_name 
        print('[PathFitCyl] Creating cylinder {0:s} '.format(cyl_pdname))

        ## Remove cylinder if it is already in the repository.
        #
        # [TODO] Repository.Delete() does not work so need to
        # manuallt remove objects from the Repository.
        #
        if Repository.Exists(cyl_pdname):
            print('[PathFitCyl] Remove cylinder {0:s} '.format(cyl_pdname))
            Repository.Delete(cyl_pdname)

        if use_solid:
            Solid.SetKernel('PolyData')
            solid = Solid.pySolidModel()
            length = dist
            solid.Cylinder(cyl_name, radius, length, center, axis)
            solid.GetPolyData(cyl_pdname, 0.5)
            GUI.ImportPolyDataFromRepos(cyl_pdname)
        else:
            cyl = self.create_cylinder(pt1, pt2, radius)
            writer = vtk.vtkPolyDataWriter()
            #writer = vtk.vtkXMLPolyDataWriter()
            file_name = self.write_directory + os.path.sep + cyl_name + ".vtp"
         
            try:
                writer.SetFileName(file_name)
                writer.SetInputData(cyl)
                writer.Update()
                Repository.ReadVtkPolyData(cyl_pdname, file_name)
                GUI.ImportPolyDataFromRepos(cyl_pdname)
            except:
                print("[PathFitCyl] ****ERROR: Can't write to {0:s} ".format(dir))

        return dist

    def create_cylinder(self, pt1, pt2, radius):
        """
        Create a cylinder aligned between two points.

        This function creates a cylinder using VTK and returns it as
        Polydata. This is a work around for the solid.Cylinder() bug.
        """
        ## Compute the cylinder axis and center.
        axis = [pt1[i] - pt2[i] for i in range(0,3)]
        length = vtk.vtkMath.Normalize(axis)
        center = [(pt1[i] + pt2[i])/2.0 for i in range(0,3)]

        # Determine angle to rotate cylinder into given axis.
        vec = [ 0.0, 1.0, 0.0 ]
        rotate_axis = 3*[0.0]
        tmp_cross = 3*[0.0]
        vtk.vtkMath.Cross(vec, axis, rotate_axis)
        radangle = math.atan2(vtk.vtkMath.Norm(rotate_axis), vtk.vtkMath.Dot(axis,vec))
        degangle = vtk.vtkMath.DegreesFromRadians(radangle)

        # Create cylinder.
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetCenter(0.0,0.0,0.0);
        cylinder.SetHeight(length);
        cylinder.SetRadius(radius);
        cylinder.SetResolution(32)
        cylinder.Update()

        # Transform.
        transformer = vtk.vtkTransform()
        transformer.Translate(center[0], center[1], center[2])
        transformer.RotateWXYZ(degangle,rotate_axis)

        # Get the polydata (polygon mesh) for the transformed cylinder.
        polyDataTransformer = vtk.vtkTransformPolyDataFilter()
        polyDataTransformer.SetInputData(cylinder.GetOutput())
        polyDataTransformer.SetTransform(transformer)
        polyDataTransformer.Update()
        return polyDataTransformer.GetOutput()
    #_def create_cylinder(self, pt1, pt2, radius)

#_class PathFitCyl(object)

## Test
#
# This test is used for the SV Demo project.
#
test_demo = False

if test_demo:
    path_name = 'aorta'
    id1 = 7
    id2 = 8
    radius = 1.0
    aorta = PathFitCyl(path_name)
    aorta.fit(id1, id2, radius)
   
