#!/usr/bin/env python

from collections import defaultdict
import os
import sys
import vtk

def add_geom(geom, renderer):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    mapper.ScalarVisibilityOff();
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    renderer.AddActor(actor)
    return actor

def add_sphere(center, renderer):
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(center[0], center[1], center[2])
    sphere.SetRadius(0.1)
    sphere.Update()
    poly_data = sphere.GetOutput()
    return add_geom(poly_data, renderer)

class SurfaceMesh(object):
    def __init__(self, file_name):
      self.file_name = file_name
      self.mesh = self.read_mesh(file_name)
      num_points = self.mesh.GetNumberOfPoints()
      points = self.mesh.GetPoints()
      point_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      num_cells = self.mesh.GetNumberOfCells()

      self.num_points = num_points
      self.points = points
      self.point_ids = point_ids

      print("[SurfaceMesh] file_name: {0:s}".format(file_name))
      print("[SurfaceMesh] num_points: {0:d}".format(num_points))
      print("[SurfaceMesh] num_cells: {0:d}".format(num_cells))

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
          pid = point_ids.GetValue(i)
          x = pt[0]
          y = pt[1]
          z = pt[2]
          #if i < 4: 
          #    print("[SurfaceMesh] pid: {0:d}  point: {1:s}".format(pid, str(pt)))
          print("[SurfaceMesh] pid: {0:d}  point: {1:s}".format(pid, str(pt)))
          self.nodal_coords[pid] = [x, y, z]

          xs = (x - min_x) / self.dx 
          ys = (y - min_y) / self.dy 
          zs = (z - min_z) / self.dz 
          ih = xs * num_points
          jh = ys * num_points
          kh = zs * num_points
          index = int(ih + jh + kh) % self.num_points
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
      print("[SurfaceMesh] num_hash_points: {0:d}".format(len(point_hash)))
      print("[SurfaceMesh] num_dupe_points: {0:d}".format(num_dupe_points))

      self.point_hash = point_hash 
      self.max_x = max_x 
      self.max_y = max_y 
      self.max_z = max_z 
      self.min_x = min_x 
      self.min_y = min_y 
      self.min_z = min_z

    def check_points(self, num_points, points, point_ids, renderer):
        print("[SurfaceMesh:check_points] ")
        print("[SurfaceMesh:check_points] num_points: {0:d}".format(num_points))
        pt = 3*[0.0]
        num_matched_points = 0
        for i in range(num_points):
            pid = point_ids.GetValue(i)
            points.GetPoint(i, pt)
            x = pt[0]
            y = pt[1]
            z = pt[2]
            xs = (x - self.min_x) / self.dx 
            ys = (y - self.min_y) / self.dy
            zs = (z - self.min_z) / self.dz
            ih = xs * self.num_points
            jh = ys * self.num_points
            kh = zs * self.num_points
            index = int(ih + jh + kh) % self.num_points
            pts = self.point_hash[index]
            if len(pts) == 0:
                #actor = add_sphere(pt, renderer)
                continue
            else:
                found_pt = False
                for hpt in pts:
                    dx = hpt[0] - pt[0]
                    dy = hpt[1] - pt[1]
                    dz = hpt[2] - pt[2]
                    d = dx*dx + dy*dy + dz*dz
                    if d == 0.0:
                        found_pt = True
                        found_id = hpt[3]
                        num_matched_points += 1
                        break
                #_for hpt in pts
                '''
                if found_pt:
                    if (pid != found_id):
                      print("[SurfaceMesh:check_points] IDs don't match: {0:d} != {1:d}".format(pid, found_id))
                      print("[SurfaceMesh:check_points]   point: {0:s} ".format(str(pt)))
                      actor = add_sphere(pt, renderer)
                '''
        #_for i in range(num_points):

        print("[SurfaceMesh:check_points] num_matched_points: {0:d} ".format(num_matched_points))


    def read_mesh(self, file_name):
        #print("[SurfaceMesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()

