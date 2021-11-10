#!/usr/bin/env python

'''
This script is used to create the fsi mesh-complete files from the .vtu and .vtp files 
created from SV Meshing boundary layer meshing. A boundary layer mesh is required with 
region IDs; this is enabled by checking the SV 'Convert Boundary Layer to New Region/Domain' 
option. Fluid elements are identified using region ID 1, solid elements region ID 2.

A model .mdl file is used to identify each face with its ID, name, and type (wall or cap). 
This is the model referenced in the SV Meshing tool. The mesh surface .vtp file contains 
'ModelFaceID' CellData that identifies the mesh faces and 'GlobalElementID' CellData that 
identifies elements.

The solid mesh will have both inner and outer components. The inner solid mesh face interfaces 
to the fluid wall face(s).

Files are written for each fluid and solid volume mesh, and the faces for each used to specify boundary
conditions. The file naming convention is

  solid-mesh.vtu		
  solid-CAP_FACE_NAME1.vtp	
  solid-CAP_FACE_NAME2.vtp	
  ...
  solid-WALL_FACE_NAME1-inner.vtp	
  solid-WALL_FACE_NAME1-outer.vtp	
  solid-WALL_FACE_NAME2-inner.vtp	
  solid-WALL_FACE_NAME2-outer.vtp	
  ...
  fluid-mesh.vtu
  solid-CAP_FACE_NAME1.vtp	
  solid-CAP_FACE_NAME2.vtp	
  ...
  fluid-WALL_FACE_NAME1.vtp	
  fluid-WALL_FACE_NAME1.vtp	
  ...

Usage: 

  create-fsi-mesh-complete.py  
      --fluid-region-id FLUID_REGION_ID 
      --mdl-file MDL_FILE 
      --solid-region-id SOLID_REGION_ID 
      --surface-mesh SURFACE_MESH 
      --volume-mesh VOLUME_MESH

  where

      FLUID_REGION_ID - The fluid region ID (usually 1)

      MDL_FILE - The SV modeling .mdl file    

      SOLID_REGION_ID - The solid region ID (usually 2)

      SURFACE_MESH - The surface mesh (.vtp) file.

      VOLUME_MESH - The volume mesh (.vtu) file.

'''

from collections import defaultdict 
import argparse
import os
import sys
import vtk
import xml.etree.ElementTree as et

class MeshPhysics(object):
    Fluid = "fluid"
    Solid = "solid"

class FaceTypes(object):
    Cap = "cap"
    Inlet = "inlet"
    Outlet = "outlet"
    Wall = "wall"

class VtkDataNames(object):
    GlobalElementID = "GlobalElementID"
    GlobalNodeID = "GlobalNodeID"
    ModelRegionID = "ModelRegionID"
    ModelFaceID = "ModelFaceID"

class BcFace(object):
    ''' This class stores BC face data for a mesh. 
    '''
    def __init__(self, face_name, face_id, face_type, mesh=None): 
        self.name = face_name
        self.id = face_id
        self.type = face_type
        self.mesh = None 
        self.node_ids = None 

        if mesh != None:
            self.set_mesh( mesh) 

    def set_mesh(self, mesh): 
        self.mesh = mesh
        self.node_ids = get_node_ids(mesh)

