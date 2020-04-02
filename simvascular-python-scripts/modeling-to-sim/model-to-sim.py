
'''
This script is an example of how to prepare a model for simulation.

The workflow is:

  1) Read in closed surface from a .vtp file representing solid model. 

  2) Generate a finite element mesh from the model

  3) Generate the mesh and .svpre files needed to run a simulation using svsolver. 

'''

import os
from shutil import copyfile
import sv
import sv_vis as vis
import sys
import vtk 

## Create a render and window to display geometry.
renderer, render_window = vis.initRen('model-to-sim')
use_graphics = False

#-------------------------------------------------------------#
#                   M o d e l i n g                           #
#-------------------------------------------------------------#
print("---------- Modeling ----------")
solid_name = 'demo'
solid_name = 'cylinder'
 
if solid_name == 'cylinder':
    # Faces:
    #   face 1: surface
    #   face 2: inlet
    #   face 3: outlet
    solid_file_name = 'cylinder.vtp'
    edge_size = 0.8
    walls = [1]

elif solid_name == "demo":
    # Faces:
    #   face 1: surface
    #   face 2: inlet
    #   face 3: outlet1
    #   face 4: outlet2
    solid_file_name = 'demo.vtp'
    edge_size = 0.2
    walls = [1]

# Set the solid modeling kernel.
sv.Solid.SetKernel('PolyData')

# Read the closed surface representing a solid model.
solid = sv.Solid.pySolidModel()
solid.ReadNative(solid_name, solid_file_name)

# Extract faces.
solid.GetBoundaryFaces(50.0)
solid_face_ids = [int(id) for id in solid.GetFaceIds()]
print ("Face IDs: " + str(solid_face_ids))

## Remesh the solid.
#
# This cab be used for STL models to produce a better 
# surface representation.
#
#print("Remeshing ... ")
#solid.RemeshFace(solid_face_ids, edge_size)

# Write the solid model.
solid_file_name = "./model/" + solid_name + '-solid.vtp'
solid.WriteNative(solid_file_name)

# Create polydata to display the model.
solid_pd = solid_name + "_pd"
solid.GetPolyData(solid_pd, 1.0)

#-------------------------------------------------------------#
#                     M e s h i n g                           #
#-------------------------------------------------------------#
print("---------- Mesh generation ----------")
mesh_dir = "./mesh/"

# Set the mesher to use TetGen
sv.MeshObject.SetKernel('TetGen')

# Load a solid model into the mesher.
mesh = sv.MeshObject.pyMeshObject()
mesh.NewObject('mesh')
mesh.LoadModel(solid_file_name)
mesh.NewMesh()

# Set mesh options.
mesh.SetMeshOptions('GlobalEdgeSize', [edge_size])
mesh.SetMeshOptions('SurfaceMeshFlag',[1])
mesh.SetMeshOptions('VolumeMeshFlag',[1])
mesh.SetMeshOptions('MeshWallFirst',[1])
mesh.SetMeshOptions('UseMMG',[1])
mesh.SetMeshOptions('setWalls',[3.0])
mesh.SetMeshOptions('QualityRatio',[1.4])
mesh.SetMeshOptions('NoBisect',[0])

# Set the mesh walls.
mesh.SetWalls(walls)

# Generate the mesh.
mesh.GenerateMesh()

# Write mesh faces polygonal data to .vtp files.
print("Mesh faces ... ")
mesh.GetBoundaryFaces(50.0)
mesh_face_file_names = []
mesh_face_file_names_map = {}
mesh_face_pd_map = {}
for face_id in solid_face_ids:
    mesh_face_name =  mesh_dir + solid_name + "_mesh_face_" + str(face_id)
    mesh.GetFacePolyData(mesh_face_name, int(face_id))
    mesh_face_pd = sv.Repository.ExportToVtk(mesh_face_name)
    print("  Face {0:d}  num nodes: {1:d}".format(int(face_id), mesh_face_pd.GetNumberOfPoints()))
    mesh_face_file_name = mesh_face_name + ".vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(mesh_face_file_name)
    writer.SetInputData(mesh_face_pd)
    writer.Update()
    writer.Write()
    mesh_face_file_names.append(mesh_face_file_name)
    mesh_face_file_names_map[int(face_id)] = mesh_face_file_name
    mesh_face_pd_map[int(face_id)] = mesh_face_pd

# Save volume mesh to a file.
mesh_vol_file_name = mesh_dir + solid_name + "-mesh.vtu"
mesh.GetUnstructuredGrid('volume')
volume_mesh = sv.Repository.ExportToVtk('volume')
writer = vtk.vtkXMLUnstructuredGridWriter()
writer.SetFileName(mesh_vol_file_name)
writer.SetInputData(volume_mesh)
writer.Update()
writer.Write()

# Save surface mesh to a file.
mesh_surf_file_name = mesh_dir + solid_name + "-mesh.vtp"
mesh.GetPolyData('surface')
surf_mesh = sv.Repository.ExportToVtk('surface')
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(mesh_surf_file_name)
writer.SetInputData(surf_mesh)
writer.Update()
writer.Write()

