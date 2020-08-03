
from sv import *
import os

#Set mesh kernel
MeshObject.SetKernel('TetGen')

#Create mesh object
msh = MeshObject.pyMeshObject()
msh.NewObject('mesh')

#Load Model
solidFn = os.getcwd() + '/cylinder-model.vtp'
msh.LoadModel(solidFn)
#Create new mesh
msh.NewMesh()
msh.SetMeshOptions('SurfaceMeshFlag',[1])
msh.SetMeshOptions('VolumeMeshFlag',[1])
msh.SetMeshOptions('GlobalEdgeSize',[0.75])
msh.SetMeshOptions('MeshWallFirst',[1])
msh.GenerateMesh()
#Save mesh to file
fileName = os.getcwd() + "/cylinder.vtk"
msh.WriteMesh(fileName)
msh.GetUnstructuredGrid('ug')
Repository.WriteVtkUnstructuredGrid("ug","ascii",fileName)
#Visualize mesh in gui
#GUI.ImportUnstructedGridFromRepos('ug')


