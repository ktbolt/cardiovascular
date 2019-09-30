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
import vtk
import math

class PathFitCyl(object):
    """ This class is used to fit a cylinder to a path at a given point.
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
        Solid.SetKernel('PolyData')
        solid = Solid.pySolidModel()
        length = dist
        solid.Cylinder('cylinder', radius, length, center, axis)
        solid.GetPolyData('cylPolydata', 0.5)
        GUI.ImportPolyDataFromRepos('cylPolydata')

        return dist

## Test
aorta = PathFitCyl('aorta')
id1 = 7
id2 = 8
radius = 1.0
aorta.fit(id1, id2, radius)
   