#-------------------------------------------------------------#
#                 S i m u l a t i o n                         #
#-------------------------------------------------------------#
print("---------- Simulation ----------")
sim_dir = "./" + solid_name + "-simulation/"
sim_mesh = sim_dir + "mesh-complete/"
sim_mesh_surf = sim_mesh + "mesh-surfaces/"

# Copy volume and surface meshes.
copyfile(mesh_vol_file_name, sim_mesh+"mesh-complete.mesh.vtu")
copyfile(mesh_surf_file_name, sim_mesh+"mesh-complete.exterior.vtp")

# Combine mesh walls into a single polydata object and write.
#
# If we extract faces using solid.GetBoundaryFaces() then
# there should only be a single wall.
#
if len(walls) == 1:
    mesh_face_file_name = mesh_face_file_names_map[walls[0]]
    copyfile(mesh_face_file_name, sim_mesh+"walls_combined.vtp")
else:
    append_filter = vtk.vtkAppendPolyData()
    for id in walls:
        mesh_face_pd = mesh_face_pd_map[id]
        append_filter.AddInputData(mesh_face_pd)
    append_filter.Update()
    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputConnection(append_filter.GetOutputPort())
    clean_filter.Update()
    mesh_surface = clean_filter.GetOutput()
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(sim_mesh+"walls_combined.vtp")
    writer.SetInputData(mesh_surface)
    writer.Update()
    writer.Write()

# Copy mesh faces. 
for i,file_name in enumerate(mesh_face_file_names):
    copyfile(file_name, sim_mesh_surf+"face_"+str((i+1))+".vtp")

# Generate .svpre file.
#
# This is for the cylinder model.
#
sim_mesh = "mesh-complete/"
sim_mesh_surf = sim_mesh + "mesh-surfaces/"
svpre_file_name = sim_dir + solid_name + ".svpre"
density = 1.06
viscosity = 0.04
bct_period = 1.0
bct_point_number = 2
bct_fourier_mode_number = 1

with open(svpre_file_name, 'w') as sfile: 
    sfile.write("mesh_and_adjncy_vtu {0:s}\n".format(sim_mesh+"mesh-complete.mesh.vtu"))
    sfile.write("set_surface_id_vtp {0:s} {1:d}\n".format(sim_mesh+"mesh-complete.exterior.vtp", 1))
    sfile.write("set_surface_id_vtp {0:s} {1:d}\n".format(sim_mesh_surf+"face_2.vtp", 2))
    sfile.write("set_surface_id_vtp {0:s} {1:d}\n".format(sim_mesh_surf+"face_3.vtp", 3))
    if solid_name == "demo":
        sfile.write("set_surface_id_vtp {0:s} {1:d}\n".format(sim_mesh_surf+"face_4.vtp", 4))

    # Initial conditions.
    sfile.write("initial_pressure {0:f}\n".format(0.0))
    sfile.write("initial_velocity {0:f} {1:f} {2:f} \n".format(0.0001, 0.0001, 0.0001))

    # Surface BC
    sfile.write("noslip_vtp {0:s}\n".format(sim_mesh_surf+"face_1.vtp"))

    # Fluid properties.
    sfile.write("fluid_density {0:f}\n".format(density))
    sfile.write("fluid_viscosity {0:f}\n".format(viscosity))

    # Inflow BC.
    sfile.write("prescribed_velocities_vtp {0:s}\n".format(sim_mesh_surf+"face_2.vtp"))
    sfile.write('bct_period {0:f} \n'.format(bct_period))
    sfile.write('bct_analytical_shape parabolic\n')
    sfile.write('bct_point_number {0:d}\n'.format(bct_point_number))
    sfile.write('bct_fourier_mode_number {0:d} \n'.format(bct_fourier_mode_number))
    sfile.write('bct_create {0:s} {1:s}\n'.format(sim_mesh_surf+"face_2.vtp", 'inflow.flow'))
    sfile.write('bct_write_dat {0:s}\n'.format('bct.dat'))
    sfile.write('bct_write_vtp {0:s}\n'.format('bct.vtp'))

    # Outlet BCs
    if solid_name == 'cylinder':
        sfile.write("pressure_vtp {0:s} {1:f} \n".format(sim_mesh_surf+"face_2.vtp", 0.0))
    elif solid_name == "demo":
        sfile.write("pressure_vtp {0:s} {1:f} \n".format(sim_mesh_surf+"face_3.vtp", 0.0))
        sfile.write("pressure_vtp {0:s} {1:f} \n".format(sim_mesh_surf+"face_4.vtp", 0.0))

    # Write bc files. 
    sfile.write('write_numstart 0 {0:s}\n'.format('numstart.dat'))
    sfile.write('write_geombc {0:s}\n'.format('geombc.dat.1'))
    sfile.write('write_restart {0:s}\n'.format('restart.0.1'))

#-------------------------------------------------------------#
#                     G r a p h i c s                         #
#-------------------------------------------------------------#
# Optional display of models and meshes.

if (False):
    vis.pRepos(renderer, solid_pd)

# Show graphics window.
if use_graphics:

    vis.interact(renderer, sys.maxsize)


