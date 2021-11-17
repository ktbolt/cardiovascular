#!/usr/bin/env python

from collections import defaultdict
import os
import sys
import vtk

class VolumeMesh(object):
    ''' This class stores data for a volume mesh.
    '''
    def __init__(self, file_name):
      self.mesh = self.read_mesh(file_name)
      geom_filter = vtk.vtkGeometryFilter()
      geom_filter.SetInputData(self.mesh)
      geom_filter.Update()
      self.polydata = geom_filter.GetOutput()

      print("[VolumeMesh] ")
      print("[VolumeMesh] ========== VolumeMesh ==========")
      print("[VolumeMesh] file_name: " + file_name)

      num_points = self.mesh.GetNumberOfPoints()
      points = self.mesh.GetPoints()
      point_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      element_ids = self.mesh.GetCellData().GetArray("GlobalElementID")

      pt = 3*[0.0]
      max_x = -1e9
      max_y = -1e9
      max_z = -1e9
      min_x = 1e9
      min_y = 1e9
      min_z = 1e9

      for i in range(num_points):
          point = points.GetPoint(i, pt)
          x = pt[0]
          y = pt[1]
          z = pt[2]
          if x < min_x:
              min_x = x
          elif x > max_x:
              max_x = x
          if y < min_y:
              min_y = y
          elif y > max_y:
              max_y = y
          if z < min_z:
              min_z = z
          elif z > max_z:
              max_z = z
      #_for i in range(num_points)

      self.nodal_coords = {}
      point_hash = defaultdict(list)
      num_dupe_points = 0

      dx = (max_x - min_x)
      if dx != 0.0:
        self.dx = dx 
      else: 
        self.dx = 1.0

      dy = (max_y - min_y)
      if dy != 0.0:
        self.dy = dy 
      else: 
        self.dy = 1.0

      dz = (max_z - min_z)
      if dz != 0.0:
        self.dz = dz 
      else: 
        self.dz = 1.0

      for i in range(num_points):
          point = points.GetPoint(i, pt)
          if point_ids:
              pid = point_ids.GetValue(i)
          else: 
              pid = i+1
          x = pt[0]
          y = pt[1]
          z = pt[2]
          self.nodal_coords[pid] = [x, y, z]

          xs = (x - min_x) / self.dx 
          ys = (y - min_y) / self.dy 
          zs = (z - min_z) / self.dz 
          ih = xs * num_points
          jh = ys * num_points
          kh = zs * num_points
          index = int(ih + jh + kh) 
          pts = point_hash[index]
          if len(pts) == 0:
              point_hash[index].append([x, y, z, pid])
          else:
              found_pt = False
              for hpt in pts:
                  ddx = hpt[0] - pt[0]
                  ddy = hpt[1] - pt[1]
                  ddz = hpt[2] - pt[2]
                  d = ddx*ddx + ddy*ddy + ddz*ddz
                  if d == 0.0:
                      found_pt = True
                      num_dupe_points += 1
                      break
              #_for hpt in pts
              if not found_pt:
                  point_hash[index].append([x, y, z, pid])
      #_for i in range(num_points)

      print("[VolumeMesh] ")
      print("[VolumeMesh] ========== Nodes ==========")
      print("[VolumeMesh] Number of nodes: {0:d}".format(num_points))
      for nid, point in self.nodal_coords.items():
      #for nid, point in sorted(self.nodal_coords.items()):
          print("[VolumeMesh] {0:d}: {1:f} {2:f} {3:f}".format(nid, point[0], point[1], point[2]))

      self.point_hash = point_hash 
      self.max_x = max_x 
      self.max_y = max_y 
      self.max_z = max_z 
      self.min_x = min_x 
      self.min_y = min_y 
      self.min_z = min_z

      print("[VolumeMesh] ")
      print("[VolumeMesh] ========== Cells ==========")
      num_cells = self.mesh.GetNumberOfCells()
      print("[VolumeMesh] Number of cells: {0:d}".format(num_cells))

      for i in range(num_cells):
          if element_ids:
              elem_id = element_ids.GetValue(i)
          else:
              elem_id = i
          id_list = vtk.vtkIdList()
          self.mesh.GetCellPoints(i, id_list)
          num_pts = id_list.GetNumberOfIds()
          ids = []
          nids = []
          for j in range(num_pts):
              pid = id_list.GetId(j)
              if point_ids:
                  nid = point_ids.GetValue(pid)
              else:
                  nid = pid
              nids.append(nid)
              ids.append(pid)
              #ids.append(nid)
              #ids_1.append(nid)
          print("[VolumeMesh] {0:d}: id: {1:d}  conn:{2:s}".format(i+1, elem_id, str(nids)))
          #print("[VolumeMesh]                   conn:{2:s}".format(i+1, elem_id, str(ids)))

    def read_mesh(self, file_name):
        #print("[Volume.read_mesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()

