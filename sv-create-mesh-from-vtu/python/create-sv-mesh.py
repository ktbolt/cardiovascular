#!/usr/bin/env python

'''This script is used to create the SimVascular project Models and Meshes files that allows
   using a mesh in VTK VTU format created outside of SimVascular for a simulation.

   A SimVascular Simulations tool needs both model and a mesh files to execute. 

   Usage:

      python create-sv-mesh.py FILE_NAME.vtu

   The following files are created for an input VTK VTU named FILE_NAME.vtu 

     Models files:
       FILE_NAME-model.vtp - A surface with integer data arrays identifying the boundary faces
       FILE_NAME-model.mdl - An XML file defining face integer IDs with names and type (wall or cap)

     Meshes files:
       FILE_NAME-mesh.vtp - A surface mesh with interger data arrays identifying the boundary faces
       FILE_NAME-mesh.vtu - A volume mesh with node and element IDs 
       FILE_NAME-mesh.mdl - An XML file defining meshing parameters 

   Create a SimVascular project and then copy these files into the project's Models and Meshes directories. 

   All faces have their tttype set to 'wall'.

   Note that the mesh scale needs to match the units used in a simulation. A mesh defined too small may not display
   correctly in SimVascular. A scale factor can be set to scale the mesh; see the call to the 'read_mesh' function.
'''

from collections import defaultdict
from collections import deque
from math import cos
from math import pi as MATH_PI
import os
import sys
import vtk
import xml.etree.ElementTree as etree

def extract_surface_boundary_faces(surface, angle, file_base_name):
    '''Extract the surface boundary faces and set the ModelFaceID cell data array.
    '''
    ## Compute edges separating cells by the given angle in degrees.
    #
    print("Compute feature edges ...")
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(surface)
    feature_edges.BoundaryEdgesOff()
    feature_edges.ManifoldEdgesOff()
    feature_edges.NonManifoldEdgesOff()
    feature_edges.FeatureEdgesOn()
    feature_edges.SetFeatureAngle(angle)
    feature_edges.Update()

    boundary_edges = feature_edges.GetOutput()
    clean_filter = vtk.vtkCleanPolyData()
    boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
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
        boundary_edge_components.append(component)
        conn_filter.DeleteSpecifiedRegion(edge_id)
        edge_id += 1

    print("Number of edges: {0:d}".format(edge_id))

    ## Identify the cells incident to the feature edges.
    #
    print("Identify edge cells ...")

    # Create a set of edge nodes.
    edge_nodes = set()
    for edge in boundary_edge_components:
        edge_num_points = edge.GetNumberOfPoints()
        edge_node_ids = edge.GetPointData().GetArray('GlobalNodeID')
        for i in range(edge_num_points):
            nid = edge_node_ids.GetTuple1(i)
            #nid = edge_node_ids.GetValue(i)
            edge_nodes.add(nid)

    # Create a set of cell IDs incident to the edge nodes.
    surf_points = surface.GetPoints()
    num_cells = surface.GetNumberOfCells()
    surf_node_ids = surface.GetPointData().GetArray('GlobalNodeID')
    edge_cell_ids = set()

    for i in range(num_cells):
        cell = surface.GetCell(i)
        cell_pids = cell.GetPointIds()
        num_ids = cell_pids.GetNumberOfIds()
        for j in range(num_ids):
            pid = surf_node_ids.GetValue(cell_pids.GetId(j))
            if pid in edge_nodes: 
                edge_cell_ids.add(i)
                break

    ## Identify boundary faces using edge cells.
    #
    cell_visited = set()
    cell_normals = surface.GetCellData().GetArray('Normals')
    feature_angle = cos((MATH_PI/180.0) * angle)
    new_cells = deque()
    faces = defaultdict(list)
    face_id = 1
    print("Traverse edge cells ...")

    for cell_id in edge_cell_ids:
        if cell_id in cell_visited:
            continue

        add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces[face_id])

        faces[face_id].append(cell_id)

        while len(new_cells) != 0:
            new_cell_id = new_cells.pop()
            if new_cell_id not in cell_visited:
                faces[face_id].append(new_cell_id)
            add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, new_cell_id, new_cells, feature_angle, faces[face_id])

        face_id += 1

    ## Check that we got all of the cells.
    print("Number of cells visited: {0:d}".format(len(cell_visited)))
    print("Number of faces: {0:d}".format(face_id))
    faces_size = 0
    face_ids = []
    for face_id in faces:
        cell_list = faces[face_id]
        faces_size += len(cell_list)
        face_ids.append(face_id)
    print("Number of faces cells: {0:d}".format(faces_size))

    ## Add the 'ModelFaceID' cell data array identifying each cell with a face ID.
    #
    face_ids_data = vtk.vtkIntArray()
    face_ids_data.SetNumberOfValues(num_cells)
    face_ids_data.SetName("ModelFaceID")
    for face_id in faces:
        cell_list = faces[face_id]
        for cell_id in cell_list:
            face_ids_data.SetValue(cell_id, face_id);
    surface.GetCellData().AddArray(face_ids_data)

    # Write the surface with the 'ModelFaceID' cell data array.
    ''' for debugging
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_base_name + "-boundary.vtp");
    writer.SetInputData(surface)
    writer.Write()
    '''

    # Write the surface without any data arrays.
    ''' for debugging
    surface.GetCellData().RemoveArray('ModelFaceID')
    surface.GetCellData().RemoveArray('GlobalElementID')
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_base_name + "-no-faceIDs.vtp")
    writer.SetInputData(surface)
    writer.Write()
    '''

    return face_ids

