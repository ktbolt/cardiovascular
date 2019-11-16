
import sv
import sv_vis
import os
import sys
import vtk

print(dir(sv))

## Create a render and window to display geometry.
renderer, render_window = sv_vis.initRen('mesh-mess')

## Read model.
#
model_name = "one-vessel"
model_name = "aorta-small"
solid_file_name = os.getcwd() + '/' + model_name + '.vtp'
sv.solid.set_kernel('PolyData')
solid = sv.solid.SolidModel()
solid.read_native(model_name, solid_file_name) 
solid.get_boundary_faces(60)
print ("Model face IDs: " + str(solid.get_face_ids()))
solid.remesh_face([1,2,3], 0.2)
model_polydata = model_name + "_pd"
solid.get_polydata(model_polydata)
sv_vis.pRepos(renderer, model_polydata)
#sv_vis.polyDisplayWireframe(renderer, model_polydata)
sv_vis.polyDisplayPoints(renderer, model_polydata)

## Get centerlines.
#
source_ids = [1]
target_ids = [2]
#
lines_name = model_name + "_lines"
voronoi_name = model_name + "_voronoi"
dist_name = model_name + "_distance"
sv.vmtk_utils.centerlines(model_polydata, source_ids, target_ids, lines_name, voronoi_name)
sv.vmtk_utils.distance_to_centerlines(model_polydata, lines_name, dist_name)
lines_actor = sv_vis.pRepos(renderer, lines_name)[1]
lines_actor.GetProperty().SetColor(0,1,0)


'''

## Set mesh kernel.
sv.mesh.set_kernel('TetGen')

## Create mesh object
mesh = sv.mesh.Mesh()
mesh.new_object('mesh')

## Load model.
mesh.load_model(solid_file_name)

## Create new mesh.
edge_size = 0.4431 
mesh.new_mesh()
mesh.set_meshing_options('GlobalEdgeSize', [edge_size])
mesh.set_meshing_options('SurfaceMeshFlag',[1])
mesh.set_meshing_options('VolumeMeshFlag',[1])
mesh.set_meshing_options('MeshWallFirst',[1])
mesh.set_meshing_options('Optimization',[3])
#mesh.set_meshing_options('QualityRatio',[1.4])
mesh.set_meshing_options('UseMMG',[1])

mesh.set_vtk_polydata(dist_name)
mesh.set_size_function_based_mesh(edge_size, "DistanceToCenterlines")
mesh.generate_mesh()

## Save mesh to a file.
mesh_file_name = os.getcwd() + "/" + model_name + "-mesh.vtp"
mesh.write_mesh(mesh_file_name)
mesh.get_unstructured_grid('ug')
sv.repository.write_vtk_unstructured_grid("ug", "ascii", mesh_file_name)

'''

sv_vis.interact(renderer, sys.maxsize)