class VolumeMesh(object):
    def __init__(self, file_name):
      self.mesh = self.read_mesh(file_name)

      geom_filter = vtk.vtkGeometryFilter()
      geom_filter.SetInputData(self.mesh)
      geom_filter.Update()
      self.polydata = geom_filter.GetOutput()

      num_points = self.mesh.GetNumberOfPoints()
      points = self.mesh.GetPoints()
      point_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      self.num_points = num_points 
      self.points = points 
      self.point_ids = point_ids 
      print("[VolumeMesh] num_points: {0:d}".format(num_points))

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

      self.nodal_coords = {}
      point_hash = defaultdict(list)
      num_dupe_points = 0

      for i in range(num_points):
          point = points.GetPoint(i, pt)
          pid = point_ids.GetValue(i)
          x = pt[0]
          y = pt[1]
          z = pt[2]
          #print("{0:d} {1:s}".format(pid, str(pt)))
          self.nodal_coords[pid] = [x, y, z]

          xs = (x - min_x) / (max_x - min_x)
          ys = (y - min_y) / (max_y - min_y)
          zs = (z - min_z) / (max_z - min_z)
          ih = xs * num_points
          jh = ys * num_points
          kh = zs * num_points
          index = int(ih + jh + kh) % self.num_points
          pts = point_hash[index]
          if len(pts) == 0:
              point_hash[index].append([x, y, z, pid])
          else:
              found_pt = False
              for hpt in pts:
                  dx = hpt[0] - pt[0]
                  dy = hpt[1] - pt[1]
                  dz = hpt[2] - pt[2]
                  d = dx*dx + dy*dy + dz*dz
                  if d == 0.0:
                      found_pt = True
                      num_dupe_points += 1
                      break
              #_for hpt in pts
              if not found_pt:
                  point_hash[index].append([x, y, z, pid])
      #_for i in range(num_points)
      print("[VolumeMesh] num_hash_points: {0:d}".format(len(point_hash)))
      print("[VolumeMesh] num_dupe_points: {0:d}".format(num_dupe_points))

      self.point_hash = point_hash 
      self.max_x = max_x 
      self.max_y = max_y 
      self.max_z = max_z 
      self.min_x = min_x 
      self.min_y = min_y 
      self.min_z = min_z

    def check_points(self, num_points, points, point_ids, renderer):
        print("[check_points] ")
        print("[check_points] num_points: {0:d}".format(num_points))
        pt = 3*[0.0]
        num_matched_points = 0

        for i in range(num_points):
            pid = point_ids.GetValue(i)
            points.GetPoint(i, pt)
            x = pt[0]
            y = pt[1]
            z = pt[2]
            xs = (x - self.min_x) / (self.max_x - self.min_x)
            ys = (y - self.min_y) / (self.max_y - self.min_y)
            zs = (z - self.min_z) / (self.max_z - self.min_z)
            ih = xs * self.num_points
            jh = ys * self.num_points
            kh = zs * self.num_points
            index = int(ih + jh + kh) % self.num_points
            pts = self.point_hash[index]
            if len(pts) == 0:
                actor = add_sphere(pt, renderer)
                continue
            else:
                found_pt = False
                for hpt in pts:
                    dx = hpt[0] - pt[0]
                    dy = hpt[1] - pt[1]
                    dz = hpt[2] - pt[2]
                    d = dx*dx + dy*dy + dz*dz
                    if d == 0.0:
                        found_pt = True
                        found_id = hpt[3]
                        num_matched_points += 1
                        break
                #_for hpt in pts
                if found_pt:
                    if (pid != found_id): 
                      print("[check_points] IDs don't match: {0:d} != {1:d}".format(pid, found_id))
        #_for i in range(num_points):
  
        print("[check_points] num_matched_points: {0:d} ".format(num_matched_points))
    
    def read_mesh(self, file_name):
        print("[read_volume_mesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()


class MeshDomain(object):
    def __init__(self, domain_dir):
        self.domain_dir = domain_dir + "/"
        self.mesh_complete_mesh_vtu = None
        self.mesh_complete_exterior_vtp  = None
        self.walls_combined_vtp = None
        self.surface_meshes = None

        self.read_meshes()

    def read_meshes(self):
        file_name = self.domain_dir + "mesh-complete.mesh.vtu"
        self.mesh_complete_mesh_vtu = VolumeMesh(file_name)

        file_name = self.domain_dir + "mesh-complete.exterior.vtp"
        self.mesh_complete_exterior_vtp = SurfaceMesh(file_name)

        file_name = self.domain_dir + "walls_combined.vtp"
        if os.path.exists(file_name):
            self.walls_combined_vtp = SurfaceMesh(file_name)

        surfaces_dir = self.domain_dir + "/mesh-surfaces/"
        files = os.listdir(surfaces_dir)
        self.surface_meshes = []
        for surf_file in files:
          file_name = surfaces_dir + surf_file 
          self.surface_meshes.append((surf_file, SurfaceMesh(file_name)))


if __name__ == '__main__':

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    file_name = sys.argv[1]
    face_1 = SurfaceMesh(file_name)
    actor = add_geom(face_1.mesh, renderer)
    actor.GetProperty().BackfaceCullingOn()
    actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetOpacity(0.5)
    actor.GetProperty().SetColor(0.0, 0.8, 0.8)

    print(" ")
    file_name = sys.argv[2]
    face_2 = SurfaceMesh(file_name)
    actor = add_geom(face_2.mesh, renderer)
    actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetColor(0.8, 0.0, 0.0)
    actor.GetProperty().SetLineWidth(3.0)

    print(" ")
    face_1.check_points(face_2.num_points, face_2.points, face_2.point_ids, renderer)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    #interactor.Start()


