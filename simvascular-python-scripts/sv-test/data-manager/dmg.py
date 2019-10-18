"""
This script tests exporting a solid model geometry to the SV Data Manger Model node. 

The script must be executed within SV with a project defined.
"""
import sv
import sv_vis as vis
import os
import sys

#--------------
# Create solid
#--------------
print("Create solid: ")
sv.solid.set_kernel('PolyData')
solid = sv.solid.SolidModel()
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
solid.cylinder('cyl', 1.5, 10, center, axis)
# Store solid polydata in repository under the name 'cyl_pd'.
solid.get_polydata('cyl_pd', 0.5)

#-------------------------------
# Show what's in the repository
#-------------------------------
repo_list = sv.repository.list()
print("Repository: " + str(repo_list))

#print(dir(sv))
sv.dmg.import_polydata_from_repository('cyl_pd')

#--------------------------------------------------
# Show the solid geometry stored in the repository
#--------------------------------------------------
renderer, render_window = vis.initRen('demo')

try:
    actor = vis.pRepos(renderer, 'cyl_pd')
    # can't export this.
    actor = vis.pRepos(renderer, 'cyl') 
except sv.repository.RepositoryException as e:
    print(e)

vis.interact(renderer, sys.maxsize)


