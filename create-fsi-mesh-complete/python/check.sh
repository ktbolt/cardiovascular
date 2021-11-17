
dir=/Users/parkerda/software/ktbolt/svFSI-Tests/07-fsi/ale/03-pipe_3D/
file1=mesh/wall/mesh-surfaces/wall_inner.vtp
file2=mesh/lumen/mesh-surfaces/lumen_wall.vtp

dir=/Users/parkerda/SimVascular/CylinderProject/Meshes/
file1=solid-mesh-complete/mesh-surfaces/interface.vtp
file2=fluid-mesh-complete/mesh-surfaces/lumen_wall.vtp

dir=./
file1=solid-wall-inner.vtp
file2=fluid-wall.vtp

check-mesh.py ${dir}/${file1} ${dir}/${file2}