class SurfaceMesh(object):
    def __init__(self, file_name):
      self.file_name = file_name
      self.mesh = self.read_mesh(file_name)
      num_points = self.mesh.GetNumberOfPoints()
      points = self.mesh.GetPoints()
      point_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      element_ids = self.mesh.GetCellData().GetArray("GlobalElementID")

      print("[SurfaceMesh] ")
      print("[SurfaceMesh] ========== SurfaceMesh ==========")
      print("[SurfaceMesh] file_name: " + file_name)

      pt = 3*[0.0]
      max_x = -1e9
      max_y = -1e9
      max_z = -1e9
      min_x = 1e9
      min_y = 1e9
      min_z = 1e9

      for i in range(num_points):
          point = points.GetPoint(i, pt)
          x = pt[0]
          y = pt[1]
          z = pt[2]
          if x < min_x:
              min_x = x
          elif x > max_x:
              max_x = x
          if y < min_y:
              min_y = y
          elif y > max_y:
              max_y = y
          if z < min_z:
              min_z = z
          elif z > max_z:
              max_z = z
      #_for i in range(num_points)

      dx = (max_x - min_x)
      if dx != 0.0:
        self.dx = dx 
      else: 
        self.dx = 1.0

      dy = (max_y - min_y)
      if dy != 0.0:
        self.dy = dy 
      else: 
        self.dy = 1.0

      dz = (max_z - min_z)
      if dz != 0.0:
        self.dz = dz 
      else: 
        self.dz = 1.0

      self.nodal_coords = {}
      point_hash = defaultdict(list)
      num_dupe_points = 0
      node_ids_set = set()

      for i in range(num_points):
          point = points.GetPoint(i, pt)
          pid = point_ids.GetValue(i)
          x = pt[0]
          y = pt[1]
          z = pt[2]
          #if pid == 2421: 
          #    print("[SurfaceMesh] ### i: {0:d}  pid: {1:d}  point: {2:s}".format(i, pid, str(pt)))
          #if pid in node_ids_set:
          #   print("[SurfaceMesh] ### dupe i: {0:d}  pid: {1:d}  point: {2:s}".format(i, pid, str(pt)))
          #self.nodal_coords[i] = [x, y, z]
          self.nodal_coords[pid] = [x, y, z]
          node_ids_set.add(pid)

          xs = (x - min_x) / self.dx 
          ys = (y - min_y) / self.dy 
          zs = (z - min_z) / self.dz 
          ih = xs * num_points
          jh = ys * num_points
          kh = zs * num_points
          index = int(ih + jh + kh) 
          pts = point_hash[index]
          if len(pts) == 0:
              point_hash[index].append([x, y, z, pid])
          else:
              found_pt = False
              for hpt in pts:
                  ddx = hpt[0] - pt[0]
                  ddy = hpt[1] - pt[1]
                  ddz = hpt[2] - pt[2]
                  d = ddx*ddx + ddy*ddy + ddz*ddz
                  if d == 0.0:
                      found_pt = True
                      num_dupe_points += 1
                      break
              #_for hpt in pts
              if not found_pt:
                  point_hash[index].append([x, y, z, pid])
      #_for i in range(num_points)

      print("[SurfaceMesh] ")
      print("[SurfaceMesh] ========== Nodes ==========")
      print("[SurfaceMesh] Number of nodes: {0:d}".format(num_points))
      for nid, point in self.nodal_coords.items():
      #for nid, point in sorted(self.nodal_coords.items()):
          print("[SurfaceMesh] {0:d}: {1:s} ".format(nid, str(point)))

      self.point_hash = point_hash 
      self.max_x = max_x 
      self.max_y = max_y 
      self.max_z = max_z 
      self.min_x = min_x 
      self.min_y = min_y 
      self.min_z = min_z

      print("[SurfaceMesh] ")
      print("[SurfaceMesh] ========== Cells ==========")
      num_cells = self.mesh.GetNumberOfCells()
      print("[SurfaceMesh] Number of cells: {0:d}".format(num_cells))

      for i in range(num_cells):
          elem_id = element_ids.GetValue(i)
          id_list = vtk.vtkIdList()
          self.mesh.GetCellPoints(i, id_list)
          num_pts = id_list.GetNumberOfIds()
          pids = []
          nids = []
          for j in range(num_pts):
              pid = id_list.GetId(j)
              pids.append(pid)
              nid = point_ids.GetValue(pid)
              nids.append(nid)
              #ids_1.append(nid)
          print("[SurfaceMesh] {0:d}: id: {1:d}  conn: {2:s}".format(i+1, elem_id, str(nids)))
          #print("[SurfaceMesh] {0:d}: id: {1:d}  conn: {2:s}".format(i+1, elem_id, str(pids)))
          #print("[SurfaceMesh] {0:d}: {1:s}".format(i+1, str(ids_1)))

    def read_mesh(self, file_name):
        #print("[SurfaceMesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()

if __name__ == '__main__':

    file_name = sys.argv[1]
    file_base_name, ext = os.path.splitext(file_name)

    if ext == ".vtp":
        surface = SurfaceMesh(file_name)
    elif ext == ".vtu":
        volume = VolumeMesh(file_name)