def add_new_cells(surface, cell_normals, edge_cell_ids, cell_visited, cell_id, new_cells, feature_angle, faces):
    cell = surface.GetCell(cell_id)
    cell_visited.add(cell_id)
    num_edges = cell.GetNumberOfEdges()
    cell_normal = [ cell_normals.GetComponent(cell_id,j) for j in range(3)]

    for i in range(num_edges):
        edge = cell.GetEdge(i)
        edge_ids = edge.GetPointIds()
        pid1 = edge_ids.GetId(0)
        pid2 = edge_ids.GetId(1)
        adj_cell_ids = vtk.vtkIdList()
        surface.GetCellEdgeNeighbors(cell_id, pid1, pid2, adj_cell_ids)

        for j in range(adj_cell_ids.GetNumberOfIds()):
            adj_cell_id = adj_cell_ids.GetId(j)
            if adj_cell_id not in cell_visited:
                add_cell = True
                if adj_cell_id in edge_cell_ids:
                    dp = sum([ cell_normal[k] * cell_normals.GetComponent(adj_cell_id,k) for k in range(3)] )
                    if dp < feature_angle:
                        add_cell = False
                if add_cell: 
                    new_cells.append(adj_cell_id)
                    cell_visited.add(cell_id)

def build_model(surface):
    '''Build an SV PolyData model from the surface.
    '''
    print('Build an SV PolyData model from the surface')
    angle = 60.0
    extract_surface_boundary_faces(surface, angle, "")
    model = sv.modeling.PolyData()
    model.set_surface(surface)
    #face_ids = model.compute_boundary_faces(angle=60.0)
    face_ids = model.get_face_ids()
    #print("Surface face IDs: " + str(face_ids))
    return model

def get_surface(mesh):
    '''Get the mesh surface. 
    '''
    print('Get the mesh surface')
    geom_filter = vtk.vtkGeometryFilter()
    geom_filter.SetInputData(mesh)
    geom_filter.Update()
    geom = geom_filter.GetOutput()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(geom)
    normals.SplittingOff()
    normals.ComputeCellNormalsOn()
    normals.ComputePointNormalsOn()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.Update()

    surface = normals.GetOutput()
    surface.BuildLinks()
    return surface 

def add_node_ids(mesh):
    '''Add a GlobalNodeID point array.
    '''
    print('Add node IDs')
    num_points = mesh.GetNumberOfPoints()
    node_ids = vtk.vtkIntArray()
    node_ids.SetName("GlobalNodeID")
    node_ids.SetNumberOfComponents(1)
    node_ids.SetNumberOfTuples(num_points)

    for i in range(num_points):
        node_ids.SetValue(i,i+1)

    mesh.GetPointData().AddArray(node_ids)

def add_element_ids(mesh):
    '''Add a GlobalElementID cell array.
    '''
    print('Add element IDs')
    num_cells = mesh.GetNumberOfCells()
    element_ids = vtk.vtkIntArray()
    element_ids.SetName("GlobalElementID")
    element_ids.SetNumberOfComponents(1)
    element_ids.SetNumberOfTuples(num_cells)

    for i in range(num_cells):
        element_ids.SetValue(i,i+1)

    mesh.GetCellData().AddArray(element_ids)

def add_region_ids(mesh):
    '''Add a ModelRegionID cell array.

       Assume a single region.
    '''
    print('Add region IDs')
    num_cells = mesh.GetNumberOfCells()
    region_ids = vtk.vtkIntArray()
    region_ids.SetName("ModelRegionID")
    region_ids.SetNumberOfComponents(1)
    region_ids.SetNumberOfTuples(num_cells)

    for i in range(num_cells):
        region_ids.SetValue(i,1)

    mesh.GetCellData().AddArray(region_ids)

