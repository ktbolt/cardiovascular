
'''
This script generates a mesh using radius based meshing, a method based on the 
distance to the solid model's centrline.
'''
import sv
import sv_vis
import os
import sys
import vtk
import math

def display_sphere(model_polydata_name, id):
    '''
    Display a sphere at the given point. 
    '''
    model_polydata = sv.Repository.ExportToVtk(model_polydata_name)
    points = model_polydata.GetPoints()
    pt = [0.0, 0.0, 0.0]
    points.GetPoint(id, pt)
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(pt[0], pt[1], pt[2])
    sphere.SetRadius(0.05)
    sphere.Update()
    sphere_name = "sphere" + str(id)
    sv.Repository.ImportVtkPd(sphere.GetOutput(), sphere_name)
    sphere_actor = sv_vis.pRepos(renderer, sphere_name)[1]
    sphere_actor.GetProperty().SetColor(1,1,1)
    sv_vis.polyDisplayWireframe(renderer, sphere_name)

def generate_mesh(model_name, solid_file_name, dist_name):
    '''
    Generate a mesh from a solid model.
    '''
    sv.Mesh.SetKernel('TetGen')
    mesh = sv.Mesh.Mesh()
    mesh.NewObject('mesh')
    mesh.LoadModel(solid_file_name)

    mesh.GetBoundaryFaces(80)
    face_info = mesh.GetModelFaceInfo()
    print ("Mesh model face info: " + str(face_info))

    mesh.NewMesh()
    mesh.SetMeshingOptions('GlobalEdgeSize', [edge_size])
    mesh.SetMeshingOptions('SurfaceMeshFlag',[1])
    mesh.SetMeshingOptions('VolumeMeshFlag',[1])
    mesh.SetMeshingOptions('MeshWallFirst',[1])
    mesh.SetMeshingOptions('Optimization',[3])
    mesh.SetMeshingOptions('QualityRatio',[1.4])
    mesh.SetMeshingOptions('UseMMG',[1])
    mesh.SetMeshingOptions('NoBisect',[1])
    mesh.SetMeshingOptions('setWalls',[1])

    # Set the centerline distance array for the mesh.
    #mesh.set_vtk_polydata(dist_name)
    #mesh.set_size_function_based_mesh(edge_size, "DistanceToCenterlines")

    mesh.GenerateMesh()

    ## Save mesh to a file.
    mesh_file_name = os.getcwd() + "/" + model_name + "-mesh.vtp"
    mesh.WriteMesh(mesh_file_name)
    mesh.GetUnstructuredGrid('ug')
    sv.Repository.WriteVtkUnstructuredGrid("ug", "ascii", mesh_file_name)

def calculate_centerlines(model_name, model_polydata_name, source_ids, target_ids):
    '''
    Calculate centerlines and the distance to centerlines array.

    The distance to centerlines is stored in polydata referenced by 'dist_name'.
    '''
    lines_name = model_name + "_lines"
    sep_lines_name = model_name + "_sep_lines"
    voronoi_name = model_name + "_voronoi"
    dist_name = model_name + "_distance"
    sv.VMTKUtils.Centerlines(model_polydata_name, source_ids, target_ids, lines_name, voronoi_name)
    sv.VMTKUtils.Separatecenterlines(lines_name, sep_lines_name)
    sv.VMTKUtils.Distancetocenterlines(model_polydata_name, sep_lines_name, dist_name)
    # Display the centerlines.
    lines_actor = sv_vis.pRepos(renderer, sep_lines_name)[1]
    lines_actor.GetProperty().SetColor(0,1,0)
    lines_file_name = lines_name + '.vtp' 
    sv.Repository.WriteVtkPolyData(sep_lines_name, "ascii", lines_file_name)

    dist_pd = sv.Repository.ExportToVtk(dist_name)
    dist_array = dist_pd.GetPointData().GetArray('DistanceToCenterlines')
    dist_range = 2*[0.0]
    dist_array.GetRange(dist_range, 0)
    print("Minumum distance: {0:f}".format(dist_range[0]))

    return dist_name