class Mesh(object):
    ''' This class stores volume and surface mesh data for a given region ID. 

        The mesh is assumed to be a subset of 'sv_volume_mesh' determined by its region ID.
    '''
    def __init__(self, sv_volume_mesh, region_id, physics):
        self.file_name = None 
        self.region_id = region_id
        self.physics = physics
        self.surface_mesh = None 
        self.bc_faces = None 
        self.nodal_coords = None

        # Extract the volume mesh for the given region ID.
        self.volume_mesh = get_region_mesh(sv_volume_mesh, region_id)

        # Create a nodal coordinate map and coordinate hash table.
        self.set_node_coords()

    def set_node_coords(self):
        ''' Create a nodal coordinate map and coordinate hash table.
        '''
        pt = 3*[0.0]
        self.nodal_coords = {}
        node_ids = self.volume_mesh.GetPointData().GetArray(VtkDataNames.GlobalNodeID)
        num_points = self.volume_mesh.GetNumberOfPoints()
        points = self.volume_mesh.GetPoints()

        # Create nodal IDs to coordinates map.
        #
        max_x = -1e9
        max_y = -1e9
        max_z = -1e9
        min_x = 1e9
        min_y = 1e9
        min_z = 1e9

        for i in range(num_points):
            nid = node_ids.GetValue(i)
            points.GetPoint(i, pt)
            x = pt[0]
            y = pt[1]
            z = pt[2]

            self.nodal_coords[nid] = [x, y, z] 

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
        #_for i in range(volume_mesh.GetNumberOfPoints())

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
  
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z

        # Create nodal coordinates hash table.
        #
        point_hash = defaultdict(list)

        for i in range(num_points):
            point = points.GetPoint(i, pt)
            pid = node_ids.GetValue(i)
            x = pt[0]
            y = pt[1]
            z = pt[2]

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

        self.point_hash = point_hash

    def get_node_id(self, point):
        ''' Get the node ID for the given point.
        '''
        node_id = -1
        num_points = self.volume_mesh.GetNumberOfPoints()
        x = point[0]
        y = point[1]
        z = point[2]
        xs = (x - self.min_x) / self.dx
        ys = (y - self.min_y) / self.dy
        zs = (z - self.min_z) / self.dz
        ih = xs * num_points
        jh = ys * num_points
        kh = zs * num_points
        index = int(ih + jh + kh) 

        pts = self.point_hash[index]
        found_pt = False
        for hpt in pts:
            dx = hpt[0] - x
            dy = hpt[1] - y
            dz = hpt[2] - z
            d = dx*dx + dy*dy + dz*dz
            if d == 0.0:
                node_id = hpt[3]
                break
        #_for hpt in pts

        return node_id 

    def extract_faces(self, bc_faces):
        ''' Extract face surface geometry for this object's region ID.
        '''
        print("\n========== Mesh.extract_faces {0:s} ==========".format(self.physics))
        print("[Mesh.extract_faces] Region ID: {0:d}".format(self.region_id))
        self.bc_faces = defaultdict(list)

        for face_id, bc_face in bc_faces.items():
            face_type = bc_face.type
            face_name = bc_face.name
            mesh = bc_face.mesh 
            print("[Mesh.extract_faces] ---------- Face ID {0:s} {1:d}: {2:s} ---------".format(face_name, face_id, face_type))
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(mesh)
            threshold.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelRegionID)
            threshold.ThresholdBetween(self.region_id,self.region_id)
            threshold.Update();

            surfacer = vtk.vtkDataSetSurfaceFilter()
            surfacer.SetInputData(threshold.GetOutput())
            surfacer.Update()
            surface = surfacer.GetOutput()
            print("[Mesh.extract_faces] Surface number of points: %d" % surface.GetNumberOfPoints())
            print("[Mesh.extract_faces] Surface number of cells: %d" % surface.GetNumberOfCells())

            if surface.GetNumberOfPoints() == 0:
                msg = "No region ID " + str(self.region_id) + " found in " + self.physics + " mesh. "
                msg += "A boundary layer mesh is required with region IDs (SV 'Convert Boundary Layer to New Region/Domain' option)."
                raise Exception(msg)
            
            # Create a new GlobalNodeID data for the face that matches
            # the volume mesh node IDs.
            #
            node_ids = surface.GetPointData().GetArray(VtkDataNames.GlobalNodeID)
            num_points = surface.GetNumberOfPoints()
            points = surface.GetPoints()

            node_ids_data = vtk.vtkIntArray()
            node_ids_data.SetNumberOfValues(num_points)
            node_ids_data.SetName(VtkDataNames.GlobalNodeID)
            pt = 3*[0.0]

            for i in range(num_points):
                points.GetPoint(i, pt)
                nid = self.get_node_id(pt)
                node_ids_data.SetValue(i, nid)

            surface.GetPointData().RemoveArray(VtkDataNames.GlobalNodeID)
            surface.GetPointData().AddArray(node_ids_data)

            # Extract solid wall faces that have disjoint inner and outer parts. 
            #
            if ((face_type == FaceTypes.Wall) and (self.physics == MeshPhysics.Solid)):
                print("[Mesh.extract_faces] Extract solid wall faces ...")
                surface_ids = get_node_ids(surface)
                conn_filter = vtk.vtkPolyDataConnectivityFilter()
                conn_filter.SetInputData(surface)
                conn_filter.SetExtractionModeToSpecifiedRegions()

                wall_num = 0
                #boundary_faces = []
                while True:
                    conn_filter.AddSpecifiedRegion(wall_num)
                    conn_filter.Update()
                    component = vtk.vtkPolyData()
                    component.DeepCopy(conn_filter.GetOutput())
                    if component.GetNumberOfCells() <= 0:
                        break

                    clean_filter = vtk.vtkCleanPolyData()
                    clean_filter.SetInputData(component)
                    clean_filter.Update();
                    component = clean_filter.GetOutput()

                    #boundary_faces.append(component)
                    conn_filter.DeleteSpecifiedRegion(wall_num)
                    print("[Mesh.extract_faces] Wall face: {0:d}".format(wall_num+1))
                    print("[Mesh.extract_faces]   Number of points: %d" % component.GetNumberOfPoints())
                    print("[Mesh.extract_faces]   Number of cells: %d" % component.GetNumberOfCells())
                    wall_num += 1
                    self.bc_faces[face_id].append( BcFace(face_name, face_id, face_type, component) )
            else:
                self.bc_faces[face_id].append( BcFace(face_name, face_id, face_type, surface) )
        #_for fid, face in surface_faces.items()

    def get_wall_faces(self):
        ''' Get BC faces of type Wall.
        '''
        print('========== get_wall_faces ==========')
        print('[get_wall_faces] Physics: {0:s}'.format(self.physics))
        wall_faces = []
        for fid, bc_faces in self.bc_faces.items():
            for bc_face in bc_faces:
                if bc_face.type == FaceTypes.Wall:
                    wall_faces.append(bc_face)
        print('[get_wall_faces] Number of wall faces: {0:d}'.format(len(wall_faces)))
        return wall_faces 

    def is_inner_solid_face(self, bc_face, fluid_wall_faces):
        ''' Check is a face is an inner solid wall faces.
        '''
        for wall_face in fluid_wall_faces:
            if len(wall_face.node_ids.intersection(bc_face.node_ids)) != 0:
                return True
        return False

    def write_faces(self, fluid_wall_faces=None):
        ''' Write BC faces to VTK .vtp files.
        '''
        print('========== write_faces ==========')
        for fid, bc_faces in self.bc_faces.items():
            print("[write_faces] ")
            print("[write_faces] Number of {0:s} bc_faces: {1:d}".format(self.physics, len(bc_faces)))
            for bc_face in bc_faces:
                face_type = bc_face.type
                face_name = bc_face.name
                base_name = self.physics
                print("[write_faces] Face name: {0:s}  type: {1:s}".format(face_name, face_type))
                if ((fluid_wall_faces != None) and (face_type == FaceTypes.Wall)):
                    if self.is_inner_solid_face(bc_face, fluid_wall_faces):
                        write_surface_mesh(base_name, face_name+'-inner', bc_face.mesh)
                    else:
                        write_surface_mesh(base_name, face_name+'-outer', bc_face.mesh)
                else:
                    write_surface_mesh(base_name, face_name, bc_face.mesh)

    def write_volume(self):
        ''' Write a volume mesh to a VTK .vtu file.
        '''
        file_base_name = self.physics
        write_volume_mesh(file_base_name, self.volume_mesh)