def write_model(file_base_name, surface, face_ids):
#def write_model(file_base_name, model):
    '''Write model .vtp and XML .mdl files..
    '''
    model_name = file_base_name + '-model'
    file_format = "vtp"
    #model.write(file_name=model_name, format=file_format)
    file_name = file_base_name + "-model.vtp"
    write_surface_mesh(file_name, surface)

    ## Create the XML data.
    #
    root = etree.Element("model")
    root.attrib['type'] = 'PolyData'

    time_step = etree.SubElement(root, 'timestep', id='0')

    model_element = etree.SubElement(time_step, 'model_element', type="PolyData",  num_sampling="0")
    segmentations = etree.SubElement(model_element, 'segmentations')
    seg = etree.SubElement(segmentations, 'seg', name=file_base_name)

    # Write face information.
    #face_ids = model.get_face_ids()
    faces = etree.SubElement(model_element, 'faces')
    for i,face_id in enumerate(face_ids):
        face_name = 'face_' + str(face_id)
        face_type = 'wall'
        face = etree.SubElement(faces, 'face', id=str(i+1), name=face_name, type=face_type,
          visible="true", opacity="1", color1="1", color2="1", color3="1")

    # Write XML data.
    tree = etree.ElementTree(root)
    #etree.indent(tree, space="   ", level=0)
    file_name = file_base_name + '-model.mdl'
    with open(file_name, 'wb') as f:
        tree.write(f, encoding='utf-8')

    return model_name 

def write_surface_mesh(file_name, mesh):
    '''Write a surface mesh.
    '''
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

def write_volume_mesh(file_base_name, mesh, model_name):
    '''Write a volume mesh to a VTK vtu file and mesh information to the .msh file..
    '''
    file_name = file_base_name + "-mesh.vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

    ## Create the XML data.
    #
    root = etree.Element("mitk_mesh", type="TetGen", model_name=model_name)

    time_step = etree.SubElement(root, 'timestep', id='0')

    mesh_element = etree.SubElement(time_step, 'mesh', type="TetGen")

    command_history = etree.SubElement(mesh_element, 'command_history')
    command = etree.SubElement(command_history, 'command', content="option surface 1")
    command = etree.SubElement(command_history, 'command', content="option volume 1")
    command = etree.SubElement(command_history, 'command', content="option UseMMG 1")
    command = etree.SubElement(command_history, 'command', content="option GlobalEdgeSize 0.7992")
    command = etree.SubElement(command_history, 'command', content="setWalls")
    command = etree.SubElement(command_history, 'command', content="option Optimization 3")
    command = etree.SubElement(command_history, 'command', content="generateMesh")
    command = etree.SubElement(command_history, 'command', content="writeMesh")

    # Write XML data.
    tree = etree.ElementTree(root)
    file_name = file_base_name + '-mesh.msh'
    with open(file_name, 'wb') as f:
        tree.write(f, encoding='utf-8')

def read_mesh(file_name, scale):
    '''Read a VTK vtu file.
    '''
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    mesh = reader.GetOutput()
    print("Mesh extent: {0:s}".format(str(mesh.GetBounds())))

    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(mesh)
    com_filter.Update()
    center = com_filter.GetCenter()
    print("Mesh center: {0:s}".format(str(center)))

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.Scale(scale, scale, scale)
    transform.Translate(-center[0], -center[1], -center[2])
    transform.Update()

    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetInputData(mesh) 
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    mesh = transform_filter.GetOutput()
    mesh.Modified()

    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(mesh)
    com_filter.Update()
    center = com_filter.GetCenter()
    print("New mesh center: {0:s}".format(str(center)))
    print("New mesh extent: {0:s}".format(str(mesh.GetBounds())))

    # check_nodes(mesh)
    #print_connectivity(mesh)

    num_points = mesh.GetNumberOfPoints()
    points = mesh.GetPoints()
    print("Number of points: {0:d}".format(num_points))

    num_cells = mesh.GetNumberOfCells()
    print("Number of cells: {0:d}".format(num_cells))
    cells = mesh.GetCells()

    return mesh

if __name__ == '__main__':
    file_name = sys.argv[1]
    #file_name = 'Cylinder_HDF5.vtu'
    #file_name = 'harfdmeshbetter_HDF5.vtu'
    file_base_name, ext = os.path.splitext(file_name)

    # The mesh scale may be too small to be viewed in SV.
    scale = 100.0
    mesh = read_mesh(file_name, scale)

    # Add a ModelRegionID array to the mesh.
    add_region_ids(mesh)

    # Add a GlobalElementID array to the mesh.
    add_element_ids(mesh)

    # Add a GlobalNodeID array to the mesh.
    add_node_ids(mesh)

    # Get the mesh surface triangles.
    surface = get_surface(mesh)

    # Build an SV model from the surface.
    #model = build_model(surface)
    angle = 60.0
    face_ids = extract_surface_boundary_faces(surface, angle, file_base_name)

    # Write the surface mesh.
    file_name = file_base_name + "-mesh.vtp"
    write_surface_mesh(file_name, surface)

    # Write the model and .mdl file.
    model_name = write_model(file_base_name, surface, face_ids)

    # Write the volume mesh and .msh file.
    write_volume_mesh(file_base_name, mesh, model_name)


