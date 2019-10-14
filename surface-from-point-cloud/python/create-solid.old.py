import sv
import sv_vis as vis
import os
import sys

## Create a render and window to display geometry.
renderer, render_window = vis.initRen('demo')

surf_name = "shapeSnakeDiaSmooth"
surf_file_name = surf_name + ".vtp"

#-------------------------------------
# Create a solid model from polydata
#-------------------------------------
#
sv.Solid.SetKernel('PolyData')
surface = sv.Solid.pySolidModel()

# Read surface polydata.
surface.ReadNative(surf_name, surf_file_name)

# Display surface.
surf_pd = surf_name + "_pd"
surface.GetPolyData(surf_pd, 1.0)
#vis.pRepos(renderer, surf_pd)
#vis.polyDisplayWireframe(renderer, surf_pd)

# Cap the surface.
capped_surf_name = surf_name + "_capped"
sv.VMTKUtils.Cap_with_ids(surf_pd, capped_surf_name, 0, 0)

## Create a solid.
#
# Set the solid model geometry to be the capped surface 'capped_surf_name'.
#
# solid.GetBoundaryFaces() creates the faces needed for meshing. The '30.0'
# parameter is an angle used to determine faces, I kept lowering it until I 
# got three faces.
#
# Remesh the solid to get triangulated surface.
#
solid = sv.Solid.pySolidModel()
solid_name = surf_name + "_solid"
solid.NewObject(solid_name)
solid.SetVtkPolyData(capped_surf_name)
solid.GetBoundaryFaces(30.0)
print ("Number of face IDs: " + str(solid.GetFaceIds()))

# Remesh the solid.
print("Remeshing ... ")
solid.RemeshFace([1,2,3], 8.0)

# Write the solid to a file.
solid.WriteNative(os.getcwd() + "/" + solid_name +".vtp") 

# Visualize the solid.
solid_pd = solid_name + "_pd"
solid.GetPolyData(solid_pd, 1.0)
#vis.pRepos(renderer, solid_pd)
#vis.polyDisplayWireframe(renderer, capped_surf_pd)

#vis.interact(renderer, 1500000000)
#sys.exit(0)

#----------------------
# Mesh the solid model 
#----------------------
#
sv.MeshObject.SetKernel('TetGen')

# Create mesh object.
msh = sv.MeshObject.pyMeshObject()
msh.NewObject('mesh')

# Load solid model.
solidFn = os.getcwd() + '/' + solid_name + ".vtp"
msh.LoadModel(solidFn)

# Create new mesh.
msh.NewMesh()
msh.SetMeshOptions('SurfaceMeshFlag',[1])
msh.SetMeshOptions('VolumeMeshFlag',[1])
#msh.SetMeshOptions('GlobalEdgeSize',[0.75])
#msh.SetMeshOptions('MeshWallFirst',[1])
msh.GenerateMesh()

# Save mesh to a file.
mesh_name = capped_surf_name + "_mesh"
mesh_file_name = os.getcwd() + "/" + mesh_name + ".vtu"
print("Write mesh to: " + mesh_file_name)
msh.WriteMesh(mesh_file_name)
msh.GetUnstructuredGrid('ug')
sv.Repository.WriteVtkUnstructuredGrid("ug", "ascii", mesh_file_name)

vis.interact(renderer, 1500000000)


