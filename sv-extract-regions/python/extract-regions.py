'''
This script is used to extract regions from an sv .vtu file. 

The extracted regions are written to a file.

The nodes shared by the regions are displayed as red points.
'''
from collections import defaultdict 
import os
import sys
import vtk

def add_interface_points(node_coord_map, renderer):
    '''
    Add interface points to renderer.
    '''
    print("")
    print("Add interface points ...")
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    num_pts = 0

    for id in node_coord_map: 
        pts = node_coord_map[id]
        if len(pts) != 1:
            pid = points.InsertNextPoint(pts[0])
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
            #print("Interface point:  {0:s}: ".format(str(pts[0])))
            #print("Point {0:d}: {1:s}".format(id, str(pts[0])))
            num_pts += 1
    #_for id in node_coord_map
    print("Number of interface points: {0:d}".format(num_pts))

    points_pd = vtk.vtkPolyData()
    points_pd.SetPoints(points)
    points_pd.SetVerts(vertices)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(points_pd)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 0.0, 0.0)
    actor.GetProperty().SetPointSize(5)
    renderer.AddActor(actor)

def add_mesh_geom(reader, mesh, renderer):
    '''
    Add mesh to renderer.
    '''
    print("")
    print("Add mesh geometry ...")

    mapper = vtk.vtkPolyDataMapper()
    show_edges = False

    if not show_edges:
        geom_filter = vtk.vtkGeometryFilter()
        geom_filter.SetInputData(mesh)
        geom_filter.Update()
        polydata = geom_filter.GetOutput()
        print("Number of polydats points: %d" % polydata.GetNumberOfPoints())
        print("Number of polydats cells: %d" % polydata.GetNumberOfCells())
        mapper.SetInputData(polydata)

    if show_edges:
        edge_filter = vtk.vtkExtractEdges()
        edge_filter.SetInputData(mesh)
        edge_filter.Update()
        edges = edge_filter.GetOutput()
        print("Number of edges points: %d" % edges.GetNumberOfPoints())
        mapper.SetInputData(edges)

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

def get_region_mesh(mesh, region_id): 
    '''
    Extract a mesh region from a mesh using a region ID.
    '''
    thresholder = vtk.vtkThreshold()
    thresholder.SetInputData(mesh);
    thresholder.SetInputArrayToProcess(0,0,0,1,"ModelRegionID");
    thresholder.ThresholdBetween(region_id, region_id);
    thresholder.Update();
    return thresholder.GetOutput()
#_get_region_mesh(mesh, region_id)

def write_mesh(mesh, region_id): 
    file_name = "mesh-" + str(region_id) + ".vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()
#_write_mesh(mesh, region_id)

## Read mesh.
#
file_name = 'extrude.vtu' 
reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName(file_name)
reader.Update()
mesh = reader.GetOutput()

num_points = mesh.GetNumberOfPoints()
points = mesh.GetPoints()
print("Number of points: {0:d}".format(num_points))

num_cells = mesh.GetNumberOfCells()
print("Number of cells: {0:d}".format(num_cells))
cells = mesh.GetCells()

## Get the cells for each region.
#
print("")
print("Count the cells for each region ...")
model_ids = mesh.GetCellData().GetArray('ModelRegionID')
regions = defaultdict(list)
for cell_id in range(num_cells):
    value = model_ids.GetValue(cell_id)
    regions[value].append(cell_id)
print("Number of regions: {0:d}".format(len(regions)))
for region_id, cells in regions.items(): 
    print("Region {0:d}: number of cells: {1:d}".format(region_id, len(cells)))

## Get mesh for region 1.
#
print("")
print("========== Region 1 mesh ==========")
mesh_1 = get_region_mesh(mesh, 1) 
write_mesh(mesh_1, 1) 
#
num_points_1 = mesh_1.GetNumberOfPoints()
points_1 = mesh_1.GetPoints()
print("Number of points: {0:d}".format(num_points_1))
#
num_cells_1 = mesh_1.GetNumberOfCells()
print("Number of cells: {0:d}".format(num_cells_1))
cells_1 = mesh_1.GetCells()
#
node_id_map = defaultdict(int)
node_coord_map = defaultdict(list)
node_ids_1 = mesh_1.GetPointData().GetArray('GlobalNodeID')
pt = 3*[0.0]
for i in range(num_points_1):
    nid = node_ids_1.GetValue(i)
    points_1.GetPoint(i, pt)
    node_id_map[nid] += 1
    node_coord_map[nid].append([pt[0], pt[1], pt[2]])
    #print("Point {0:d}: {1:d}  {2:s}".format(i, nid, str(pt)))

## Get mesh for region 2.
#
print("")
print("========== Region 2 mesh ==========")
mesh_2 = get_region_mesh(mesh, 2) 
write_mesh(mesh_2, 2) 
#
num_points_2 = mesh_2.GetNumberOfPoints()
points_2 = mesh_2.GetPoints()
print("Number of points: {0:d}".format(num_points_2))
#
num_cells_2 = mesh_2.GetNumberOfCells()
print("Number of cells: {0:d}".format(num_cells_2))
cells_2 = mesh_2.GetCells()
#
node_ids_2 = mesh_2.GetPointData().GetArray('GlobalNodeID')
for i in range(num_points_2):
    nid = node_ids_2.GetValue(i)
    points_2.GetPoint(i, pt)
    node_id_map[nid] += 1
    node_coord_map[nid].append([pt[0], pt[1], pt[2]])
    #print("Point {0:d}: {1:d}  {2:s}".format(i, id, str(pts[0])))
    #print("Point {0:d}: {1:d}  {2:s}".format(i, nid, str(pt)))
    #pts = node_coord_map[id]
    #print("      {0:s}".format(str(pts[0])))

num_dupe = 0
for nid, count in node_id_map.items(): 
    if count != 1:
        pts = node_coord_map[nid]
        #print("Node id {0:d}: number: {1:d}".format(nid, count))
        #print("    {0:s}: ".format(str(pts[0])))
        #print("    {0:s}: ".format(str(pts[1])))
        num_dupe += 1
print("Number of duplicate nodes: {0:d} ".format(num_dupe))

## Show mesh.
#
# Create renderer and graphics window.
renderer = vtk.vtkRenderer()
renderer_win = vtk.vtkRenderWindow()
renderer_win.AddRenderer(renderer)
renderer.SetBackground(0.6, 0.6, 0.6)
renderer_win.SetSize(1000, 1000)


add_mesh_geom(reader, mesh, renderer)

add_interface_points(node_coord_map, renderer)

# Create a trackball interacter to transoform the geometry using the mouse.
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(renderer_win)
interactor.Start()



