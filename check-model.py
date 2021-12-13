#!/usr/bin/env python3
'''
This script is used to check a model. 
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

def create_node_coord_hash(model):
    '''Create nodal coordinates hash table.
    '''
    num_points = model.GetNumberOfPoints()
    points = model.GetPoints()

    max_x = -1e9
    max_y = -1e9
    max_z = -1e9
    min_x = 1e9
    min_y = 1e9
    min_z = 1e9
    pt = 3*[0.0]

    for i in range(num_points):
        points.GetPoint(i, pt)
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

    extent = Extent(max_x, min_x, max_y, min_y, max_z, min_z)
    num_dupe = 0

    point_hash = defaultdict(list)

    for i in range(num_points):
        points.GetPoint(i, pt)
        x = pt[0]
        y = pt[1]
        z = pt[2]

        xs = (x - extent.min_x) / extent.dx
        ys = (y - extent.min_y) / extent.dy
        zs = (z - extent.min_z) / extent.dz
        ih = xs * num_points
        jh = ys * num_points
        kh = zs * num_points
        index = int(ih + jh + kh) 
        pts = point_hash[index]

        if len(pts) == 0:
            point_hash[index].append([x, y, z])
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
                point_hash[index].append([x, y, z])
            else:
              num_dupe += 1

    print("Number of duplicate vertices: {0:d}".format(num_dupe))

def find_holes(model):
    print("---------- find holes ---------- ")
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(model)
    feature_edges.BoundaryEdgesOn()
    feature_edges.FeatureEdgesOff()
    feature_edges.ManifoldEdgesOff()
    feature_edges.ColoringOn()
    feature_edges.NonManifoldEdgesOff()
    feature_edges.Update()

    boundary_edges = feature_edges.GetOutput()
    if boundary_edges.GetNumberOfPoints() == 0: 
        raise RuntimeError('No boundary edges.')

    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputData(boundary_edges)
    clean_filter.Update();
    cleaned_edges = clean_filter.GetOutput()

    conn_filter = vtk.vtkPolyDataConnectivityFilter()
    conn_filter.SetInputData(cleaned_edges)
    conn_filter.SetExtractionModeToSpecifiedRegions()
    boundary_edge_components = list()
    edge_id = 0

    while True:
        conn_filter.AddSpecifiedRegion(edge_id)
        conn_filter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(conn_filter.GetOutput())
        if component.GetNumberOfCells() <= 0:
            break
        #print("{0:d}: Number of boundary lines: {1:d}".format(edge_id, component.GetNumberOfCells()))
        boundary_edge_components.append(component)
        conn_filter.DeleteSpecifiedRegion(edge_id)
        edge_id += 1

    print("Number of holes: {0:d}".format(edge_id))

def extract_faces(model, angle):
    '''Extract the surface faces.
    '''
    print("---------- extract faces ---------- ")

    ## Compute edges separating cells by the angle set in 'self.params.angle'.
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(model)
    feature_edges.BoundaryEdgesOff()
    feature_edges.ManifoldEdgesOff()
    feature_edges.NonManifoldEdgesOff()
    feature_edges.FeatureEdgesOn()
    feature_edges.SetFeatureAngle(angle)
    feature_edges.Update()

    boundary_edges = feature_edges.GetOutput()
    if boundary_edges.GetNumberOfPoints() == 0: 
        raise RuntimeError('No boundary edges.')

    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputData(boundary_edges)
    clean_filter.Update();
    cleaned_edges = clean_filter.GetOutput()

    conn_filter = vtk.vtkPolyDataConnectivityFilter()
    conn_filter.SetInputData(cleaned_edges)
    conn_filter.SetExtractionModeToSpecifiedRegions()
    boundary_edge_components = list()
    edge_id = 0

    while True:
        conn_filter.AddSpecifiedRegion(edge_id)
        conn_filter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(conn_filter.GetOutput())
        if component.GetNumberOfCells() <= 0:
            break
        #print("{0:d}: Number of boundary lines: {1:d}".format(edge_id, component.GetNumberOfCells()))
        boundary_edge_components.append(component)
        conn_filter.DeleteSpecifiedRegion(edge_id)
        edge_id += 1

    print("[extract_faces] Number of edges: {0:d}".format(edge_id))

def check_area(model):
    print("---------- check area ---------- ")
    max_area = -1e9
    min_area = 1e9
    avg_area = 0.0
    tol = 1e-4
    points = model.GetPoints()

    for cell_id in range(model.GetNumberOfCells()):
        cell = model.GetCell(cell_id)
        dim = cell.GetCellDimension()
        num_cell_nodes = cell.GetNumberOfPoints()
        #print("Cell: {0:d}".format(cell_id))
        #print("    dim: {0:d}".format(dim))
        #print("    cell_num_nodes: {0:d}".format(num_cell_nodes))
        tri = vtk.vtkTriangle()
        tri_points = []
        for j in range(0, num_cell_nodes):
            node_id = cell.GetPointId(j)
            pt = points.GetPoint(node_id)
            tri_points.append(pt)
        area = vtk.vtkTriangle.TriangleArea(tri_points[0], tri_points[1], tri_points[2])
        #area = tri.ComputeArea()            
        if area < min_area:
            min_area = area
        if area > max_area:
            max_area = area
        if area < tol:
            print("[check_area] area: {0:d} {1:f}".format(cell_id, area))
        avg_area += area

    avg_area /= model.GetNumberOfCells()
    print("[check_area] Max area: {0:f}".format(max_area))
    print("[check_area] Min area: {0:f}".format(min_area))
    print("[check_area] Avg area: {0:f}".format(avg_area))


if __name__ == '__main__':

    # Read model.
    file_name = sys.argv[1]
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    model = reader.GetOutput()

    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetPointMerging(True)
    clean_filter.SetInputData(model)
    clean_filter.Update();
    model = clean_filter.GetOutput()
    model.BuildLinks()

    create_node_coord_hash(model)


    #find_holes(model)

    fill_hole_filter = vtk.vtkFillHolesFilter()
    fill_hole_filter.SetInputData(model)
    fill_hole_filter.SetHoleSize(float(1e10))
    fill_hole_filter.Update()
    model = fill_hole_filter.GetOutput()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(model)
    normals.ConsistencyOn();
    normals.SplittingOn();
    normals.Update();
    model = normals.GetOutput()

    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetPointMerging(True)
    clean_filter.SetInputData(model)
    clean_filter.Update();
    model = clean_filter.GetOutput()
    model.BuildLinks()

    check_area(model)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName("fixed.vtp")
    writer.SetInputData(model)
    writer.Update()
    writer.Write()