class Args(object):
    ''' This class defines the command line arguments to the script.
    '''
    PREFIX = "--"
    FLUID_REGION_ID = "fluid_region_id"
    INLET_FACES = "inlet_faces"
    OUTLET_FACES = "outlet_faces"
    MDL_FILE = "mdl_file"
    SOLID_REGION_ID = "solid_region_id"
    SURFACE_MESH = "surface_mesh"
    VOLUME_MESH = "volume_mesh"
    WALL_FACES = "wall_faces"

def cmd(name):
    ''' Create an argparse command argument.
    '''
    return Args.PREFIX + name.replace("_", "-")

def parse_args():
    ''' Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(cmd(Args.FLUID_REGION_ID), help="The fluid region ID.", type=int, required=True)
    #parser.add_argument(cmd(Args.INLET_FACES),     help="The inlet face IDs.", required=True)
    parser.add_argument(cmd(Args.MDL_FILE),        help="The SV modeling .mdl file.", required=True)
    #parser.add_argument(cmd(Args.OUTLET_FACES),    help="The outlet face IDs.", required=True)
    parser.add_argument(cmd(Args.SOLID_REGION_ID), help="The solid region ID.", type=int, required=True)
    parser.add_argument(cmd(Args.SURFACE_MESH),    help="The surface mesh (.vtp) file.", required=True)
    parser.add_argument(cmd(Args.VOLUME_MESH),     help="The volume mesh (.vtu) file.", required=True)
    #parser.add_argument(cmd(Args.WALL_FACES),      help="The walls face IDs.", required=True)

    return parser.parse_args(), parser.print_help

def get_node_ids(polydata):
        node_ids = polydata.GetPointData().GetArray(VtkDataNames.GlobalNodeID)
        num_points = polydata.GetNumberOfPoints()
        id_set = set()
        for i in range(num_points):
            nid = node_ids.GetValue(i)
            id_set.add(nid)
        return id_set

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
    sphere.SetRadius(0.05)
    sphere.SetPhiResolution(16)
    sphere.SetThetaResolution(16)
    sphere.Update()
    poly_data = sphere.GetOutput()
    return add_geom(poly_data, renderer)

def get_surface_faces(surface_mesh, bc_faces):
    ''' Get the faces from the surface mesh.
 
        The faces are vtkPolyData objects with cell data arrays.
    '''
    print("\n========== get_surface_faces ==========")
    face_ids = surface_mesh.GetCellData().GetArray(VtkDataNames.ModelFaceID)
    face_ids_range = 2*[0]
    face_ids.GetRange(face_ids_range, 0)
    min_id = int(face_ids_range[0])
    max_id = int(face_ids_range[1])
    print("[get_surface_faces] Face IDs range: {0:d} {1:d}".format(min_id, max_id))

    ## Extract face geometry.
    #
    for i in range(min_id, max_id+1):
        if i not in bc_faces:
            continue
        print("[get_surface_faces] ----- Face ID {0:d} ----".format(i))
        print("[get_surface_faces] Face name: {0:s} ".format(bc_faces[i].name))
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(surface_mesh)
        threshold.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelFaceID)
        threshold.ThresholdBetween(i,i)
        threshold.Update();

        surfacer = vtk.vtkDataSetSurfaceFilter()
        surfacer.SetInputData(threshold.GetOutput())
        surfacer.Update()
        bc_faces[i].set_mesh( surfacer.GetOutput() )
        print("[get_surface_faces] Face number of points: %d" % bc_faces[i].mesh.GetNumberOfPoints())
        print("[get_surface_faces] Face number of cells: %d" % bc_faces[i].mesh.GetNumberOfCells())
    #_for i in range(min_id, max_id+1)

def add_mesh_geom(mesh, renderer, color=[1,1,1]):
    ''' Add mesh to renderer.
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
    #actor.GetProperty().SetOpacity(0.5) 
    #actor.GetProperty().SetEdgeColor(1, 0, 0) 
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    #actor.GetProperty().SetPointSize(5)
    renderer.AddActor(actor)

