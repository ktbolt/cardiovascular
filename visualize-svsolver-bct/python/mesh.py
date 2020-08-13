#!/usr/bin/env python

import vtk
from math import sqrt

class Mesh(object):

    def __init__(self):
        self.surface = None
        self.graphics = None
        self.velocity_data = None
        self.num_time_steps = None 
        self.min_vel_mag = None 
        self.max_vel_mag = None 

    def read_mesh(self, file_name):
        '''Read in a surface mesh.
        '''
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        self.surface = reader.GetOutput()
        num_points = self.surface.GetPoints().GetNumberOfPoints()
        print("Number of points: %d" % num_points)
        num_polys = self.surface.GetPolys().GetNumberOfCells()
        print("Number of triangles: %d" % num_polys)

        ## Compute surface area.
        mass_props = vtk.vtkMassProperties()
        mass_props.SetInputData(self.surface)
        mass_props.Update()
        surf_area = mass_props.GetSurfaceArea()
        print("Mesh surface area: {0:f}".format(surf_area))

        ## Get velocity data.
        self.get_data_arrays()

    def get_data_arrays(self):
      num_point_arrays = self.surface.GetPointData().GetNumberOfArrays()
      print("[Mesh.get_data_arrays] Number of PointData arrays: {0:d}".format(num_point_arrays))
      print("[Mesh.get_data_arrays] PointData arrays: ")

      self.velocity_data = {}
      time_step = 0
      max_mag = 0.0
      min_mag = 1e9
      for i in range(num_point_arrays):
          data_type_id = self.surface.GetPointData().GetArray(i).GetDataType() 
          array_name = self.surface.GetPointData().GetArrayName(i)
          #print("[Mesh.get_data_arrays] Array {0:d}  {1:s} ".format(i, array_name))
          if 'velocity' not in array_name:
              continue
          time = array_name[array_name.find("_")+1:]
          #print("[Mesh.get_data_arrays] Time {0:s} ".format(time))
          time_step += 1
          data = self.surface.GetPointData().GetArray(array_name)
          self.velocity_data[time_step] = (time, data)
          num_data = data.GetNumberOfTuples()

          for j in range(num_data):
              vel = data.GetTuple(j)
              mag = sqrt(vel[0]*vel[0] + vel[1]*vel[1] + vel[2]*vel[2])
              if mag > max_mag: 
                  max_mag = mag
              elif mag < min_mag: 
                  min_mag = mag

      self.num_time_steps = time_step
      self.min_vel_mag = min_mag 
      self.max_vel_mag = max_mag 

