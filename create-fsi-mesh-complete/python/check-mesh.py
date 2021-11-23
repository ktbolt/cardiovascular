#!/usr/bin/env python
'''
This script is used to check that the volume and surface face meshes are consistent wrt Fortran IDs.
'''
from collections import defaultdict
from math import sqrt
import os
import sys
import vtk

class Extent(object):
    '''This class stores a coordinate extent.
    '''
    def __init__(self, max_x, min_x, max_y, min_y, max_z, min_z):
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z

        dx = (max_x - min_x)
        if dx == 0.0:
            dx = 1.0

        dy = (max_y - min_y)
        if dy == 0.0:
            dy = 1.0

        dz = (max_z - min_z)
        if dz == 0.0:
            dz = 1.0

        self.dx = dx
        self.dy = dy
        self.dz = dz

class SurfaceMesh(object):
    '''This class is used to store data for a surface face mesh.
    '''
    def __init__(self, file_name):
      self.file_name = file_name
      self.mesh = self.read_mesh(file_name)

      self.num_points = self.mesh.GetNumberOfPoints()
      self.points = self.mesh.GetPoints()
      self.node_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      self.num_cells = self.mesh.GetNumberOfCells()

      print("[SurfaceMesh] file_name: {0:s}".format(file_name))
      print("[SurfaceMesh] num_points: {0:d}".format(self.num_points))
      print("[SurfaceMesh] num_cells: {0:d}".format(self.num_cells))

      # Create node ID to node coord map.
      use_ids = True
      nodal_coords, extent = create_node_coord_map(self.num_points, self.node_ids, self.points, use_ids)
      self.nodal_coords = nodal_coords
      self.extent = extent
      print("[SurfaceMesh] ========== Nodes ==========")
      print("[SurfaceMesh] Number of nodes: {0:d}".format(self.num_points))
      i = 0
      for nid, point in nodal_coords.items():
          print("[SurfaceMesh] {0:d}:  id: {1:d}  coord: {2:s}".format(i, nid, str(point)))
          i += 1

      # Create a map hashing node coords to IDs..
      #
      self.point_hash = create_node_coord_hash(self.nodal_coords, self.extent)

      # Create list of element connectivity.
      #
      print("[SurfaceMesh] ")
      print("[SurfaceMesh] ========== Elements ==========")
      print("[SurfaceMesh] Number of elements: {0:d}".format(self.num_cells))
      self.elem_conn = defaultdict(set)
      self.elem_conn = defaultdict(set)
      elem_ids = self.mesh.GetCellData().GetArray('GlobalElementID')
      for i in range(self.num_cells):
          elem_id = elem_ids.GetValue(i)
          id_list = vtk.vtkIdList()
          self.mesh.GetCellPoints(i, id_list)
          num_pts = id_list.GetNumberOfIds()
          conn = set()

          for j in range(num_pts):
              pid = id_list.GetId(j)
              nid = self.node_ids.GetValue(pid)
              conn.add(nid)

          self.elem_conn[elem_id] = conn
          print("[VolumeMesh] {0:d}:  id: {1:d}  conn: {2:s}".format(i, elem_id, str(conn)))

    def read_mesh(self, file_name):
        #print("[SurfaceMesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()

class VolumeMesh(object):
    '''This class is used to store data for a volume mesh.
    '''
    def __init__(self, file_name):
      self.mesh = self.read_mesh(file_name)

      geom_filter = vtk.vtkGeometryFilter()
      geom_filter.SetInputData(self.mesh)
      geom_filter.Update()
      self.polydata = geom_filter.GetOutput()

      self.node_ids = self.mesh.GetPointData().GetArray("GlobalNodeID")
      self.num_points = self.mesh.GetNumberOfPoints()
      self.points = self.mesh.GetPoints()
      self.num_cells = self.mesh.GetNumberOfCells()

      # Create node ID to node coord map.
      nodal_coords, extent = create_node_coord_map(self.num_points, self.node_ids, self.points)
      self.nodal_coords = nodal_coords
      self.extent = extent
      print("[VolumeMesh] ========== Nodes ==========")
      print("[VolumeMesh] Number of nodes: {0:d}".format(self.num_points))
      i = 0
      for nid, point in nodal_coords.items():
          print("[VolumeMesh] {0:d}:  id: {1:d}  coord: {2:s}".format(i, nid, str(point)))
          i += 1

      # Create a map hashing node coords to IDs..
      # 
      self.point_hash = create_node_coord_hash(self.nodal_coords, self.extent)

      # Create list of element connectivity.
      #
      # Don't use node IDs for the connectivity.
      #
      print("[VolumeMesh] ")
      print("[VolumeMesh] ========== Elements ==========")
      print("[VolumeMesh] Number of elements: {0:d}".format(self.num_cells))
      self.elem_conn = defaultdict(set)
      elem_ids = self.mesh.GetCellData().GetArray('GlobalElementID')
      for i in range(self.num_cells):
          elem_id = elem_ids.GetValue(i)
          id_list = vtk.vtkIdList()
          self.mesh.GetCellPoints(i, id_list)
          num_pts = id_list.GetNumberOfIds()
          conn = set()

          for j in range(num_pts):
              pid = id_list.GetId(j)
              nid = self.node_ids.GetValue(pid)
              conn.add(pid+1)

          #print("[VolumeMesh] {0:d}  id: {1:d}  conn: {2:s}".format(i, elem_id, str(conn)))
          print("[VolumeMesh] {0:d}:  id: {1:d}  conn: {2:s}".format(i, elem_id, str(conn)))
          self.elem_conn[i+1] = conn

    def check_surface_mesh(self, surface):
        '''Check that the surface node IDs and element connectivity match the volume mesh.
        '''
        print("[VolumeMesh] ========== check_surface_mesh ==========")
        tol = 1e-4
        num_diff = 0
        for nid, point in self.nodal_coords.items():
            if nid not in surface.nodal_coords:
                continue
            surf_point = surface.nodal_coords[nid]
            dist = sqrt(sum([(point[j]-surf_point[j])*(point[j]-surf_point[j]) for j in range(0,3)]))
            if abs(dist) > tol:
                num_diff += 1
                print("[VolumeMesh.check_surface_mesh] ")
                print("[VolumeMesh.check_surface_mesh] No match for surface point {0:d} {1:s}. Dist {2:f}.".format(nid, str(surf_point), dist))
                node_id, index = find_node_id(self.point_hash, self.num_points, self.extent, surf_point)
                print("[VolumeMesh.check_surface_mesh] Hash node ID {0:d}".format(node_id))

        if num_diff == 0:
            print("[VolumeMesh.check_surface_mesh] All surface points match volume points.")
        else:
            print("[VolumeMesh.check_surface_mesh] {0:d} surface points did not match volume points.".format(num_diff))

        num_diff = 0
        for elem_id, conn in self.elem_conn.items():
            if elem_id not in surface.elem_conn:
                continue
            surf_conn = surface.elem_conn[elem_id]
            if len(conn.intersection(surf_conn)) == 0:
                print("[VolumeMesh] elem {0:d} doesn't match:  conn: {1:s}  {2:s}".format(elem_id, str(conn), str(surf_conn)))
                num_diff += 1

        if num_diff == 0:
            print("[VolumeMesh.check_surface_mesh] All surface elements match volume elements.")
        else:
            print("[VolumeMesh.check_surface_mesh] {0:d} surface elements did not match volume points.".format(num_diff))
    
    def read_mesh(self, file_name):
        print("[read_volume_mesh] file_name: " + file_name)
        file_base_name, ext = os.path.splitext(file_name)
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(file_name)
        reader.Update()
        return reader.GetOutput()