def get_region_mesh(mesh, region_id): 
    ''' Extract a mesh region from a mesh using a region ID.
    '''
    thresholder = vtk.vtkThreshold()
    thresholder.SetInputData(mesh);
    thresholder.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelRegionID);
    thresholder.ThresholdBetween(region_id, region_id);
    thresholder.Update();
    return thresholder.GetOutput()
#_get_region_mesh(mesh, region_id)

def read_mdl_file(file_name):
    ''' Read an SV modeling .mdl file.
    '''
    print("\n========== read_mdl_file ==========")
    # Remove 'format' tag from xml file.
    f = open(file_name, "r")
    lines = f.readlines()
    new_lines = []
    for line in lines:
      if '<format' not in line:
        new_lines.append(line)

    # Create string from xml file and parse it.
    xml_string = "".join(new_lines)
    tree = et.ElementTree(et.fromstring(xml_string))
    #tree = et.parse(file_name)
    root = tree.getroot()

    bc_faces = {}
    for face_t in root.iter('face'):
        name = face_t.attrib["name"]
        face_id = int(face_t.attrib["id"])
        face_type = face_t.attrib["type"]
        print("[read_mdl_file] face name: {0:s}  id: {1:d}  type: {2:s}".format(name, face_id, face_type))
        bc_faces[face_id] = BcFace(name, face_id, face_type)

    return bc_faces 

def write_volume_mesh(file_base_name, mesh): 
    file_name = file_base_name + "-mesh.vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

def write_surface_mesh(file_base_name, name, mesh): 
    file_name = file_base_name + "-" + name + ".vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

if __name__ == '__main__':

    args, print_help = parse_args()

    ## Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    ## Read SV modeling .mdl file.
    file_name = args.mdl_file
    bc_faces = read_mdl_file(file_name)
  
    ## Read SV volume mesh.
    file_name = args.volume_mesh
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    volume_mesh = reader.GetOutput()

    ## Read SV surface mesh.
    file_name = args.surface_mesh
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    surface_mesh = reader.GetOutput()

    ## Get the surface mesh faces and inlet, outlet and wall face IDs.
    get_surface_faces(surface_mesh, bc_faces)

    ## Get the fluid mesh.
    fluid = Mesh(volume_mesh, args.fluid_region_id, MeshPhysics.Fluid)
    fluid.extract_faces(bc_faces)
    fluid.write_faces()
    fluid.write_volume()
    fluid_walls = fluid.get_wall_faces()

    ## Get the solid mesh.
    solid = Mesh(volume_mesh, args.solid_region_id, MeshPhysics.Solid)
    solid.extract_faces(bc_faces)
    solid.write_faces(fluid_walls)
    solid.write_volume()

    # Show the meshes.
    add_mesh_geom(fluid.volume_mesh, renderer, color=[0,0,1])
    add_mesh_geom(solid.volume_mesh, renderer, color=[1,0,0])

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    interactor.Start()


