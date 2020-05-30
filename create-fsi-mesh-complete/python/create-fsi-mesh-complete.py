#!/usr/bin/env python

''' This script is used to create fsi mesh-complete files from sv .vtu file. 

 The mesh surface .vtp file contains "ModelFaceID" CellData that identifies
 the mesh faces and "GlobalElementID" CellData that identifies elements.

'''

from collections import defaultdict 
import argparse
import os
import sys
import vtk
from sets import Set

class MeshPhysics(object):
    Fluid = "fluid"
    Solid = "solid"

class VtkDataNames(object):
    GlobalElementID = "GlobalElementID"
    ModelRegionID = "ModelRegionID"
    ModelFaceID = "ModelFaceID"

class BcFaces(object):
    ''' This class stores BC face data for a mesh. 
    '''
    def __init__(self, mesh_faces, inlet_ids, outlet_ids, wall_ids):
        self.inlet_ids = inlet_ids 
        self.outlet_ids = outlet_ids 
        self.wall_ids = wall_ids 
        self.mesh_faces = mesh_faces 

    def get_face_type(self, face_id):
        if face_id in self.inlet_ids:
            face_type = "inlet"
        elif face_id in self.outlet_ids:
            face_type = "outlet"
        else:
            face_type = "wall"

        return face_type 

class Mesh(object):
    ''' This class stores face data for a mesh. 
    '''
    def __init__(self, mesh, region_id, physics):
        self.file_name = None 
        self.region_id = region_id
        self.physics = physics
        self.volume_mesh = get_region_mesh(mesh, region_id)
        self.surface_mesh = None 
        self.mesh_faces = None 

    def extract_faces(self, bc_faces):
        print("\n========== Mesh.extract_faces {0:s} ==========".format(self.physics))
        print("[Mesh.extract_faces] Region ID: {0:d}".format(self.region_id))
        self.mesh_faces = {}
        surface_faces = bc_faces.mesh_faces

        for fid, face in surface_faces.items():
            face_type = bc_faces.get_face_type(fid)
            print("[Mesh.extract_faces] ---------- Face ID {0:d}: {1:s} ---------".format(fid, face_type))
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(face)
            threshold.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelRegionID)
            threshold.ThresholdBetween(self.region_id,self.region_id)
            threshold.Update();

            surfacer = vtk.vtkDataSetSurfaceFilter()
            surfacer.SetInputData(threshold.GetOutput())
            surfacer.Update()
            self.mesh_faces[fid] = surfacer.GetOutput()
            print("Face number of points: %d" % self.mesh_faces[fid].GetNumberOfPoints())
            print("Face number of cells: %d" % self.mesh_faces[fid].GetNumberOfCells())
        #_for fid, face in surface_faces.items()

    #_extract_faces(self, surface_faces)

    def write_faces(self):
        for fid, face in self.mesh_faces.items():
            face_type = bc_faces.get_face_type(fid)
            base_name = self.physics + "-" + face_type
            write_surface_mesh(base_name, face, str(fid))

class Args(object):
    ''' This class defines the command line arguments to the script.
    '''
    PREFIX = "--"
    FLUID_REGION_ID = "fluid_region_id"
    INLET_FACES = "inlet_faces"
    OUTLET_FACES = "outlet_faces"
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
    parser.add_argument(cmd(Args.INLET_FACES),     help="The inlet face IDs.", required=True)
    parser.add_argument(cmd(Args.OUTLET_FACES),    help="The outlet face IDs.", required=True)
    parser.add_argument(cmd(Args.SOLID_REGION_ID), help="The solid region ID.", type=int, required=True)
    parser.add_argument(cmd(Args.SURFACE_MESH),    help="The surface mesh (.vtp) file.", required=True)
    parser.add_argument(cmd(Args.VOLUME_MESH),     help="The volume mesh (.vtu) file.", required=True)
    parser.add_argument(cmd(Args.WALL_FACES),      help="The walls face IDs.", required=True)

    return parser.parse_args(), parser.print_help

def get_surface_faces(surface_mesh, args):
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

    # Get inlet, outlet and face IDs.
    inlet_ids = [int(x) for x in args.inlet_faces.split(",") ] 
    outlet_ids = [int(x) for x in args.outlet_faces.split(",") ] 
    wall_ids = [int(x) for x in args.wall_faces.split(",") ] 

    ## Extract face geometry.
    #
    mesh_faces = {}

    for i in range(min_id, max_id+1):
        print("[get_surface_faces] ---------- ID {0:d} ---------".format(i))
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(surface_mesh)
        threshold.SetInputArrayToProcess(0,0,0,1,VtkDataNames.ModelFaceID)
        threshold.ThresholdBetween(i,i)
        threshold.Update();

        surfacer = vtk.vtkDataSetSurfaceFilter()
        surfacer.SetInputData(threshold.GetOutput())
        surfacer.Update()
        mesh_faces[i] = surfacer.GetOutput()
        print("[get_surface_faces] Face number of points: %d" % mesh_faces[i].GetNumberOfPoints())
        print("[get_surface_faces] Face number of cells: %d" % mesh_faces[i].GetNumberOfCells())
        #write_surface_mesh("surface", mesh_faces[i], str(i))
    #_for i in range(min_id, max_id+1)

    return BcFaces(mesh_faces, inlet_ids, outlet_ids, wall_ids)

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
    thresholder.SetInputArrayToProcess(0,0,0,1,"ModelRegionID");
    thresholder.ThresholdBetween(region_id, region_id);
    thresholder.Update();
    return thresholder.GetOutput()
#_get_region_mesh(mesh, region_id)

def write_volume_mesh(file_base_name, mesh, region_id): 
    file_name = file_base_name + "-mesh-" + str(region_id) + ".vtu"
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

def write_surface_mesh(file_base_name, mesh, name): 
    file_name = file_base_name + "-" + name + ".vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(mesh)
    writer.Update()
    writer.Write()

if __name__ == '__main__':

    args, print_help = parse_args()
  
    ## Read volume mesh.
    file_name = args.volume_mesh
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()
    volume_mesh = reader.GetOutput()

    ## Read surface mesh.
    file_name = args.surface_mesh
    file_base_name, ext = os.path.splitext(file_name)
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    surface_mesh = reader.GetOutput()

    ## Get the surface mesh faces and inlet, outlet and wall face IDs.
    bc_faces = get_surface_faces(surface_mesh, args)

    ## Get the fluid mesh.
    fluid = Mesh(volume_mesh, args.fluid_region_id, MeshPhysics.Fluid)
    fluid.extract_faces(bc_faces)
    fluid.write_faces()

    ## Get the solid mesh.
    solid = Mesh(volume_mesh, args.solid_region_id, MeshPhysics.Solid)
    solid.extract_faces(bc_faces)
    solid.write_faces()

    ## Create renderer and graphics window.
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.6, 0.6, 0.6)
    renderer_win.SetSize(800, 800)

    # Show the meshes.
    add_mesh_geom(fluid.volume_mesh, renderer, color=[0,0,1])
    add_mesh_geom(solid.volume_mesh, renderer, color=[1,0,0])

    # Create a trackball interacter to transoform the geometry using the mouse.
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    #interactor.Start()


