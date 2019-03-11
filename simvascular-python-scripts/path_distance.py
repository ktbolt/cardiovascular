#!/usr/bin/env python

"""
This script is used to compute the distance between two control points
on a path created by the SimVascular 'SV Path Planning' module.

A Path name corresponds to a data node under the SimVascular 
'SV Data Manager' 'Paths' node. 

Example: SimVascular DemoProject

    >>> aorta_dist = PathDistance('aorta')
    [PathDistance] Repository name: aortaRepo
    [PathDistance] Add aortaRepo to the repository.
    [PathDistance] Number of control points:  27
    >>> aorta_dist.dist(1,6)
    [PathDistance] Distance between control points 1 6 : 11.3838
    >>> 

"""

from sv import *
import vtk
import math

class PathDistance(object):
    """ This class is used to calculate distances between path control points.
    """
    def __init__(self, path_name):
        """ Initialize the PathDistance object
        Args:
            path_name (string): The name of a SimVascular Path data node.
        """
        self.path_name = path_name
        self.repo_path_name = path_name + 'Repo'
        print('[PathDistance] Repository name: {0:s}'.format(self.repo_path_name))

        # Add the Path to the Repository.
        if int(Repository.Exists(self.repo_path_name)):
            print('[PathDistance] {0:s} is already in the repository.'.format(self.repo_path_name))
        else:
            GUI.ExportPathToRepos(self.path_name, self.repo_path_name)
            print('[PathDistance] Add {0:s} to the repository.'.format(self.repo_path_name))

        self.path = Path.pyPath()
        self.path.GetObject(self.repo_path_name)

        # Get the path's control points.
        self.control_points = self.path.GetControlPts()
        self.num_control_points = len(self.control_points)
        print('[PathDistance] Number of control points: {0:3d}'.format(self.num_control_points))

    def dist(self, id1, id2):
        """ Calculate the distance between two control points.

        This function calculates the distance between two control point IDs
        id1 and id2 by summing the distance between adjacent control points.

        Args:
            id1 (int): The start ID. 
            id2 (int): The end ID. 
        """
        dist = 0.0
        for id in range(id1, id2+1):
            p1 = self.control_points[id];
            p2 = self.control_points[id+1];
            dist_squared = vtk.vtkMath.Distance2BetweenPoints(p1,p2)
            dist += math.sqrt(dist_squared)
        #_for id in range(id1, id2+1)

        print('[PathDistance] Distance between control points {0:d} {1:d} : {2:g}'.format(id1, id2, dist))
        return dist
   
