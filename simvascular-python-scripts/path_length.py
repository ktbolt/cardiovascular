#!/usr/bin/env python

"""
This script is used to compute the length of a path created by the 
SimVascular 'SV Path Planning' module.

A Path name corresponds to a data node under the SimVascular 
'SV Data Manager' 'Paths' node. 

Example: SimVascular DemoProject

    >>> aorta_path = PathLength('aorta')
    [PathDistance] Repository name: aortaRepo
    [PathDistance] Add aortaRepo to the repository.
    [PathDistance] Number of control points:  27
    >>> aorta_path.length()
    >>> 

"""

from sv import *
import vtk
import math

class PathLength(object):
    """ This class is used to calculate the length of a path.
    """
    def __init__(self, path_name):
        """ 
        Initialize the PathLength object

        Args:
            path_name (string): The name of a SimVascular Path data node.
        """
        self.path_name = path_name
        self.repo_path_name = path_name + 'Repo'
        print('[PathLength] Repository name: {0:s}'.format(self.repo_path_name))

        # Add the Path to the Repository.
        if int(Repository.Exists(self.repo_path_name)):
            print('[PathLength] {0:s} is already in the repository.'.format(self.repo_path_name))
        else:
            GUI.ExportPathToRepos(self.path_name, self.repo_path_name)
            print('[PathLength] Add {0:s} to the repository.'.format(self.repo_path_name))

        self.path = Path.pyPath()
        self.path.GetObject(self.repo_path_name)

        # Get the path's control points.
        self.control_points = self.path.GetControlPts()
        self.num_control_points = len(self.control_points)
        self.path_points = self.path.GetPathPosPts()
        self.num_path_points = len(self.path_points)
        print('[PathLength] Number of path points: {0:3d}'.format(self.num_path_points))

    def length(self):
        """ 
        Calculate the path length.
        """
        length = 0.0
        for id in range(0, self.num_path_points-1):
            p1 = self.path_points[id]
            p2 = self.path_points[id+1]
            dist_squared = vtk.vtkMath.Distance2BetweenPoints(p1,p2)
            length += math.sqrt(dist_squared)
        #_for id in range(0, self.num_path_points-1)

        print('[PathLength] Path length: {0:g}'.format(length))
        return length
   
