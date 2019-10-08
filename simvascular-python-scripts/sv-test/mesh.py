import sv
import sv_vis as vis

import os

#print(dir(sv))
#help(sv.mesh)

# Set mesh kernel
sv.mesh.set_kernel('TetGen')

# Create mesh object
mesh = sv.mesh.Mesh()
mesh.new_object('mesh')

# Load model.
model_name = 'cylinder'
model_file = os.getcwd() + '/' + model_name + '.vtp'
mesh.load_model(model_file)

# Create a new mesh.
mesh.new_mesh()
mesh.set_meshing_options('SurfaceMeshFlag',[1])
mesh.set_meshing_options('VolumeMeshFlag',[1])
mesh.set_meshing_options('GlobalEdgeSize',[0.75])
mesh.set_meshing_options('MeshWallFirst',[1])
mesh.generate_mesh()

#Save mesh to file
mesh_file_name = os.getcwd() + "/" + model_name + ".vtk"
mesh.write_mesh(mesh_file_name)
mesh.get_unstructured_grid('ug')








