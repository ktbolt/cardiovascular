
import sv
import os

## Set mesh kernel.
sv.MeshObject.SetKernel('TetGen')

## Create mesh object
mesh = sv.MeshObject.pyMeshObject()
mesh.NewObject('mesh')

## Load model.
model_name = "aorta-small"
model_name = "one-vessel"
solid_file_name = os.getcwd() + '/' + model_name + '.vtp'
mesh.LoadModel(solid_file_name)

## Create new mesh.
edge_size = 0.4431 
mesh.NewMesh()
mesh.SetMeshOptions('GlobalEdgeSize', [edge_size])
mesh.SetMeshOptions('SurfaceMeshFlag',[1])
mesh.SetMeshOptions('VolumeMeshFlag',[1])
mesh.SetMeshOptions('MeshWallFirst',[1])
mesh.SetMeshOptions('Optimization',[3])
#mesh.SetMeshOptions('QualityRatio',[1.4])
mesh.SetMeshOptions('UseMMG',[1])
mesh.SetSizeFunctionBasedMesh(edge_size, "DistanceToCenterlines")
mesh.GenerateMesh()

## Save mesh to a file.
mesh_file_name = os.getcwd() + "/" + model_name + "-mesh.vtp"
mesh.WriteMesh(mesh_file_name)
mesh.GetUnstructuredGrid('ug')
sv.Repository.WriteVtkUnstructuredGrid("ug", "ascii", mesh_file_name)