def get_face_center_ids(model_polydata_name, face_centers):
    '''
    Find point IDs for face centers.
    '''
    model_polydata = sv.Repository.ExportToVtk(model_polydata_name)
    points = model_polydata.GetPoints()
    face_point_ids = []
    pt = [0.0, 0.0, 0.0]

    for center in face_centers:
        min_i = 0
        min_d = 1e6
        for i in range(points.GetNumberOfPoints()):
            points.GetPoint(i, pt)
            d = math.pow(pt[0]-center[0],2) + math.pow(pt[1]-center[1],2) + math.pow(pt[2]-center[2],2)
            if (d < min_d):
                min_d = d;
                min_i = i;
        #_for i in range(points.GetNumberOfPoints())
        face_point_ids.append(min_i)
    #_for center in face_centers

    return face_point_ids 

def get_face_center(solid, face_id, color=[1,0,0]):
    '''
    Get the center of a solid model face.
    '''
    model_face = model_name + "_face_" + str(face_id)
    solid.GetFacePolyData(model_face, face_id)

    face_pd = sv.Repository.ExportToVtk(model_face)
    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(face_pd)
    com_filter.Update()
    face_center = com_filter.GetCenter()

    # Show the face.
    face_actor = sv_vis.pRepos(renderer, model_face)[1]
    #sv_vis.polyDisplayWireframe(renderer, model_face_2)
    face_actor.GetProperty().SetColor(color[0],color[1],color[2])
    return face_center 

def read_solid_model(model_name):
    '''
    Read in a solid model.
    '''
    solid_file_name = os.getcwd() + '/' + model_name + '.vtp'
    sv.Solid.SetKernel('PolyData')
    solid = sv.Solid.pySolidModel()
    solid.ReadNative(model_name, solid_file_name)
    solid.GetBoundaryFaces(60)
    print ("Model face IDs: " + str(solid.GetFaceIds()))
    model_polydata_name = model_name + "_pd"
    solid.GetPolyData(model_polydata_name)
    model_actor = sv_vis.pRepos(renderer, model_polydata_name)[1]
    model_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    #sv_vis.polyDisplayWireframe(renderer, model_polydata)
    sv_vis.polyDisplayPoints(renderer, model_polydata_name)
    return solid, model_polydata_name, solid_file_name 

## Create a render and window to display geometry.
renderer, render_window = sv_vis.initRen('mesh-mess')

## Read solid model.
#
# Assume the first id in 'face_ids' is the source, the rest
# are targets for the centerline calculation.
#
model_name = "aorta-outer"
model_name = "aorta-small"

if model_name == "aorta-outer":
    edge_size = 0.4733
    face_ids = [2, 3]
#
elif model_name == "demo":
    face_ids = [2, 3, 4]

elif model_name == "aorta-small":
    edge_size = 0.4431
    face_ids = [2, 3]

solid, model_polydata_name, solid_file_name = read_solid_model(model_name)

## Get cap faces centers.
#
colors = [ [1,0,0], [0,1,0], [0,0,1], [1,1,0], [1,0,1] ]
face_centers = []
for i,face_id in enumerate(face_ids):
    color = colors[i]
    face_center = get_face_center(solid, face_id, color)
    face_centers.append(face_center)
    print("Face {0:d}  color: {1:s}".format(face_id, str(color)))

## Find point IDs for face centers.
#
face_point_ids = get_face_center_ids(model_polydata_name, face_centers)
print("Face point IDs: {0:s}".format(str(face_point_ids)))

## Calculate centerlines.
#
source_ids = face_point_ids[0:1]
target_ids = face_point_ids[1:] 
print("Source IDs: {0:s}".format(str(source_ids)))
print("Target IDs: {0:s}".format(str(target_ids)))
dist_name = calculate_centerlines(model_name, model_polydata_name, source_ids, target_ids)

## Display a sphere at the source. 
#
id = source_ids[0]
display_sphere(model_polydata_name, id)

## Generate the mesh for the solid model. 
#
try:
    generate_mesh(model_name, solid_file_name, dist_name)
except:
    pass

## Display the graphics.
sv_vis.interact(renderer, sys.maxsize)


