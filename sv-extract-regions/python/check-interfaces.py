'''
This script is used to check the fluid-solid interace surfaces.  

'''
from collections import defaultdict 
import os
import sys
import vtk
from math import sqrt

def add_mesh_geom(reader, mesh, renderer):
    ''' Add mesh to renderer.
    '''
    print("")
    print("Add mesh geometry ...")

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    mapper.ScalarVisibilityOff();

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToPoints()
    #actor.GetProperty().SetRepresentationToWireframe()
    #actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().BackfaceCullingOn()   
    #actor.GetProperty().SetDiffuseColor(0, 0.5, 0) 
    actor.GetProperty().SetEdgeVisibility(1) 
    actor.GetProperty().SetOpacity(0.5) 
    #actor.GetProperty().SetEdgeColor(1, 0, 0) 
    actor.GetProperty().SetColor(0.0, 0.8, 0.8)
    #actor.GetProperty().SetPointSize(5)
    renderer.AddActor(actor)


def check_nodes(mesh1, mesh2):
    num_points1 = mesh1.GetNumberOfPoints()
    points1 = mesh1.GetPoints()
    num_cells1 = mesh1.GetNumberOfCells()
    num_points2 = mesh2.GetNumberOfPoints()
    points2 = mesh2.GetPoints()
    num_cells2 = mesh2.GetNumberOfCells()

    ## Check nodal coordinates.
    #
    pt = 3*[0.0]
    max_x = -1e9
    max_y = -1e9
    max_z = -1e9
    min_x = 1e9
    min_y = 1e9
    min_z = 1e9
    for i in range(num_points1):
        points1.GetPoint(i, pt)
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
    #_for i in range(num_points):

    point_hash = defaultdict(list)
    num_dupe_points = 0
    for i in range(num_points1):
        points1.GetPoint(i, pt)
        x = pt[0]
        y = pt[1]
        z = pt[2]
        xs = (x-min_x) / (max_x-min_x)
        ys = (y-min_y) / (max_y-min_y)
        zs = (z-min_z) / (max_z-min_z)
        ih = xs*num_points1
        jh = ys*num_points1
        kh = zs*num_points1
        index = int(ih + jh + kh)
        pts = point_hash[index]
        if len(pts) == 0:
            point_hash[index].append([pt[0], pt[1], pt[2]])
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
                point_hash[index].append([pt[0], pt[1], pt[2]])
    #_for i in range(num_points)

    for i in range(num_points2):
        points2.GetPoint(i, pt)
        x = pt[0]
        y = pt[1]
        z = pt[2]
        xs = (x-min_x) / (max_x-min_x)
        ys = (y-min_y) / (max_y-min_y)
        zs = (z-min_z) / (max_z-min_z)
        ih = xs*num_points1
        jh = ys*num_points1
        kh = zs*num_points1
        index = int(ih + jh + kh)
        pts = point_hash[index]
        if len(pts) == 0:
            point_hash[index].append([pt[0], pt[1], pt[2]])
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
                point_hash[index].append([pt[0], pt[1], pt[2]])
    #_for i in range(num_points)
    if (num_dupe_points != num_points2):
        print("ERROR: Coordinates don't match.")
    else:
        print("Coordinates match.")

    ## Check nodal IDs.
    #
    node_id_map = defaultdict(int)
    node_coord_map = defaultdict(list)
    node_ids1 = mesh1.GetPointData().GetArray('GlobalNodeID')
    for i in range(num_points1):
        nid = node_ids1.GetValue(i)
        points1.GetPoint(i, pt)
        node_id_map[nid] += 1
        node_coord_map[nid].append([pt[0], pt[1], pt[2]])
        #print("Point {0:d}: {1:d}  {2:s}".format(i, nid, str(pt)))

    node_ids2 = mesh2.GetPointData().GetArray('GlobalNodeID')
    for i in range(num_points2):
        nid = node_ids2.GetValue(i)
        points2.GetPoint(i, pt)
        node_id_map[nid] += 1
        if len(node_coord_map[nid]) != 0:
            cpt = node_coord_map[nid][0]
            d = sqrt(sum([(cpt[j]-pt[j])*(cpt[j]-pt[j]) for j in range(3)]))
        node_coord_map[nid].append([pt[0], pt[1], pt[2]])
        #print("Point {0:d}: {1:d}  {2:s}".format(i, id, str(pts[0])))
        #print("Point {0:d}: {1:d}  {2:s}".format(i, nid, str(pt)))
        #pts = node_coord_map[id]
        #print("      {0:s}".format(str(pts[0])))

    if len(node_id_map) != num_points1:
        print("ERROR: Nodel IDs don't match.")
    else:
        print("Nodel IDs match.")

    num_dupe = 0
    for nid, count in node_id_map.items():
        if count != 1:
            pts = node_coord_map[nid]
            #print("Node id {0:d}: number: {1:d}".format(nid, count))
            #print("    {0:s}: ".format(str(pts[0])))
            #print("    {0:s}: ".format(str(pts[1])))
            num_dupe += 1
    #_for nid, count in node_id_map.items()
    print("Mesh 1 and mesh 2 share {0:d} nodes.".format(num_dupe))


if __name__ == '__main__':

    ## Read meshes.
    #
    print("")
    print("========== Mesh 1 ==========")
    file_name1 = sys.argv[1]
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name1)
    reader.Update()
    mesh1 = reader.GetOutput()
    #
    num_points1 = mesh1.GetNumberOfPoints()
    points1 = mesh1.GetPoints()
    print("Number of points: {0:d}".format(num_points1))
    num_cells1 = mesh1.GetNumberOfCells()
    print("Number of cells: {0:d}".format(num_cells1))
    #cells = mesh.GetCells()

    print("========== Mesh 2 ==========")
    file_name2 = sys.argv[2]
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name2)
    reader.Update()
    mesh2 = reader.GetOutput()
    #
    num_points2 = mesh2.GetNumberOfPoints()
    points2 = mesh2.GetPoints()
    print("Number of points: {0:d}".format(num_points2))
    num_cells2 = mesh2.GetNumberOfCells()
    print("Number of cells: {0:d}".format(num_cells2))
    #cells = mesh.GetCells()

    # Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    add_mesh_geom(reader, mesh1, renderer)
    add_mesh_geom(reader, mesh2, renderer)

    ## Check for duplicate nodes.
    #
    check_nodes(mesh1, mesh2)

    #add_interface_points(node_coord_map, renderer)

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()