def create_node_coord_map(num_points, node_ids, points, use_ids=False):
    '''Create nodal IDs to coordinates map.
    '''
    max_x = -1e9
    max_y = -1e9
    max_z = -1e9
    min_x = 1e9
    min_y = 1e9
    min_z = 1e9
    pt = 3*[0.0]
    nodal_coords = {}

    # Store coords using index into points array.
    #
    for i in range(num_points):
        if use_ids:
            nid = node_ids.GetValue(i)
        else:
            nid = i + 1 
        points.GetPoint(i, pt)
        x = pt[0]
        y = pt[1]
        z = pt[2]
        if nid in nodal_coords:
            print("Duplicate node ID {0:d}.".format(nid))
        nodal_coords[nid] = [x, y, z, i]

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

    return nodal_coords, Extent(max_x, min_x, max_y, min_y, max_z, min_z)

def create_node_coord_hash(nodal_coords, extent):
    '''Create nodal coordinates hash table.
    '''
    point_hash = defaultdict(list)
    num_points = len(nodal_coords)
    #print("[create_node_coord_hash] num_points: {0:d}".format(num_points)

    n = 0
    for nid, point in nodal_coords.items():
        x = point[0]
        y = point[1]
        z = point[2]

        xs = (x - extent.min_x) / extent.dx
        ys = (y - extent.min_y) / extent.dy
        zs = (z - extent.min_z) / extent.dz
        ih = xs * num_points
        jh = ys * num_points
        kh = zs * num_points
        index = int(ih + jh + kh) 
        pts = point_hash[index]

        if len(pts) == 0:
            point_hash[index].append([x, y, z, nid, n])
        else:
            found_pt = False
            for hpt in pts:
                ddx = hpt[0] - x
                ddy = hpt[1] - y 
                ddz = hpt[2] - z
                d = ddx*ddx + ddy*ddy + ddz*ddz
                if d == 0.0:
                    found_pt = True
                    break
            if not found_pt:
                point_hash[index].append([x, y, z, nid, n])
        n += 1

    return point_hash

def find_node_id(point_hash, num_points, extent, point):
    node_id = -1
    x = point[0]
    y = point[1]
    z = point[2]
    xs = (x - extent.min_x) / extent.dx
    ys = (y - extent.min_y) / extent.dy
    zs = (z - extent.min_z) / extent.dz
    ih = xs * num_points
    jh = ys * num_points
    kh = zs * num_points
    index = int(ih + jh + kh)

    pts = point_hash[index]
    found_pt = False
    for hpt in pts:
      dx = hpt[0] - x
      dy = hpt[1] - y
      dz = hpt[2] - z
      d = dx*dx + dy*dy + dz*dz
      if d == 0.0:
          node_id = hpt[3]
          index = hpt[4]
          break

    return node_id, index

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

if __name__ == '__main__':

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    # Read volume mesh.
    file_name = sys.argv[1]
    volume_mesh = VolumeMesh(file_name)
    actor = add_geom(volume_mesh.polydata, renderer)
    actor.GetProperty().BackfaceCullingOn()
    actor.GetProperty().SetEdgeVisibility(1)
    actor.GetProperty().SetOpacity(0.8)
    actor.GetProperty().SetColor(0.0, 0.8, 0.8)
    actor.GetProperty().SetRepresentationToWireframe()

    # Read surface mesh.
    file_name = sys.argv[2]
    surface_mesh = SurfaceMesh(file_name)
    actor = add_geom(surface_mesh.mesh, renderer)
    actor.GetProperty().SetColor(0.8, 0.0, 0.0)

    volume_mesh.check_surface_mesh(surface_mesh)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    #interactor.Start()


